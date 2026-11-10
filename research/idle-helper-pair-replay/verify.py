#!/usr/bin/env python3
"""Conformance and rejection controls for the bounded evaluation adapter."""

from collections import Counter
from contextlib import redirect_stdout
import hashlib
from io import StringIO
from itertools import product
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile


def need(condition, message):
    if not condition:
        raise SystemExit(message)


def observed_run(adapter, mode):
    source = adapter["load_source"]()
    counts = Counter()
    matrices = hashlib.sha256()
    original_need = source["need"]

    def counted_guard(condition, message):
        counts[message] += 1
        original_need(condition, message)

    def observe(difference, width):
        # All recorded integer entries of this fixed source fit in one byte.
        matrices.update(bytes(value + int(j // width == j % width)
                              for j, value in enumerate(difference)))

    source["need"] = counted_guard
    if mode == "baseline":
        multiply = source["mat_mul"]

        def observed_multiply(left, right):
            result = multiply(left, right)
            matrices.update(bytes(value for row in result for value in row))
            return result

        source["mat_mul"] = observed_multiply
    else:
        def observed_pairs(projectors):
            return adapter["check_pair_rank"](projectors, observe, counted_guard)

        source["check_pair_rank"] = observed_pairs
    output = StringIO()
    with redirect_stdout(output):
        source["main"]()
    # These checks enforce the new adapter's deliberately bounded domain.
    for message in ("projector count outside adapter domain", "width outside adapter domain",
                    "projectors are not equally square"):
        counts.pop(message, None)
    return output.getvalue(), counts, matrices.hexdigest()


def rejection_controls(adapter):
    source = adapter["load_source"]()
    bad = tuple(tuple(int(row == col and row < 3) for col in range(4))
                for row in range(4))
    rejected = 0
    for checker in (source["check_pair_rank"], adapter["check_pair_rank"]):
        try:
            checker([bad])
        except SystemExit as error:
            need(str(error) == "two rank-one updates produced rank above 2", "wrong rejection")
            rejected += 1
        else:
            raise SystemExit("rank-three mutation was accepted")
    for projectors in ([], [((1,),)], [((1, 0, 0), (0, 1, 0), (0, 0))]):
        try:
            adapter["check_pair_rank"](projectors)
        except SystemExit:
            rejected += 1
        else:
            raise SystemExit("invalid adapter domain was accepted")
    return rejected


def binding_control(adapter):
    """A disposable source export must reject a changed dependency before replay."""
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    with tempfile.TemporaryDirectory(prefix="idle-helper-binding-") as temporary:
        export = Path(temporary)
        replay = export / "research/idle-helper-pair-replay/replay.py"
        source = export / adapter["SOURCE"]
        replay.parent.mkdir(parents=True)
        source.parent.mkdir(parents=True)
        replay.write_bytes((package / "replay.py").read_bytes())
        source.write_bytes((root / adapter["SOURCE"]).read_bytes() + b"\n# changed source\n")
        result = subprocess.run([sys.executable, "-I", "-W", "error", "-B", str(replay)],
                                capture_output=True, text=True, timeout=10, check=False)
        need(result.returncode != 0 and result.stderr.strip() == "source hash mismatch",
             "changed source did not fail closed")
        need(not result.stdout, "changed source executed before rejection")


def main():
    adapter = runpy.run_path(str(Path(__file__).with_name("replay.py")))
    source = adapter["load_source"]()
    # Both determinant polynomials are multilinear in their nine entries.
    # Equality at all Boolean vertices proves their polynomial identity over Z.
    for entries in product((0, 1), repeat=9):
        matrix = tuple(tuple(entries[3 * row + col] for col in range(3)) for row in range(3))
        need(adapter["determinant_at"](entries, range(9)) == source["det3"](matrix),
             "determinant polynomial mismatch")
    baseline = observed_run(adapter, "baseline")
    fast = observed_run(adapter, "fast")
    need(baseline == fast, "complete output, guard coverage or matrix transcript differs")
    need(fast[1]["two rank-one updates produced rank above 2"] == 3686400,
         "minor coverage changed")
    rejected = rejection_controls(adapter)
    binding_control(adapter)
    print("PASS_IDLE_HELPER_PAIR_REPLAY pairs=14400 assignments=230400 minors=3686400"
          f" determinant_vertices=512 rejection_controls={rejected + 1} transcript={fast[2]}")


if __name__ == "__main__":
    main()
