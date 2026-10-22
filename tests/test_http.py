import json
import threading
import urllib.request
import urllib.error
import pytest
import app
from test_app import payload

@pytest.fixture
def server(tmp_path,monkeypatch):
    monkeypatch.setattr(app,'DB',str(tmp_path/'http.db'))
    monkeypatch.setenv('SANDBOX_BACKEND','local')
    # Handler's analysis uses the module function default, so bind the test database.
    original=app.analyze_request; approve=app.approve_decision
    monkeypatch.setattr(app,'analyze_request',lambda req:original(req,app.DB,'local'))
    monkeypatch.setattr(app,'approve_decision',lambda decision:approve(decision,app.DB))
    app.init_db(app.DB)
    http=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
    thread=threading.Thread(target=http.serve_forever,daemon=True); thread.start()
    yield f'http://127.0.0.1:{http.server_port}'
    http.shutdown(); http.server_close(); thread.join()

def call(server,path,data=None,headers=None):
    req=urllib.request.Request(server+path,data=json.dumps(data).encode() if data is not None else None,headers=headers or {})
    try:
        with urllib.request.urlopen(req) as response: return response.status,response.read()
    except urllib.error.HTTPError as exc: return exc.code,exc.read()

def test_http_e2e_and_persisted_readback(server):
    status,raw=call(server,'/api/analyze',payload()); result=json.loads(raw)
    assert status==200 and result['status']=='PROPOSED'
    assert json.loads(call(server,'/api/order/PO1')[1])['order'] is None
    assert json.loads(call(server,'/api/approve/'+result['decision_id'],{})[1])['status']=='VERIFIED'
    assert json.loads(call(server,'/api/order/PO1')[1])['order']['supplier_id']=='A'

def test_http_rejects_invalid_origin_and_input(server):
    assert call(server,'/api/analyze',{},headers={'Origin':'https://untrusted.invalid'})[0]==403
    assert call(server,'/api/analyze',{})[0]==400

def test_http_static_boundary_and_health(server):
    assert call(server,'/static/../app.py')[0]==404
    assert call(server,'/static/app.js')[0]==200
    assert call(server,'/')[0]==200
    assert call(server,'/health')[0]==200
