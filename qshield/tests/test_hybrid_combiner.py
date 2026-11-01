import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from crypto_engine.hybrid_combiner import combine_keys

def test_combine_keys():
    k1 = b'a' * 32
    k2 = b'b' * 32
    k3 = b'c' * 32
    result = combine_keys(k1, k2, k3)
    assert len(result) == 32
    # Same inputs should produce same output
    result2 = combine_keys(k1, k2, k3)
    assert result == result2