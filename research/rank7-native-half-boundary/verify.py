# SPDX-License-Identifier: Apache-2.0
"""Bind the A13 native conversion, exact grid and attained range."""

import argparse
import hashlib
import json
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path

from boundary import (
    DIM,
    component,
    evaluate,
    matrix,
    output_rows,
    require,
    summary,
    witnesses,
)
from vendor import bitadder
from vendor import clifford as C

PACKAGE = Path(__file__).resolve().parent


def load_parent():
    sys.path.insert(0, str(PACKAGE / "vendor/parent"))
    import replay_parent as inherited
    from contractions import produce
    from tariff import produce as parent

    inherited.check_pins()
    return inherited, produce, parent


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def authenticate():
    records = json.loads((PACKAGE / "VENDOR.json").read_text())["files"]
    actual = {
        p.relative_to(PACKAGE).as_posix()
        for p in (PACKAGE / "vendor").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    require(actual == {r["path"] for r in records}, "complete frozen inventory")
    for record in records:
        path = PACKAGE / record["path"]
        require(
            not path.is_symlink() and path.stat().st_size <= 8_000_000,
            "bounded regular source",
        )
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
            "frozen source bytes",
        )
    return len(records)


def logical_warp(columns):
    """K_G = P(G), then D(I + G^-T G^-1), exactly as retained BW semantics."""
    require(len(columns) == 9, "nine warp columns")
    require(all(type(x) is int and 0 <= x < DIM for x in columns), "valid warp columns")
    rows = C.transpose(columns)
    inverse_columns = C.transpose(C.f2_inverse(rows))
    quad = [
        (1 << i)
        ^ sum(((a & b).bit_count() % 2) << j for j, b in enumerate(inverse_columns))
        for i, a in enumerate(inverse_columns)
    ]
    linear = [(quad[i] >> i) & 1 for i in range(9)]
    return [("P", rows), ("D", quad, linear)]


def prefix_rows(events):
    require(len(events) <= 30_000, "bounded scalar prefix")
    rows = {r: {(r, ()): Q(1)} for r in range(632)}
    for event in events:
        if event[0] == "scalar":
            gate = event[1]
            require(gate[0] in ("add", "scale"), "ordinary invertible prefix scalar")
            require(gate[1][0] == "L", "ordinary prefix target")
            t = gate[1][1]
            if gate[0] == "scale":
                rows[t] = {a: q * Q(gate[2], gate[3]) for a, q in rows[t].items()}
            else:
                require(gate[2][0] == "L", "ordinary prefix source")
                require(t != gate[2][1], "distinct prefix ADD operands")
                for a, q in rows[gate[2][1]].items():
                    rows[t][a] = rows[t].get(a, Q(0)) + q * Q(gate[3], gate[4])
                rows[t] = {a: q for a, q in rows[t].items() if q}
        elif event[0] == "warp":
            require(event[1][0] == "L", "ordinary prefix warp")
            t, op = event[1][1], event[2]
            require(type(op) is int and op != 0, "nonzero warp symbol")
            rows[t] = {
                (a, w[1:] if w and w[0] == -op else (op, *w)): q
                for (a, w), q in rows[t].items()
            }
        else:
            require(
                event[0] in ("phase", "adapter", "residual_adapter"),
                "declared prefix conversion",
            )
        if event[0] in ("scalar", "warp"):
            require(len(rows[t]) <= 4096, "bounded prefix support")
            require(all(len(w) <= 256 for _, w in rows[t]), "bounded prefix warp words")
    return rows


