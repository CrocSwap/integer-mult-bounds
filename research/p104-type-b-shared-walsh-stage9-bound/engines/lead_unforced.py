"""Check whether the forced optimality certificate also proves the global bound."""
from collections import Counter
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
spec = run_path(str(ROOT/"replay.py"))
w, o = spec["WALSH"], spec["ORIGINAL"]
receipt = loads((ROOT/"FORCED-RESULT.json").read_bytes())
caller = (ROOT/"inputs"/"CALLER.json").read_bytes()
assert sha256(caller).hexdigest() == spec["PIN"]
tape = loads(caller)["events"]
roles = spec["ROLES"]
edges,rewards,anchors,_ = spec["contact_graph"](tape,range(roles,2*roles))
cap = Counter()
for a,b in edges:
    if a!=b:
        cap[a,b] += 1
        cap[b,a] += 1
for v in rewards:
    cap[w,v] = 1
for v in anchors:
    cap[v,o] += len(edges)+len(rewards)+1
paths = receipt["flow_paths"]
assert len(paths)==17 and all(n==1 and p[0]==w and p[-1]==o and len(set(p))==len(p) for n,p in paths)
forced = receipt["forced"]
selected = None
for i, (_,p) in enumerate(paths):
    if p[1] != forced:
        continue
    sent = Counter((a,b) for j,(_,p) in enumerate(paths) if i!=j for a,b in zip(p,p[1:]))
    if all(value - sent[b,a] <= cap[a,b] for (a,b),value in sent.items()):
        selected = i
        break
assert selected is not None
assert {b for (a,b),n in sent.items() if a==w and n}==set(rewards)
print(dumps({"forced_optimum_reused": True,"additional_solves":0,
             "discarded_forced_path":selected,"feasible_unforced_flow":len(paths)-1,
             "all_original_cut":len(rewards),"unforced_upper_h8_units_per_port":0,
             "proof":"capacity and flow conservation from pinned contacts and paths"},
            indent=2,sort_keys=True))
