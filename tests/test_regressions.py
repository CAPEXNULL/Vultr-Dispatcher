import copy
import sqlite3
import pytest
from app import analyze_request, approve_decision
from engine import validate_request
from test_app import payload

@pytest.mark.parametrize('field,value',[('quantity',1.5),('max_budget',float('nan')),('max_budget',float('inf')),('deadline_days',True)])
def test_bad_numbers(field,value):
    req=payload(); req[field]=value
    with pytest.raises(ValueError): validate_request(req)

def test_duplicate_suppliers():
    req=payload(); req['offers']*=2
    with pytest.raises(ValueError): validate_request(req)

def test_stale_proposal_cannot_apply(tmp_path):
    db=str(tmp_path/'t.db'); req=payload(); first=analyze_request(req,db,'local')
    changed=copy.deepcopy(req); changed['max_budget']=1
    assert analyze_request(changed,db,'local')['status']=='CONFLICT'
    assert approve_decision(first['decision_id'],db)[1]==409
    with sqlite3.connect(db) as c: assert c.execute('SELECT count(*) FROM orders').fetchone()[0]==0

def test_request_fingerprint_includes_constraints(tmp_path):
    db=str(tmp_path/'t.db'); req=payload(); first=analyze_request(req,db,'local')
    req['max_budget']=200; second=analyze_request(req,db,'local')
    assert first['decision_id']!=second['decision_id']
    assert approve_decision(first['decision_id'],db)[1]==409

@pytest.mark.parametrize('change',['product','quantity','budget','deadline','supplier'])
def test_experience_never_transfers_outside_its_envelope(tmp_path,change):
    db=str(tmp_path/'t.db'); req=payload(); first=analyze_request(req,db,'local')
    approve_decision(first['decision_id'],db)
    req['order_id']='NEXT'
    if change=='product': req['product']='Y'; req['offers'][0]['product']='Y'
    if change=='quantity': req['quantity']=11; req['offers'][0]['available_qty']=11
    if change=='budget': req['max_budget']=80; req['offers'][0]['total_cost']=70
    if change=='deadline': req['deadline_days']=2; req['offers'][0]['eta_days']=1
    if change=='supplier': req['offers'][0]['supplier_id']='OTHER'
    result=analyze_request(req,db,'local')
    assert result['status']=='PROPOSED' and not result['experience_used']
