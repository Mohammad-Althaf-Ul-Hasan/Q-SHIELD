"""
quantum_circuit.py
SVG quantum circuit diagram generator (no Qiskit dependency).

Generates a minimal quantum circuit diagram showing:
    - qubit wire
    - a Hadamard gate (H) when X‑basis is used
    - measurement symbol (M)
"""


def generate_circuit_svg(basis: str, output_filename: str = 'circuit.svg'):
    """
    Generate a simple SVG of a single‑qubit BB84 circuit.

    Args:
        basis: 'Z' or 'X'
        output_filename: path to save the SVG file.

    Returns:
        SVG string.
    """
    width = 200
    height = 60
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">\n'
    # Wire
    svg += f'  <line x1="30" y1="30" x2="{width-30}" y2="30" stroke="#94a3b8" stroke-width="2"/>\n'

    if basis == 'X':
        # Hadamard gate (box with H)
        svg += '  <rect x="60" y="15" width="30" height="30" fill="none" stroke="#06b6d4" stroke-width="2" rx="4"/>\n'
        svg += '  <text x="75" y="36" fill="#06b6d4" font-family="monospace" font-size="16" text-anchor="middle">H</text>\n'

    # Measurement gate
    svg += f'  <rect x="{width-80}" y="15" width="40" height="30" fill="none" stroke="#8b5cf6" stroke-width="2" rx="4"/>\n'
    svg += f'  <text x="{width-60}" y="36" fill="#8b5cf6" font-family="monospace" font-size="14" text-anchor="middle">M</text>\n'

    svg += '</svg>'

    with open(output_filename, 'w') as f:
        f.write(svg)
    return svg