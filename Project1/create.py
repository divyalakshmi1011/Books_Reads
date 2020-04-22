from flask import Flask, session, request, render_template
from models import *

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://jenumarqtdtzgf:c9e7217407a0c348ffc7a8126cce68aa80d1ec84eb77112af7d88703be24705b@ec2-54-88-130-244.compute-1.amazonaws.com:5432/dcviid8iqa94rj'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

def main() :
    db.create_all()

if __name__ == "__main__" :

    with app.app_context() :
        main()