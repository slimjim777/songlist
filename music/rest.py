# -*- coding: utf-8 -*-
from music import app
from music.authorize import login_required
from flask import request
from flask import jsonify
from flask import session
from music.model.cache import Cache
from music.model.transpose import Transpose
from music.views import cache_files


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
        cache_files()

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
