"""Cold, source-pinned checks for the conditional 39/10000 installation."""

from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from install import build


def run(script, *args, expected=None, scope=None):
    print("RUN", script.name, flush=True)
    with TemporaryDirectory(prefix="target-private-cache-") as cache:
        proc = subprocess.run(
            [
                sys.executable,
                "-IB",
                "-X",
                f"pycache_prefix={cache}",
                str(script),
                *map(str, args),
            ],
            capture_output=True,
            text=True,
        )
    if proc.returncode:
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        raise RuntimeError(f"{script.name} exited {proc.returncode}")
    if expected:
        observed = json.loads(proc.stdout)
        assert observed == json.loads((HERE / expected).read_bytes()), script.name
    if scope:
        assert scope in proc.stdout, (script.name, scope)
    if expected is None:
        print(proc.stdout.strip()[-1024:], flush=True)


def replay(mode):
    if not __debug__:
        raise RuntimeError("Run with assertions enabled")
    with TemporaryDirectory(prefix="target-8088-") as scratch:
        root = Path(scratch)
        tree = root / "application"
        peer, runtime = build(tree)
        if mode == "price":
            run(HERE / "invoice.py", tree, expected="RESULT.json")
            tables = root / "bill-inputs.json"
            run(
                HERE / "freeze_inputs.py",
                "--runtime",
                runtime,
                "--expected-result",
                HERE / "RESULT.json",
                "--output",
                tables,
                scope="PASS_FROZEN_LITERAL_INVOICE_INPUTS",
            )
            assert json.loads(tables.read_bytes()) == json.loads(
                (HERE / "BILL-INPUTS.json").read_bytes()
            )
            run(
                HERE / "check_bill.py",
                "--inputs",
                tables,
                "--expected-result",
                HERE / "RESULT.json",
                expected="BILL.json",
            )
            run(HERE / "check_comparator.py", expected="COMPARATOR.json")
            run(HERE / "check_negative_controls.py", "--inputs", tables, "--expected-result", HERE / "RESULT.json", "--output", root/"negative.json", scope="PASS_INDEPENDENT_BILL_NEGATIVE_CONTROLS")
            run(HERE / "check_prices.py", tree, expected="PRICES.json")
            run(HERE / "check_ordinary.py", runtime, peer, expected="ORDINARY.json")
            run(HERE / "check_floor.py", tree, expected="FLOOR.json")
        elif mode == "algebra":
            run(HERE / "check_grid.py", runtime, expected="GRID.json")
            run(
                HERE / "check_caller.py",
                runtime,
                HERE / "GRID.json",
                expected="CALLER.json",
            )
            run(HERE / "check_atlas.py", runtime, expected="ATLAS.json")
            run(
                HERE / "check_rational.py",
                runtime,
                "--output",
                root / "matrix.json",
                scope="PASS_RATIONAL_1291_OUTPUT_IDENTITY",
            )
        elif mode == "setup":
            run(
                HERE / "check_bootstrap.py",
                HERE / "parent8088",
                tree,
                "--frozen-bytes",
                scope="PASS_PINNED_BOOTSTRAP_COMPARISON",
            )
            run(HERE / "check_census.py", tree, expected="CENSUS.json")
            run(HERE / "check_phase_census.py", tree, expected="PHASES.json")
            run(
                HERE / "check_setup.py",
                tree,
                scope="PASS_8088_TARGET_FIXED_CONSTRUCTOR",
            )
            run(
                HERE / "check_receiver.py",
                "run",
                tree,
                scope="PASS_SEPARATE_PROCESS_FIXED_INSTALLATION",
            )
        elif mode == "layers":
            run(HERE / "check_cutoff.py", runtime, scope="PASS_LITERAL_LOWER_CUTOFF")
            run(
                HERE / "check_path_binding.py",
                runtime,
                "--output",
                root / "path.json",
                scope="PASS_SHORTCUT_PATH_BINDING",
            )
            for name in (
                "check_calendar.py",
                "check_ownership.py",
                "check_placement.py",
                "check_raw.py",
                "check_exterior.py",
            ):
                run(peer / name, runtime)
        elif mode == "product":
            run(peer / "check_nested.py", runtime, scope="PASS_NONZERO_INTERIOR")
            run(
                HERE / "check_product_path.py",
                runtime,
                peer,
                scope="PASS_CANDIDATE_RESTORED_SIGNED_PRODUCT",
            )
        else:
            raise ValueError(mode)
    print("PASS_TARGET_" + mode.upper(), flush=True)


if __name__ == "__main__":
    p = ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=["price", "algebra", "setup", "layers", "product"])
    replay(p.parse_args().mode)
