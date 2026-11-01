"""
key_rate_forecaster.py
Predictive key rate forecasting using linear regression.

Models the trend of secret key rate over multiple QKD runs
and predicts future values based on the observed pattern.
"""

import numpy as np
from sklearn.linear_model import LinearRegression


class KeyRateForecaster:
    """
    Time‑series forecasting of secret key rate.

    Usage:
        forecaster = KeyRateForecaster()
        forecaster.add_observation(run_id=1, skr=5000.0, qber=2.1)
        forecaster.train()
        forecast = forecaster.predict(steps=3)
    """

    def __init__(self):
        self.run_ids = []
        self.skr_values = []          # secret key rate (bps)
        self.qber_values = []
        self.timestamps = []
        self.model = LinearRegression()
        self.trained = False
        self._counter = 0

    def add_observation(self, run_id: int = None, skr: float = 0.0, qber: float = 0.0):
        """
        Add a data point.

        Args:
            run_id: Optional run identifier. If None, auto‑incremented.
            skr: Secret key rate in bits per second.
            qber: QBER percentage.
        """
        self._counter += 1
        rid = run_id if run_id is not None else self._counter
        self.run_ids.append(rid)
        self.skr_values.append(skr)
        self.qber_values.append(qber)
        self.timestamps.append(len(self.timestamps))  # run index as timestamp

    def train(self):
        """Fit the linear regression model to current data."""
        if len(self.timestamps) < 2:
            raise ValueError("Need at least 2 observations to train.")
        X = np.array(self.timestamps).reshape(-1, 1)
        y = np.array(self.skr_values)
        self.model.fit(X, y)
        self.trained = True

    def predict(self, steps: int = 1) -> dict:
        """
        Forecast SKR for the next `steps` runs.

        Returns:
            dict with forecasted values and confidence band.
        """
        if not self.trained:
            raise RuntimeError("Model not trained. Call train() first.")
        last_idx = self.timestamps[-1] if self.timestamps else 0
        future_idx = np.arange(last_idx + 1, last_idx + 1 + steps).reshape(-1, 1)
        predictions = self.model.predict(future_idx)

        # Simple confidence band: ±1 standard deviation of residuals
        residuals = []
        if len(self.timestamps) >= 2:
            X_hist = np.array(self.timestamps).reshape(-1, 1)
            pred_hist = self.model.predict(X_hist)
            residuals = np.array(self.skr_values) - pred_hist
            std_resid = np.std(residuals) if len(residuals) > 1 else 0
        else:
            std_resid = 0

        return {
            'forecast': [round(p, 2) for p in predictions.tolist()],
            'lower_bound': [round(p - std_resid, 2) for p in predictions.tolist()],
            'upper_bound': [round(p + std_resid, 2) for p in predictions.tolist()],
            'trend': 'increasing' if predictions[-1] > predictions[0] else 'decreasing',
        }

    def get_summary(self) -> dict:
        """Return summary statistics of observed data."""
        if not self.skr_values:
            return {}
        return {
            'num_observations': len(self.skr_values),
            'mean_skr': round(np.mean(self.skr_values), 2),
            'std_skr': round(np.std(self.skr_values), 2),
            'min_skr': round(np.min(self.skr_values), 2),
            'max_skr': round(np.max(self.skr_values), 2),
        }