from flask import Flask, request, send_file, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
import json

app = Flask(__name__)

PARCHMENT = colors.HexColor('#f5ede0')
INK = colors.HexColor('#1a1008')
BLOOD = colors.HexColor('#8b1a1a')
GOLD = colors.HexColor('#c9a84c')
PROMPT_BG = colors.HexColor('#ede4d4')

def make_styles():
    styles = {}
    styles['cover_eyebrow'] = ParagraphStyle('cover_eyebrow', fontName='Helvetica', fontSize=7, textColor=BLOOD, alignment=TA_CENTER, spaceAfter=8, leading=10)
    styles['cover_title'] = ParagraphStyle('cover_title', fontName='Helvetica-Bold', fontSize=36, textColor=INK, alignment=TA_CENTER, spaceAfter=4, leading=42)
    styles['cover_subtitle'] = ParagraphStyle('cover_subtitle', fontName='Helvetica', fontSize=8, textColor=GOLD, alignment=TA_CENTER, spaceAfter=14, leading=12)
    styles['cover_tagline'] = ParagraphStyle('cover_tagline', fontName='Helvetica-Oblique', fontSize=12, textColor=INK, alignment=TA_CENTER, spaceAfter=6, leading=18)
    styles['ornament'] = ParagraphStyle('ornament', fontName='Helvetica', fontSize=11, textColor=GOLD, alignment=TA_CENTER, spaceAfter=6, spaceBefore=6, leading=14)
    styles['section_heading'] = ParagraphStyle('section_heading', fontName='Helvetica-Bold', fontSize=7, textColor=BLOOD, alignment=TA_LEFT, spaceAfter=8, spaceBefore=10, leading=10)
    styles['welcome'] = ParagraphStyle('welcome', fontName='Helvetica', fontSize=10, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6, leading=16, leftIndent=12, rightIndent=12)
    styles['how_to_item'] = ParagraphStyle('how_to_item', fontName='Helvetica', fontSize=10, textColor=INK, alignment=TA_LEFT, spaceAfter=4, leading=15, leftIndent=20)
    styles['category_number'] = ParagraphStyle('category_number', fontName='Helvetica', fontSize=7, textColor=GOLD, alignment=TA_CENTER, spaceAfter=4, leading=10)
    styles['category_title'] = ParagraphStyle('category_title', fontName='Helvetica-Bold', fontSize=18, textColor=BLOOD, alignment=TA_CENTER, spaceAfter=4, leading=22)
    styles['category_desc'] = ParagraphStyle('category_desc', fontName='Helvetica-Oblique', fontSize=10, textColor=GOLD, alignment=TA_CENTER, spaceAfter=10, leading=14)
    styles['prompt_num'] = ParagraphStyle('prompt_num', fontName='Helvetica-Bold', fontSize=7, textColor=GOLD, alignment=TA_LEFT, spaceAfter=4, leading=10)
    styles['prompt_text'] = ParagraphStyle('prompt_text', fontName='Helvetica-Oblique', fontSize=9.5, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6, leading=15, leftIndent=8, rightIndent=8)
    styles['prompt_expect'] = ParagraphStyle('prompt_expect', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#5a3d1a'), alignment=TA_LEFT, spaceAfter=0, leading=13)
    styles['tips_title'] = ParagraphStyle('tips_title', fontName='Helvetica-Bold', fontSize=12, textColor=BLOOD, alignment=TA_CENTER, spaceAfter=10, leading=16)
    styles['tips_item'] = ParagraphStyle('tips_item', fontName='Helvetica', fontSize=9.5, textColor=INK, alignment=TA_LEFT, spaceAfter=5, leading=14, leftIndent=16)
    styles['footer_main'] = ParagraphStyle('footer_main', fontName='Helvetica-Bold', fontSize=11, textColor=BLOOD, alignment=TA_CENTER, spaceAfter=6, leading=15)
    styles['footer_sub'] = ParagraphStyle('footer_sub', fontName='Helvetica-Oblique', fontSize=10, textColor=INK, alignment=TA_CENTER, spaceAfter=8, leading=14)
    styles['disclaimer'] = ParagraphStyle('disclaimer', fontName='Helvetica-Oblique', fontSize=8, textColor=GOLD, alignment=TA_CENTER, spaceAfter=0, leading=12)
    return styles

def hr(color=GOLD):
    return HRFlowable(width='100%', thickness=1, color=color, spaceAfter=8, spaceBefore=8)

def on_page(canvas, doc):
    canvas.saveState()
    w, h = letter
    canvas.setFillColor(PARCHMENT)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1.5)
    canvas.rect(0.3*inch, 0.3*inch, w - 0.6*inch, h - 0.6*inch, fill=0, stroke=1)
    canvas.setLineWidth(0.5)
    canvas.setStrokeColor(colors.HexColor('#e8c97a'))
    canvas.rect(0.35*inch, 0.35*inch, w - 0.7*inch, h - 0.7*inch, fill=0, stroke=1)
    canvas.restoreState()

