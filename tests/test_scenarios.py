"""299 fresh databases and events, checked by a test-only enumerating oracle."""
import copy
import random
import sqlite3
import pytest
from app import analyze_request, approve_decision, trace_for

KINDS=['valid','budget','quantity','deadline','product','none','tie','approval','event','reuse','reject_reuse','no_delay','boundary']

def scenario(index):
    rng=random.Random(73000+index)
    q=rng.randint(1,500); budget=rng.randint(20,2000); deadline=rng.randint(1,30)
    req=dict(order_id=f'PO-{index}',product=f'ITEM-{index%7}',quantity=q,max_budget=budget,deadline_days=deadline,delay_confirmed=True)
    req['offers']=[dict(supplier_id=f'S-{j}',product=req['product'],available_qty=q+rng.randint(0,50),total_cost=budget-rng.randint(0,budget//2),eta_days=rng.randint(0,deadline)) for j in range(rng.randint(2,7))]
    kind=KINDS[index%len(KINDS)]
    if kind in ['budget','quantity','deadline','product']:
        field,value={'budget':('total_cost',budget+1),'quantity':('available_qty',q-1),'deadline':('eta_days',deadline+1),'product':('product','WRONG')}[kind]
        req['offers'][0][field]=value
    if kind=='none':
        for j,o in enumerate(req['offers']):
            field,value=[('total_cost',budget+1),('available_qty',q-1),('eta_days',deadline+1),('product','WRONG')][j%4]
            o[field]=value
    if kind=='tie':
        for o in req['offers']: o.update(total_cost=budget,eta_days=deadline)
        req['offers'].reverse()
    if kind=='no_delay': req['delay_confirmed']=False
    if kind=='boundary':
        for o in req['offers']: o.update(total_cost=budget,eta_days=deadline,available_qty=q)
    return req,kind

def test_oracle(req):
    if not req['delay_confirmed']: return None
    candidates=[o for o in req['offers'] if o['product']==req['product'] and o['available_qty']>=req['quantity'] and o['total_cost']<=req['max_budget'] and o['eta_days']<=req['deadline_days']]
    winners=[o for o in candidates if all((o['total_cost'],o['eta_days'],o['supplier_id']) <= (p['total_cost'],p['eta_days'],p['supplier_id']) for p in candidates)]
    return winners[0] if winners else None
test_oracle.__test__=False

@pytest.mark.parametrize('index',range(299),ids=lambda i:f'{i:03d}-{KINDS[i%len(KINDS)]}')
def test_independent_workflow(index,tmp_path):
    req,kind=scenario(index); db=str(tmp_path/'case.db'); expected=test_oracle(req)
    result=analyze_request(req,db,sandbox_backend='local')
    assert result.get('selected')==expected
    assert result['status']==('NO_TRIGGER' if not req['delay_confirmed'] else 'PROPOSED' if expected else 'CONFLICT')
    with sqlite3.connect(db) as c: assert c.execute('SELECT count(*) FROM orders').fetchone()[0]==0
    if not expected: return
    decision=result['decision_id']
    applied,status=approve_decision(decision,db)
    assert status==200 and applied['status']=='VERIFIED'
    with sqlite3.connect(db) as c:
        assert c.execute('SELECT supplier_id,total_cost,eta_days FROM orders').fetchone()==(expected['supplier_id'],expected['total_cost'],expected['eta_days'])
    repeated,status=approve_decision(decision,db)
    assert status==200 and repeated['idempotent']
    assert sum(t['event']=='VERIFIED' for t in trace_for(decision,db))==1
    again=analyze_request(copy.deepcopy(req),db,sandbox_backend='local')
    assert again['decision_id']==decision and again['experience_used']
    assert approve_decision(decision,db)[0]['idempotent']
    with sqlite3.connect(db) as c: assert c.execute('SELECT count(*) FROM experiences').fetchone()[0]==1
    if kind in ['reuse','reject_reuse']:
        changed=copy.deepcopy(req); changed['order_id']+='-next'
        if kind=='reject_reuse':
            changed['offers'].append(dict(expected,supplier_id='CHEAPER',total_cost=max(0,expected['total_cost']-1)))
        next_result=analyze_request(changed,db,sandbox_backend='local')
        assert next_result['selected']==test_oracle(changed)
        assert next_result['experience_used']==(kind=='reuse')
