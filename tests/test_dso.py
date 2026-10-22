from dso import dispatch, DSOState
from engine import matan_solve


def payload(delay=True):
    return {"order_id":"1","product":"X","quantity":10,"max_budget":100,"deadline_days":5,"delay_confirmed":delay,"offers":[
        {"supplier_id":"B","product":"X","available_qty":10,"total_cost":90,"eta_days":3},
        {"supplier_id":"A","product":"X","available_qty":10,"total_cost":90,"eta_days":3},
    ]}


def test_dso_no_trigger_without_delay():
    r=dispatch(payload(False),matan_solve,DSOState(mode="RECEIVED"))
    assert r["status"]=="NO_TRIGGER"
    assert r["dso"]["triggered"] is False


def test_dso_triggers_and_validates_matan():
    r=dispatch(payload(True),matan_solve,DSOState(mode="RECEIVED"))
    assert r["status"]=="PROPOSED"
    assert r["selected"]["supplier_id"]=="A"
    assert r["dso"]["triggered"] is True


def test_matan_exact_oracle():
    req=payload(True)
    r=matan_solve(req)
    feasible=[]
    for o in req["offers"]:
        if o["product"]==req["product"] and o["available_qty"]>=req["quantity"] and o["total_cost"]<=req["max_budget"] and o["eta_days"]<=req["deadline_days"]:
            feasible.append(o)
    oracle=min(feasible,key=lambda o:(o["total_cost"],o["eta_days"],o["supplier_id"]))
    assert r["selected"]==oracle
