"""Complete source-bound conformance and new-loop rejection controls."""

from contextlib import redirect_stdout
import hashlib
from io import StringIO
from itertools import product
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from loop import one_axis
from replay import ROOT, execute, load_source


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def complete_conformance():
    runs = []
    for mode in ("baseline", "fast"):
        census, output = [], StringIO()
        with redirect_stdout(output):
            execute(mode, census=census)
        runs.append((output.getvalue(), census))
    need(runs[0] == runs[1], "complete stdout and ordered rollout equality")
    text, census = runs[1]
    need(text == "PASS_CHIRP_RESIDUE_STEP rollouts=6141 no_new_kappa\n", "source marker")
    need(len(census) == 6141, "every rollout")
    steps = sum(row[3] for row in census)
    need(steps == 13981010, "every state")
    command = [sys.executable, "-I", "-W", "error", "-B",
               str(ROOT / "research/chirp-residue-step/test_verify.py")]
    result = subprocess.run(command, capture_output=True, timeout=10)
    need(result.returncode == 0 and not result.stderr
         and result.stdout == b"PASS_CHIRP_RESIDUE_STEP_TEST\n", "retained controls")
    return {"rollouts": len(census), "one_axis_states": steps,
            "eliminated_require_calls": 3 * steps + 2 * len(census),
            "census_sha256": hashlib.sha256(json.dumps(census).encode()).hexdigest()}


def initial_state_controls():
    failures = 0
    for length, slope in ((2, 1), (4, 1), (4, 3)):
        factor = (-slope * (4 // length)) % 8
        for value, difference, total in product(range(8), repeat=3):
            expected = ("value" if value != 0 else "difference" if difference != factor
                        else "one-axis total" if total != value else None)
            try:
                result = one_axis(4, length, slope, initial=(0, value, difference, total))
            except SystemExit as error:
                need(str(error) == "FAIL_CHIRP_RESIDUE_STEP " + str(expected),
                     "first failing source predicate")
                failures += 1
            else:
                need(expected is None and result == length, "valid initial state")
    need(failures == 1533, "initial-state rejection census")
    return failures


def boundary_controls():
    cases = ((True, 2, 1), (2, 1, 1), (8192, 4096, 1), (6, 3, 1),
             (4, True, 1), (4, 3, 1), (4, 4, True), (4, 4, 2),
             (4, 4, 0), (4, 4, 5))
    for args in cases:
        try:
            one_axis(*args)
        except ValueError:
            continue
        raise AssertionError("invalid domain accepted: " + repr(args))
    initials = ((0,), (0, 0, True, 0), (-1, 0, 0, 0), (2, 0, 0, 0),
                (0, 0, 1 << 65, 0))
    for initial in initials:
        try:
            one_axis(4, 2, 1, initial=initial)
        except ValueError:
            continue
        raise AssertionError("invalid control state accepted")
    return len(cases) + len(initials)


def source_invalidation():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    with tempfile.TemporaryDirectory(prefix="chirp-loop-control-") as folder:
        root = Path(folder)
        for row in inputs:
            target = root / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / row["path"]).read_bytes())
        target = root / "research/chirp-residue-step/verify.py"
        target.write_bytes(target.read_bytes() + b"\nraise RuntimeError('must not execute')\n")
        try:
            load_source(root)
        except ValueError as error:
            need(str(error) == "source hash mismatch: research/chirp-residue-step/verify.py",
                 "source drift must reject before execution")
        else:
            raise AssertionError("altered source accepted")
    return 1


def main():
    result = complete_conformance()
    result["initial_state_rejections"] = initial_state_controls()
    result["boundary_rejections"] = boundary_controls()
    result["source_drift_rejections"] = source_invalidation()
    result["status"] = "PASS_CHIRP_RESIDUE_LOOP"
    result["files"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
