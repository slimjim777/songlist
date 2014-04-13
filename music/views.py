from music import app
from flask import render_template
from music.model.drive import Drive


@app.route('/')
def index():
    store = Drive()
    files = store.files()

    return render_template('index.html', songs=enumerate((files.keys())), files=files)

