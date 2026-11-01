from flask import Blueprint, request, jsonify, session
from crypto_engine.aes_encryptor import encrypt, decrypt

encrypt_bp = Blueprint('encrypt_bp', __name__)

_mem = {'ciphertext': None, 'tag': None, 'nonce': None}


@encrypt_bp.route('/encrypt', methods=['POST'])
def encrypt_message():
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'status': 'error', 'message': 'No message provided.'})
    key_hex = session.get('final_key')
    if not key_hex:
        return jsonify({'status': 'error', 'message': 'No key generated yet.'})
    ct_body, tag, nonce = encrypt(message, bytes.fromhex(key_hex))
    _mem['ciphertext'] = ct_body.hex()
    _mem['tag'] = tag.hex()
    _mem['nonce'] = nonce.hex()
    try:
        from database.db_connector import get_db
        conn = get_db(); c = conn.cursor()
        c.execute("INSERT INTO messages (ciphertext, authentication_tag, nonce) VALUES (%s,%s,%s)", (_mem['ciphertext'], _mem['tag'], _mem['nonce']))
        conn.commit(); c.close(); conn.close()
    except Exception:
        pass
    return jsonify({'status': 'encrypted', 'ciphertext_snippet': ct_body.hex()[:40] + '...'})


@encrypt_bp.route('/decrypt', methods=['POST'])
def decrypt_message():
    key_hex = session.get('final_key')
    if not key_hex:
        return jsonify({'status': 'error', 'message': 'No key generated yet.'})
    # Always use memory store (guaranteed)
    if not _mem['ciphertext']:
        return jsonify({'status': 'error', 'message': 'No message found. Encrypt a message first.'})
    try:
        plain = decrypt(bytes.fromhex(_mem['ciphertext']), bytes.fromhex(_mem['tag']), bytes.fromhex(_mem['nonce']), bytes.fromhex(key_hex))
        return jsonify({'status': 'decrypted', 'plaintext': plain})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Decryption failed: {str(e)}'})