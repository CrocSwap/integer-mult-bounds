"""Check the exact full-suffix and independent receipts key by key."""
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEAD = "c81636f5fe4a5db1cb31220b451e400f2eb86af6dc3480235b7cfd34d09a8f40"
lead_bytes = (ROOT/"inputs/R139-LEAD-RESULT.json").read_bytes()
assert sha256(lead_bytes).hexdigest() == LEAD
a = loads(lead_bytes)
b_bytes = (ROOT/"RESULT.json").read_bytes()
b = loads(b_bytes)
assert (a["head"],a["caller"]) == (b["head"],b["caller"])
assert not a["survivors"] and not a["unresolved"] and not b["unvisited"]
assert b["counts"] == {"excluded":47} and a["COPY_clocks"] == b["copy_clocks"] == [33805]
firsts = {r["move_clock"]:r for r in a["rows"]}
assert len(firsts) == len(a["rows"]) == len(b["cases"]) == 47
checks = []
for row in b["cases"]:
    clock = row["move_clock"]
    lead = firsts.pop(clock)
    assert lead["key"] == [row[k] for k in ("role","before","after","rank")]
    assert lead["observable_count"] == len(row["final_public"]) + len(row["copy_guards"])
    assert lead["first"] == ["public"] + row["final_public"][0]
    assert row["reverse_first_public"] == row["final_public"][0]
    assert not row["copy_guards"]
    checks.append([clock,*lead["first"][1:],lead["observable_count"]])
assert not firsts
print(dumps({"agrees":True,"checked":checks,"head":a["head"],"lead_sha256":LEAD,
             "independent_sha256":sha256(b_bytes).hexdigest(),
             "copy_guard_checks":sum(c[0]<33805 for c in checks),"copy_guard_nonzero":0,
             "unresolved":0},indent=2,sort_keys=True))
