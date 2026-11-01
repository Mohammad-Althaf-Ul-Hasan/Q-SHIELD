"""
comparator.py
Side‑by‑side comparison of classical and quantum‑safe protocols.
"""

from benchmark.classical_benchmark import benchmark_rsa_keygen, benchmark_ecdh_keygen
from benchmark.quantum_benchmark import benchmark_hybrid_protocol


def run_full_comparison() -> list:
    """
    Run all benchmarks and return a list of results.
    """
    results = []
    results.append(benchmark_rsa_keygen(2048))
    results.append(benchmark_ecdh_keygen())
    results.append(benchmark_hybrid_protocol(num_bits=256))
    return results