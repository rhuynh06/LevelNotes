# Do LAST after setting configurations and database model

from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import db, Page, Block, User
from sqlalchemy import func, cast, String
from dotenv import load_dotenv
load_dotenv()
import os

# to get user_id
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

# count TOTAL words
def count_words(content):
    if content is None:
        return 0
    if isinstance(content, dict):
        text = content.get('text', '')
    else:
        text = str(content)
    
    # Normalize all whitespace
    text = ' '.join(text.split())
    return len(text.split()) if text else 0

# open app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True

CORS(app, origins=["http://localhost:5173", "https://rhuynh06.github.io"], supports_credentials=True)

# set CORS manually
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin')
    if origin in ['https://rhuynh06.github.io', 'http://localhost:5173']:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

# database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mydatabase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# connect database
db.init_app(app)

# return all pages
@app.route('/pages', methods=['GET'])
def get_pages():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    pages = Page.query.filter_by(user_id=user.id).order_by(Page.title).all() # Query all pages from DB (ordered by id)
    return jsonify([p.to_dict() for p in pages]) # Convert each to dict

# create a new page
@app.route('/pages', methods=['POST'])
def create_page():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() # Get JSON body from request
    page = Page(title=data['title'], user_id=user.id) # Create Page instance
    db.session.add(page) # Add to DB session
    db.session.commit() # Save to DB
    return jsonify(page.to_dict()), 201  # Return created page

# rename a page
@app.route('/pages/<int:page_id>', methods=['PUT'])
def update_page(page_id):
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

# delete a page
@app.route('/pages/<int:page_id>', methods=['DELETE'])
def delete_page(page_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    page = Page.query.get_or_404(page_id)
    if page.user_id != user.id:
        return jsonify({'error': 'Forbidden'}), 403

    db.session.delete(page)
    db.session.commit()
    return '', 204  # 204 No Content means success with no response body

# get all blocks for a page
@app.route('/pages/<int:page_id>/blocks')
def get_blocks(page_id):
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401

    page = Page.query.get(page_id)
    if not page or page.user_id != user.id:
        return jsonify({'error': 'Page not found or unauthorized'}), 404

    blocks = [block.to_dict() for block in page.blocks]
    return jsonify(blocks)

# create a new block
@app.route('/blocks', methods=['POST'])
def create_block():
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

# update a block's content
@app.route('/blocks/<int:block_id>', methods=['PUT'])
def update_block(block_id):
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

    # get new word count
    new_word_count = count_words(block.content)

    # Calculate delta (only positive changes)
    delta = max(new_word_count - old_word_count, 0)

    # Update user's word count
    user.word_count = (user.word_count or 0) + delta
    db.session.commit()

    return jsonify(block.to_dict())

# delete a block
@app.route('/blocks/<int:block_id>', methods=['DELETE'])
def delete_block(block_id):
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


# user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 400
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

# user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        return jsonify({'message': 'Logged in successfully'})
    return jsonify({'error': 'Invalid credentials'}), 401

# user logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out'})

# record user session
@app.route('/user/stats')
def user_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user = User.query.get(session['user_id'])

    def level_info(word_count):
        level = 0
        threshold = 1000
        while word_count >= threshold:
            level += 1
            threshold += 2 * (level - 1)

        return {
            'level': level,
            'progress': word_count,
            'next_level_words': threshold
        }

    info = level_info(user.word_count)

    return jsonify({
        'username': user.username,
        'word_count': user.word_count,
        'level': info['level'],
        'progress': info['progress'],
        'next_level_words': info['next_level_words']
    })

@app.route('/test-cors')
def test_cors():
    return jsonify({"ok": True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5050)