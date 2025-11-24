from flask import jsonify

def register_blueprints(app):
    """Register all route blueprints"""
    from routes.auth import auth_bp
    from routes.pages import pages_bp
    from routes.blocks import blocks_bp
    from routes.users import users_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(blocks_bp)
    app.register_blueprint(users_bp)
    
    # Test route
    @app.route('/test-cors')
    def test_cors():
        return jsonify({"ok": True})