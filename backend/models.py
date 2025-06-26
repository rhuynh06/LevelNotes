# Work on Second (database model)

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True) # always required
    title = db.Column(db.String(100), nullable=False) # string of size up to 100, null values not allowed
    parent_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=True) 
    children = db.relationship('Page')
    blocks = db.relationship('Block', # Page contains Blocks
                             backref='page', # backref adds .page attr to each Block
                             cascade='all, delete-orphan') # cascade tells sqlalch if delete parent, auto delete all children

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'parent_id': self.parent_id
        }
    
class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False) # ex: text, todo, heading, etc
    content = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'page_id': self.page_id,
            'type': self.type,
            'content': self.content,
            'order_index': self.order_index
        }