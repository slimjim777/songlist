from flask import Flask
import os

app = Flask(__name__)

if os.environ.get('DEBUG'):
    app.debug = True

app.config['DRIVE_FILES'] = os.environ['DRIVE_FILES']
app.config['NAV_rota'] = os.environ['NAV_ROTA']
app.config['NAV_rehearsal'] = os.environ['NAV_REHEARSAL']
app.config['NAV_spotify'] = os.environ['NAV_SPOTIFY']


import music.views
