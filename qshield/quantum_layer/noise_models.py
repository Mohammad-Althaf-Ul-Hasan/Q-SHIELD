"""
noise_models.py
Realistic quantum channel noise models for QKD simulation.
"""

import random
import math
from abc import ABC, abstractmethod


class NoiseModel(ABC):
    """Abstract base class for quantum channel noise."""

    @abstractmethod
    def apply(self, bit: int) -> int:
        """
        Apply noise to a qubit.
        
        Args:
            bit: The input bit (0 or 1).
            
        Returns:
            The output bit after noise (may be flipped).
        """
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class NoiselessChannel(NoiseModel):
    """Perfect quantum channel — no noise, no errors."""

    def apply(self, bit: int) -> int:
        return bit


class DepolarizingChannel(NoiseModel):
    """
    Depolarizing noise: qubit is replaced with maximally mixed state
    with probability p.
    
    This is the most common noise model in quantum information theory.
    """

    def __init__(self, error_prob: float = 0.02):
        if not 0.0 <= error_prob <= 1.0:
            raise ValueError("error_prob must be between 0 and 1")
        self.error_prob = error_prob

    def apply(self, bit: int) -> int:
        if random.random() < self.error_prob:
            return random.randint(0, 1)
        return bit

    def __repr__(self):
        return f"DepolarizingChannel(p={self.error_prob})"


class AmplitudeDampingChannel(NoiseModel):
    """
    Amplitude damping noise: models energy loss (|1⟩ → |0⟩ decay).
    
    This simulates photon loss in optical fiber, where a qubit in state |1⟩
    can spontaneously decay to |0⟩ with probability gamma.
    
    Args:
        gamma: Damping probability (0 to 1). Higher = more energy loss.
    """

    def __init__(self, gamma: float = 0.01):
        if not 0.0 <= gamma <= 1.0:
            raise ValueError("gamma must be between 0 and 1")
        self.gamma = gamma

    def apply(self, bit: int) -> int:
        if bit == 1 and random.random() < self.gamma:
            return 0  # Decay from |1⟩ to |0⟩
        return bit

    def __repr__(self):
        return f"AmplitudeDampingChannel(gamma={self.gamma})"


class PhaseDampingChannel(NoiseModel):
    """
    Phase damping (dephasing) noise: loss of phase information without energy loss.
    
    Affects superposition states. In BB84, this manifests as errors when
    measuring in the X-basis (|+⟩, |−⟩) but not in Z-basis.
    
    Since our simulation works at bit level, we model this as an increased
    error probability specifically for X-basis qubits.
    
    Args:
        lambda_param: Dephasing rate (0 to 1).
    """

    def __init__(self, lambda_param: float = 0.01):
        if not 0.0 <= lambda_param <= 1.0:
            raise ValueError("lambda_param must be between 0 and 1")
        self.lambda_param = lambda_param

    def apply(self, bit: int) -> int:
        # Dephasing causes errors in superposition states
        # At bit level: random flip with probability lambda/2
        if random.random() < (self.lambda_param / 2):
            return 1 - bit
        return bit

    def __repr__(self):
        return f"PhaseDampingChannel(lambda={self.lambda_param})"


class AtmosphericTurbulenceChannel(NoiseModel):
    """
    Atmospheric turbulence model for free-space QKD.
    
    Models beam wandering and scintillation effects that cause
    fluctuating transmission efficiency and random photon loss.
    
    Args:
        Cn2: Refractive index structure constant (typical: 1e-15 to 1e-13)
        link_distance_km: Link distance in kilometers.
        wavelength_nm: Optical wavelength in nanometers.
    """

    def __init__(
        self,
        Cn2: float = 1e-14,
        link_distance_km: float = 1.0,
        wavelength_nm: float = 1550.0,
    ):
        self.Cn2 = Cn2
        self.link_distance_km = link_distance_km
        self.wavelength_nm = wavelength_nm

        # Calculate Rytov variance (scintillation strength)
        k = 2 * math.pi / (wavelength_nm * 1e-9)
        self.rytov_variance = 1.23 * (k ** (7/6)) * (link_distance_km * 1000) ** (11/6) * Cn2

    def _scintillation_loss(self) -> float:
        """Estimate random loss due to atmospheric scintillation."""
        if self.rytov_variance < 0.3:
            # Weak turbulence regime
            return random.gauss(0, math.sqrt(self.rytov_variance))
        # Moderate to strong turbulence
        return abs(random.gauss(0, 0.5))

    def apply(self, bit: int) -> int:
        # Atmospheric effects cause photon loss rather than bit flips
        # Model: probability of losing the qubit increases with turbulence
        loss_prob = min(0.3, abs(self._scintillation_loss()))
        if random.random() < loss_prob:
            # Lost photon = random measurement result
            return random.randint(0, 1)
        return bit

    def __repr__(self):
        return (
            f"AtmosphericTurbulenceChannel("
            f"Cn2={self.Cn2:.1e}, "
            f"distance={self.link_distance_km}km, "
            f"wavelength={self.wavelength_nm}nm)"
        )


# Pre-built noise model instances for quick use
NOISE_MODELS = {
    'none': NoiselessChannel(),
    'depolarizing_low': DepolarizingChannel(error_prob=0.02),
    'depolarizing_medium': DepolarizingChannel(error_prob=0.05),
    'depolarizing_high': DepolarizingChannel(error_prob=0.10),
    'amplitude_damping': AmplitudeDampingChannel(gamma=0.03),
    'phase_damping': PhaseDampingChannel(lambda_param=0.04),
    'atmospheric': AtmosphericTurbulenceChannel(Cn2=1e-14, link_distance_km=2.0),
}