"""
sockets/events.py
WebSocket event emitter for real‑time Q‑SHIELD protocol streaming.

This module is the single place that knows about Flask‑SocketIO.
Every other module simply calls emit_event(...) to push a real‑time
update to all connected browsers.
"""

from flask_socketio import emit

# ----------------------------------------------------------------------
# Event name constants — prevents typos across the codebase
# ----------------------------------------------------------------------
EVENT_QKD_START         = 'qkd_start'
EVENT_ALICE_PREPARED    = 'alice_prepared'
EVENT_BOB_MEASURED      = 'bob_measured'
EVENT_SIFTING_DONE      = 'sifting_done'
EVENT_QBER_COMPUTED     = 'qber_computed'
EVENT_KEY_READY         = 'key_ready'
EVENT_EVE_DETECTED      = 'eve_detected'
EVENT_ENCRYPT_START     = 'encrypt_start'
EVENT_ENCRYPT_DONE      = 'encrypt_done'
EVENT_DECRYPT_START     = 'decrypt_start'
EVENT_DECRYPT_DONE      = 'decrypt_done'
EVENT_ERROR             = 'qkd_error'
EVENT_STATUS_UPDATE     = 'status_update'


def emit_event(event_name: str, data: dict):
    """
    Emit a WebSocket event to all connected clients.

    Args:
        event_name: One of the EVENT_* constants above.
        data: Dictionary payload (will be JSON‑serialized automatically).

    If the SocketIO server is not running (e.g. during unit tests),
    this function fails silently.
    """
    try:
        emit(event_name, data, broadcast=True)
    except Exception:
        # SocketIO not initialised — ignore (useful during testing)
        pass