"""
app.py
Q-SHIELD -- Quantum Secure Hybrid Integrated Encryption for Layered Data Distribution
Main Flask-SocketIO application entry point.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_socketio import SocketIO

from config import config
from database.db_connector import init_db
from blockchain.audit_trail import audit_chain


# ----------------------------------------------------------------------
# Application Factory
# ----------------------------------------------------------------------
def create_app():
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',
    )
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG
    app.config['ENV'] = config.ENV

    # ---- Logging -------------------------------------------------------
    if not os.path.exists('logs'):
        os.makedirs('logs')

    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=5_000_000,   # 5 MB
        backupCount=3,
    )
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Q-SHIELD starting up')  # fixed: regular hyphen

    # ---- WebSocket -----------------------------------------------------
    socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')
    
    # Attach socketio to app so other modules can import it if needed
    app.socketio = socketio

    # ---- Database Initialization ---------------------------------------
    try:
        init_db()
        app.logger.info('Database initialised')
    except Exception as e:
        app.logger.warning(f'Database initialisation skipped: {e}')

    # ---- Blockchain Audit Trail ----------------------------------------
    app.logger.info(
        f'Blockchain audit trail ready - {len(audit_chain.chain)} blocks'
    )

    # ---- Register Blueprints -------------------------------------------
    from routes.key_routes import key_bp
    from routes.encrypt_routes import encrypt_bp
    from routes.network_routes import network_bp
    from routes.benchmark_routes import benchmark_bp
    from routes.report_routes import report_bp
    from routes.satellite_routes import satellite_bp
    from routes.ml_routes import ml_bp
    from routes.etsi_routes import etsi_bp
    from routes.audit_routes import audit_bp

    app.register_blueprint(key_bp)
    app.register_blueprint(encrypt_bp)
    app.register_blueprint(network_bp)
    app.register_blueprint(benchmark_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(satellite_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(etsi_bp)
    app.register_blueprint(audit_bp)

    # ---- Error Pages ---------------------------------------------------
    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', code=404, message='Page not found'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', code=500, message='Internal server error'), 500

    # ---- Home Route ----------------------------------------------------
    @app.route('/')
    def index():
        """Serve the main multi-tab SPA."""
        return render_template('index.html')

    return app, socketio


# ----------------------------------------------------------------------
# Main Entry Point
# ----------------------------------------------------------------------
if __name__ == '__main__':
    flask_app, sio = create_app()
    flask_app.logger.info('Starting Q‑SHIELD server on http://127.0.0.1:5000')
    sio.run(flask_app, host='127.0.0.1', port=5000, debug=config.DEBUG)