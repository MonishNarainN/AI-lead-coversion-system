import logging
import time
import uuid
import os
from flask import request, g

# Ensure logs directory exists BEFORE configuring file handler
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'api.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding='utf-8')
    ]
)
logger = logging.getLogger('leadpro')


def init_logger(app):
    """Register before/after request hooks on the Flask app."""

    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())[:8]

    @app.after_request
    def after_request(response):
        latency_ms = round((time.time() - g.start_time) * 1000, 2)
        logger.info(
            f"[{g.request_id}] {request.method} {request.path} "
            f"→ {response.status_code} ({latency_ms}ms)"
        )
        response.headers['X-Request-ID'] = g.request_id
        return response
