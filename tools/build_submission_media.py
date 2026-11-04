"""Legacy local walkthrough builder. Use build_final_media.py for the cloud video.

Text/font helpers are reused by the final builder; do not run this legacy
entrypoint against final deliverables.
"""
from pathlib import Path
import json, subprocess, wave
from PIL import Image, ImageDraw, ImageFont, ImageOps
import fitz, imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/media'; TMP=ROOT/'tmp/media'
OUT.mkdir(parents=True,exist_ok=True); TMP.mkdir(parents=True,exist_ok=True)
FONT='C:/Windows/Fonts/segoeui.ttf'; BOLD='C:/Windows/Fonts/segoeuib.ttf'
def font(n,bold=False): return ImageFont.truetype(BOLD if bold else FONT,n)
def wrap(draw,text,f,width):
    lines=[]; line=''
    for word in text.split():
        trial=(line+' '+word).strip()
        if draw.textlength(trial,font=f)>width and line: lines.append(line); line=word
        else: line=trial
    return lines+[line]
def text(draw,xy,s,n=28,color='#e8f0fa',width=1050,bold=False):
    x,y=xy; f=font(n,bold)
    for line in wrap(draw,s,f,width): draw.text((x,y),line,font=f,fill=color); y+=int(n*1.4)
    return y

SCENES=[
('Supply Dispatcher','Verified recovery after a supplier delay',None,
 'A delayed supplier puts an order at risk. Supply Dispatcher turns that disruption into a repeatable comparison, buyer approval, and a verified saved result.'),
('01 / The disruption','Order constraints turn a delay into a precise task.','current-order.png',
 'The buyer defines quantity, budget, and deadline, confirms the delay, and enters supplier offers. Add supplier extends the comparison. Analyze disruption checks the alternatives instead of asking the buyer to judge a fluent answer. Without a confirmed delay, no replacement action is proposed.'),
('02 / Calculation chooses','A cheaper offer is useful only when it is admissible.','analytics-charts.png',
 'The cheapest offer, Supplier C, lacks enough units. Supplier A meets all requirements at one hundred fifteen thousand and six days. Faster Supplier B costs more. The fixed objective ranks cost, delivery time, then supplier identifier. Table, Metrics, and Charts present the comparison in three distinct views.'),
('03 / Independent checks, buyer control','Explanation cannot override the calculated choice.','verified-result.png',
 'Mathematics selects the supplier; a separate verifier checks the result. Explanation cannot override the choice. The buyer retains control through Approve replacement. If no supplier satisfies the constraints, the application reports a conflict and leaves the order unchanged.'),
('04 / Proof of the actual update','Database commit, fresh readback, visible evidence.','verified-result.png',
 'Approval is followed by a database commit and a fresh readback of supplier, cost, and delivery time. Evidence confirms the checks: success means a saved result, not just generated text. Edit conditions returns to the inputs for a new analysis. This synthetic ledger does not place real purchases.'),
('05 / Bounded execution','Recorded local Docker containment evidence',None,
 'Saved local Docker evidence confirms resource limits, no network, no application key, timeout cleanup, and a successful next task. Isolation supports the workflow; it does not replace checking whether the supplier decision itself is correct.'),
('06 / Verified experience','Reuse a proven case, while checking the present.',None,
 'Only verified successes enter experience storage. Reuse requires compatible conditions and the same freshly calculated winner. It can avoid a redundant model explanation, but never calculation or approval. Repeated approval creates no duplicate update. Changed conditions invalidate an old pending proposal.'),
('07 / Evidence and deployment status','Local results verified. Cloud integration still pending.',None,
 'The saved report records three hundred thirty three passing tests, including two hundred ninety nine independent scenarios. Those use local subprocesses; Docker has separate tests. Current screens use local explanations. Verified Vultr deployment, live inference, and a public demo remain pending.'),
('Repeatable. Reviewable. Verifiable.','github.com/CAPEXNULL/Vultr-Dispatcher',None,
 'For procurement, the benefit is an explainable choice under explicit constraints, buyer control, and evidence of the actual update. Public source and setup instructions make that workflow reviewable.'),
]

