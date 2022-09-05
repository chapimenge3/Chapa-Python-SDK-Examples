from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name
    
    def __repr__(self):
        return '<User %r>' % self.email

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    year = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    price = db.Column(db.Float)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, title, author, year, user_id, price):
        self.title = title
        self.author = author
        self.year = year
        self.user_id = user_id
        self.price = price
    
    def __repr__(self):
        return '<Book %r>' % self.title

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    transaction_id = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    date = db.Column(db.DateTime)
    price = db.Column(db.Float)
    # status enum for transaction
    status = db.Column(db.Enum('pending', 'complete', 'cancelled'))
    chapa_url = db.Column(db.String(100), nullable=True) # url to the chapa checkout page

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __init__(self, user_id, book_id, date, price, chapa_url, transaction_id):
        self.user_id = user_id
        self.book_id = book_id
        self.date = date
        self.price = price
        self.chapa_url = chapa_url
        self.transaction_id = transaction_id
        self.status = 'pending'

    def __repr__(self):
        return '<Transaction %r>' % self.id
