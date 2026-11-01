from flask import Blueprint, jsonify, session, send_file
from reporting.report_generator import generate_pdf_report
import os, tempfile

report_bp = Blueprint('report_bp', __name__)

@report_bp.route('/api/report/generate', methods=['POST'])
def generate_report():
    run_data = {
        'qber_percent': session.get('last_qber', 'N/A'),
        'compromised': session.get('last_compromised', False),
        'sifted_bits': session.get('last_sifted', 'N/A'),
        'errors_corrected': session.get('last_errors', 'N/A'),
        'final_key_length': session.get('last_key_len', 'N/A'),
        'key_id': session.get('current_key_id', 'N/A'),
    }
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    path = generate_pdf_report(run_data, tmp.name)
    return send_file(path, as_attachment=True, download_name='qshield_report.pdf')