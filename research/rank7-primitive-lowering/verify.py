# SPDX-License-Identifier: Apache-2.0
"""Compile six words and verify thirty-six exact real-arithmetic lowerings."""

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from pathlib import Path
import tempfile

from fixtures import check_blocks, produce
from literal import check_macro
from lower import POLICIES, certify, exclude_short_blocks, execute, lower, require
from replay import PACKAGE, authenticate, canonical, compile_word, digest, read


def scalar_parts(gate):
    kind, target = gate[:2]
    require(kind in ("clear", "copy", "add", "scale"), "emitted scalar kind")
    require(len(target) == 2 and target[0] in ("L", "C", "Z"), "emitted target")
    if kind in ("add", "copy"):
        source = gate[2]
        require(
            source != target and len(source) == 2 and source[0] in ("L", "C", "Z"),
            "emitted source",
        )
    else:
        source = None
    a, b = gate[3:5] if kind == "add" else gate[2:4] if kind == "scale" else (1, 1)
    q = Q(a, b)
    return kind, target, source, q


def primitive_event(operation, target, source, component, frame):
    registers = [
        [*target, component],
        None if source is None else [*source, component],
        ["K", 0, component],
    ]
    item = [operation[0], registers[operation[1]]]
    if len(operation) > 2:
        item.append(registers[operation[2]])
    if len(operation) > 3:
        item.append(operation[3])
    require(None not in item, "all primitive operands owned")
    return ["primitive", item, frame]


def materialize(events, output, *, policy="scratch"):
    require(not output.exists(), "fresh materialized output")
    require(len(events) <= 30_000, "bounded emitted events")
    expanded, certificates, counts = [], {}, Counter()
    for event in events:
        require(len(expanded) < 400_000, "bounded materialized stream")
        if event[0] != "scalar":
            expanded.append(event)
            continue
        _, gate, frame = event
        kind, target, source, q = scalar_parts(gate)
        key = (kind, q.numerator, q.denominator)
        if key not in certificates:
            require(len(certificates) < 128, "bounded coefficient alphabet")
            certificates[key] = certify(*key, policy=policy)
        for component in range(2):
            for operation in certificates[key]:
                require(len(expanded) < 400_000, "bounded materialized stream")
                expanded.append(
                    primitive_event(operation, target, source, component, frame)
                )
                counts[operation[0]] += 1
    payload = canonical(expanded)
    require(
        output.write_bytes(gzip.compress(payload, mtime=0)) > 0,
        "complete materialized output",
    )
    checked = check_expansion(events, read(output), policy=policy)
    return {
        "program_sha256": digest(events),
        "expanded_sha256": digest(expanded),
        "serialized_real_macros_checked": checked,
        "real_instructions": sum(counts.values()),
        "instruction_histogram": dict(sorted(counts.items())),
        "certified_macro_types": len(certificates),
        "non_scalar_sha256": digest([e for e in expanded if e[0] != "primitive"]),
    }


def check_expansion(events, expanded, *, policy="scratch"):
    require(
        len(events) <= 30_000 and len(expanded) <= 400_000, "bounded literal streams"
    )
    cursor, checked, lengths = 0, 0, {}
    for event in events:
        if event[0] != "scalar":
            require(
                cursor < len(expanded) and expanded[cursor] == event,
                "literal non-scalar chronology",
            )
            cursor += 1
            continue
        kind, target, source, q = scalar_parts(event[1])
        key = (kind, q.numerator, q.denominator)
        if key not in lengths:
            require(len(lengths) < 128, "bounded literal coefficient alphabet")
            lengths[key] = len(lower(*key, policy=policy))
        for component in range(2):
            count = lengths[key]
            require(cursor + count <= len(expanded), "complete literal macro")
            check_macro(
                expanded[cursor : cursor + count],
                kind,
                q,
                target,
                source,
                component,
                event[2],
            )
            cursor += count
            checked += 1
    require(cursor == len(expanded), "no extra literal instructions")
    return checked


