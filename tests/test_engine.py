from engine import analyze

def req():
    return {"order_id":"1","product":"X","quantity":10,"max_budget":100,"deadline_days":5,"delay_confirmed":True,"offers":[
        {"supplier_id":"B","product":"X","available_qty":10,"total_cost":90,"eta_days":3},
        {"supplier_id":"A","product":"X","available_qty":10,"total_cost":90,"eta_days":3},
        {"supplier_id":"C","product":"X","available_qty":9,"total_cost":80,"eta_days":2}]}

def test_deterministic_choice():
    r=analyze(req()); assert r["status"]=="PROPOSED"; assert r["selected"]["supplier_id"]=="A"

def test_conflict():
    x=req(); x["max_budget"]=10; r=analyze(x); assert r["status"]=="CONFLICT"; assert r["selected"] is None

def test_no_delay_no_trigger():
    x=req(); x["delay_confirmed"]=False; assert analyze(x)["status"]=="NO_TRIGGER"

def test_conflict_reports_constraint():
    x=req()
    x["max_budget"]=10
    r=analyze(x)
    assert "budget" in r["conflicts"]["A"]
