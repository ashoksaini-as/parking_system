import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

RATE_PER_HOUR = 20.0
MIN_FEE = 20.0

def calculate_fee(entry_time):
    if isinstance(entry_time, str):
        entry_time = datetime.strptime(entry_time, '%Y-%m-%d %H:%M:%S')
    duration = datetime.now() - entry_time
    hours = duration.total_seconds() / 3600
    fee = max(round(hours * RATE_PER_HOUR, 2), MIN_FEE)
    return fee, round(hours, 2)

def generate_receipt_pdf(vehicle, receipts_dir='app/static/receipts'):
    os.makedirs(receipts_dir, exist_ok=True)
    filename = f"receipt_{vehicle['id']}_{vehicle['vehicle_number']}.pdf"
    filepath = os.path.join(receipts_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Title'],
        fontSize=24, textColor=colors.HexColor('#1e293b'),
        spaceAfter=6, alignment=TA_CENTER, fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#64748b'),
        spaceAfter=4, alignment=TA_CENTER)
    label_style = ParagraphStyle('Label', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#64748b'), fontName='Helvetica')
    value_style = ParagraphStyle('Value', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold')
    total_style = ParagraphStyle('Total', parent=styles['Normal'],
        fontSize=16, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold',
        alignment=TA_RIGHT)

    # Header
    story.append(Paragraph("🅿 ParkSmart", title_style))
    story.append(Paragraph("Parking Management System", sub_style))
    story.append(Paragraph("PAYMENT RECEIPT", ParagraphStyle('Receipt',
        parent=styles['Normal'], fontSize=13, textColor=colors.HexColor('#3b82f6'),
        fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=16)))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#3b82f6')))
    story.append(Spacer(1, 0.5*cm))

    # Info Table
    entry = vehicle['entry_time']
    exit_t = vehicle['exit_time'] or datetime.now()
    if isinstance(entry, str):
        entry = datetime.strptime(entry, '%Y-%m-%d %H:%M:%S')
    if isinstance(exit_t, str):
        exit_t = datetime.strptime(exit_t, '%Y-%m-%d %H:%M:%S')
    duration_hrs = round((exit_t - entry).total_seconds() / 3600, 2)

    data = [
        ['Receipt No.', f"RCP-{vehicle['id']:06d}", 'Date', exit_t.strftime('%d %b %Y')],
        ['Vehicle No.', vehicle['vehicle_number'], 'Slot', f"#{vehicle['slot_number']}"],
        ['Owner', vehicle['owner_name'], 'Time In', entry.strftime('%I:%M %p')],
        ['', '', 'Time Out', exit_t.strftime('%I:%M %p')],
        ['', '', 'Duration', f"{duration_hrs} hours"],
    ]
    t = Table(data, colWidths=[3.5*cm, 6*cm, 3*cm, 5*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#64748b')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#f8fafc'), colors.white]),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    story.append(Spacer(1, 0.4*cm))

    # Fee breakdown
    fee_data = [
        ['Rate', f"₹{RATE_PER_HOUR:.0f} / hour"],
        ['Duration', f"{duration_hrs} hours"],
        ['Minimum Charge', f"₹{MIN_FEE:.0f}"],
    ]
    ft = Table(fee_data, colWidths=[8*cm, 8*cm])
    ft.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(ft)
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1e293b')))
    story.append(Spacer(1, 0.3*cm))

    total_data = [['TOTAL AMOUNT', f"₹{float(vehicle['fee']):.2f}"]]
    tt = Table(total_data, colWidths=[8*cm, 8*cm])
    tt.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#3b82f6')),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(tt)

    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Thank you for using ParkSmart!", ParagraphStyle('Footer',
        parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER)))

    doc.build(story)
    return filename
