import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from post_processing.cascade import CascadeErrorCorrection
from post_processing.privacy_amplification import ToeplitzPrivacyAmplification
from post_processing.finite_key_analysis import FiniteKeyAnalysis

def test_cascade_no_errors():
    cascade = CascadeErrorCorrection()
    key = [1,0,1,1,0,0,1,0]*32
    corrected, errors = cascade.correct(key, key[:])
    assert errors == 0
    assert corrected == key

def test_privacy_amplification():
    pa = ToeplitzPrivacyAmplification()
    bits = [1,0,1,0]*64
    out = pa.apply(bits, 32)
    assert len(out) == 32

def test_finite_key_analysis():
    fka = FiniteKeyAnalysis()
    result = fka.compute_secret_key_rate(200, 180, 0.03, 10)
    assert result['is_secure'] == True
    assert result['secure_key_length'] > 0