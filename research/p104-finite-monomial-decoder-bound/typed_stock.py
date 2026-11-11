"""Exact one-input multi-output MOVE stock by proportional rows and target cosets."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import gzip
import json


HEAD = '4156504fa39efb51c550d218a9b94fe69dbce8f6'
TREE = 'f201bc8b5d1402ca40e7aa419269a58b7724798d'
PINS = {
    'inputs/native/WORD.json.gz': '75061d1e4b354e4cf36b690f30ddb2b257ed2f4e86509f87e17bb0f63eca126f',
    'inputs/native/RESULT.json': '75f34132b5b12b1a92f13b7a7c47ea3857f1955403090ae06b38dd9cf18aeb49',
    'inputs/caller/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'deps/round20/complex-stock/stock.py': '8a1968502614a3c2fe90699460e9d7f8d4667fa9072b2947c53f430a0efab49e',
    'deps/round13/alternative/reprice.py': '97f4524d11a08cd3a09ceb9abc6b90f45ca579ac1c529a176b80a67201ecd90a',
    'deps/canonical/research/shared-wire-split-composition/frozen/clifford_exact.py': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
}


def checked(root, key):
    path = root / key
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != PINS[key]:
        raise ValueError(f'SHA-256 mismatch: {key}')
    return path, raw


def authenticated(root, name):
    path, data = checked(root, name)
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def load_stock(root):
    path, _ = checked(root, 'deps/round20/complex-stock/stock.py')
    spec = spec_from_file_location(path.stem, path)
    stock = module_from_spec(spec)
    spec.loader.exec_module(stock)
    return stock


def invoice(word, caller, result, spaces, ranks):
    main = set(word['live']) | {112 + r for r in word['live']} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    assert len(main) == 400 and len(word['initial']) == len(word['final']) == word['public'] == 1501
    assert sorted(p for spec in caller['types'].values() for p in spec['ports']) == list(range(104))
    assert sorted(word['hosted']['Dports']) == sorted(caller['types']['A']['ports'])
    stages = [row[1] for row in caller['events'] if row[0] == 'J']
    assert stages == list(range(1, 18))
    repeat = len(stages)
    native = Counter(abs(ranks[f] - ranks[g]) for op, _, *a in word['program'] if op == 'MOVE' for f, g, _ in (a,))
    targets = Counter()
    for j, (f, g) in enumerate(zip(word['initial'], word['final'], strict=True)):
        if j not in main:
            assert spaces[f] < spaces[g]
            targets[ranks[g] - ranks[f]] += repeat
    for spec in caller['types'].values():
        for sign, h, *body in spec['diagonal']:
            assert sign == -1 and h == 0 and len(body) == repeat and set(body) <= {0, 1}
            targets[1 + 8 * sum(body)] += len(spec['ports'])
    paid = Counter({r: n * repeat for r, n in native.items()})
    for row in caller['events']:
        if row[0] == 'J':
            continue
        k, op, _, *a = row
        p = len(caller['types'][k]['ports'])
        if op == 'QUERY':
            paid[1] += p
        elif op in ('IDLE_ONE', 'IDLE_ODD'):
            paid[8 * len(a[0]) + (op == 'IDLE_ODD')] += p
    frozen = result['price']['after']
    physical = result['checks']['ODD-PHYSICAL-BINDING.json']['occurrence_and_geometry']
    for hist, field, physical_field in ((paid, 'P', 'paid'), (targets, 'T', 'targets')):
        assert {str(r): n for r, n in hist.items()} == frozen[field] == physical[physical_field]
    assert sum(native.values()) == 6281 and sum(paid.values()) == 110553 and sum(targets.values()) == 22461
    assert sum(r * (targets[r] - paid[r]) for r in targets.keys() | paid.keys()) == frozen['S'] == 1424
    assert result['caller_sha256'] == PINS['inputs/caller/CALLER.json']
    return targets, paid, native, repeat


def controls(stock):
    assert stock.proportional({1: Q(1), 3: Q(2)}) == stock.proportional({1: Q(-3), 3: Q(-6)})
    assert stock.proportional({1: Q(1), 3: Q(2)}) != stock.proportional({1: Q(1), 3: Q(3)})
    groups = [[{'rank': 3, 'event': 0}, {'rank': 1, 'event': 3}], [{'rank': 2, 'event': 4}]]
    assert [min(group, key=lambda r: (r['rank'], r['event']))['event'] for group in groups] == [3, 4]
    return dict(signed_proportional=True, one_coefficient_corruption_splits_group=True,
                cheapest_retained_charged=True)


def run(root, cap, seconds):
    assert __debug__
    w, frozen, caller = (authenticated(root, key) for key in list(PINS)[:3])
    stock = load_stock(root)
    price = stock.load(root / 'deps', stock.PRICE_PATH, stock.PRICE_SHA)
    clifford = stock.load(root / 'deps', stock.CLIFFORD_PATH, stock.CLIFFORD_SHA)
    ranks = list(map(len, w['frames']))
    spaces = [price.span(basis) for basis in w['frames']]
    targets, paid, native, stages = invoice(w, caller, frozen, spaces, ranks)
    rows, _, reason = stock.sweep(w, spaces, ranks, cap, seconds)
    tables = [clifford.canonical_frame(9, tuple(frame)).tab for frame in w['frames']]
    inverse = list(map(clifford.inverse, tables))
    cosets = [stock.binary_span(x | (z << 9) for x, z, _ in inv[9:]) for inv in inverse]
    groups = defaultdict(list)
    zero = []
    for row in rows:
        if row['row']:
            groups[stock.proportional(row['row'])].append(row)
        else:
            zero.append(row)
    assert sum(map(len, groups.values())) + len(zero) == len(rows)
    eligible = []
    saving = Counter()
    added = stock.hist(zero)
    member_ids = set()
    for coeff, group in groups.items():
        kinds = {cosets[row['target']] for row in group}
        if len(kinds) < 2:
            continue
        keep = min(group, key=lambda row: (row['rank'], row['event']))
        dropped = [row for row in group if row is not keep]
        saving.update(stock.hist(dropped))
        assert not member_ids.intersection(row['event'] for row in group)
        member_ids.update(row['event'] for row in group)
        eligible.append(dict(projective_row=coeff, target_cosets=len(kinds),
                             retained_event=keep['event'], retained_rank=keep['rank'],
                             members=[{k: v for k, v in row.items() if k != 'row'} for row in group]))
    old = targets.copy()
    old.subtract(paid)
    before = price.moment(old)
    pending = native.copy()
    pending.subtract(stock.hist(rows))
    assert all(n >= 0 for n in pending.values())
    grant = saving + added + pending
    stage = price.moment(grant)
    over_all = tuple(stages * q for q in stage)
    upper = before[1] + over_all[1]
    return dict(status='NEGATIVE_TYPED_STOCK_UPPER' if upper < 0 else 'POSITIVE_OPTIMISTIC_STOCK',
                scope='One retained original child per exact proportional row group and distinct target cosets; free typed outputs.',
                cap=dict(moves=cap, seconds=seconds), stop_reason=reason, source_head=HEAD, source_tree=TREE,
                input_pins=PINS, target=str(price.TARGET), stages=stages, moves_checked=len(rows),
                moves_pending=sum(pending.values()), original_paid_positions=sum(paid.values()),
                original_productive_targets=sum(targets.values()),
                row_groups=len(groups), nonzero_repeated_groups=sum(len(g)>1 for g in groups.values()),
                repeated_same_target_only_groups=sum(len(g)>1 and len({cosets[x['target']] for x in g})==1 for g in groups.values()),
                eligible_groups=len(eligible), eligible_members=len(member_ids), target_cosets=len({cosets[row['target']] for row in rows}),
                eligible_member_hist=dict(Counter(len(g['members']) for g in eligible)),
                eligible_group_details=eligible, zero_row_events=[r['event'] for r in zero],
                retained_hist=dict(Counter(g['retained_rank'] for g in eligible)),
                skipped_child_hist=dict(saving), pending_full_credit_hist={r: n for r, n in pending.items() if n},
                per_stage_saving_interval=list(map(str, stage)), complete_saving_interval=list(map(str, over_all)),
                baseline=list(map(str, before)), raw_margin_upper=str(upper), controls=controls(stock), site_tests=0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--cap', type=int, choices=range(1, 6282), default=6281)
    parser.add_argument('--seconds', type=int, choices=range(1, 481), default=480)
    print(json.dumps(run(**vars(parser.parse_args())), indent=2, sort_keys=True))
