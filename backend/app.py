# Do LAST after setting configurations and database model

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, Page, Block

# open app
app = Flask(__name__)
CORS(app)  # enable CORS for frontend-backend communication (access to all, should change after testing)

# database configuration (using SQLite for local development)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# connect database
db.init_app(app)

# create tables automatically before the first request
@app.before_request
def create_tables():
    db.create_all()

# return all pages
@app.route('/pages', methods=['GET'])
def get_pages():
    pages = Page.query.order_by(Page.title).all()  # Query all pages from DB (ordered by title)
    return jsonify([p.to_dict() for p in pages])  # Convert each to dict

# create a new page
@app.route('/pages', methods=['POST'])
def create_page():
    data = request.get_json()  # Get JSON body from request
    page = Page(title=data['title'], parent_id=data.get('parent_id'))  # Create Page instance
    db.session.add(page)  # Add to DB session
    db.session.commit()  # Save to DB
    return jsonify(page.to_dict()), 201  # Return created page

# rename a page
@app.route('/pages/<int:page_id>', methods=['PUT'])
def update_page(page_id):
    data = request.get_json()
    page = Page.query.get_or_404(page_id)
    page.title = data.get('title', page.title)
    db.session.commit()
    return jsonify(page.to_dict())

# delete a page
@app.route('/pages/<int:page_id>', methods=['DELETE'])
def delete_page(page_id):
    page = Page.query.get_or_404(page_id)
    db.session.delete(page)
    db.session.commit()
    return '', 204  # 204 No Content means success with no response body

# get all blocks for a page
@app.route('/pages/<int:page_id>/blocks', methods=['GET'])
def get_blocks(page_id):
    blocks = Block.query.filter_by(page_id=page_id).order_by(Block.order_index).all()  # Fetch and sort blocks
    return jsonify([b.to_dict() for b in blocks])  # Return list

# create a new block
@app.route('/blocks', methods=['POST'])
def create_block():
    data = request.get_json()  # Get JSON data
    block = Block(
        page_id=data['page_id'],
        type=data['type'],
        content=data.get('content', ''),
        order_index=data['order_index']
    )
    db.session.add(block)
    db.session.commit()
    return jsonify(block.to_dict()), 201  # Return created block

# update a block's content
@app.route('/blocks/<int:block_id>', methods=['PUT'])
def update_block(block_id):
    data = request.get_json()
    block = Block.query.get_or_404(block_id)  # Get or 404 if not found
    block.content = data.get('content', block.content)  # Update content
    db.session.commit()
    return jsonify(block.to_dict())

# delete a block
@app.route('/blocks/<int:block_id>', methods=['DELETE'])
def delete_block(block_id):
    block = Block.query.get_or_404(block_id)
    db.session.delete(block)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)