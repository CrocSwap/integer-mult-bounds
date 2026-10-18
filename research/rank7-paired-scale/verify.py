# SPDX-License-Identifier: Apache-2.0
"""Cold native replay, complete scalar invoice and exact paired SCALE checks."""

import argparse
import hashlib
import json
import tempfile
from fractions import Fraction
from pathlib import Path

import bindings
import checks
import pairscale as p
from vendor import scalars as s

WIDTHS = (23, 24, 64, 84, 85, 148, 256)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def aggregate(width, histogram, bits, lower):
    s.require(
        len(histogram) == 29 and sum(histogram.values()) == 9992,
        "complete scalar histogram",
    )
    baseline, current = {"cx": 0, "ccx": 0}, {"cx": 0, "ccx": 0}
    templates, negative = {}, 0
    for key, count in sorted(histogram.items()):
        kind, numerator, denominator = key.split(":")
        a, b = int(numerator), int(denominator)
        recipe = lower.certify(kind, a, b, policy="target_walk")
        powers = bits.terms(a, b) if kind == "add" else []
        old = s.counts(s.circuit(width, kind, a, b, recipe, powers))
        if kind == "scale":
            gates = p.circuit(width, a, b, recipe)
            new = s.counts(gates)
            control = s.counts(p.circuit(width, a, b, recipe, control=True))
            s.require(
                control == {name: 2 * n for name, n in old.items()},
                "actual reused-partner control equals published baseline",
            )
            templates[key] = gates
            negative += count * (Fraction(a, b) < 0)
        else:
            new = {name: 2 * n for name, n in old.items()}
        for name in baseline:
            baseline[name] += 2 * count * old[name]
            current[name] += count * new[name]
    saving = {name: baseline[name] - current[name] for name in baseline}
    s.require(negative == 462, "all negative denominator encodings counted")
    s.require(
        saving == {"cx": negative * (14 * width + 4), "ccx": negative * 4 * width},
        "complete uniform delta",
    )
    s.require(
        current == {"cx": 85046 * width - 11324, "ccx": 41740 * width - 44544},
        "complete affine invoice",
    )
    return {
        "baseline": baseline,
        "paired": current,
        "saving": saving,
        "negative_scales": negative,
        "scale_circuits_sha256": hashlib.sha256(canonical(templates)).hexdigest(),
    }


def example(work, provider):
    import replay_parent as parent

    programs = parent.read(work / provider / "native/LOCAL-PROGRAMS.json.gz")
    s.require(len(programs["forward"]) <= 30_000, "bounded native stream")
    active = False
    for index, event in enumerate(programs["forward"]):
        if event[0] == "phase":
            if event[1] == "centers":
                break
            active = event[1] == "A"
        if active and event[0] == "scalar" and event[1][0] == "scale":
            gate = event[1]
            if Fraction(*gate[-2:]) < 0:
                return {
                    "event_index": index,
                    "event": event,
                    "next_event": programs["forward"][index + 1],
                    "ownership": (
                        "Real and imaginary W-bit words of each coordinate "
                        "of the same target role; one clean carry."
                    ),
                }
    raise ValueError("literal negative A-stage SCALE required")


def invoice_streams(parent, bits, lower):
    prior = json.loads((bindings.PACKAGE / "vendor/RESULT.json").read_text())
    streams, alphabet = {}, set()
    for provider in ("base", "extra"):
        for direction in ("forward", "backward"):
            name = f"{provider}/{direction}"
            fresh = parent["providers"][provider][direction]
            old = prior["streams"][name]
            s.require(
                all(
                    fresh[k] == old[k]
                    for k in ("dispatch_sha256", "histogram", "macros")
                ),
                "fresh stream equals exact PR3152 dispatch",
            )
            invoices = {
                str(w): aggregate(w, fresh["histogram"], bits, lower) for w in WIDTHS
            }
            for w in WIDTHS:
                s.require(
                    invoices[str(w)]["baseline"]
                    == old["invoices"][str(w)]["both_components"],
                    "literal predecessor invoice reproduced",
                )
            alphabet.update(
                tuple(map(int, key.split(":")[1:]))
                for key in fresh["histogram"]
                if key.startswith("scale:")
            )
            streams[name] = {
                "dispatch_sha256": fresh["dispatch_sha256"],
                "macros": fresh["macros"],
                "histogram": fresh["histogram"],
                "invoices": invoices,
            }
    return streams, sorted(alphabet)


def run(work):
    bits, caller, replay, lower, sources = bindings.load()
    fresh = replay.run(work)
    expected = json.loads((bindings.PARENT / "RESULT.json").read_text())
    expected.pop("bit_checks")
    s.require(fresh == expected, "cold native/capacity/old scalar bindings")
    streams, alphabet = invoice_streams(fresh, bits, lower)
    result = {
        "status": "PASS_PAIRED_SCALE_NO_NEW_KAPPA",
        "authenticated_files": sources,
        "data_width": 84,
        "clean_carry_bits": 1,
        "extra_scale_banks": 0,
        "streams": streams,
        "literal_examples": {name: example(work, name) for name in ("base", "extra")},
        "bit_checks": checks.exhaustive(alphabet, lower),
    }
    result["bit_checks"]["independent_array_fixtures"] = checks.fixtures(
        alphabet, lower, caller.guards
    )
    result["bit_checks"]["all_width_tariff_checks"] = sum(
        bool(p.negate(w)) for w in range(4, 257)
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()
    if args.work:
        work = args.work.expanduser().resolve()
        s.require(
            not work.exists() and not work.is_relative_to(bindings.ROOT),
            "fresh external output",
        )
        work.mkdir(parents=True)
        result = run(work)
    else:
        with tempfile.TemporaryDirectory(prefix="paired-scale-") as directory:
            result = run(Path(directory))
    expected = bindings.PACKAGE / "RESULT.json"
    if expected.exists():
        s.require(result == json.loads(expected.read_text()), "deterministic receipt")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
