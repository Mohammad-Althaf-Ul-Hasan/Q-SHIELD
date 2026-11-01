import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from crypto_engine.key_lifecycle import KeyLifecycleManager

def test_create_and_validate():
    mgr = KeyLifecycleManager()
    entry = mgr.create_key(b'test_key_32_bytes_1234567890_ab')
    assert mgr.is_valid(entry['key_id']) == True

def test_revocation():
    mgr = KeyLifecycleManager()
    entry = mgr.create_key(b'another_key_32_bytes_1234567890')
    mgr.revoke_key(entry['key_id'])
    assert mgr.is_valid(entry['key_id']) == False