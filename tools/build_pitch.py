"""Create the requested 12-slide PDF and a visual QA contact sheet."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import fitz
import json
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
('A consistent choice with a checked outcome','Decision quality',[
    'Each recommendation satisfies the declared order requirements.',
    'Identical offers produce the same calculated winner.',
    'Every approved action receives a durable record and independent readback.']),
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
    'Eligibility checks keep the recommendation aligned with the order.']),
('Every task has a bounded lifetime','Execution and containment',[
    'Disposable Docker execution with no network or application secrets.',
    '128 MiB RAM, 0.50 CPU, 64 processes, CPU and wall-clock limits.',
    'The infinite-loop demo confirms termination, cleanup and recovery.']),
('Running on Vultr','Verified deployment - 5 November 2026',[
    'Vultr VM: Python backend, SQLite ledger and Docker task runner.',
    'Vultr Serverless Inference: qwen3.8-flash-next explains the checked choice.',
    'Caddy serves public HTTPS. The browser workflow used real inference.']),
('Approval leads to a checked record','Verifiable execution',[
    'The host checks the sandbox optimum and mandatory constraints.',
    'Approval commits supplier, cost and ETA to the order ledger.',
    'A fresh connection reads back the result. Evidence records the outcome.']),
('Evidence comes from executed checks','Reliability evidence',[
    '299 generated fresh-state workflow cases use an independent oracle.',
    'Separate HTTP, regression and real Docker tests check boundaries.',
    'Cloud checks separately verified HTTPS, inference and Docker recovery.']),
('The buyer can explain and verify the choice','Business value',[
    'The cloud sample selects SYNTH-A at 1,200 within a 1,500 budget.',
    'The cheaper offer arrives late. The faster feasible alternative costs 150 more.',
    'The buyer can compare the alternatives and confirm the verified saved result.']),
('Public demo and recorded evidence','Verified deployment',[
    'Public source: github.com/CAPEXNULL/Vultr-Dispatcher',
    'Demo: supply-dispatcher.80.240.28.98.sslip.io',
    'Approved orders survived service restart and VM reboot. Cloud workflow and containment recorded.'])
]

# Per-photo exposure, chosen after inspecting all twelve originals.
BACKGROUNDS=[
 ('marcofedermann-port-6131793_1920.png',.18),
 ('rgaudet17-truck-3401529_1920.png',.36),
 ('pexels-kampus-8204322.png',.36),
 ('erikviktor2005-controleur-aerien-virtual-2243223_1920.png',.25),
 ('pexels-ron-lach-8681896.png',.44),
 ('ralphs_fotos-truck-3910170_1920.png',.37),
 ('schwoaze-highway-3392100_1920.png',.30),
 ('niklas9416-hamburg-6849995_1920.png',.06),
 ('pexels-ron-lach-8681899.png',.30),
 ('papazachariasa-cargo-ship-5724401_1920.png',.25),
 ('postcardtrip-port-4602964_1920.png',.48),
 ('dendoktoor-container-ship-6631117_1920.png',.29),
]

def background(c,out,qa,index):
    name,opacity=BACKGROUNDS[index]
    compressed=qa/(Path(name).stem+'.jpg')
    if (out/name).exists():
        source=Image.open(out/name).convert('RGB')
        source.save(compressed,quality=91,optimize=True,subsampling=0)
    else:
        source=Image.open(compressed)
    scale=max(960/source.width,540/source.height)
    w,h=source.width*scale,source.height*scale
    c.saveState()
    clip=c.beginPath();clip.rect(0,0,960,540);c.clipPath(clip,stroke=0,fill=0)
    c.drawImage(ImageReader(str(compressed)),(960-w)/2,(540-h)/2,w,h)
    # PDF transparency layers leave the supplied originals untouched.
    c.setFillColor(HexColor('#04101a'));c.setFillAlpha(opacity);c.rect(0,0,960,540,fill=1,stroke=0)
    for x in range(0,960,2):
        t=max(0,(x/960-.28)/.72)
        alpha=.84*(1-t)**.85+.02
        c.setFillAlpha(alpha);c.rect(x,0,2,540,fill=1,stroke=0)
    c.restoreState()

def build():
    out=ROOT/'output/pdf'; out.mkdir(parents=True,exist_ok=True)
    qa=ROOT/'tmp/pitch';qa.mkdir(parents=True,exist_ok=True)
    pdf=out/'Supply-Dispatcher-Pitch.pdf'
    # The published PDF carries its own photo assets. A clone can rebuild it
    # without separately publishing the owner's supplied original image files.
    missing=[i for i,(name,_) in enumerate(BACKGROUNDS) if not (out/name).exists()]
    if missing:
        previous=fitz.open(pdf)
        for i in missing:
            name=BACKGROUNDS[i][0];images=previous[i].get_images()
            if not images:raise RuntimeError('Missing supplied background: '+name)
            asset=previous.extract_image(images[0][0])
            (qa/(Path(name).stem+'.jpg')).write_bytes(asset['image'])
        previous.close()
    c=canvas.Canvas(str(pdf),pagesize=(960,540)); c.setTitle('Supply Dispatcher'); c.setAuthor('Supply Dispatcher contributors')
    title=ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=35,leading=41,textColor=HexColor('#ffffff'))
    body=ParagraphStyle('body',fontName='Helvetica',fontSize=21,leading=29,textColor=HexColor('#f1f4f6'))
    for index,(heading,sub,lines) in enumerate(SLIDES):
        background(c,out,qa,index)
        c.setFont('Helvetica-Bold',11);c.setFillColor(HexColor('#ffbc68'));c.drawString(64,490,'CAPEXNULL / SUPPLY DISPATCHER')
        if index==0:
            c.setFillColor(HexColor('#ffffff'));c.setFont('Helvetica-Bold',65);c.drawString(60,380,'Supply')
            c.setFillColor(HexColor('#ffbc68'));c.drawString(60,309,'Dispatcher')
            c.setFont('Helvetica',23);c.setFillColor(HexColor('#ffffff'));c.drawString(64,260,sub)
            y=184
            for line in lines:
                c.setFont('Helvetica',20);c.drawString(64,y,line);y-=39
        else:
            c.setFont('Helvetica',12);c.setFillColor(HexColor('#ffbc68'));c.drawString(64,448,sub.upper())
            p=Paragraph(heading,title);w,h=p.wrap(775,110);assert h<=100
            p.drawOn(c,62,414-h)
            y=302 if h<60 else 274
            for line in lines:
                p=Paragraph(line,body);w,h=p.wrap(715,100);assert h<=87
                c.setFillColor(HexColor('#ffbc68'));c.setFont('Helvetica-Bold',20);c.drawString(64,y-6,'-')
                p.drawOn(c,91,y+13-h);y-=h+25
            assert y>55,(index,y)
        c.setFont('Helvetica',10);c.setFillColor(HexColor('#e0e7ec'))
        c.drawString(64,28,'VULTR AGENT RUSH 2026')
        c.drawRightString(898,28,f'{index+1:02d} / 12')
        c.showPage()
    c.save()
    md=['# Supply Dispatcher pitch deck','', '12-slide source. Cloud deployment verified on 2026-11-05; all demo data is synthetic.','']
    for i,(heading,sub,lines) in enumerate(SLIDES,1):
        md.extend([f'## {i}. {heading}','',sub,'']+['- '+line for line in lines]+[''])
    (ROOT/'PITCH_DECK.md').write_text('\n'.join(md),encoding='utf-8')
    doc=fitz.open(pdf); assert len(doc)==12
    (qa/'background-design.json').write_text(json.dumps([{'slide':i+1,'image':n,'base_darkening':v,'text_gradient':'0.86 left to 0.02 right'} for i,(n,v) in enumerate(BACKGROUNDS)],indent=2)+'\n')
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
