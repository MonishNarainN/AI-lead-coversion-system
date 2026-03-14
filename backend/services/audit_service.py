import os
import json
import datetime
import logging

LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'audit.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

audit_logger = logging.getLogger('leadpro.audit')
handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
handler.setFormatter(logging.Formatter('%(message)s'))
audit_logger.addHandler(handler)
audit_logger.setLevel(logging.INFO)


def log_event(event_type: str, user: str, details: dict = None):
    """Write an immutable audit event to the audit log."""
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "event": event_type,
        "user": user,
        "details": details or {},
    }
    audit_logger.info(json.dumps(entry))
