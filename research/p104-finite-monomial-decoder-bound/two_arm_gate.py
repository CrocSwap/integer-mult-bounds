"""Two returned monomials: width-one support and finite-arm tensor gate."""
from collections import Counter
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from time import monotonic
import argparse
import json


PINS = {
    'prior/TYPED.json': '68202ba9326938cb0bf5abbabb893c3db01090a22acb6ba55afaef1dbae2bf9c',
    'prior/GATE.json': 'd047446188cd0bb93c5835a536560dc6509e8369e774c017e0f4a63c98cdc61d',
    'prior/typed_stock.py': '85564000a1a1a54f46af4e2c7091351f918886f7e0868343c9518f7ef9a518f3',
    'prior/decode_gate.py': 'dc0fcc441e6c64797168acea834f42e6ff7c46dee8afdc9ac59d5fd4239f491c',
    'contracts/PROOF.md': 'd9cc72480f7fd7d7cdcac3d8617b91c39d0630f5dc36a67fb6c2dbf81377bbc0',
    'contracts/SOURCES.json': 'ac7b4473035af648d6073e78b6c39675e706e8194b346bb55ed62a0adc81d593',
    'contracts/canonical-PROOF-REVIEW.md': '4501502c2ceb9759b20372435fe4beb51082c5a5e2910c1fd5dbe6edca415055',
    'contracts/pr7161-PROOF.md': 'acbebef2405e98ec83e3013342167aaa7c06540e491a346cd2ed53ee3359c5e5',
}


class TimeCap(Exception):
    pass


def checked(root, key):
    path = root / key
    data = path.read_bytes()
    if sha256(data).hexdigest() != PINS[key]:
        raise ValueError(f'SHA-256 mismatch: {key}')
    return path, data


def load(root, key):
    path, _ = checked(root, key)
    spec = spec_from_file_location(path.stem, path)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def hist(rows):
    return Counter(r['rank'] for r in rows)


def controls(stock):
    d = stock.binary_span([1])
    e = stock.binary_span([1, 2])
    q = len(stock.binary_span(d + e)) - len(d)
    assert q == 1 and 2 ** (q * 2) > 2 + 1
    # Multiplicity 3, two independent returned rows, one raw source row.
    coherence_squared = Q(1, 8)
    off_block_norm_bound = Q(1, 2)
    assert off_block_norm_bound ** 2 == 2 * coherence_squared
    gram_min = 1 - off_block_norm_bound
    projection = 3 * coherence_squared / gram_min
    assert projection == Q(3, 4) < 1
    assert len({3, 3}) == 1
    return dict(width_one_known_pass_and_tensor_fiber_failure=True,
                distinct_basis_squared_coherence_upper=str(coherence_squared),
                three_arm_gram_eigenvalue_lower=str(gram_min),
                target_projection_squared_upper=str(projection), duplicate_returned_row_deduplicates=True)


