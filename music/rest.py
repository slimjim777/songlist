# -*- coding: utf-8 -*-
from music import app
from flask import render_template
from flask import request
from flask import jsonify
from music.model.onsong import Transpose
import json


@app.route('/song/transpose', methods=['POST'])
def transpose():
    # Get the parameters from the JSON request
    if not 'song' in request.json or not 'key' in request.json:
        return jsonify({'response': 'Failed', 'error': "The 'song' and 'key' must be supplied."})
        
    app.logger.debug(request.json['song'])
        
    song = request.json['song']
    key = request.json['key']

    # Transpose the song
    transpose = Transpose()
    song_chart = transpose.transpose(song, key)
    return jsonify(song_chart)
