from dataclasses import dataclass, asdict
from typing import Any
import math

def integer(value):
    if isinstance(value, bool) or not math.isfinite(float(value)) or float(value) != int(value):
        raise ValueError('Expected an integer')
    return int(value)

def amount(value):
    if isinstance(value, bool) or not math.isfinite(float(value)):
        raise ValueError('Expected a finite amount')
    return float(value)

@dataclass(frozen=True)
class Offer:
    supplier_id: str
    product: str
    available_qty: int
    total_cost: float
    eta_days: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Offer":
        offer = cls(
            supplier_id=str(d["supplier_id"]).strip(),
            product=str(d["product"]).strip(),
            available_qty=integer(d["available_qty"]),
            total_cost=amount(d["total_cost"]),
            eta_days=integer(d["eta_days"]),
        )
        if not offer.supplier_id or not offer.product:
            raise ValueError("supplier_id and product must be non-empty")
        if offer.available_qty < 0 or offer.total_cost < 0 or offer.eta_days < 0:
            raise ValueError("offer quantity, cost and eta must be non-negative")
        return offer

def validate_request(data: dict[str, Any]) -> None:
    if not isinstance(data, dict): raise ValueError('Expected an order')
    required = ["order_id", "product", "quantity", "max_budget", "deadline_days", "delay_confirmed", "offers"]
    missing = [k for k in required if k not in data]
    if missing:
        raise ValueError("Missing fields: " + ", ".join(missing))
    if not str(data["order_id"]).strip() or not str(data["product"]).strip():
        raise ValueError("order_id and product must be non-empty")
    if not isinstance(data["delay_confirmed"], bool):
        raise ValueError("delay_confirmed must be boolean")
    if integer(data["quantity"]) <= 0 or amount(data["max_budget"]) <= 0 or integer(data["deadline_days"]) < 0:
        raise ValueError("quantity and max_budget must be positive; deadline_days must be non-negative")
    if not isinstance(data["offers"], list):
        raise ValueError("offers must be a list")
    if len(data['offers']) > 100: raise ValueError('At most 100 offers')
    offers=[Offer.from_dict(o) for o in data['offers']]
    if len({o.supplier_id for o in offers}) != len(offers):
        raise ValueError('Supplier IDs must be unique')

def violations(req: dict[str, Any], offer: Offer) -> list[str]:
    out=[]
    if offer.product != str(req["product"]).strip(): out.append("product")
    if offer.available_qty < int(req["quantity"]): out.append("quantity")
    if offer.total_cost > float(req["max_budget"]): out.append("budget")
    if offer.eta_days > int(req["deadline_days"]): out.append("deadline")
    return out

def matan_solve(req: dict[str, Any]) -> dict[str, Any]:
    """Exact finite constrained optimization with deterministic lexicographic objective."""
    validate_request(req)
    offers=[Offer.from_dict(x) for x in req["offers"]]
    eligible=[]
    conflicts={}
    for o in offers:
        v=violations(req,o)
        if v:
            conflicts[o.supplier_id]=v
        else:
            eligible.append(o)
    eligible.sort(key=lambda o:(o.total_cost,o.eta_days,o.supplier_id))
    selected=eligible[0] if eligible else None
    return {
        "status":"PROPOSED" if selected else "CONFLICT",
        "eligible":[asdict(o) for o in eligible],
        "selected":asdict(selected) if selected else None,
        "conflicts":conflicts,
        "objective": {
            "type": "lexicographic",
            "priority": ["total_cost", "eta_days", "supplier_id"]
        }
    }

# Backward-compatible direct mathematical entry point used by unit tests.
def analyze(req: dict[str, Any]) -> dict[str, Any]:
    validate_request(req)
    if req["delay_confirmed"] is not True:
        return {"status":"NO_TRIGGER", "eligible":[], "selected":None, "conflicts":{}}
    return matan_solve(req)
