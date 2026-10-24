#!/usr/bin/env python3
"""Lockstep live-role audit and #4470 binding of the outer-reserve constant C.

Standard library only. Exit status 0 means every check passed; a JSON summary is
printed. See README.md for the statements and the general argument.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import constant_c  # noqa: E402
import live_roles as L  # noqa: E402

BINDINGS = {
    "research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md": [
        "a distinct physical array. The row matching here assumes that ownership.",
        r"x_g\longmapsto y_{gS}=x_g.",
    ],
    "research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md": [
        "Process a class in word order. At round `j`, suspend every unit of that",
        "One owned `C0` per recursion depth is therefore insufficient in general.",
        "or even per compiled unit instance. Retain each bank until its unit clears",
    ],
    "research/kappa-rebuild/transfer-audit/AUDIT.md": [
        "New source arrays are globally distinct. Within a class, each parent issues",
    ],
    "research/higher-moment-strictification/README.md": [
        "Never combine two different paid positions of the same suspended U copy.",
    ],
    "research/kappa-rebuild/transfer-audit/OUTER-TRANSFER-AUDIT.md": [
        "q0(h,p) <= C*(log2 h + h^0.003*(log2 p)^3 + 1)",
    ],
    "research/capped-phase-fusion/SUPPLIER-SUPPORT-AUDIT.md": [
        "G=4 ceil(log2 p)+6",
        "With K=128G",
    ],
}

CASES = ([(L.toy(), n) for n in (4, 7, 12, 16, 28, 40, 64)]
         + [(L.bit_shaped(s), n) for s in range(3) for n in (50, 400, 3200)]
         + [(L.bit_shaped(10, adversarial="one_owner"), 3200), (L.bit_shaped(11, adversarial="centre"), 3200)]
         + [(L.bit_shaped(20, roles_per_rank=(2, 1, 1), n_rounds=8), 25600)])


def need(ok, msg):
    if not ok:
        raise SystemExit("FAIL: " + msg)


def main():
    t0 = time.time()
    for path, needles in BINDINGS.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        for s in needles:
            need(s in text, f"binding in {path}: {s}")
    # 1. constant C
    c = constant_c.compute()
    need(c["log2_C_upper"] == 64215200000088 and c["fit_log2p"] == 64473100659114, "constant C values")
    # 2. compiler counting equals the repository receipt
    rec = json.loads((ROOT / "research/kappa-rebuild/transfer-audit/FINITE-DAG-AUDIT.json").read_text())
    t40 = next(r for r in rec["synthetic_rule_tests"] if r["rank"] == 40)
    B, a, P, _ = L.Compiler(L.toy()).compile(40)
    need((B, P) == (t40["width"], t40["leaves"]), "toy rank 40 width/leaves equal FINITE-DAG-AUDIT")
    cx = L.complex_p2()
    B, a, P, _ = L.Compiler(cx).compile(41)
    need((B, P) == (1397, 57149), "complex p2 rank 41 equals receipt")
    # 3. event-level execution with live-role stacks
    rows = {}
    for rule, n in CASES + [(cx, 41)]:
        try:
            r = L.audit(rule, n)
        except L.Violation as e:
            raise SystemExit(f"FAIL {rule.name} N={n}: {e}")
        rows[f"{rule.name} | N={n}"] = {k: r[k] for k in ("generations", "width_B_log10", "executed_tree_copies",
                                                           "full_width_executed", "events",
                                                           "max_live_stack_on_one_array")}
    print(json.dumps({"status": "PASS", "bindings": sum(map(len, BINDINGS.values())),
                      "log2_C_upper": c["log2_C_upper"], "complex_share_log2": c["complex_share_log2"],
                      "bit_share_log2": c["bit_share_log2"], "fit_log2p": c["fit_log2p"],
                      "constant_c_checks": len(constant_c.LINES), "live_role_cases": rows,
                      "seconds": round(time.time() - t0, 1)}, indent=1))


if __name__ == "__main__":
    main()
