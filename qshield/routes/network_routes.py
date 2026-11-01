"""
routes/network_routes.py
Multi‑node QKD network simulation with trusted‑relay chain.
"""

from flask import Blueprint, request, jsonify
from network_layer.qkd_network import QKDNetwork
from network_layer.trusted_relay import forward_key_xor

network_bp = Blueprint('network_bp', __name__)
demo_network = QKDNetwork()


@network_bp.route('/api/network/create', methods=['POST'])
def create_network():
    data = request.get_json() or {}
    global demo_network
    demo_network = QKDNetwork()
    for node in data.get('nodes', []):
        demo_network.add_node(node['id'], node.get('name', node['id']))
    for link in data.get('links', []):
        demo_network.add_link(link['node1'], link['node2'], distance_km=link.get('distance_km', 10), noise_model=link.get('noise_model', 'none'))
    return jsonify({'status': 'ok', 'nodes': len(demo_network.nodes), 'links': len(demo_network.links)})


@network_bp.route('/api/network/simulate', methods=['POST'])
def simulate_network():
    if not demo_network.nodes:
        return jsonify({'status': 'error', 'message': 'No network created yet.'}), 400
    try:
        demo_network.simulate_all_links(num_bits=256)
        summary = demo_network.get_network_summary()
        return jsonify({'status': 'ok', 'summary': summary})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@network_bp.route('/api/network/key/<path_a>/<path_b>', methods=['GET'])
def get_e2e_key(path_a, path_b):
    try:
        key = demo_network.get_end_to_end_key(path_a, path_b)
        return jsonify({'status': 'ok', 'key': key.hex()[:32] + '...'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@network_bp.route('/api/network/relay_chain', methods=['POST'])
def relay_chain():
    """Compute a key over a specified chain of nodes."""
    data = request.get_json() or {}
    chain = data.get('chain', [])
    if len(chain) < 2:
        return jsonify({'status': 'error', 'message': 'Chain must contain at least two nodes'}), 400
    try:
        # Create a temporary network for this chain
        temp_net = QKDNetwork()
        for node_id in chain:
            temp_net.add_node(node_id)
        for i in range(len(chain)-1):
            temp_net.add_link(chain[i], chain[i+1], distance_km=50)
        temp_net.simulate_all_links()
        keys = [temp_net.nodes[chain[i]].link_keys[chain[i+1]] for i in range(len(chain)-1)]
        e2e = forward_key_xor(keys)
        return jsonify({'status': 'ok', 'end_to_end_key': e2e.hex()[:32] + '...', 'chain_length': len(chain)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500