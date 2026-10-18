# SPDX-License-Identifier: Apache-2.0
"""Bind the physical forward A13 operands and execute its guarded bit ADD."""

import argparse
import gzip
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import bit_audit
import fanout
from native_audit import run as native_audit
from operators import (
    ZERO,
    N,
    Q,
    apply,
    closed_source,
    digest,
    group,
    need,
    real_rows,
    signature,
)
from vendor import kernel

HERE = Path(__file__).resolve().parent
MAX_BYTES = 8_000_000


def read(path):
    need(path.is_file() and not path.is_symlink(), "regular input")
    need(path.stat().st_size <= MAX_BYTES, "bounded input")
    raw = path.read_bytes()
    if path.suffix == ".gz":
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
            raw = stream.read(MAX_BYTES + 1)
    need(len(raw) <= MAX_BYTES, "bounded decoded input")
    return json.loads(raw)


def authenticate(package=HERE):
    records = read(package / "VENDOR.json")["files"]
    need(
        len(records) == 10 and len({r["path"] for r in records}) == 10,
        "source inventory",
    )
    for row in records:
        path = package / row["path"]
        need(path.resolve().is_relative_to(package), "contained source")
        need(path.is_file() and not path.is_symlink(), "regular source")
        need(path.stat().st_size <= MAX_BYTES, "source size")
        need(
            hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "source hash",
        )
    return len(records)


def check_emitted(events, canonical):
    need(type(events) is list and len(events) <= 30_000, "bounded native events")
    start = events.index(["phase", "A"])
    expected = [["phase", "A"]]
    for e in canonical["A"][:12]:
        need(
            e[0] == "scale" and e[2:4] == [1, 1] and e[-1] == 0,
            "initial identity scales",
        )
        expected.append(["scalar", ["scale", ["L", e[1]], 1, 1], 0])
    expected.append(["warp", ["L", 83], 52, 85, 136])
    for role in (126, 153, 164, 218):
        expected.append(["climb", "A", role, 0, 136, 1])
        expected.append(["scalar", ["add", ["L", role], ["L", 83], -1, 2], 136])
    expected.append(["warp", ["L", 83], -52, 136, 85])
    need(
        events[start : start + len(expected)] == expected,
        "literal emitted paid group chronology",
    )


def transport(provider, work):
    output = work / provider
    env = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPYCACHEPREFIX=str(work / "pycache"),
    )
    for key in ("PYTHONOPTIMIZE", "PYTHONPATH"):
        env.pop(key, None)
    stages = (
        ("bw_transport.py", [HERE / f"vendor/WORD-{provider}.json.gz", output]),
        ("bw_emit.py", [output]),
    )
    for script, args in stages:
        with (work / f"{provider}-{script}.log").open("x") as log:
            subprocess.run(
                [
                    sys.executable,
                    "-W",
                    "error",
                    "-B",
                    str(HERE / "vendor" / script),
                    *map(str, args),
                ],
                env=env,
                cwd=work,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
                timeout=90,
            )
    canonical = read(output / "CANONICAL-WORD.json.gz")
    check_emitted(read(output / "LOCAL-PROGRAMS.json.gz")["forward"], canonical)
    return canonical


def inputs(precision, kind, rows):
    need(type(precision) is int and 1 <= precision <= 251, "input precision")
    bound = 2 ** (precision - 1)
    state = {r: [ZERO] * N for r in (83, 126, 127, 153, 154, 164, 165, 217, 218)}
    if kind in ("quarter", "norm"):
        terms = [next(term for term in rows[0] if term[3].denominator == 4)]
        if kind == "norm":
            terms = rows[0]
        for role, x, component, q in terms:
            value = 1 if kind == "quarter" else (bound - 1) * (1 if q > 0 else -1)
            old = list(state[role][x])
            old[component] = Q(value)
            state[role][x] = tuple(old)
    else:
        need(kind in ("zero", "dense", "negative"), "fixture kind")
        for role in state:
            for x in range(N):
                a = ((x * 37 + role * 19) % (2 * bound)) - bound
                b = ((x * 11 + role * 29) % (2 * bound)) - bound
                state[role][x] = {
                    "zero": ZERO,
                    "negative": (Q(-bound), Q(-bound)),
                    "dense": (Q(a), Q(b)),
                }[kind]
    return state


def operands(state, preparation, target, source):
    targets = []
    for row in preparation.values():
        vector = [
            tuple(
                sum((q * state[r][x][c] for r, q in row.items()), Q(0)) for c in (0, 1)
            )
            for x in range(N)
        ]
        targets.append(apply(target, vector))
    return targets, apply(source, state[83])


def program(width, shared, work):
    circuit = fanout.build(width, shared)
    if not shared:
        original = kernel.build(width, 1, -1, "wired")
        mapped = []
        for j in range(4):
            wires = (
                tuple(range(width))
                + tuple(range((j + 1) * width, (j + 2) * width))
                + (5 * width,)
            )
            mapped.extend(tuple(wires[i] for i in gate) for gate in original.gates)
        need(circuit.gates == tuple(mapped), "literal PR3081 separate-call baseline")
    document = {
        "width": width,
        "shared": shared,
        "wires": circuit.wires,
        "gates": [list(g) for g in circuit.gates],
    }
    path = work / f"ADD-{width}-{shared}.json"
    raw = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
    with path.open("xb") as stream:
        need(stream.write(raw) == len(raw), "complete circuit write")
    decoded = read(path)
    need(decoded == document, "serialized circuit readback")
    literal = fanout.Circuit(width, shared, tuple(map(tuple, decoded["gates"])))
    return literal, bit_audit.parse(decoded), digest(document)