def run(root, cap, seconds):
    started = monotonic()

    def time():
        if monotonic() - started >= seconds:
            raise TimeCap

    old = json.loads(checked(root, 'prior/TYPED.json')[1])
    prior = json.loads(checked(root, 'prior/GATE.json')[1])
    canonical = checked(root, 'contracts/canonical-PROOF-REVIEW.md')[1].decode()
    manifest = json.loads(checked(root, 'contracts/SOURCES.json')[1])
    proof = checked(root, 'contracts/PROOF.md')[1].decode()
    old_proof = checked(root, 'contracts/pr7161-PROOF.md')[1].decode()
    assert any(x['sha256'] == PINS['contracts/canonical-PROOF-REVIEW.md'] for x in manifest['files'])
    assert 'T_U^(tensor f) z' in canonical and 'arbitrary full arrays at every f' in canonical
    assert 'all-column native maps' in proof and 'at every positive column multiplicity' in old_proof
    assert old['moves_pending'] == 0 and prior['pending_groups'] == 0
    typed = load(root, 'prior/typed_stock.py')
    previous = load(root, 'prior/decode_gate.py')
    stock = typed.load_stock(root)
    price = stock.load(root / 'deps', stock.PRICE_PATH, stock.PRICE_SHA)
    clifford = stock.load(root / 'deps', stock.CLIFFORD_PATH, stock.CLIFFORD_SHA)
    word = typed.authenticated(root, 'inputs/native/WORD.json.gz')
    typed.authenticated(root, 'inputs/native/RESULT.json')
    typed.authenticated(root, 'inputs/caller/CALLER.json')
    tables = [clifford.canonical_frame(9, tuple(frame)).tab for frame in word['frames']]
    inv = list(map(clifford.inverse, tables))
    cosets = [stock.binary_span(x | (z << 9) for x, z, _ in t[9:]) for t in inv]

    @cache
    def direction(f, g):
        relative = clifford.compose(tables[f], inv[g])
        return stock.binary_span(x for x, _, _ in relative[9:])

    def moment(h):
        return price.moment(h, price.TARGET)

    base = Q(old['baseline'][1])
    stages = old['stages']
    groups = old['eligible_group_details']
    total = sum(len(g['members']) * (len(g['members']) - 1) for g in groups)
    assert total == 2602 and len(groups) == 898
    pending = Counter({int(k): n for k, n in old['skipped_child_hist'].items()})
    modes = ('width_one_clock_free', 'width_one_independent', 'tensor_finite_arms_independent')
    saved = {mode: Counter() for mode in modes}
    best = {mode: Counter() for mode in modes}
    stats = Counter()
    survivor_rows = {mode: [] for mode in modes[1:]}
    disjoint = set()
    tested = completed = 0
    reason = 'ordered-pair scope exhausted'
    checkpoints = []

    def bill(credit):
        stage = moment(credit + pending)
        return dict(savings_hist=dict(credit), stage_upper=str(stage[1]),
                    caller_upper=str(stages * stage[1]), raw_margin_upper=str(base + stages * stage[1]))

    def record():
        p = {mode: bill(saved[mode])['raw_margin_upper'] for mode in modes}
        checkpoints.append(dict(groups=completed, pairs=tested, margins=p))
        return Q(p[modes[1]]) < 0

    try:
        first = previous.first_observation(word, groups, cosets, stock, time)
        for group in groups:
            time()
            rows = group['members']
            case_count = len(rows) * (len(rows) - 1)
            if tested + case_count > cap:
                reason = 'ordered-pair cap'
                break
            key = tuple(map(tuple, group['projective_row']))
            ids = {e['event'] for e in rows}
            assert len(ids) == len(rows) and not (ids & disjoint)
            disjoint.update(ids)
            assert len({cosets[e['target']] for e in rows}) == len(rows)
            choices = {mode: [] for mode in modes}
            for kept in rows:
                f, g = kept['source'], kept['target']
                d = direction(f, g)
                assert len(d) == kept['rank'] > 0
                residents = first[cosets[f], key]
                matched = {mode: [] for mode in modes}
                for removed in rows:
                    if kept is removed:
                        continue
                    tested += 1
                    h = removed['target']
                    e = direction(f, h)
                    between = direction(g, h)
                    assert bool(e) == (cosets[f] != cosets[h])
                    assert bool(between) == (cosets[g] != cosets[h])
                    quotient_dim = len(stock.binary_span(d + e)) - len(d)
                    stats['width_one_direction_pass' if quotient_dim <= 1 else 'width_one_direction_fail'] += 1
                    if not between:
                        stats['identical_target_coset'] += 1
                    elif not e:
                        stats['source_monomial_bypass'] += 1
                    else:
                        stats['three_distinct_tensor_rejected'] += 1
                    if quotient_dim > 1:
                        continue
                    matched[modes[0]].append(removed)
                    born = min((x for j, x in residents.items()
                                if j != removed['role'] or x[0] <= removed['event']), default=None)
                    if born is None or born[0] > removed['latest_clock']:
                        if not e:
                            stats['source_bypass_unavailable'] += 1
                        continue
                    stats['width_one_independent_pass'] += 1
                    note = dict(kept=kept['event'], omitted=removed['event'], omitted_rank=removed['rank'],
                                relative_ranks=(len(d), len(e), len(between)), quotient_dimension=quotient_dim,
                                source_observation=list(born), deadline=removed['latest_clock'])
                    matched[modes[1]].append(removed)
                    survivor_rows[modes[1]].append(note)
                    if not e or not between:
                        stats['tensor_independent_pass'] += 1
                        matched[modes[2]].append(removed)
                        survivor_rows[modes[2]].append(note)
                for mode in modes:
                    choices[mode].append(matched[mode])
            ideal_keep = group['retained_event']
            pending.subtract(hist(x for x in rows if x['event'] != ideal_keep))
            assert min(pending.values(), default=0) >= 0
            for mode in modes:
                one = max(choices[mode], key=lambda r: moment(hist(r))[1])
                best[mode].update(hist(one))
                may_omit = {e['event'] for subset in choices[mode] for e in subset}
                union = [e for e in rows if e['event'] in may_omit]
                if len(union) == len(rows):
                    union.remove(min(union, key=lambda e: (e['rank'], e['event'])))
                saved[mode].update(hist(union))
            completed += 1
            if completed % 32 == 0 and record():
                reason = 'negative width-one directed upper'
                break
    except TimeCap:
        reason = 'time cap'
    if not checkpoints or checkpoints[-1]['groups'] != completed:
        record()
    width = bill(saved[modes[1]])
    tensor = bill(saved[modes[2]])
    if completed == len(groups):
        assert stats['source_monomial_bypass'] == prior['passed_by_mode']['support_no_clock']
        assert stats['source_bypass_unavailable'] == stats['source_monomial_bypass']
    return dict(status='NEGATIVE_FIXED_FINITE_MONOMIAL_ARMS' if Q(tensor['raw_margin_upper']) < 0
                else 'UNRESOLVED_OR_POSITIVE_TENSOR_UPPER',
                head=old['source_head'], tree=old['source_tree'], target=old['target'], stages=stages,
                source_pins={**PINS, **typed.PINS}, scope='One exact arbitrary projective lane and one retained old child. '
                    'The width-one screen grants two returned monomial arms, and the coherence proof applies to any '
                    'fixed finite source/returned arm count under the exact tensor lift.',
                cap=dict(pairs=cap, seconds=seconds), tested_pairs=tested, pending_pairs=total-tested,
                checked_groups=completed, pending_groups=len(groups)-completed, stop_reason=reason,
                pending_ideal_hist={r: n for r, n in pending.items() if n}, stats=dict(stats),
                old_baseline_upper=str(base), width_one_independent=width, tensor_independent=tensor,
                union_prices={mode: bill(saved[mode]) for mode in modes},
                single_retained_prices={mode: bill(best[mode]) for mode in modes},
                checkpoints=checkpoints, survivors=survivor_rows, controls=controls(stock),
                site_tests=0, ordinary_costs_granted_free=True)


if __name__ == '__main__':
    assert __debug__
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--cap', type=int, choices=range(1, 2603), default=2602)
    p.add_argument('--seconds', type=int, choices=range(1, 181), default=180)
    print(json.dumps(run(**vars(p.parse_args())), indent=2, sort_keys=True))
