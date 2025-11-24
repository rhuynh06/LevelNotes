from flask import Blueprint, request, jsonify, session
from models import db, Block, Page, User
from utils.helpers import get_current_user, count_words

blocks_bp = Blueprint('blocks', __name__)

@blocks_bp.route('/blocks', methods=['POST'])
def create_block():
    """Create a new block"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    page_id = data.get('page_id')
    block_type = data.get('type', 'text')
    content = data.get('content')
    order_index = data.get('order_index')

    page = Page.query.get(page_id)
    if not page or page.user_id != user.id:
        return jsonify({'error': 'Page not found or unauthorized'}), 404

    # Normalize content based on block type
    if block_type == 'todo':
        if not isinstance(content, dict):
            content = {'checked': False, 'text': ''}
        else:
            content.setdefault('checked', False)
            content.setdefault('text', '')
    else:
        if not isinstance(content, str):
            content = ''

    block = Block(
        page_id=page_id,
        type=block_type,
        content=content,
        order_index=order_index
    )
    db.session.add(block)

    # Add new block words to user's lifetime count
    words = count_words(content)
    user.word_count = (user.word_count or 0) + words

    db.session.commit()

    return jsonify(block.to_dict()), 201

@blocks_bp.route('/blocks/<int:block_id>', methods=['PUT'])
def update_block(block_id):
    """Update a block's content"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])
    block = Block.query.get_or_404(block_id)
    data = request.get_json()
    
    # Get previous word count
    old_word_count = count_words(block.content)

    # Update block content
    block.content = data.get('content')
    db.session.commit()

    # Get new word count
    new_word_count = count_words(block.content)

    # Calculate delta (only positive changes)
    delta = max(new_word_count - old_word_count, 0)

    # Update user's word count
    user.word_count = (user.word_count or 0) + delta
    db.session.commit()

    return jsonify(block.to_dict())

@blocks_bp.route('/blocks/<int:block_id>', methods=['DELETE'])
def delete_block(block_id):
    """Delete a block"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    block = Block.query.get_or_404(block_id)
    if block.page.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403

    # Subtract block words from user's lifetime count
    words = count_words(block.content)
    user.word_count = max(user.word_count - words, 0)

    db.session.delete(block)
    db.session.commit()
    
    return '', 204