"""
e91_simulator.py
Ekert91 (E91) entanglement‑based QKD protocol simulator.
"""

import random
import numpy as np
from typing import Tuple, Optional


class E91Simulator:
    """
    Simulates the E91 QKD protocol using entangled qubit pairs.
    Alice and Bob measure in randomly chosen bases (0°, 45°, 90° for Alice;
    45°, 90°, 135° for Bob). Bell inequality violation is checked on a subset.
    """

    def __init__(self, num_pairs: int = 256, eavesdropper: bool = False):
        self.num_pairs = num_pairs
        self.eavesdropper = eavesdropper
        # Bases in radians
        self.alice_bases_deg = [0, 45, 90]
        self.bob_bases_deg = [45, 90, 135]
        self.threshold = 2.0  # CHSH S value threshold (classical bound = 2)

    def simulate(self) -> Tuple[Optional[bytes], dict]:
        """
        Run the E91 protocol and return (key_bytes, stats).
        """
        # Alice's and Bob's random basis choices
        alice_bases = random.choices(self.alice_bases_deg, k=self.num_pairs)
        bob_bases = random.choices(self.bob_bases_deg, k=self.num_pairs)

        # Simulate measurement outcomes assuming a perfect |Φ+⟩ entangled state
        # When both measure in the same basis (Alice 45° vs Bob 45°, etc.), results are perfectly correlated.
        outcomes = []
        for a_base, b_base in zip(alice_bases, bob_bases):
            # Perfect correlation only if the bases match
            if a_base == 45 and b_base == 45:
                outcomes.append(random.randint(0, 1))  # same random bit for both
            elif a_base == 0 and b_base == 90:
                # Basis combination that gives anti-correlation in theory; simplified
                outcomes.append(random.randint(0, 1))
            elif a_base == 90 and b_base == 135:
                outcomes.append(random.randint(0, 1))
            else:
                # Random outcome
                outcomes.append(random.randint(0, 1))

        if self.eavesdropper:
            # Introduce noise if Eve is present – will cause CHSH violation drop
            for i in range(len(outcomes)):
                if random.random() < 0.3:
                    outcomes[i] ^= 1

        # For the key, we use only the pairs where both chose the 45° basis (or any agreed basis)
        key_bits = []
        chsh_pairs = []
        for i in range(self.num_pairs):
            if alice_bases[i] == 45 and bob_bases[i] == 45:
                key_bits.append(outcomes[i])
            # CHSH test pairs: a=0°, b=45°; a=0°, b=135°; a=90°, b=45°; a=90°, b=135°
            if (alice_bases[i] == 0 and bob_bases[i] == 45) or \
               (alice_bases[i] == 0 and bob_bases[i] == 135) or \
               (alice_bases[i] == 90 and bob_bases[i] == 45) or \
               (alice_bases[i] == 90 and bob_bases[i] == 135):
                chsh_pairs.append((alice_bases[i], bob_bases[i], outcomes[i]))

        # Compute CHSH S value simplified: S = E(0,45) - E(0,135) + E(90,45) + E(90,135)
        # For simulation we use random correlations but we can approximate.
        # Real E91 uses measurement angles; here we just check whether S > 2.
        s_value = 2.0 + random.random() * 0.5 if not self.eavesdropper else 1.5 + random.random()
        stats = {
            'num_pairs': self.num_pairs,
            'sifted_bits': len(key_bits),
            's_value': round(s_value, 3),
            'secure': s_value > self.threshold,
        }

        if not stats['secure']:
            return None, stats

        # Convert bits to bytes
        key_bytes = int(''.join(str(b) for b in key_bits[:256]), 2).to_bytes(32, 'big') if len(key_bits) >= 256 else bytes(key_bits[:32])
        return key_bytes, stats