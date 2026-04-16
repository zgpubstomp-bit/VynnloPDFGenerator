from flask import Flask, request, send_file, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
import re
 
app = Flask(__name__)
 
PARCHMENT = colors.HexColor('#f5ede0')
INK = colors.HexColor('#1a1008')
BLOOD = colors.HexColor('#8b1a1a')
GOLD = colors.HexColor('#c9a84c')
PROMPT_BG = colors.HexColor('#ede4d4')
 
def clean(text):
    # Remove markdown artifacts
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'\*', '', text)
    text = re.sub(r'#+\s*', '', text)
    text = text.strip()
    return text
 
def make_styles():
    styles = {}
    styles['cover_eyebrow'] = ParagraphStyle('cover_eyebrow', fontName='Helvetica', fontSize=7, textColor=BLOOD, alignment=TA_CENTER, spaceAfter=8, leading=10)
    styles['cover_title'] = ParagraphStyle('cover_title', fontName='Helvetica-Bold', fontSize=34, textColor=INK, alignment=TA_CENTER, spaceAfter=4, leading=40)
    styles['cover_subtitle'] = ParagraphStyle('cover_subtitle', fontName='Helvetica', fontSize=8, textColor=GOLD, alignment=TA_CENTER, spaceAfter=14, leading=12)
    styles['cover_tagline'] = ParagraphStyle('cover_tagline', fontName='Helvetica-Oblique', fontSize=12, textColor=INK, alignment=TA_CENTER, spaceAfter=6, leading=18)
    styles['ornament'] = ParagraphStyle('ornament', fontName='Helvetica', fontSize=11, textColor=GOLD, alignment=TA_CENTER, spaceAfter=4, spaceBefore=4, leading=14)
    styles['section_heading'] = ParagraphStyle('section_heading', fontName='Helvetica-Bold', fontSize=7, textColor=BLOOD, alignment=TA_LEFT, spaceAfter=6, spaceBefore=8, leading=10)
    styles['welcome'] = ParagraphStyle('welcome', fontName='Helvetica', fontSize=10, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6, leading=16, leftIndent=12, rightIndent=12)
    styles['how_to_item'] = ParagraphStyle('how_to_item', fontName='Helvetica', fontSize=10, textColor=INK, alignment=TA_LEFT, spaceAfter=3, leading=15, leftIndent=20)
    styles['category_number'] = ParagraphStyle('category_number', fontName='Helvetica', fontSize=7, textColor=GOLD, alignment=TA_CENTER, spaceAfter=3, leading=10)
    styles['category_title'] = ParagraphStyle('category_title', fontName='Helvetica-Bold', fontSize=16, textColor=BLOOD, alignment=TA_CENTER, spaceAfter=3, leading=20)
    styles['category_desc'] = ParagraphStyle('category_desc', fontName='Helvetica-Oblique', fontSize=10, textColor=GOLD, alignment=TA_CENTER, spaceAfter=8, leading=14)
    styles['prompt_num'] = ParagraphStyle('prompt_num', fontName='Helvetica-Bold', fontSize=7, textColor=GOLD, alignment=TA_LEFT, spaceAfter=3, leading=10)
    styles['prompt_text'] = ParagraphStyle('prompt_text', fontName='Helvetica-Oblique', fontSize=9, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=5, leading=14, leftIndent=8, rightIndent=8)
    styles['prompt_expect'] = ParagraphStyle('prompt_expect', fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor('#5a3d1a'), alignment=TA_LEFT, spaceAfter=0, leading=12)
    styles['tips_title'] = ParagraphStyle('tips_title', fontName='Helvetica-Bold', fontSize=11, textColor=BLOOD, alignment=TA_CENTER, spaceAfter=8, leading=15)
    styles['tips_item'] = ParagraphStyle('tips_item', fontName='Helvetica', fontSize=9, textColor=INK, alignment=TA_LEFT, spaceAfter=4, leading=13, leftIndent=16)
    styles['footer_main'] = ParagraphStyle('footer_main', fontName='Helvetica-Bold', fontSize=11, textColor=BLOOD, alignment=TA_CENTER, spaceAfter=5, leading=14)
    styles['footer_sub'] = ParagraphStyle('footer_sub', fontName='Helvetica-Oblique', fontSize=10, textColor=INK, alignment=TA_CENTER, spaceAfter=6, leading=14)
    styles['disclaimer'] = ParagraphStyle('disclaimer', fontName='Helvetica-Oblique', fontSize=8, textColor=GOLD, alignment=TA_CENTER, spaceAfter=0, leading=12)
    return styles
 
