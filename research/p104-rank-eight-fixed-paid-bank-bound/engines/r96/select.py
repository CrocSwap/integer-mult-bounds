"""Freeze the first four suffix drops in the original rank-eight bank order."""
from hashlib import sha256
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
raw = (root/"lead/SUFFIX.json").read_bytes()
assert sha256(raw).hexdigest()=="77d78eb692bf6d3f0433730b48dbf8a0178c3288eeca961f94b2aaa6683eb59a"
s = json.loads(raw)
assert not s["unvisited"] and s["counts"]=={"excluded":1,"rank drop":6}
drops=[r for r in s["rows"] if r["disposition"]=="rank drop"]
print(json.dumps({"selected":drops[:4],"unselected":[r["key"] for r in drops[4:]]+s["unselected"],
                  "case_cap":4,"seconds_cap":35},indent=2,sort_keys=True))