def bind(canonical_word, events):
    require(len(events) <= 30_000, "bounded emitted stream")
    require(canonical_word["A"][12] == ["warp", 83, 52, 85, 136], "literal A12 warp")
    require(canonical_word["A"][13] == ["add", 126, 83, -1, 2, 136], "literal A13 ADD")
    frames = canonical_word["frames"]
    require(
        frames[0] == [] and frames[85] == [382] and frames[136] == [45],
        "actual frame bases",
    )
    start = events.index(["phase", "A"])
    expected = [
        ["warp", ["L", 83], 52, 85, 136],
        ["climb", "A", 126, 0, 136, 1],
        ["scalar", ["add", ["L", 126], ["L", 83], -1, 2], 136],
    ]
    require(events[start + 13 : start + 16] == expected, "adjacent emitted boundary")
    rows = prefix_rows(events[: start + 13])
    require(rows[83] == {(83, ()): 1}, "unmodified normalized source")
    target = {
        (r, ()): Q(sign, 2) for r, sign in ((126, 1), (127, -1), (164, 1), (165, -1))
    }
    require(rows[126] == target, "actual normalized dirty target prefix")
    warp = [w for w in canonical_word["warps"] if w["op"] == 52]
    require(len(warp) == 1, "unique warp52")
    return warp[0]["G_columns"], start + 15


def integer_check(circuit, rational):
    """Compare all columns against the retained packed-integer Clifford engine."""
    depth = C.c_gates(circuit)
    beta = C.radix(depth)
    columns = C.columns(C.run(circuit, beta), beta)
    for y, row in enumerate(rational):
        expected = {
            x: (Q(col[y][0], 2**depth), Q(col[y][1], 2**depth))
            for x, col in columns.items()
            if y in col
        }
        require(row == expected, "independent integer/Fraction operator equality")
    return digest(
        [[[x, str(a), str(b)] for x, (a, b) in sorted(row.items())] for row in rational]
    )


def internal_formats(old, new, warp, precision):
    source_trace, target_trace = [], []
    matrix(warp, matrix(old), source_trace)
    target = [
        {
            field * DIM + x: (Q(sign, 2), Q(0))
            for field, sign in enumerate((1, -1, 1, -1))
        }
        for x in range(DIM)
    ]
    matrix(new, target, target_trace)
    result = {}
    for name, trace in (("source", source_trace), ("target", target_trace)):
        result[name] = []
        for index, kind, rows in trace:
            report = summary(
                [component(row, im) for row in rows for im in (False, True)], precision
            )
            require(report["fractional_bits"] <= 2, "local internal grid")
            # Summary uses the smallest grid of this stage. Compare at common D2.
            low, high = Q(report["low"]) * 4, Q(report["high"]) * 4
            require(
                -(1 << (precision + 4)) <= low <= high < (1 << (precision + 4)),
                "local internal signed range",
            )
            result[name].append(dict(gate=index, kind=kind, **report))
    return result


