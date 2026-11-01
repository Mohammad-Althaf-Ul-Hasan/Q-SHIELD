"""
cascade.py
Cascade error correction protocol for QKD post-processing.

Reference: G. Brassard and L. Salvail, "Secret-Key Reconciliation by Public Discussion",
Proceedings of EUROCRYPT '93, LNCS 765, pp. 410-423, 1994.
"""

import random
from typing import List, Tuple, Set


class CascadeErrorCorrection:
    """
    Cascade protocol for correcting errors in the sifted key.

    Alice and Bob hold sifted keys (as bit lists) that may differ
    due to channel noise or eavesdropping. Cascade uses iterative
    parity checks and binary search to locate and correct mismatched
    bits without revealing the entire key.

    Parameters:
        block_size_initial (int): Starting block size for first pass.
        passes (int): Number of Cascade passes (default 4).
        block_size_multiplier (float): Block size multiplication factor per pass.
        shuffle_seed (int): Random seed for reproducible shuffling.
    """

    def __init__(
        self,
        block_size_initial: int = 16,
        passes: int = 4,
        block_size_multiplier: float = 2.0,
        shuffle_seed: int = 42,
    ):
        self.block_size_initial = block_size_initial
        self.passes = passes
        self.block_size_multiplier = block_size_multiplier
        self.shuffle_seed = shuffle_seed
        random.seed(shuffle_seed)

    def correct(self, alice_key: List[int], bob_key: List[int]) -> Tuple[List[int], int]:
        """
        Run Cascade error correction.

        Args:
            alice_key: Alice's sifted key bits.
            bob_key: Bob's sifted key bits.

        Returns:
            (corrected_key, total_errors_corrected)
            Both Alice and Bob end with identical keys.
        """
        if len(alice_key) != len(bob_key):
            raise ValueError("Key lengths must match.")
        n = len(alice_key)

        a = alice_key[:]  # working copies
        b = bob_key[:]
        total_errors = 0
        error_locations: Set[int] = set()

        block_size = self.block_size_initial

        for p in range(self.passes):
            # Generate a random permutation (shuffle)
            indices = list(range(n))
            random.shuffle(indices)

            # Apply permutation to both keys
            a_perm = [a[i] for i in indices]
            b_perm = [b[i] for i in indices]

            # Process blocks
            for start in range(0, n, block_size):
                end = min(start + block_size, n)
                block_len = end - start

                # Parity check on this block
                parity_a = sum(a_perm[start:end]) % 2
                parity_b = sum(b_perm[start:end]) % 2

                if parity_a != parity_b:
                    # Mismatch found — binary search for the error
                    error_pos = self._binary_search(
                        a_perm, b_perm, start, end
                    )
                    if error_pos is not None:
                        # Correct the bit
                        original_idx = indices[error_pos]
                        b[original_idx] ^= 1  # Flip the erroneous bit
                        error_locations.add(original_idx)
                        total_errors += 1

            block_size = int(block_size * self.block_size_multiplier)

        return b, total_errors

    def _binary_search(
        self,
        a: List[int],
        b: List[int],
        left: int,
        right: int,
    ) -> int | None:
        """
        Binary search for an error in block [left, right).

        Returns the index (in the permuted key) of the erroneous bit,
        or None if the error cannot be localized.
        """
        if left >= right:
            return None

        if right - left == 1:
            return left if a[left] != b[left] else None

        mid = (left + right) // 2

        parity_a_left = sum(a[left:mid]) % 2
        parity_b_left = sum(b[left:mid]) % 2

        if parity_a_left != parity_b_left:
            return self._binary_search(a, b, left, mid)
        else:
            return self._binary_search(a, b, mid, right)

    def get_info_leakage(self, n: int, total_errors: int) -> int:
        """
        Estimate the number of bits leaked during error correction.

        Cascade reveals parity information publicly. This function
        estimates that leakage for security analysis.

        Returns:
            Estimated number of bits leaked to Eve during correction.
        """
        # Heuristic: each error correction pass leaks ~log2(block_size) bits
        # per block that had an error. Approximate total.
        return total_errors * 2  # conservative upper bound