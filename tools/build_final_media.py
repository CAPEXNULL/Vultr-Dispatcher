"""Superseded montage builder; use build_action_media.py for the action video."""
from pathlib import Path
import json,subprocess,wave,hashlib
from PIL import Image,ImageDraw
import imageio_ffmpeg
from build_submission_media import text
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/media';TMP=ROOT/'tmp/media/final';TMP.mkdir(parents=True,exist_ok=True)
EVIDENCE=ROOT/'reports/cloud-evidence'
SCENES=[
('Supply Dispatcher','Verified recovery after a supplier delay','cover',
'A delayed supplier puts an order at risk. Supply Dispatcher compares the alternatives, keeps the buyer in control, and verifies that the approved replacement was actually saved.'),
('A precise recovery task','Synthetic order on the deployed Vultr application','order',
'The buyer defines the product, quantity, budget, and delivery deadline. Here, twelve units must arrive within five days, with a budget of fifteen hundred. The delay is confirmed. Every supplier is checked against those same requirements. This makes the comparison explicit and repeatable.'),
('The cheapest feasible supplier wins','Recorded cloud result: SYNTH-A, 1,200, four days','comparison',
'The cheapest offer arrives too late. Supplier A meets every constraint at twelve hundred, with delivery in four days. Supplier B is faster but costs one hundred fifty more. The deterministic solver ranks cost first, then delivery time and supplier identifier. An independent implementation checks the winner.'),
('Actual public HTTPS workflow','Recorded browser session; real Vultr Serverless Inference','workflow',
'This is the recorded public workflow running on a Vultr virtual machine. Vultr Serverless Inference explains the already checked selection. It cannot change the chosen supplier. The buyer reviews the comparison before approving the replacement.'),
('Approval produces a verified record','Commit, independent readback, visible confirmation','verified',
'Approval commits the supplier, cost, and delivery time to the application ledger. A fresh database connection reads back the saved values. Both cloud test orders survived a service restart and a virtual machine reboot. Repeated approval does not create another update. This demonstration does not place real purchases.'),
('Execution has a hard boundary','Recorded remote execution; observed timing preserved','containment',
'The recorded containment test deliberately runs an infinite loop. Docker disables networking and limits memory, CPU, and process count. The five second wall limit stops the task. The container is removed, the host continues, and the next isolated solver task succeeds. No application credentials reach the task.'),
('Experience saves repeated explanation','Fresh calculation and buyer approval remain mandatory','experience',
'Only verified successes enter experience storage. Reuse requires compatible conditions and the same freshly calculated winner. It may skip a repeated model explanation, while preserving calculation, independent checking, and approval. Changed conditions invalidate an old pending proposal. The benefit is a reviewable choice with proof of the actual update.'),
('Try the public demo','supply-dispatcher.80.240.28.98.sslip.io','closing',
'The public demo now runs on Vultr with verified HTTPS, live inference, and recorded Docker containment. The source and setup instructions are public on GitHub. All examples are synthetic. Customer savings and production return on investment have not been measured.')]

def capture():
    from playwright.sync_api import sync_playwright
    a=json.loads((EVIDENCE/'public-analysis.json').read_text())
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=3)
        page.goto('https://supply-dispatcher.80.240.28.98.sslip.io');page.locator('#offersTable').wait_for()
        values={'order':'CLOUD-UI-20261105-C','currentSupplier':'SYNTH-DELAYED','product':'SYNTHETIC-GEAR-77','qty':'12','budget':'1500','deadline':'5'}
        for k,v in values.items():page.locator('#'+k).fill(v)
        data=[['SYNTH-A','SYNTHETIC-GEAR-77','12','1200','4'],['SYNTH-B','SYNTHETIC-GEAR-77','20','1350','3'],['SYNTH-LATE','SYNTHETIC-GEAR-77','12','900','8']]
        for i,row in enumerate(data):
            for j,v in enumerate(row):page.locator('#offersTable tbody tr').nth(i).locator('input').nth(j).fill(v)
        page.locator('#f').screenshot(path=str(TMP/'order.png'))
        # Display the unchanged retained response through the application's own renderer.
        page.evaluate('(d)=>render(d)',a);page.locator('#analyticsView').select_option('charts')
        page.locator('#analyticsCharts').screenshot(path=str(TMP/'analytics.png'));page.locator('#recommendation').screenshot(path=str(TMP/'recommendation.png'))
        with page.expect_response(lambda r:'/api/approve/' in r.url) as response:page.locator('#approve').click()
        assert response.value.json()['idempotent'] is True
        page.get_by_text('Order updated successfully',exact=True).wait_for();page.locator('details').evaluate('(e)=>e.open=true')
        page.locator('#verified').screenshot(path=str(TMP/'verified.png'));page.locator('.evidence-card').screenshot(path=str(TMP/'evidence.png'))
        browser.close()
    print('High-DPI reading views captured; no analysis/model call')

