import sqlite3, time

SCHEMA="""
CREATE TABLE IF NOT EXISTS experiences(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 product TEXT NOT NULL,
 supplier_id TEXT NOT NULL,
 max_quantity INTEGER NOT NULL,
 min_budget REAL NOT NULL,
 min_deadline_days INTEGER NOT NULL,
 success INTEGER NOT NULL,
 created_at REAL NOT NULL
);
"""

class ExperienceStore:
    def __init__(self, path="dispatcher.db"):
        self.path=path
        with sqlite3.connect(self.path) as c: c.executescript(SCHEMA)

    def save_success(self, req, selected):
        with sqlite3.connect(self.path) as c:
            c.execute("INSERT INTO experiences(product,supplier_id,max_quantity,min_budget,min_deadline_days,success,created_at) VALUES(?,?,?,?,?,?,?)",
                      (req["product"], selected["supplier_id"], int(req["quantity"]), float(selected["total_cost"]), int(selected["eta_days"]), 1, time.time()))

    def applicable(self, req, eligible):
        ids={o["supplier_id"] for o in eligible}
        with sqlite3.connect(self.path) as c:
            rows=c.execute("SELECT product,supplier_id,max_quantity,min_budget,min_deadline_days FROM experiences WHERE success=1 AND product=? ORDER BY id DESC LIMIT 20",(req["product"],)).fetchall()
        for product,supplier_id,max_q,min_b,min_d in rows:
            if supplier_id in ids and int(req["quantity"]) <= max_q and float(req["max_budget"]) >= min_b and int(req["deadline_days"]) >= min_d:
                return {"product":product,"supplier_id":supplier_id,"max_quantity":max_q,"min_budget":min_b,"min_deadline_days":min_d}
        return None
