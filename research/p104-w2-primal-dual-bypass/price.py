"""Verify official recursive invoice order and 256-bit crossing bracket via repository scripts.

Uses repository scripts/compare_recursive_invoices.py and scripts/evaluate_recursive_power.py:
  1. Checks SHA-256 of evidence/invoice-step1.json and data/invoice-7616.json.
  2. Runs compare_recursive_invoices.py vs #7616 and derived #7617 (both strictly uniformly_better).
  3. Runs evaluate_recursive_power.py (--bits 256) vs zero baseline verifying the crossing bracket
     (C = 0.003665051802188 -> new_cost_lower; C = 0.003665051802189 -> new_cost_higher),
     and vs #7616 (#7617) confirming new_cost_lower at C = 0.003656628302607, 0.00365760025222, and 0.003665051802188.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
EVID = HERE / "evidence"

EXPECTED_SHA256 = {
    "invoice-step1.json": "e3f1c1bb9516eb141f2c51b8cd12a9a55026f5968082083bd8d9fdb793a2e486",
    "invoice-7616.json": "a447ee0dd378ee10f3892d68136b7923a71742c0bd2fa783a8bd53c7f7023159",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_json_script(script: Path, argv: list[str]) -> dict:
    proc = subprocess.run(
        [sys.executable, "-B", str(script), *argv],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def resolve_repo(explicit: str | None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    env_repo = os.environ.get("IMB_REPO")
    if env_repo:
        candidates.append(Path(env_repo))
    if len(HERE.parents) >= 3:
        candidates.append(HERE.parents[2])
    for cand in candidates:
        if (cand / "scripts" / "compare_recursive_invoices.py").is_file() and (
            cand / "scripts" / "evaluate_recursive_power.py"
        ).is_file():
            return cand
    raise FileNotFoundError("Could not locate integer-mult-bounds scripts/ directory; pass --repo PATH or set IMB_REPO")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=None, help="Path to integer-mult-bounds repository checkout")
    args = parser.parse_args(argv)
    repo = resolve_repo(args.repo)
    cmp_script = repo / "scripts" / "compare_recursive_invoices.py"
    pow_script = repo / "scripts" / "evaluate_recursive_power.py"

    inv_step1 = EVID / "invoice-step1.json"
    inv_7616 = DATA / "invoice-7616.json"
    assert sha256_file(inv_step1) == EXPECTED_SHA256["invoice-step1.json"]
    assert sha256_file(inv_7616) == EXPECTED_SHA256["invoice-7616.json"]

    d_step1 = json.loads(inv_step1.read_text(encoding="utf-8"))
    d_7616 = json.loads(inv_7616.read_text(encoding="utf-8"))
    assert d_step1["contract"] == d_7616["contract"]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        inv_zero = tmp / "invoice-zero.json"
        inv_zero.write_text(
            json.dumps(
                {
                    "schema": d_step1["schema"],
                    "contract": d_step1["contract"],
                    "paid": {},
                    "targets": {},
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        # #7617 delta over #7616 is paid {1:-17, 2:-17, 3:-17, 6:+17}, targets unchanged
        paid_7617 = {k: int(v) for k, v in d_7616["paid"].items()}
        for rk, dv in (("1", -17), ("2", -17), ("3", -17), ("6", 17)):
            nv = paid_7617.get(rk, 0) + dv
            if nv:
                paid_7617[rk] = nv
            else:
                paid_7617.pop(rk, None)
        inv_7617 = tmp / "invoice-7617.json"
        inv_7617.write_text(
            json.dumps(
                {
                    "schema": d_7616["schema"],
                    "contract": d_7616["contract"],
                    "paid": paid_7617,
                    "targets": d_7616["targets"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        cmp16 = run_json_script(cmp_script, [str(inv_7616), str(inv_step1)])
        assert cmp16["classification"] == "uniformly_better"
        assert cmp16["delta_paid"] == {"1": -85, "2": 1139, "3": -2397, "4": 1054, "5": 34, "6": 102}
        assert cmp16["delta_targets"] == {}

        cmp17 = run_json_script(cmp_script, [str(inv_7617), str(inv_step1)])
        assert cmp17["classification"] == "uniformly_better"
        assert cmp17["delta_paid"] == {"1": -68, "2": 1156, "3": -2380, "4": 1054, "5": 34, "6": 85}
        assert cmp17["delta_targets"] == {}

        lo = run_json_script(
            pow_script, [str(inv_zero), str(inv_step1), "--exponent", "0.996334948197812", "--bits", "256"]
        )
        hi = run_json_script(
            pow_script, [str(inv_zero), str(inv_step1), "--exponent", "0.996334948197811", "--bits", "256"]
        )
        assert lo["classification"] == "new_cost_lower"
        assert hi["classification"] == "new_cost_higher"

        p16 = run_json_script(
            pow_script, [str(inv_7616), str(inv_step1), "--exponent", "0.996343371697393", "--bits", "256"]
        )
        p17 = run_json_script(
            pow_script, [str(inv_7617), str(inv_step1), "--exponent", "0.99634239974778", "--bits", "256"]
        )
        p_own = run_json_script(
            pow_script, [str(inv_7617), str(inv_step1), "--exponent", "0.996334948197812", "--bits", "256"]
        )
        assert p16["classification"] == "new_cost_lower"
        assert p17["classification"] == "new_cost_lower"
        assert p_own["classification"] == "new_cost_lower"

    print(
        "PASS_PRICE_STEP1 kappa=0.003665051802188 (bracket [0.003665051802188, 0.003665051802189]); "
        "uniformly_better vs #7616 & #7617"
    )


if __name__ == "__main__":
    main()
