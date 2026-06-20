"""
KephalosData Backend - Flask app factory
"""

import os
import warnings

# Suppress multiprocessing resource_tracker warnings (e.g., from transformers)
# Must be set before other imports
warnings.filterwarnings("ignore", message=".*resource_tracker.*")

from flask import Flask, request, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import limiter
from .utils.logger import setup_logger, get_logger


def create_app(config_class=Config):
    """Flask应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 设置JSON编码：确保中文直接显示（而不是 \uXXXX 格式）
    # Flask >= 2.3 使用 app.json.ensure_ascii，旧版本使用 JSON_AS_ASCII 配置
    if hasattr(app, 'json') and hasattr(app.json, 'ensure_ascii'):
        app.json.ensure_ascii = False
    
    # Configure logger
    logger = setup_logger('kephalosdata')
    
    # Only log startup messages in the reloader sub-process (avoid duplicate logs in debug mode)
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    debug_mode = app.config.get('DEBUG', False)
    should_log_startup = not debug_mode or is_reloader_process
    
    if should_log_startup:
        logger.info("=" * 50)
        logger.info("KephalosData Backend starting...")
        logger.info("=" * 50)
    
    # CORS — restrict to configured origins (set CORS_ORIGINS env var in production)
    cors_origins = app.config.get('CORS_ORIGINS', ['*'])
    CORS(app, resources={r"/api/*": {"origins": cors_origins}}, supports_credentials=False)

    # Rate limiting
    limiter.init_app(app)

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify(success=False, error='Muitas requisições. Aguarde um momento.'), 429
    
    # Register simulation process cleanup function (ensure child processes are terminated on exit)
    from .services.simulation_runner import SimulationRunner
    SimulationRunner.register_cleanup()
    if should_log_startup:
        logger.info("Simulation process cleanup registered")
    
    # Request/response middleware
    @app.before_request
    def log_request():
        req_logger = get_logger('kephalosdata.request')
        req_logger.debug(f"{request.method} {request.path}")

    @app.after_request
    def add_security_headers(response):
        # Prevent MIME-type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Disallow embedding in iframes (clickjacking protection)
        response.headers['X-Frame-Options'] = 'DENY'
        # Limit referrer information sent to third parties
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # Disable browser caching for API responses
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        req_logger = get_logger('kephalosdata.request')
        req_logger.debug(f"→ {response.status_code}")
        return response
    
    # Register blueprints
    from .api import graph_bp, simulation_bp, report_bp
    from .api.stripe_bp import stripe_bp
    app.register_blueprint(graph_bp, url_prefix='/api/graph')
    app.register_blueprint(simulation_bp, url_prefix='/api/simulation')
    app.register_blueprint(report_bp, url_prefix='/api/report')
    app.register_blueprint(stripe_bp, url_prefix='/api/stripe')
    
    # Health check
    @app.route('/health')
    def health():
        return {'status': 'ok', 'service': 'KephalosData Backend'}
    
    if should_log_startup:
        logger.info("KephalosData Backend ready")
    
    return app

