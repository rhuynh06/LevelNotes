from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON as SQLiteJSON
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    blocks = db.relationship('Block', backref='page', cascade='all, delete-orphan', order_by='Block.order_index')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title
        }
    
class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    type = db.Column(db.String, default='text')
    content = db.Column(SQLiteJSON, nullable=False, default={})
    order_index = db.Column(db.Integer)

    def to_dict(self):
        # For text blocks, content might be string or dict; normalize here
        if self.type == 'todo':
            # Expect content to be a dict with keys: checked (bool), text (str)
            checked = self.content.get('checked', False)
            text = self.content.get('text', '')
            content_repr = {'checked': checked, 'text': text}
        else:
            # For text blocks, content can be just a string or dict, normalize to string
            content_repr = self.content.get('text', '') if isinstance(self.content, dict) else self.content

        return {
            'id': self.id,
            'page_id': self.page_id,
            'type': self.type,
            'content': content_repr,
            'order_index': self.order_index
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    pages = db.relationship('Page', backref='user', lazy=True)

    word_count = db.Column(db.Integer, default=0)  # total words typed in lifetime

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
