"""Exact original MOVE stock by normalized row, chart, role and clock."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from time import monotonic
import argparse
import json
import sys


PRICE_PATH = 'round13/alternative/reprice.py'
PRICE_SHA = '97f4524d11a08cd3a09ceb9abc6b90f45ca579ac1c529a176b80a67201ecd90a'
SOURCE_HEAD = 'e3f8d39c43b07063dfc5b800f71c5d21015259e6'
SOURCE_TREE = '6678a6718f29a2da57efa3e748fa8ba997f6a46c'
CLIFFORD_PATH = 'canonical/research/shared-wire-split-composition/frozen/clifford_exact.py'
CLIFFORD_SHA = '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'


def load(deps, relative, expected):
    path = deps / relative
    if sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f'SHA-256 mismatch: {relative}')
    spec = spec_from_file_location(path.stem, path)
    price = module_from_spec(spec)
    sys.modules[spec.name] = price
    spec.loader.exec_module(price)
    return price


def scale(a, c):
    return a if c == 1 else {i: c * x for i, x in a.items() if c * x}


def add(a, b, c):
    result = a.copy()
    for j, x in b.items():
        if z := result.get(j, 0) + c * x:
            result[j] = z
        else:
            result.pop(j, None)
    return result


def insert(basis, row):
    x = row
    while x:
        p = min(x)
        if p not in basis:
            basis[p] = scale(x, 1 / x[p])
            return True
        x = add(x, basis[p], -x[p])
    return False


def key(row):
    return tuple((i, str(v)) for i, v in sorted(row.items()))


def proportional(row):
    return key(scale(row, 1 / row[min(row)])) if row else ()


def sweep(word, spaces, ranks, cap, seconds):
    p = word['public']
    n = len(word['program'])
    at = [*word['initial'], *([None] * word['owned_fields'])]
    rows = [{i: Q(1)} for i in range(p)] + [{} for _ in range(word['owned_fields'])]
    representative = {frozenset(s): f for f, s in reversed(list(enumerate(spaces)))}
    aliases = [representative[frozenset(s)] for s in spaces]
    last = [-1] * len(at)
    recent = [None] * len(at)
    open_chain = [[] for _ in at]
    chains = []
    stock = []
    began = monotonic()

    def close(j, t):
        if recent[j] is not None:
            recent[j]['latest_clock'] = t
            recent[j] = None

    def flush(j):
        if open_chain[j]:
            chains.append(open_chain[j])
            open_chain[j] = []

    reason = 'literal scope exhausted'
    for t, (op, j, *a) in enumerate(word['program']):
        if t % 128 == 0 and monotonic() - began >= seconds:
            reason = 'time cap'
            break
        if op == 'MOVE':
            if len(stock) == cap:
                reason = 'MOVE cap'
                break
            f, g, own = a
            assert at[j] == f and own == (j >= p)
            assert spaces[f] < spaces[g] or (own and spaces[g] < spaces[f])
            close(j, t)
            record = dict(event=t, role=j, owned=own, source=f, target=g,
                          canonical_source=aliases[f], canonical_target=aliases[g],
                          rank=abs(ranks[f] - ranks[g]), row=rows[j],
                          earliest_clock=last[j] + 1, latest_clock=n)
            stock.append(record)
            recent[j] = record
            open_chain[j].append(record)
            at[j] = g
            last[j] = t
            continue
        touched = (j, a[0]) if op in ('ADD', 'COPY') else (j,)
        for role in touched:
            close(role, t)
            flush(role)
            last[role] = t
        if op == 'ADD':
            assert at[j] == at[a[0]] == a[-1]
            rows[j] = add(rows[j], rows[a[0]], Q(a[1]))
        elif op == 'COPY':
            assert at[j] == at[a[0]] == a[-1] and not rows[j]
            rows[j] = scale(rows[a[0]], Q(a[1]))
        elif op == 'SCALE':
            assert at[j] == a[-1]
            rows[j] = scale(rows[j], Q(a[0]))
        else:
            assert op in ('INIT', 'CLEAR') and j >= p
            assert at[j] == (None if op == 'INIT' else a[0])
            at[j] = a[0] if op == 'INIT' else None
            rows[j] = {}
    if reason == 'literal scope exhausted':
        assert at == [*word['final'], *([None] * word['owned_fields'])]
    for j in range(len(at)):
        flush(j)
    assert sum(map(len, chains)) == len(stock)
    return stock, chains, reason


def classes(rows, field):
    groups = defaultdict(list)
    for row in rows:
        groups[field(row)].append(row)
    return groups


def summary(groups, digest=False):
    report = []
    for group, rows in sorted(groups.items()):
        basis = {}
        kept = []
        for row in rows:
            if insert(basis, row['row']):
                kept.append(row['event'])
        label = sha256(json.dumps(group, separators=(',', ':')).encode()).hexdigest() if digest else group
        report.append(dict(group=label, count=len(rows), basis_size=len(basis), basis_events=kept,
                           rank=rows[0]['rank']))
    return report


def binary_span(rows):
    basis = {}
    for x in rows:
        for p, y in sorted(basis.items(), reverse=True):
            if x & (1 << p):
                x ^= y
        if not x:
            continue
        p = x.bit_length() - 1
        for q, y in basis.items():
            if y & (1 << p):
                basis[q] = y ^ x
        basis[p] = x
    return tuple(v for _, v in sorted(basis.items()))


def physical_classes(clifford, frames, stock):
    tables = [clifford.canonical_frame(9, tuple(frame)).tab for frame in frames]
    inverses = list(map(clifford.inverse, tables))
    cosets = [binary_span(x | (z << 9) for x, z, _ in inv[9:]) for inv in inverses]
    signed = {}
    for row in stock:
        f, g, r = row['source'], row['target'], row['rank']
        if (f, g) not in signed:
            table = clifford.compose(tables[g], inverses[f])
            assert clifford.rank(x for x, _, _ in table[9:]) == r
            signed[f, g] = table
    return classes(stock, lambda row: signed[row['source'], row['target']]), classes(stock, lambda row: cosets[row['target']])


def cost_basis(groups, clock_order):
    discarded = []
    chosen = 0
    for rows in groups.values():
        order = sorted(rows, key=(lambda x: x['event']) if clock_order else (lambda x: (x['rank'], x['event'])))
        basis = {}
        for row in order:
            if insert(basis, row['row']):
                chosen += 1
            else:
                discarded.append(row)
    return discarded, chosen


def hist(rows):
    return Counter(r['rank'] for r in rows)


def difference(rows, report):
    billed = Counter()
    for row in report:
        billed[row['rank']] += row['basis_size']
    result = hist(rows)
    result.subtract(billed)
    assert all(v >= 0 for v in result.values())
    return result


def span_order(a, b):
    return a <= b or b <= a


def controls():
    p = {1: Q(1)}
    q = {2: Q(1)}
    b = {}
    assert insert(b, p) and insert(b, q)
    assert not insert(b, {1: Q(-2), 2: Q(3)})
    assert not insert(b, {})
    assert proportional({1: Q(7)}) == proportional({1: Q(-3)})
    assert proportional(p) != proportional(q)
    return dict(independent_pair_charged_twice=True, arbitrary_linear_dependence_charged_twice=True,
                exact_zero_unbilled=True, signed_proportional=True)


def run(inputs, deps, cap, seconds):
    assert __debug__
    price = load(deps, PRICE_PATH, PRICE_SHA)
    clifford = load(deps, CLIFFORD_PATH, CLIFFORD_SHA)
    w, result, caller = (price.authenticated(inputs, k) for k in price.PINS)
    target, paid, _, native, stages, _, _, ranks, spaces = price.invoice(w, caller, result)
    assert sum(native.values()) == 6279 and stages == 17
    stock, chains, reason = sweep(w, spaces, ranks, cap, seconds)
    literal = classes(stock, lambda row: (row['source'], row['target'], row['rank']))
    canonical = classes(stock, lambda row: (row['canonical_source'], row['canonical_target'], row['rank']))
    literal_report = summary(literal)
    canonical_report = summary(canonical)
    quotient, cosets = physical_classes(clifford, w['frames'], stock)
    quotient_report = summary(quotient, digest=True)
    discarded_optimistic, target_rank = cost_basis(cosets, False)
    discarded_chronological, chronological_rank = cost_basis(cosets, True)
    assert target_rank == chronological_rank
    compound = [chain for chain in chains if len(chain) > 1]
    single = [chain[0] for chain in chains if len(chain) == 1]
    serial = []
    serial_hist = Counter()
    serial_relax_hist = Counter()
    for chain in compound:
        first, last = chain[0], chain[-1]
        assert all(a['target'] == b['source'] for a, b in zip(chain, chain[1:]))
        assert all(first['row'] == row['row'] for row in chain)
        f, g = first['source'], last['target']
        comparable = span_order(spaces[f], spaces[g])
        assumed_rank = abs(ranks[f] - ranks[g]) if comparable else 0
        gain = hist(chain)
        if assumed_rank:
            gain[assumed_rank] -= 1
        serial_hist.update(gain)
        serial_relax_hist.update(hist(chain))
        serial.append(dict(events=[r['event'] for r in chain], role=first['role'],
                           first_chart=f, last_chart=g, owned=first['owned'], comparable=comparable,
                           direct_assumed_rank=assumed_rank, literal_identity=(f == g),
                           original_ranks=[r['rank'] for r in chain]))
    old_h = target.copy()
    old_h.subtract(paid)
    moment = lambda h: price.dot(h, lambda r: price.power(r, price.TARGET))
    baseline = moment(old_h)
    pending = native.copy()
    pending.subtract(hist(stock))
    assert all(v >= 0 for v in pending.values())

    def bill(saved):
        h = saved.copy()
        h.update(pending)
        stage = moment(h)
        return dict(saving_hist={r: n for r, n in sorted(saved.items()) if n},
                    stage_interval=list(map(str, stage)), caller_interval=[str(stages * q) for q in stage],
                    target_upper=str(baseline[1] + stages * stage[1]))

    same_map = difference(stock, canonical_report)
    literal_map = difference(stock, literal_report)
    same_quotient = difference(stock, quotient_report)
    single_events = {row['event'] for row in single}
    single_quotients = {q: [r for r in rows if r['event'] in single_events] for q, rows in quotient.items()}
    single_report = summary({q: rows for q, rows in single_quotients.items() if rows})
    combined = serial_relax_hist.copy()
    combined.update(difference(single, single_report))
    zero = [r['event'] for r in stock if not r['row']]
    return dict(source_head=SOURCE_HEAD, source_tree=SOURCE_TREE, target=str(price.TARGET),
                pins={PRICE_PATH: PRICE_SHA, CLIFFORD_PATH: CLIFFORD_SHA,
                      **{f'public/{k}': v for k, v in price.PINS.items()}},
                cap=dict(moves=cap, seconds=seconds), reason=reason, pending_moves=sum(pending.values()),
                native_moves=len(stock), stages=stages, paid_positions=sum(paid.values()),
                productive_targets=sum(target.values()), stage_deficit_upper=str(-baseline[0] / stages),
                baseline=list(map(str, baseline)), literal_classes=len(literal), canonical_classes=len(canonical),
                signed_quotient_classes=len(quotient), target_monomial_cosets=len(cosets),
                class_report=dict(literal=literal_report, canonical=canonical_report, signed_quotient=quotient_report),
                prices=dict(literal_identical_all_clock=bill(literal_map),
                            canonical_identical_all_clock=bill(same_map),
                            signed_quotient_phase_free_all_clock=bill(same_quotient),
                            adjacent_serial_direct_quotient=bill(serial_hist),
                            combined_chains_granted_free_and_singleton_quotients=bill(combined),
                            target_coset_minimum_paid_basis=bill(hist(discarded_optimistic)),
                            target_coset_chronological_basis=bill(hist(discarded_chronological))),
                target_coset_basis_size=target_rank,
                target_coset_all_clock_discarded=[r['event'] for r in discarded_optimistic],
                target_coset_chronological_discarded=[r['event'] for r in discarded_chronological],
                zero_rows=zero, serial_runs=serial, controls=controls(), site_tests=0,
                stock=[{**{k: v for k, v in r.items() if k != 'row'}, 'row_support': len(r['row']),
                        'row_sha256': sha256(json.dumps(key(r['row']), separators=(',', ':')).encode()).hexdigest()}
                       for r in stock])


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('inputs', 'deps'):
        p.add_argument(name, type=Path)
    p.add_argument('--cap', type=int, choices=range(1, 6280), default=6279)
    p.add_argument('--seconds', type=int, choices=range(1, 601), default=600)
    print(json.dumps(run(**vars(p.parse_args())), indent=2, sort_keys=True))
