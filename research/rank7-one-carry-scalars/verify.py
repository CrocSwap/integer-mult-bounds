# SPDX-License-Identifier: Apache-2.0
"""Cold replay and full one-carry scalar invoice, with bounded truth checks."""

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

import bindings
import checks
import scalars as s


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def factory(bits, lower):
    def build(width, kind, a, b):
        recipe = lower.certify(kind, a, b, policy="target_walk")
        powers = bits.terms(a, b) if kind == "add" else []
        return s.circuit(width, kind, a, b, recipe, powers)

    return build


def aggregate(width, histogram, build):
    s.require(
        len(histogram) == 29 and sum(histogram.values()) == 9992, "complete histogram"
    )
    total = {"cx": 0, "ccx": 0}
    templates = {}
    for key, count in sorted(histogram.items()):
        kind, a, b = key.split(":")
        gates = build(width, kind, int(a), int(b))
        templates[key] = gates
        for name, n in s.counts(gates).items():
            total[name] += 2 * count * n
    return {
        "both_components": total,
        "templates_sha256": hashlib.sha256(canonical(templates)).hexdigest(),
    }


def run(work):
    bits, caller, replay, lower = bindings.load()
    parent = replay.run(work)
    expected = json.loads((bindings.PARENT / "RESULT.json").read_text())
    expected.pop("bit_checks")
    s.require(parent == expected, "fresh native/capacity and prior invoice binding")
    build = factory(bits, lower)
    streams, all_keys = {}, set()
    for provider in ("base", "extra"):
        for direction in ("forward", "backward"):
            old = parent["providers"][provider][direction]
            histogram = old["histogram"]
            all_keys.update(histogram)
            invoices = {
                str(w): aggregate(w, histogram, build)
                for w in (23, 24, 64, 84, 85, 148, 256)
            }
            current = invoices["84"]["both_components"]
            baseline = old["both_components_at_84_bits"]["direct"]
            saving = {g: baseline[g] - current[g] for g in baseline}
            s.require(sum(saving.values()) > 0, "strict full scalar gate saving")
            # All shifts are below 23: counts are affine throughout 23..256.
            for w in (64, 84, 85, 148, 256):
                for g in current:
                    lo = invoices["23"]["both_components"][g]
                    slope = invoices["24"]["both_components"][g] - lo
                    s.require(
                        invoices[str(w)]["both_components"][g] == lo + (w - 23) * slope,
                        "uniform tariff law",
                    )
            streams[f"{provider}/{direction}"] = {
                "dispatch_sha256": old["dispatch_sha256"],
                "macros": old["macros"],
                "histogram": histogram,
                "invoices": invoices,
                "saving_at_84_bits": saving,
            }
    alphabet = [
        tuple([k, int(a), int(b)])
        for k, a, b in (key.split(":") for key in sorted(all_keys))
    ]
    return {
        "status": "PASS_ONE_CARRY_SCALARS_NO_NEW_KAPPA",
        "data_width": 84,
        "clean_carry_bits": 1,
        "prior_clean_carry_bits": 83,
        "operand_bits": 168,
        "coefficient_scratch_bits": 0,
        "boundary": "Both operand banks exclusively writable during each macro; source and carry restored.",
        "streams": streams,
        "bit_checks": checks.run(alphabet, build, caller.guards),
    }


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
        with tempfile.TemporaryDirectory(prefix="one-carry-scalars-") as directory:
            result = run(Path(directory))
    expected = bindings.PACKAGE / "RESULT.json"
    if expected.exists():
        s.require(result == json.loads(expected.read_text()), "deterministic receipt")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
