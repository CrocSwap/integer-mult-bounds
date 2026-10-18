# SPDX-License-Identifier: Apache-2.0
"""Source-bound native streams, explicit bit circuits and conditional tariffs."""

import argparse
import hashlib
import json
import sys
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

from bitadder import adder, circuit, require, terms
from check_bits import check_truth, decode

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE / "vendor/parent"))
sys.path.insert(0, str(PACKAGE / "vendor"))
import replay_parent as inherited  # noqa: E402
from contractions import produce  # noqa: E402
from tariff import produce as tariff_parent  # noqa: E402
from unit_lower import certify  # noqa: E402


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def authenticate(package=PACKAGE):
    package = package.resolve()
    records = json.loads((package / "VENDOR.json").read_text())["files"]
    require(len(records) == 17, "complete frozen source inventory")
    expected = {
        p.relative_to(package).as_posix()
        for p in (package / "vendor").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    require(expected == {r["path"] for r in records}, "no unpinned vendor files")
    for record in records:
        path = package / record["path"]
        require(
            not path.is_symlink() and path.resolve().is_relative_to(package),
            "source path",
        )
        require(path.stat().st_size <= 8_000_000, "bounded source")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"],
            "frozen source bytes: " + record["path"],
        )
    return len(records)


def scalar_coefficient(gate):
    kind = gate[0]
    require(kind in ("clear", "copy", "add", "scale"), "native scalar kind")
    require(kind != "add" or gate[1] != gate[2], "distinct native ADD ports")
    a, b = gate[3:5] if kind == "add" else gate[2:4] if kind == "scale" else (1, 1)
    return kind, Fraction(a, b)


def count_stream(events, width, signed):
    counts, coefficients = Counter(), Counter()
    unit_counts, recipes = Counter(), {}
    shift_total = 0
    for event in events:
        if event[0] != "scalar":
            continue
        kind, q = scalar_coefficient(event[1])
        for policy in ("scratch", "source_walk", "target_walk"):
            key = (kind, q, policy)
            if key not in recipes:
                require(len(recipes) < 384, "bounded unit recipe alphabet")
                recipes[key] = certify(kind, q.numerator, q.denominator, policy=policy)
            unit_counts[policy] += 2 * len(recipes[key])
        if kind != "add":
            continue
        coefficients[str(q)] += 2
        for _, shift in terms(q.numerator, q.denominator, signed):
            active = max(0, width - max(0, shift))
            shift_total += 2 * max(0, shift)
            counts["shifted_adds"] += 2
            counts["ccx"] += 2 * (4 * active - 6 if active >= 2 else 0)
            counts["cx"] += 2 * (4 * active - 5 if active >= 2 else active)
    return {
        "ADD_layer": dict(sorted(counts.items())),
        "ADD_layer_affine_for_width_ge_5": {
            gate: [
                4 * counts["shifted_adds"],
                -constant * counts["shifted_adds"] - 4 * shift_total,
            ]
            for gate, constant in (("ccx", 6), ("cx", 5))
        },
        "real_ADD_macros": sum(coefficients.values()),
        "coefficient_histogram": dict(sorted(coefficients.items())),
        "unit_instruction_counts": dict(sorted(unit_counts.items())),
        "program_sha256": digest(events),
        "non_ADD_sha256": digest(
            [e for e in events if e[0] != "scalar" or e[1][0] != "add"]
        ),
    }


