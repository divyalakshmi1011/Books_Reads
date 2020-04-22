import hashlib, binascii, os

from flask import Flask, session, request, render_template, flash, redirect
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from create import app

app.secret_key = "c9e7217407a0c348ffc7a8126cce68aa80d1ec84eb77112af7d88703be24705b"
# @app.route("/")
# def index():
    # return "Project 1: TODO"

@app.route("/")
def index() :
    return render_template("index.html")

@app.route("/register")
def register() :
    return render_template("register.html")

@app.route("/profile", methods=["GET","POST"])
def profile() :
    if request.method == "GET" :
        return render_template("register.html")
    if request.method == "POST" :
        name = request.form.get("name")
        emailID = request.form.get("emailID")
        print(request.form.get("pwd"))
        password = request.form.get("pwd")
        gender = request.form["options"]
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash) 
        pass_word = (salt + pwdhash).decode('ascii')  
        user = User(name=name, email=emailID, password=password,gender=gender)
        try :
            db.session.add(user)
            db.session.commit()
            return render_template("profile.html", name=name, email=emailID,gender=gender)
        except Exception as exc:
            flash("An Account with same Email id already exists", "info")
            print(exc)
            return redirect("register")

@app.route("/login", methods=["GET", "POST"])
def login() :
    if request.method == "GET" :
        if session.get("user_email") :
            return render_template("user.html",name=name)
        else :
            return render_template("login.html")
    else :
        return render_template("login.html")

@app.route("/authenticate", methods=["GET", "POST"])
def authenticate() :
    if request.method == "POST" :
        emailID = request.form.get("emailID")
        user = User.query.filter_by(email=emailID).first()
        password = request.form.get("pwd")
        if user :
            salt = user.password[:64]
            stored_password = user.password[64:]
            pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt.encode('ascii'), 100000)
            pwdhash = binascii.hexlify(pwdhash).decode('ascii')
            if stored_password == pwdhash :
                session["user_email"] = user.email
                flash("Login Succesful !", "info")
                return redirect("user")
            else :
                flash("Please create an Account", "info")
                return redirect('register')
        else :
            flash("Please create an Account", "info")
            return redirect('register')

    else :
        
        if  session.get("user_email") :
            flash("Already Logged in !", "info")
            return redirect("user")

        return render_template("login.html")

@app.route("/logout")
def logout() :
    
    if session.get("user_email") :
        session.pop("user_email", None)
        flash("You have been Logged out !")
        return redirect("/")
    else :
        flash("Please Login", "info")
        return redirect("login")

@app.route("/user", methods=["GET", "POST"])
def user() :
    
    if session.get("user_email") :
        user_email = session["user_email"]
        books = Book.query.all()
        return render_template("user.html", user=user_email, books=books)
    else :
        flash("You are not logged in!")
        return redirect("login")

@app.route("/admin")
def admin() :
    users = User.query.order_by(User.timestamp.desc()).all()
    return render_template("admin.html", users=users)

@app.route("/bookpage")
def bookpage(isbn):
    # Get data about book from database
        result = db.execute("SELECT isbn, title, author, year FROM books WHERE id = :id",
        {"id": id})

        # Store isbn, title, author, year (in that order) in book_data
        for row in result:
            book_data = dict(row)

        # add book id to book_data
        book_data['id'] = id
        # Get all reviews on this book from reviews table
        result = db.execute("SELECT author, rating, review_text FROM reviews WHERE book_id = :id",
                            {"id": id})

        # Store all rows in a list of dicts
        review_rows = []

        for row in result:
            review_rows.append(dict(row))

        return render_template("book.html", book_data=book_data, review_rows=review_rows)

if __name__ == "__main__" :
    app.run(debug=True)
