# SPDX-License-Identifier: Apache-2.0
"""Reconstruct both native streams and certify their formal scalar formats."""

import argparse
import hashlib
import json
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path

from check_integer import check as integer_check
from rows import canonical, require, summarize, triangle_bound

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE / "vendor/parent"))
sys.path.insert(0, str(PACKAGE / "vendor"))
import replay_parent as inherited
from bitadder import execute
from contractions import produce
from tariff import produce as parent


def authenticate(package=PACKAGE):
    package = package.resolve()
    records = json.loads((package / "VENDOR.json").read_text())["files"]
    require(len(records) == 19, "complete frozen inventory")
    actual = {
        p.relative_to(package).as_posix()
        for p in (package / "vendor").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    require(actual == {r["path"] for r in records}, "no unpinned vendor files")
    for record in records:
        path = package / record["path"]
        require(
            not path.is_symlink() and path.resolve().is_relative_to(package),
            "source path",
        )
        require(path.stat().st_size <= 8_000_000, "bounded source input")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
            "frozen source bytes: " + record["path"],
        )
    inherited.check_pins()
    return len(records)


def decode(row):
    return {(v, tuple(w)): Q(a, b) for v, w, a, b in row}


def evaluate(row, assignment):
    return sum((q * assignment.get(atom, 0) for atom, q in row.items()), Q(0))


def independent_control(events, exact, backward):
    checked = integer_check(events, exact["fractional_bits"], backward)
    require(
        all(value == exact[key] for key, value in checked.items()),
        "separate fixed-denominator integer replay agrees",
    )
    try:
        integer_check(events, exact["fractional_bits"] - 1, backward)
    except ValueError as error:
        require(
            "exact fixed-grid divisibility" in str(error), "semantic grid rejection"
        )
    else:
        raise ValueError("undersized grid accepted")
    return dict(checked, depth_minus_one_rejected=True)


def witness_checks(summary, events, precision=64):
    """Attain formal extrema and run the corresponding literal PR3080 ADD circuit."""
    d, width = summary["fractional_bits"], summary["signed_width"]
    deepest = decode(summary["witnesses"]["depth"]["row"])
    atom, coefficient = next(
        (a, q) for a, q in deepest.items() if q.denominator == 2**d
    )
    require((coefficient * 2 ** (d - 1)).denominator == 2, "one fewer grid bit fails")
    require(evaluate(deepest, {atom: 1}) == coefficient, "basis-atom depth witness")
    outcomes = {}
    for side in ("low", "high"):
        witness = summary["witnesses"][side]
        row = decode(witness["row"])
        limit = 1 << (precision - 1)
        assignment = {
            a: (limit - 1 if (q > 0) == (side == "high") else -limit)
            for a, q in row.items()
        }
        observed = evaluate(row, assignment)
        require(observed == Q(summary[side]), "attaining signed-box endpoint")
        scaled = observed * 2**d
        require(
            not -(1 << (width - 2)) <= scaled < (1 << (width - 2)),
            "one fewer endpoint bit fails",
        )
        gate = events[witness["event"]][1]
        require(gate[0] == "add", "actual extremal ADD witness")
        source = evaluate(decode(witness["source"]), assignment) * 2**d
        target = evaluate(decode(witness["before"]), assignment) * 2**d
        require(source.denominator == target.denominator == 1, "integral caller inputs")
        q = Q(gate[3], gate[4])
        require(int(source) % q.denominator == 0, "literal source alignment")
        output = execute(width, q.numerator, q.denominator, int(source), int(target))
        require(output == scaled, "literal aligned bit-circuit endpoint")
        outcomes[side] = {
            "event": witness["event"],
            "source": str(source),
            "target": str(target),
            "output": str(output),
            "coefficient": str(q),
        }
    return {
        "depth_minus_one_rejected": True,
        "width_minus_one_rejected": True,
        "literal_bit_ADDs": outcomes,
    }


def run(work):
    pin_count = authenticate()
    result = {}
    for provider in ("base", "extra"):
        original = inherited.read(
            PACKAGE / f"vendor/parent/vendor/WORD-{provider}.json.gz"
        )
        word = produce(
            parent(original), inherited.read(PACKAGE / "vendor/parent/EDITS.json")
        )
        programs, native = inherited.compile_word(word, work / provider)
        result[provider] = {}
        for direction in ("forward", "backward"):
            events = programs[direction]
            exact = summarize(events, direction == "backward")
            control = triangle_bound(events)
            require(
                exact["signed_width"] < control["signed_width"],
                "strict format bound improvement",
            )
            checks = witness_checks(exact, events)
            result[provider][direction] = {
                "program_sha256": hashlib.sha256(canonical(events)).hexdigest(),
                "native_check": native[direction],
                "exact": exact,
                "independent_integer": independent_control(
                    events, exact, direction == "backward"
                ),
                "triangle_control": control,
                "witness_checks": checks,
            }
    return {
        "status": "PASS_FORMAL_COEFFICIENT_FORMAT_NOT_NATIVE_RANGE",
        "input_precision": 64,
        "frozen_files": pin_count,
        "providers": result,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, help="fresh external output directory")
    args = parser.parse_args()
    if args.work:
        work = args.work.expanduser().resolve()
        require(
            not work.is_relative_to(PACKAGE.parents[1]), "external output directory"
        )
        require(not work.exists(), "fresh output directory; preserve diagnostics")
        work.mkdir(parents=True)
        result = run(work)
    else:
        with tempfile.TemporaryDirectory(prefix="rank7-coefficient-grid-") as directory:
            result = run(Path(directory))
    expected = PACKAGE / "RESULT.json"
    if expected.exists():
        require(
            result == json.loads(expected.read_text()),
            "deterministic committed receipt",
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
