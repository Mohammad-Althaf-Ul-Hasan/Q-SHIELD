"""
anomaly_detector.py
Quantum eavesdropping anomaly detection using SGDClassifier for online learning.
"""

import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


class EavesdroppingDetector:
    def __init__(self):
        self.model = make_pipeline(
            StandardScaler(),
            SGDClassifier(loss='log_loss', max_iter=1, tol=None, warm_start=True, random_state=42)
        )
        self.trained = False

    def _extract_features(self, run: dict) -> np.ndarray:
        qber = float(run.get('qber', 0))
        sifted = float(run.get('sifted_count', 0))
        errors_corrected = float(run.get('errors_corrected', 0))
        key_len = float(run.get('final_key_length', 0))
        return np.array([qber, sifted, errors_corrected, key_len])

    def train(self, runs: list, labels: list):
        X = np.array([self._extract_features(r) for r in runs])
        y = np.array(labels)
        self.model.fit(X, y)
        self.trained = True

    def partial_fit(self, runs: list, labels: list):
        """Incremental training with new data."""
        X = np.array([self._extract_features(r) for r in runs])
        y = np.array(labels)
        self.model.fit(X, y)  # SGD with warm_start continues training
        self.trained = True

    def predict(self, run: dict) -> dict:
        X = np.array([self._extract_features(run)])
        if not self.trained:
            qber = run.get('qber', 0)
            if qber > 10:
                return {'prediction': 'attack', 'confidence': 0.9}
            return {'prediction': 'normal', 'confidence': 0.7}
        pred = self.model.predict(X)[0]
        prob = self.model.predict_proba(X)[0]
        confidence = max(prob)
        return {
            'prediction': 'attack' if pred == 1 else 'normal',
            'confidence': round(confidence, 4),
        }

    def generate_synthetic_training_data(self, num_samples: int = 200) -> tuple:
        runs, labels = [], []
        for _ in range(num_samples // 2):
            qber = np.random.normal(2.0, 1.0)
            sifted = np.random.randint(100, 200)
            errors = int(sifted * max(0, qber/100))
            key_len = sifted - errors - 20
            runs.append({'qber': qber, 'sifted_count': sifted, 'errors_corrected': errors, 'final_key_length': max(0, key_len)})
            labels.append(0)
            qber_att = np.random.normal(15.0, 3.0)
            sifted_att = np.random.randint(80, 150)
            errors_att = int(sifted_att * max(0, qber_att/100))
            runs.append({'qber': qber_att, 'sifted_count': sifted_att, 'errors_corrected': errors_att, 'final_key_length': max(0, sifted_att - errors_att - 30)})
            labels.append(1)
        return runs, labels