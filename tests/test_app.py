from app import analyze_request, approve_decision

def payload(delay=True):
    return {'order_id':'PO1','product':'X','quantity':10,'max_budget':100,'deadline_days':5,'delay_confirmed':delay,'offers':[{'supplier_id':'A','product':'X','available_qty':10,'total_cost':90,'eta_days':3}]}

def test_e2e_approve_idempotent(tmp_path):
    db=str(tmp_path/'t.db'); d=analyze_request(payload(),db,sandbox_backend='local')
    assert d['status']=='PROPOSED' and d['evidence']['oracle_match'] is True
    b,status=approve_decision(d['decision_id'],db); assert status==200 and b['status']=='VERIFIED'
    again,status=approve_decision(d['decision_id'],db); assert status==200 and again['idempotent'] is True

def test_no_delay_skips_sandbox(tmp_path):
    d=analyze_request(payload(False),str(tmp_path/'t.db'),sandbox_backend='local')
    assert d['status']=='NO_TRIGGER' and 'sandbox' not in d

def test_invalid_input(tmp_path):
    try: analyze_request({},str(tmp_path/'t.db'),sandbox_backend='local')
    except ValueError: return
    assert False

def test_successful_experience_reused_without_llm(tmp_path):
    db=str(tmp_path/'t.db'); first=analyze_request(payload(),db,sandbox_backend='local'); approve_decision(first['decision_id'],db)
    second=analyze_request(payload(),db,sandbox_backend='local')
    assert second['experience_used'] is True and second['llm_called'] is False

def test_sandbox_evidence(tmp_path):
    d=analyze_request(payload(),str(tmp_path/'t.db'),sandbox_backend='local')
    assert d['sandbox']['run_id'] and len(d['sandbox']['output_sha256'])==64
