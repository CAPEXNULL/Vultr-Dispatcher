"""Verify the standalone runtime from a fresh export, with no copied database."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def reproduce():
    with tempfile.TemporaryDirectory(prefix='supply-clean-export-') as td:
        export=Path(td)/'release'; export.mkdir()
        assert export.resolve().is_relative_to(Path(td).resolve())
        excluded={'.git','__pycache__','.pytest_cache','tmp','.venv'}
        copied=0
        for path in ROOT.rglob('*'):
            relative=path.relative_to(ROOT)
            if not path.is_file() or any(part in excluded for part in relative.parts): continue
            if path.suffix in {'.db','.pyc','.log','.xml'} or path.name=='.env': continue
            dest=export/relative; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(path,dest); copied+=1
        env={k:v for k,v in os.environ.items() if not any(t in k.upper() for t in ['VULTR','TOKEN','SECRET','PASSWORD','PYTHONPATH'])}
        env.update(REQUIRE_VULTR_INFERENCE='0',SANDBOX_BACKEND='docker')
        code="""import sys; sys.path.insert(0,'.')
from app import analyze_request,approve_decision
req=dict(order_id='REPRO',product='X',quantity=2,max_budget=100,deadline_days=4,delay_confirmed=True,offers=[dict(supplier_id='B',product='X',available_qty=2,total_cost=90,eta_days=3),dict(supplier_id='A',product='X',available_qty=2,total_cost=80,eta_days=4)])
result=analyze_request(req,'clean.db','docker')
assert result['selected']['supplier_id']=='A'
assert approve_decision(result['decision_id'],'clean.db')[1]==200
"""
        subprocess.run([sys.executable,'-I','-c',code],cwd=export,env=env,check=True,timeout=45)
        reread="import sqlite3; c=sqlite3.connect('clean.db'); assert c.execute('SELECT supplier_id,total_cost,eta_days FROM orders').fetchone()==('A',80,4)"
        subprocess.run([sys.executable,'-I','-c',reread],cwd=export,env=env,check=True,timeout=10)
        image=subprocess.run(['docker','image','inspect','python:3.13-slim','--format','{{.Id}}'],capture_output=True,text=True,check=True).stdout.strip()
        result={'status':'PASS','fresh_export':True,'files_copied':copied,'no_prior_database':True,'isolated_python':True,'real_docker_workflow':True,'new_process_readback':True,'python':sys.version.split()[0],'sandbox_image_id':image}
        (ROOT/'reports/reproducibility.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))

if __name__=='__main__': reproduce()
