"""Identify unvisited rank-eight banks and the two unresolved dual drops."""
from hashlib import sha256
import json
from pathlib import Path
import sys

PINS = {
    "lead/GEOMETRY.json": "c6f9f018df8b58fcdf4f44356bd59bcac6d411b7845104ff4ad372ed4a95cfbd",
    "lead/RESULT.json": "45b6c8992dcff04b7252dfec809fc64812b86f094531ed3964ff967408057ed2",
    "lead/SUFFIX.json": "77d78eb692bf6d3f0433730b48dbf8a0178c3288eeca961f94b2aaa6683eb59a",
    "lead/EXACT.json": "362a879401158678c8a30ea0dbd4f919a9a0e907db2d2247ce96ac8724f68b14",
}

root = Path(sys.argv[1])
receipts = {}
for name, digest in PINS.items():
    raw = (root/name).read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f"changed receipt: {name}")
    receipts[Path(name).stem] = json.loads(raw)
g, p, s, e = (receipts[k] for k in ("GEOMETRY","RESULT","SUFFIX","EXACT"))
assert g["eligible_bank_count"] == 326 and g["status"] == "EXHAUSTED"
assert p["counts"] == {"excluded":9,"rank drop":7} and not p["unvisited"]
assert s["counts"] == {"excluded":1,"rank drop":6} and not s["unvisited"]
assert e["counts"] == {"no unit pairing":4} and not e["selected_unresolved"]
exact = {tuple(r["key"]) for r in e["results"]}
unresolved = [r["key"] for r in s["rows"] if r["disposition"] == "rank drop" and tuple(r["key"]) not in exact]
unvisited = g["unvisited_keys"]
assert len(unvisited) == 310 and len(unresolved) == 2
assert e["unselected"] == unresolved + unvisited
print(json.dumps({"head":g["head"],"input_sha256":PINS,"excluded":14,
    "unresolved":312,"unvisited_prefix":unvisited,"dual_drops_requiring_rational":unresolved,
    "next_modular_cases":310,"next_modular_runner_seconds":25,
    "next_exact_cases":4,"next_exact_runner_seconds":35},indent=2,sort_keys=True))
