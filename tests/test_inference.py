import json
import pytest
from inference import explain, BASE_URL
from test_app import payload

def test_production_inference_requires_credentials(monkeypatch):
    monkeypatch.delenv('VULTR_SERVERLESS_INFERENCE_API_KEY',raising=False)
    monkeypatch.setenv('REQUIRE_VULTR_INFERENCE','1')
    with pytest.raises(RuntimeError): explain(payload(),payload()['offers'][0])

def test_all_llm_calls_use_fixed_vultr_endpoint(monkeypatch):
    monkeypatch.setenv('VULTR_SERVERLESS_INFERENCE_API_KEY','test-only-placeholder')
    monkeypatch.setenv('VULTR_MODEL','test-model')
    observed=[]
    class Response:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def read(self): return json.dumps({'choices':[{'message':{'content':'Supplier A meets the order conditions.'}}]}).encode()
    def open_request(req,timeout):
        observed.append(req)
        return Response()
    monkeypatch.setattr('urllib.request.urlopen',open_request)
    explanation,called,source=explain(payload(),payload()['offers'][0])
    assert called and source=='vultr-serverless-inference'
    assert observed[0].full_url==BASE_URL+'/chat/completions'
    body=json.loads(observed[0].data)
    assert body['model']=='test-model' and 'English' in body['messages'][0]['content']

def test_production_failure_does_not_silently_fallback(monkeypatch):
    monkeypatch.setenv('VULTR_SERVERLESS_INFERENCE_API_KEY','test-only-placeholder')
    monkeypatch.setenv('VULTR_MODEL','test-model')
    monkeypatch.setenv('REQUIRE_VULTR_INFERENCE','1')
    def fail(*args,**kwargs): raise OSError('simulated network failure')
    monkeypatch.setattr('urllib.request.urlopen',fail)
    with pytest.raises(OSError): explain(payload(),payload()['offers'][0])
