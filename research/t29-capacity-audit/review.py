#!/usr/bin/env python3
"""Independent phase-2 T29 inventory audit; no imports from package workers.

Written for the mathematical reviewer with OpenAI assistance, Apache-2.0.
The ten-pattern witness was derived by hand, independently of the producer.
This certifies capacity-tagged integer packing, not physical owner execution.
"""
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
PINS = {
    "research/complex-t37-owners/ALL-T-PROOF.md": "4c0c71ccd0afb850538af1b467e5208b7eb3edd0260fded84e02a8c01dfc868b",
    "research/complex-t21-owner-bound/PROOF.md": "2aa0aa6ec1d87402138564c38749b5ca0f058c16817efdf58a2685d2d90cb417",
    "research/t37-integrality-audit/PROOF.md": "0dd18b2b486b98dc06e67b0b64e21dc18b6282af483f975e551b1f36dbc5d7ca",
    "research/t37-integrality-audit/README.md": "5e90726de4069d8d19c1f3cf49e636578f46c1d150f1b8d7a7ca64c90b78ea1c",
}
WIDTHS = (4, 5, 7, 8, 9)
PRICES = (-1, -20, -8, -2, 4)
BONUSES = {8: 2, 16: 4, 32: 8, 48: -13}
CAPS = {8: 19488, 16: 12992, 32: 12992, 48: 12992}
HELPERS = {4: 20880, 5: 8352, 7: 14094, 8: 31842, 9: 56376}
RANKS = {0: 49770, 1: 4, 2: 1, 48: 8689}
# (capacity, multiplicity, counts at widths 4,5,7,8,9)
WITNESS = (
    (8, 8285, (2, 0, 0, 0, 0)),
    (8, 11203, (0, 0, 0, 1, 0)),
    (16, 4824, (0, 0, 1, 0, 1)),
    (16, 8168, (0, 0, 0, 2, 0)),
    (32, 8352, (0, 1, 0, 0, 3)),
    (32, 4635, (0, 0, 2, 0, 2)),
    (32, 4, (1, 0, 0, 0, 3)),
    (32, 1, (3, 0, 0, 0, 2)),
    (48, 4303, (1, 0, 0, 1, 4)),
    (48, 8689, (0, 0, 0, 0, 0)),
)


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def legal_patterns():
    """Reachability closure by adding one helper; no Cartesian/DFS generator."""
    result = []
    for capacity in BONUSES:
        seen = {(0, 0, 0, 0, 0)}
        todo = list(seen)
        while todo:
            counts = todo.pop()
            fill = sum(w * n for w, n in zip(WIDTHS, counts))
            result.append((capacity, counts, capacity - fill,
                           BONUSES[capacity] + sum(p * n for p, n in zip(PRICES, counts))))
            for i, width in enumerate(WIDTHS):
                if fill + width <= capacity:
                    next_counts = list(counts)
                    next_counts[i] += 1
                    next_counts = tuple(next_counts)
                    if next_counts not in seen:
                        seen.add(next_counts)
                        todo.append(next_counts)
    return result


def tally(rows):
    caps, helpers, ranks = Counter(), Counter(), Counter()
    signed = 0
    for capacity, multiplicity, counts in rows:
        need(type(capacity) is int and capacity in BONUSES, "capacity domain")
        need(type(multiplicity) is int and multiplicity >= 0, "multiplicity domain")
        need(len(counts) == 5 and all(type(x) is int and x >= 0 for x in counts), "whole-helper domain")
        rank = capacity - sum(w * n for w, n in zip(WIDTHS, counts))
        need(rank >= 0, "capacity overflow")
        caps[capacity] += multiplicity
        ranks[rank] += multiplicity
        for width, number in zip(WIDTHS, counts):
            helpers[width] += multiplicity * number
        signed += multiplicity * (BONUSES[capacity] + sum(p * n for p, n in zip(PRICES, counts)))
    return caps, helpers, ranks, signed


def aggregate(rows):
    """Deliberately weak: profile/count, mass and signed price, not type quotas."""
    caps, helpers, ranks, signed = tally(rows)
    return (dict(ranks) == RANKS and sum(caps.values()) == 58464
            and sum(r * n for r, n in ranks.items()) == 417078
            and signed == -112868)


