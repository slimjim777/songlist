from music import db
from sqlalchemy.orm import validates
import datetime


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    role = db.Column(db.Enum('admin', 'standard', name='role_types'), default='standard')
    last_login = db.Column(db.DateTime())

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
