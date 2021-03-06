import hashlib, binascii, os

from flask import Flask, session, request, render_template, flash, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from create import app
from datetime import timedelta
from sqlalchemy import or_, and_


app.secret_key = "1c488f4b4a21cd7fbc5007664656985c2459b2362cf1f88d44b97e750b0c14b2cf7bc7b792d3f45db"
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

        name = request.form.get("name").trim()

        emailID = request.form.get("emailID").trim()

        password = request.form.get("pwd").trim()

        dateOfBirth = request.form.get("dob")

        gender = request.form["options"]

        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')

        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)

        password = (salt + pwdhash).decode('ascii')

        user = User(name=name, email=emailID, password=password, dateOfBirth=dateOfBirth, gender=gender)

        try :

            db.session.add(user)

            db.session.commit()

            return render_template("profile.html", name=name, email=emailID, dob=dateOfBirth, gender=gender)

        except Exception as exc:

            flash("An Account with same Email id alresdy exists", "info")

            return redirect(url_for("register"))

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
    
@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def bookpage(isbn) :

    if request.method == "POST":

        if session.get("user_email"):

            comments = request.form.get('textarea')
            rating = request.form.get('star')

            if rating is None:
                rating=0
            review_data = Reviews.query.filter(and_(Reviews.isbn == isbn ,Reviews.emailid == session.get("user_email"))).first()

            if review_data is None:

                reviewobj = Reviews(isbn = isbn,emailid=session.get('user_email'),rating=rating,comments=comments)
                db.session.add(reviewobj)
                db.session.commit()
                print("inserted into db")
                existing_reviews = Reviews.query.filter_by(isbn =isbn).order_by(Reviews.timestamp.desc()).all()
                book_details = Book.query.get(isbn)

                return render_template("bookpage.html",details = existing_reviews , book = book_details)

            else:

                flash("You already reviewed this book  !")
                existing_reviews = Reviews.query.filter_by(isbn =isbn).order_by(Reviews.timestamp.desc()).all()
                book_details = Book.query.get(isbn)

                return render_template("bookpage.html",details = existing_reviews , book = book_details)
        else:

            flash("You cannot view this page unless you login!")
            return redirect(url_for("login"))

    elif request.method == "GET":

        if session.get('user_email') is  None:

            flash("You cannot view this page unless you login!")
            return redirect(url_for("login"))

        else:

            review_data = Reviews.query.filter(and_(Reviews.isbn == isbn ,Reviews.emailid == session.get("user_email"))).first()

            if review_data is not None:

                 flash("You already reviewed this book !")

            book_details = Book.query.get(isbn)
            existing_reviews = Reviews.query.filter_by(isbn =isbn).order_by(Reviews.timestamp.desc()).all()

            return render_template("bookpage.html", details=existing_reviews , book=book_details)

@app.route("/api/book" , methods=["GET","POST"])
def bookdetails():

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

        reviews = Reviews.query.filter_by(isbn=str(isbn)).order_by(Reviews.timestamp.desc()).all()

        reviewlist = []

        for review in reviews:

            temp1={}
            temp1["isbn"] = review.isbn
            temp1["emailid"] = review.emailid
            temp1["rating"] = review.rating
            temp1["comments"] = review.comments

            reviewlist.append(temp1)

        return jsonify({"book": book_details ,"reviews":reviewlist}),200

    except Exception as exe:
        print (exe)
        return jsonify({"error": "Server Error"}),500


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

        validEMail = User.query.get(email)

        if validEMail is None :
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
  
@app.route("/book/<string:isbn>", methods=["GET", "POST"])
def bookpage(isbn) :

    if request.method == "POST":
        # we have to check whether the user is logged in here also because he might give the rating, comments in the url itself
        if session.get("user_email"):

            comments = request.form.get('textarea')
            rating = request.form.get('star')

            if rating is None:
                rating=0
            review_data = Reviews.query.filter(and_(Reviews.isbn == isbn ,Reviews.emailid == session.get("user_email"))).first()

            if review_data is None:

                reviewobj = Reviews(isbn = isbn,emailid=session.get('user_email'),rating=rating,comments=comments)
                db.session.add(reviewobj)
                db.session.commit()
                print("inserted into db")
                existing_reviews = Reviews.query.filter_by(isbn =isbn).order_by(Reviews.timestamp.desc()).all()
                book_details = Book.query.get(isbn)

                return render_template("bookpage.html",details = existing_reviews , book = book_details)

            else:

                flash("You already reviewed this book  !")
                existing_reviews = Reviews.query.filter_by(isbn =isbn).order_by(Reviews.timestamp.desc()).all()
                book_details = Book.query.get(isbn)

                return render_template("bookpage.html",details = existing_reviews , book = book_details)
        else:

            flash("You cannot view this page unless you login!")
            return redirect(url_for("login"))

    elif request.method == "GET":

        if session.get('user_email') is  None:

            flash("You cannot view this page unless you login!")
            return redirect(url_for("login"))

        else:

            review_data = Reviews.query.filter(and_(Reviews.isbn == isbn ,Reviews.emailid == session.get("user_email"))).first()

            if review_data is not None:

                 flash("You already reviewed this book !")

            book_details = Book.query.get(isbn)
            existing_reviews = Reviews.query.filter_by(isbn =isbn).order_by(Reviews.timestamp.desc()).all()
            return render_template("bookpage.html",details = existing_reviews , book = book_details)


@app.route("/api/submit_review",methods=["GET","POST"])
def submit_review():
   # the user has given email, isbn and the review in the url . Now i have to get it.
    try:
        if (not request.is_json) :
            return jsonify({"error" : "not a json request"}), 400

        reqData = request.get_json()

        if( "isbn" not in reqData):
            return jsonify({"error" : "invalid param key"}), 400
        # email or session["email"]
        if("email" not in reqData):
            return jsonify({"error" : "invalid email"}), 400
        #render login page other wise

        if("comment" not in reqData):
            return jsonify({"error" : "no reviews given "}), 400

        if("rating" not in reqData):
            return jsonify({"error" : "no rating given"}), 400

        isbn = reqData.get("isbn")
        if len(isbn)!=10 :
            remain=10-len(isbn)
            zeros="0"*remain
            isbn=zeros+isbn

        book = Book.query.get(isbn)

        if book is None:
            return jsonify({"error" : "Invalid book isbn"}), 400

        email = reqData.get("email")
        review_data = Reviews.query.filter(and_(Reviews.isbn == isbn ,Reviews.emailid == email )).first()

        if review_data is not  None:
            return jsonify({"error" : "You already gave a review "}), 400
        if(review_data is None):
            comment = reqData.get("comment")

        rating = reqData.get("rating")
        # now add the review to the database

        reviewobj = Reviews(isbn = isbn,emailid=session['user_email'],rating=rating,comments=comment)
        db.session.add(reviewobj)
        db.session.commit()
        return jsonify({"email":email,"comment":comment,"rating":rating}) , 200

    except Exception as exe:
        print(exe)
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