def frame(i):
    title,sub,kind,_=SCENES[i]
    if kind=='cover':return OUT/'Supply-Dispatcher-Cover.png'
    im=Image.new('RGB',(1920,1080),'#08131e');d=ImageDraw.Draw(im)
    text(d,(70,44),'SUPPLY DISPATCHER',24,'#ffb15a',bold=True,width=1780)
    text(d,(70,100),title,50,bold=True,width=1780)
    text(d,(70,185),sub,29,'#adc2d4',width=1780)
    def put(name,box):
        shot=Image.open(TMP/(name+'.png')).convert('RGB');scale=min(1,(box[2]-box[0])/shot.width,(box[3]-box[1])/shot.height)
        assert scale<=1,'Do not enlarge UI screenshots'
        shot=shot.resize((round(shot.width*scale),round(shot.height*scale)),Image.Resampling.LANCZOS)
        im.paste(shot,(box[0]+(box[2]-box[0]-shot.width)//2,box[1]+(box[3]-box[1]-shot.height)//2))
    if kind=='order':put('order',(40,270,1880,995))
    elif kind=='comparison':put('analytics',(55,265,1105,995));put('recommendation',(1150,265,1865,995))
    elif kind=='verified':put('verified',(70,290,980,950));put('evidence',(1030,290,1850,950))
    else:
        lines={
        'experience':['Verified success is stored after approval and readback.','Reuse requires compatible conditions and the same fresh winner.','Calculation and human approval are always required.','Changed conditions invalidate an outdated proposal.'],
        'closing':['Public HTTPS demo on Vultr','supply-dispatcher.80.240.28.98.sslip.io','github.com/CAPEXNULL/Vultr-Dispatcher','Synthetic demonstration; no measured customer ROI.']}
        y=345
        for line in lines[kind]:y=text(d,(85,y),line,36,width=1750,bold=kind=='closing')+65
    text(d,(70,1035),'VERIFIED CLOUD DEMONSTRATION  |  Synthetic data only',22,'#adc2d4',width=1780)
    target=TMP/f'frame-{i:02d}.png';im.save(target);return target

def prepare():
    for i,s in enumerate(SCENES):(TMP/f'voice-{i:02d}.txt').write_text(s[3],encoding='utf-8')
    print('Narration prepared:',sum(len(s[3].split()) for s in SCENES),'words')

def build():
    ff=imageio_ffmpeg.get_ffmpeg_exe();durations=[];clips=[]
    for i,scene in enumerate(SCENES):
        kind=scene[2];wav=TMP/f'voice-{i:02d}.wav'
        with wave.open(str(wav)) as w:duration=w.getnframes()/w.getframerate()+0.65
        if kind in ['workflow','containment']:
            video=EVIDENCE/('Supply-Dispatcher-Cloud-'+('Workflow' if kind=='workflow' else 'Containment')+'.mp4')
            reader=imageio_ffmpeg.read_frames(str(video));metadata=next(reader);reader.close()
            duration=max(duration,metadata['duration'])
            inputs=['-i',str(video)]
            vf=f'tpad=stop_mode=clone:stop_duration={duration},fps=25,setsar=1'
        else:inputs=['-loop','1','-framerate','25','-i',str(frame(i))];vf='scale=1920:1080:flags=lanczos,setsar=1'
        target=TMP/f'clip-{i:02d}.mp4'
        subprocess.run([ff,'-y',*inputs,'-i',str(wav),'-t',str(duration),'-map','0:v:0','-map','1:a:0','-vf',vf,'-af','apad=pad_dur=0.65','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','1',str(target)],capture_output=True,check=True)
        durations.append(duration);clips.append(target)
    assert sum(durations)<180,('Shorten script; never accelerate narration',sum(durations))
    concat=TMP/'concat.txt';concat.write_text('\n'.join("file '"+p.as_posix()+"'" for p in clips))
    target=OUT/'Supply-Dispatcher-Demo-FullHD.mp4'
    subprocess.run([ff,'-y','-f','concat','-safe','0','-i',str(concat),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','25','-c:a','aac','-ar','44100','-ac','1','-movflags','+faststart',str(target)],capture_output=True,check=True)
    (OUT/'Supply-Dispatcher-Transcript.txt').write_text('\n\n'.join(s[0]+'\n'+s[3] for s in SCENES),encoding='utf-8')
    info={'file':target.name,'resolution':'1920x1080','fps':25,'duration_seconds':round(sum(durations),2),'normal_voice_speed':True,'voice':'Microsoft Zira Desktop','voice_rate':0,'ui_upscaled':False,'scene_seconds':durations,'cloud_video_playback_speed':1,'high_dpi_views':'Unchanged retained cloud response rendered through actual public app; idempotent approval readback','cover_sha256':hashlib.sha256((OUT/'Supply-Dispatcher-Cover.png').read_bytes()).hexdigest(),'uploaded':False}
    (OUT/'media-check.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info))
if __name__=='__main__':
    import sys
    {'capture':capture,'prepare':prepare,'build':build}[sys.argv[1]]()
