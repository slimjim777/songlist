from music import app
from music import db
from music.authorize import login_required
from music.model.database import SongList
from music.model.database import Song
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
        songlist = SongList.query.get(songlist_id)

        result = {
            'songlist': songlist.to_dict(),
        }
        return jsonify(songlist.to_dict())
    elif request.method == "POST":
        if songlist_id:
            # Update an existing songlist
            pass
        else:
            # Create a new songlist
            try:
                songlist = SongList(request.json.get('name'), request.json.get('event_date'), session['user_id'])
                db.session.add(songlist)
                db.session.commit()
                return jsonify({'response': 'Success', 'record': songlist.to_dict()})
            except Exception, v:
                return jsonify({'response': 'Error', 'message': str(v)})


@app.route('/api/song/<int:song_id>')
@login_required
def api_song(song_id):
    song = Song.query.get(song_id)
    return jsonify(song.to_dict())
