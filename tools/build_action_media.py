"""Record an actual ordered public-app walkthrough with visible pointer/clicks."""
from pathlib import Path
import json,time,subprocess,wave,hashlib
import cv2,numpy as np,imageio_ffmpeg
from PIL import Image,ImageDraw
from build_submission_media import text
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/media';TMP=ROOT/'tmp/media/actions';TMP.mkdir(parents=True,exist_ok=True)
EVIDENCE=ROOT/'reports/cloud-evidence';URL='https://supply-dispatcher.80.240.28.98.sslip.io'
SCENES=[
('Supply Dispatcher','cover','A delayed supplier puts an order at risk. Watch the complete recovery workflow on the deployed Vultr application, from entering the task to confirming the saved replacement.'),
('01 / Define the delayed order','ui','First, enter the order and product. Set the required quantity, maximum budget, and delivery deadline. Confirm the supplier delay. Here, twelve units must arrive within five days, with a budget of fifteen hundred. These become mandatory conditions for every alternative.'),
('02 / Enter supplier alternatives','ui','Next, enter the supplier offers under those same conditions. Supplier A offers twelve units for twelve hundred in four days. Supplier B is faster but costs more. The cheaper third offer arrives in eight days, which misses the deadline. Now the comparison is ready.'),
('03 / Analyze disruption','ui','Click Analyze disruption. Supply Dispatcher calculates the best admissible supplier and independently verifies the result. Vultr Serverless Inference turns the checked selection into a clear business explanation. The buyer receives a consistent recommendation, with the reasoning and supporting comparison ready for review.'),
('04 / Review the recommendation','ui','Review the comparison before acting. Switch from the table to metrics and charts. The cheapest offer fails the deadline. Supplier A is the lowest cost admissible option, within budget and available quantity. The recommendation shows its cost and delivery time alongside the explanation.'),
('05 / Approve and inspect evidence','ui','Click Approve replacement to confirm the choice. Supply Dispatcher saves the supplier, cost, and delivery time, then independently reads back the committed result. Open Evidence to inspect the completed checks. The green confirmation gives the buyer a verified record of the successful order recovery.'),
('06 / Reuse and safe repetition','ui','Edit conditions returns to the input form. Run the same case again. Verified experience can avoid a repeated model explanation, while calculation and checking still run. Approving the same saved decision again is safe: the order was already updated, so no duplicate update is created.'),
('Reliable execution','containment','Supply Dispatcher keeps calculation isolated so the workflow stays responsive. Here, an intentionally looping task is stopped automatically. Its container is cleaned up, the host continues working, and the next calculation succeeds. This automatic recovery keeps a failed task from interrupting subsequent work.'),
('Supply Dispatcher online','closing','Supply Dispatcher brings supplier comparison, clear explanations, buyer approval, and verified order recovery into one workflow. Open the application to try it. Public source and setup instructions are available on GitHub.')]
COLORS=['#ffb15a','#60a5fa','#a78bfa','#34d399','#f472b6','#facc15']

def prepare():
    for i,(_,_,s) in enumerate(SCENES):(TMP/f'voice-{i:02d}.txt').write_text(s,encoding='utf-8')
    print('Narration words:',sum(len(s[2].split()) for s in SCENES))

def duration(i):
    with wave.open(str(TMP/f'voice-{i:02d}.wav')) as w:return w.getnframes()/w.getframerate()+.7