def check(rows, upper):
    caps, helpers, ranks, signed = tally(rows)
    need(caps == Counter(CAPS), "capacity census")
    need(helpers == Counter(HELPERS), "helper census")
    need(ranks == Counter(RANKS), "residual census")
    need(signed == -3892 * 29, "signed price")
    slack = 0
    for capacity, multiplicity, counts in rows:
        rank = capacity - sum(w * n for w, n in zip(WIDTHS, counts))
        actual = BONUSES[capacity] + sum(p * n for p, n in zip(PRICES, counts))
        need(actual <= upper[rank], "bin dual inequality")
        slack += multiplicity * (upper[rank] - actual)
    need(slack == 0, "tight-price necessity")
    return dict(capacities=dict(caps), helpers=dict(helpers), residuals=dict(ranks),
                signed_price=signed, total_bins=sum(caps.values()),
                total_helpers=sum(helpers.values()), residual_mass=417078,
                used_cells=sum(w * n for w, n in helpers.items()), price_slack=slack)


def unit_slot_oracle(rows):
    """Expand every bin and every indivisible helper; count literal unit slots."""
    caps, helpers, ranks = Counter(), Counter(), Counter()
    for capacity, multiplicity, counts in rows:
        for _ in range(multiplicity):
            slots = [None] * capacity
            cursor = 0
            for width, count in zip(WIDTHS, counts):
                for _ in range(count):
                    helpers[width] += 1
                    for _ in range(width):
                        need(cursor < len(slots), "slot overflow")
                        slots[cursor] = width
                        cursor += 1
            caps[len(slots)] += 1
            ranks[slots.count(None)] += 1
    need(caps == Counter(CAPS) and helpers == Counter(HELPERS) and ranks == Counter(RANKS),
         "expanded unit-slot inventories")


