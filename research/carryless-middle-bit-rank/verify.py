"""Replay the construction and its independent certificates using the standard library."""
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def run(relative_path):
    # Several frozen research checkers use assert. Invoke each in isolated mode
    # with assertions active, even when the outer runner uses optimized Python.
    return subprocess.run(
        [sys.executable, "-I", "-B", "-W", "error", str(ROOT / relative_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=90,
    ).stdout


def compare_json(script, receipt, environmental_fields=()):
    actual = json.loads(run(script))
    expected = json.loads((ROOT / receipt).read_text(encoding="utf-8"))
    for name in environmental_fields:
        del actual[name], expected[name]
    if actual != expected:
        raise ValueError(f"output from {script} disagrees with {receipt}")
    return actual


def main():
    raw = run("raw/check.py").splitlines()
    reference = (ROOT / "raw/rank_checks.txt").read_text(encoding="utf-8").splitlines()
    if not reference[-1].startswith("wall_seconds=") or raw != reference[:-1]:
        raise ValueError("literal product-bit rank table changed")
    planes = compare_json("planes/verify.py", "planes/certificate.json")
    witness = compare_json(
        "nonlinear/verify.py", "nonlinear/RESULT.json",
        ("CPU_seconds", "maximum_RSS_KiB", "limits", "utc_start", "utc_end", "wall_seconds"),
    )
    review = compare_json("review/independent_check.py", "review/independent-result.json")
    fields = compare_json("review/extension_check.py", "review/extension-result.json")
    joint = compare_json("review/joint_extension_check.py", "review/joint-extension-result.json")
    print("PASS carryless middle product bit")
    print(f"full and odd ranks through m=12; {planes['summary']['digit_comparisons']:,} digit comparisons")
    print(f"{witness['checked_pairs']} five-bit odd pairs; {witness['total_gate_counts']}")
    gates = review["odd_five_bit"]["fixed_encoding_AND_minimum"]
    print(f"{gates['second_gate_factor_pairs']:,} independent second-gate factor pairs")
    print(f"{fields['checked_pairs']:,} odd field-construction pairs through m=10")
    print(f"{joint['pairs']:,} full odd-residue and adjacent-bit pairs through m=10")


if __name__ == "__main__":
    main()
