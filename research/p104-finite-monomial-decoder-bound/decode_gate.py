"""Necessary support and earliest-resident gate for a one-child/two-arm decoder."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from time import monotonic
import argparse
import json


STOCK_SHA = '68202ba9326938cb0bf5abbabb893c3db01090a22acb6ba55afaef1dbae2bf9c'


class TimeCap(Exception):
    pass


def module(path):
    spec = spec_from_file_location(path.stem, path)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def first_observation(word, eligible, frame_cosets, stock, time):
    """Every literal input or changed state; free holding and source coset adapters."""
    wanted = defaultdict(set)
    for group in eligible:
        row = tuple(map(tuple, group['projective_row']))
        for e in group['members']:
            wanted[frame_cosets[e['source']], len(row), row[0][0]].add(row)
    first = defaultdict(dict)
    public = word['public']
    states = [{i: Q(1)} for i in range(public)] + [{} for _ in range(word['owned_fields'])]
    frames = [*word['initial'], *([None] * word['owned_fields'])]

    def observe(j, cut):
        row = states[j]
        if not row:
            return
        f = frame_cosets[frames[j]]
        allowed = wanted.get((f, len(row), min(row)))
        if allowed:
            candidate = stock.proportional(row)
            if candidate in allowed:
                first[f, candidate].setdefault(j, (cut, j, frames[j]))

    for j in range(public):
        observe(j, 0)
    for t, (op, j, *a) in enumerate(word['program']):
        if t % 256 == 0:
            time()
        if op == 'MOVE':
            assert frames[j] == a[0]
            frames[j] = a[1]
        elif op == 'ADD':
            assert frames[j] == frames[a[0]] == a[-1]
            states[j] = stock.add(states[j], states[a[0]], Q(a[1]))
        elif op == 'COPY':
            assert not states[j] and frames[j] == frames[a[0]] == a[-1]
            states[j] = stock.scale(states[a[0]], Q(a[1]))
        elif op == 'SCALE':
            assert frames[j] == a[-1]
            states[j] = stock.scale(states[j], Q(a[0]))
            # A nonzero SCALE leaves a projective row unchanged.
            assert Q(a[0])
            continue
        else:
            assert op in ('INIT', 'CLEAR')
            states[j] = {}
            frames[j] = a[0] if op == 'INIT' else None
            continue
        observe(j, t + 1)
    return first


def hist(rows):
    return Counter(e['rank'] for e in rows)


def controls():
    def possible(r, s, same):
        return s == 0 or (s == r and same)
    assert not possible(1, 2, False)
    assert not possible(3, 2, True)
    assert not possible(3, 3, False)
    assert possible(1, 1, True) and possible(3, 0, False)
    return dict(larger_support_rejected=True, one_point_cannot_halve_rank_three=True,
                different_equal_size_direction_rejected=True, zero_rank_source_bypass_allowed=True)


def run(root, seconds):
    started = monotonic()

    def time():
        if monotonic() - started >= seconds:
            raise TimeCap

    raw = (root / 'TYPED.json').read_bytes()
    if sha256(raw).hexdigest() != STOCK_SHA:
        raise ValueError('SHA-256 mismatch: TYPED.json')
    old = json.loads(raw)
    assert old['moves_pending'] == 0
    typed = module(root / 'typed_stock.py')
    stock = typed.load_stock(root)
    price = stock.load(root / 'deps', stock.PRICE_PATH, stock.PRICE_SHA)
    clifford = stock.load(root / 'deps', stock.CLIFFORD_PATH, stock.CLIFFORD_SHA)
    word = typed.authenticated(root, 'inputs/native/WORD.json.gz')
    table = [clifford.canonical_frame(9, tuple(f)).tab for f in word['frames']]
    inv = list(map(clifford.inverse, table))
    cosets = [stock.binary_span(x | (z << 9) for x, z, _ in q[9:]) for q in inv]

    @cache
    def direction(f, g):
        quotient_adjoint = clifford.compose(table[f], inv[g])
        return stock.binary_span(x for x, _, _ in quotient_adjoint[9:])

    def moment(values):
        return price.moment(values, price.TARGET)

    eligible = old['eligible_group_details']
    total_pairs = sum(len(g['members']) * (len(g['members']) - 1) for g in eligible)
    assert total_pairs == 2602
    modes = ('support_no_clock', 'support_literal_window', 'support_any_original_resident',
             'support_independent_original_resident')
    one = {mode: Counter() for mode in modes}
    many = {mode: Counter() for mode in modes}
    passed = Counter()
    survivors = {mode: [] for mode in modes}
    group_count = Counter()
    tested = 0
    completed_groups = 0
    reason = 'ordered pair scope exhausted'
    try:
        first = first_observation(word, eligible, cosets, stock, time)
        for group in eligible:
            time()
            rows = group['members']
            row_key = tuple(map(tuple, group['projective_row']))
            by_mode = {mode: [] for mode in modes}
            for retained in rows:
                f, g = retained['source'], retained['target']
                d = direction(f, g)
                assert len(d) == retained['rank']
                residents = first[cosets[f], row_key]
                born = min(residents.values())
                assert born[0] <= retained['earliest_clock'] <= retained['event']
                matched = {mode: [] for mode in modes}
                for removed in rows:
                    if retained is removed:
                        continue
                    tested += 1
                    want = direction(f, removed['target'])
                    if want and d != want:
                        continue
                    modes_here = [modes[0]]
                    if retained['earliest_clock'] <= removed['latest_clock']:
                        modes_here.append(modes[1])
                    if born[0] <= removed['latest_clock']:
                        modes_here.append(modes[2])
                    independent = min((candidate for role, candidate in residents.items()
                                       if role != removed['role'] or candidate[0] <= removed['event']),
                                      default=None)
                    if independent is not None and independent[0] <= removed['latest_clock']:
                        modes_here.append(modes[3])
                    for mode in modes_here:
                        matched[mode].append(removed)
                        passed[mode] += 1
                        survivors[mode].append(dict(retained=retained['event'], removed=removed['event'],
                                                    removed_rank=removed['rank'], decoder_rank=len(want),
                                                    source_observation=list(independent if mode == modes[3] else born)))
                for mode in modes:
                    by_mode[mode].append(matched[mode])
            for mode in modes:
                best = max(by_mode[mode], key=lambda rows: moment(hist(rows))[1])
                one[mode].update(hist(best))
                union_ids = {r['event'] for subset in by_mode[mode] for r in subset}
                union = [r for r in rows if r['event'] in union_ids]
                if len(union) == len(rows):
                    union.remove(min(union, key=lambda e: (e['rank'], e['event'])))
                many[mode].update(hist(union))
                group_count[mode] += bool(best)
            completed_groups += 1
    except TimeCap:
        reason = 'time cap'

    pending = Counter()
    for g in eligible[completed_groups:]:
        pending.update(hist(e for e in g['members'] if e['event'] != g['retained_event']))
    upper = Q(old['baseline'][1])
    stages = old['stages']

    def bill(values):
        stage = moment(values + pending)
        return dict(saving_hist=dict(values), stage_interval=list(map(str, stage)),
                    caller_interval=[str(stages * q) for q in stage], raw_margin_upper=str(upper + stages * stage[1]))

    return dict(status='NEGATIVE_FIXED_ONE_MONOMIAL_PER_ARM_UPPER' if Q(bill(many[modes[-1]])['raw_margin_upper']) < 0
                else 'UNRESOLVED_OR_POSITIVE_SUPPORT_UPPER',
                head=old['source_head'], target=old['target'], original_stock_sha256=STOCK_SHA,
                max_seconds=seconds, tested_pairs=tested, total_pairs=total_pairs,
                completed_groups=completed_groups, pending_groups=len(eligible)-completed_groups,
                pending_ideal_hist=dict(pending), stop_reason=reason, site_tests=0,
                scope='One source monomial plus one monomial of one completed old paid child per removed target, '
                      'same exact projective input, old scalar tape, original target deadlines, and no reuse of the '
                      'removed physical output as an independently available source.',
                passed_by_mode=dict(passed), eligible_groups_by_mode=dict(group_count),
                price_one_retained={mode: bill(one[mode]) for mode in modes},
                price_overgrant_multiple_retained={mode: bill(many[mode]) for mode in modes},
                survivors=survivors, controls=controls())


if __name__ == '__main__':
    assert __debug__
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--seconds', type=int, choices=range(1, 181), default=180)
    print(json.dumps(run(**vars(p.parse_args())), indent=2, sort_keys=True))
