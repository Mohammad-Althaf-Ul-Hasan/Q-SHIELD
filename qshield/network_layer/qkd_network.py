"""
qkd_network.py
Multi‑node Quantum Key Distribution network simulator.

Supports arbitrary graph topologies. Nodes represent QKD devices.
Edges represent quantum links (optical fiber or free‑space).
The simulator generates pairwise keys on each link, then uses trusted
relays to establish end‑to‑end keys between any pair of nodes.
"""

import random
import time
from typing import Dict, List, Tuple, Optional

from quantum_layer.qkd_simulator import BB84Simulator
from network_layer.trusted_relay import forward_key_xor, relay_key


class QKDNode:
    """A node (QKD device) in the network."""

    def __init__(self, node_id: str, name: str = ""):
        self.node_id = node_id
        self.name = name or node_id
        self.neighbors: Dict[str, 'QKDNode'] = {}
        self.link_keys: Dict[str, bytes] = {}  # neighbor_id -> shared key


class QKDNetwork:
    """
    Multi‑node QKD network simulator.

    Usage:
        net = QKDNetwork()
        alice = net.add_node("Alice")
        bob = net.add_node("Bob")
        net.add_link("Alice", "Bob", distance_km=50)
        net.simulate_all_links(num_bits=256)
        e2e_key = net.get_end_to_end_key("Alice", "Bob")
    """

    def __init__(self):
        self.nodes: Dict[str, QKDNode] = {}
        self.links: List[Tuple[str, str, dict]] = []  # (node1, node2, params)
        self.simulation_log = []

    def add_node(self, node_id: str, name: str = "") -> QKDNode:
        if node_id in self.nodes:
            raise ValueError(f"Node {node_id} already exists.")
        node = QKDNode(node_id, name)
        self.nodes[node_id] = node
        return node

    def add_link(self, node1_id: str, node2_id: str,
                 distance_km: float = 10.0,
                 noise_model: str = 'none',
                 decoy_state: bool = False):
        """Add a quantum link between two nodes."""
        for nid in (node1_id, node2_id):
            if nid not in self.nodes:
                raise ValueError(f"Node {nid} does not exist.")
        if node1_id == node2_id:
            raise ValueError("Cannot link a node to itself.")

        params = {
            'distance_km': distance_km,
            'noise_model': noise_model,
            'decoy_state': decoy_state,
        }
        self.links.append((node1_id, node2_id, params))
        self.nodes[node1_id].neighbors[node2_id] = self.nodes[node2_id]
        self.nodes[node2_id].neighbors[node1_id] = self.nodes[node1_id]

    def simulate_link(self, node1_id: str, node2_id: str,
                      params: dict, num_bits: int = 256) -> bytes:
        """Simulate QKD on a single link. Returns the shared key."""
        # Adjust noise based on distance (simple fiber loss model)
        dist = params.get('distance_km', 10)
        # For every 10 km, approximate QBER increase of ~0.5% (realistic fiber)
        base_qber = dist / 2000  # 0.5% per 10 km -> 0.005 per 10 km, so per km = 0.0005
        # We'll use the depolarizing noise model with configurable error prob
        from quantum_layer.noise_models import DepolarizingChannel, NOISE_MODELS
        noise_model_name = params.get('noise_model', 'none')
        if noise_model_name == 'none':
            noise = DepolarizingChannel(error_prob=min(0.1, base_qber))
        else:
            noise = NOISE_MODELS.get(noise_model_name, DepolarizingChannel(0.01))

        sim = BB84Simulator(
            num_bits=num_bits,
            eavesdropper=False,  # Eve not present on a trusted link
            noise_model=noise,
        )
        key, qber = sim.generate_key()
        if key is None:
            # If QBER too high, retry with more bits
            sim2 = BB84Simulator(
                num_bits=num_bits * 2,
                eavesdropper=False,
                noise_model=noise,
            )
            key, qber = sim2.generate_key()
            if key is None:
                raise RuntimeError(f"Link {node1_id}-{node2_id} failed: QBER {qber*100:.1f}%")

        self.simulation_log.append({
            'link': f"{node1_id}--{node2_id}",
            'qber': round(qber * 100, 1),
            'key_length': len(key),
            'distance_km': dist,
        })
        return key

    def simulate_all_links(self, num_bits: int = 256):
        """Generate QKD keys on all links in the network."""
        for node1_id, node2_id, params in self.links:
            key = self.simulate_link(node1_id, node2_id, params, num_bits)
            self.nodes[node1_id].link_keys[node2_id] = key
            self.nodes[node2_id].link_keys[node1_id] = key

    def get_end_to_end_key(self, start_id: str, end_id: str) -> bytes:
        """
        Compute an end‑to‑end key between start and end via the shortest
        path of trusted relays. Uses XOR forwarding.
        """
        path = self._shortest_path(start_id, end_id)
        if not path:
            raise ValueError(f"No path between {start_id} and {end_id}")

        # Collect link keys along the path
        link_keys = []
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            key = self.nodes[u].link_keys.get(v)
            if key is None:
                raise RuntimeError(f"Link key missing for {u}--{v}")
            link_keys.append(key)

        # Combine using XOR
        return forward_key_xor(link_keys)

    def _shortest_path(self, start: str, end: str) -> Optional[List[str]]:
        """BFS shortest path."""
        visited = set()
        queue = [[start]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == end:
                return path
            if node not in visited:
                visited.add(node)
                for neighbor in self.nodes[node].neighbors:
                    if neighbor not in visited:
                        queue.append(path + [neighbor])
        return None

    def get_network_summary(self) -> dict:
        """Return a summary of the network state."""
        return {
            'num_nodes': len(self.nodes),
            'num_links': len(self.links),
            'simulation_log': self.simulation_log,
        }