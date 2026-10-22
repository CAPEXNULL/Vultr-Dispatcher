"""Automated browser acceptance of the release, with synthetic data only."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def audit():
    output=ROOT/'docs/screenshots'; output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='supply-ui-') as temp:
        env={**os.environ,'PORT':'8013','DISPATCHER_DB':str(Path(temp)/'ui.db'),'SANDBOX_BACKEND':'docker','REQUIRE_VULTR_INFERENCE':'0'}
        process=subprocess.Popen([sys.executable,'app.py'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen('http://127.0.0.1:8013/health',timeout=1); break
                except Exception: time.sleep(.1)
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True)
                page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
                errors=[]; page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto('http://127.0.0.1:8013/')
                assert page.locator('html').get_attribute('lang')=='en'
                page.screenshot(path=str(output/'current-order.png'),full_page=True)
                page.get_by_role('button',name='Light theme',exact=True).click()
                assert page.get_by_role('button',name='Dark theme',exact=True).is_visible()
                page.get_by_role('button',name='Dark theme',exact=True).click()
                page.get_by_role('button',name='Add supplier',exact=True).click()
                assert page.locator('#offersTable tbody tr').count()==4
                page.get_by_role('button',name='Analyze disruption',exact=True).click()
                page.locator('#approve').wait_for(state='visible',timeout=30000)
                assert page.locator('#recommendationBody h3').inner_text()=='SUP-A'
                assert page.locator('#analyticsTable').is_visible()
                page.locator('#analyticsView').select_option('metrics')
                assert page.locator('#analyticsMetrics').is_visible() and not page.locator('#analyticsTable').is_visible()
                assert page.locator('.supplier-metrics').count()==4
                page.locator('#analyticsView').select_option('charts')
                assert page.locator('#analyticsCharts').is_visible() and page.locator('.column-chart').count()==3
                assert not page.locator('#analyticsMetrics').is_visible()
                page.screenshot(path=str(output/'analytics-charts.png'),full_page=True)
                page.get_by_role('button',name='Approve replacement',exact=True).click()
                page.get_by_role('heading',name='Order updated successfully').wait_for(timeout=10000)
                page.get_by_text('Evidence',exact=True).click()
                assert 'Updated order check: Passed' in page.locator('#evidence').inner_text()
                page.screenshot(path=str(output/'verified-result.png'),full_page=True)
                text=page.locator('body').inner_text()
                assert not any('\u0400'<=c<='\u04ff' for c in text)
                for forbidden in ['sandbox_task.py','MATAN','DSO','PROPOSED','SHA-256','run_id','local-dev']:
                    assert forbidden not in text
                for width in [390,768,1440]:
                    page.set_viewport_size({'width':width,'height':900})
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
                    if width==390: page.screenshot(path=str(output/'mobile-result.png'),full_page=True)
                page.get_by_role('button',name='Edit conditions',exact=True).click()
                assert page.locator('#f').is_visible() and not page.locator('#run').is_visible()
                assert not errors,errors
                browser.close()
            # Cold start with the same database, read the persisted result.
            process.terminate(); process.wait(timeout=10)
            process=subprocess.Popen([sys.executable,'app.py'],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
            for _ in range(100):
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8013/api/order/PO-1042',timeout=1) as r: saved=json.load(r)
                    break
                except Exception: time.sleep(.1)
            assert saved['order']['supplier_id']=='SUP-A'
            return {'status':'PASS','controls':['analyze','add supplier','approve','edit conditions','theme','evidence','Table','Metrics','Charts'],'widths':[390,768,1440],'english_only':True,'no_horizontal_page_overflow':True,'javascript_errors':errors,'cold_restart_persistence':True,'execution':'real Docker, local deterministic explanation','public_deployment':'BLOCKED: not provisioned'}
        finally:
            process.terminate(); process.wait(timeout=10)

if __name__=='__main__':
    result=audit(); (ROOT/'reports/ui-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
