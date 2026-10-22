import hashlib, json, mimetypes, os, sqlite3, time
import threading
from functools import wraps
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from engine import matan_solve, violations, Offer, validate_request
from dso import validate_result
from experience import ExperienceStore
from inference import explain
from sandbox_runner import SandboxRunner, SandboxError
from verification import independent_choice

ROOT=Path(__file__).resolve().parent
DB=os.getenv('DISPATCHER_DB',str(ROOT/'dispatcher.db'))
STATE_LOCK=threading.RLock()

def serialized(fn):
    @wraps(fn)
    def wrapped(*args,**kwargs):
        with STATE_LOCK: return fn(*args,**kwargs)
    return wrapped

def init_db(db_path=DB):
    ExperienceStore(db_path)
    with sqlite3.connect(db_path) as c:
        c.execute('CREATE TABLE IF NOT EXISTS decisions(decision_id TEXT PRIMARY KEY, order_id TEXT, request_json TEXT, selected_json TEXT, status TEXT, explanation TEXT, llm_called INTEGER, sandbox_json TEXT, created_at REAL)')
        # Lightweight schema migration for earlier local DB.
        cols={r[1] for r in c.execute('PRAGMA table_info(decisions)').fetchall()}
        if 'sandbox_json' not in cols: c.execute('ALTER TABLE decisions ADD COLUMN sandbox_json TEXT')
        c.execute('CREATE TABLE IF NOT EXISTS orders(order_id TEXT PRIMARY KEY, supplier_id TEXT, total_cost REAL, eta_days INTEGER, status TEXT, updated_at REAL)')
        c.execute('CREATE TABLE IF NOT EXISTS trace(id INTEGER PRIMARY KEY AUTOINCREMENT, decision_id TEXT, event TEXT, payload TEXT, created_at REAL)')

def log(db_path,decision_id,event,payload):
    with sqlite3.connect(db_path) as c: c.execute('INSERT INTO trace(decision_id,event,payload,created_at) VALUES(?,?,?,?)',(decision_id,event,json.dumps(payload,sort_keys=True),time.time()))

def make_id(req,selected):
    raw=json.dumps({'request':req,'selected':selected},sort_keys=True).encode(); return hashlib.sha256(raw).hexdigest()[:32]

def human_plan():
    return [
        'Read the delayed order and supplier offers.',
        'Compare all supplier offers against the required conditions.',
        'Validate the result against quantity, budget and delivery deadline.',
        'Request human approval before changing the order.',
        'Update the order after approval and confirm the saved result.'
    ]

def offer_rows(req,result):
    eligible_ids={o['supplier_id'] for o in result.get('eligible',[])}
    rows=[]
    for raw in req['offers']:
        sid=str(raw['supplier_id']).strip(); reasons=result.get('conflicts',{}).get(sid,[])
        rows.append({**raw,'admissible':sid in eligible_ids,'reasons':reasons or ['all constraints satisfied']})
    rows.sort(key=lambda o:(0 if o['admissible'] else 1,float(o['total_cost']),int(o['eta_days']),str(o['supplier_id'])))
    return rows

