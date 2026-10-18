#!/usr/bin/env python3
"""Exact width-pattern dual certificate. No optimizer or network is used.

Frame-invoice logic reimplemented from PR2322's paid_profile using explicit
GF(2)^9 subspace sets, rather than the producer's row-reduction implementation.
This checks the cost interface, not the scalar circuit's correctness.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIDTHS = (4, 5, 7, 8, 9)
RANKS = (8, 16, 32, 48)
EXPECTED_STOCK = {8: 49728, 16: 33152, 32: 33152, 48: 33152}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def canonical(value):
    # JSON round-trip normalizes integer inventory keys to strings before
    # sorting, so in-memory recounts and parsed receipts have the same order.
    return json.dumps(json.loads(json.dumps(value)), sort_keys=True, separators=(',', ':'))


@lru_cache(None)
def space(frame):
    result = {0}
    for x in frame:
        need(type(x) is int and 0 < x < 512, 'invalid frame vector')
        result |= {y ^ x for y in result}
    return frozenset(result)


def dim(subspace):
    return len(subspace).bit_length() - 1


def mapped(columns, x):
    result = 0
    for bit, column in enumerate(columns):
        if (x >> bit) & 1:
            result ^= column
    return result


def invoice(word):
    need([word['report'][k] for k in ('v', 'h', 'R')] == [112, 9, 480], 'word geometry')
    ports = word['ports']
    need(len(ports) == len(set(ports)) == 112, 'ports')
    removed = set(word['removed'])
    need(len(removed) == len(word['removed']) == 80 and removed <= set(range(224, 704)), 'removed roles')
    live = set(range(704)) - removed
    cur = [space((p,)) for p in ports] + [space(())] * 592
    for role, frame in word['start_extra'].items():
        role = int(role)
        need(role in live and role >= 224, 'helper entrance')
        cur[role] = space(tuple(frame))
    initial = list(cur)
    full = frozenset(range(512))
    ends = [full] * 112 + [frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0) for p in ports] + [full] * 480
    for role, frame in word['helper_final'].items():
        role = int(role)
        need(role in live and role >= 224, 'helper exit')
        ends[role] = space(tuple(frame))
    paid = Counter()

    def climb(role, frame):
        need(role in live and cur[role] <= frame, 'nonmonotone or absent role')
        degree = dim(frame) - dim(cur[role])
        if degree:
            paid[degree] += 1
        cur[role] = frame

    def gate(event):
        need(event[0] in ('add', 'scale'), 'unknown gate')
        for role in event[1:3] if event[0] == 'add' else event[1:2]:
            climb(role, space(tuple(event[-1])))

    for event in word['A']:
        gate(event)
    levels = {int(t): space(tuple(f)) for t, f in word['target_levels'].items()}
    need(all(cur[112+t] == levels.get(t, space(())) for t in range(112)), 'cut targets')
    need(len(word['centers']) == len(word['center_frames']), 'cut center count')
    for role, frame in zip(word['centers'], word['center_frames']):
        frame = space(tuple(frame))
        need(cur[role] == frame, 'cut producer')
        readers = {levels.get(e[1]-112, space(())) for e in word['cut'] if e[2] == role}
        for reader in sorted(readers, key=lambda s: (-len(s), tuple(sorted(s)))):
            need(reader <= frame, 'unnested private copy')
            degree = dim(frame)-dim(reader)
            if degree:
                paid[degree] += 1
            frame = reader
    warps = defaultdict(list)
    for record in word['warps']:
        need(0 <= record[0] <= len(word['B']), 'warp position')
        warps[record[0]].append(record)
    for position in range(len(word['B'])+1):
        for _, role, columns, old, new in warps[position]:
            old, new = space(tuple(old)), space(tuple(new))
            need(role in live and cur[role] == old, 'handoff source frame')
            need(len(columns) == 9 and space(tuple(columns)) == full, 'singular warp')
            need(frozenset(mapped(columns, x) for x in old) == new, 'warp image')
            cur[role] = new
        if position < len(word['B']):
            gate(word['B'][position])
    for event in word['restore']:
        gate(event)
    for role in sorted(live):
        climb(role, ends[role])
    widths = Counter(dim(ends[r])-dim(initial[r]) for r in live if r >= 224)
    need(all(s > 0 for s in widths), 'nonpositive width')
    need(dict(paid) == {int(k): v for k, v in word['report']['local_profile'].items()}, 'reported local profile')
    need(dict(widths) == {int(k): v for k, v in word['report']['width_inventory'].items()}, 'reported widths')
    return dict(sorted(paid.items())), dict(sorted(widths.items()))


def geometry(plan):
    need((plan['M'], plan['live'], plan['deficit']) == (73, 66304, 23680), 'parent geometry')
    order = [tuple(x) for x in plan['order']]
    need(len(order) == 666 and set(order) == set(itertools.product(range(9), range(74))), 'call permutation')
    need(set(plan['windows']) == {f'{r},{c}' for r in range(74) for c in range(18)}, 'window keys')
    stock = Counter()
    for rank, times in plan['windows'].values():
        need(rank in RANKS and len(times) == len(set(times)) and set(times) <= set(range(666)), 'window contents')
        stock[rank] += 112
    need(dict(stock) == EXPECTED_STOCK, 'bin inventory')
    return dict(sorted(stock.items()))


def power_engine(source_bytes):
    spec = importlib.util.spec_from_file_location('width_cap_moment', ROOT/'vendor/fine_moment.py')
    module = importlib.util.module_from_spec(spec)
    # Execute the bytes authenticated by run(), never an unrelated .pyc cache.
    exec(compile(source_bytes, str(ROOT/'vendor/fine_moment.py'), 'exec'), module.__dict__)
    # Same directed algorithm and explicit tails; this coarse bound needs no
    # 3000-digit endpoint. Integer fallback suffices in the standard library.
    module.SH = 256
    module.GRID = 1 << 256
    module.LOG_TERMS = 100
    module.EXP_TERMS = 96
    return module


def certify(local, inventory, stock, dual, engine):
    b = Q(dual['threshold'])
    need(0 < b < Q(1, 100), 'threshold range')
    need(tuple(dual['widths']) == WIDTHS and tuple(dual['bin_ranks']) == RANKS, 'dual axes')
    y = list(map(Q, dual['width_dual']))
    z = list(map(Q, dual['bin_dual']))
    need(len(y) == 5 and len(z) == 4, 'dual dimensions')
    f_lower = {0: Q(0)}
    for r in range(1, 49):
        lo, _ = engine.moment(73, 1, [(r, 1)], b)
        f_lower[r] = (73*lo-r)/b
    slacks = []
    for R, price in zip(RANKS, z):
        for counts in itertools.product(*(range(R//s+1) for s in WIDTHS)):
            rem = R-sum(n*s for n, s in zip(counts, WIDTHS))
            if rem < 0:
                continue
            slack = f_lower[rem]-price-sum(n*v for n, v in zip(counts, y))
            need(slack >= 0, f'infeasible dual: capacity {R}, counts {counts}')
            slacks.append(slack)
    need(len(slacks) == 1163, 'pattern enumeration')
    D = sum(666*inventory[s]*v for s, v in zip(WIDTHS, y)) + sum(stock[r]*v for r, v in zip(RANKS, z))
    idle_mass = sum(r*n for r, n in stock.items())-666*sum(s*n for s, n in inventory.items())
    local_mass = 666*sum(r*n for r, n in local.items())
    need(idle_mass >= 0 and local_mass+idle_mass == 73*66304-23680, 'rank mass')
    local_lo, _ = engine.moment(73, 66304, [(r, 666*n) for r, n in local.items()], b)
    lower = local_lo+(idle_mass+b*D)/(73*66304)
    need(lower > 1, 'cap not established')
    return dict(threshold=str(b), pattern_count=len(slacks), minimum_dual_slack=str(min(slacks)), idle_excess_lower=str(D), idle_rank_mass=idle_mass, total_rank_mass=local_mass+idle_mass, moment_lower=str(lower), moment_margin=str(lower-1))


def rejected(label, action):
    try:
        action()
    except ValueError as error:
        return dict(control=label, rejection=str(error))
    raise ValueError('negative control passed: '+label)


def run():
    pins = read(ROOT/'INPUTS.json')
    verified = {}
    for entry in pins['sources']:
        data = (ROOT/entry['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == entry['sha256'], 'source digest: '+entry['path'])
        verified[entry['path']] = data
        if 'uncompressed_sha256' in entry:
            need(hashlib.sha256(gzip.decompress(data)).hexdigest() == entry['uncompressed_sha256'], 'uncompressed digest')
    extra = read(ROOT/'inputs/word80-extra.json.gz')
    base = read(ROOT/'inputs/word80-base.json.gz')
    local, inventory = invoice(extra)
    base_local, base_inventory = invoice(base)
    need(inventory == base_inventory == {4: 4, 5: 4, 7: 36, 8: 84, 9: 272}, 'common widths')
    delta = {r: base_local.get(r, 0)-local.get(r, 0) for r in set(base_local)|set(local)}
    need({r: n for r, n in delta.items() if n} == {1: 16, 2: -8}, 'mixture envelope')
    plan = read(ROOT/'inputs/pr2269-plan.json.gz')
    stock = geometry(plan)
    dual = read(ROOT/'DUAL.json')
    engine = power_engine(verified['vendor/fine_moment.py'])
    result = certify(local, inventory, stock, dual, engine)
    parent = {int(k): v for k, v in read(ROOT/'inputs/pr2269-profile.json').items()}
    _, parent_hi = engine.moment(73, 66304, list(parent.items()), Q(dual['threshold']))
    need(parent_hi < 1, 'attained parent positive control')
    controls = []
    bad = copy.deepcopy(extra); bad['report']['local_profile']['1'] -= 1
    controls.append(rejected('undercharged invoice', lambda: invoice(bad)))
    bad = copy.deepcopy(extra); bad['report']['width_inventory']['9'] -= 1
    controls.append(rejected('missing width-9 helper', lambda: invoice(bad)))
    bad = copy.deepcopy(extra); bad['B'][0][-1] = []
    controls.append(rejected('nonmonotone gate', lambda: invoice(bad)))
    bad = copy.deepcopy(extra); bad['warps'][0][4] = []
    controls.append(rejected('incorrect warp image', lambda: invoice(bad)))
    bad = copy.deepcopy(plan); bad['order'][1] = bad['order'][0]
    controls.append(rejected('duplicate call', lambda: geometry(bad)))
    bad = copy.deepcopy(plan); bad['windows']['0,0'][0] = 48
    controls.append(rejected('altered bin inventory', lambda: geometry(bad)))
    bad = copy.deepcopy(dual); bad['bin_dual'][0] = str(Q(bad['bin_dual'][0])+1)
    controls.append(rejected('overstated dual', lambda: certify(local, inventory, stock, bad, engine)))
    bad = copy.deepcopy(dual); bad['threshold'] = '1/1000'
    controls.append(rejected('unsupported stronger cap', lambda: certify(local, inventory, stock, bad, engine)))
    return dict(schema=1, scope='Fixed PR2339 words, 666 calls, unsplit helpers, unchanged PR2269 bin stock; arbitrary fractional patterns and free chronology.', sources=pins, dual_sha256=hashlib.sha256((ROOT/'DUAL.json').read_bytes()).hexdigest(), extra_local_profile=local, base_local_profile=base_local, helper_widths=inventory, bin_stock=stock, certificate=result, parent_moment_upper=str(parent_hi), controls=controls)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, help='write a new receipt; refuses to overwrite')
    args = parser.parse_args()
    if args.record:
        need(not args.record.exists(), 'receipt already exists')
    result = run()
    if args.record:
        with args.record.open('x') as output:
            output.write(json.dumps(result, sort_keys=True, indent=2)+'\n')
    else:
        need(canonical(result) == canonical(read(ROOT/'EXPECTED.json')), 'receipt mismatch')
    c = result['certificate']
    print('PASS_T74_LOW_ALIAS_WIDTH_CAP', c['threshold'], 'patterns', c['pattern_count'], 'margin', float(Q(c['moment_margin'])), 'rejecting_controls', len(result['controls']))


if __name__ == '__main__':
    main()
