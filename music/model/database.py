from music import db


role_users = db.Table(
    'role_users',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    role_users = db.relationship('User', secondary=role_users, backref=db.backref('roles_ref', lazy='dynamic'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    firstname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    user_roles = db.relationship('Role', secondary=role_users, backref=db.backref('users_ref', lazy='dynamic'))

    def __init__(self, email, firstname, lastname):
        self.email = email
        self.firstname = firstname
        self.lastname = lastname

    @staticmethod
    def user_by_email(email):
        """
        Get the user by the Email address.
        """
        user = User.query.filter_by(email=email).first()
        return user

    def __repr__(self):
        return '<User %r>' % self.email
