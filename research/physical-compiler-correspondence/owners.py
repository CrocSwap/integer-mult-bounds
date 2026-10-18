"""All-low separation of the selected same-family owner charts."""

import json
from collections import Counter
from fractions import Fraction
from hashlib import sha256

from catalogue import Catalogue
from topology import SelectedTopology


def require(condition, message):
    if not condition:
        raise ValueError(message)


def key(chart):
    return chart.key


def collect(topology):
    pairs, counts = set(), Counter()
    for stage in range(9):
        for replica in range(32):
            owners = topology.call(stage, replica).owners
            require(len(owners) == 661, "complete selected staged owner list")
            counts["calls"] += 1
            counts["owners"] += len(owners)
            groups = {}
            for owner in owners:
                groups.setdefault(owner.family, []).append(owner.chart)
            counts["family_groups"] += len(groups)
            for charts in groups.values():
                for i, first in enumerate(charts):
                    for second in charts[i + 1 :]:
                        require(first != second, "duplicate same-family owner chart")
                        pairs.add(tuple(sorted((first, second), key=key)))
                        counts["same_family_pairs"] += 1
    require(
        counts["calls"] == 288 and counts["owners"] == 190368,
        "selected complete source dimensions",
    )
    return tuple(sorted(pairs, key=lambda pair: tuple(map(key, pair)))), dict(counts)


def witness(catalogue, first, second):
    a, b = catalogue.chart_matrix(first), catalogue.chart_matrix(second)
    for row in range(64):
        for column in range(64):
            difference = a[row][column] - b[row][column]
            if difference in (1, -1, Fraction(1, 2), Fraction(-1, 2)):
                return row, column, str(difference)
    raise ValueError("no odd-prime-uniform coordinate separator")


def validate(catalogue, pairs, witnesses):
    require(len(witnesses) == len(pairs), "one separator for every chart pair")
    for (first, second), (row, column, difference) in zip(pairs, witnesses):
        require(0 <= row < 64 and 0 <= column < 64, "separator coordinate")
        actual = (
            catalogue.chart_matrix(first)[row][column]
            - catalogue.chart_matrix(second)[row][column]
        )
        require(
            actual == Fraction(difference)
            and actual in (1, -1, Fraction(1, 2), Fraction(-1, 2)),
            "nonzero separator over every odd prime",
        )


def chart_domain(catalogue, pairs):
    charts = {chart for pair in pairs for chart in pair}
    denominators = Counter()
    for chart in charts:
        matrix = catalogue.chart_matrix(chart)
        require(
            len(matrix) == 64 and all(len(row) == 64 for row in matrix),
            "complete chart matrix",
        )
        for row in matrix:
            for entry in row:
                denominator = Fraction(entry).denominator
                require(denominator in (1, 2), "odd primes define the complete chart")
                denominators[denominator] += 1
    return {
        "charts": len(charts),
        "entry_denominators": {str(k): v for k, v in denominators.items()},
    }


def run():
    # Only rational selected labels are used. No q=3 low class is enumerated.
    catalogue = Catalogue(3)
    pairs, counts = collect(SelectedTopology(catalogue))
    counts.update(chart_domain(catalogue, pairs))
    witnesses = tuple(witness(catalogue, first, second) for first, second in pairs)
    validate(catalogue, pairs, witnesses)
    records = [
        (key(first), key(second), proof)
        for (first, second), proof in zip(pairs, witnesses)
    ]
    counts.update(
        unique_chart_pairs=len(pairs),
        witness_differences=dict(Counter(proof[2] for proof in witnesses)),
    )
    counts["separators_sha256"] = sha256(
        json.dumps(records, separators=(",", ":")).encode()
    ).hexdigest()
    rejected = []
    for label, changed in (
        ("missing_separator", witnesses[:-1]),
        ("zero_separator", ((0, 0, "0"),) + witnesses[1:]),
    ):
        try:
            validate(catalogue, pairs, changed)
        except ValueError:
            rejected.append(label)
    require(
        rejected == ["missing_separator", "zero_separator"], "separator controls reject"
    )
    return {
        "census": counts,
        "rejected": rejected,
        "scope": "Distinct charts at every odd prime; disjoint low packets when charts are invertible",
    }
