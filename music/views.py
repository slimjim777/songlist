from music import app
from flask import render_template
from music.model.drive import Drive
from music.model.onsong import Onsong


@app.route('/')
def index():
    store = Drive()
    files = store.files()
    
    app.logger.debug(files)

    return render_template('index.html', songs=enumerate(sorted(files.keys())), files=files)

@app.route('/chart/<file_path>')
def chart(file_path):
    song_path = file_path.replace('__','/')

    # Get the Onsong file contents from the file store
    store = Drive()
    contents = store.file_contents(song_path)
    
    # Parse the Onsong file
    songon = Onsong(contents)
    song_chart = songon.parse()
    
    # Use the song flow to define the order to display the song sections
    sections = []
    for f in song_chart['Flow']:
        if f not in sections:
            sections.append(f)
    
    return render_template('chart.html', song=song_chart, sections=sections)
