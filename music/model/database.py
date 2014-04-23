from music import db
from sqlalchemy.orm import validates


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    role = db.Column(db.Enum('admin', 'standard', name='role_types'), default='standard')
    #user_roles = db.relationship('Role', secondary=role_users, backref=db.backref('users_ref', lazy='dynamic'))

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
        
    def __repr__(self):
        return '<User %r>' % self.email
