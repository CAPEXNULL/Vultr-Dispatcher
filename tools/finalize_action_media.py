from pathlib import Path
import json,shutil,hashlib
from build_action_media import ROOT,OUT,TMP,EVIDENCE,SCENES

qa=json.loads((TMP/'qa.json').read_text())
assert qa['white_frames']==0 and qa['black_frames']==0 and qa['decode_errors']==0 and qa['duration_seconds']<180
assert qa['final_video_sha256']==hashlib.sha256((TMP/'final.mp4').read_bytes()).hexdigest()
assert qa['cover_sha256']==hashlib.sha256((OUT/'Supply-Dispatcher-Cover.png').read_bytes()).hexdigest()
if not (TMP/'prior-final.mp4').exists():shutil.copy2(OUT/'Supply-Dispatcher-Demo-FullHD.mp4',TMP/'prior-final.mp4')
shutil.copy2(TMP/'final.mp4',OUT/'Supply-Dispatcher-Demo-FullHD.mp4')
shutil.copy2(TMP/'workflow.webm',EVIDENCE/'Supply-Dispatcher-Action-Workflow.webm')
(OUT/'media-check.json').write_text(json.dumps(qa,indent=2)+'\n')
(OUT/'Supply-Dispatcher-Transcript.txt').write_text('\n\n'.join(s[0]+'\n'+s[2] for s in SCENES)+'\n')
timeline=[];start=0
for i,(scene,d) in enumerate(zip(SCENES,qa['scene_seconds'])):
    timeline.extend([f'## {i+1}. {scene[0]}',f'{start:.2f}-{start+d:.2f} seconds', '',scene[2],'']);start+=d
(ROOT/'VIDEO_SCRIPT.md').write_text('# Final video: visible action sequence\n\nActual public-app actions with visible cursor and click markers. Normal speech and playback speed. Synthetic data only.\n\n'+'\n'.join(timeline))
(OUT/'VIDEO_FACT_CHECK.md').write_text('''# Final action video verification

This revision replaces the previous montage. The main walkthrough is a new actual public HTTPS browser recording. It shows the real order-entry, supplier-entry, analysis, analytics-view selection, first approval, Evidence expansion, return to inputs, experience reuse and idempotent repeated approval, in that order. Pointer movement and click rings mark actual mouse events. Step labels are recording overlays; application responses are not mocked, injected or replayed.

The browser is displayed at 125 percent zoom for readability and recorded at 1920x1080. Navigation/loading frames before the first ready step are excluded using the visible step markers. Every decoded final frame is checked for a predominantly white or black screen. All stage boundaries and the reported 00:56-01:00 interval are visually reviewed. See media-check.json for exact duration and results.

One fresh synthetic case uses real Vultr inference; the repeated case uses verified experience without another model call. Actual response evidence: reports/cloud-evidence/action-workflow.json. The unedited new browser source is retained as reports/cloud-evidence/Supply-Dispatcher-Action-Workflow.webm.

The separate containment section remains recorded remote evidence replayed at its observed timing and labelled as such. Its raw execution and observed policy remain in reports/cloud-evidence/containment-live.json. The approved cover is unchanged. Normal Zira narration rate 0 and normal video playback are preserved. No real purchases, customer savings or production ROI are claimed. Public upload/submission remains outstanding.
''')
p=ROOT/'README.md';s=p.read_text();s=s.replace('(2:43, normal voice speed)',f'({qa["duration_seconds"]:.2f} seconds, normal voice speed)');s=s.replace('includes actual cloud workflow footage and recorded containment evidence','shows the actual sequence of cloud UI actions with visible clicks, plus recorded containment evidence');p.write_text(s)
p=ROOT/'SUBMISSION.md';s=p.read_text();s=s.replace('1920x1080, 2:43, normal voice speed',f'1920x1080, {qa["duration_seconds"]:.2f} seconds, normal voice speed');s=s.replace('It combines actual public HTTPS workflow footage, readable views of recorded results and containment evidence at observed timing.','It shows the actual public HTTPS action sequence with visible clicks, including first approval, Evidence inspection and safe repetition, followed by containment evidence at observed timing.');p.write_text(s)
p=ROOT/'reports/cloud-deployment.json';d=json.loads(p.read_text());d['final_media'].update(duration_seconds=qa['duration_seconds'],revision='Actual ordered actions with visible pointer/click markers; white pre-roll removed');d['limitations']=[x.replace('high-DPI reading views of the retained response','actual ordered public UI actions with visible clicks') for x in d['limitations']];d['action_video_evidence']='reports/cloud-evidence/action-workflow.json';d['inference_attempts']['total']=4;d['inference_attempts']['action_recording']='PASS; one fresh synthetic call, repeat used experience';p.write_text(json.dumps(d,indent=2)+'\n')
p=ROOT/'docs/NEXT_SESSION.md';s=p.read_text();note=f'''## Corrected action video - 2026-11-05

Owner reported a white screen at 00:56-01:00 and missing visible click sequence. Replaced the prior montage after confirming its browser source contained white navigation pre-roll. Final video now {qa['duration_seconds']:.2f}sec, FullHD25fps, normal Zira rate0. Main section is a new real public browser sequence with visible pointer and actual click rings: conditions, offers, Analyze, analytics views, first Approve, Evidence, Edit conditions, reanalyze via verified experience, idempotent reapproval. Browser zoom125percent. No injected API/rendered response in this revision. One fresh synthetic inference call; experience repeat had no call. Total cloud model attempts now4 across deployment/media work.

Raw new source: reports/cloud-evidence/Supply-Dispatcher-Action-Workflow.webm. Primary proof: reports/cloud-evidence/action-workflow.json. Every decoded final frame checked: zero predominantly white/black frames, zero decode errors; stage boundaries and 00:56-01:00 reviewed. Approved cover retained. Separate labelled containment recording unchanged. output/media still has only the same five deliverables. Revised builder: tools/build_action_media.py, QA: tools/check_action_media.py. Prior final kept only under ignored tmp/media/actions/prior-final.mp4 for diagnosis. No infrastructure duplication or publication.

''';p.write_text(s.replace('# VULTR: handoff for a new window\n','# VULTR: handoff for a new window\n\n'+note,1))
assert len(list(OUT.iterdir()))==5
print('Verified replacement published locally; media folder still has five files')
