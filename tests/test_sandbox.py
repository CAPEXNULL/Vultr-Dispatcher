from pathlib import Path
from sandbox_runner import SandboxRunner

def req():
    return {'order_id':'1','product':'X','quantity':10,'max_budget':100,'deadline_days':5,'delay_confirmed':True,'offers':[{'supplier_id':'A','product':'X','available_qty':10,'total_cost':90,'eta_days':3}]}

def test_local_sandbox_executes_solver():
    r,e=SandboxRunner(backend='local').run_solver(req())
    assert r['selected']['supplier_id']=='A'; assert e['backend']=='local-dev'; assert e['exit_code']==0

def test_docker_policy_is_hardened_source_contract():
    src=Path(__file__).resolve().parents[1].joinpath('sandbox_runner.py').read_text()
    for token in ['--network','none','--memory','128m','--cpus','0.50','--pids-limit','64','--read-only','--rm']:
        assert repr(token) in src or f"'{token}'" in src or f'"{token}"' in src
