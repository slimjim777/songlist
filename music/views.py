# -*- coding: utf-8 -*-
from music import app
from flask import render_template
from flask import request
from music.model.drive import Drive
from music.model.onsong import Onsong
from music.model.onsong import Transpose


@app.route('/')
def index():
    store = Drive()
    files = store.files()
    
    app.logger.debug(files)

    return render_template('index.html', songs=enumerate(sorted(files.keys())), files=files)

@app.route('/chart/<file_path>', methods=['GET', 'POST'])
def chart(file_path):
    song_path = file_path.replace('__','/')
    
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
