from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import ForeignKey


db = SQLAlchemy()

class User(db.Model):
    __tablename__="UserDetails"

    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=True)
    gender = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, name, email, password,gender) :

        self.name = name
        self.email = email
        self.password = password
        self.gender = gender
        self.timestamp = datetime.now()

class Book(db.Model) :

    __tablename__="books"

    isbn = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)

    def __init__(self, isbn, title, author, year) :
        
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year

    def __repr__(self) :

        return "ISBN : " + self.isbn + " | Title : " + self.title + " | Author : " + self.author + " | Year : " + self.year

class Review(db.Model):
    _tablename_ = "Review"
    email = db.Column(db.String, ForeignKey("UserDetails.email"), primary_key=True)
    isbn = db.Column(db.String, ForeignKey("books.isbn"), nullable=False, primary_key=True)
    rating = db.Column(db.String, nullable=False)
    review = db.Column(db.String, nullable=False)
    
    def __init__(self, email, isbn, rating, review) :
        
        self.isbn = isbn
        self.email = email
        self.rating = rating
        self.review = review