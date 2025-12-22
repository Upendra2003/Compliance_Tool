"""PDF Report Generator for DPDP Compliance Reports"""
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def generate_compliance_pdf(results, provider):
    """
    Generate a PDF report for DPDP compliance check results.

    Args:
        results: List of compliance check results
        provider: Provider name/ID

    Returns:
        BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#6c757d'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#495057'),
        spaceAfter=12,
        alignment=TA_JUSTIFY,
    )

    # Title
    title = Paragraph("DPDP Act Compliance Report", title_style)
    elements.append(title)

    # Provider name
    provider_name = provider.upper() if isinstance(provider, str) else f"Provider {provider}"
    subtitle = Paragraph(f"Privacy Policy Analysis: {provider_name}", subtitle_style)
    elements.append(subtitle)

    # Timestamp
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    time_para = Paragraph(f"<i>Generated on: {timestamp}</i>", subtitle_style)
    elements.append(time_para)

    elements.append(Spacer(1, 0.3 * inch))

    # Executive Summary
    summary_heading = Paragraph("Executive Summary", heading_style)
    elements.append(summary_heading)

    total_checks = len(results)
    passed_checks = sum(1 for r in results if r.get('passed', False))
    failed_checks = total_checks - passed_checks
    pass_rate = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    summary_text = f"""
    This report presents the results of an automated compliance check of {provider_name}'s
    privacy policy against the requirements of India's Digital Personal Data Protection Act, 2023 (DPDP Act).
    <br/><br/>
    <b>Total Checks Performed:</b> {total_checks}<br/>
    <b>Passed:</b> {passed_checks}<br/>
    <b>Failed:</b> {failed_checks}<br/>
    <b>Compliance Rate:</b> {pass_rate:.1f}%
    """

    summary_para = Paragraph(summary_text, body_style)
    elements.append(summary_para)
    elements.append(Spacer(1, 0.3 * inch))

    # Group results by category
    grouped_results = {}
    for result in results:
        category = result.get('group', 'Unknown')
        if category not in grouped_results:
            grouped_results[category] = []
        grouped_results[category].append(result)

    # Detailed Results
    details_heading = Paragraph("Detailed Compliance Results", heading_style)
    elements.append(details_heading)
    elements.append(Spacer(1, 0.2 * inch))

    for category, checks in grouped_results.items():
        # Category heading
        cat_heading = Paragraph(
            f"<b>{category.upper()}</b>",
            ParagraphStyle(
                'CategoryHeading',
                parent=body_style,
                fontSize=14,
                textColor=colors.HexColor('#495057'),
                fontName='Helvetica-Bold',
                spaceAfter=10,
                spaceBefore=15,
            )
        )
        elements.append(cat_heading)

        # Create table for this category
        table_data = [['Check', 'Status', 'Details']]

        for check in checks:
            check_name = check.get('id', 'Unknown').replace('_', ' ').title()
            status = 'PASSED' if check.get('passed', False) else 'FAILED'
            status_color = colors.HexColor('#28a745') if check.get('passed', False) else colors.HexColor('#dc3545')

            message = check.get('message', 'No details available')

            # Wrap long text
            check_para = Paragraph(check_name, body_style)
            status_para = Paragraph(f"<b>{status}</b>", body_style)
            message_para = Paragraph(message, body_style)

            table_data.append([check_para, status_para, message_para])

        # Create table
        table = Table(table_data, colWidths=[2*inch, 1*inch, 3.5*inch])

        # Style the table
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a1a1a')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e1e8ed')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ])

        # Add status-specific coloring
        for i, check in enumerate(checks, start=1):
            if check.get('passed', False):
                table_style.add('TEXTCOLOR', (1, i), (1, i), colors.HexColor('#28a745'))
            else:
                table_style.add('TEXTCOLOR', (1, i), (1, i), colors.HexColor('#dc3545'))

        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

    # Footer disclaimer
    elements.append(Spacer(1, 0.5 * inch))
    disclaimer = Paragraph(
        "<i><b>Disclaimer:</b> This report is generated through automated analysis and should be used "
        "as a preliminary assessment tool. It does not constitute legal advice. For comprehensive "
        "compliance evaluation, please consult with legal professionals specializing in data protection law.</i>",
        ParagraphStyle(
            'Disclaimer',
            parent=body_style,
            fontSize=9,
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_JUSTIFY,
        )
    )
    elements.append(disclaimer)

    # Build PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and return it
    pdf = buffer.getvalue()
    buffer.close()

    return pdf
