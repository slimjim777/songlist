from music import app
from flask import redirect
from flask import request
from flask import url_for
from flask import session
from flask_oauthlib.client import OAuth
from functools import wraps


# Prepare OAuth
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key=app.config.get('GCLIENT_ID'),
    consumer_secret=app.config.get('GCLIENT_SECRET'),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/userinfo.email'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('google_token') is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/login/authorized')
@google.authorized_handler
def authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    me = google.get('userinfo')
    app.logger.debug(me.data)

    # Check get the user permissions from the database

    return redirect(url_for('index'))


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')
