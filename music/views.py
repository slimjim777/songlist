# -*- coding: utf-8 -*-
from music import app
from flask import render_template
from flask import request
from flask import abort
from flask import session
from music.model.drive import Drive
from music.model.song import Onsong
from music.model.song import ChordPro
from music.authorize import login_required
from music.model.database import Person
from music.model.database import Folder
from music.model.database import File
from music.model.database import Tag
from music.model.transpose import Transpose


PAGE_SIZE = int(app.config['PAGE_SIZE'])


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/songs')
@login_required
def index():
    # Get the page number for pagination
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1

    tags_selected = request.args.get('tags_selected', '').split('|')
    if '' in tags_selected:
        tags_selected.remove('')

    # Get the folders for the page
    if len(tags_selected) == 0:
        folders = Folder.query.order_by(Folder.name).paginate(page, PAGE_SIZE, False)
    else:
        folders = Folder.query.filter(Folder.tags.any(Tag.name.in_(tags_selected))).order_by(Folder.name).paginate(page, PAGE_SIZE, False)
    tags = Tag.query.all()

    return render_template('index.html', folders=folders, page=page, pages=folders.pages, tags=tags, tags_selected=tags_selected)


@app.route('/songs/search')
@login_required
def song_search():
    # Check if we have a search query
    q = request.args.get('q')
    if q:
        # Search for folders containing the query
        song_list_folders = Folder.query.filter(Folder.name.ilike('%%%s%%' % q))
        song_list_files = File.query.filter(File.name.ilike('%%%s%%' % q))
        song_list_file_folders = Folder.query.filter(Folder.id.in_([fil.folder_id for fil in song_list_files]))
        song_list = song_list_file_folders.union(song_list_folders).order_by(Folder.name)
    else:
        song_list = None

    return render_template('search.html', files=song_list, q=q)


@app.route('/song')
@login_required
def song():
    # Get the file path of the song
    file_path = request.args.get('file_path')
    if not file_path:
        abort(404)

    # Get the Onsong file contents from the file store
    store = Drive()
    contents = store.file_contents(file_path)

    # Parse the file based on the extension
    extension = file_path.split('.')[-1]

    if extension.lower() == 'onsong':
        # Parse the Onsong file
        on_song = Onsong(contents)
        song_chart = on_song.parsed
    else:
        song_pro = ChordPro(contents)
        song_chart = song_pro.parsed

    # Transpose to 'OriginalKey' if it is provided
    if song_chart.get('OriginalKey'):
        t = Transpose(song_chart, song_chart['OriginalKey'])
        song_chart = t.song

    return render_template('song.html', song=song_chart)


@app.route('/error')
def error():
    return render_template('alerts.html')


@app.route('/admin')
@login_required
def admin():
    if 'admin' not in session['role']:
        abort(403)

    users = Person.query.order_by('lastname', 'firstname').all()
    return render_template('admin.html', users=users)


@app.route('/songlist')
@login_required
def songlist():
    return render_template('metronome.hbs')
