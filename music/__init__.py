# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)

if os.environ.get('DEBUG'):
    app.debug = True

app.config['NAV_rota'] = os.environ['NAV_ROTA']
app.config['NAV_rehearsal'] = os.environ['NAV_REHEARSAL']
app.config['NAV_spotify'] = os.environ['NAV_SPOTIFY']
app.config['DROPBOX_ACCESS_TOKEN'] = os.environ['DROPBOX_ACCESS_TOKEN']
app.config['REDIS'] = os.environ['REDISCLOUD_URL']
app.config['PAGE_SIZE'] = os.environ['PAGE_SIZE']
app.config['GCLIENT_ID'] = os.environ['GCLIENT_ID']
app.config['GCLIENT_SECRET'] = os.environ['GCLIENT_SECRET']
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
app.secret_key = os.environ['APP_SECRET']

# Date format
app.config['DATE_FORMAT'] = os.environ.get('DATE_FORMAT', '%d/%m/%Y')


db = SQLAlchemy(app)

import music.authorize
import music.views
import music.rest
