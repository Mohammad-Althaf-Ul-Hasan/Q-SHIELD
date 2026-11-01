"""
quantum_benchmark.py
Benchmarking hybrid quantum-safe protocol.
"""

import time
from quantum_layer.qkd_simulator import BB84Simulator
from crypto_engine.pqc_handler import generate_keypair, encapsulate
from crypto_engine.qrng_client import fetch_quantum_bytes
from crypto_engine.hybrid_combiner import combine_keys


def benchmark_hybrid_protocol(num_bits: int = 256) -> dict:
    """Benchmark the full hybrid key generation pipeline."""
    start = time.perf_counter()

    # QKD
    qkd = BB84Simulator(num_bits=num_bits, eavesdropper=False)
    qkd_key, qber = qkd.generate_key()

    # PQC Kyber-512
    pk, sk = generate_keypair()
    ct, pqc_secret = encapsulate(pk)

    # QRNG
    qrng_bytes = fetch_quantum_bytes(32)

    # Combine
    final_key = combine_keys(qkd_key, pqc_secret, qrng_bytes)

    end = time.perf_counter()
    return {
        'algorithm': 'Q-SHIELD Hybrid (QKD+PQC+QRNG)',
        'time_seconds': round(end - start, 4),
        'qber_percent': round(qber * 100, 2),
        'pqc_algorithm': 'Kyber-512',
        'qrng_source': 'ANU Quantum Numbers (fallback os.urandom)',
        'final_key_size_bytes': len(final_key),
        'quantum_vulnerable': False,
    }