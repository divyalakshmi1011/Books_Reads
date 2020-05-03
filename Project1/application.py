import hashlib, binascii, os

from flask import Flask, session, request, render_template, flash, redirect, url_for,jsonify
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from create import app
from datetime import timedelta
from sqlalchemy import or_


app.permanent_session_lifetime = timedelta(minutes=30)

@app.route("/")
@app.route("/index")
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

        password = request.form.get("pwd")

        # dateOfBirth = request.form.get("dob")
        
        gender = request.form["options"]
        
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')

        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash) 

        password = (salt + pwdhash).decode('ascii')  

        user = User(name=name, email=emailID, password=password, gender=gender)

        try :

            db.session.add(user)
            
            db.session.commit()

            return render_template("profile.html", name=name, email=emailID, gender=gender)

        except Exception as exc:
            flash("An Account with same Email id alresdy exists", "info")
            return redirect("register")

@app.route("/login", methods=["GET", "POST"])
def login() :

    if request.method == "GET" :
        if session.get("user_email") :
            return redirect("search")
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
                session.permanent=True
                session.modified=True
                flash("Login Succesful !", "info")
                return redirect("/search")
            else :
                flash("Please create an Account", "info")
                return redirect('register')
        else :
            flash("Please create an Account", "info")
            return redirect('register')
    else :
        
        if  session.get("user_email") :
            flash("Already Logged in !", "info")
            return redirect("/search")

        return render_template("login.html")

@app.route("/logout")
def logout() :
    
    if session.get("user_email") :
        session.pop("user_email", None)
        flash("You have been Logged out !")
        return redirect("login")
    else :
        flash("Please Login", "info")
        return redirect("login")


@app.route("/book/<isbn>", methods=['GET','POST'])
def book(isbn):

    """ Save user review and load same page with reviews updated."""
    query = isbn
    book = Book.query.filter_by(isbn=query)
    review = Review.query.filter_by(isbn=query)
    # if not review :
    #     return render_template("review.html")
    # else:
    #     return render_template("book.html", book=book,reviews=review)
    if not review:
        return render_template("book.html", book=book,message="No Review")
    else:
        return render_template("book.html", book=book,reviews=review)
 


@app.route("/search", methods=["GET", "POST"])
def search() :
    
    if request.method == "GET" :
    
        if session.get("user_email") :
            email = session.get("user_email")
            return render_template("userHome.html", email=email)
        else :
            flash("Pleae Login", "info")
            return redirect("/login")
    
    if request.method == "POST" :

        if session.get("user_email") :
            query = request.form.get("search_item")
            query = "%{}%".format(query)
            books = Book.query.filter(or_(Book.isbn.ilike(query), Book.title.ilike(query), Book.author.ilike(query), Book.year.like(query)))
            session["query"] = query
            try :
                books[0].isbn
                return render_template("userHome.html", books=books)
            except Exception :
                flash("No Results Found")
                return render_template("userHome.html", books=books)
        else :
            flash("Please Login", "info")
            return redirect(url_for("login"))

    else :

        if session.get("user_email") :
            query = session.get("query")
            books = Book.query.filter(or_(Book.isbn.like(query), Book.title.like(query), Book.author.like(query), Book.year.like(query)))
            return render_template("userHome.html", books=books)
        else :
            flash("Please Login", "info")
            return redirect(url_for("login"))

@app.route("/api/search", methods=["POST"])
def searchAPI() :
    try :
        if (not request.is_json) :
            return jsonify({"error" : "not a json request"}), 400
        reqData = request.get_json()
        if "search" not in reqData:
            return jsonify({"error" : "missing search param"}), 400
        value = reqData.get("search")
        if len(value) == 0 :
            return jsonify({"error" : "no results found"}), 404
        if "email" not in reqData :
            return jsonify({"error" : "missing key email"}), 400
        email = reqData.get("email")
        isEmailExists = User.query.get(email)
        if isEmailExists is None :
            return jsonify({"error" : "not a registered email"}), 200
        query = "%{}%".format(value)
        books = Book.query.filter(or_(Book.isbn.ilike(query), Book.title.ilike(query), Book.author.ilike(query), Book.year.like(query)))
        try :
            books[0].isbn
            results = []
            for book in books :
                temp = {}
                temp["isbn"] = book.isbn
                temp["title"] = book.title
                temp["author"] = book.author
                temp["year"] = book.isbn
                results.append(temp)
            return jsonify({"books" : results}), 200
        except Exception as exc :
            return jsonify({"error" : "no results found"}), 404
    except Exception :
        return jsonify({"error" : "Server Error"}), 500

@app.route("/api/book", methods=["POST"])
def bookAPI() :
    try:
        if (not request.is_json) :
            return jsonify({"error" : "not a json request"}), 400
        reqData = request.get_json()
        print (reqData,"my book")
        if "isbn" not in reqData:
            return jsonify({"error" : "missing isbn param"}), 400
        if "email" not in reqData:
            return jsonify({"error" : "missing email"}), 400
        isbn = reqData.get("isbn")
        print (len(isbn))
        if len(isbn)!=10 :
            remain=10-len(isbn)
            zeros="0"*remain
            isbn=zeros+isbn
        book = Book.query.get(isbn)
        print (book,"query book")
        if book is None :
            return jsonify({"error" : "invalid isbn"})
        email = reqData.get("email")
        validEmail = User.query.get(email)
        if validEmail is None :
            return jsonify({"error" : "not a registered email"})
        book_details = {"isbn" : book.isbn, "title" : book.title, "author" : book.author, "year" : book.year}
        print ("isbn" , book.isbn, "title" , book.title, "author" , book.author, "year" , book.year)
        reviews = Review.query.filter_by(isbn=str(isbn));
        reviewlist = []
        for review in reviews:
            temp1={}
            temp1["isbn"] = review.isbn
            temp1["emailid"] = review.username
            temp1["rating"] = review.rating
            temp1["review"] = review.review
            reviewlist.append(temp1)
        return jsonify({"book": book_details ,"reviews":reviewlist}),200
    except Exception as exe:
        print (exe)
        return jsonify({"error": "Server Error"}),500

@app.route("/admin")
def admin() :
    if session.get("user_email") :
        users = User.query.order_by(User.timestamp.desc()).all()
        return render_template("admin.html", users=users)
    else :
        flash("Please Login First", "info")
        return redirect("/login")

if __name__ == "__main__" :
    app.run(debug=True)

    