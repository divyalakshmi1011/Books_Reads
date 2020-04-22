import os

from flask import Flask, session, request, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


@app.route("/")
@app.route("/register")
def index() :
    return render_template("Register.html")

@app.route("/profile", methods=["GET","POST"])
def profile() :
    user_details = []
    name = request.form.get("name")
    user_details.append(name)
    emailID = request.form.get("emailID")
    user_details.append(emailID)
    if request.form.get("male") == "on" :
        user_details.append("Male")
    else :
        user_details.append("Female")
    if request.method == "GET" :
        return render_template("Register.html")
    if request.method == "POST" :
        return render_template("Profile.html", user_details=user_details)

if __name__ == "__main__" :
    app.run()