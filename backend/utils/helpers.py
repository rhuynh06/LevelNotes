from flask import session
from models import User

def get_current_user():
    """Get the currently logged-in user from session"""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)

def count_words(content):
    """Count words in text or dict content"""
    if content is None:
        return 0
    if isinstance(content, dict):
        text = content.get('text', '')
    else:
        text = str(content)
    
    # Normalize all whitespace
    text = ' '.join(text.split())
    return len(text.split()) if text else 0