"""
routes/satellite_routes.py
Satellite QKD simulation endpoints.
"""

from flask import Blueprint, request, jsonify
from quantum_layer.satellite_qkd import SatelliteQKDSimulator

satellite_bp = Blueprint('satellite_bp', __name__)


@satellite_bp.route('/api/satellite/link_budget', methods=['POST'])
def link_budget():
    """Calculate satellite QKD link budget."""
    data = request.get_json() or {}
    sat = SatelliteQKDSimulator(
        wavelength_nm=data.get('wavelength_nm', 1550),
        tx_aperture_diameter_m=data.get('tx_aperture_m', 0.3),
        rx_aperture_diameter_m=data.get('rx_aperture_m', 1.0),
        satellite_altitude_km=data.get('altitude_km', 500),
        zenith_angle_deg=data.get('zenith_deg', 0),
        atmospheric_attenuation_db=data.get('atmospheric_db', 3),
        detector_efficiency=data.get('detector_efficiency', 0.3),
        pulse_rate_hz=data.get('pulse_rate_hz', 100e6)
    )
    budget = sat.compute_link_budget()
    return jsonify(budget)