"""
etsi_qkd_api.py
Implementation of ETSI GS QKD 014 REST API standard.

This module defines a Flask Blueprint that adheres to the
ETSI QKD 014 specification for key delivery between a
QKD device and an application.

Endpoints:
    GET  /api/v1/keys                - List available key IDs
    POST /api/v1/keys                - Request a new key
    GET  /api/v1/keys/<key_id>       - Retrieve a specific key
    DELETE /api/v1/keys/<key_id>     - Delete a key

Reference: ETSI GS QKD 014 V1.2.1 (2023-03)
"""

import uuid
import time
import hashlib
from flask import Blueprint, request, jsonify

# In‑memory key store (replace with database in production)
_etsi_key_store = {}

etsi_014_bp = Blueprint('etsi_014', __name__, url_prefix='/api/v1')

# Number of keys to keep in the pool (simplified)
KEY_POOL_SIZE = 10


@etsi_014_bp.route('/keys', methods=['GET'])
def list_keys():
    """Get IDs of available keys."""
    key_ids = list(_etsi_key_store.keys())
    return jsonify({
        'keys': key_ids,
    }), 200


@etsi_014_bp.route('/keys', methods=['POST'])
def request_key():
    """
    Request a new key.

    Request body (JSON):
        {
            "master_SAE_id": "app123",
            "slave_SAE_id": "app456",
            "size": 32  (default 32 bytes)
        }
    """
    data = request.get_json() or {}
    size = data.get('size', 32)
    # In a real system, this would trigger key generation via QKD.
    # Here we generate a random key (placeholder; later integrate with QKDNetwork).
    key = hashlib.sha256(str(time.time()).encode() + str(uuid.uuid4()).encode()).digest()[:size]
    key_id = str(uuid.uuid4())
    _etsi_key_store[key_id] = {
        'key': key.hex(),
        'created_at': time.time(),
        'size': size,
    }
    return jsonify({
        'key_id': key_id,
        'key': key.hex(),
    }), 201


@etsi_014_bp.route('/keys/<key_id>', methods=['GET'])
def get_key(key_id):
    """Retrieve a key by ID and delete it (one‑time pad style)."""
    entry = _etsi_key_store.pop(key_id, None)
    if entry is None:
        return jsonify({'error': 'Key not found'}), 404
    return jsonify({
        'key_id': key_id,
        'key': entry['key'],
    }), 200


@etsi_014_bp.route('/keys/<key_id>', methods=['DELETE'])
def delete_key(key_id):
    """Delete a key."""
    if key_id in _etsi_key_store:
        del _etsi_key_store[key_id]
        return '', 204
    return jsonify({'error': 'Key not found'}), 404