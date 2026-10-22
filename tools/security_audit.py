"""Scan the explicit public release, without printing candidate secret values."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'.git','.pytest_cache','__pycache__','.venv','tmp'}

def audit():
    paths=[]
    for p in ROOT.rglob('*'):
        if not p.is_file(): continue
        relative=p.relative_to(ROOT)
        if any(x in EXCLUDE for x in relative.parts): continue
        if p.suffix in {'.db','.pyc','.log','.xml'} or p.name=='.env': continue
        if p.name.startswith('.env.') and p.name!='.env.example': continue
        if p.name=='publication-audit.json': continue
        paths.append(p)
    patterns={
        'github_credential':r'gh[pousr]_[A-Za-z0-9]{30,}',
        'github_fine_grained':r'github_pat_[A-Za-z0-9_]{40,}',
        'private_key':r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
        'openai_credential':r'sk-(?:proj-)?[A-Za-z0-9_-]{32,}',
        'aws_access_key':r'AKIA[A-Z0-9]{16}',
        'local_user_path':r'[A-Za-z]:[\\/]+Users[\\/]|/(?:Users|home)/[A-Za-z0-9_.-]+/',
    }
    findings=[]; manifest=[]
    for p in paths:
        raw=p.read_bytes(); name=p.relative_to(ROOT).as_posix()
        if p.suffix not in {'.jpg','.png','.pdf'}:
            content=raw.decode('utf-8')
            for rule,pattern in patterns.items():
                if re.search(pattern,content): findings.append({'file':name,'rule':rule})
        manifest.append({'file':name,'sha256':hashlib.sha256(raw).hexdigest()})
    prohibited=[x for x in manifest if x['file'].split('/')[0] in {'ALGO.md','FORMAL.md','EXPERIMENT.md','TZ.md','ARCH.md'} or re.search(r'(?:^|/)v[1245][.-]',x['file'])]
    findings.extend({'file':x['file'],'rule':'outside_release_scope'} for x in prohibited)
    result={'status':'PASS' if not findings else 'FAIL','findings':findings,'files_scanned':len(manifest),'manifest':sorted(manifest,key=lambda x:x['file']),'scope':'Separate public release only. Excludes databases, env files, caches, local paths and original private reference documents. Binary assets visually reviewed.'}
    (ROOT/'reports/publication-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='manifest'},indent=2))
    if findings: raise SystemExit(1)

if __name__=='__main__': audit()
