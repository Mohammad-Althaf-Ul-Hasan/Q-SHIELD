from flask import Blueprint, jsonify
from benchmark.comparator import run_full_comparison

benchmark_bp = Blueprint('benchmark_bp', __name__)

@benchmark_bp.route('/api/benchmark/run', methods=['POST'])
def run_benchmark():
    results = run_full_comparison()
    return jsonify({'status': 'ok', 'results': results})