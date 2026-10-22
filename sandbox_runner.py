import hashlib, json, os, shutil, subprocess, sys, tempfile, time, uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parent

class SandboxError(RuntimeError): pass

class SandboxRunner:
    def __init__(self, backend=None, timeout_s=8):
        self.backend=(backend or os.getenv('SANDBOX_BACKEND') or ('docker' if shutil.which('docker') else 'local')).lower()
        self.timeout_s=timeout_s

    def run_solver(self, req):
        run_id=uuid.uuid4().hex[:12]
        started=time.perf_counter()
        with tempfile.TemporaryDirectory(prefix='supply-sbx-') as td:
            work=Path(td)
            input_path=work/'input.json'; output_path=work/'output.json'; task_path=work/'task.py'
            input_path.write_text(json.dumps(req,sort_keys=True),encoding='utf-8')
            task_path.write_bytes((ROOT/'sandbox_task.py').read_bytes())
            if self.backend=='docker':
                evidence=self._run_docker(work,run_id)
            elif self.backend=='local':
                evidence=self._run_local(work,run_id)
            else:
                raise SandboxError(f'Unsupported sandbox backend: {self.backend}')
            if not output_path.exists(): raise SandboxError('sandbox produced no output artifact')
            result=json.loads(output_path.read_text(encoding='utf-8'))
            out_hash=hashlib.sha256(output_path.read_bytes()).hexdigest()
            evidence.update({'duration_ms':round((time.perf_counter()-started)*1000,2),'output_sha256':out_hash})
            return result,evidence

    def _run_docker(self,work,run_id):
        image=os.getenv('SANDBOX_IMAGE','python:3.13-slim')
        name=f'supply-sbx-{run_id}'
        cmd=[
            'docker','run','--name',name,'--rm','--network','none','--memory','128m','--memory-swap','128m','--cpus','0.50','--pids-limit','64',
            '--cap-drop','ALL','--security-opt','no-new-privileges','--ulimit','cpu=4:4',
            '--read-only','--tmpfs','/tmp:rw,noexec,nosuid,size=32m','-v',f'{work}:/work:rw',
            '-w','/work',image,'python','/work/task.py','/work/input.json','/work/output.json'
        ]
        try:
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=self.timeout_s)
        except subprocess.TimeoutExpired as exc:
            raise SandboxError('Execution time limit reached') from exc
        finally:
            # Killing the Docker CLI alone does not kill a running container.
            subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=10)
        if p.returncode!=0: raise SandboxError((p.stderr or p.stdout or 'sandbox failed')[-1000:])
        return {'run_id':run_id,'backend':'docker','contained':True,'network':'disabled','memory_limit':'128 MiB','cpu_limit':'0.50 CPU','pids_limit':64,'lifecycle':'destroyed after task','exit_code':p.returncode}

    def _run_local(self,work,run_id):
        # Development fallback only. It intentionally makes no containment claim.
        clean_env={k:v for k,v in os.environ.items() if k.upper() in {'SYSTEMROOT','WINDIR','PATH','TEMP','TMP'}}
        p=subprocess.run([sys.executable,'-I',str(work/'task.py'),str(work/'input.json'),str(work/'output.json')],env=clean_env,cwd=work,capture_output=True,timeout=self.timeout_s)
        if p.returncode: raise SandboxError('Development calculation failed')
        return {'run_id':run_id,'backend':'local-dev','contained':False,'network':'unrestricted development subprocess','memory_limit':'development mode','cpu_limit':'development mode','pids_limit':None,'lifecycle':'temporary workdir destroyed after task','exit_code':0}
