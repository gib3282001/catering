from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.Text, nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    date = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, poster_id, date):
        self.event_name = name
        self.poster_id = poster_id
        self.date = date

    def __repr__(self):
        return '<Event {}>'.format(self.event_id)

signed_up = db.Table('signed_up',
db.Column('id_staff', db.Integer, db.ForeignKey('staff.staff_id'), primary_key=True),
db.Column('id_event', db.Integer, db.ForeignKey('event.event_id'), primary_key=True))

class Staff(db.Model):
    staff_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    following = db.relationship('Event', secondary=signed_up, backref='members')

    def __init__(self, username, pw):
        self.username = username
        self.password = pw

    def __repr__(self):
        return '<Staff {}>'.format(self.username)

class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    events = db.relationship('Event', backref='poster')

    def __init__(self, username, pw):
        self.username = username
        self.password = pw

    def __repr__(self):
        return '<Customer {}>'.format(self.username)
 