import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from quantum_layer.satellite_qkd import SatelliteQKDSimulator

def test_link_budget():
    sat = SatelliteQKDSimulator()
    budget = sat.compute_link_budget()
    assert 'link_distance_km' in budget
    assert budget['link_distance_km'] > 0