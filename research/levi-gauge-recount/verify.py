#!/usr/bin/env python3
"""Independent recount of #4518: Levi-adaptive gauges in the complete THREE-base native word.

Inputs: the pinned original word, #4505's word on main, and #4518's NATIVE.json vendored as NATIVE-4518.json (sha256
pinned to #4518 head 9f0d81c8). Separately written code checks, in both orientations:
  * every non-scalar event is unchanged; all changes lie in one scalar segment whose exact linear effect on every
    touched field equals the original's;
  * the scalar allowance (re-implemented tariff) is 158,120 -> 158,020 (#4505) -> 157,970 forward and
    158,168 -> 158,068 -> 158,018 backward: 50 below #4505 and 150 below the original per orientation;
  * #4510's logical defect model (exact reverse free-word responses): worst ADD+SCALE weight 1,328 forward and
    4,871 backward (down from 4,879), initial-input factor 2;
  * #4518's interval optimum C + min_(L<=0<=H) [4(H-L) + 2 sum dist(s_i,[L,H])] equals an exhaustive Dijkstra search
    over gauge walks (unit SCALE steps cost 2) and add orders (ADD at gauge g costs 2|s_i - g| above the odd part), on
    400 random valuation multisets of size <= 6.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import defaultdict
from fractions import Fraction as F
from fractions import Fraction as Q
import gzip
import hashlib
import heapq
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = "research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz"
MID = "research/native-splice-replay/NATIVE.json"
NEW_SHA = "d705f0ea8200e527f94dc6311e1303de497a843cc6bf407321b78cbb8a0874d7"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def allowance(op):
    if op[0] in ("clear", "copy"):
        return 2
    q = Q(op[3], op[4]) if op[0] == "add" else Q(op[2], op[3])
    n, d = abs(q.numerator), q.denominator
    need(n and d & (d - 1) == 0, "nonzero dyadic scalar")
    if op[0] == "scale":
        need(n & (n - 1) == 0, "dyadic unit scale")
        return 2 * (abs(n.bit_length() - d.bit_length()) + (q < 0))
    need(op[0] == "add", "known scalar op")
    return 2 * (3 + n.bit_length() - 1 + bin(n).count("1") + d.bit_length() - 1)


def segments(word):
    out = [[]]
    for e in word:
        if e[0] == "scalar":
            out[-1].append(e)
        else:
            out.append([])
    return out


def linear_effect(seg):
    st = {}
    get = lambda f: st.setdefault(f, {f: Q(1)})
    for e in seg:
        op = e[1]
        if op[0] == "add":
            dst, src, q = tuple(op[1]), tuple(op[2]), Q(op[3], op[4])
            v = dict(get(dst))
            for k, c in get(src).items():
                v[k] = v.get(k, 0) + q * c
            st[dst] = {k: c for k, c in v.items() if c}
        elif op[0] == "scale":
            f, q = tuple(op[1]), Q(op[2], op[3])
            st[f] = {k: q * c for k, c in get(f).items()}
        elif op[0] == "clear":
            st[tuple(op[1])] = {}
        elif op[0] == "copy":
            st[tuple(op[1])] = dict(get(tuple(op[2])))
        else:
            raise AssertionError(f"unknown scalar op {op[0]}")
    return st


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




def formula(s):
    lo, hi = min(min(s), 0), max(max(s), 0)
    return min(4 * (H - L) + 2 * sum(max(L - x, 0) + max(x - H, 0) for x in s)
               for L in range(lo, 1) for H in range(0, hi + 1))


def brute(s):
    n, lo, hi = len(s), min(min(s), 0) - 2, max(max(s), 0) + 2
    dist, pq = {(0, 0): 0}, [(0, 0, 0)]
    while pq:
        d, g, mask = heapq.heappop(pq)
        if d > dist.get((g, mask), 1 << 60):
            continue
        if mask == (1 << n) - 1 and g == 0:
            return d
        moves = [(d + 2, g + dg, mask) for dg in (-1, 1) if lo <= g + dg <= hi]
        moves += [(d + 2 * abs(s[i] - g), g, mask | 1 << i) for i in range(n) if not mask >> i & 1]
        for nd, ng, nm in moves:
            if nd < dist.get((ng, nm), 1 << 60):
                dist[(ng, nm)] = nd
                heapq.heappush(pq, (nd, ng, nm))


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    raw = (HERE / "NATIVE-4518.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == NEW_SHA, "#4518 NATIVE.json bytes")
    old = json.loads(gzip.decompress((ROOT / OLD).read_bytes()))
    mid = json.loads((ROOT / MID).read_bytes())
    new = json.loads(raw)
    expect = {"forward": (158120, 158020, 157970, 1328), "backward": (158168, 158068, 158018, 4871)}
    out = {}
    for o in ("forward", "backward"):
        need([e for e in old[o] if e[0] != "scalar"] == [e for e in new[o] if e[0] != "scalar"], f"{o}: non-scalar events")
        A, B = segments(old[o]), segments(new[o])
        ch = [i for i in range(len(A)) if A[i] != B[i]]
        need(len(ch) == 1, f"{o}: one changed segment")
        ea, eb = linear_effect(A[ch[0]]), linear_effect(B[ch[0]])
        for f in set(ea) | set(eb):
            need(ea.get(f, {f: Q(1)}) == eb.get(f, {f: Q(1)}), f"{o}: field {f} same linear effect")
        cost = tuple(sum(allowance(e[1]) for e in w[o] if e[0] == "scalar") for w in (old, mid, new))
        need(cost == expect[o][:3], f"{o}: allowance {cost}")
        w, E0 = response(new[o])
        worst = max(w["add"][i] + w["scale"][i] for i in range(632))
        need(worst == expect[o][3] and E0 == 2, f"{o}: suffix worst {worst}")
        out[o] = {"allowance_orig_4505_4518": list(cost), "suffix_worst_add_scale": str(worst),
                  "segment_scalars": [len(A[ch[0]]), len(B[ch[0]])]}
    rng = random.Random(4518)
    for _ in range(400):
        s = [rng.randint(-5, 5) for _ in range(rng.randint(1, 6))]
        need(formula(s) == brute(s), f"interval optimum {s}")
    print(json.dumps({"status": "PASS_LEVI_GAUGE_RECOUNT", **out, "interval_formula_cases": 400,
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
