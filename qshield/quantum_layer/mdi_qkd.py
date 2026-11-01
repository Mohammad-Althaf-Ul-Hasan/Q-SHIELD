"""
mdi_qkd.py
Measurement‑Device‑Independent QKD (MDI‑QKD) simulation.

In MDI‑QKD, Alice and Bob send qubits to an untrusted central
relay (Charlie), who performs a Bell‑state measurement.
Charlie's announcement allows Alice and Bob to distill a secret
key, even if Charlie is malicious.
"""

import random
from typing import Tuple, Optional


class MDIQKDSimulator:
    """
    MDI‑QKD protocol simulator.

    Alice and Bob independently prepare qubits in one of four states
    (Z‑basis: |0⟩,|1⟩; X‑basis: |+⟩,|−⟩). Charlie performs a Bell‑state
    measurement. Only when Alice and Bob used the X‑basis does the outcome
    contribute to the raw key (after basis reconciliation).

    Parameters:
        num_signals: Number of signals sent.
        qber_threshold: Maximum acceptable QBER.
    """

    # Bell states: |Φ+⟩, |Φ−⟩, |Ψ+⟩, |Ψ−⟩
    # In the X‑basis, when Alice prepares |+⟩ and Bob prepares |+⟩,
    # a successful BSM (|Ψ−⟩) yields correlated bits.
    BELL_STATES = {
        (0, 0, 0): 'Φ+',  # placeholder mapping
        (0, 0, 1): 'Φ-',
        (0, 1, 0): 'Ψ+',
        (0, 1, 1): 'Ψ−',
        (1, 0, 0): 'Ψ+',
        (1, 0, 1): 'Ψ−',
        (1, 1, 0): 'Φ+',
        (1, 1, 1): 'Φ−',
    }

    def __init__(self, num_signals: int = 512, qber_threshold: float = 0.11):
        self.num_signals = num_signals
        self.qber_threshold = qber_threshold

    def simulate(self) -> Tuple[Optional[bytes], dict]:
        """
        Run MDI‑QKD simulation.

        Returns:
            (final_key, stats) where stats includes QBER, num_bits, etc.
        """
        # Alice & Bob random bit & basis
        alice_bits = [random.randint(0, 1) for _ in range(self.num_signals)]
        alice_bases = [random.choice(['Z', 'X']) for _ in range(self.num_signals)]
        bob_bits = [random.randint(0, 1) for _ in range(self.num_signals)]
        bob_bases = [random.choice(['Z', 'X']) for _ in range(self.num_signals)]

        # Charlie's BSM outcomes (simplified: success probability ~50%)
        outcomes = []
        for i in range(self.num_signals):
            if alice_bases[i] == 'X' and bob_bases[i] == 'X':
                # In X‑basis, BSM succeeds with 50% probability
                if random.random() < 0.5:
                    # Correlated outcome
                    outcomes.append(alice_bits[i] ^ bob_bits[i] ^ 1)  # inverted for key
                else:
                    outcomes.append(None)  # lost
            else:
                # Z‑basis or mismatched basis: outcome discarded for key
                outcomes.append(None)

        # Sifting: keep only X‑basis with successful BSM
        raw_key = []
        for i, o in enumerate(outcomes):
            if o is not None:
                # Alice's bit is the reference; Bob's bit must be flipped based on outcome
                raw_key.append(alice_bits[i] ^ o)

        sample_size = min(len(raw_key) // 3, 50)
        if sample_size == 0:
            return None, {'error': 'Insufficient signals'}

        errors = sum(random.random() < 0.02 for _ in range(sample_size))  # simulate noise
        qber = errors / sample_size
        if qber > self.qber_threshold:
            return None, {'qber': qber, 'key_compromised': True}

        final = raw_key[sample_size:]
        # Convert to bytes
        key_bytes = int(''.join(str(b) for b in final[:256]), 2).to_bytes(32, 'big') if len(final) >= 256 else bytes(final)

        return key_bytes, {
            'signals_sent': self.num_signals,
            'sifted_bits': len(raw_key),
            'qber': qber,
            'key_length': len(key_bytes),
        }