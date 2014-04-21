# -*- coding: utf-8 -*-
from music import app
from flask import render_template
from flask import request
from flask import abort
from music.model.drive import Drive
from music.model.onsong import Onsong
from music.model.database import Database
import json


PAGE_SIZE = int(app.config['PAGE_SIZE'])


@app.route('/')
def index():
    # Get the page number for pagination
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1

    # Check if the local cache of the file/folder list is valid
    db = Database()
    cache_valid = db.hcache_valid('fileshash')

    if not cache_valid:
        cache_files()
    
    # Get the song list from the cache, retrieving the songs for the current page
    files = {}
    for f in db.r.lrange('songnames', (page - 1) * PAGE_SIZE, (page - 1) * PAGE_SIZE + (PAGE_SIZE - 1)):
        files[f] = json.loads(db.hget_cache('fileshash', f))
        
    # Get the total number of pages
    total_pages = int((len(db.r.hkeys('fileshash')) + PAGE_SIZE - 1)  / PAGE_SIZE)

    app.logger.debug(files)
    return render_template('index.html', songs=enumerate(sorted(files.keys())), files=files, page=page, pages=total_pages)


def cache_files():
    """
    The folder/file list is cached in a hash (with the key as a song name/folder, value as 
    JSON file list). The expiry date/time is also set for the cache. The list of song names
    is kept in the cache as a sorted list - this is used for pagination.
    
    Redis keys:
                filehash: hash of all the folders and files.
        fileshash_expiry: expiry date/time of the cached data.
               songnames: sorted list of the songs for pagination.
    """
    # Cache was invalid or expired, so get the current file list
    store = Drive()
    files = store.files()

    # Update the cache, store the file names in a hash
    db = Database()
    db.delete('fileshash')
    db.hset_cache_expiry('fileshash')
    for file, value in files.iteritems():
        # Hash key is the song name and the value is the JSON file list
        db.hset_cache('fileshash', file, json.dumps(value))
       
    # Cache the song names in a list (sorted). This is used for pagination
    db.delete('songnames')
    for f in sorted(files.keys()):
        db.r.rpush('songnames', f)


@app.route('/song')
def song():
    # Get the file path of the song
    file_path = request.args.get('file_path')
    app.logger.debug(file_path)
    if not file_path:
        abort(404)

    # Get the Onsong file contents from the file store
    store = Drive()
    contents = store.file_contents(file_path)

    # Parse the Onsong file
    songon = Onsong(contents)
    song_chart = songon.parse()

    return render_template('song.html', song=song_chart)
