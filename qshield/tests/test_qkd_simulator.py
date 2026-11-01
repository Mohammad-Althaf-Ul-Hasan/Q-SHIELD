import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from quantum_layer.qkd_simulator import BB84Simulator

def test_generate_key_no_eve():
    sim = BB84Simulator(num_bits=256, eavesdropper=False)
    key, qber = sim.generate_key()
    assert key is not None
    assert len(key) > 0
    assert 0.0 <= qber <= 0.11

def test_eve_detection():
    sim = BB84Simulator(num_bits=256, eavesdropper=True, eve_intercept_prob=0.8)
    key, qber = sim.generate_key()
    # With high intercept probability, key should be None (compromised)
    assert key is None or qber > 0.05