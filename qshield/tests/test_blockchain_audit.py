import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from blockchain.audit_trail import Blockchain

def test_genesis_block():
    bc = Blockchain(difficulty=1)
    assert len(bc.chain) == 1
    assert bc.is_chain_valid()

def test_add_event():
    bc = Blockchain(difficulty=1)
    bc.add_event({'event': 'test', 'qber': 2.5})
    assert len(bc.chain) == 2
    assert bc.is_chain_valid()