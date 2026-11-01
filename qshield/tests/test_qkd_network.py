import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from network_layer.qkd_network import QKDNetwork

def test_network_creation():
    net = QKDNetwork()
    net.add_node('Alice')
    net.add_node('Bob')
    net.add_link('Alice', 'Bob', distance_km=10)
    assert len(net.nodes) == 2
    assert len(net.links) == 1

def test_network_simulation():
    net = QKDNetwork()
    net.add_node('A'); net.add_node('B')
    net.add_link('A', 'B', distance_km=5)
    net.simulate_all_links(num_bits=128)
    e2e = net.get_end_to_end_key('A', 'B')
    assert len(e2e) > 0