def record():
    if (EVIDENCE/'action-workflow.json').exists() and (EVIDENCE/'Supply-Dispatcher-Action-Workflow.webm').exists():
        print('Verified recording already retained; use split/build to avoid another model call.')
        return
    from playwright.sync_api import sync_playwright
    events=[];proof={}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        c=browser.new_context(viewport={'width':1920,'height':1080},record_video_dir=str(TMP/'raw'),record_video_size={'width':1920,'height':1080})
        page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(URL);page.locator('#offersTable').wait_for();page.evaluate("document.body.style.zoom='1.25'")
        page.evaluate('''() => {
          const style=document.createElement('style');style.textContent=`
          #demo-pointer{position:fixed;left:960px;top:540px;width:24px;height:32px;background:white;clip-path:polygon(0 0,0 100%,28% 72%,52% 100%,70% 90%,46% 63%,90% 63%);filter:drop-shadow(1px 1px 2px black);z-index:2147483647;pointer-events:none}
          #demo-click{position:fixed;width:56px;height:56px;border:5px solid #ffb15a;border-radius:50%;z-index:2147483646;pointer-events:none;display:none;box-shadow:0 0 20px #ffb15a}
          #demo-step{position:fixed;bottom:0;left:0;right:0;height:64px;box-sizing:border-box;padding:14px 26px;background:#142638;color:white;border-left:12px solid #ffb15a;font:28px 'Segoe UI',sans-serif;z-index:2147483645;pointer-events:none}`;
          document.head.append(style);
          for(const id of ['demo-step','demo-click','demo-pointer']){let el=document.createElement('div');el.id=id;document.documentElement.append(el)}
          addEventListener('pointermove',e=>{let el=document.querySelector('#demo-pointer');el.style.left=e.clientX+'px';el.style.top=e.clientY+'px'});
          addEventListener('pointerdown',e=>{let el=document.querySelector('#demo-click');el.style.left=(e.clientX-28)+'px';el.style.top=(e.clientY-28)+'px';el.style.display='block';setTimeout(()=>el.style.display='none',650)},true);
        }''')
        def stage(n):
            page.evaluate('([label,color])=>{let el=document.querySelector("#demo-step");el.textContent=label;el.style.borderLeftColor=color}',[SCENES[n][0],COLORS[n-1]])
            events.append({'stage':n,'label':SCENES[n][0]});return time.monotonic()
        def finish(n,t):
            remaining=duration(n)-(time.monotonic()-t)
            if remaining>0:page.wait_for_timeout(remaining*1000)
            events[-1]['actual_seconds']=round(time.monotonic()-t,3)
        def point(loc):
            loc.scroll_into_view_if_needed();box=loc.bounding_box();page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2,steps=20);page.wait_for_timeout(350)
        def click(loc):
            point(loc);loc.click();page.wait_for_timeout(700)
        def fill(selector,value):
            loc=page.locator(selector);click(loc);loc.press('Control+A');loc.press_sequentially(value,delay=40);page.wait_for_timeout(150)
        t=stage(1)
        for k,v in {'order':'CLOUD-ACTION-20261105-D','product':'SYNTH-PUMP-88','qty':'12','budget':'1500','deadline':'5','currentSupplier':'SYNTH-DELAYED'}.items():fill('#'+k,v)
        click(page.locator('#delay'));click(page.locator('#delay'));finish(1,t)
        t=stage(2)
        data=[['SUP-A','SYNTH-PUMP-88','12','1200','4'],['SUP-B','SYNTH-PUMP-88','20','1350','3'],['SUP-LATE','SYNTH-PUMP-88','12','900','8']]
        for i,row in enumerate(data):
            for j,v in enumerate(row):
                loc=page.locator('#offersTable tbody tr').nth(i).locator('input').nth(j);point(loc);loc.click();loc.fill(v);page.wait_for_timeout(220)
        finish(2,t)
        t=stage(3)
        with page.expect_response(lambda r:r.url.endswith('/api/analyze'),timeout=60000) as response:click(page.locator('#analyze'))
        a=response.value.json();proof['analysis']=a
        assert a['status']=='PROPOSED' and a['inference_source']=='vultr-serverless-inference' and a['llm_called'] and a['selected']['supplier_id']=='SUP-A',a
        page.locator('#approve').wait_for(state='visible');point(page.locator('#recommendation'));finish(3,t)
        t=stage(4)
        select=page.locator('#analyticsView')
        for mode in ['metrics','charts','table','charts']:
            click(select);select.select_option(mode);page.wait_for_timeout(2200)
        point(page.locator('#approve'));finish(4,t)
        t=stage(5)
        with page.expect_response(lambda r:'/api/approve/' in r.url) as response:click(page.locator('#approve'))
        proof['approval']=response.value.json();assert proof['approval']['status']=='VERIFIED' and not proof['approval']['idempotent']
        page.get_by_text('Order updated successfully',exact=True).wait_for();click(page.locator('details summary'));point(page.locator('#evidence'));finish(5,t)
        t=stage(6);click(page.locator('#editConditions'))
        with page.expect_response(lambda r:r.url.endswith('/api/analyze')) as response:click(page.locator('#analyze'))
        proof['reuse']=response.value.json();assert proof['reuse']['experience_used'] and not proof['reuse']['llm_called']
        with page.expect_response(lambda r:'/api/approve/' in r.url) as response:click(page.locator('#approve'))
        proof['repeated_approval']=response.value.json();assert proof['repeated_approval']['idempotent']
        point(page.locator('#verified'));finish(6,t)
        assert not errors,errors
        video=page.video;c.close();video.save_as(str(TMP/'workflow.webm'));browser.close()
    (EVIDENCE/'action-workflow.json').write_text(json.dumps({'status':'PASS','url':URL,'synthetic_only':True,'events':events,'proof':proof,'javascript_errors':errors,'paid_model_calls':1},indent=2)+'\n')
    print(json.dumps({'status':'PASS','stages':events}))