def subtract_one(rows, index, number=1):
    rows = list(rows)
    capacity, multiplicity, counts = rows[index]
    rows[index] = (capacity, multiplicity - number, counts)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--witness', type=Path, help='Post-blind review: independently check a producer WITNESS.json and its sibling EXPECTED.json')
    args = parser.parse_args()
    for relative, digest in PINS.items():
        need(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest,
             "source drift: " + relative)
    need(CAPS == {c: 29 * n for c, n in zip((8, 16, 32, 48), (672, 448, 448, 448))}, "capacity interpretation")
    need(HELPERS == {w: 29 * 9 * n for w, n in zip(WIDTHS, (80, 32, 54, 122, 216))}, "nine-call interpretation")
    need(RANKS[0] == sum(CAPS.values()) - sum(n for r, n in RANKS.items() if r), "rank-zero interpretation")
    patterns = legal_patterns()
    need(len(patterns) == 1163 and len({(c, h) for c, h, r, s in patterns}) == 1163, "complete pattern census")
    upper = {}
    for capacity, counts, rank, signed in patterns:
        upper[rank] = max(upper.get(rank, signed), signed)
    need(len(upper) == 45 and {r: upper[r] for r in RANKS} == {0: 0, 1: 19, 2: 13, 48: -13}, "source dual values")
    tight = [p for p in patterns if p[2] in RANKS and p[3] == upper[p[2]]]
    # Direct algebra: fill + 4 * price removes widths 4 and 8.
    for capacity, counts, rank, signed in patterns:
        x4, x5, x7, x8, x9 = counts
        need(25 * (x9 - x7 - 3 * x5) == capacity - rank + 4 * (signed - BONUSES[capacity]), "elimination identity")
    need(sum(upper[r] * n for r, n in RANKS.items()) == -3892 * 29, "global price equality")
    certificate = check(WITNESS, upper)
    unit_slot_oracle(WITNESS)

    controls = []
    # Four width-4 helpers replace width 7 + width 9 in one full cap-16 bin:
    # fill 16 and price -4 are unchanged, but source helper demands are broken.
    wrong_helpers = subtract_one(WITNESS, 2) + [(16, 1, (4, 0, 0, 0, 0))]
    need(aggregate(wrong_helpers), "helper control must preserve weak aggregate certificate")
    controls.append(("aggregate-preserving wrong helper census", wrong_helpers, "helper census"))
    # Three full cap-16 bins (six width-8 helpers) become two cap-8 and one
    # cap-32 bin. All helpers, ranks, total capacity, bin count and price agree.
    wrong_caps = subtract_one(WITNESS, 3, 3) + [(8, 2, (0, 0, 0, 1, 0)), (32, 1, (0, 0, 0, 4, 0))]
    need(aggregate(wrong_caps) and tally(wrong_caps)[1] == Counter(HELPERS), "capacity control must preserve aggregate and helper census")
    controls.append(("aggregate-and-helper-preserving wrong capacity census", wrong_caps, "capacity census"))
    controls.append(("omitted empty bins", WITNESS[:-1], "capacity census"))
    controls.append(("overfilled bin", WITNESS + ((8, 1, (0, 0, 0, 0, 1)),), "capacity overflow"))
    controls.append(("fractional helper", WITNESS + ((8, 1, (0.5, 0, 0, 0, 0)),), "whole-helper domain"))
    controls.append(("negative multiplicity", WITNESS + ((8, -1, (0, 0, 0, 0, 0)),), "multiplicity domain"))
    controls.append(("boolean multiplicity", WITNESS + ((8, True, (0, 0, 0, 0, 0)),), "multiplicity domain"))
    controls.append(("unknown capacity", WITNESS + ((9, 1, (0, 0, 0, 0, 0)),), "capacity domain"))
    rejected = []
    for name, rows, reason in controls:
        try:
            check(rows, upper)
        except ValueError as error:
            need(str(error) == reason, "wrong rejection for " + name)
            rejected.append(dict(control=name, reason=reason))
        else:
            raise ValueError("accepted invalid control: " + name)
    # Legal row order and splitting a multiplicity must not affect admission.
    need(check(tuple(reversed(WITNESS)), upper) == certificate, "order independence")
    split = subtract_one(WITNESS, 0) + [(8, 1, (2, 0, 0, 0, 0))]
    need(check(split, upper) == certificate, "split-row invariance")
    result = dict(status="PASS_INDEPENDENT_T29_CAPACITY_REVIEW", outcome="supports H",
                          patterns=len(patterns), attained_ranks=len(upper),
                          tight_patterns_for_target_ranks=len(tight),
                          witness=WITNESS, certificate=certificate,
                          negative_controls=rejected, positive_controls=2,
                          source_sha256=PINS)
    if args.witness:
        document = json.loads(args.witness.read_text())
        need(document['hypothesis'] == 'q_b6cf2a2ce15a43ed:e10' and document['replicas'] == 29, 'producer header')
        need(document['remainder_profile'] == {str(r): n for r, n in RANKS.items()}, 'producer declared profile')
        rows = []
        for item in document['patterns']:
            need(all(type(w) is int and w in WIDTHS for w in item['widths']), 'producer width domain')
            rows.append((item['capacity'], item['count'], tuple(item['widths'].count(w) for w in WIDTHS)))
        producer = check(rows, upper)
        unit_slot_oracle(rows)
        expected = json.loads(args.witness.with_name('EXPECTED.json').read_text())
        need(expected['u'] == {str(r): p for r, p in upper.items()}, 'producer full u table')
        classes = {str(r): set() for r in RANKS}
        for capacity, counts, rank, signed in tight:
            widths = [w for w, n in zip(WIDTHS, counts) for _ in range(n)]
            classes[str(rank)].add(str(capacity) + ':{' + ','.join(map(str, sorted(widths, reverse=True))) + '}')
        claimed = expected['structure']['tight_patterns_by_class']
        need(set(claimed) == set(classes) and all(len(claimed[r]) == len(classes[r]) and set(claimed[r]) == classes[r] for r in classes), 'producer complete tight classes')
        need(producer == certificate, 'independent witnesses have identical inventories')
        result['integration'] = dict(witness_sha256=hashlib.sha256(args.witness.read_bytes()).hexdigest(),
                                     producer_witness=producer, complete_tight_classes_match=True,
                                     witness_differs_from_blind=sorted(rows) != sorted(WITNESS))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
