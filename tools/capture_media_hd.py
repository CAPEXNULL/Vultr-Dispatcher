"""Render the local application in an isolated test browser for video assets."""
from pathlib import Path
import os,sys,subprocess,tempfile,time,json,urllib.request
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'tmp/media/hd';OUT.mkdir(parents=True,exist_ok=True)

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
    env={**os.environ,'PORT':'8014','BIND_HOST':'127.0.0.1','DISPATCHER_DB':str(Path(td)/'capture.db'),'SANDBOX_BACKEND':'local','REQUIRE_VULTR_INFERENCE':'0'}
    process=subprocess.Popen([sys.executable,'app.py'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    try:
        for _ in range(60):
            try: urllib.request.urlopen('http://127.0.0.1:8014/health',timeout=1);break
            except Exception:time.sleep(.1)
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=4)
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto('http://127.0.0.1:8014/');page.locator('#offersTable').wait_for()
            assets={}
            def capture(name,selector):
                locator=page.locator(selector);locator.screenshot(path=str(OUT/(name+'.png')))
                box=locator.bounding_box();assets[name]={'selector':selector,'css_width':box['width'],'css_height':box['height'],'device_scale_factor':4}
            capture('order','#f')
            page.locator('#addOffer').click()
            page.locator('#analyze').click();page.locator('#approve').wait_for(state='visible')
            assert page.locator('#recommendationBody h3').inner_text()=='SUP-A'
            page.locator('#analyticsView').select_option('charts')
            capture('analytics','#analyticsCharts');capture('recommendation','#recommendation')
            capture('plan','.plan-card')
            page.locator('#approve').click();page.get_by_text('Order updated successfully',exact=True).wait_for()
            page.locator('details').evaluate('(element)=>element.open=true')
            capture('confirmed','#verified');capture('evidence','.evidence-card')
            assert page.locator('#evidence').inner_text().count('Passed')==2
            assert not errors,errors
            browser.close()
            (OUT/'capture.json').write_text(json.dumps({'assets':assets,'backend':'local-dev subprocess','current_code':True,'javascript_errors':errors},indent=2))
            print(json.dumps(assets))
    finally:
        process.terminate();process.wait(timeout=10)
