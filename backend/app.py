from flask import Flask, request
from flask_cors import CORS
from utils.config import configure_app
from models import db
from routes import register_blueprints
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    configure_app(app)
    
    # CORS setup
    CORS(app, origins=[
        "http://localhost:5173",
        "https://rhuynh06.github.io"
    ], supports_credentials=True)
    
    @app.after_request # after every request processed (right before response sent to client)
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin in ['https://rhuynh06.github.io', 'http://localhost:5173']:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    register_blueprints(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5050)