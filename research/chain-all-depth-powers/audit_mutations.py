#!/usr/bin/env python3
"""Exercise the normal verifier with deliberately incorrect private copies."""
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
MUTANTS = [
    ("strip_only_one_shared_factor", "law.py", "while (shared :=", "if (shared :="),
    ("ban_prime_boundary", "law.py", "prime < depth:", "prime <= depth:"),
    ("stop_gates_at_depth_four", "law.py", "prime < depth:", "prime < min(depth, 5):"),
    ("lose_composite_multiplier", "law.py", "(repeats // depth) * pow", "pow"),
    ("erase_surviving_shift", "law.py", "return (repeats // depth) * pow(block_size, depth, modulus) % modulus", "return 0"),
    ("allow_uncleared_block", "law.py", "if base_target is None or offset is None:",
     "if base_target is None and offset is not None:\n        base_target = 0\n    if offset is None:"),
    ("skip_exact_quotient", "law.py", "if offset is None or (target - offset) % repeats:", "if offset is None:"),
    ("omit_shift_in_root", "law.py", "((target - offset) // repeats)", "(target // repeats)"),
    ("omit_small_prime_radical", "law.py", "gcd(target, modulus // radical)", "gcd(target, modulus)"),
    ("use_prime_instead_of_prime_power", "law.py", "% edge_power == 0:", "% depth == 0:"),
    ("lose_prime_order_extension", "law.py", "bound *= depth", "bound *= 1"),
    ("allow_composite_unit_depth", "law.py", "first_missing_prime(depth, 1) != depth or modulus % depth", "modulus % depth"),
    ("ignore_unit_residue", "law.py", "or (target - residue) % depth:", "or False:"),
    ("wrong_inverse_suffix_sign", "quintic_rows.py", "sign*matrix[5][0] % n", "matrix[5][0] % n"),
    ("lose_gap_interleavings", "quintic_rows.py", "prod(comb(x+y, x) for x, y in zip(a[0], b[0]))", "1"),
    ("tamper_with_witness", "source/depth5-witnesses.json", "41545521341233132545311545421342223",
     "11545521341233132545311545421342223"),
    ("tamper_with_result", "EXPECTED.json", '"total_blocks": 123698', '"total_blocks": 123699'),
]

REJECTION_CHECKS = {
    "strip_only_one_shared_factor": ("first surviving coefficient",),
    "ban_prime_boundary": ("literal power disagreement",),
    "stop_gates_at_depth_four": ("literal power disagreement",),
    "lose_composite_multiplier": ("literal power disagreement",),
    "erase_surviving_shift": ("literal power disagreement",),
    "allow_uncleared_block": ("literal power disagreement",),
    "skip_exact_quotient": ("fixed-count transform",),
    "omit_shift_in_root": ("fixed-count transform",),
    "omit_small_prime_radical": ("sharp nonunit order bound",),
    "use_prime_instead_of_prime_power": ("full prime-power target congruence",),
    "lose_prime_order_extension": ("target-wise divisor of W",),
    "allow_composite_unit_depth": ("unit root arithmetic",),
    "ignore_unit_residue": ("unit primitive count", "unit root arithmetic"),
    "wrong_inverse_suffix_sign": ("witness inverse-suffix join",),
    "lose_gap_interleavings": ("gap multinomial mass",),
    "tamper_with_witness": ("retained source bytes differ",),
    "tamper_with_result": ("retained result differs",),
}


def private_copy(destination):
    shutil.copytree(HERE, destination, copy_function=shutil.copyfile,
                    ignore=shutil.ignore_patterns("__pycache__"))
    for directory in [destination, *(p for p in destination.rglob("*") if p.is_dir())]:
        directory.chmod(directory.stat().st_mode | stat.S_IRWXU)


def run(folder, optimized):
    flags = ["-O"] if optimized else []
    return subprocess.run([sys.executable, "-I", *flags, "-W", "error", "-B",
                           str(folder / "verify.py")], cwd=folder,
                          capture_output=True, text=True, timeout=180)


def main():
    reasons = {}
    with tempfile.TemporaryDirectory(prefix="all-depth-chain-check-") as scratch:
        baseline = Path(scratch) / "baseline"
        private_copy(baseline)
        for optimized in (False, True):
            result = run(baseline, optimized)
            if result.returncode or json.loads(result.stdout)["result"]["status"] != "PASS_CHAIN_ALL_DEPTH_POWERS":
                raise ValueError("unmodified private copy failed: " + result.stderr)
        for name, filename, old, new in MUTANTS:
            changed = Path(scratch) / name
            private_copy(changed)
            target = changed / filename
            original = target.read_text(encoding="utf-8")
            if original.count(old) != 1:
                raise ValueError("mutation anchor must be unique: " + name)
            target.write_text(original.replace(old, new), encoding="utf-8", newline="\n")
            modes = []
            for optimized in (False, True):
                result = run(changed, optimized)
                last = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""
                permitted = tuple("ValueError: " + message for message in REJECTION_CHECKS[name])
                if result.returncode == 0 or not last.startswith(permitted):
                    raise ValueError("expected semantic rejection: " + name + " " + last)
                modes.append(last)
            if modes[0] != modes[1]:
                raise ValueError("rejection differs between modes: " + name)
            reasons[name] = modes[0]
    print(json.dumps(dict(status="PASS_CHAIN_ALL_DEPTH_MUTATIONS", positive_probes=2,
                          rejected_probes=2*len(reasons), reasons=reasons), sort_keys=True))


if __name__ == "__main__":
    main()
