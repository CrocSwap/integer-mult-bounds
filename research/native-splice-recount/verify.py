#!/usr/bin/env python3
"""Independent recount of #4505: borrowed rank-one adapters installed in the complete THREE-base word.

Separately written code reads the pinned original native word and #4505's rewritten NATIVE.json and checks, in
both orientations:
  * every non-scalar event (climb, center, warp, adapter, residual_adapter, phase) is identical and in the same
    order, so paid profile, transports and warps are unchanged;
  * all changes lie inside one maximal scalar segment, and that segment computes the identical exact linear map
    on every field it touches (fields as rational combinations of their entry values; ADD/SCALE/CLEAR/COPY);
  * the scalar allowance, re-implemented from the stated tariff (CLEAR/COPY 2; dyadic unit SCALE
    2(|bitlen n - bitlen d| + [q<0]); ADD 2(3 + bitlen n - 1 + popcount n + bitlen d - 1)), is 158,120 -> 158,020
    forward and 158,168 -> 158,068 backward: a saving of exactly 100 each.
This is a logical (free-word) check; physical frames and phases are #4505's own replay.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = "research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz"
NEW = "research/native-splice-replay/NATIVE.json"
EXPECT = {"forward": (158120, 158020), "backward": (158168, 158068)}


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


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    old = json.loads(gzip.decompress((ROOT / OLD).read_bytes()))
    new = json.loads((ROOT / NEW).read_bytes())
    out = {}
    for o in ("forward", "backward"):
        need([e for e in old[o] if e[0] != "scalar"] == [e for e in new[o] if e[0] != "scalar"], f"{o}: non-scalar events")
        A, B = segments(old[o]), segments(new[o])
        need(len(A) == len(B), f"{o}: segment count")
        changed = [i for i in range(len(A)) if A[i] != B[i]]
        need(len(changed) == 1, f"{o}: one changed scalar segment")
        i = changed[0]
        ea, eb = linear_effect(A[i]), linear_effect(B[i])
        for f in set(ea) | set(eb):
            need(ea.get(f, {f: Q(1)}) == eb.get(f, {f: Q(1)}), f"{o}: field {f} has the same linear effect")
        cost = tuple(sum(allowance(e[1]) for e in w[o] if e[0] == "scalar") for w in (old, new))
        need(cost == EXPECT[o], f"{o}: scalar allowance {cost}")
        out[o] = {"allowance": list(cost), "saving": cost[0] - cost[1], "changed_segment": i,
                  "segment_scalars": [len(A[i]), len(B[i])], "fields_compared": len(set(ea) | set(eb))}
    print(json.dumps({"status": "PASS_NATIVE_SPLICE_RECOUNT", **out, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
