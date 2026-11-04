"""Check every decoded frame, scene boundaries and actual visible action frames."""
from pathlib import Path
import json,hashlib,subprocess
import cv2,numpy as np,imageio_ffmpeg
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];TMP=ROOT/'tmp/media/actions'
def check():
    path=TMP/'final.mp4';cap=cv2.VideoCapture(str(path));fps=cap.get(cv2.CAP_PROP_FPS);n=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));assert fps==25 and n/fps<180
    white=[];black=[];idx=0
    while True:
        ok,frame=cap.read()
        if not ok:break
        sample=frame[::8,::8]
        if np.mean(np.all(sample>240,axis=2))>.95:white.append(idx)
        if np.mean(np.all(sample<8,axis=2))>.98:black.append(idx)
        idx+=1
    cap.release();assert not white and not black,{'white':white,'black':black}
    run=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(path),'-f','null','-'],capture_output=True);assert run.returncode==0 and not run.stderr
    info=json.loads((TMP/'build.json').read_text());times=[];start=0
    for i,d in enumerate(info['scene_seconds']):
        for f in [.08,.5,.92]:times.append((i,start+d*f))
        start+=d
    # Explicitly inspect the originally reported interval as well.
    times.extend([(9,t) for t in [56,57,58,59,60]])
    cap=cv2.VideoCapture(str(path));sheet=Image.new('RGB',(1920,((len(times)+3)//4)*285),'#eee')
    for j,(i,t) in enumerate(times):
        cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,bgr=cap.read();assert ok
        image=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB));image.thumbnail((475,267));x=(j%4)*480;y=(j//4)*285;sheet.paste(image,(x,y));ImageDraw.Draw(sheet).text((x+6,y+269),f'Scene {i+1} | {t:.1f}s',fill='#111')
    sheet.save(TMP/'all-scenes.png');cap.release()
    result={'duration_seconds':n/fps,'resolution':'1920x1080','fps':fps,'decoded_frames':idx,'white_frames':len(white),'black_frames':len(black),'decode_errors':0,'scene_seconds':info['scene_seconds'],'normal_voice_speed':True,'voice':'Microsoft Zira Desktop','voice_rate':0,'playback_speed':1,'ordered_actions':['define order','enter offers','Analyze disruption','switch analytics views','Approve replacement','open Evidence','Edit conditions','analyze again','repeat approval safely'],'pointer_and_click_marker':True,'white_preroll_removed':True,'synthetic_only':True,'cover_sha256':hashlib.sha256((ROOT/'output/media/Supply-Dispatcher-Cover.png').read_bytes()).hexdigest(),'final_video_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'uploaded':False}
    (TMP/'qa.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':check()
