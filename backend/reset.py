from models import db
from app import app
import os

if os.path.exists("mydatabase.db"):
    os.remove("mydatabase.db")

with app.app_context():
    db.create_all()
    print("Database reset successfully")
