import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from quantum_layer.noise_models import DepolarizingChannel, AmplitudeDampingChannel, PhaseDampingChannel, NoiselessChannel

def test_noiseless():
    nl = NoiselessChannel()
    assert nl.apply(0) == 0
    assert nl.apply(1) == 1

def test_depolarizing():
    dp = DepolarizingChannel(error_prob=0.0)
    assert dp.apply(0) == 0
    dp2 = DepolarizingChannel(error_prob=1.0)
    # With 100% error prob, output is random (0 or 1) — just check it's an int
    assert dp2.apply(0) in (0, 1)