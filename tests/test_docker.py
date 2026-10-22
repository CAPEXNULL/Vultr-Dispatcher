import os
from containment_demo import demonstrate
from sandbox_runner import SandboxRunner
from test_app import payload
import pytest

@pytest.mark.docker
def test_real_docker_solver_and_independent_process():
    result,evidence=SandboxRunner(backend='docker').run_solver(payload())
    assert result['selected']['supplier_id']=='A'
    assert evidence['contained'] and len(evidence['output_sha256'])==64

@pytest.mark.docker
def test_containment_timeout_cleanup_and_recovery(monkeypatch):
    monkeypatch.setenv('VULTR_SERVERLESS_INFERENCE_API_KEY','containment-test-sentinel')
    proof=demonstrate()
    assert proof['status']=='PASS' and not proof['observed']['secret_present']
