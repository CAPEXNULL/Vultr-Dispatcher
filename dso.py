import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any, Callable

@dataclass(frozen=True)
class DSOState:
    mode: str
    request_fingerprint: str | None = None
    decision_id: str | None = None
    sequence: int = 0


def fingerprint_request(req: dict[str, Any]) -> str:
    canonical = json.dumps(req, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def observe(req: dict[str, Any], state: DSOState | None = None) -> dict[str, Any]:
    return {
        "delay_confirmed": req.get("delay_confirmed") is True,
        "fingerprint": fingerprint_request(req),
        "state": asdict(state or DSOState(mode="RECEIVED")),
    }


def interpret(observation: dict[str, Any]) -> str:
    if not observation["delay_confirmed"]:
        return "IDLE"
    previous = observation["state"].get("request_fingerprint")
    if previous == observation["fingerprint"] and observation["state"].get("mode") in {"PROPOSED", "CONFLICT"}:
        return "UNCHANGED"
    return "REPLAN"


def trigger(mode: str) -> bool:
    return mode == "REPLAN"


def dispatch(req: dict[str, Any], compute: Callable[[dict[str, Any]], dict[str, Any]], state: DSOState | None = None) -> dict[str, Any]:
    obs = observe(req, state)
    mode = interpret(obs)
    if mode == "IDLE":
        return {
            "status": "NO_TRIGGER",
            "eligible": [],
            "selected": None,
            "conflicts": {},
            "dso": {"mode": mode, "triggered": False, "fingerprint": obs["fingerprint"]},
        }
    if not trigger(mode):
        return {
            "status": "UNCHANGED",
            "eligible": [],
            "selected": None,
            "conflicts": {},
            "dso": {"mode": mode, "triggered": False, "fingerprint": obs["fingerprint"]},
        }

    result = compute(req)
    validate_result(req, result)
    result["dso"] = {
        "mode": "PROPOSED" if result["status"] == "PROPOSED" else "CONFLICT",
        "triggered": True,
        "fingerprint": obs["fingerprint"],
    }
    return result


def validate_result(req: dict[str, Any], result: dict[str, Any]) -> None:
    status = result.get("status")
    if status not in {"PROPOSED", "CONFLICT", "NO_TRIGGER"}:
        raise ValueError("DSO validation failed: invalid status")
    if status == "PROPOSED":
        selected = result.get("selected")
        eligible = result.get("eligible") or []
        if selected is None or selected not in eligible:
            raise ValueError("DSO validation failed: selected offer is not eligible")
        if selected["product"] != str(req["product"]).strip():
            raise ValueError("DSO validation failed: product invariant")
        if int(selected["available_qty"]) < int(req["quantity"]):
            raise ValueError("DSO validation failed: quantity invariant")
        if float(selected["total_cost"]) > float(req["max_budget"]):
            raise ValueError("DSO validation failed: budget invariant")
        if int(selected["eta_days"]) > int(req["deadline_days"]):
            raise ValueError("DSO validation failed: deadline invariant")
    if status == "CONFLICT" and result.get("selected") is not None:
        raise ValueError("DSO validation failed: conflict cannot contain selected offer")