def coefficient_certificate(events, *, policy="scratch"):
    certificates = {}
    for event in events:
        if event[0] != "scalar":
            continue
        kind, _, _, q = scalar_parts(event[1])
        key = f"{kind}:{q}"
        if key in certificates:
            continue
        recipe = certify(kind, q.numerator, q.denominator, policy=policy)
        scratch_peak, source_peak, fractional_bits, source_fractional_bits = (
            Q(0),
            Q(1),
            0,
            0,
        )
        target_factor = Q(1)
        for length in range(len(recipe) + 1):
            target, source, scratch = execute(recipe[:length], ((1, 0), (0, 1), (0, 0)))
            if kind == "add":
                require(
                    target[0] > 0 and min(0, q) <= target[1] / target[0] <= max(0, q),
                    "normalized ADD target prefixes lie between macro endpoints",
                )
                target_factor = max(target_factor, target[0])
            require(scratch[0] == source[0] == 0, "workspace depends only on source")
            scratch_peak = max(scratch_peak, abs(scratch[1]))
            source_peak = max(source_peak, abs(source[1]))
            fractional_bits = max(
                fractional_bits, scratch[1].denominator.bit_length() - 1
            )
            source_fractional_bits = max(
                source_fractional_bits, source[1].denominator.bit_length() - 1
            )
        require(len(certificates) < 128, "bounded coefficient certificates")
        certificates[key] = {
            "recipe": recipe,
            "scratch_peak_times_source": str(scratch_peak),
            "scratch_extra_fractional_bits": fractional_bits,
            "source_peak_times_source": str(source_peak),
            "source_extra_fractional_bits": source_fractional_bits,
            "target_add_peak_factor": str(target_factor),
        }
    return dict(sorted(certificates.items()))


def source_obligations(events):
    coefficients, registers, targets, changed, saved = {}, {}, {}, 0, 0
    for event in events:
        if event[0] != "scalar":
            continue
        kind, target, source, q = scalar_parts(event[1])
        before = len(lower(kind, q.numerator, q.denominator))
        after = len(lower(kind, q.numerator, q.denominator, policy="source_walk"))
        if before == after:
            continue
        require(kind == "add" and before > after, "source-walk ADD saving")
        changed += 1
        saved += 2 * (before - after)
        record = coefficients.setdefault(
            str(q), {"macros": 0, "real_instructions_saved": 0}
        )
        record["macros"] += 1
        record["real_instructions_saved"] += 2 * (before - after)
        bits = q.denominator.bit_length() - 1
        if bits:
            require(len(registers) < 800, "bounded writable sources")
            registers[tuple(source)] = max(registers.get(tuple(source), 0), bits)
            targets[tuple(target)] = max(targets.get(tuple(target), 0), bits)
    return {
        "changed_scalar_macros": changed,
        "real_instructions_saved": saved,
        "coefficients": dict(sorted(coefficients.items())),
        "target_extra_integer_bits": [
            [list(r), bits] for r, bits in sorted(targets.items())
        ],
        "writable_source_extra_fractional_bits": [
            [list(r), bits] for r, bits in sorted(registers.items())
        ],
    }


def check_native(events, checks):
    require(checks["sha256"] == digest(events), "literal native program hash")
    require(
        checks["all_columns"] == 632 and checks["zero_buffers_returned_to_zero"] == 91,
        "native dirty/private boundary",
    )
    require(
        checks["private_centers_cleared"]
        and checks["private_coefficient_stream_cleared_after_each_macro"],
        "native scratch flags",
    )
    require(
        {int(r): n for r, n in checks["paid_profile"].items()}
        == {1: 2433, 2: 712, 3: 232, 4: 108, 5: 18, 8: 8},
        "native recursive bill",
    )


