# -*- coding: utf-8 -*-
from music import app
from flask import render_template
from flask import request
from music.model.drive import Drive
from music.model.onsong import Onsong
from music.model.onsong import Transpose
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


@app.route('/chart/<file_path>', methods=['GET', 'POST'])
def chart(file_path):
    song_path = file_path.replace('__', '/')

    # Get the new key, if requested
    new_key = None
    if request.method == 'POST':
        new_key = request.form.get('key')

    # Get the Onsong file contents from the file store
    store = Drive()
    contents = store.file_contents(song_path)

    # Parse the Onsong file
    songon = Onsong(contents)
    song_chart = songon.parse()

    # Transpose the song
    transpose = Transpose()
    song_chart = transpose.transpose(song_chart, new_key)

    # Use the song flow to define the order to display the song sections
    sections = transpose.song_sections()

    return render_template('chart.html', song=song_chart, sections=sections)
