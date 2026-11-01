"""
pqc_handler.py
Post-Quantum Cryptography handler using Kyber-512 (NIST FIPS 203).
Falls back to simulation if the library is unavailable.
"""

# Try real Kyber-512, fall back to simulation
try:
    from kyber import Kyber512
    _REAL_KYBER = True
except ImportError:
    _REAL_KYBER = False
    import os
    import hashlib


def generate_keypair():
    """
    Generate a Kyber-512 keypair.

    Returns:
        (public_key, secret_key) -- both bytes.
    """
    if _REAL_KYBER:
        pk, sk = Kyber512.keygen()
        return pk, sk
    else:
        # Simulation placeholder
        sk = os.urandom(1632)   # Kyber-512 secret key size
        pk = hashlib.sha256(sk).digest()  # not real, just a demo
        return pk, sk


def encapsulate(public_key):
    """
    Encapsulate a shared secret using the recipient's public key.

    Returns:
        (ciphertext, shared_secret) -- both bytes (shared_secret is 32 bytes).
    """
    if _REAL_KYBER:
        ciphertext, shared_secret = Kyber512.enc(public_key)
        return ciphertext, shared_secret
    else:
        # Simulation placeholder
        shared_secret = os.urandom(32)
        ciphertext = hashlib.sha256(public_key + shared_secret).digest()
        return ciphertext, shared_secret


def decapsulate(secret_key, ciphertext):
    """
    Decapsulate the shared secret using the recipient's secret key.

    Returns:
        shared_secret -- 32 bytes.
    """
    if _REAL_KYBER:
        shared_secret = Kyber512.dec(secret_key, ciphertext)
        return shared_secret
    else:
        # Simulation: not reversible, just a placeholder
        return os.urandom(32)