def compare_variants(rows):
    for orientation in ("forward", "backward"):
        original = rows["parent"][orientation]
        for variant, bound_delta in (("three_add", 12), ("tariff", 24)):
            changed = rows[variant][orientation]
            for policy in POLICIES:
                before, after = (
                    original["lowerings"][policy],
                    changed["lowerings"][policy],
                )
                require(
                    after["real_instructions"] == before["real_instructions"],
                    "block forms tie under the same unit lowering",
                )
                require(
                    after["non_scalar_sha256"] == before["non_scalar_sha256"],
                    "unchanged complete non-scalar stream",
                )
            require(
                changed["conservative_tariff"]
                == original["conservative_tariff"] - bound_delta,
                "reported bound delta",
            )


def lower_program(events, output, certificates, obligations):
    result = {}
    for policy in POLICIES:
        row = materialize(
            events,
            output.with_name(output.name + "-" + policy + ".json.gz"),
            policy=policy,
        )
        fresh = coefficient_certificate(events, policy=policy)
        row["coefficient_types"] = sorted(fresh)
        for key, certificate in fresh.items():
            previous = certificates[policy].setdefault(key, certificate)
            require(previous == certificate, "consistent coefficient certificate")
        result[policy] = row
    for policy in ("source_walk", "target_walk"):
        require(
            result[policy]["real_instructions"]
            < result["scratch"]["real_instructions"],
            "strict fully counted scalar saving",
        )
        require(
            result[policy]["non_scalar_sha256"]
            == result["scratch"]["non_scalar_sha256"],
            "unchanged non-scalar stream across policies",
        )
    require(
        result["source_walk"]["real_instructions"]
        == result["target_walk"]["real_instructions"],
        "equal-cost source and target width alternatives",
    )
    require(
        result["scratch"]["real_instructions"]
        - result["source_walk"]["real_instructions"]
        == obligations["real_instructions_saved"],
        "access ledger matches materialized saving",
    )
    return result


def audit(work):
    pins = authenticate()
    work.mkdir(exist_ok=False)
    result = {
        "source_pins": pins,
        "blocks": check_blocks(),
        "minimum_unit_instructions": 4,
        "short_word_exclusion": exclude_short_blocks(),
        "providers": {},
        "coefficient_certificate": {policy: {} for policy in POLICIES},
        "source_write_obligations": {},
    }
    for provider in ("base", "extra"):
        parent = read(PACKAGE / f"vendor/WORD-{provider}.json.gz")
        rows = {}
        for variant in ("parent", "three_add", "tariff"):
            programs, checks = compile_word(
                produce(parent, variant), work / f"{provider}-{variant}"
            )
            rows[variant] = {}
            for orientation in ("forward", "backward"):
                events = programs[orientation]
                check_native(events, checks[orientation])
                obligations = source_obligations(events)
                previous = result["source_write_obligations"].setdefault(
                    orientation, obligations
                )
                require(
                    previous == obligations,
                    "same source-write obligations for every variant/provider",
                )
                rows[variant][orientation] = {
                    "conservative_tariff": checks[orientation][
                        "real_component_primitive_bound"
                    ],
                    "lowerings": lower_program(
                        events,
                        work / f"{provider}-{variant}-{orientation}",
                        result["coefficient_certificate"],
                        obligations,
                    ),
                }
        compare_variants(rows)
        result["providers"][provider] = rows
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work",
        type=Path,
        help="fresh external output directory; preserves diagnostics",
    )
    args = parser.parse_args()
    if args.work is None:
        with tempfile.TemporaryDirectory(prefix="rank7-lowering-") as directory:
            result = audit(Path(directory) / "replay")
    else:
        work = args.work.resolve()
        require(
            not work.is_relative_to(PACKAGE.parents[1]), "external output directory"
        )
        result = audit(work)
    require(
        canonical(result) == canonical(read(PACKAGE / "evidence/RESULT.json")),
        "recorded complete lowering receipt",
    )
    print(canonical(result).decode())


if __name__ == "__main__":
    main()
