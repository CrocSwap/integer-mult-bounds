#!/usr/bin/env python3
"""Exact finite controls for the arbitrary-mask affine-agreement theorem.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
The all-length proof is in README.md; this is supporting finite evidence.
"""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import struct
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MAX_BITS = 8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def source_check(root=ROOT):
    source = read_json(HERE / "SOURCE.json")
    for name, expected in source["sha256"].items():
        require(sha256((root / name).read_bytes()).hexdigest() == expected,
                "Source pin mismatch: " + name)
    return source["sha256"]


def mask_parameters(bits, mask):
    require(type(bits) is int and bits >= 1, "Positive integer width required")
    require(type(mask) is int and 0 <= mask < 1 << bits, "Mask outside domain")
    lower = mask & ((1 << (bits - 1)) - 1)
    selected = bin(lower).count("1")
    unselected = bits - 1 - selected
    return selected, unselected


def prediction(bits, mask):
    selected, unselected = mask_parameters(bits, mask)
    minority = min(selected, unselected)
    size = 1 << bits
    slope = 1 if selected <= unselected else size - 1
    return {
        "bits": bits, "mask": mask,
        "lower_selected": selected, "lower_unselected": unselected,
        "movement_lower_bound": minority,
        "maximum_agreement": 1 << (bits - minority),
        "minimum_affine_graph_cover": 1 << minority,
        "witness_slope": slope, "witness_offset": mask,
    }


def histogram(bits, mask, slope):
    """Literal address enumeration; a bin counts one possible affine offset."""
    size = 1 << bits
    counts = [0] * size
    for address in range(size):
        counts[((address ^ mask) - slope * address) % size] += 1
    return counts


def check_histogram(bits, mask, slope, counts):
    require(len(counts) == 1 << bits, "Incomplete offset domain")
    require(all(type(value) is int and value >= 0 for value in counts),
            "Invalid agreement count")
    require(sum(counts) == 1 << bits, "Incomplete address domain")
    selected, unselected = mask_parameters(bits, mask)
    if slope % 2 == 0:
        require(all(value == 1 for value in counts), "Even slope is not bijective")
    else:
        restricted = selected if slope % 4 == 1 else unselected
        require(max(counts) <= 1 << (bits - restricted),
                "Slope-class valuation bound exceeded")


def cover_offsets(bits, mask):
    """Explicit optimal cover, with a common slope and disjoint target fibers."""
    record = prediction(bits, mask)
    slope = record["witness_slope"]
    selected_branch = record["lower_selected"] <= record["lower_unselected"]
    positions = [i for i in range(bits - 1)
                 if bool(mask & (1 << i)) == selected_branch]
    offsets = []
    for subset in range(1 << len(positions)):
        value = sum(1 << position for j, position in enumerate(positions)
                    if subset & (1 << j))
        offsets.append((mask + (-2 if selected_branch else 2) * value) % (1 << bits))
    return slope, offsets


def check_cover(bits, mask, slope, offsets):
    record = prediction(bits, mask)
    require(len(offsets) == len(set(offsets)) == record["minimum_affine_graph_cover"],
            "Nonminimal, incomplete, or duplicate cover")
    observed = histogram(bits, mask, slope)
    require(set(offsets) == {b for b, count in enumerate(observed) if count},
            "Cover misses a target edge")
    require(all(observed[b] == record["maximum_agreement"] for b in offsets),
            "Cover has an incorrect fiber size")


def census(bits):
    size = 1 << bits
    digest = sha256()
    maxima = Counter()
    slope_pairs = 0
    for mask in range(size):
        record = prediction(bits, mask)
        maximum = 0
        for slope in range(size):
            counts = histogram(bits, mask, slope)
            check_histogram(bits, mask, slope, counts)
            maximum = max(maximum, max(counts))
            # Fixed little-endian 32-bit counts, M/a/b in increasing order.
            digest.update(struct.pack("<" + "I" * size, *counts))
            slope_pairs += 1
        require(maximum == record["maximum_agreement"], "Global maximum differs")
        witness = histogram(bits, mask, record["witness_slope"])
        require(witness[mask] == maximum, "Explicit maximum witness failed")
        slope, offsets = cover_offsets(bits, mask)
        check_cover(bits, mask, slope, offsets)
        maxima[str(maximum)] += 1
    require(slope_pairs == size * size, "Incomplete mask/slope domain")
    return {
        "bits": bits, "masks": size, "slopes_per_mask": size,
        "offsets_per_slope": size, "mask_slope_pairs": slope_pairs,
        "address_evaluations": size ** 3,
        "agreement_counts_covered": size ** 3,
        "maximum_agreement_histogram": dict(sorted(maxima.items(), key=lambda item: int(item[0]))),
        "all_histograms_sha256": digest.hexdigest(),
    }