def split():
    source=TMP/'workflow.webm' if (TMP/'workflow.webm').exists() else EVIDENCE/'Supply-Dispatcher-Action-Workflow.webm'
    cap=cv2.VideoCapture(str(source));fps=cap.get(cv2.CAP_PROP_FPS)
    colors=np.array([[int(c[k:k+2],16) for k in [1,3,5]] for c in COLORS]);ranges={};idx=0;white=0
    while True:
        ok,bgr=cap.read()
        if not ok:break
        rgb=bgr[1040,4,::-1].astype(float);delta=np.linalg.norm(colors-rgb,axis=1);n=int(np.argmin(delta))+1
        if delta[n-1]<30:
            if n not in ranges:ranges[n]=[idx,idx]
            ranges[n][1]=idx
        idx+=1
    cap.release();assert len(ranges)==6,ranges
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    for n,(start,end) in ranges.items():
        subprocess.run([ff,'-y','-ss',str(start/fps),'-i',str(source),'-t',str((end-start+1)/fps),'-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-an',str(TMP/f'ui-{n}.mp4')],capture_output=True,check=True)
    (TMP/'ranges.json').write_text(json.dumps({'fps':fps,'ranges':ranges},indent=2));print('Ready-only footage split:',ranges)

def build():
    ff=imageio_ffmpeg.get_ffmpeg_exe();clips=[];durations=[]
    for i,(title,kind,narration) in enumerate(SCENES):
        d=duration(i)
        if kind=='cover':inputs=['-loop','1','-framerate','25','-i',str(OUT/'Supply-Dispatcher-Cover.png')];vf='scale=1920:1080:flags=lanczos,setsar=1'
        elif kind in ['ui','containment']:
            source=TMP/f'ui-{i}.mp4' if kind=='ui' else EVIDENCE/'Supply-Dispatcher-Cloud-Containment.mp4'
            r=imageio_ffmpeg.read_frames(str(source));m=next(r);r.close();d=max(d,m['duration'])
            inputs=['-i',str(source)];vf=f'tpad=stop_mode=clone:stop_duration={d},fps=25,setsar=1'
        else:
            im=Image.new('RGB',(1920,1080),'#08131e');draw=ImageDraw.Draw(im)
            text(draw,(80,120),'Supply Dispatcher',64,bold=True,width=1760)
            text(draw,(80,300),'Supplier recovery, from comparison to confirmation',44,'#ffb15a',width=1760)
            text(draw,(80,430),'supply-dispatcher.80.240.28.98.sslip.io',42,width=1760)
            text(draw,(80,620),'github.com/CAPEXNULL/Vultr-Dispatcher',38,width=1760)
            text(draw,(80,860),'Consistent selection. Buyer control. Verified saved results.',28,width=1760)
            im.save(TMP/'closing.png');inputs=['-loop','1','-framerate','25','-i',str(TMP/'closing.png')];vf='setsar=1'
        clip=TMP/f'clip-{i}.mp4'
        subprocess.run([ff,'-y',*inputs,'-i',str(TMP/f'voice-{i:02d}.wav'),'-t',str(d),'-map','0:v','-map','1:a','-vf',vf,'-af','apad','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-ar','44100','-ac','1',str(clip)],capture_output=True,check=True)
        clips.append(clip);durations.append(d)
    assert sum(durations)<180,('Shorten narration/actions; never speed up',durations,sum(durations))
    concat=TMP/'concat.txt';concat.write_text('\n'.join("file '"+c.as_posix()+"'" for c in clips))
    draft=TMP/'final.mp4'
    subprocess.run([ff,'-y','-f','concat','-safe','0','-i',str(concat),'-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','25','-c:a','aac','-ar','44100','-ac','1','-movflags','+faststart',str(draft)],capture_output=True,check=True)
    (TMP/'build.json').write_text(json.dumps({'scene_seconds':durations,'expected_seconds':sum(durations)},indent=2));print('Draft complete',sum(durations))

if __name__=='__main__':
    import sys
    {'prepare':prepare,'record':record,'split':split,'build':build}[sys.argv[1]]()
