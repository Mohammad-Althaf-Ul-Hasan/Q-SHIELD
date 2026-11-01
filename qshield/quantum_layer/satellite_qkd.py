"""
satellite_qkd.py
Satellite Quantum Key Distribution (SatQKD) simulator.
Models ground‑to‑LEO satellite quantum link using real physics.
"""

import math
import random
from typing import Tuple


class SatelliteQKDSimulator:
    """
    Simulates a QKD link between a ground station and a satellite.

    Parameters:
        wavelength_nm: Optical wavelength in nanometers (default 1550 nm).
        tx_aperture_diameter_m: Transmitter aperture diameter (default 0.3 m).
        rx_aperture_diameter_m: Receiver aperture diameter (default 1.0 m).
        satellite_altitude_km: Satellite altitude (default 500 km for LEO).
        zenith_angle_deg: Angle from zenith (0 = directly overhead).
        atmospheric_attenuation_db: Atmospheric loss (default 3 dB).
        detector_efficiency: Single‑photon detector efficiency (default 0.3).
        pulse_rate_hz: Pulse repetition rate (default 100e6 = 100 MHz).
    """

    def __init__(
        self,
        wavelength_nm: float = 1550.0,
        tx_aperture_diameter_m: float = 0.3,
        rx_aperture_diameter_m: float = 1.0,
        satellite_altitude_km: float = 500.0,
        zenith_angle_deg: float = 0.0,
        atmospheric_attenuation_db: float = 3.0,
        detector_efficiency: float = 0.3,
        pulse_rate_hz: float = 100e6,
    ):
        self.wavelength = wavelength_nm * 1e-9
        self.tx_diameter = tx_aperture_diameter_m
        self.rx_diameter = rx_aperture_diameter_m
        self.altitude = satellite_altitude_km * 1e3
        self.zenith_angle = math.radians(zenith_angle_deg)
        self.atmospheric_loss = atmospheric_attenuation_db
        self.detector_efficiency = detector_efficiency
        self.pulse_rate = pulse_rate_hz

    def _link_distance(self) -> float:
        """Slant range from ground to satellite."""
        Re = 6371e3  # Earth radius
        h = self.altitude
        z = self.zenith_angle
        return math.sqrt((Re + h) ** 2 - (Re * math.sin(z)) ** 2) - Re * math.cos(z)

    def _diffraction_loss_db(self) -> float:
        """Transmitter gain and diffraction loss."""
        L = self._link_distance()
        A_tx = math.pi * (self.tx_diameter / 2) ** 2
        # Diffraction‑limited divergence
        theta_div = self.wavelength / (math.pi * self.tx_diameter)
        A_rx = math.pi * (self.rx_diameter / 2) ** 2
        # Geometric loss
        geometric_loss = A_rx / (L ** 2 * theta_div ** 2) if theta_div > 0 else 1e-12
        return -10 * math.log10(max(geometric_loss, 1e-12))

    def compute_link_budget(self) -> dict:
        """Calculate the optical link budget."""
        L = self._link_distance()
        diff_loss = self._diffraction_loss_db()
        total_loss = diff_loss + self.atmospheric_loss
        transmittance = 10 ** (-total_loss / 10)

        # Photon number per pulse (assume mean photon number 0.1 for decoy‑state)
        mu = 0.1
        photons_per_pulse = mu * transmittance * self.detector_efficiency

        # Secret key rate estimate (simplified BB84 bound)
        sk_rate = self.pulse_rate * photons_per_pulse * 0.5  # 50% basis match

        return {
            'link_distance_km': L / 1e3,
            'diffraction_loss_db': round(diff_loss, 2),
            'total_loss_db': round(total_loss, 2),
            'transmittance': f'{transmittance:.2e}',
            'photons_per_pulse': f'{photons_per_pulse:.2e}',
            'estimated_skr_bps': round(sk_rate, 2),
            'altitude_km': self.altitude / 1e3,
            'zenith_angle_deg': math.degrees(self.zenith_angle),
        }

    def simulate_skr(self) -> float:
        """Return estimated secret key rate in bits per second."""
        budget = self.compute_link_budget()
        return budget['estimated_skr_bps']