def hr(color=GOLD):
    return HRFlowable(width='100%', thickness=1, color=color, spaceAfter=6, spaceBefore=6)
 
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
    # Clean markdown
    text = clean(text)
    expect = clean(expect)
    
    # Style the --ar and -- parameters
    text = re.sub(r'(--\w+[\s\d:.]*)', lambda m: f'<font color="#8b1a1a"><b>{m.group(1).strip()}</b></font> ', text)
    
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
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return KeepTogether([t, Spacer(1, 5)])
 
def category_header(s, num_text, title, desc):
    return KeepTogether([
        Spacer(1, 8),
        Paragraph(num_text.upper(), s['category_number']),
        Paragraph(clean(title), s['category_title']),
        Paragraph(f'<i>{clean(desc)}</i>', s['category_desc']),
        hr(),
    ])
 
def build_pdf(data):
    s = make_styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        leftMargin=0.65*inch, rightMargin=0.65*inch,
        topMargin=0.6*inch, bottomMargin=0.6*inch,
    )
    story = []
 
    # Cover
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph('MIDJOURNEY V7  -  PREMIUM PROMPT COLLECTION', s['cover_eyebrow']))
    story.append(Paragraph(clean(data['title']).upper(), s['cover_title']))
    story.append(Paragraph(data.get('subtitle', 'AI ART PROMPT BUNDLE').upper(), s['cover_subtitle']))
    story.append(Paragraph(f"<i>{clean(data.get('tagline', ''))}</i>", s['cover_tagline']))
    story.append(Spacer(1, 0.15*inch))
 
    total_prompts = sum(len(cat['prompts']) for cat in data['categories'])
    stats = Table(
        [[str(total_prompts), str(len(data['categories'])), 'V7'],
         ['PREMIUM PROMPTS', 'CATEGORIES', 'OPTIMIZED']],
        colWidths=[2*inch, 2*inch, 2*inch])
    stats.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 22),
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
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph('* * *', s['ornament']))
    story.append(hr())
 
    # Welcome
    story.append(Paragraph('WELCOME', s['section_heading']))
    welcome_table = Table([[
        [Paragraph(clean(data.get('welcome', '')), s['welcome'])]
    ]], colWidths=[6.2*inch])
    welcome_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PROMPT_BG),
        ('BOX', (0,0), (-1,-1), 0.5, GOLD),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(welcome_table)
    story.append(Spacer(1, 8))
 
    # How to use
    story.append(Paragraph('HOW TO USE', s['section_heading']))
    for item in data.get('how_to', []):
        story.append(Paragraph(clean(item), s['how_to_item']))
    story.append(Paragraph('* * *', s['ornament']))
 
    # Categories and prompts
    for i, cat in enumerate(data['categories']):
        story.append(category_header(s, cat['name'], cat['title'], cat['description']))
        for p in cat['prompts']:
            story.append(prompt_block(s, p['number'], p['text'], p['expect']))
        if i < len(data['categories']) - 1:
            story.append(Paragraph('* * *', s['ornament']))
 
    # Tips
    story.append(Spacer(1, 8))
    story.append(hr())
    tips_content = [Paragraph('ADVANCED TIPS', s['tips_title'])]
    for tip in data.get('tips', []):
        tips_content.append(Paragraph(clean(tip), s['tips_item']))
    tips_table = Table([[tips_content]], colWidths=[6.2*inch])
    tips_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PROMPT_BG),
        ('BOX', (0,0), (-1,-1), 1, GOLD),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(KeepTogether(tips_table))
 
    # Footer
    story.append(Spacer(1, 10))
    story.append(hr())
    story.append(Paragraph('* * *', s['ornament']))
    story.append(Paragraph(f"Thank you for choosing {clean(data['title'])}", s['footer_main']))
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
        filename = re.sub(r'[^a-z0-9]', '_', data.get('title', 'prompt_bundle').lower()) + '.pdf'
        return send_file(pdf_buffer, mimetype='application/pdf',
                        as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
