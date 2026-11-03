"""Exact sum-conditioned shared-power cost certificate. Apache-2.0."""

import hashlib
import json
from pathlib import Path

from oracle import exhaustive_maxima, inherited_overhead


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(width, radix_width, total):
    require(type(width) is int and 1 <= width <= 4096, "width outside 1..4096")
    require(type(radix_width) is int and 1 <= radix_width < 2**64,
            "radix width outside 1..2^64-1")
    require(type(total) is int and 0 <= total <= 3 * ((1 << width) - 1),
            "total outside the three-word domain")


def advance(states, bit_index, target_bit, width, radix_width):
    coefficient = 14 * radix_width * width + 36 * radix_width - 9
    following = {}
    transitions = 0
    for (outgoing, active), (score, exponents) in sorted(states.items()):
        for bits in range(8):
            incoming = target_bit + 2 * outgoing - bits.bit_count()
            if not 0 <= incoming <= 2:
                continue
            used = active | bits
            added = used.bit_count() - 5 * (radix_width - 1) * bits.bit_count()
            added += coefficient * (used.bit_count() - active.bit_count())
            witness = tuple(exponents[j] + (((bits >> j) & 1) << bit_index)
                            for j in range(3))
            key = incoming, used
            candidate = score + added, witness
            if key not in following or candidate > following[key]:
                following[key] = candidate
            transitions += 1
    require(len(following) <= 24 and transitions <= 192, "state capacity")
    return following


def maximum_overhead(width, radix_width, total):
    """Return the exact overhead maximum and one attaining ordered triple."""
    validate(width, radix_width, total)
    states = {(total >> width, 0): (0, (0, 0, 0))}
    for bit_index in range(width - 1, -1, -1):
        states = advance(states, bit_index, (total >> bit_index) & 1,
                         width, radix_width)
    terminals = [value for (carry, _), value in states.items() if carry == 0]
    require(bool(terminals), "a valid sum must have a terminal state")
    score, witness = max(terminals)
    overhead = 15 * (radix_width - 1) * total + score
    require(sum(witness) == total, "witness sum")
    require(all(0 <= e < 1 << width for e in witness), "witness width")
    require(inherited_overhead(witness, width, radix_width) == overhead,
            "attaining witness tariff")
    return overhead, witness


def strict_threshold(width, radix_width, total):
    """None means strict saving is impossible, including the all-zero tie."""
    overhead, witness = maximum_overhead(width, radix_width, total)
    threshold = None if total < 2 else overhead // (total - 1) + 1
    return threshold, overhead, witness


def finite_comparison():
    triples = comparisons = 0
    stream = hashlib.sha256()
    for width in range(1, 6):
        for radix_width in (1, 2, 3, 7):
            maxima, visited = exhaustive_maxima(width, radix_width)
            triples += visited
            for total, expected in enumerate(maxima):
                actual, witness = maximum_overhead(width, radix_width, total)
                require(actual == expected, "carry maximum differs from enumeration")
                row = [width, radix_width, total, actual, witness]
                stream.update((json.dumps(row, separators=(",", ":")) + "\n").encode())
                comparisons += 1
    require(triples == 149792 and comparisons == 704, "finite domain inventory")
    return {"enumerated_triples": triples, "maximum_comparisons": comparisons,
            "maximum_stream_sha256": stream.hexdigest()}


def boundary_checks():
    threshold, overhead, witness = strict_threshold(4, 1, 10)
    require((threshold, overhead, witness) == (29, 257, (4, 4, 2)), "sharp case")
    require(9 * 29 - overhead == 4 and 9 * 28 - overhead == -5,
            "strict integer boundary")
    require((3 * (14 * 4 + 27) + 3 * 4) // 9 + 1 == 30,
            "independent-statistic sufficient threshold")
    require(strict_threshold(4, 3, 0)[:2] == (None, 0), "all-zero tie")
    require(strict_threshold(4, 3, 1)[0] is None, "one-atom loss")
    for width, radix_width, total in ((64, 3, 2**63 + 100), (4096, 1, 2)):
        h, attaining = maximum_overhead(width, radix_width, total)
        require(h == inherited_overhead(attaining, width, radix_width), "large witness")
    require(inherited_overhead((4, 4, 2), 4, 1) > 256, "undercut maximum control")
    require(inherited_overhead((4, 4, 2), 4, 1) != 3 * 83 + 3 * 4,
            "independent maxima cannot all be attained here")
    return {"width": 4, "radix_width": 1, "total": 10, "maximum_overhead": overhead,
            "attaining_exponents": witness, "exact_minimum_radix_invoice": threshold,
            "separate_statistic_sufficient_invoice": 30, "minimum_gain_at_29": 4,
            "attained_gain_at_28": -5}


def invalid_checks():
    cases = ((0, 1, 0), (4097, 1, 0), (True, 1, 0), (1.0, 1, 0),
             (2, 0, 0), (2, True, 0), (2, 2**64, 0), (2, 1.0, 0),
             (2, 1, -1), (2, 1, 10), (2, 1, True), (2, 1, 1.0))
    for arguments in cases:
        try:
            maximum_overhead(*arguments)
        except ValueError:
            continue
        raise ValueError("invalid argument accepted")
    return len(cases)


def receipt():
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "verify.py", "oracle.py")
    sources = {}
    for name in names:
        with (package / name).open("rb") as handle:
            payload = handle.read(131073)
        require(len(payload) <= 131072, "source read capacity")
        sources[name] = hashlib.sha256(payload).hexdigest()
    return {"status": "PASS_SHARED_ATOM_CROSSOVER", "claim_type": "scoped proof",
            "finite": finite_comparison(), "sharp_case": boundary_checks(),
            "invalid_arguments_rejected": invalid_checks(), "source_sha256": sources}


if __name__ == "__main__":
    print(json.dumps(receipt(), sort_keys=True, indent=2))
