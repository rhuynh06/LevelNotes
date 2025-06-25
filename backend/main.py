# Work on LAST

from flask import request, jsonify
from config import app, db
from models import Page, Block

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # create database if not already created

    app.run(debug=True)

