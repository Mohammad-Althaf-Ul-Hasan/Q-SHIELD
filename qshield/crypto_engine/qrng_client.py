"""
qrng_client.py
True Quantum Random Number Generator client.
Fetches quantum entropy from ANU QRNG cloud service.
"""

import requests
import os
from config import config


def fetch_quantum_bytes(length=32, timeout=5):
    """
    Fetch quantum random bytes from ANU QRNG API.

    Args:
        length: Number of bytes required (default 32).
        timeout: HTTP request timeout in seconds.

    Returns:
        bytes of length `length` filled with quantum randomness.
        Falls back to os.urandom if the API is unreachable.
    """
    url = config.QRNG_API_URL
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        # ANU API returns {'success': True, 'data': [int, int, ...]}
        if data.get('success') and isinstance(data.get('data'), list):
            raw = data['data'][:length]
            return bytes(raw)

        raise ValueError('Invalid QRNG response format')
    except Exception as e:
        print(f"QRNG fetch failed: {e}. Falling back to os.urandom.")
        return os.urandom(length)