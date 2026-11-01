import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from quantum_layer.qkd_simulator import BB84Simulator
from crypto_engine.pqc_handler import generate_keypair, encapsulate
from crypto_engine.hybrid_combiner import combine_keys
from post_processing.finite_key_analysis import FiniteKeyAnalysis

def test_full_pipeline():
    # QKD
    sim = BB84Simulator(num_bits=128, eavesdropper=False)
    qkd_key, qber = sim.generate_key()
    assert qkd_key is not None

    # PQC
    pk, sk = generate_keypair()
    ct, ss = encapsulate(pk)

    # Combine
    final = combine_keys(qkd_key, ss, os.urandom(32))
    assert len(final) == 32

    # Analysis
    fka = FiniteKeyAnalysis()
    result = fka.compute_secret_key_rate(len(sim.sifted_alice), len(sim.sifted_alice), qber, 2)
    assert result['is_secure'] == True