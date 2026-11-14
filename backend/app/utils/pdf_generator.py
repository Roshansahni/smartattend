"""PDF report generator for attendance using ReportLab."""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_attendance_pdf(report_data: dict) -> bytes:
    """Generate attendance report PDF as bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=10
    )
    
    elements.append(Paragraph("SmartAttend — Attendance Report", title_style))
    elements.append(Paragraph(f"<b>Session / Course:</b> {report_data.get('title', 'N/A')}", styles['Normal']))
    elements.append(Paragraph(f"<b>Generated At:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    table_data = [["#", "Enrollment No.", "Student Name", "Status", "Marked At", "Method"]]
    for idx, rec in enumerate(report_data.get("records", []), start=1):
        table_data.append([
            str(idx),
            rec.get("enrollment_number", "N/A"),
            rec.get("student_name", "N/A"),
            "Present" if rec.get("is_present") else "Absent",
            str(rec.get("marked_at", "N/A"))[:19],
            rec.get("verification_method", "qr").upper()
        ])
        
    t = Table(table_data, colWidths=[30, 100, 150, 60, 130, 60])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    elements.append(t)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.read()
