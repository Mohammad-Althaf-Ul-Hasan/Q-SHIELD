"""
routes/key_routes.py
API endpoints for hybrid key generation and E91 protocol.
"""

import os
import hashlib
import random
from flask import Blueprint, request, jsonify, session

from quantum_layer.qkd_simulator import BB84Simulator
from quantum_layer.noise_models import NOISE_MODELS
from quantum_layer.e91_simulator import E91Simulator
from post_processing.cascade import CascadeErrorCorrection
from post_processing.privacy_amplification import ToeplitzPrivacyAmplification
from post_processing.finite_key_analysis import FiniteKeyAnalysis
from crypto_engine.pqc_handler import generate_keypair, encapsulate, decapsulate
from crypto_engine.qrng_client import fetch_quantum_bytes
from crypto_engine.hybrid_combiner import combine_keys
from crypto_engine.key_lifecycle import KeyLifecycleManager
from sockets.events import emit_event
from sockets.events import (
    EVENT_KEY_READY,
    EVENT_EVE_DETECTED,
    EVENT_ERROR,
    EVENT_STATUS_UPDATE,
)

key_bp = Blueprint('key_bp', __name__)
lifecycle_manager = KeyLifecycleManager()


def _execute_qkd_pipeline(qkd_key: bytes, qber: float, sifted_alice_bits, sifted_bob_bits, session_obj) -> dict:
    """Common post‑processing and key assembly."""
    cascade = CascadeErrorCorrection()
    corrected_bits, errors_corrected = cascade.correct(sifted_alice_bits, sifted_bob_bits)
    corrected_key_bytes = BB84Simulator._bits_to_bytes(corrected_bits)

    privacy = ToeplitzPrivacyAmplification()
    fka = FiniteKeyAnalysis()
    analysis = fka.compute_secret_key_rate(
        n_sifted=len(sifted_alice_bits),
        n_error_corrected=len(corrected_bits),
        qber=qber,
        bits_leaked_ec=cascade.get_info_leakage(len(sifted_alice_bits), errors_corrected),
    )

    if analysis['is_secure']:
        amplified_bits = privacy.apply(corrected_bits, analysis['secure_key_length'])
        qkd_key_final = BB84Simulator._bits_to_bytes(amplified_bits)
    else:
        qkd_key_final = corrected_key_bytes

    pk, sk = generate_keypair()
    ciphertext_pqc, pqc_shared_secret = encapsulate(pk)
    qrng_bytes = fetch_quantum_bytes(32)
    classical_bytes = os.urandom(32)
    final_key = combine_keys(qkd_key_final, pqc_shared_secret, qrng_bytes)

    key_entry = lifecycle_manager.create_key(final_key, session_id=session_obj.get('session_id'))
    session_obj['final_key'] = final_key.hex()
    session_obj['current_key_id'] = key_entry['key_id']

    emit_event(EVENT_KEY_READY, {
        'qber': round(qber * 100, 1),
        'secure_bits': analysis.get('secure_key_length', len(qkd_key_final)*8),
    })

    return {
        'status': 'success',
        'qber_percent': round(qber * 100, 1),
        'qkd_key_snippet': qkd_key_final.hex()[:24] + '...',
        'pqc_key_snippet': pqc_shared_secret.hex()[:24] + '...',
        'qrng_snippet': qrng_bytes.hex()[:24] + '...',
        'classical_key_snippet': classical_bytes.hex()[:24] + '...',
        'final_key_snippet': final_key.hex()[:24] + '...',
        'key_id': key_entry['key_id'],
        'errors_corrected': errors_corrected,
        'secure_key_bits': analysis.get('secure_key_length', 0),
        'secret_key_rate': analysis.get('secret_key_rate', 0),
    }


@key_bp.route('/generate_keys', methods=['POST'])
def generate_keys():
    """BB84 hybrid key generation."""
    data = request.get_json(silent=True) or {}
    num_bits = int(data.get('num_bits', 256))
    eavesdropper = bool(data.get('eavesdropper', False))
    attack_type = str(data.get('attack_type', 'intercept_resend'))
    eve_prob = float(data.get('eve_intercept_prob', 0.3))
    noise_model_name = str(data.get('noise_model', 'none'))
    noise_model = NOISE_MODELS.get(noise_model_name, NOISE_MODELS['none'])

    qkd = BB84Simulator(
        num_bits=num_bits,
        eavesdropper=eavesdropper,
        attack_type=attack_type,
        eve_intercept_prob=eve_prob,
        noise_model=noise_model,
        qber_threshold=0.11,
        on_event=emit_event,
    )

    try:
        qkd_key, qber = qkd.generate_key()
    except ValueError as e:
        emit_event(EVENT_ERROR, {'message': str(e)})
        return jsonify({'status': 'error', 'message': str(e)}), 400

    if qkd_key is None:
        emit_event(EVENT_STATUS_UPDATE, {'system_status': 'compromised'})
        return jsonify({
            'status': 'error',
            'message': f'Eavesdropper detected! QBER: {qber*100:.1f}% exceeds 11%.',
            'qber_percent': round(qber * 100, 1),
        })

    result = _execute_qkd_pipeline(qkd_key, qber, qkd.sifted_alice, qkd.sifted_bob, session)
    return jsonify(result)


@key_bp.route('/generate_keys_e91', methods=['POST'])
def generate_keys_e91():
    """E91 protocol key generation."""
    data = request.get_json(silent=True) or {}
    num_pairs = int(data.get('num_pairs', 256))
    eavesdropper = bool(data.get('eavesdropper', False))

    e91 = E91Simulator(num_pairs=num_pairs, eavesdropper=eavesdropper)
    key, stats = e91.simulate()

    if key is None or not stats.get('secure'):
        return jsonify({
            'status': 'error',
            'message': f'E91 protocol failed security check. S value: {stats.get("s_value", "N/A")}',
            's_value': stats.get('s_value'),
        })

    # For E91 we don't have separate sifted lists; we treat the key itself as sifted
    # and skip post-processing to keep the demo simple, or we could reuse the pipeline.
    # Here we generate a quick classical randomness for the post-processing placeholder.
    sifted_bits = [int(b) for byte in key for b in f'{byte:08b}']  # crude
    if len(sifted_bits) > 256:
        sifted_bits = sifted_bits[:256]
    result = _execute_qkd_pipeline(key, 0.0, sifted_bits, sifted_bits, session)
    return jsonify(result)