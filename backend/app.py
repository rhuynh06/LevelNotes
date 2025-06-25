# Work on LAST

from flask import request, jsonify
from config import app, db
from models import Page, Block

@app.route('/api/pages', methods=['GET'])
def get_pages():
    pages = Page.query.all() # get all pages in database
    return jsonify([p.to_dict() for p in pages]) # convert to dict for python

@app.route('api/pages', methods=['POST'])
def create_pages():
    data = request.get_json()
    page = Page(title=data['title'], parent_id=data.get('parent_id'))
    db.session.add(page)
    db.session.commit()
    return jsonify(page.to_dict()), 201

@app.route('/api/pages/<int:page_id>blocks', methods=['GET'])
def get_blocks(page_id):
    blocks = Block.query.filter_by(page_id=page_id).order_by(Block.order_index).all()
    return jsonify([b.to_dict() for b in blocks])

@app.route('/api/blocks', method=['POST'])
def create_blocks():
    data = request.get_json()
    block = Block(
        page_id=data['page_id'],
        type=data['type'],
        content=data.get('content', ''),
        order_index=data['order_index']
    )
    db.session.add(block)
    db.session.commit()
    return jsonify(block.to_dict()), 201

@app.route('/api/blocks/<int:block_id>', methods=['PUT'])
def update_blocks(block_id):
    data = request.get_json()
    block = Block.query.get_or_404(block_id)
    block.content = data.get('content', block.content)
    db.session.commit()
    return jsonify(block.to_dict())

@app.route('/app/blocks/<int:block_id>', methods=['DELETE'])
def delete_blocks(block_id):
    block = Block.query.get_or_404(block_id)
    db.session.delete(block)
    db.session.commit()
    return '', 204

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # create database if not already created

    app.run(debug=True)

