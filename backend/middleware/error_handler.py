from flask import jsonify

def init_error_handlers(app):
    """Register global JSON error handlers on the Flask app."""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "details": str(e), "code": 400}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "details": "Valid token required", "code": 401}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden", "details": "Insufficient permissions", "code": 403}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "details": str(e), "code": 404}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File too large. Maximum is 500 MB.", "code": 413}), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error", "details": str(e), "code": 500}), 500
