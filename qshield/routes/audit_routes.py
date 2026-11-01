"""
routes/audit_routes.py
Blockchain audit trail endpoints.
"""

from flask import Blueprint, jsonify
from blockchain.audit_trail import audit_chain

audit_bp = Blueprint('audit_bp', __name__)


@audit_bp.route('/api/audit/logs', methods=['GET'])
def get_audit_logs():
    """Return recent audit events."""
    events = audit_chain.get_events(limit=20)
    chain_valid = audit_chain.is_chain_valid()
    return jsonify({'events': events, 'chain_valid': chain_valid, 'chain_length': len(audit_chain.chain)})


@audit_bp.route('/api/audit/validate', methods=['GET'])
def validate_chain():
    """Check chain integrity."""
    valid = audit_chain.is_chain_valid()
    return jsonify({'valid': valid})