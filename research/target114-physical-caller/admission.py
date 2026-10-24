"""Complete compact-word lifetime and all-low physical owner admission.

The cancellation lemma and coordinate-witness method follow Nick Petalas's
physical-compiler-correspondence/owners.py; this reconstructs the changed
compact source's entire 658-role/2595-pair inventory.
"""
from collections import Counter
from dataclasses import replace
from copy import copy
from fractions import Fraction
from hashlib import sha256
import json

from source_binding import need


def collect(topology):
    pairs, counts = set(), Counter()
    for stage in range(9):
        for replica in range(32):
            owners = topology.call(stage, replica).owners
            need(len(owners) == 658, 'complete compact owner arity')
            groups = {}
            for owner in owners:
                need(0 <= owner.family < topology.families, 'actual source family label')
                groups.setdefault(owner.family, []).append(owner.chart)
            counts.update(calls=1, owners=len(owners), family_groups=len(groups))
            for charts in groups.values():
                for i, first in enumerate(charts):
                    for second in charts[i + 1:]:
                        need(first != second, 'distinct same-family owner chart')
                        pairs.add(tuple(sorted((first, second), key=lambda chart: chart.key)))
                        counts['pair_occurrences'] += 1
    return sorted(pairs, key=lambda pair: tuple(chart.key for chart in pair)), dict(counts)


def validate(catalogue, pairs, witnesses):
    need(len(pairs) == len(witnesses), 'complete owner separator inventory')
    for (first, second), (row, column, difference) in zip(pairs, witnesses):
        need(0 <= row < 64 and 0 <= column < 64, 'separator coordinate')
        actual = catalogue.chart_matrix(first)[row][column] - catalogue.chart_matrix(second)[row][column]
        need(actual == Fraction(difference) and actual in (1, -1, Fraction(1, 2), Fraction(-1, 2)),
             'exact every-odd-prime owner separator')


def run(caller, catalogue):
    topology = catalogue._recursive_caller_topology
    census = caller.literal_census(catalogue)
    pairs, counts = collect(topology)
    denominators = Counter()
    charts = {chart for pair in pairs for chart in pair}
    for chart in charts:
        matrix = catalogue.chart_matrix(chart)
        need(len(matrix) == 64 and all(len(row) == 64 for row in matrix), 'complete owner matrix')
        for row in matrix:
            for value in row:
                denominator = Fraction(value).denominator
                need(denominator & (denominator - 1) == 0, 'odd-prime-defined dyadic chart')
                denominators[str(denominator)] += 1
    witnesses = []
    for first, second in pairs:
        a, b = catalogue.chart_matrix(first), catalogue.chart_matrix(second)
        found = next(((r, c, str(a[r][c] - b[r][c])) for r in range(64) for c in range(64)
                      if a[r][c] - b[r][c] in (1, -1, Fraction(1, 2), Fraction(-1, 2))), None)
        need(found is not None, 'complete odd-prime coordinate separator')
        witnesses.append(found)
    validate(catalogue, pairs, witnesses)
    need({k: counts[k] for k in ("calls", "owners", "pair_occurrences")} ==
         dict(calls=288, owners=189504, pair_occurrences=178528),
         'entire changed caller ownership census')
    need(len(pairs) == 2595, 'all changed distinct chart pairs')
    rejected = []
    for label, altered in [('missing_separator', witnesses[:-1]),
                           ('zero_separator', [(0, 0, '0')] + witnesses[1:])]:
        try:
            validate(catalogue, pairs, altered)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError('invalid owner certificate accepted ' + label)
    # Mutants use actual source calls, not a reduced invented topology.
    from control import LocalState
    actual = topology.call(0, 0)
    position = next(i for i, event in enumerate(actual.events) if event[0] == 2)
    events = list(actual.events)
    changed = list(events[position]); changed[2] = 661; events[position] = tuple(changed)
    state = LocalState(replace(actual, events=tuple(events)))
    try:
        for i in range(position + 1):
            state.accept(i)
    except ValueError as error:
        need(str(error) == 'fresh transported COPY interval', 'old private-index rejection')
        rejected.append('retired_private_index661')
    else:
        raise ValueError('retired private index admitted')
    malformed = copy(topology)
    schedule = [dict(event) for event in topology.schedule]
    bridge = next(event for event in schedule if event['kind'] == 'bridge')
    bridge['src'] = bridge['dst']; malformed.schedule = tuple(schedule)
    try:
        malformed._validate_global()
    except ValueError as error:
        need(str(error) == 'native bridge frame alignment', 'self-bridge source guard')
        rejected.append('self_bridge')
    else:
        raise ValueError('self-bridge admitted')
    records = [[a.key, b.key, witness] for (a, b), witness in zip(pairs, witnesses)]
    counts.update(unique_pairs=len(pairs), compared_charts=len(charts), chart_entry_denominators=dict(sorted(denominators.items())), witness_histogram=dict(Counter(w[2] for w in witnesses)),
                  witness_sha256=sha256(json.dumps(records, separators=(',', ':')).encode()).hexdigest())
    return dict(literal=census, owner_separation=counts, rejected=rejected,
                scope='All compact calls and every admissible low class; no symbolic payload kernel')
