# -*- coding: utf-8 -*-
from music import app
from music.authorize import login_required
from flask import request
from flask import jsonify
from flask import session
from flask import render_template
from flask import abort
from music.model.cache import Cache
from music.model.transpose import Transpose
from music.model.drive import Drive
from music.model.database import Folder
from music.model.database import File
from music.model.database import SongList
from music.model.database import SongListLink
from music.model.database import Person
from music.model.database import Tag
from music import db
import time
import datetime


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


@app.route('/song/<int:song_id>', methods=['GET', 'POST'])
@login_required
def song_by_id(song_id):
    song = Folder.query.get(song_id)
    if request.method != 'POST':
        return render_template('snippet_song.html', song=song)

    song.url = request.json.get('url')
    song.tempo = request.json.get('tempo')
    song.time_signature = request.json.get('time_signature')
    db.session.commit()
    return jsonify({'response': 'Success'})


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
    no_longer = Folder.query.filter(~Folder.name.in_(files.keys())).all()
    for nl in no_longer:
        db.session.delete(nl)

    db.session.commit()

    # Set the cache expiry
    cache = Cache()
    cache.hset_cache_expiry('fileshash')


@app.route('/admin/users', methods=['POST'])
@app.route('/admin/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
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
        elif request.method == "DELETE":
            # Delete the user
            try:
                db.session.delete(user)
                db.session.commit()
                return jsonify({'response': 'Success'})
            except Exception, e:
                return jsonify({'response': 'Error', 'message': str(e)})
    elif request.method == "POST":
        # Add a new user record
        try:
            u = Person(request.form.get('email'), request.form.get('firstname'), request.form.get('lastname'))
            u.role = request.form.get('role')
            db.session.add(u)
            db.session.commit()
            return jsonify({'response': 'Success'})
        except ValueError, v:
            return jsonify({'response': 'Error', 'message': str(v)})


@app.route('/songlist/list', methods=['POST'])
@app.route('/songlist/list/<int:songlist_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def songlist_admin(songlist_id=None):
    """
    Maintain the song lists: add, update, delete.
    """
    if songlist_id:
        sl = SongList.query.get(songlist_id)
        if request.method == "GET":
            return render_template('snippet_songlist.html', songlist=sl)
        elif request.method == "PUT":
            # Update the song list record
            try:
                sl.name = request.form.get('name')
                ev_date = time.strptime(request.form.get('event_date'), '%d/%m/%Y')
                sl.event_date = datetime.date(*ev_date[:3])
                db.session.commit()
                return jsonify({'response': 'Success'})
            except Exception, v:
                return jsonify({'response': 'Error', 'message': str(v)})
        elif request.method == "DELETE":
            # Delete the user
            try:
                db.session.delete(sl)
                db.session.commit()
                return jsonify({'response': 'Success'})
            except Exception, e:
                return jsonify({'response': 'Error', 'message': str(e)})
    elif request.method == 'POST':
        try:
            # Check the date
            ev_date = time.strptime(request.form.get('event_date'), '%d/%m/%Y')
            sl = SongList(request.form.get('name'), datetime.date(*ev_date[:3]), request.form.get('owner_id'))
            db.session.add(sl)
            result = db.session.commit()
            app.logger.debug(result)
            return jsonify({'response': 'Success'})
        except Exception, v:
            return jsonify({'response': 'Error', 'message': str(v)})


@app.route('/songs/find', methods=['POST'])
@login_required
def songs_find():
    # Check if we have a search query
    q = request.form.get('q')
    if q:
        # Search for folders containing the query
        song_list = Folder.query.filter(Folder.name.ilike('%%%s%%' % q)).order_by(Folder.name)
    else:
        song_list = None
    return render_template('snippet_song_find.html', song_list=song_list)


@app.route('/songlist/<int:songlist_id>/add', methods=['POST'])
@login_required
def songlist_add(songlist_id):
    """
    Add a song to an existing song list.
    """
    sl = SongList.query.get(songlist_id)
    song_id = int(request.form.get('song_id'))
    if not song_id:
        return jsonify({'response': 'Error', 'message': "The 'song_id' must be supplied."})

    # Check if we have the song in the song list already
    for s in sl.folders:
        if s.folder.id == song_id:
            # Nothing to do
            return jsonify({'response': 'Success'})

    # Add the song to the song list
    song = Folder.query.get(song_id)
    link = SongListLink()
    link.folder = song
    sl.folders.append(link)
    db.session.commit()
    return jsonify({'response': 'Success'})


@app.route('/songlist/<int:songlist_id>/remove', methods=['DELETE'])
@login_required
def songlist_remove(songlist_id):
    """
    Remove a song to an existing song list.
    """
    song_id = int(request.form.get('song_id'))
    if not song_id:
        return jsonify({'response': 'Error', 'message': "The 'song_id' must be supplied."})

    # Remove the song from the song list
    links = SongListLink.query.filter_by(songlist_id=songlist_id, song_id=song_id).all()
    for l in links:
        db.session.delete(l)
    db.session.commit()
    return jsonify({'response': 'Success'})


@app.route('/songlist/<int:songlist_id>/list', methods=['GET', 'PUT'])
@login_required
def songlist_list(songlist_id):
    """
    Get the list of songs for the song list or update the order of the songs.
    """
    #sl = SongList.query.get(songlist_id)
    links = SongListLink.query.filter_by(songlist_id=songlist_id).order_by(SongListLink.position).all()
    if request.method == 'GET':
        return render_template('snippet_songlist_songs.html', song_list=links)
    elif request.method == 'PUT':
        new_order = request.json.get('new_order')
        if not new_order:
            return jsonify({'response': 'Error', 'message': "The 'new_order' must be supplied."})

        # Update the order of the songs in the link table
        for l in links:
            # Get the index of the song in the newly ordered list
            position = new_order.index(str(l.song_id))
            l.position = position
        db.session.commit()
        return jsonify({'response': 'Success'})


@app.route('/song/<int:folder_id>/tags', methods=['GET', 'POST'])
@login_required
def song_tags(folder_id):
    if request.method == 'GET':
        folder = Folder.query.get(folder_id)
        selected_ids = [t.id for t in folder.tags]
        if len(selected_ids) > 0:
            unselected = Tag.query.filter(~ Tag.id.in_(selected_ids))
        else:
            unselected = Tag.query.all()
        return render_template('snippet_song_tags.html', folder_id=folder_id, selected=folder.tags,
                               unselected=unselected)
    elif request.method == 'POST':
        folder = Folder.query.get(folder_id)
        selected = request.json.get('selected', [])
        app.logger.debug(selected)

        # Remove the existing tags for the song
        for t in folder.tags:
            folder.tags.remove(t)

        # Add the updated list of song tags
        for sel in selected:
            try:
                tag_id = int(sel)
                tag = Tag.query.get(tag_id)
                folder.tags.append(tag)
            except ValueError:
                # Must be a new tag that needs creating
                tag = Tag()
                tag.name = sel
                db.session.add(tag)
                folder.tags.append(tag)
        db.session.commit()
        return jsonify({'response': 'Success'})
