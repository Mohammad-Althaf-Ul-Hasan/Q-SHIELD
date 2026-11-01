import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from crypto_engine.pqc_handler import generate_keypair, encapsulate, decapsulate

def test_kem_roundtrip():
    pk, sk = generate_keypair()
    ct, ss_sender = encapsulate(pk)
    ss_receiver = decapsulate(sk, ct)
    assert ss_sender == ss_receiver
    assert len(ss_sender) == 32