def execute_case(programs, state, preparation, target, source):
    targets, sources = operands(state, preparation, target, source)
    output = []
    for x in range(N):
        pair = []
        for c in (0, 1):
            ts, s = tuple(t[x][c] for t in targets), sources[x][c]
            need(
                all((4 * t).denominator == 1 for t in ts) and s.denominator == 1,
                "physical input grids",
            )
            encoded_t, encoded_s = tuple(int(4 * t) for t in ts), int(4 * s)
            after = []
            for circuit, independent, _ in programs:
                after.append(fanout.check(circuit, encoded_s, encoded_t))
                bit_audit.check(independent, encoded_s, encoded_t)
            need(
                after[0] == after[1], "shared and separate complete bit-state equality"
            )
            words, carry = fanout.observe(programs[0][0], after[0])
            need(
                carry == 0
                and tuple(Q(v, 4) for v in words[1:]) == tuple(t - s / 2 for t in ts),
                "physical target identity",
            )
            pair.append([str(Q(v, 4)) for v in words[1:]])
        output.append(pair)
    return output


def check_cases(preparation, target, source, rows, work):
    result = []
    for precision in (3, 5, 64):
        programs = [program(precision + 5, shared, work) for shared in (True, False)]
        circuit, cases = programs[0][0], {}
        for kind in ("zero", "quarter", "norm", "dense", "negative"):
            state = inputs(precision, kind, rows)
            output = execute_case(programs, state, preparation, target, source)
            cases[kind] = digest(output)
            observed = Q(output[0][0][0])
            if kind == "quarter":
                need(observed == Q(1, 4), "physical quarter witness")
            if kind == "norm":
                need(
                    observed == Q(9, 2) * (2 ** (precision - 1) - 1),
                    "attained row norm",
                )
                if precision == 5:
                    need(4 * observed == 270 > 255, "one-less-width failure")
        invoice, baseline = fanout.invoice(circuit), fanout.invoice(programs[1][0])
        need(
            baseline["cx"] - invoice["cx"] == 6 and baseline["ccx"] == invoice["ccx"],
            "complete local saving",
        )
        result.append(
            {
                "input_bits": precision,
                "width": circuit.width,
                "circuit_sha256": programs[0][2],
                "baseline_circuit_sha256": programs[1][2],
                "cases": cases,
                "component_calls": 5 * 2 * N,
                "add_layer_cx": 2 * N * invoice["cx"],
                "add_layer_ccx": 2 * N * invoice["ccx"],
                "baseline_cx": 2 * N * baseline["cx"],
                "saved_cx": 12 * N,
                "array_bits_plus_one_reused_carry": 10 * N * circuit.width + 1,
            }
        )
    return result


def run(work):
    pins = authenticate()
    providers = {}
    for provider in ("base", "extra"):
        preparation, g, target, source = group(transport(provider, work))
        row_sets = {r: real_rows(p, target, source) for r, p in preparation.items()}
        rows = row_sets[126]
        hashes = {
            "source": digest(signature(source)),
            "target": digest(signature(target)),
            "closed_source": digest(signature(closed_source(g, target, source))),
        }
        need(
            native_audit(g) == hashes, "all 512 native Gaussian columns including phase"
        )
        providers[provider] = hashes
    need(providers["base"] == providers["extra"], "same physical A13 boundary")
    return {
        "status": "PASS_PHYSICAL_A13_LOCAL_BOUNDARY_NOT_SUPPLIER_ADMISSION",
        "source_files": pins,
        "providers": providers,
        "prepared_target_rows": {
            str(r): {str(i): str(q) for i, q in sorted(row.items())}
            for r, row in preparation.items()
        },
        "physical_source_grid": "Z[i]",
        "physical_target_grid": "1/4 Z[i]",
        "component_row_norm": "9/2",
        "real_rows": sum(map(len, row_sets.values())),
        "quarter_witness": {
            "input": [126, 0, 0],
            "output": [126, 0, 0],
            "value": "1/4",
        },
        "width_witness": {
            "input_bits": 5,
            "encoded_output": 270,
            "one_less_width_max": 255,
        },
        "fraction_bits": 2,
        "sufficient_width": "P+5",
        "rank_one_target_climbs_still_charged": 4,
        "bit_cases": check_cases(preparation, target, source, rows, work),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.work:
        need(not args.work.exists(), "fresh work directory")
        need(
            not args.work.resolve().is_relative_to(HERE.parents[1]),
            "external work directory",
        )
        args.work.mkdir(parents=True)
        result = run(args.work.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="rank7-physical-a13-") as directory:
            result = run(Path(directory))
    expected = HERE / "RESULT.json"
    if args.write:
        with expected.open("x") as stream:
            raw = json.dumps(result, sort_keys=True, indent=2) + "\n"
            need(stream.write(raw) == len(raw), "complete evidence write")
    else:
        need(read(expected) == result, "deterministic complete receipt")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
