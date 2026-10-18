#!/usr/bin/env python3
"""Check directional backing bounds on authenticated PR2697 continuation tapes."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREDECESSOR = ROOT / "research/selected-continuation-storage"
HEAD = "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def capacities(depth, index_bits, residue_bits):
    need(type(depth) is int and 0 <= depth <= 1_000_000, "bounded nonnegative depth")
    need(
        all(type(b) is int and 2 <= b <= 1_000_000 for b in (index_bits, residue_bits)),
        "bounded fixed word lengths",
    )
    request, scalar = 2 * index_bits + 4, residue_bits + 3
    if depth == 0:
        return (request + 1, request, scalar + 1, scalar)
    largest = max(request, scalar)
    live = (depth + 1) * largest + depth * scalar
    return (live + 1, largest, (depth + 1) * scalar + 1, scalar)


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    inputs = [item for item in manifest["files"] if item["usage"] == "input"]
    expected = {"README.md", "verify.py", "SNAPSHOT.json"} | {
        "vendor/" + name
        for name in (
            "words.py",
            "records.py",
            "matrices.py",
            "controller.py",
            "NOTICE.md",
        )
    }
    need(len(inputs) == len(expected), "closed predecessor input inventory")
    for item in inputs:
        path = Path(item["path"])
        need(
            path.as_posix().startswith("research/selected-continuation-storage/"),
            "canonical predecessor path",
        )
        relative = path.relative_to("research/selected-continuation-storage").as_posix()
        need(relative in expected, "declared predecessor input")
        expected.remove(relative)
        source = ROOT / path
        need(not source.is_symlink() and source.is_file(), "regular source input")
        raw = source.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == item["sha256"], "predecessor SHA256")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == item["git_blob"], "predecessor Git blob")
    need(not expected, "complete predecessor inputs")
    snapshot = json.loads((PREDECESSOR / "SNAPSHOT.json").read_text())
    need(snapshot["head"] == HEAD, "scientific source head")
    module = ModuleType("continuation_predecessor")
    path = PREDECESSOR / "verify.py"
    module.__file__ = str(path)
    # The bytes and every nonstandard dependency were authenticated above.
    exec(
        compile(path.read_bytes(), str(path), "exec", dont_inherit=True),
        module.__dict__,
    )
    return module


def observer_type(predecessor, limits, collected, warm, total_quota):
    class Directional(predecessor.Census):
        """Observe each actual Tape.write and enforce before any growing write."""

        def __init__(self, records, stacks, direct=False):
            super().__init__(records, stacks, direct)
            for tape, length in zip(self.tapes, warm, strict=True):
                tape.cells.extend([records.BLANK] * (length - len(tape.cells)))
            self.entry = tuple(len(tape.cells) for tape in self.tapes)
            self.limits = tuple(
                max(k, c) for k, c in zip(self.entry, limits, strict=True)
            )
            self.lengths = self.entry
            collected.append(self)

        def __enter__(self):
            try:
                return super().__enter__()
            except Exception:
                # Python does not call __exit__ when __enter__ rejects.
                super().__exit__()
                raise

        def scan(self):
            super().scan()
            actual = tuple(len(tape.cells) for tape in self.tapes)
            need(
                all(k <= c for k, c in zip(actual, self.limits, strict=True)),
                "directional tape capacity",
            )
            self.lengths = actual
            if total_quota is not None:
                need(sum(actual) <= total_quota, "joint tape capacity")

        def write(self, tape, symbol):
            if id(tape) in self.identities:
                position = self.tapes.index(tape)
                proposed = max(len(tape.cells), tape.head + 1)
                need(proposed <= self.limits[position], "directional tape capacity")
                if total_quota is not None:
                    other = sum(len(t.cells) for t in self.tapes if t is not tape)
                    need(other + proposed <= total_quota, "joint tape capacity")
            super().write(tape, symbol)
            self.scan()

    return Directional


def fixture_limits(modes, residue_bits, literal, short, warm, repeats):
    depth = len(modes)
    need(
        depth <= 6 and all(mode in "GBLRTU" for mode in modes), "bounded fixture modes"
    )
    need(type(repeats) is int and repeats in (1, 2), "bounded fixture repetitions")
    need(
        type(residue_bits) is int and 2 <= residue_bits <= 128 and short in (0, 1),
        "bounded fixture word/quota",
    )
    need(
        type(literal) is bool
        and (
            not literal or (set(modes) <= {"B"} and residue_bits == 3 and repeats == 1)
        ),
        "literal GL64 fixture uses binary modes, three residue bits and one call",
    )
    need(
        len(warm) == 4 and all(type(k) is int and 1 <= k <= 1024 for k in warm),
        "four bounded entry tape extents",
    )
    index_bits = 6 * (depth + 1) + 2 if literal else max(8, 6 * depth + 2)
    limits = list(capacities(depth, index_bits, residue_bits))
    limits[2] -= short
    return limits


def execute(
    predecessor,
    modules,
    modes,
    residue_bits,
    *,
    literal=False,
    short=0,
    warm=(1, 1, 1, 1),
    repeats=1,
    total_quota=None,
):
    limits = fixture_limits(modes, residue_bits, literal, short, warm, repeats)
    depth = len(modes)
    collected = []
    census, weight = predecessor.Census, modules[2].Callback.weight
    original_bound = predecessor.bound

    def warm_bound(h, i, r):
        live, backing = original_bound(h, i, r)
        # Extend only the predecessor fixture's fresh-entry acceptance to our
        # explicit warm-entry theorem. The literal scientific code is unchanged.
        return live, max(
            backing, sum(max(k, c) for k, c in zip(warm, limits, strict=True))
        )

    def repeated(callback, coordinate):
        for _ in range(repeats - 1):
            result = weight(callback, coordinate)
            callback.residue.free(result)
            need(
                callback.pending.empty() and callback.values.empty(),
                "repeat entry restored",
            )
        return weight(callback, coordinate)

    predecessor.Census = observer_type(
        predecessor, limits, collected, warm, total_quota
    )
    predecessor.bound = warm_bound
    modules[2].Callback.weight = repeated
    try:
        result = (
            predecessor.literal_case(modules, depth)
            if literal
            else predecessor.run_case(modules, modes, residue_bits)
        )
    finally:
        predecessor.Census = census
        predecessor.bound = original_bound
        modules[2].Callback.weight = weight
    need(len(collected) == 1, "one private callback census")
    observed = collected[0]
    return observation(result, observed, modes, literal, repeats, original_bound)


def observation(result, observed, modes, literal, repeats, original_bound):
    return {
        "modes": modes,
        "I": result["I"],
        "R": result["R"],
        "literal_gl64": literal,
        "repeats": repeats,
        "entry": observed.entry,
        "lengths": observed.lengths,
        "limits": observed.limits,
        "backing": observed.backing_peak,
        "bound": sum(observed.limits),
        "old_bound": original_bound(len(modes), result["I"], result["R"])[1],
        "live_peak": observed.peak,
        "writes": observed.writes,
        "pops": observed.pops,
    }


def controls(predecessor, modules):
    rejected = []
    for name, options in (
        ("one_value_cell_short", {"short": 1}),
        ("live_content_used_as_backing", {"total_quota": 112}),
        ("warm_history_omitted", {"warm": (500, 70, 90, 40), "total_quota": 214}),
    ):
        try:
            execute(predecessor, modules, "BB", 3, **options)
        except ValueError as error:
            need("tape capacity" in str(error), "actual quota rejection")
            rejected.append(name)
        else:
            raise ValueError("invalid capacity accepted: " + name)
    need(
        execute(predecessor, modules, "BB", 3)["backing"] == 166,
        "observer methods restored after entry rejection",
    )
    return rejected


def verify():
    predecessor = authenticate()
    modules = predecessor.load_source()
    cases = []
    for depth in range(4):
        for modes in itertools.product("GBLRTU", repeat=depth):
            for bits in (4, 32):
                cases.append(execute(predecessor, modules, "".join(modes), bits))
    for depth in (4, 5, 6):
        for bits in (4, 128):
            cases.append(execute(predecessor, modules, "B" * depth, bits))
    sharp = [
        c
        for c in cases
        if (not c["modes"] or set(c["modes"]) == {"B"}) and 2 * c["I"] + 4 >= c["R"] + 3
    ]
    need(
        all(c["lengths"] == c["limits"] for c in sharp),
        "sharp request-dominant envelope",
    )
    literal = [
        execute(predecessor, modules, "B" * h, 3, literal=True) for h in range(3)
    ]
    need(literal[2]["lengths"] == (145, 44, 19, 6), "literal GL64 depth-two backing")
    repeated = execute(predecessor, modules, "BB", 4, repeats=2)
    warm = execute(predecessor, modules, "BB", 4, warm=(500, 70, 90, 40), repeats=2)
    need(warm["lengths"] == (500, 70, 90, 40), "warm backing retained through reuse")
    return {
        "status": "PASS_SELECTED_CONTINUATION_BACKING",
        "source_head": HEAD,
        "synthetic_cases": len(cases),
        "sharp_cases": len(sharp),
        "observed_writes": sum(c["writes"] for c in cases),
        "largest_binary": [c for c in cases if c["modes"] == "BBBBBB"],
        "literal_gl64": literal,
        "repeated": repeated,
        "warm": warm,
        "controls": controls(predecessor, modules),
        "scope": "Four continuation arrays; successful private weight calls. No complete reserve or supplier admission.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = verify()
    if not args.emit:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        need(
            json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "fixed typed receipt",
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
