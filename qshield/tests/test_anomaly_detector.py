import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ml_engine.anomaly_detector import EavesdroppingDetector

def test_synthetic_training():
    det = EavesdroppingDetector()
    runs, labels = det.generate_synthetic_training_data(50)
    assert len(runs) == 50
    assert len(labels) == 50
    det.train(runs, labels)
    result = det.predict({'qber': 2.0, 'sifted_count': 120, 'errors_corrected': 3, 'final_key_length': 100})
    assert result['prediction'] in ('normal', 'attack')