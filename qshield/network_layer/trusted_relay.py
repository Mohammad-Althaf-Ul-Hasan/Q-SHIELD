"""
trusted_relay.py
Trusted relay logic for QKD networks.

In a chain A -> T1 -> T2 -> B, the end-to-end key is established
by hopping through trusted intermediate nodes. Each link uses QKD.
"""

from typing import List


def forward_key_xor(keys: List[bytes]) -> bytes:
    """
    Combine multiple link keys into an end-to-end key using XOR.

    Alice shares K1 with T1 (first trusted node).
    T1 shares K2 with T2 (second trusted node).
    ...
    Tn shares Kn with Bob.

    The end-to-end key is K1 XOR K2 XOR ... XOR Kn.
    Bob can compute it after receiving the XORed values from each relay.
    Each intermediate node computes Ki XOR K(i+1) and sends it to Bob.
    """
    if not keys:
        raise ValueError("At least one key required.")
    result = keys[0]
    for k in keys[1:]:
        result = bytes(a ^ b for a, b in zip(result, k))
    return result


def relay_key(upstream_key: bytes, downstream_key: bytes) -> bytes:
    """
    Compute the relay message: upstream_key XOR downstream_key.
    This is what a trusted node sends to Bob so he can reconstruct the
    end‑to‑end key.
    """
    return bytes(a ^ b for a, b in zip(upstream_key, downstream_key))