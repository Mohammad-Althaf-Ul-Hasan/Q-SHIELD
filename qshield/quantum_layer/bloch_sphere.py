"""
bloch_sphere.py
Qubit state vector calculations for 3D Bloch sphere visualization.

Each qubit state is represented by spherical coordinates (theta, phi)
on the Bloch sphere. The state |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ) sin(θ/2)|1⟩.
"""

import math
from typing import Tuple


def state_to_bloch(bit: int, basis: str) -> Tuple[float, float]:
    """
    Convert a BB84 qubit to Bloch sphere angles (θ, φ) in radians.

    Args:
        bit: 0 or 1
        basis: 'Z' or 'X'

    Returns:
        (theta, phi) — polar angle from z‑axis, azimuthal angle.
    """
    if basis == 'Z':
        if bit == 0:    # |0⟩ → θ=0, φ=0 (north pole)
            return 0.0, 0.0
        else:           # |1⟩ → θ=π, φ=0 (south pole)
            return math.pi, 0.0
    else:  # X‑basis
        if bit == 0:    # |+⟩ = (|0⟩+|1⟩)/√2 → θ=π/2, φ=0
            return math.pi / 2, 0.0
        else:           # |−⟩ = (|0⟩-|1⟩)/√2 → θ=π/2, φ=π
            return math.pi / 2, math.pi


def bloch_to_cartesian(theta: float, phi: float) -> Tuple[float, float, float]:
    """
    Convert Bloch sphere coordinates to 3D Cartesian.
    Unit sphere radius = 1.

    Returns:
        (x, y, z)
    """
    x = math.sin(theta) * math.cos(phi)
    y = math.sin(theta) * math.sin(phi)
    z = math.cos(theta)
    return x, y, z