def periodic_controls():
    rows = []
    for periods in range(1, 5):
        for spacing in range(1, 5):
            for offset in range(spacing):
                bits = periods * spacing
                mask = sum(1 << (offset + j * spacing) for j in range(periods))
                record = prediction(bits, mask)
                if spacing == 1:
                    expected = 0
                elif spacing == 2 or offset == spacing - 1:
                    expected = periods - 1
                else:
                    expected = periods
                require(record["movement_lower_bound"] == expected,
                        "Periodic boundary formula differs")
                slope, offsets = cover_offsets(bits, mask)
                check_cover(bits, mask, slope, offsets)
                rows.append(dict(periods=periods, spacing=spacing, offset=offset,
                                 **record))
    return rows


def negative_controls():
    rejected = []

    def reject(name, action):
        try:
            action()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("Negative control accepted: " + name)

    # Concrete, independently enumerated counterexamples to false extensions.
    controls = [
        ("count_the_top_bit", 6, 32, 32),
        ("ignore_complement_branch", 6, 15, 4),
        ("retain_n_at_top_periodic_offset", 6, 36, 16),
        ("retain_n_with_spacing_two", 6, 21, 8),
    ]
    counterexamples = []
    for name, bits, mask, false_bound in controls:
        record = prediction(bits, mask)
        actual = histogram(bits, mask, record["witness_slope"])[mask]
        reject(name, lambda actual=actual, bound=false_bound:
               require(actual <= bound, "False proposed upper bound"))
        counterexamples.append(dict(control=name, false_upper_bound=false_bound,
                                    witnessed_agreement=actual, **record))

    counts = histogram(4, 3, 2)
    reject("missing_offset_cell", lambda: check_histogram(4, 3, 2, counts[:-1]))
    corrupt = list(counts)
    corrupt[0] += 1
    corrupt[1] -= 1
    reject("mass_preserving_even_slope_corruption",
           lambda: check_histogram(4, 3, 2, corrupt))
    slope, offsets = cover_offsets(6, 18)
    reject("dropped_cover_graph", lambda: check_cover(6, 18, slope, offsets[:-1]))
    reject("shifted_cover_offsets",
           lambda: check_cover(6, 18, slope, [(b + 1) % 64 for b in offsets]))
    reject("wrong_cover_slope", lambda: check_cover(6, 18, 0, offsets))
    reject("mask_outside_domain", lambda: prediction(6, 64))
    reject("noninteger_width", lambda: prediction(6.0, 3))
    return {"rejected": rejected, "concrete_counterexamples": counterexamples}


def audit():
    pins = source_check()
    rows = [census(bits) for bits in range(1, MAX_BITS + 1)]
    return {
        "status": "PASS_XOR_AFFINE_AGREEMENT", "new_kappa": False,
        "base_commit": read_json(HERE / "SOURCE.json")["base_commit"],
        "source_sha256": pins,
        "coverage": {
            "bits_inclusive": [1, MAX_BITS], "all_masks": True,
            "all_residue_slopes_including_even": True, "all_residue_offsets": True,
            "mask_count": sum(row["masks"] for row in rows),
            "mask_slope_pairs": sum(row["mask_slope_pairs"] for row in rows),
            "agreement_counts_covered": sum(row["agreement_counts_covered"] for row in rows),
            "stopping_rule": "Complete every mask, slope, and offset for 1 <= L <= 8; no sampling or early stopping.",
        },
        "histogram_encoding": "SHA256 of concatenated unsigned 32-bit little-endian counts, lexicographic (mask,slope,offset) order, separately per width.",
        "census": rows, "periodic_controls": periodic_controls(),
        "negative_controls": negative_controls(),
        "scope": "Finite supporting evidence for the written all-L theorem; not proof-assistant verification, a matching movement-circuit upper bound, or a new multiplication result.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate this package's receipt only")
    args = parser.parse_args()
    report = audit()
    if args.write:
        (HERE / "CERTIFICATE.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    else:
        require(report == read_json(HERE / "CERTIFICATE.json"), "Certificate differs")
    print("PASS_XOR_AFFINE_AGREEMENT: 510 masks; 87,380 mask/slope pairs; "
          "19,173,960 exact agreement counts; 11 rejected controls", flush=True)
    if not args.write:
        command = [sys.executable, "-I", "-B"] + ["-O"] * sys.flags.optimize
        subprocess.run(command + [str(HERE / "independent.py")], check=True)


if __name__ == "__main__":
    main()
