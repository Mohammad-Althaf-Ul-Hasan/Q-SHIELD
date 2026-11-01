"""
classical_benchmark.py
Benchmarking classical cryptographic key generation (RSA, ECDH).
"""

import time
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives.asymmetric.ec import ECDH
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def benchmark_rsa_keygen(key_size: int = 2048) -> dict:
    """Benchmark RSA key pair generation."""
    start = time.perf_counter()
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=key_size, backend=default_backend()
    )
    end = time.perf_counter()
    public_key = private_key.public_key()
    return {
        'algorithm': 'RSA',
        'key_size': key_size,
        'time_seconds': round(end - start, 4),
        'public_key_size_bytes': public_key.key_size // 8,
        'quantum_vulnerable': True,  # Shor's algorithm
    }


def benchmark_ecdh_keygen(curve=ec.SECP256R1()) -> dict:
    """Benchmark ECDH key pair generation and shared secret derivation."""
    start = time.perf_counter()
    priv_a = ec.generate_private_key(curve, default_backend())
    pub_a = priv_a.public_key()
    priv_b = ec.generate_private_key(curve, default_backend())
    pub_b = priv_b.public_key()
    shared_a = priv_a.exchange(ECDH(), pub_b)
    shared_b = priv_b.exchange(ECDH(), pub_a)
    end = time.perf_counter()
    return {
        'algorithm': 'ECDH',
        'curve': curve.name,
        'time_seconds': round(end - start, 4),
        'shared_secret_size_bytes': len(shared_a),
        'quantum_vulnerable': True,  # Shor's algorithm
    }