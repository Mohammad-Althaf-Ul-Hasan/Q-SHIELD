from flask import Blueprint, jsonify
etsi_bp = Blueprint('etsi_bp', __name__)

@etsi_bp.route('/api/v1/keys/<key_id>', methods=['GET'])
def get_key_etsi():
    return jsonify({'status': 'ok', 'message': 'ETSI QKD 014 API will be implemented later.'})