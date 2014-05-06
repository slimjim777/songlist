from music import db, app
from sqlalchemy.orm import validates
import datetime
import re


class SongListLink(db.Model):
    songlist_id = db.Column(db.Integer, db.ForeignKey('song_list.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('folder.id'), primary_key=True)
    position = db.Column(db.Integer, default=0)
    folder = db.relationship('Folder', backref='songlist_link')


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    role = db.Column(db.Enum('admin', 'standard', name='role_types'), default='standard')
    last_login = db.Column(db.DateTime())
    songlists = db.relationship('SongList', backref='person', lazy='dynamic')

    def __init__(self, email, firstname, lastname):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname

    @validates('firstname', 'lastname', 'email')
    def check_not_empty(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError('The field `%s` must not be empty' % key)
        else:
            return value.strip()

    @staticmethod
    def user_by_email(email):
        """
        Get the user by the Email address.
        """
        user = Person.query.filter_by(email=email).first()
        return user

    def full_name(self):
        return '%s %s' % (self.firstname, self.lastname)

    @staticmethod
    def update_last_login(user_id):
        user = Person.query.get(user_id)
        user.last_login = datetime.datetime.utcnow()
        db.session.add(user)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.email


class Folder(db.Model):
    """
    Cache the folder details in the database.
    The URL and description allow users to enter extra metadata against a song e.g. Youtube link.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, index=True)
    active = db.Column(db.Boolean, default=True)
    url = db.Column(db.String(255))
    notes = db.Text()
    files = db.relationship('File', backref='folder', lazy='joined', cascade="save-update, merge, delete")
    tempo = db.Column(db.Integer)

    def highlight(self, q):
        """
        Mark up match text in the name.
        """
        if not q:
            return self.name
        p = re.compile("(" + q + ")", re.IGNORECASE)
        return p.sub('<mark>' + q + '</mark>', self.name)

    def __repr__(self):
        return '<Folder %r>' % self.name


class File(db.Model):
    """
    Cache the file details in the database.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    extension = db.Column(db.String(20))
    size = db.Column(db.String(10))
    mime_type = db.Column(db.String(255))
    url = db.Column(db.String(255))
    folder_id = db.Column(db.Integer, db.ForeignKey('folder.id'))

    def highlight(self, q):
        """
        Mark up match text in the name.
        """
        if not q:
            return self.name
        p = re.compile("(" + q + ")", re.IGNORECASE)
        return p.sub('<mark>' + q + '</mark>', self.name)

    def __repr__(self):
        return '<File %r>' % self.name


class SongList(db.Model):
    """
    Song List to be able to create play lists of songs. This has a many-to-many relationship with the Folder.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    event_date = db.Column(db.Date)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    folders = db.relationship('SongListLink', backref='songlist')

    def __init__(self, name, event_date, owner_id):
        self.name = name
        self.event_date = event_date
        self.person_id = owner_id

    @validates('name', 'person_id')
    def check_not_empty(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError('The field `%s` must not be empty' % key)
        else:
            return value.strip()

    def __repr__(self):
        return '<SongList %r>' % self.name
