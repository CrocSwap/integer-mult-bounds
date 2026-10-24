#!/usr/bin/env python3
"""Independent recomputation of #4510: suffix-weighted logical error bounds for the complete THREE-base word.

Model (#4510): an additive logical defect may be injected into the target field after every scalar, warp, climb and
center event; free warp operators are isometric free-group symbols (an operator and its negation cancel when
adjacent); all other events are exact. A reverse sweep keeps, for every field, its exact response
{(output, reduced warp word): rational coefficient}; at each event the l1 norm of the target field's response is
added to that output's weight for the event's class. Checks, for the original and #4505-rewritten words:
  * worst persistent-output ADD+SCALE weight 1,328 (forward) and 4,879 (backward), unchanged by the rewrite, hence
    11 and 13 extra logical-defect bits (2^11 > 1,328, 2^13 > 4,879);
  * ADD-only backward maximum 4,308 -> 4,300; initial-input amplification factor 2;
  * 33 forward and 90 backward output rows change, with largest increases 2 and 12 (largest decreases 109/4 and 4).
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import defaultdict
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = "research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz"
NEW = "research/native-splice-replay/NATIVE.json"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def response(word):
    # adjoint[role] = {(output_index, warp_word): coeff}; reverse sweep
    roles=[('L',i) for i in range(632)]+[('C',0)]
    idx={r:i for i,r in enumerate(roles)}
    adj={r:{(idx[r],()):F(1)} for r in roles}
    w=defaultdict(lambda: defaultdict(F))   # class -> output -> weight
    def acc(dst,src,q):
        for k,c in src.items():
            v=dst.get(k,0)+q*c
            if v: dst[k]=v
            else: dst.pop(k,None)
    for e in reversed(word):
        t=e[0]
        if t=='scalar':
            op=e[1]; tgt=tuple(op[1]); cls=op[0]
        elif t=='warp': tgt=tuple(e[1]); cls='warp'
        elif t=='climb': tgt=('L',e[2]); cls='rank-%d'%e[5]
        elif t=='center': tgt=('C',e[1]); cls='rank-%d'%e[4]
        else: continue
        for (o,_),c in adj[tgt].items(): w[cls][o]+=abs(c)
        if t=='scalar':
            if op[0]=='add': acc(adj[tuple(op[2])],adj[tgt],F(op[3],op[4]))
            elif op[0]=='scale':
                q=F(op[2],op[3]); adj[tgt]={k:q*c for k,c in adj[tgt].items()}
            elif op[0]=='clear': adj[tgt]={}
            elif op[0]=='copy': acc(adj[tuple(op[2])],adj[tgt],F(1)); adj[tgt]={}
        elif t=='warp':
            s=e[2]; new={}
            for (o,wd),c in adj[tgt].items():
                nw=wd[:-1] if wd and wd[-1]==-s else wd+(s,)
                new[(o,nw)]=new.get((o,nw),0)+c
            adj[tgt]={k:c for k,c in new.items() if c}
    E0=max(sum(abs(c) for r in roles for (o2,_),c in adj[r].items() if o2==o) for o in range(632))
    return w,E0


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    words = {"original": json.loads(gzip.decompress((ROOT / OLD).read_bytes())),
             "rewritten": json.loads((ROOT / NEW).read_bytes())}
    joint, addonly, out = {}, {}, {}
    for name, d in words.items():
        for o in ("forward", "backward"):
            w, E0 = response(d[o])
            joint[name, o] = [w["add"][i] + w["scale"][i] for i in range(632)]
            addonly[name, o] = max(w["add"][i] for i in range(632))
            need(E0 == 2, f"{name} {o}: initial-input factor 2")
    for o, worst, bits in (("forward", 1328, 11), ("backward", 4879, 13)):
        for name in words:
            need(max(joint[name, o]) == worst, f"{name} {o}: worst ADD+SCALE weight {worst}")
        need(2 ** (bits - 1) < worst < 2 ** bits, f"{o}: {bits} extra bits")
        a, b = joint["original", o], joint["rewritten", o]
        ch = [i for i in range(632) if a[i] != b[i]]
        inc = max(b[i] - a[i] for i in ch)
        dec = max(a[i] - b[i] for i in ch)
        out[o] = {"worst_add_scale": worst, "extra_bits": bits, "rows_changed": len(ch), "max_increase": str(inc),
                  "max_decrease": str(dec)}
    need(out["forward"]["rows_changed"] == 33 and out["backward"]["rows_changed"] == 90, "changed rows 33 / 90")
    need(out["forward"]["max_increase"] == "2" and out["backward"]["max_increase"] == "12", "largest increases 2 / 12")
    need(addonly["original", "backward"] == 4308 and addonly["rewritten", "backward"] == 4300, "ADD-only backward 4308 -> 4300")
    print(json.dumps({"status": "PASS_SUFFIX_ERROR_RECOUNT", **out, "add_only_backward": [4308, 4300],
                      "initial_input_factor": 2, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
