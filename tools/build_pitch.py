"""Create the requested 12-slide PDF and a visual QA contact sheet."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import fitz
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
SLIDES=[
('Supply Dispatcher','Verified recovery after a supplier delay',[
    'Deterministic supplier comparison',
    'Buyer approval before the order changes',
    'A saved result with independent verification']),
('A delayed supplier puts the order at risk','Procurement disruption',[
    'A buyer must compare price, quantity, product and delivery at once.',
    'The cheapest offer can fail a mandatory requirement.',
    'An explanation alone does not recover the order.']),
('Fluent text cannot prove feasibility','The weakness of LLM-only selection',[
    'A recommendation must satisfy every declared order constraint.',
    'Identical offers should produce an identical winner.',
    'An approved action needs a durable record and a checked outcome.']),
('Calculation chooses. Inference explains.','Our approach',[
    'A fixed solver compares the current offers in an isolated container.',
    'An independent implementation checks the optimum.',
    'Vultr inference explains the checked choice. The buyer approves it.']),
('One disruption, one reviewable workflow','Product workflow',[
    'Enter the delayed order and supplier alternatives.',
    'Review the plan, recommendation and three analytics views.',
    'Approve the replacement and inspect the verified saved result.']),
('The selection rule is explicit','Deterministic mathematical decision layer',[
    'Product matches. Quantity covers the order. Cost and ETA fit the limits.',
    'Minimize cost, then ETA, then supplier ID for an exact tie.',
    'No feasible offer means no replacement and no order update.']),
('Every task has a bounded lifetime','Execution and containment',[
    'Disposable Docker execution with no network or application secrets.',
    '128 MiB RAM, 0.50 CPU, 64 processes, CPU and wall-clock limits.',
    'The infinite-loop demo confirms termination, cleanup and recovery.']),
('Vultr is the planned control plane','Deployment architecture',[
    'Vultr VM: Python backend, SQLite ledger and Docker task runner.',
    'Vultr Serverless Inference: OpenAI-compatible explanation calls.',
    'Caddy: public HTTPS. Cloud deployment and live inference are pending.']),
('Approval leads to a checked record','Verifiable execution',[
    'The host checks the sandbox optimum and mandatory constraints.',
    'Approval commits supplier, cost and ETA to the order ledger.',
    'A fresh connection reads back the result. Evidence records the outcome.']),
('Evidence comes from executed checks','Reliability evidence',[
    '299 generated fresh-state workflow cases use an independent oracle.',
    'Separate HTTP, regression and real Docker tests check boundaries.',
    'Recorded local evidence does not establish a public cloud deployment.']),
('The buyer can explain and verify the choice','Business value',[
    'The sample selects SUP-A at 115,000 within a 120,000 budget.',
    'SUP-C fails quantity. Faster SUP-B costs more under the fixed objective.',
    'The sample is synthetic. Customer ROI and time savings are unmeasured.']),
('From recommendation to verified recovery','Demo and completion',[
    'Public source: github.com/CAPEXNULL/Vultr-Dispatcher',
    'Next: verify Vultr deployment, live inference and the HTTPS workflow.',
    'Record the containment moment, upload the video and submit on lablab.'])
]

def build():
    out=ROOT/'output/pdf'; out.mkdir(parents=True,exist_ok=True)
    pdf=out/'Supply-Dispatcher-Pitch.pdf'
    c=canvas.Canvas(str(pdf),pagesize=(960,540)); c.setTitle('Supply Dispatcher'); c.setAuthor('Supply Dispatcher contributors')
    title=ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=34,leading=40,textColor=HexColor('#f5f3ff'))
    body=ParagraphStyle('body',fontName='Helvetica',fontSize=21,leading=29,textColor=HexColor('#ddd8ed'))
    for index,(heading,sub,lines) in enumerate(SLIDES):
        c.setFillColor(HexColor('#10101d')); c.rect(0,0,960,540,fill=1,stroke=0)
        c.setFillColor(HexColor('#8b5cf6')); c.rect(52,458,52,5,fill=1,stroke=0)
        c.setFont('Helvetica',12); c.setFillColor(HexColor('#b4a3e4')); c.drawString(52,490,sub.upper())
        p=Paragraph(heading,title); w,h=p.wrap(845,110); assert h<=100
        p.drawOn(c,52,432-h)
        y=302 if h<60 else 270
        for number,line in enumerate(lines,1):
            c.setFillColor(HexColor('#9c7bfa')); c.setFont('Helvetica-Bold',13); c.drawString(54,y-4,f'{number:02d}')
            p=Paragraph(line,body); w,h=p.wrap(785,90); assert h<=87
            p.drawOn(c,102,y+13-h); y-=h+28
        assert y>55,(index,y)
        c.setStrokeColor(HexColor('#343047')); c.line(52,48,908,48)
        c.setFont('Helvetica',10); c.setFillColor(HexColor('#a49bb7'))
        c.drawString(52,28,'Supply Dispatcher / Vultr Agent Rush 2026')
        c.drawRightString(908,28,f'{index+1:02d} / 12')
        c.showPage()
    c.save()
    md=['# Supply Dispatcher pitch deck','', '12-slide source. Local evidence and pending cloud work are stated separately.','']
    for i,(heading,sub,lines) in enumerate(SLIDES,1):
        md.extend([f'## {i}. {heading}','',sub,'']+['- '+line for line in lines]+[''])
    (ROOT/'PITCH_DECK.md').write_text('\n'.join(md),encoding='utf-8')
    doc=fitz.open(pdf); assert len(doc)==12
    qa=ROOT/'tmp/pitch'; qa.mkdir(parents=True,exist_ok=True)
    sheet=Image.new('RGB',(1440,4*292),'#eeeeee')
    for i,page in enumerate(doc):
        pix=page.get_pixmap(matrix=fitz.Matrix(1,1))
        png=qa/f'slide-{i+1:02d}.png'; pix.save(png)
        image=Image.open(png); image.thumbnail((460,259))
        sheet.paste(image,((i%3)*480+10,(i//3)*292+10))
        ImageDraw.Draw(sheet).text(((i%3)*480+12,(i//3)*292+272),f'{i+1:02d}',fill='#111111')
    sheet.save(qa/'contact-sheet.png')
    print('Created 12-page pitch PDF and rendered every page for QA.')

if __name__=='__main__': build()
