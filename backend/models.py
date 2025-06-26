from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import JSON as SQLiteJSON

db = SQLAlchemy()

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=True)
    children = db.relationship('Page', backref=db.backref('parent', remote_side=[id]))
    blocks = db.relationship('Block', backref='page', cascade='all, delete-orphan', order_by='Block.order_index')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'parent_id': self.parent_id
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