def prompt_block(s, num, text, expect):
    text = text.replace('--ar 16:9', '<font color="#8b1a1a"><b>--ar 16:9</b></font>')
    text = text.replace('--ar 3:2', '<font color="#8b1a1a"><b>--ar 3:2</b></font>')
    text = text.replace('--ar 5:4', '<font color="#8b1a1a"><b>--ar 5:4</b></font>')
    text = text.replace('--ar 21:9', '<font color="#8b1a1a"><b>--ar 21:9</b></font>')
    items = [
        Paragraph(f'PROMPT {num:02d}', s['prompt_num']),
        Paragraph(text, s['prompt_text']),
        Paragraph(f'<font color="#8b1a1a"><b>EXPECT:</b></font>  {expect}', s['prompt_expect']),
    ]
    t = Table([[items]], colWidths=[6.2*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PROMPT_BG),
        ('BOX', (0,0), (-1,-1), 0.5, GOLD),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return KeepTogether([t, Spacer(1, 6)])

def build_pdf(data):
    s = make_styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
        leftMargin=0.7*inch, rightMargin=0.7*inch,
        topMargin=0.65*inch, bottomMargin=0.65*inch)
    story = []

    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph('MIDJOURNEY V7  -  PREMIUM PROMPT COLLECTION', s['cover_eyebrow']))
    story.append(Paragraph(data['title'].upper(), s['cover_title']))
    story.append(Paragraph(data.get('subtitle', 'AI ART PROMPT BUNDLE').upper(), s['cover_subtitle']))
    story.append(Paragraph(f"<i>{data.get('tagline', 'Unlock stunning AI art with these premium prompts.')}</i>", s['cover_tagline']))
    story.append(Spacer(1, 0.2*inch))

    stats = Table(
        [[str(data.get('prompt_count', 50)), str(len(data['categories'])), 'V7'],
         ['PREMIUM PROMPTS', 'CATEGORIES', 'OPTIMIZED']],
        colWidths=[2*inch, 2*inch, 2*inch])
    stats.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 24),
        ('TEXTCOLOR', (0,0), (-1,0), BLOOD),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,1), 7),
        ('TEXTCOLOR', (0,1), (-1,1), GOLD),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(stats)
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph('* * *', s['ornament']))
    story.append(hr())

    story.append(Paragraph('WELCOME', s['section_heading']))
    welcome_table = Table([[
        [Paragraph(data.get('welcome', 'Welcome to this premium prompt bundle.'), s['welcome'])]
    ]], colWidths=[6.2*inch])
    welcome_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PROMPT_BG),
        ('BOX', (0,0), (-1,-1), 0.5, GOLD),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(welcome_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph('HOW TO USE', s['section_heading']))
    for item in data.get('how_to', []):
        story.append(Paragraph(item, s['how_to_item']))
    story.append(Paragraph('* * *', s['ornament']))

    for i, cat in enumerate(data['categories']):
        story.append(Spacer(1, 10))
        story.append(Paragraph(cat['name'].upper(), s['category_number']))
        story.append(Paragraph(cat['title'], s['category_title']))
        story.append(Paragraph(f"<i>{cat['description']}</i>", s['category_desc']))
        story.append(hr())
        for p in cat['prompts']:
            story.append(prompt_block(s, p['number'], p['text'], p['expect']))
        if i < len(data['categories']) - 1:
            story.append(Paragraph('* * *', s['ornament']))

    story.append(Spacer(1, 10))
    story.append(hr())
    tips_content = [Paragraph('ADVANCED TIPS', s['tips_title'])]
    for tip in data.get('tips', []):
        tips_content.append(Paragraph(tip, s['tips_item']))
    tips_table = Table([[tips_content]], colWidths=[6.2*inch])
    tips_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PROMPT_BG),
        ('BOX', (0,0), (-1,-1), 1, GOLD),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(KeepTogether(tips_table))

    story.append(Spacer(1, 14))
    story.append(hr())
    story.append(Paragraph('* * *', s['ornament']))
    story.append(Paragraph(f"Thank you for choosing {data['title']}", s['footer_main']))
    story.append(Paragraph('<i>May your creations exceed your imagination.</i>', s['footer_sub']))
    story.append(Paragraph('This is a digital product. No physical item will be shipped. Access to Midjourney AI is required and not included. Results may vary.', s['disclaimer']))

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    buffer.seek(0)
    return buffer

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        pdf_buffer = build_pdf(data)
        filename = data.get('title', 'prompt_bundle').replace(' ', '_').lower() + '.pdf'
        return send_file(pdf_buffer, mimetype='application/pdf',
                        as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
