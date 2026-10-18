"""Verify the dense-polar small-T gain screen.

Reruns search.py (deterministic, seeded) and checks CERTIFICATE.json against
the pinned PR 2125 table values and the exhaustive-census counts.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

PINNED_CONTROLS = {
    "D4": {"v": 12, "cost": 12},
    "D5": {"v": 20, "cost": 20},
    "D6": {"v": 30, "cost": 30},
    "A4": {"v": 10, "cost": 16},
    "A5": {"v": 15, "cost": 25},
    "A6": {"v": 21, "cost": 36},
    "E7": {"v": 63, "cost": 49},
    "E8": {"v": 120, "cost": 72},
    "E6": {"v": 36, "cost": 36},
    "E6_firstB0": {"v": 36, "cost": 37},
}

PINNED_EXHAUSTIVE = {
    "T3_pm1_all_subsets": {"subsets_checked": 8191, "gain_count": 0, "min_cost_minus_v": 0},
    "D4_all_subsets": {"subsets_checked": 4095, "gain_count": 0, "min_cost_minus_v": 0},
    "D5_all_subsets": {"subsets_checked": 1048575, "gain_count": 0, "min_cost_minus_v": 0},
}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    py = sys.executable
    run = subprocess.run([py, os.path.join(HERE, "search.py")],
                         capture_output=True, text=True, encoding="utf-8")
    print(run.stdout[-2000:])
    if run.returncode != 0:
        print("FAIL search.py exited", run.returncode)
        print(run.stderr[-1000:])
        return 1
    with open(os.path.join(HERE, "CERTIFICATE.json"), encoding="utf-8") as f:
        cert = json.load(f)
    bad = []
    for name, want in PINNED_CONTROLS.items():
        got = cert["controls"].get(name)
        if got is None:
            bad.append("missing control " + name)
            continue
        for k, w in want.items():
            if got.get(k) != w:
                bad.append("control %s %s: got %s want %s" % (name, k, got.get(k), w))
    ex = {r["label"]: r for r in cert["exhaustive"]}
    for name, want in PINNED_EXHAUSTIVE.items():
        got = ex.get(name)
        if got is None:
            bad.append("missing exhaustive " + name)
            continue
        for k, w in want.items():
            if got.get(k) != w:
                bad.append("exhaustive %s %s: got %s want %s" % (name, k, got.get(k), w))
    if cert.get("any_gain_found") is not False:
        bad.append("any_gain_found is not False")
    if cert.get("control_failures"):
        bad.append("control failures recorded: %s" % cert["control_failures"])
    # every bounded search must report a nonnegative min
    for group in ("bounded", "basis_pivots"):
        for nm, entry in cert.get(group, {}).items():
            vals = entry.values() if group == "basis_pivots" else (
                [entry["greedy"], entry["random"]])
            for sub in vals:
                if isinstance(sub, dict) and sub.get("min_cost_minus_v", 0) < 0:
                    bad.append("%s/%s reports a gain" % (group, nm))
    if bad:
        for b in bad:
            print("FAIL", b)
        print("FAIL_POLAR_SMALLT_SCREEN")
        return 1
    print("PASS_POLAR_SMALLT_SCREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
