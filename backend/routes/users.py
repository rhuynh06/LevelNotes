from flask import Blueprint, jsonify, session
from models import User

users_bp = Blueprint('users', __name__)

@users_bp.route('/user/stats')
def user_stats():
    """Get user statistics (word count, level, progress)"""
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