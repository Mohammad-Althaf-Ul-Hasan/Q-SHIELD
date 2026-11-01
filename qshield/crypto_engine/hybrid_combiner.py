"""
hybrid_combiner.py
Secure combination of multiple key sources using HKDF.
"""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def combine_keys(qkd_key: bytes, pqc_secret: bytes, qrng_bytes: bytes,
                 salt: bytes = None, info: bytes = b'Q-SHIELD hybrid key') -> bytes:
    """
    Derive a cryptographically strong key from three independent sources.

    Args:
        qkd_key: Key material from BB84 QKD (bytes, any length).
        pqc_secret: Shared secret from Kyber-512 KEM (32 bytes).
        qrng_bytes: True quantum random bytes (32 bytes).
        salt: Optional HKDF salt (if None, all-zeros).
        info: Context-specific label (binds the key to this application).

    Returns:
        32-byte final AES-256 key.
    """
    # Input key material (IKM) = concatenation of all three
    ikm = qkd_key + pqc_secret + qrng_bytes

    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=info,
    )
    return hkdf.derive(ikm)