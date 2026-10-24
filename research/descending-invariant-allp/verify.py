#!/usr/bin/env python3
"""The descending-support invariant of #4440's complex p-controller, for every p and keep mask.

Invariant (README, written proof): along the constructor's emitted event stream, every stage letter prepended to a
line (by LOCAL on a thick stage, or as an IDLE block d_(s_k)...d_(s_1)) is larger than every stage letter already on
that line; ADD only merges lines and SWAP/SIGNED_SWAP only move them. Hence every word in W is strictly descending
with distinct letters, abelianization is injective on W's support, and by the reduction lemma of
research/free-identity-allp any scalar commutative factorization L W_ab R = diag is also a noncommuting one.

Mechanized check: the constructor (research/kappa-rebuild/bit/complex_controller_factor.py via
research/query-thinned-controllers/controller.py) emits its event stream with its polynomial arithmetic stubbed out;
this verifier tracks, per line, the largest letter present, and checks the strict-increase condition at every
prepend, for p = 2..60, keep masks all-ones, all-zeros and three random masks, with and without thick-stage thinning.
The same is checked for #4440's BIT controller (bit.physical_controller; IDLE bitmasks decoded to stage lists).
evidence/ records the complex check up to p = 200.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def load_constructor():
    sys.path.insert(0, str(ROOT / "research/query-thinned-controllers"))
    spec = importlib.util.spec_from_file_location("qtc_controller", ROOT / "research/query-thinned-controllers/controller.py")
    C = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    B, M = C.engines()
    M.plus = lambda a, b, c=1: a              # the event stream does not depend on the polynomial values
    M.monomial_times = lambda poly, exp, c=1: poly
    B.add = lambda a, b: a                    # same for the binary group-ring controller
    B.shift = lambda a, m: a
    B.polynomial_coefficients = lambda m: {}
    return M, B


def invariant(events, p, thick=None):
    mx = [-1] * (2 * p)                       # largest letter on each line; -1 = no letter
    for ev in events:
        op = ev[0]
        if op == "LOCAL":
            _, stage, pair, rev = ev
            x, y = (2 * pair + 1, 2 * pair) if rev else (2 * pair, 2 * pair + 1)
            mx[y] = max(mx[y], mx[x])         # the shear merges x into y before the stage letter
            if thick is not None and stage not in thick:
                continue                      # thin stage: query shear only, no letter
            for r in (x, y):
                if not stage > mx[r]:
                    return False
                mx[r] = stage
        elif op == "IDLE":
            _, pair, sel = ev
            sel = [s for s in sel if thick is None or s in thick]
            if not sel:
                continue
            for r in (2 * pair, 2 * pair + 1):
                if not min(sel) > mx[r]:
                    return False
                mx[r] = max(sel)
        elif op == "ADD":
            _, d, s, *c = ev
            mx[d] = max(mx[d], mx[s])
        elif op in ("SWAP", "SIGNED_SWAP"):
            _, x, y = ev
            mx[x], mx[y] = mx[y], mx[x]
        else:
            raise AssertionError("unknown event " + op)
    return True


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    M, B = load_constructor()
    rng = random.Random(4540)
    cases = bit_cases = 0
    for p in range(2, 61):
        thick = {0, 2 * p, *range(1, 2 * p, 2)}
        for keep in [(1 << (8 * p)) - 1, 0] + [rng.getrandbits(8 * p) for _ in range(3)]:
            _, events, _ = M.controller(p, keep)
            for th in (None, thick):
                need(invariant(events, p, th), f"p={p}: descending invariant")
                cases += 1
            _, bev, _ = B.physical_controller(p, keep)
            bev = [["IDLE", e[1], [s for s in range(2 * p + 1) if e[2] >> (s + 1) & 1]] if e[0] == "IDLE" else e for e in bev]
            for th in (None, thick):
                need(invariant(bev, p, th), f"p={p}: BIT descending invariant")
                bit_cases += 1
    # control: a schedule that prepends an old stage again must fail
    bad = [["LOCAL", 1, 0, False], ["LOCAL", 0, 0, False]]
    need(not invariant(bad, 1), "non-increasing prepend rejected")
    ev = (HERE / "evidence/INVARIANT-P2-200.txt").read_text(encoding="utf-8")
    need("invariant holds:" in ev and "FAIL" not in ev, "recorded sweep to p = 200")
    print(json.dumps({"status": "PASS_DESCENDING_INVARIANT_ALLP", "cases_checked_here": cases, "bit_cases_checked_here": bit_cases, "p_range": [2, 60],
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
