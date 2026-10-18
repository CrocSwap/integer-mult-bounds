"""Read-only exact audit of the rounded-pair Boolean construction.

New material: Nick Petalas, Apache-2.0. No predecessor executable is imported.
"""

import argparse
import hashlib
import itertools
import json
import random
import sys
from collections import Counter
from dataclasses import replace
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from circuit import MAX_WIDTH, compile_pair, evaluate, gate_count, require, run  # noqa: E402


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    require(path.is_file() and not path.is_symlink(), "missing regular artifact")
    require(path.stat().st_size <= 100000, "artifact byte capacity")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def authenticate():
    pins = read_json(PACKAGE / "PREDECESSOR.json")
    require(type(pins) is dict and len(pins.get("files", [])) == 2, "source inventory")
    names = {"source/FORMAT-README.md", "source/format-verify.py"}
    require({row["local"] for row in pins["files"]} == names, "source names")
    for row in pins["files"]:
        path = PACKAGE / row["local"]
        require(path.is_file() and not path.is_symlink(), "missing source")
        require(path.stat().st_size <= 40000, "source byte capacity")
        data = path.read_bytes()
        require(len(data) <= 40000, "source byte capacity")
        require(
            hashlib.sha256(data).hexdigest() == row["sha256"], "source hash mismatch"
        )
        blob = hashlib.sha1(
            b"blob " + str(len(data)).encode() + b"\0" + data
        ).hexdigest()
        require(blob == row["git_blob"], "source Git blob mismatch")
    return pins["head"]


def oracle(values, sign, scale):
    """Direct signed-magnitude rational nearest-even, independent of bit logic."""
    a, b, c, d = values
    numerators = (
        a + c - sign * b + sign * d,
        b + d + sign * a - sign * c,
        a + c + sign * b - sign * d,
        b + d - sign * a + sign * c,
    )
    divisor = 1 << (scale + 1)
    result = []
    for value in numerators:
        quotient, remainder = divmod(abs(value), divisor)
        if 2 * remainder > divisor or 2 * remainder == divisor and quotient % 2:
            quotient += 1
        result.append((-quotient if value < 0 else quotient) << scale)
    return tuple(result)


