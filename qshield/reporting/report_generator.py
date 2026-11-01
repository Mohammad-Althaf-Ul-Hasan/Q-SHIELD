"""
report_generator.py
PDF report generation for QKD simulation runs.
Uses ReportLab to create a downloadable audit report.
"""

import os
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.platypus.flowables import HRFlowable


def generate_pdf_report(run_data: dict, output_path: str) -> str:
    """
    Generate a PDF report for a QKD protocol run.

    Args:
        run_data: Dictionary with protocol results.
        output_path: File path for the generated PDF.

    Returns:
        The output_path.
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            title="Q-SHIELD Protocol Run Report")
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        textColor=colors.HexColor('#7c3aed'), spaceAfter=20
    )
    story.append(Paragraph("Q-SHIELD — Protocol Audit Report", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#8b5cf6')))
    story.append(Spacer(1, 12))

    # Meta
    meta_style = styles['Normal']
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", meta_style))
    story.append(Paragraph(f"<b>Protocol Version:</b> BB84 + Kyber-512 + AES-256-GCM", meta_style))
    story.append(Spacer(1, 18))

    # Key metrics table
    table_data = [
        ['Parameter', 'Value'],
        ['QBER (%)', f"{run_data.get('qber_percent', 'N/A')}%"],
        ['Eavesdropper Detected', 'Yes' if run_data.get('compromised') else 'No'],
        ['Sifted Bits', str(run_data.get('sifted_bits', 'N/A'))],
        ['Errors Corrected', str(run_data.get('errors_corrected', 'N/A'))],
        ['Final Key Length (bytes)', str(run_data.get('final_key_length', 'N/A'))],
        ['Key ID', str(run_data.get('key_id', 'N/A'))],
    ]
    table = Table(table_data, colWidths=[200, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
    ]))
    story.append(table)
    story.append(Spacer(1, 24))

    # Security analysis text
    sec_style = ParagraphStyle(
        'SecurityAnalysis', parent=styles['Normal'],
        fontSize=11, leading=16
    )
    if run_data.get('compromised'):
        verdict = "❌ The key was discarded because the Quantum Bit Error Rate exceeded the security threshold. Eavesdropping is suspected."
    else:
        verdict = "✅ The key was successfully generated and is considered secure against both classical and quantum adversaries."
    story.append(Paragraph(f"<b>Security Verdict:</b> {verdict}", sec_style))

    doc.build(story)
    return output_path