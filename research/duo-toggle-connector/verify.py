"""Reproduction entry point for research/duo-toggle-connector.

Runs the deterministic census (generate.py --check), the code-disjoint
independent checks (independent.py), and the priced whole-construction
comparison.  Standard library only.

    python3 -B research/duo-toggle-connector/verify.py

Expected: PASS_DUO_TOGGLE_CONNECTOR queries=72->74 adds=74

Navinor, with help from opencode.  Apache-2.0.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(script):
    cmd = [sys.executable, "-B", os.path.join(HERE, script)]
    if script == "generate.py":
        cmd.append("--check")
    res = subprocess.run(cmd, capture_output=True, text=True)
    sys.stdout.write(res.stdout)
    sys.stderr.write(res.stderr)
    return res.returncode


def pricing(cert):
    base = cert["pricing"]["baseline_74"]
    duo = cert["pricing"]["duo_72"]
    assert base["root_queries"] == 74 and base["toggle_adds"] == 74
    assert duo["root_queries"] == 72 and duo["toggle_adds"] == 74
    assert duo["source_calls"] + duo["readouts"] == 72
    assert duo["readouts"] == base["readouts"] == 62
    w = cert["n5_witness"]
    assert w["k"][0] == duo["source_calls"] == 10
    assert w["W"] == 12 and duo["toggle_adds"] == 62 + 12
    saved_queries = base["root_queries"] - duo["root_queries"]
    saved_adds = base["toggle_adds"] - duo["toggle_adds"]
    assert saved_queries == 2 and saved_adds == 0
    # Model c_B = o + p (one add), c_DUO = o + 2p, c_A = o + p.
    # Baseline total 74o + 74p; DUO total 72o + 74p; saving exactly 2o.
    return saved_queries, saved_adds


def main():
    args = set(sys.argv[1:])
    if "--downstream" not in args:
        if run("generate.py") != 0:
            print("FAIL: generate.py")
            return 1
    if run("independent.py") != 0:
        print("FAIL: independent.py")
        return 1
    with open(os.path.join(HERE, "CERTIFICATE.json"), encoding="utf-8") as f:
        cert = json.load(f)
    saved_queries, saved_adds = pricing(cert)
    print("PRICING baseline=%d queries/%d adds duo=%d queries/%d adds"
          % (74, 74, 72, 74))
    print("PRICING saving=%d root queries, %d toggle-adds (2 per-call overheads o)"
          % (saved_queries, saved_adds))
    print("PASS_DUO_TOGGLE_CONNECTOR queries=72->74 adds=74 pareto=(10,12)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