def masks(rows, width):
    """Transpose bounded signed integer tuples into bit-sliced truth tables."""
    count = len(rows)
    require(1 <= count <= 65536 and 1 <= width <= 6, "exhaustive matrix capacity")
    buffers = [bytearray((count + 7) // 8) for _ in range(4 * width)]
    for index, row in enumerate(rows):
        byte, offset = divmod(index, 8)
        for component, value in enumerate(row):
            for bit in range(width):
                buffers[component * width + bit][byte] |= ((value >> bit) & 1) << offset
    return [int.from_bytes(buffer, "little") for buffer in buffers]


def exhaustive():
    assignments, circuits = 0, 0
    for width in range(1, 5):
        half = 1 << (width - 1)
        rows = list(itertools.product(range(-half, half), repeat=4))
        inputs, count = masks(rows, width), len(rows)
        ones = (1 << count) - 1
        for sign in (-1, 1):
            runtime = compile_pair(width, sign)
            circuits += 1
            for scale in range(width + 1):
                expected_rows = [oracle(row, sign, scale) for row in rows]
                expected_bits = masks(expected_rows, width + 2)
                expected = tuple(
                    tuple(expected_bits[j : j + width + 2])
                    for j in range(0, 4 * (width + 2), width + 2)
                )
                fixed = compile_pair(width, sign, scale)
                controls = [
                    ones if (scale >> i) & 1 else 0 for i in range(width.bit_length())
                ]
                require(
                    evaluate(runtime, inputs + controls, count) == expected,
                    "runtime truth table",
                )
                require(evaluate(fixed, inputs, count) == expected, "fixed truth table")
                assignments += count
                circuits += 1
    require(assignments == 689728 and circuits == 36, "complete truth domain")
    return {"pair_assignments_each_variant": assignments, "literal_circuits": circuits}


def wide_checks():
    generator = random.Random(620107)
    cases = 0
    for width in (8, 16, 64, 453, 1024):
        half = 1 << (width - 1)
        rows = [
            (-half, -half, -half, -half),
            (half - 1,) * 4,
            (-half, half - 1, half - 1, -half),
            (-1, 0, 1, -1),
        ]
        rows += [
            tuple(generator.randrange(-half, half) for _ in range(4)) for _ in range(4)
        ]
        for sign in (-1, 1):
            runtime = compile_pair(width, sign)
            for scale in sorted({0, 1, width // 2, width}):
                fixed = compile_pair(width, sign, scale)
                for row in rows:
                    expected = oracle(row, sign, scale)
                    require(
                        run(runtime, row, scale) == expected, "wide runtime arithmetic"
                    )
                    require(run(fixed, row, scale) == expected, "wide fixed arithmetic")
                    require(
                        all(
                            -(1 << (width + 1)) <= v < 1 << (width + 1)
                            for v in expected
                        ),
                        "output range",
                    )
                    cases += 1
    require(cases == 320, "wide case count")
    return cases


def changed_gate(circuit, index, gate):
    gates = list(circuit.gates)
    gates[index] = gate
    return replace(circuit, gates=tuple(gates))


def semantic_controls():
    fixed = compile_pair(4, 1, 0)
    runtime = compile_pair(4, 1)
    start = 44 * 6
    zero_extension_gate = 5 * 4
    gate = fixed.gates[zero_extension_gate]
    controls = [
        (
            "ties forced upward",
            changed_gate(fixed, start, ("OR", 0, 1)),
            (1, 0, 0, 0),
            0,
        ),
        (
            "sticky omitted",
            changed_gate(runtime, start + 1, ("AND", 0, 0)),
            (3, 0, 0, 0),
            1,
        ),
        (
            "signed extension omitted",
            changed_gate(fixed, zero_extension_gate, (gate[0], 0, gate[2])),
            (-8, 0, 0, 0),
            0,
        ),
        ("adder XOR removed", changed_gate(fixed, 0, ("AND", 0, 0)), (3, 0, 0, 0), 0),
        (
            "runtime shift select omitted",
            changed_gate(runtime, start + 3, ("AND", 0, 0)),
            (6, 0, 0, 0),
            1,
        ),
        ("wrong native sign", compile_pair(4, -1), (3, 2, -1, 0), 0),
    ]
    for name, circuit, row, scale in controls:
        require(
            run(circuit, row, scale) != oracle(row, 1, scale),
            "ineffective control: " + name,
        )
    return [row[0] for row in controls]


def boundary_controls():
    rejected = 0
    for width, sign, scale in (
        (0, 1, None),
        (MAX_WIDTH + 1, 1, None),
        (True, 1, None),
        (4, True, None),
        (4, 0, None),
        (4, 1, -1),
        (4, 1, 5),
        (4, 1, True),
    ):
        try:
            compile_pair(width, sign, scale)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid circuit accepted")
    circuit = compile_pair(4, 1)
    for row, scale in (
        ((8, 0, 0, 0), 0),
        ((-9, 0, 0, 0), 0),
        ((0, 0, 0, 0), 5),
        ((False, 0, 0, 0), 0),
    ):
        try:
            run(circuit, row, scale)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("invalid arithmetic input accepted")
    return rejected


def invoice():
    rows = []
    for width in (1, 4, 64, 453, 1024):
        circuit = compile_pair(width, 1)
        counts = dict(sorted(Counter(g[0] for g in circuit.gates).items()))
        rows.append(
            {
                "input_bits": width,
                "output_bits": width + 2,
                "scale_bits": width.bit_length(),
                "gates": len(circuit.gates),
                "by_gate": counts,
            }
        )
        require(sum(counts.values()) == gate_count(width), "gate-kind invoice")
    require(rows[3]["gates"] == 124028, "consumed 456-bit format example")
    return {
        "runtime_examples": rows,
        "example_pair_evaluations_coefficient": 336 * 124028 // 2,
        "example_fixed_max_gates": gate_count(453, 0),
    }


def result():
    head = authenticate()
    return {
        "status": "PASS_QQ16_ROUNDED_PAIR_BIT_CIRCUIT",
        "source_head": head,
        "truth_tables": exhaustive(),
        "wide_signed_cases_each_variant": wide_checks(),
        "semantic_controls": semantic_controls(),
        "boundary_rejections": boundary_controls(),
        "invoice": invoice(),
        "scope": "irreversible arithmetic gates; no scan, routing, tape or supplier tariff",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="create a missing RESULT.json exclusively"
    )
    args = parser.parse_args()
    actual = result()
    canonical = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    if args.write:
        with (PACKAGE / "RESULT.json").open("x", encoding="utf-8") as stream:
            require(stream.write(canonical) == len(canonical), "short receipt write")
    else:
        expected = read_json(PACKAGE / "RESULT.json")
        require(
            json.dumps(expected, sort_keys=True) == json.dumps(actual, sort_keys=True),
            "receipt mismatch",
        )
    print(
        actual["status"],
        "pair_assignments=689728",
        "wide_cases=320",
        "runtime_example_gates=124028",
    )


if __name__ == "__main__":
    main()
