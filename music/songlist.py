from music import app
from music import db
from music.authorize import login_required
from music.model.database import SongList
from music.model.database import Song
from music.model.database import Folder
from flask import jsonify
from flask import session
from flask import request


@app.route('/api/songlists', methods=['GET'])
@login_required
def api_songlists():
    """
    Get the list of songlists, returned as JSON
    """
    from_page = int(request.args.get('page', 1))
    songlists = SongList.query.order_by('event_date desc').paginate(
        from_page, 10, False)

    result = paginate_rows(songlists)
    return jsonify(result)


def paginate_rows(paginate):
    rows = paginate.items
    meta = {
        'total': paginate.pages,
        'page': paginate.page,
        'has_next': paginate.has_next,
        'has_prev': paginate.has_prev,
        'next_num': paginate.next_num,
        'prev_num': paginate.prev_num,
    }
    data = [p.to_dict() for p in rows]
    return {'response': 'Success', 'data': data, 'meta': meta}


@app.route('/api/songlists', methods=['POST'])
@app.route(
    '/api/songlists/<int:songlist_id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def api_songlist(songlist_id=None):
    """
    Get a specific songlist.
    Create or update a songlist.
    """
    if request.method == "GET":
        try:
            songlist = SongList.query.get(songlist_id)
            if not songlist:
                raise Exception('Cannot find the songlist')
            result = {
                'response': 'Success',
                'songlist': songlist.to_dict(),
            }
            return jsonify(result)
        except Exception, v:
            return jsonify({'response': 'Error', 'message': str(v)})
    elif request.method == "POST":
        if songlist_id:
            try:
                # Update an existing songlist
                songlist = SongList.query.get(songlist_id)
                if not songlist:
                    raise Exception('Cannot find the songlist')
                songlist.name = request.json.get('name')
                songlist.event_date = request.json.get('event_date')
                db.session.commit()
                return jsonify(
                    {'response': 'Success', 'record': songlist.to_dict()})
            except Exception, v:
                return jsonify({'response': 'Error', 'message': str(v)})
        else:
            # Create a new songlist
            try:
                songlist = SongList(
                    request.json.get('name'), request.json.get('event_date'),
                    session['user_id'])
                db.session.add(songlist)
                db.session.commit()
                return jsonify(
                    {'response': 'Success', 'record': songlist.to_dict()})
            except Exception, v:
                return jsonify({'response': 'Error', 'message': str(v)})
    elif request.method == "DELETE":
        try:
            # Delete the songlist
            songlist = SongList.query.get(songlist_id)
            db.session.delete(songlist)
            db.session.commit()
            return jsonify({'response': 'Success'})
        except Exception, v:
            return jsonify({'response': 'Error', 'message': str(v)})


@app.route('/api/song/find', methods=['POST'])
@login_required
def api_song_find():
    # Check if we have a search query
    q = request.json.get('q')
    if q:
        # Search for folders containing the query
        song_query = Folder.query.filter(
            Folder.name.ilike('%%%s%%' % q)).order_by(Folder.name)
        song_list = [f.dict() for f in song_query.all()]
    else:
        song_list = []

    return jsonify({'response': 'Success', 'folders': song_list})


@app.route('/api/song', methods=['POST'])
@app.route('/api/song/<int:song_id>', methods=['GET', 'POST'])
@login_required
def api_song(song_id=None):
    if request.method == "POST":
        if song_id:
            try:
                # Update existing song
                song = Song.query.get(song_id)
                song.songlist_id = request.json.get('songlist_id')
                song.name = request.json.get('name')
                song.key = request.json.get('key')
                song.tempo = request.json.get('tempo')
                song.time_signature = request.json.get('time_signature')
                db.session.commit()
                return jsonify(
                    {'response': 'Success', 'record': song.to_dict()})
            except Exception, v:
                return jsonify({'response': 'Error', 'message': str(v)})
        else:
            try:
                # Create a new song
                song = Song()
                song.songlist_id = request.json.get('songlist_id')
                song.name = request.json.get('name')
                song.key = request.json.get('key')
                song.tempo = request.json.get('tempo')
                song.time_signature = request.json.get('time_signature')
                db.session.add(song)
                db.session.commit()
                return jsonify(
                    {'response': 'Success', 'record': song.to_dict()})
            except Exception, v:
                return jsonify({'response': 'Error', 'message': str(v)})

    elif request.method == "GET":
        if song_id:
            try:
                song = Song.query.get(song_id)
                if not song:
                    raise Exception('Cannot find the request song.')
                return jsonify(
                    {'response': 'Success', 'record': song.to_dict()})
            except:
                return jsonify({'response': 'Error', 'message': str(v)})
        else:
            return jsonify(
                {'response': 'Error', 'message': 'No song requested.'})


@app.route('/api/songlists/<int:songlist_id>/song_order', methods=['POST'])
@login_required
def api_songlist_order(songlist_id):
    update = False
    for index, song_id in enumerate(request.json.get('song_order', [])):
        update = True
        song = Song.query.get(song_id)
        song.position = index

    if update:
        db.session.commit()
    return jsonify({'response': 'Success'})


@app.route('/api/songlists/<int:songlist_id>/remove_song', methods=['POST'])
@login_required
def api_songlist_remove_song(songlist_id):
    song_id = request.json.get('song_id')
    if song_id:
        song = Song.query.get(song_id)
        db.session.delete(song)
        db.session.commit()
    return jsonify({'response': 'Success'})
