"""
aes_encryptor.py
AES-256-GCM authenticated encryption.
"""

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt(plaintext: str, key: bytes) -> tuple:
    """
    Encrypt a plaintext string with AES-256-GCM.

    Args:
        plaintext: The message to encrypt.
        key: 32-byte symmetric key.

    Returns:
        (ciphertext_body, tag, nonce) -- all bytes.
        ciphertext_body and tag must be recombined for decryption.
    """
    nonce = os.urandom(12)          # 96-bit recommended for GCM
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext.encode(), None)

    # The library appends the 16-byte tag at the end internally.
    # We separate for cleaner storage.
    ciphertext_body = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]
    return ciphertext_body, tag, nonce


def decrypt(ciphertext_body: bytes, tag: bytes, nonce: bytes, key: bytes) -> str:
    """
    Decrypt a ciphertext with AES-256-GCM.

    Args:
        ciphertext_body: The encrypted message (without tag).
        tag: 16-byte authentication tag.
        nonce: 12-byte nonce.
        key: 32-byte symmetric key.

    Returns:
        Decrypted plaintext string.

    Raises:
        cryptography.exceptions.InvalidTag if tampered.
    """
    ciphertext_with_tag = ciphertext_body + tag
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    return plaintext.decode()