def make_frame(i):
    heading,sub,shot,narration=SCENES[i]
    im=Image.new('RGB',(1920,1080),'#08131e'); d=ImageDraw.Draw(im)
    d.rectangle((0,0,1920,10),fill='#ffad16')
    text(d,(72,42),'CAPEXNULL  /  SUPPLY DISPATCHER',24,'#ffad16',bold=True,width=1752)
    text(d,(72,98),heading,52,bold=True,width=1752)
    text(d,(72,180),sub,31,'#9eb5c9',width=1752)
    if shot:
        def detail(name,region):
            image=Image.open(TMP/'hd'/(name+'.png')).convert('RGB')
            scale=min((region[2]-region[0])/image.width,(region[3]-region[1])/image.height)
            assert scale<=1, f'Never enlarge a low-resolution UI image: {name}'
            image=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
            im.paste(image,(region[0]+(region[2]-region[0]-image.width)//2,region[1]+(region[3]-region[1]-image.height)//2))
        if i==1:
            detail('order',(36,275,1884,990))
        elif i==2:
            detail('analytics',(72,260,1080,995))
            detail('recommendation',(1130,260,1850,995))
        elif i==3:
            detail('plan',(72,265,910,990))
            detail('recommendation',(984,265,1848,990))
        elif i==4:
            detail('confirmed',(72,265,910,990))
            detail('evidence',(984,265,1848,990))
    else:
        blocks={
        0:['Deterministic supplier selection','Human approval before mutation','Independent verification after commit'],
        5:['Memory: 128 MiB  |  CPU: 0.50  |  PIDs: 64','Network disabled  |  Read-only root  |  No app secret','Timeout enforced  >  Container destroyed  >  Next task PASS'],
        6:['Verified success > Compatible conditions > Recalculate winner','Reuse may skip explanation; never calculation or approval','Repeated approval: no duplicate update. Changed input: new analysis.'],
        7:['Recorded local report: 333 passing tests / 299 independent scenarios','Local explanations; separate saved Docker containment tests','Pending: Vultr VM + live inference + public HTTPS demo'],
        8:['github.com/CAPEXNULL/Vultr-Dispatcher','Setup, architecture, tests and containment demonstration','Status: local release verified; cloud completion pending']}
        y=324
        for block in blocks[i]:
            d.rounded_rectangle((72,y-19,1848,y+120),radius=18,fill='#122536')
            text(d,(108,y+11),block,36,width=1692,bold=True); y+=192
    d.rectangle((0,1020,1920,1080),fill='#112130')
    text(d,(72,1034),'LOCAL DEMO WALKTHROUGH  |  No cloud deployment claimed',22,'#c0d0df',width=1660)
    text(d,(1764,1034),f'{i+1:02d} / 09',22)
    im.save(TMP/f'scene-{i:02d}.png')
    return im

def prepare():
    for i,s in enumerate(SCENES):
        make_frame(i); (TMP/f'voice-{i:02d}.txt').write_text(s[3],encoding='utf-8')
    assert (OUT/'Supply-Dispatcher-Cover.png').is_file(), 'Keep the approved cinematic cover.'
    doc=fitz.open(ROOT/'output/pdf/Supply-Dispatcher-Pitch.pdf')
    contact=Image.new('RGB',(1440,1168),'#ddd')
    for i,p in enumerate(doc):
        pix=p.get_pixmap(matrix=fitz.Matrix(.48,.48)); img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
        contact.paste(img,((i%3)*480,(i//3)*292))
    contact.save(TMP/'pitch-contact.png')

def assemble():
    ff=imageio_ffmpeg.get_ffmpeg_exe(); manifest=[]; elapsed=0; srt=[]
    for i,s in enumerate(SCENES):
        wav=TMP/f'voice-{i:02d}.wav'
        with wave.open(str(wav)) as w: duration=w.getnframes()/w.getframerate()+0.7
        target=TMP/f'clip-{i:02d}.mp4'
        frame=OUT/'Supply-Dispatcher-Cover.png' if i==0 else TMP/f'scene-{i:02d}.png'
        subprocess.run([ff,'-y','-loop','1','-framerate','10','-i',str(frame),'-i',str(wav),'-t',str(duration),'-vf','scale=1920:1080:flags=lanczos,setsar=1','-af','apad=pad_dur=0.7','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','1',str(target)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        manifest.append("file '"+target.as_posix()+"'")
        elapsed+=duration
    (TMP/'concat.txt').write_text('\n'.join(manifest),encoding='utf-8')
    subprocess.run([ff,'-y','-f','concat','-safe','0','-i',str(TMP/'concat.txt'),'-vf','fps=25,setsar=1','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','1','-movflags','+faststart',str(OUT/'Supply-Dispatcher-Demo-FullHD.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    (OUT/'Supply-Dispatcher-Transcript.txt').write_text('\n\n'.join(s[0]+'\n'+s[3] for s in SCENES),encoding='utf-8')
    print(json.dumps({'duration_seconds':round(elapsed,1),'video_bytes':(OUT/'Supply-Dispatcher-Demo-FullHD.mp4').stat().st_size,'scenes':len(SCENES)}))

if __name__=='__main__':
    import sys
    assemble() if 'assemble' in sys.argv else prepare()
