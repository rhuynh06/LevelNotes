from flask import Blueprint, request, jsonify
from models import db, Page
from utils.helpers import get_current_user

pages_bp = Blueprint('pages', __name__)

@pages_bp.route('/pages', methods=['GET'])
def get_pages():
    """Get all pages for current user"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    pages = Page.query.filter_by(user_id=user.id).order_by(Page.title).all()
    return jsonify([p.to_dict() for p in pages])

@pages_bp.route('/pages', methods=['POST'])
def create_page():
    """Create a new page"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    page = Page(title=data['title'], user_id=user.id)
    db.session.add(page)
    db.session.commit()
    
    return jsonify(page.to_dict()), 201

@pages_bp.route('/pages/<int:page_id>', methods=['PUT'])
def update_page(page_id):
    """Rename a page"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    page = Page.query.get_or_404(page_id)
    if page.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json()
    page.title = data.get('title', page.title)
    db.session.commit()
    
    return jsonify(page.to_dict())

@pages_bp.route('/pages/<int:page_id>', methods=['DELETE'])
def delete_page(page_id):
    """Delete a page"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    page = Page.query.get_or_404(page_id)
    if page.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403

    db.session.delete(page)
    db.session.commit()
    
    return '', 204

@pages_bp.route('/pages/<int:page_id>/blocks')
def get_blocks(page_id):
    """Get all blocks for a page"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    page = Page.query.get(page_id)
    if not page or page.user_id != user.id:
        return jsonify({'error': 'Page not found or unauthorized'}), 404

    blocks = [block.to_dict() for block in page.blocks]
    return jsonify(blocks)