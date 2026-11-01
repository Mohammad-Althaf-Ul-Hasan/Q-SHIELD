"""
decoy_state.py
Decoy-state BB84 protocol implementation.
Defeats photon-number-splitting (PNS) attacks by inserting decoy pulses.
"""

import random
from typing import List, Tuple, Optional


class DecoyStateBB84:
    """
    Decoy-state protocol wrapper.
    
    Alice prepares three types of pulses:
        - Signal: high mean photon number (mu ≈ 0.8)
        - Decoy: low mean photon number (nu ≈ 0.1)
        - Vacuum: zero photons
    
    Eve cannot distinguish signal from decoy without disturbing the channel.
    
    Parameters:
        mu (float): Mean photon number for signal pulses (default 0.8).
        nu (float): Mean photon number for decoy pulses (default 0.1).
        decoy_fraction (float): Fraction of pulses that are decoys (default 0.3).
        vacuum_fraction (float): Fraction of pulses that are vacuum (default 0.1).
    """

    def __init__(
        self,
        mu: float = 0.8,
        nu: float = 0.1,
        decoy_fraction: float = 0.3,
        vacuum_fraction: float = 0.1,
    ):
        if not 0.0 < nu < mu:
            raise ValueError("Must have 0 < nu < mu")
        if not 0.0 <= decoy_fraction + vacuum_fraction <= 1.0:
            raise ValueError("decoy_fraction + vacuum_fraction must be <= 1.0")

        self.mu = mu
        self.nu = nu
        self.decoy_fraction = decoy_fraction
        self.vacuum_fraction = vacuum_fraction
        self.signal_fraction = 1.0 - decoy_fraction - vacuum_fraction

    def generate_pulse_intensities(self, num_pulses: int) -> List[str]:
        """
        Generate a sequence of pulse types.
        
        Returns:
            List of 'signal', 'decoy', or 'vacuum' for each pulse.
        """
        pulse_types = []
        for _ in range(num_pulses):
            r = random.random()
            if r < self.vacuum_fraction:
                pulse_types.append('vacuum')
            elif r < self.vacuum_fraction + self.decoy_fraction:
                pulse_types.append('decoy')
            else:
                pulse_types.append('signal')
        return pulse_types

    def simulate_photon_number(self, intensity: str) -> int:
        """
        Simulate the actual photon number in a pulse.
        
        Uses Poisson distribution with mean = mu for signal, nu for decoy, 0 for vacuum.
        """
        if intensity == 'vacuum':
            return 0
        mean = self.mu if intensity == 'signal' else self.nu
        # Poisson sampling using inverse transform
        L = pow(2.718, -mean)  # e^(-mean)
        k = 0
        p = 1.0
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    def pns_attack_possible(self, photon_number: int) -> bool:
        """
        Check if a PNS attack is possible on this pulse.
        
        PNS requires at least 2 photons — Eve steals one, forwards the rest.
        """
        return photon_number >= 2

    def estimate_pns_gain(
        self,
        total_pulses: int,
        detected_pulses: int,
        intensity: str,
    ) -> float:
        """
        Estimate the gain (detection probability) for a given intensity.
        
        In a secure protocol, decoy and signal gains should be consistent.
        A discrepancy indicates a PNS attack.
        
        Returns:
            Gain value. If decoy_gain significantly differs from signal_gain,
            an attack is suspected.
        """
        if total_pulses == 0:
            return 0.0
        return detected_pulses / total_pulses

    def verify_decoy_security(
        self,
        signal_pulses: int,
        signal_detected: int,
        decoy_pulses: int,
        decoy_detected: int,
        tolerance: float = 0.2,
    ) -> Tuple[bool, str]:
        """
        Verify that decoy-state statistics are consistent.
        
        If decoy gain deviates from signal gain by more than tolerance,
        a PNS attack may be in progress.
        
        Returns:
            (secure: bool, message: str)
        """
        signal_gain = self.estimate_pns_gain(signal_pulses, signal_detected, 'signal')
        decoy_gain = self.estimate_pns_gain(decoy_pulses, decoy_detected, 'decoy')

        if signal_pulses == 0 or decoy_pulses == 0:
            return True, "Not enough data for verification."

        relative_diff = abs(signal_gain - decoy_gain) / max(signal_gain, decoy_gain, 1e-9)

        if relative_diff > tolerance:
            return False, (
                f"Possible PNS attack detected! "
                f"Signal gain: {signal_gain:.3f}, "
                f"Decoy gain: {decoy_gain:.3f}, "
                f"Deviation: {relative_diff:.1%}"
            )
        return True, (
            f"Decoy-state statistics consistent. "
            f"Signal gain: {signal_gain:.3f}, "
            f"Decoy gain: {decoy_gain:.3f}"
        )


class BB84WithDecoyStates(BB84Simulator):
    """
    BB84 protocol enhanced with decoy-state method.
    
    Inherits from BB84Simulator and adds decoy-state security analysis.
    Import BB84Simulator from quantum_layer.qkd_simulator to use this.
    """
    # This is defined later in the integration phase
    # We'll complete this when building the advanced features
    pass