from flask_login import login_user, logout_user
from sqlalchemy.event import listens_for

from rapidpro_webhooks.apps.core.db import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    country = db.Column(db.String)
    country_slug = db.Column(db.String)
    group = db.Column(db.String)
    group_slug = db.Column(db.String)
    is_superuser = db.Column(db.Boolean, default=False)
    authenticated = db.Column(db.Boolean, default=False)

    @classmethod
    def create_superuser(cls, email, password):
        user = cls(email=email, password=password, is_superuser=True)
        db.session.add(user)
        db.session.commit()

    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def superuser(self):
        return self.is_superuser

    def login(self, password):
        if self.password == password:
            self.authenticated = True
            db.session.add(self)
            db.session.commit()
            login_user(self, remember=True)
            return True
        return False

    def create_slug(self):
        if self.country:
            self.country_slug = self.country.lower().replace(" ", "_")
        if self.group:
            self.group_slug = self.group.lower().replace(" ", "_")

    def logout(self):
        self.authenticated = False
        db.session.add(self)
        db.session.commit()
        logout_user()

    @classmethod
    def update_country_slug(cls):
        for obj in cls.query.all():
            obj.create_slug()
            db.session.add(obj)
            db.session.commit()


@listens_for(User, 'before_insert')
def create_slug(mapper, connect, self):
    self.create_slug()
