"""
qkd_simulator.py
Pure-Python BB84 Quantum Key Distribution simulator.
Supports multiple attack types, noise models, and event emission for WebSocket streaming.
"""

import random
import time
import hashlib
import numpy as np
from typing import Optional, Callable, Dict, List, Tuple
from quantum_layer.noise_models import NoiseModel, NoiselessChannel


class BB84Simulator:
    """
    BB84 QKD protocol simulator with configurable parameters.
    
    Parameters:
        num_bits (int): Number of raw qubits Alice sends. Default 256.
        eavesdropper (bool): Enable Eve's attack. Default False.
        attack_type (str): Type of attack —
            'intercept_resend' (default),
            'photon_number_splitting',
            'faked_state',
            'collective'
        eve_intercept_prob (float): Probability Eve intercepts a given qubit (0.0 to 1.0).
        noise_model (NoiseModel): Quantum channel noise model. Default: NoiselessChannel().
        qber_threshold (float): Maximum acceptable QBER before key is discarded. Default 0.11.
        sample_fraction (float): Fraction of sifted key sacrificed for QBER estimation. Default 0.3.
        on_event (Optional[Callable]): Callback for WebSocket event emission.
            Signature: on_event(event_name: str, data: dict) -> None
            Events emitted:
                'qkd_start'       — protocol begins
                'alice_prepared'  — Alice has chosen bits and bases
                'bob_measured'    — Bob has measured all qubits
                'sifting_done'    — basis reconciliation complete
                'qber_computed'   — QBER calculated
                'key_ready'       — final key produced
                'eve_detected'    — eavesdropper detected, key discarded
                'qkd_error'       — protocol error
    """

    SUPPORTED_ATTACKS = [
        'intercept_resend',
        'photon_number_splitting',
        'faked_state',
        'collective',
    ]

    def __init__(
        self,
        num_bits: int = 256,
        eavesdropper: bool = False,
        attack_type: str = 'intercept_resend',
        eve_intercept_prob: float = 0.3,
        noise_model: Optional[NoiseModel] = None,
        qber_threshold: float = 0.11,
        sample_fraction: float = 0.3,
        on_event: Optional[Callable] = None,
    ):
        if num_bits < 16:
            raise ValueError("num_bits must be at least 16 to produce a usable key.")
        if attack_type not in self.SUPPORTED_ATTACKS:
            raise ValueError(f"attack_type must be one of {self.SUPPORTED_ATTACKS}")
        if not 0.0 <= eve_intercept_prob <= 1.0:
            raise ValueError("eve_intercept_prob must be between 0.0 and 1.0")

        self.num_bits = num_bits
        self.eavesdropper = eavesdropper
        self.attack_type = attack_type
        self.eve_intercept_prob = eve_intercept_prob
        self.noise_model = noise_model if noise_model is not None else NoiselessChannel()
        self.qber_threshold = qber_threshold
        self.sample_fraction = sample_fraction
        self.on_event = on_event or self._noop

        # State tracking
        self.alice_bits: List[int] = []
        self.alice_bases: List[int] = []
        self.bob_bases: List[int] = []
        self.bob_bits: List[int] = []
        self.sifted_alice: List[int] = []
        self.sifted_bob: List[int] = []
        self.qber: float = 0.0
        self.final_key: Optional[bytes] = None
        self.compromised: bool = False

    @staticmethod
    def _noop(*args, **kwargs):
        pass

    @staticmethod
    def _random_bits(n: int) -> List[int]:
        return [random.randint(0, 1) for _ in range(n)]

    @staticmethod
    def _random_bases(n: int) -> List[int]:
        # 0 = Z-basis (|0⟩, |1⟩), 1 = X-basis (|+⟩, |−⟩)
        return [random.randint(0, 1) for _ in range(n)]

    def generate_key(self) -> Tuple[Optional[bytes], float]:
        """
        Execute the full BB84 protocol.

        Returns:
            Tuple[Optional[bytes], float]: (final_key, qber).
            final_key is None if eavesdropping detected (QBER > threshold).
        """
        self._emit('qkd_start', {
            'num_bits': self.num_bits,
            'eavesdropper': self.eavesdropper,
            'attack_type': self.attack_type,
        })

        # ——— Step 1: Alice prepares qubits ———
        self.alice_bits = self._random_bits(self.num_bits)
        self.alice_bases = self._random_bases(self.num_bits)
        self._emit('alice_prepared', {
            'num_qubits': self.num_bits,
            'basis_distribution': {
                'Z': self.alice_bases.count(0),
                'X': self.alice_bases.count(1),
            },
        })

        # ——— Step 2: Bob chooses measurement bases ———
        self.bob_bases = self._random_bases(self.num_bits)

        # ——— Step 3: Quantum channel with Eve + noise ———
        self.bob_bits = []
        for i in range(self.num_bits):
            a_bit = self.alice_bits[i]
            a_basis = self.alice_bases[i]
            b_basis = self.bob_bases[i]

            # Eve attacks on some qubits
            qubit_intercepted = False
            if self.eavesdropper and random.random() < self.eve_intercept_prob:
                qubit_intercepted = True
                if self.attack_type == 'intercept_resend':
                    # Eve measures in random basis, resends result
                    eve_basis = random.randint(0, 1)
                    if eve_basis == a_basis:
                        eve_result = a_bit
                    else:
                        eve_result = random.randint(0, 1)
                    # Eve resends; Bob receives disturbed state
                    if b_basis == a_basis:
                        # But Eve disturbed it
                        self.bob_bits.append(random.randint(0, 1))
                    else:
                        self.bob_bits.append(random.randint(0, 1))

                elif self.attack_type == 'photon_number_splitting':
                    # PNS: Eve stores one photon, measures after basis revelation
                    # Causes no disturbance on multi-photon pulses, but we simulate disturbance
                    if a_basis == b_basis:
                        self.bob_bits.append(a_bit)  # Eve learns this bit
                    else:
                        self.bob_bits.append(random.randint(0, 1))

                elif self.attack_type == 'faked_state':
                    # Eve prepares a fake state based on her guess
                    if b_basis == a_basis:
                        self.bob_bits.append(a_bit)  # Eve guessed correctly
                    else:
                        self.bob_bits.append(random.randint(0, 1))

                elif self.attack_type == 'collective':
                    # Eve performs collective measurement — higher QBER
                    if a_basis == b_basis:
                        # 50% chance Eve gets the bit right even with matching bases
                        self.bob_bits.append(a_bit if random.random() < 0.7 else 1 - a_bit)
                    else:
                        self.bob_bits.append(random.randint(0, 1))
            else:
                # No Eve — apply noise model and basis matching
                if a_basis == b_basis:
                    # Same basis: result = Alice's bit, but channel may flip it
                    noisy = self.noise_model.apply(a_bit)
                    self.bob_bits.append(noisy)
                else:
                    # Different basis: random result
                    self.bob_bits.append(random.randint(0, 1))

        self._emit('bob_measured', {
            'num_measured': self.num_bits,
            'intercepted_count': sum(1 for i in range(self.num_bits)
                                     if self.eavesdropper and random.random() < self.eve_intercept_prob),
        })

        # ——— Step 4: Sifting ———
        self.sifted_alice = []
        self.sifted_bob = []
        for a_bit, a_basis, b_bit, b_basis in zip(
            self.alice_bits, self.alice_bases, self.bob_bits, self.bob_bases
        ):
            if a_basis == b_basis:
                self.sifted_alice.append(a_bit)
                self.sifted_bob.append(b_bit)

        if len(self.sifted_alice) < 8:
            self._emit('qkd_error', {'message': 'Insufficient sifted bits.'})
            raise ValueError("Not enough matching bases to establish a key. Increase num_bits.")

        self._emit('sifting_done', {
            'sifted_count': len(self.sifted_alice),
            'discarded_count': self.num_bits - len(self.sifted_alice),
        })

        # ——— Step 5: QBER estimation ———
        sample_size = max(1, int(len(self.sifted_alice) * self.sample_fraction))
        sample_size = min(sample_size, 80)
        errors = sum(
            self.sifted_alice[i] != self.sifted_bob[i]
            for i in range(sample_size)
        )
        self.qber = errors / sample_size if sample_size > 0 else 0.0

        self._emit('qber_computed', {
            'qber': round(self.qber * 100, 1),
            'sample_size': sample_size,
            'errors': errors,
        })

        # ——— Step 6: Eavesdropper threshold check ———
        if self.qber > self.qber_threshold:
            self.compromised = True
            self.final_key = None
            self._emit('eve_detected', {
                'qber': round(self.qber * 100, 1),
                'threshold': round(self.qber_threshold * 100, 1),
            })
            return None, self.qber

        # ——— Step 7: Discard sample bits ———
        self.sifted_alice = self.sifted_alice[sample_size:]
        self.sifted_bob = self.sifted_bob[sample_size:]

        # ——— Step 8: Convert to bytes ———
        self.final_key = self._bits_to_bytes(self.sifted_alice)

        self._emit('key_ready', {
            'key_length_bytes': len(self.final_key),
            'key_bit_length': len(self.sifted_alice),
            'qber': round(self.qber * 100, 1),
        })

        return self.final_key, self.qber

    @staticmethod
    def _bits_to_bytes(bits: List[int]) -> bytes:
        """Convert bit list to bytes, zero-padded to byte boundary."""
        bits_copy = bits[:]
        while len(bits_copy) % 8 != 0:
            bits_copy.append(0)
        byte_array = bytearray()
        for i in range(0, len(bits_copy), 8):
            byte_val = 0
            for j in range(8):
                byte_val = (byte_val << 1) | bits_copy[i + j]
            byte_array.append(byte_val)
        return bytes(byte_array)

    def _emit(self, event: str, data: dict):
        """Emit an event via the callback, if set."""
        try:
            self.on_event(event, data)
        except Exception:
            pass  # Never let event errors break the protocol

    def get_summary(self) -> dict:
        """Return a summary of the last protocol run."""
        return {
            'num_bits': self.num_bits,
            'attack_type': self.attack_type,
            'qber': round(self.qber * 100, 1),
            'sifted_count': len(self.sifted_alice),
            'final_key_length': len(self.final_key) if self.final_key else 0,
            'compromised': self.compromised,
            'noise_model': self.noise_model.__class__.__name__,
        }