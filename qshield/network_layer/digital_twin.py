"""
digital_twin.py
Digital twin deployment for QKD networks.

Mirrors a real QKD network topology and provides what‑if analysis:
"What happens if link 3 goes down?" "What is the key rate if
distance doubles?"

Builds on QKDNetwork, adding scenario replay and analysis.
"""

import copy
from typing import List, Dict

from network_layer.qkd_network import QKDNetwork


class DigitalTwin:
    """
    Digital twin of a QKD network.

    Usage:
        dt = DigitalTwin()
        dt.load_topology({'nodes':[...], 'links':[...]})
        dt.simulate()
        dt.run_what_if('link_failure', {'link':('A','B')})
    """

    def __init__(self):
        self.base_network: QKDNetwork = None
        self.current_state: dict = {}
        self.scenarios: List[dict] = []

    def load_topology(self, topology: dict):
        """
        Load a network topology from a dictionary.

        Example:
            {
                'nodes': [
                    {'id': 'A', 'name': 'Alice'},
                    {'id': 'B', 'name': 'Bob'},
                    {'id': 'T1', 'name': 'Trusted Relay 1'}
                ],
                'links': [
                    {'nodes': ('A','T1'), 'distance_km': 30},
                    {'nodes': ('T1','B'), 'distance_km': 45}
                ]
            }
        """
        net = QKDNetwork()
        for node in topology.get('nodes', []):
            net.add_node(node['id'], node.get('name', ''))
        for link in topology.get('links', []):
            n1, n2 = link['nodes']
            net.add_link(n1, n2,
                         distance_km=link.get('distance_km', 10),
                         noise_model=link.get('noise_model', 'none'))
        self.base_network = net

    def simulate(self, num_bits: int = 256):
        """Run simulation on the base network and store the state."""
        if not self.base_network:
            raise RuntimeError("No topology loaded.")
        self.base_network.simulate_all_links(num_bits)
        self.current_state = self.base_network.get_network_summary()

    def run_what_if(self, scenario: str, params: dict):
        """
        Run a what‑if scenario: clone the base network, apply a change,
        simulate, and compare.

        Supported scenarios:
            - 'link_failure': params={'link': ('A','T1')}
            - 'distance_increase': params={'link': ('A','T1'), 'factor': 2.0}
        """
        base_copy = copy.deepcopy(self.base_network)

        if scenario == 'link_failure':
            link = params['link']
            # Remove the link
            base_copy.links = [
                (u, v, p) for (u, v, p) in base_copy.links
                if (u, v) != link and (v, u) != link
            ]
            if link[0] in base_copy.nodes:
                base_copy.nodes[link[0]].neighbors.pop(link[1], None)
                base_copy.nodes[link[0]].link_keys.pop(link[1], None)
            if link[1] in base_copy.nodes:
                base_copy.nodes[link[1]].neighbors.pop(link[0], None)
                base_copy.nodes[link[1]].link_keys.pop(link[0], None)
        elif scenario == 'distance_increase':
            link = params['link']
            factor = params.get('factor', 2.0)
            for i, (u, v, p) in enumerate(base_copy.links):
                if (u, v) == link or (v, u) == link:
                    new_params = p.copy()
                    new_params['distance_km'] *= factor
                    base_copy.links[i] = (u, v, new_params)
                    break
        else:
            raise ValueError(f"Unknown scenario: {scenario}")

        base_copy.simulate_all_links()
        scenario_result = {
            'scenario': scenario,
            'params': params,
            'summary': base_copy.get_network_summary(),
        }
        self.scenarios.append(scenario_result)
        return scenario_result