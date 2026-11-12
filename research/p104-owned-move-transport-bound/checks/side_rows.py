"""Screen chart-local side rows on all common-clock cuts of exact #7161."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from math import gcd, lcm
import json
from pathlib import Path
from time import monotonic

PREDECESSOR = '53da0a7b551b34f3baf633083a4362570ebe694a694e2d0b6226d01c08a6ab3b'


def import_pinned(name, path, expected):
    assert sha256(path.read_bytes()).hexdigest() == expected, path
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def primitive(row):
    content = gcd(*row.values())
    if content > 1:
        return {i: x // content for i, x in row.items()}
    return row


def integral(row):
    denominator = lcm(*(x.denominator for x in row.values()))
    return primitive({i: x.numerator * (denominator // x.denominator) for i, x in row.items()})


def insert(basis, vector):
    """Add one row over Q by fraction-free sparse elimination."""
    row = vector.copy()
    while row:
        lead = min(row)
        entry = row[lead]
        other = basis.get(lead)
        if other is None:
            basis[lead] = row
            return 1
        pivot = other[lead]
        common = gcd(pivot, entry)
        a, b = pivot // common, entry // common
        if a != 1:
            row = {i: a*x for i, x in row.items()}
        for i, x in other.items():
            value = row.get(i, 0)-b*x
            if value:
                row[i] = value
            else:
                row.pop(i, None)
        row = primitive(row)
    return 0


def controls():
    basis = {}
    assert insert(basis, {1: 2, 2: 3}) == 1
    assert insert(basis, {1: 4, 2: 6}) == 0
    assert insert(basis, {1: -3, 2: -4}) == 1
    assert insert(basis, {2: 1}) == 0
    assert insert(basis, {2: 1, 3: 1}) == 1
    row = {1: Fraction(6,5), 2: Fraction(-3,10)}
    assert integral(row) == {1:4, 2:-1}


def max_sets(moves):
    def active(cut):
        return tuple(m['event'] for m in moves if m['window'][0] <= cut <= m['window'][1])

    starts = sorted({m['window'][0] for m in moves})
    families = {frozenset(active(cut)) for cut in starts}
    families = sorted((a for a in families if not any(a < b for b in families)), key=lambda a: sorted(a))
    return active, families


def run(peer_root, caller_path, gate_path, owned_path, seconds, maximal_cap):
    controls()
    started = monotonic()

    def check_time():
        if monotonic() - started > seconds:
            raise TimeoutError('side-row time budget expired')

    owned = import_pinned('retained_owned', owned_path, PREDECESSOR)
    package = peer_root / owned.PACKAGE
    word_raw = gzip.decompress(owned.pinned(package/'WORD.json.gz', f'peer/{owned.PACKAGE}/WORD.json.gz'))
    assert sha256(word_raw).hexdigest() == owned.PINS[f'peer/{owned.PACKAGE}/WORD.json.gz#decompressed']
    word = json.loads(word_raw)
    result = json.loads(owned.pinned(package/'RESULT.json', f'peer/{owned.PACKAGE}/RESULT.json'))
    caller = json.loads(owned.pinned(caller_path, 'caller-inputs/CALLER.json'))
    gate = import_pinned('retained_interval', gate_path, owned.PINS['caller-inputs/interval_gate.py'])
    spaces, native, moves, _ = owned.scan_word(word, check_time, 80000)
    signed, invoice = owned.full_invoice(word, caller, result, native)
    baseline = gate.moment(signed, owned.TARGET)
    move = {m['event']: m for m in moves}
    active_at, families = max_sets(moves)
    assert len(families) == 42
    scope = {}
    cut_range = range(min(m['window'][0] for m in moves), max(m['window'][1] for m in moves)+1)
    for cut in cut_range:
        active = active_at(cut)
        if active:
            assert len(active) == len({move[i]['role'] for i in active})
            group = frozenset(active)
            scope[cut] = (active, next(j for j,family in enumerate(families) if group <= family))
    assert len(scope) == 11163
    assert len({a for a,_ in scope.values()}) == 53

    charts = word['initial'] + [None] * word['owned_fields']
    rows = [{i: Fraction(1)} for i in range(word['public'])] + [{} for _ in range(word['owned_fields'])]
    row_ids = list(range(len(rows)))
    coefficients = {}
    live_at = defaultdict(set)
    for i, label in enumerate(charts):
        if label is not None:
            live_at[spaces[label]].add(i)
    int_rows, bases, ranks = {}, {}, {}
    used_families, used_groups = set(), set()
    stats = {name: Counter() for name in ('target_pool','endpoint_pool')}
    drop_union = {name:set() for name in stats}
    bound_groups = {name:{} for name in stats}
    local_sites = {}
    local_groups = {}
    local_group_cuts = Counter()
    group_stats = defaultdict(Counter)
    examined = 0
    first_pending = None
    site_counts = Counter()

    def base_for(sides):
        ids = tuple(row_ids[i] for i in sides)
        if ids not in bases:
            basis = {}
            for i in sides:
                key = row_ids[i]
                if key not in int_rows:
                    int_rows[key] = integral(rows[i])
                insert(basis, int_rows[key])
            bases[ids] = basis
        return bases[ids]

    def quotient_rank(sides, roles):
        key = tuple(row_ids[i] for i in sides), tuple(row_ids[i] for i in roles)
        if key not in ranks:
            basis = base_for(sides).copy()
            start = len(basis)
            for i in roles:
                k = row_ids[i]
                if k not in int_rows:
                    int_rows[k] = integral(rows[i])
                insert(basis, int_rows[k])
            ranks[key] = len(basis) - start
        return ranks[key]

    def side_rows(chart_labels, exempt):
        return tuple(sorted({role for label in chart_labels for role in live_at[spaces[label]]
                             if role not in exempt and rows[role]}))

    def remember(target, key, value):
        if key not in target or value[:3] < target[key][:3]:
            target[key] = value

    for i,(op, r, *args) in enumerate(word['program'][:max(scope)+1]):
        if i % 1024 == 0 and monotonic()-started > seconds:
            first_pending = dict(cut=i, reason='time')
            break
        if i in scope:
            events, family = scope[i]
            if family >= maximal_cap:
                if first_pending is None:
                    first_pending = dict(cut=i, family=family, reason='family cap')
            else:
                if monotonic()-started > seconds:
                    first_pending = dict(cut=i, family=family, reason='time')
                    break
                used_families.add(family)
                used_groups.add(events)
                roles = tuple(move[e]['role'] for e in events)
                group_stats[family]['cuts'] += 1
                examined += 1
                targets = {move[e]['target'] for e in events}
                endpoints = targets | {move[e]['source'] for e in events}
                assert all(rows[r0] for r0 in roles)
                for name, frames in (('target_pool', targets), ('endpoint_pool', endpoints)):
                    sides = side_rows(frames, roles)
                    quotient = quotient_rank(sides, roles)
                    d = len(roles)-quotient
                    stats[name][d] += 1
                    group_stats[family][f'{name}_{d}'] += 1
                    if d:
                        drop_union[name].update(events)
                        remember(bound_groups[name], (events,d), (len(sides), i, quotient, sides))
                for event, r0 in zip(events, roles):
                    sides = side_rows((move[event]['target'],), {r0})
                    if quotient_rank(sides, (r0,)) == 0:
                        site_counts[event] += 1
                        remember(local_sites, event, (len(sides), i, move[event]['rank'], sides))
                if quotient_rank(side_rows(targets, roles), roles) < len(roles):
                    for size in range(2, len(events)+1):
                        for selected in combinations(events, size):
                            selected_roles = tuple(move[e]['role'] for e in selected)
                            selected_charts = {move[e]['target'] for e in selected}
                            sides = side_rows(selected_charts, selected_roles)
                            d = size-quotient_rank(sides, selected_roles)
                            if d:
                                local_group_cuts[selected,d] += 1
                                remember(local_groups, (selected,d), (len(sides), i, d, sides))

        if op == 'MOVE':
            before, after, _ = args
            assert charts[r] == before
            live_at[spaces[before]].remove(r)
            live_at[spaces[after]].add(r)
            charts[r] = after
        elif op == 'INIT':
            assert not rows[r] and charts[r] is None
            charts[r] = args[0]
            live_at[spaces[charts[r]]].add(r)
        elif op == 'CLEAR':
            assert charts[r] == args[0]
            live_at[spaces[charts[r]]].remove(r)
            rows[r], charts[r] = {}, None
            row_ids[r] = len(rows) + i
        else:
            key = args[0 if op == 'SCALE' else 1]
            if key not in coefficients:
                coefficients[key] = Fraction(key)
            multiplier = coefficients[key]
            if op == 'SCALE':
                assert charts[r] == args[1]
                rows[r] = {j:multiplier*x for j,x in rows[r].items()}
            else:
                source = args[0]
                assert charts[r] == charts[source] == args[2]
                assert op == 'ADD' or op == 'COPY' and not rows[r]
                for j,x in rows[source].items():
                    value = rows[r].get(j,0)+multiplier*x
                    if value:
                        rows[r][j] = value
                    else:
                        rows[r].pop(j,None)
            row_ids[r] = len(rows) + i

    def price_upper(sites):
        prices = Counter(move[i]['rank'] for i in sites)
        saving = gate.smul(gate.moment(prices, owned.TARGET), owned.STAGES)
        return dict(ranks=prices, sites=sorted(sites), saving_upper=gate.show(saving)[1],
                    resulting_moment_upper=gate.show(gate.add(baseline, (0,saving[1])))[1])

    # Keep one occurrence in at most one replacement group. Overgrant choosing
    # the highest-rank erased calls without constraining the carrier rows.
    options = [(set(selected), tuple(sorted(selected, key=lambda e: (move[e]['rank'], e), reverse=True)[:d]))
               for selected,d in sorted(local_groups)]

    def packed_price_bound(index, used, deleted):
        if index == len(options):
            return [(deleted, used)]
        selected, omitted = options[index]
        outcomes = packed_price_bound(index+1, used, deleted)
        if not used & selected:
            outcomes += packed_price_bound(index+1, used | selected, deleted + omitted)
        return outcomes

    cases = packed_price_bound(0, set(), ())
    current = gate.moment(Counter(m['rank'] for m in moves), owned.TARGET)
    total_rank = sum(m['rank'] for m in moves)
    best = max(cases, key=lambda case: sum(move[e]['rank'] for e in case[0]))
    remaining_rank = total_rank - sum(move[e]['rank'] for e in best[0])
    packed = gate.power(remaining_rank, owned.TARGET)
    packed_credit = gate.smul(gate.sub(current, packed), owned.STAGES)
    singletons = price_upper(local_sites)
    retained_rank_drop = max((price_upper(deleted) for deleted,_ in cases),
                             key=lambda x: Fraction(x['saving_upper']))

    screened = {}
    for name in stats:
        screened[name] = dict(deficit_cut_histogram=stats[name], unique_event_deletion_upper=price_upper(drop_union[name]),
                              positive_group_bounds=[dict(events=events, deficit=d, witness_cut=spec[1],
                                                          supply_count=spec[0], side_roles=spec[3])
                                                     for (events,d),spec in sorted(bound_groups[name].items())])
    return dict(status='EXHAUSTED' if examined == len(scope) else 'CAP_PENDING', head=owned.HEAD,
                target=str(owned.TARGET), invoice=invoice, baseline=gate.show(baseline),
                caps=dict(maximal_families=maximal_cap, seconds=seconds),
                pins=owned.PINS | {'round8/evidence/complex/owned.py':PREDECESSOR},
                first_pending=first_pending, clock_cuts_total=len(scope), clock_cuts_tested=examined,
                clock_cuts_unresolved=len(scope)-examined, exact_active_sets_total=53,
                exact_active_sets_tested=len(used_groups), maximal_families_total=len(families),
                maximal_families_tested=len(used_families), basis_count=len(bases), quotient_count=len(ranks),
                family_stats=[dict(maximal_events=sorted(a), counts=group_stats[j]) for j,a in enumerate(families)],
                screened=screened,
                singleton_target_local=dict(price_upper=singletons, witnesses=[
                    dict(event=i, cut=spec[1], rank=spec[2], side_roles=spec[3], eligible_cuts=site_counts[i])
                    for i,spec in sorted(local_sites.items())]),
                exact_positive_target_subgroups=[dict(events=selected, deficit=d, witness_cut=spec[1],
                                                       supply_count=spec[0], side_roles=spec[3],
                                                       eligible_cuts=local_group_cuts[selected,d])
                                                  for (selected,d),spec in sorted(local_groups.items())],
                disjoint_group_deletion=dict(price_upper=retained_rank_drop, cases=len(cases),
                                             additive_packing=dict(deleted=list(best[0]), rank=remaining_rank,
                                                                   saving_upper=gate.show(packed_credit)[1],
                                                                   resulting_moment_upper=gate.show(gate.add(baseline, (0,packed_credit[1])))[1])),
                controls=['fraction-free elimination for singular, independent and negative pivot cases',
                          'rational row denominator clearing', 'exact reconstructed paid invoice'], seed=None)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run with assertions enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('peer_root','caller_path','gate_path','owned_path'):
        parser.add_argument(key, type=Path)
    parser.add_argument('--seconds', type=int, default=720)
    parser.add_argument('--maximal-cap', type=int, default=42)
    args = parser.parse_args()
    assert 0 < args.seconds <= 720 and 0 < args.maximal_cap <= 42
    print(json.dumps(run(**vars(args)), indent=2, sort_keys=True))
