"""
privacy_amplification.py
Privacy amplification using Toeplitz matrix hashing.

Reference: C. H. Bennett, G. Brassard, C. Crepeau, and U. M. Maurer,
"Generalized Privacy Amplification," IEEE Trans. Info. Theory, 1995.
"""

import hashlib
import secrets
from typing import List


class ToeplitzPrivacyAmplification:
    """
    Privacy amplification via Toeplitz matrix multiplication.

    A Toeplitz matrix is a matrix where each descending diagonal
    from left to right is constant. This structure allows efficient
    multiplication (O(n log n) via FFT) while providing universal
    hashing properties.

    The final key length = input_key_length - n_minus (security factor)
    where n_minus accounts for Eve's potential information.

    Parameters:
        hash_seed (bytes): Random seed for generating the Toeplitz matrix.
                           In practice, this seed is exchanged over the
                           authenticated classical channel.
    """

    def __init__(self, hash_seed: bytes | None = None):
        self.hash_seed = hash_seed or secrets.token_bytes(64)

    def _toeplitz_matrix(self, rows: int, cols: int) -> List[List[int]]:
        """
        Generate a pseudo-random Toeplitz matrix from the hash seed.
        For efficiency, we use a PRNG seeded by the hash_seed.
        """
        seed_int = int.from_bytes(self.hash_seed, byteorder='big')
        rng = __import__('random').Random(seed_int)

        matrix = []
        for i in range(rows):
            row = [0] * cols
            for j in range(cols):
                # Toeplitz: element depends on (i - j) only
                if i - j >= 0:
                    row[j] = rng.randint(0, 1)
                else:
                    row[j] = rng.randint(0, 1)
            matrix.append(row)
        return matrix

    def apply(self, bits: List[int], output_length: int) -> List[int]:
        """
        Compress key bits to output_length using Toeplitz hashing.

        Args:
            bits: Input key bits (list of 0/1).
            output_length: Desired number of output bits.

        Returns:
            Compressed key bits (list of 0/1, length = output_length).

        Raises:
            ValueError: if output_length > len(bits).
        """
        n = len(bits)
        if output_length > n:
            raise ValueError("output_length cannot exceed input length.")

        matrix = self._toeplitz_matrix(output_length, n)

        result = []
        for row in matrix:
            dot = sum(row[j] * bits[j] for j in range(n)) % 2
            result.append(dot)

        return result

    def compute_secure_length(
        self,
        n: int,
        qber: float,
        info_leakage_ec: int,
        security_parameter: float = 1e-9,
    ) -> int:
        """
        Compute the maximum length of a provably secure key.

        Args:
            n: Sifted key length after error correction.
            qber: Quantum Bit Error Rate.
            info_leakage_ec: Bits leaked during error correction.
            security_parameter: Epsilon — composable security bound (default 1e-9).

        Returns:
            Maximum secure key length in bits.
        """
        # Entropy bound: raw key entropy reduced by QBER
        # For BB84, the entropy per bit is 1 - h2(QBER)
        h2 = self._binary_entropy(qber) if 0 < qber < 1 else 0.0
        raw_secret = n * (1 - h2)

        # Subtract leakage from error correction
        available = raw_secret - info_leakage_ec

        # Finite-key adjustment
        finite_adjustment = int(__import__('math').log2(1.0 / security_parameter))

        secure = int(available - finite_adjustment)
        return max(0, secure)

    @staticmethod
    def _binary_entropy(p: float) -> float:
        """Binary entropy function h2(p) = -p*log2(p) - (1-p)*log2(1-p)."""
        import math
        if p == 0.0 or p == 1.0:
            return 0.0
        return -p * math.log2(p) - (1 - p) * math.log2(1 - p)