def literal_half_add(final, source, fixtures, width):
    checked = {}
    for side in ("low", "high"):
        witness = fixtures[side]
        index = witness["row"]
        assignment = dict(witness["assignment"])
        before = {a: q for a, q in final[index].items() if a < 4 * 2 * DIM}
        source_row = {
            4 * 2 * DIM + a: q
            for a, q in component(source[index // 2], bool(index % 2)).items()
        }
        target_value = evaluate(before, assignment) * 4
        source_value = evaluate(source_row, assignment) * 4
        require(
            source_value.denominator == target_value.denominator == 1,
            "actual integer caller operands",
        )
        observed = bitadder.execute(width, -1, 2, int(source_value), int(target_value))
        require(
            str(observed) == witness["encoded"], "literal physical-boundary ADD result"
        )
        try:
            bitadder.execute(width - 1, -1, 2, int(source_value), int(target_value))
        except ValueError as error:
            require(
                "signed endpoint range" in str(error),
                "undersized caller endpoint rejection",
            )
        else:
            raise ValueError("undersized physical caller accepted")
        checked[side] = {
            "source": str(source_value),
            "target": str(target_value),
            "output": observed,
        }
    gates = bitadder.circuit(width, -1, 2)
    return {
        "fixtures": checked,
        "source_preserved": True,
        "clean_carries_returned": width - 1,
        "gates_per_real_component": len(gates),
        "components": 1024,
        "sequential_ADD_layer_gates": 1024 * len(gates),
    }


def monomial_counts(rows):
    units = {"1": (1, 0), "-1": (-1, 0), "i": (0, 1), "-i": (0, -1)}
    require(
        all(
            len(row) == 1 and next(iter(row.values())) in units.values() for row in rows
        ),
        "physical warp is a Gaussian monomial",
    )
    require(len({next(iter(row)) for row in rows}) == DIM, "physical warp bijection")
    counts = {
        name: sum(next(iter(row.values())) == value for row in rows)
        for name, value in units.items()
    }
    require(
        counts == {"1": 144, "-1": 112, "i": 128, "-i": 128},
        "actual physical warp phases",
    )
    return counts


def analyze(columns, precision=64):
    old, new = C.canonical_frame([382]), C.canonical_frame([45])
    logical = logical_warp(columns)
    warp = C.adjoint(old) + logical + new
    physical = matrix(warp)
    phase_counts = monomial_counts(physical)
    require(not C.same_operator(warp, logical), "physical warp differs from logical K")
    frame, source = matrix(new), matrix(logical + new)
    require(
        C.same_operator(old + warp, logical + new), "native source commuting square"
    )
    for circuit, rows in ((new, frame), (logical + new, source), (warp, physical)):
        integer_check(circuit, rows)
    final = output_rows(frame, source)
    result = summary(final, precision)
    limit = 1 << (precision - 1)
    require(
        result
        == {
            "fractional_bits": 2,
            "max_norm": "5",
            "low": str(-5 * limit + Q(9, 4)),
            "high": str(5 * limit - Q(9, 4)),
            "signed_width": precision + 5,
        },
        "sharp native format",
    )
    source_rows = [component(row, im) for row in source for im in (False, True)]
    require(
        all(
            (q * 4).denominator == 1 and int(q * 4) % 2 == 0
            for row in source_rows
            for q in row.values()
        ),
        "every encoded source is even",
    )
    fixtures = witnesses(final, precision, result)
    return {
        "input_precision": precision,
        "native": result,
        "witnesses": fixtures,
        "source": summary(source_rows, precision),
        "physical_warp_sha256": integer_check(warp, physical),
        "frame_sha256": integer_check(new, frame),
        "source_sha256": integer_check(logical + new, source),
        "internal_formats": internal_formats(old, new, warp, precision),
        "literal_half_ADD": literal_half_add(final, source, fixtures, precision + 5),
        "all_columns": 512,
        "aligned_half_add": True,
        "physical_warp_phases": phase_counts,
    }


def run(work):
    pins = authenticate()
    inherited, produce, parent = load_parent()
    results = {}
    for provider in ("base", "extra"):
        raw = inherited.read(PACKAGE / f"vendor/parent/vendor/WORD-{provider}.json.gz")
        word = produce(
            parent(raw), inherited.read(PACKAGE / "vendor/parent/EDITS.json")
        )
        programs, checks = inherited.compile_word(word, work / provider)
        canonical_word = inherited.read(
            work / provider / "native/CANONICAL-WORD.json.gz"
        )
        columns, event = bind(canonical_word, programs["forward"])
        results[provider] = {
            "event": event,
            "program_sha256": digest(programs["forward"]),
            "native_checks": checks,
            "columns": columns,
            "boundary": analyze(columns),
        }
    return {
        "status": "PASS_LOCAL_NATIVE_BOUNDARY_NOT_SUPPLIER_ADMISSION",
        "frozen_files": pins,
        "providers": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()
    if args.work:
        work = args.work.expanduser().resolve()
        require(
            not work.exists() and not work.is_relative_to(PACKAGE.parents[1]),
            "fresh external output path",
        )
        work.mkdir(parents=True)
        result = run(work)
    else:
        with tempfile.TemporaryDirectory(prefix="rank7-native-boundary-") as directory:
            result = run(Path(directory))
    expected = PACKAGE / "RESULT.json"
    if expected.exists():
        require(
            result == json.loads(expected.read_text()),
            "committed deterministic receipt",
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