def native_comparison(work):
    result, alphabet = {}, set()
    for provider in ("base", "extra"):
        original = inherited.read(
            PACKAGE / f"vendor/parent/vendor/WORD-{provider}.json.gz"
        )
        parent = tariff_parent(original)
        candidate = produce(
            parent, inherited.read(PACKAGE / "vendor/parent/EDITS.json")
        )
        result[provider] = {}
        for name, word in (("parent", parent), ("candidate", candidate)):
            programs, checks = inherited.compile_word(word, work / f"{provider}-{name}")
            result[provider][name] = {}
            for direction in ("forward", "backward"):
                events = programs[direction]
                binary = count_stream(events, 64, False)
                signed = count_stream(events, 64, True)
                alphabet.update(binary["coefficient_histogram"])
                result[provider][name][direction] = {
                    "binary": binary,
                    "signed": signed,
                    "native": checks[direction],
                }
        for direction in ("forward", "backward"):
            before = result[provider]["parent"][direction]["signed"]
            after = result[provider]["candidate"][direction]["signed"]
            require(
                before["non_ADD_sha256"] == after["non_ADD_sha256"],
                "all non-ADD native events stay literal",
            )
            require(
                before["ADD_layer"]["ccx"] > after["ADD_layer"]["ccx"],
                "strict Boolean tariff improvement",
            )
    return result, sorted(alphabet)


def circuit_checks(work, alphabet):
    templates, truth_cases = {}, 0
    for text in alphabet:
        q = Fraction(text)
        require(abs(q.numerator) in (1, 2, 3, 4, 5, 7, 8), "actual numerator alphabet")
        for signed in (False, True):
            key = f"{q}:signed={signed}"
            gates = circuit(64, q.numerator, q.denominator, signed=signed)
            templates[key] = gates
            for width in range(max(1, q.denominator.bit_length()), 7):
                small = circuit(width, q.numerator, q.denominator, signed=signed)
                serialized = decode(json.loads(canonical(small)))
                truth_cases += check_truth(
                    serialized, width, q.numerator, q.denominator
                )
    payload = canonical(templates)
    target = work / "CIRCUITS.json"
    require(target.write_bytes(payload) == len(payload), "complete serialized circuits")
    loaded = json.loads(target.read_bytes())
    counts = {}
    for key, raw in loaded.items():
        gates = decode(raw)
        q = Fraction(key.split(":")[0])
        signed = key.endswith("True")
        require(
            gates == circuit(64, q.numerator, q.denominator, signed=signed),
            "literal serialized circuit",
        )
        counts[key] = dict(sorted(Counter(g[0] for g in gates).items()))
    for width in range(1, 9):
        gates = decode(json.loads(canonical(adder(width, 0))))
        truth_cases += check_truth(gates, width, 1, 1)
        truth_cases += check_truth(list(reversed(gates)), width, -1, 1)
    return {
        "width": 64,
        "sha256": digest(loaded),
        "templates": counts,
        "exhaustive_assignments": truth_cases,
        "carry_bits": 63,
        "temporary_source_or_target_guard_bits": 0,
    }


def run(work):
    pins = authenticate()
    inherited.check_pins()
    native, alphabet = native_comparison(work)
    bits = circuit_checks(work, alphabet)
    for providers in native.values():
        for word in providers.values():
            for orientation in word.values():
                for policy in ("binary", "signed"):
                    row = orientation[policy]
                    for gate in ("cx", "ccx"):
                        literal = sum(
                            count
                            * bits["templates"][f"{q}:signed={policy == 'signed'}"].get(
                                gate, 0
                            )
                            for q, count in row["coefficient_histogram"].items()
                        )
                        require(
                            literal == row["ADD_layer"][gate],
                            "complete tariff from serialized literal circuits",
                        )
    return {
        "status": "PASS_CONDITIONAL_ALIGNED_ADD_LAYER_NOT_SUPPLIER_ADMISSION",
        "frozen_files": pins,
        "width": 64,
        "alphabet": alphabet,
        "circuits": bits,
        "streams": native,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()
    if args.work:
        require(not args.work.exists(), "fresh output directory; preserve diagnostics")
        args.work.mkdir(parents=True)
        result = run(args.work)
    else:
        with tempfile.TemporaryDirectory(prefix="rank7-aligned-bits-") as directory:
            result = run(Path(directory))
    expected = PACKAGE / "RESULT.json"
    if expected.exists():
        require(json.loads(expected.read_text()) == result, "deterministic receipt")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
