"""
routes/ml_routes.py
Machine learning anomaly detection endpoints with online learning.
"""

from flask import Blueprint, request, jsonify
from ml_engine.anomaly_detector import EavesdroppingDetector
from ml_engine.key_rate_forecaster import KeyRateForecaster

ml_bp = Blueprint('ml_bp', __name__)

detector = EavesdroppingDetector()
forecaster = KeyRateForecaster()
models_trained = False


@ml_bp.route('/api/ml/train', methods=['POST'])
def train_models():
    """Train the anomaly detector with synthetic data."""
    global models_trained
    runs, labels = detector.generate_synthetic_training_data(200)
    detector.train(runs, labels)
    models_trained = True
    for i in range(1, 11):
        forecaster.add_observation(run_id=i, skr=5000 + i*200 + (i-5)**2 * 10, qber=2.0 + 0.3*i)
    forecaster.train()
    return jsonify({'status': 'ok', 'message': 'Models trained successfully'})


@ml_bp.route('/api/ml/partial_train', methods=['POST'])
def partial_train():
    """Update models incrementally with a new run."""
    global models_trained
    if not models_trained:
        return jsonify({'status': 'error', 'message': 'Initial training required first'}), 400

    run_data = request.get_json() or {}
    label = run_data.get('label', 0)  # 0 normal, 1 attack
    features = {
        'qber': float(run_data.get('qber', 0)),
        'sifted_count': int(run_data.get('sifted_count', 100)),
        'errors_corrected': int(run_data.get('errors_corrected', 0)),
        'final_key_length': int(run_data.get('final_key_length', 100)),
    }
    detector.partial_fit([features], [label])

    # Also update forecaster
    forecaster.add_observation(skr=float(run_data.get('skr', 5000)), qber=features['qber'])
    forecaster.train()

    return jsonify({'status': 'ok', 'message': 'Model updated incrementally'})


@ml_bp.route('/api/ml/predict_attack', methods=['POST'])
def predict_attack():
    """Submit a protocol run for anomaly classification."""
    if not models_trained:
        return jsonify({'status': 'error', 'message': 'Models not trained yet'}), 400
    run = request.get_json() or {}
    result = detector.predict(run)
    return jsonify(result)


@ml_bp.route('/api/ml/forecast', methods=['GET'])
def forecast_skr():
    """Return SKR forecast for the next 3 runs."""
    if not models_trained:
        return jsonify({'status': 'error', 'message': 'Models not trained yet'}), 400
    forecast = forecaster.predict(3)
    summary = forecaster.get_summary()
    return jsonify({'forecast': forecast, 'summary': summary})