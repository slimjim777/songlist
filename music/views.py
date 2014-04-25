# -*- coding: utf-8 -*-
from music import app
from music import db
from flask import render_template
from flask import request
from flask import abort
from flask import session
from flask import jsonify
from music.model.drive import Drive
from music.model.song import Onsong, ChordPro
from music.authorize import login_required
from music.model.database import Person
from music.model.database import Folder
import time


PAGE_SIZE = int(app.config['PAGE_SIZE'])


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/songs')
@login_required
def index():
    start = time.time()
    # Get the page number for pagination
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1

    # Get the folders for the page
    folders = Folder.query.order_by(Folder.name).paginate(page, PAGE_SIZE, False)

    resp = render_template('index.html', folders=folders, page=page, pages=folders.pages)
    end = time.time()
    app.logger.info('Page load: %s' % (end - start))
    return resp


@app.route('/songs/search')
@login_required
def song_search():
    # Check if we have a search query
    q = request.args.get('q')
    if q:
        # Search for folders containing the query
        song_list = Folder.query.filter(Folder.name.ilike('%%%s%%' % q)).order_by(Folder.name)
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


@app.route('/admin/users', methods=['POST'])
@app.route('/admin/users/<int:user_id>', methods=['GET', 'PUT'])
@login_required
def admin_user_edit(user_id=None):
    """
    Edit the user permissions.
    """
    if 'admin' not in session['role']:
        abort(403)
    if user_id:
        user = Person.query.get(user_id)
        if request.method == "GET":
            return render_template('snippet_user.html', user=user)
        elif request.method == "PUT":
            # Update the user record
            try:
                user.email = request.form.get('email')
                user.firstname = request.form.get('firstname')
                user.lastname = request.form.get('lastname')
                user.role = request.form.get('role')
                db.session.commit()
                return jsonify({'response': 'Success'})
            except ValueError, v:
                return jsonify({'response': 'Error', 'message': str(v)})
    elif request.method == "POST":
        # Add a new user record
        try:
            u = Person(request.form.get('email'), request.form.get('firstname'), request.form.get('lastname'))
            u.role = request.form.get('role')
            db.session.add(u)
            result = db.session.commit()
            app.logger.debug(result)
            return jsonify({'response': 'Success'})
        except ValueError, v:
            return jsonify({'response': 'Error', 'message': str(v)})
