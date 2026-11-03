"""Check the new implementation contract, custody and full source integration.

Produced by Nick Petalas. Apache-2.0. This preserves predecessor coverage;
it does not claim independent acceptance of the predecessor mathematics.
"""

from contextlib import redirect_stderr, redirect_stdout
from fractions import Fraction
from hashlib import sha256
from io import StringIO
from itertools import product
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay


def rejected(call, message):
    try:
        call()
    except (ValueError, OSError) as error:
        replay.require(message in str(error), "unexpected rejection: " + str(error))
        return
    raise ValueError("missing rejection: " + message)


def dot_cases():
    basis = [tuple(int(i == j) for i in range(8)) for j in range(8)]
    cases = [(a, b) for a in basis for b in basis]
    for signs in product((-1, 1), repeat=8):
        a = tuple(signs[i] * (i + 1) for i in range(8))
        b = tuple(Fraction(signs[7 - i] * (3 * i - 11), i + 2) for i in range(8))
        cases.extend(((a, b), (b, a)))
    for a, b in cases:
        replay.require(replay.dot8(a, b) == sum(x * y for x, y in zip(a, b)),
                       "exact scalar case")
    for left, right in ((0, 8), (7, 8), (9, 8), (8, 0), (8, 7), (8, 9)):
        rejected(lambda: replay.dot8([0] * left, [0] * right), "eight coordinates")
    rejected(lambda: replay.run_replay("unknown"), "replay mode")
    return len(cases), 7


def custody_controls():
    originals = replay.authenticated_inputs(replay.PACKAGE.parents[1])
    with TemporaryDirectory(prefix="e8-dot-custody-") as name:
        root = Path(name)
        for path, raw in originals.items():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            replay.require(target.write_bytes(raw) == len(raw), "fixture write")
        for path, raw in originals.items():
            target = root / path
            replay.require(target.write_bytes(raw + b"\n") == len(raw) + 1,
                           "mutation write")
            rejected(lambda: replay.authenticated_inputs(root), "changed source")
            replay.require(target.write_bytes(raw) == len(raw), "fixture restore")
        path = next(iter(originals))
        (root / path).unlink()
        rejected(lambda: replay.authenticated_inputs(root), "No such file")
    return len(originals) + 1


def complete_conformance():
    names = ("geometry_audit", "algebra_check", "extension_check", "e8_bound_source")
    previous = {name: sys.modules.get(name) for name in names}
    sentinels = {name: ModuleType(name) for name in names}
    old_path, old_argv = sys.path[:], sys.argv[:]
    output = StringIO()
    try:
        sys.modules.update(sentinels)
        with redirect_stdout(output):
            stats = replay.run_replay("checked")
        replay.require(output.getvalue() == replay.EXPECTED, "complete source stdout")
        replay.require(stats == {"calls": 5096623}, "complete replacement coverage")
        replay.require(all(sys.modules[name] is sentinels[name] for name in names),
                       "module restoration")
        replay.require(sys.path == old_path and sys.argv == old_argv,
                       "process-state restoration")
    finally:
        for name in names:
            if previous[name] is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous[name]
    return stats


def kernel_fault_control():
    original = replay.dot8
    def damaged(a, b):
        return original(a, b) - a[7] * b[7]
    replay.dot8 = damaged
    error = StringIO()
    try:
        with redirect_stdout(StringIO()), redirect_stderr(error):
            rejected(lambda: replay.run_replay("fast"), "complete scientific replay failed")
        replay.require("root norm is not two" in error.getvalue(),
                       "source did not detect the changed dot product")
    finally:
        replay.dot8 = original
    return 1


def main():
    replay.require(len(sys.argv) == 1, "verify.py takes no arguments")
    scalar_cases, controls = dot_cases()
    controls += custody_controls()
    stats = complete_conformance()
    controls += kernel_fault_control()
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "replay.py", "benchmark.py", "verify.py")
    hashes = {name: sha256((replay.PACKAGE / name).read_bytes()).hexdigest()
              for name in names}
    print(json.dumps({"status": "PASS_E8_ROOT_SWAP_FAST_INNER",
                      "scalar_cases": scalar_cases, "controls": controls,
                      "complete_dot_comparisons": stats["calls"],
                      "source_stdout_sha256": sha256(replay.EXPECTED.encode()).hexdigest(),
                      "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
