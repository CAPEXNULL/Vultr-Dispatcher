"""Safe reproducible containment demonstration using the production runner policy."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import uuid
from sandbox_runner import SandboxRunner, SandboxError

def demonstrate():
    run_id='demo-'+uuid.uuid4().hex[:10]
    name='supply-sbx-'+run_id
    started=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='supply-demo-') as td:
        work=Path(td)
        (work/'input.json').write_text('{}')
        (work/'task.py').write_text('''import json, os, pathlib, resource
root=pathlib.Path('/sys/fs/cgroup')
proof={k:(root/k).read_text().strip() for k in ['memory.max','memory.swap.max','pids.max','cpu.max']}
proof['environment_names']=sorted(os.environ)
proof['secret_present']=any(k.startswith(('VULTR','AWS_','GITHUB','GH_')) or k.endswith(('_TOKEN','_PASSWORD','_SECRET')) for k in os.environ)
proof['cpu_seconds']=resource.getrlimit(resource.RLIMIT_CPU)[0]
pathlib.Path('/work/proof.json').write_text(json.dumps(proof))
while True: pass
''',encoding='utf-8')
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future=pool.submit(SandboxRunner(backend='docker',timeout_s=5)._run_docker,work,run_id)
            policy=None
            for _ in range(40):
                if (work/'proof.json').exists():
                    inspected=subprocess.run(['docker','inspect',name],capture_output=True,text=True,timeout=5)
                    if inspected.returncode==0: policy=json.loads(inspected.stdout)[0]['HostConfig']
                    break
                if future.done(): break
                time.sleep(.1)
            limited=False
            try: future.result()
            except SandboxError: limited=True
        proof=json.loads((work/'proof.json').read_text())
        remaining=subprocess.run(['docker','ps','-aq','--filter',f'name=^{name}$'],capture_output=True,text=True,timeout=5).stdout.strip()
        assert limited and not remaining and policy
        assert policy['NetworkMode']=='none' and policy['ReadonlyRootfs']
        assert policy['Memory']==134217728 and policy['PidsLimit']==64 and policy['NanoCpus']==500000000
        assert proof['memory.max']=='134217728' and proof['pids.max']=='64'
        assert proof['cpu_seconds']==4 and not proof['secret_present']
        req=dict(order_id='CONTAINMENT-RECOVERY',product='X',quantity=1,max_budget=10,deadline_days=1,delay_confirmed=True,offers=[dict(supplier_id='A',product='X',available_qty=1,total_cost=5,eta_days=1)])
        result,evidence=SandboxRunner(backend='docker').run_solver(req)
        assert result['selected']['supplier_id']=='A'
        return dict(status='PASS',limit_enforced=True,container_destroyed=True,host_continues=True,next_task_passed=True,observed=proof,policy_observed=True,duration_seconds=round(time.monotonic()-started,2),recovery=evidence)

if __name__=='__main__':
    result=demonstrate()
    Path('reports').mkdir(exist_ok=True)
    Path('reports/containment.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
