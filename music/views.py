# -*- coding: utf-8 -*-
from music import app
from flask import render_template
from flask import request
from flask import abort
from music.model.drive import Drive
from music.model.onsong import Onsong
from music.model.database import Database
import json


@app.route('/')
def index():
    # Check if the local cache of the file/folder list is valid
    db = Database()
    files_json = db.get_cache('files')

    if not files_json:
        # Cache was invalid or expired, so get the current file list
        store = Drive()
        files = store.files()

        # Update the cache
        db.set_cache('files', json.dumps(files))
    else:
        # Convert the response into a dictionary
        files = json.loads(files_json)

    app.logger.debug(files)
    return render_template('index.html', songs=enumerate(sorted(files.keys())), files=files)


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
