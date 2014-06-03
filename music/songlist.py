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
    songlists = SongList.query.order_by('event_date desc').all()
    json_songlists = []
    for sl in songlists:
        json_songlists.append(sl.to_dict())

    result = {
        'response': 'Success',
        'songlists': json_songlists,
    }

    return jsonify(result)


@app.route('/api/songlists', methods=['POST'])
@app.route('/api/songlists/<int:songlist_id>', methods=['GET', 'POST'])
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
                songlist = SongList.query.get(songlist_id);
                if not songlist:
                    raise Exception('Cannot find the songlist')
                songlist.name = request.json.get('name')
                songlist.event_date = request.json.get('event_date')
                db.session.commit()
                return jsonify({'response': 'Success', 'record': songlist.to_dict()})
            except Exception, v:
                return jsonify({'response': 'Error', 'message': str(v)})
        else:
            # Create a new songlist
            try:
                songlist = SongList(request.json.get('name'), request.json.get('event_date'), session['user_id'])
                db.session.add(songlist)
                db.session.commit()
                return jsonify({'response': 'Success', 'record': songlist.to_dict()})
            except Exception, v:
                return jsonify({'response': 'Error', 'message': str(v)})


@app.route('/api/song/find', methods=['POST'])
@login_required
def api_song_find():
    # Check if we have a search query
    q = request.json.get('q')
    if q:
        # Search for folders containing the query
        song_query = Folder.query.filter(Folder.name.ilike('%%%s%%' % q)).order_by(Folder.name)
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
                return jsonify({'response': 'Success', 'record': song.to_dict()})
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
                return jsonify({'response': 'Success', 'record': song.to_dict()})
            except Exception, v:
                return jsonify({'response': 'Error', 'message': str(v)})

    elif request.method == "GET":
        if song_id:
            try:
                song = Song.query.get(song_id)
                if not song:
                    raise Exception('Cannot find the request song.')
                return jsonify({'response': 'Success', 'record': song.to_dict()})
            except:
                return jsonify({'response': 'Error', 'message': str(v)})
        else:
            return jsonify({'response': 'Error', 'message': 'No song requested.'})
