"""
key_lifecycle.py
Key lifecycle management: ID generation, expiry, rotation, revocation.
"""

import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from config import config


class KeyLifecycleManager:
    """Manages encryption key lifecycle."""

    def __init__(self):
        self._keys = {}          # key_id -> key_data dict

    def create_key(self, key_bytes: bytes, session_id: str = None) -> dict:
        """
        Register a new key with unique ID and expiry.

        Returns:
            dict with key entry.
        """
        key_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        entry = {
            'key_id': key_id,
            'key_data': key_bytes.hex(),
            'key_fingerprint': hashlib.sha256(key_bytes).hexdigest()[:16],
            'created_at': now,
            'expires_at': now + timedelta(minutes=config.KEY_EXPIRY_MINUTES),
            'status': 'active',
            'session_id': session_id,
        }
        self._keys[key_id] = entry
        return entry

    def get_key(self, key_id: str) -> dict | None:
        """Retrieve key entry by ID."""
        return self._keys.get(key_id)

    def revoke_key(self, key_id: str):
        """Revoke a key."""
        if key_id in self._keys:
            self._keys[key_id]['status'] = 'revoked'

    def is_valid(self, key_id: str) -> bool:
        """Check if key is active and not expired."""
        entry = self._keys.get(key_id)
        if not entry or entry['status'] != 'active':
            return False
        if datetime.now(timezone.utc) > entry['expires_at']:
            entry['status'] = 'expired'
            return False
        return True

    def cleanup_expired(self):
        """Remove expired keys from memory."""
        now = datetime.now(timezone.utc)
        expired_ids = [
            kid for kid, e in self._keys.items()
            if now > e['expires_at']
        ]
        for kid in expired_ids:
            del self._keys[kid]
        return len(expired_ids)

    def list_active(self) -> list:
        """Return list of active key entries."""
        self.cleanup_expired()
        return [e for e in self._keys.values() if e['status'] == 'active']