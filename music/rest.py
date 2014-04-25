# -*- coding: utf-8 -*-
from music import app
from music.authorize import login_required
from flask import request
from flask import jsonify
from flask import session
from music.model.cache import Cache
from music.model.transpose import Transpose
from music.model.drive import Drive
from music.model.database import Folder
from music.model.database import File
from music import db


@app.route('/song/transpose', methods=['POST'])
@login_required
def transpose():
    # Get the parameters from the JSON request
    if not 'song' in request.json or not 'key' in request.json:
        return jsonify({'response': 'Failed', 'error': "The 'song' and 'key' must be supplied."})
        
    song = request.json['song']
    key = request.json['key']

    # Transpose the song
    t = Transpose(song, key)
    return jsonify(t.song)


@app.route('/monitor', methods=['GET'])
def monitor():
    """
    Expose a URL for the site monitoring that will also refresh the song cache
    from Dropbox every hour.
    """
    # Check if the local cache of the file/folder list is valid
    cache = Cache()
    cache_valid = cache.hcache_valid('fileshash')

    if not cache_valid:
        cache_files_in_database()

    return jsonify({'response': 'Success'})


@app.route('/refresh', methods=['GET'])
@login_required
def refresh():
    """
    Expose an authenticated URL refresh the song cache on demand.
    """
    cache_files_in_database()
    return jsonify({'response': 'Success'})


@app.route('/user/theme', methods=['POST'])
@login_required
def change_theme():
    """
    Store the user's theme as a session variable.
    """
    if 'theme' in request.json:
        session['theme'] = request.json['theme']
    return ''


def cache_files_in_database():
    """
    The folders and files are cached in the database, so that we have a persistent, local store that we can store
    additional metadata against a folder e.g. Youtube link to a song. The folders and files are in two tables with a
    parent-child relationship.

    Since Dropbox does not offer a reliable unique ID for a file, we can only identify the folders and files by name.
    If a folder or file is renamed, then we will lose the metadata stored against it. We will need to handle the
    removal of the old-named records ourselves.
    """
    # Get the current list of files from the Dropbox file store
    store = Drive()
    files = store.files()

    # Update database with the current list of files and folders
    folder = Folder()
    for filename, value in files.iteritems():
        # Check if the folder name exists
        song_folder = folder.query.filter_by(name=filename).first()
        if not song_folder:
            # No: create it
            app.logger.debug('Create it')
            song_folder = Folder()
            song_folder.name = filename
            db.session.add(song_folder)
            db.session.commit()
        else:
            # Remove all file records that are linked to the folder record
            for f in song_folder.files:
                db.session.delete(f)

        # Create the file records with the updated URLs
        for file_meta in value:
            f = File()
            f.folder_id = song_folder.id
            for field in ['name', 'path', 'extension', 'size', 'mime_type', 'url']:
                setattr(f, field, file_meta[field])
            db.session.add(f)
        db.session.commit()

    # Delete any folder records that no longer exist in Dropbox
    no_longer = Folder.query.filter(~Folder.name.in_(files.keys()))
    for nl in no_longer:
        db.session.delete(nl)

    db.session.commit()

    # Set the cache expiry
    cache = Cache()
    cache.hset_cache_expiry('fileshash')
