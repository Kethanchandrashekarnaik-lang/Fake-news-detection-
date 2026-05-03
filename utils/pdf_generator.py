import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.colors import HexColor

def generate_pdf_report(prediction_data, output_path):
    """
    Generates a PDF report for a given prediction.
    prediction_data should be a dict containing:
    - id, timestamp, prediction, confidence, input_text, source_url
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontSize=11, leading=14))
    styles.add(ParagraphStyle(name='CenterTitle', alignment=TA_CENTER, fontSize=18, spaceAfter=20, textColor=HexColor('#2a2a2a')))
    styles.add(ParagraphStyle(name='Meta', fontSize=10, textColor=HexColor('#555555'), spaceAfter=5))
    
    # Custom Result Style
    result_color = HexColor('#00e676') if prediction_data.get('prediction', '').upper() == 'REAL' else HexColor('#ff1744')
    styles.add(ParagraphStyle(name='Result', alignment=TA_CENTER, fontSize=16, spaceAfter=20, textColor=result_color))

    Story = []

    # Title
    Story.append(Paragraph("Fake News Detection Report", styles['CenterTitle']))
    
    # Metadata
    date_str = str(prediction_data.get('timestamp', 'Unknown'))
    Story.append(Paragraph(f"<b>Report ID:</b> #{prediction_data.get('id', 'N/A')}", styles['Meta']))
    Story.append(Paragraph(f"<b>Date:</b> {date_str}", styles['Meta']))
    
    if prediction_data.get('source_url'):
        Story.append(Paragraph(f"<b>Source URL:</b> {prediction_data.get('source_url')}", styles['Meta']))
    
    Story.append(Spacer(1, 12))
    
    # Result
    pred_label = prediction_data.get('prediction', 'UNKNOWN').upper()
    conf = prediction_data.get('confidence', 0)
    Story.append(Paragraph(f"<b>ANALYSIS VERDICT: {pred_label}</b>", styles['Result']))
    Story.append(Paragraph(f"<b>Confidence Level:</b> {conf}%", styles['Normal']))
    
    Story.append(Spacer(1, 12))
    
    # Reason
    if prediction_data.get('explanation'):
        Story.append(Paragraph("<b>AI Reasoning:</b>", styles['Normal']))
        Story.append(Paragraph(prediction_data['explanation'], styles['Justify']))
        Story.append(Spacer(1, 12))

    # Sources
    import json
    sources_raw = prediction_data.get('sources_json', '[]')
    try:
        sources = json.loads(sources_raw)
        if sources:
            Story.append(Paragraph("<b>Verified Sources:</b>", styles['Normal']))
            for s in sources:
                Story.append(Paragraph(f"• <a href='{s['url']}' color='blue'>{s['title']}</a>", styles['Normal']))
            Story.append(Spacer(1, 12))
    except:
        pass
    
    Story.append(Paragraph("<b>Analyzed Text:</b>", styles['Normal']))
    Story.append(Spacer(1, 8))
    
    # Text snippet
    text = prediction_data.get('input_text', '')
    if len(text) > 3000:
        text = text[:3000] + "... [truncated]"
        
    Story.append(Paragraph(text, styles['Justify']))
    
    doc.build(Story)
    return output_path