@serialized
def analyze_request(req,db_path=DB,sandbox_backend=None):
    init_db(db_path); validate_request(req)
    with sqlite3.connect(db_path) as c:
        c.execute("UPDATE decisions SET status='SUPERSEDED' WHERE order_id=? AND status='PROPOSED' AND request_json<>?",(str(req['order_id']),json.dumps(req)))
    if req['delay_confirmed'] is not True:
        return {'status':'NO_TRIGGER','message':'No confirmed delivery delay. The current order remains unchanged.'}
    runner=SandboxRunner(backend=sandbox_backend)
    result,evidence=runner.run_solver(req)
    validate_result(req,result)
    # Independent host-side oracle confirms the sandbox result.
    oracle=independent_choice(req)
    if result.get('selected')!=oracle or result.get('status')!=('PROPOSED' if oracle else 'CONFLICT'):
        raise ValueError('Decision verification failed')
    if result['status']=='CONFLICT':
        return {
            'status':'CONFLICT','task':f"Replace delayed order {req['order_id']} for {req['quantity']} × {req['product']}",
            'plan':human_plan(),'offers':offer_rows(req,result),'message':'No supplier satisfies all mandatory constraints.',
            'sandbox':evidence,'evidence':{'oracle_match':True,'constraint_violations':0,'decision_applied':False}
        }
    selected=result['selected']; decision_id=make_id(req,selected)
    store=ExperienceStore(db_path); experience=store.applicable(req,result['eligible'])
    use_exp=bool(experience and experience['supplier_id']==selected['supplier_id'])
    explanation,llm_called,inference_source=explain(req,selected,use_exp)
    with sqlite3.connect(db_path) as c:
        c.execute("UPDATE decisions SET status='SUPERSEDED' WHERE order_id=? AND decision_id<>? AND status='PROPOSED'",(str(req['order_id']),decision_id))
        c.execute('INSERT OR IGNORE INTO decisions(decision_id,order_id,request_json,selected_json,status,explanation,llm_called,sandbox_json,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                  (decision_id,str(req['order_id']),json.dumps(req),json.dumps(selected),'PROPOSED',explanation,int(llm_called),json.dumps(evidence),time.time()))
    log(db_path,decision_id,'PROPOSED',{'selected':selected,'experience_used':use_exp,'llm_called':llm_called,'sandbox_run_id':evidence['run_id']})
    return {
        'status':'PROPOSED','decision_id':decision_id,
        'task':f"Replace delayed order {req['order_id']} for {req['quantity']} × {req['product']}",
        'plan':human_plan(),'offers':offer_rows(req,result),'selected':selected,'explanation':explanation,
        'approval_required':True,'experience_used':use_exp,'llm_called':llm_called,'inference_source':inference_source,
        'sandbox':evidence,'evidence':{'oracle_match':True,'selected_constraint_violations':0,'decision_applied':False}
    }

@serialized
def approve_decision(decision_id,db_path=DB):
    init_db(db_path)
    with sqlite3.connect(db_path) as c:
        row=c.execute('SELECT order_id,request_json,selected_json,status,sandbox_json FROM decisions WHERE decision_id=?',(decision_id,)).fetchone()
        if not row: return {'status':'ERROR','error':'decision not found'},404
        order_id,req_json,sel_json,status,sandbox_json=row; req=json.loads(req_json); selected=json.loads(sel_json)
        if status=='SUPERSEDED': return {'status':'ERROR','error':'Order conditions changed. Analyze the current order before approval.'},409
        if status in ('UPDATED','VERIFIED'):
            order=c.execute('SELECT supplier_id,total_cost,eta_days,status FROM orders WHERE order_id=?',(order_id,)).fetchone()
            if not order or tuple(order[:3])!=(selected['supplier_id'],float(selected['total_cost']),int(selected['eta_days'])):
                return {'status':'ERROR','error':'The order has changed since this approval.'},409
            return {'status':'VERIFIED','idempotent':True,'message':'Order was already updated and verified.','order':{'order_id':order_id,'supplier_id':order[0],'total_cost':order[1],'eta_days':order[2],'status':order[3]}},200
        if violations(req,Offer.from_dict(selected)): return {'status':'ERROR','error':'selected offer is no longer admissible'},409
        c.execute('INSERT OR REPLACE INTO orders(order_id,supplier_id,total_cost,eta_days,status,updated_at) VALUES(?,?,?,?,?,?)',(order_id,selected['supplier_id'],selected['total_cost'],selected['eta_days'],'UPDATED',time.time()))
    # A fresh connection verifies the committed durable record.
    with sqlite3.connect(db_path) as c:
        persisted=c.execute('SELECT supplier_id,total_cost,eta_days,status FROM orders WHERE order_id=?',(order_id,)).fetchone()
        expected=(selected['supplier_id'],float(selected['total_cost']),int(selected['eta_days']),'UPDATED')
        actual=(persisted[0],float(persisted[1]),int(persisted[2]),persisted[3]) if persisted else None
        if actual!=expected: return {'status':'ERROR','error':'verification failed after order update'},500
        c.execute("UPDATE decisions SET status='VERIFIED' WHERE decision_id=?",(decision_id,))
    ExperienceStore(db_path).save_success(req,selected)
    log(db_path,decision_id,'VERIFIED',{'order_id':order_id,'selected':selected,'verified':True})
    return {'status':'VERIFIED','idempotent':False,'message':'Replacement approved. The order was updated and independently verified.','order':{'order_id':order_id,**selected,'status':'UPDATED'},'evidence':{'verified':True,'selected_constraint_violations':0,'order_matches_recommendation':True}},200

def trace_for(decision_id,db_path=DB):
    init_db(db_path)
    with sqlite3.connect(db_path) as c: rows=c.execute('SELECT event,payload,created_at FROM trace WHERE decision_id=? ORDER BY id',(decision_id,)).fetchall()
    return [{'event':e,'payload':json.loads(p),'created_at':t} for e,p,t in rows]

class Handler(BaseHTTPRequestHandler):
    def send_json(self,data,status=200):
        raw=json.dumps(data,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def send_file(self,path):
        p=(ROOT/path).resolve()
        if not p.is_relative_to(ROOT.resolve()): self.send_error(404); return
        if str(path).startswith('static/') and not p.is_relative_to((ROOT/'static').resolve()): self.send_error(404); return
        if not p.is_file(): self.send_error(404); return
        raw=p.read_bytes(); self.send_response(200); self.send_header('Content-Type',mimetypes.guess_type(str(p))[0] or 'application/octet-stream'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=='/':
            return self.send_file('templates/index.html')
        if path=='/health': return self.send_json({'status':'ok'})
        if path.startswith('/api/order/'):
            with sqlite3.connect(DB) as c:
                row=c.execute('SELECT supplier_id,total_cost,eta_days,status FROM orders WHERE order_id=?',(path.rsplit('/',1)[-1],)).fetchone()
            return self.send_json({'order':dict(zip(['supplier_id','total_cost','eta_days','status'],row)) if row else None})
        if path.startswith('/static/'): return self.send_file(path.lstrip('/'))
        if path.startswith('/api/trace/'): return self.send_json(trace_for(path.rsplit('/',1)[-1]))
        self.send_error(404)
    def do_POST(self):
        path=urlparse(self.path).path
        origin=self.headers.get('Origin')
        if origin and urlparse(origin).netloc!=self.headers.get('Host'):
            return self.send_json({'error':'Request origin is not allowed.'},403)
        if path=='/api/analyze':
            try:
                n=int(self.headers.get('Content-Length','0'))
                if n<0 or n>131072: return self.send_json({'error':'Order data is too large.'},413)
                data=json.loads(self.rfile.read(n) or b'{}'); return self.send_json(analyze_request(data))
            except (ValueError,KeyError,TypeError,json.JSONDecodeError,SandboxError,RuntimeError): return self.send_json({'status':'ERROR','error':'The request could not be completed. Check the entered order and supplier data.'},400)
        if path.startswith('/api/approve/'):
            data,status=approve_decision(path.rsplit('/',1)[-1]); return self.send_json(data,status)
        self.send_error(404)
    def log_message(self,format,*args): pass

def run():
    if os.getenv('REQUIRE_VULTR_INFERENCE','0')=='1':
        if not os.getenv('VULTR_SERVERLESS_INFERENCE_API_KEY') or not os.getenv('VULTR_MODEL'):
            raise RuntimeError('Production requires Vultr inference credentials and model')
        if os.getenv('SANDBOX_BACKEND')!='docker': raise RuntimeError('Production requires Docker containment')
    init_db(DB); port=int(os.getenv('PORT','8003')); ThreadingHTTPServer((os.getenv('BIND_HOST','127.0.0.1'),port),Handler).serve_forever()
if __name__=='__main__': run()
