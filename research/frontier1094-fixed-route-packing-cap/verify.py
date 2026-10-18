#!/usr/bin/env python3
"""Exact fixed-route rank-48 ceiling, independently of predecessor ceiling.py.

Apache-2.0. Josie Elliston, with substantial AI assistance (OpenAI Codex draft; Claude review and fixes).
"""
import copy
import gzip
import hashlib
import json
import sys
import tarfile
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
ROUTE = 'research/direct-delivery504-global/inputs/data-base/work/complex-nine-native/DATA-PHASES.json'
PLAN = 'research/complex-t16-rare-pattern-exchanges/data/PLAN.json'
SPEC = 'research/complex-t16-rare-pattern-exchanges/data/SPEC.json'
OWNERS = 'research/complex-t16-rare-pattern-exchanges/data/OWNERS.json.gz'
HOSTING_PROOF = 'research/gauge44-slots-t16/hosting/PROOF.md'
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBER = 'candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json'
RANKS = {0: 2, 8: 6, 16: 4, 32: 4, 48: 4}  # per port
LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
GRID = Q(1, 10**15)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_bytes())


def sources():
    for pin in read(HERE.relative_to(ROOT) / 'SOURCES.json')['files']:
        if pin['usage'] == 'input':
            need(sha((ROOT / pin['path']).read_bytes()) == pin['sha256'], 'source drift: ' + pin['path'])
    selected = read('certificates/selected-result.json')
    manifest_path = 'research/community-frontier1094-audit/SELECTED-SOURCE.json'
    need(selected['source_manifest'] == manifest_path, 'selected manifest path')
    need(selected['review'] == 'docs/research/community-batch1099-review.md', 'selected review path')
    need(selected['certificate'] == 'research/community-frontier1094-audit/ASSEMBLY.json', 'selected certificate path')
    need(selected['reproduce'] == 'make frontier1094-verify', 'selected replay command')
    route_bytes = (ROOT / ROUTE).read_bytes()
    manifest = read(manifest_path)
    need(manifest['files'][ROUTE] == sha(route_bytes), 'route not pinned by selected manifest')
    need(manifest['files'][PLAN] == sha((ROOT/PLAN).read_bytes()), 'plan not pinned by selected manifest')
    need(manifest['files'][SPEC] == sha((ROOT/SPEC).read_bytes()), 'spec not pinned by selected manifest')
    owners_bytes = (ROOT/OWNERS).read_bytes()
    need(manifest['files'][OWNERS] == sha(owners_bytes), 'owner map not pinned by selected manifest')
    need(manifest['files'][HOSTING_PROOF] == sha((ROOT/HOSTING_PROOF).read_bytes()),
         'parent hosting proof not pinned by selected manifest')
    replay = read('research/community-frontier1094-audit/REPLAY.json')
    spec = read(SPEC)
    need(replay['spec_sha256'] == sha((ROOT/SPEC).read_bytes()), 'replay/spec binding')
    need(spec['data']['plan_sha256'] == sha((ROOT/PLAN).read_bytes()), 'spec/plan binding')
    need(spec['data']['owners_sha256'] == sha(owners_bytes), 'spec/owner-map binding')
    with tarfile.open(ROOT / ARCHIVE, 'r:gz') as archive:
        member = archive.extractfile(MEMBER)
        need(member is not None and member.read() == route_bytes, 'selected archive route mismatch')
    return selected, replay, json.loads(route_bytes), read(PLAN), json.loads(gzip.decompress(owners_bytes))


def gf2_rank(vectors):
    basis = {}
    for value in vectors:
        need(type(value) is int and value > 0, 'invalid route axis')
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return len(basis)


def route_ranks(route):
    need(route['m'] == 73 and route['ports'] == 112, 'route geometry')
    recipes = route['recipes']
    need(len(recipes) == 112 and {r['port'] for r in recipes} == set(range(112)), 'route port coverage')
    total = Counter()
    for recipe in recipes:
        counts = Counter()
        for child in recipe['idle_children']:
            rank, axes = child['rank'], child['orthogonal_axes']
            need(type(rank) is int and rank >= 0, 'invalid route rank')
            need(rank == len(axes) == gf2_rank(axes), 'route rank/axes mismatch')
            counts[rank] += 1
        need(dict(counts) == RANKS, 'route child inventory changed')
        total.update(counts)
    return dict(sorted(total.items()))


def hosting(route, plan, owners, replay):
    """Selected pending-child capacities are the route ranks; hosting is a prefix.

    Every T16 pending-child group g = (owner replica, child, port) takes its
    capacity C_g from the selected plan's window catalogue. Check C_g against
    the route child rank, check that each hosted helper lies in its group's
    window, that hosted offsets tile the prefix [0, U_g) with U_g <= C_g, and
    that the remainders C_g - U_g reproduce the replay's idle profile.
    """
    rank = {(r['port'], i): c['rank'] for r in route['recipes']
            for i, c in enumerate(r['idle_children'])}
    windows = {}
    for key, (capacity, times) in plan['windows'].items():
        owner, child = map(int, key.split(','))
        windows[owner, child] = capacity, set(times)
    lift = plan['replica_lift']['replicas']
    children = {child for _, child in windows}
    need(set(windows) == {(o, c) for o in range(lift) for c in children}, 'window catalogue coverage')
    for (owner, child), (capacity, _) in windows.items():
        for port in range(route['ports']):
            need(capacity == rank[port, child], 'window capacity differs from route rank')
    need(all(rank[port, child] == 0 for port in range(route['ports'])
             for child in range(len(route['recipes'][0]['idle_children'])) if child not in children),
         'positive-rank route child missing from windows')
    need(len(owners) == 144*480, 'selected owner-map size')
    occupied = {}
    for item in owners:
        key = (item['owner_replica'], item['child'], item['port'])
        need((key[0], key[1]) in windows and 0 <= key[2] < route['ports'], 'owner outside catalogue')
        need(item['time'] in windows[key[0], key[1]][1], 'hosted call outside window')
        need(type(item['width']) is int and item['width'] > 0, 'hosted width')
        occupied.setdefault(key, []).append((item['offset'], item['width']))
    idle = Counter()
    for (owner, child), (capacity, _) in windows.items():
        for port in range(route['ports']):
            prefix = 0
            for offset, width in sorted(occupied.get((owner, child, port), [])):
                need(offset == prefix, 'hosted offsets are not a disjoint prefix')
                prefix += width
            need(prefix <= capacity, 'hosted width exceeds child capacity')
            if capacity > prefix:
                idle[capacity-prefix] += 1
    need(dict(idle) == {int(r): n for r, n in replay['idle_remainder_profile'].items()},
         'capacity minus hosted prefix differs from replay idle profile')
    return max(c for c, _ in windows.values()), len(windows)*route['ports']


def profile(replay, plan):
    calls, live = replay['complete_invocations'], plan['live']
    need((calls, live) == (144, 14336), 'selected calls/live changed')
    lift = plan['replica_lift']
    need((lift['source_replicas'], lift['replicas']) == (8, 16), 'selected replica lift changed')
    need(plan['profile'] == replay['complex_profile'] and plan['deficit'] == 5120,
         'plan/replay profile binding')
    complete = {int(r): n for r, n in replay['complex_profile'].items()}
    idle = {int(r): n for r, n in replay['idle_remainder_profile'].items()}
    local = {}
    for rank in set(complete) | set(idle):
        n = complete.get(rank, 0) - idle.get(rank, 0)
        need(n >= 0 and n % calls == 0, 'local profile split')
        if n:
            local[rank] = n // calls
    need(local == LOCAL, 'selected local word changed')
    need(sum(r*n for r, n in complete.items()) == 72*live + 64*calls,
         'selected coverage identity')
    mass = sum(r*n for r, n in idle.items())
    need(mass == 237024 and max(idle) <= 48, 'selected idle profile')
    return calls, live, local, mass, idle


def atanh(z):
    """Rational enclosure of atanh(z), 0 <= z <= 1/3."""
    need(0 <= z <= Q(1, 3), 'atanh domain')
    summation, power = Q(0), z
    for k in range(40):
        summation += power / (2*k + 1)
        power *= z*z
    return summation, summation + power / (81*(1-z*z))


@lru_cache(None)
def ln(integer):
    """Reduce integer to [1,2), then use atanh; unlike predecessor's ln(k-1) chain."""
    need(type(integer) is int and integer >= 1, 'log domain')
    if integer == 1:
        return Q(0), Q(0)
    j = integer.bit_length() - 1
    y = Q(integer, 1 << j)
    z = (y-1)/(y+1)
    zlo, zhi = atanh(z)
    tlo, thi = atanh(Q(1, 3))  # ln 2 = 2 atanh(1/3)
    return 2*(j*tlo+zlo), 2*(j*thi+zhi)


@lru_cache(None)
def log_ratio(m, r):
    ml, mh = ln(m)
    rl, rh = ln(r)
    return ml-rh, mh-rl


def exp_interval(low, high):
    need(0 <= low <= high < Q(1, 2), 'exp domain')
    def series(x):
        s = term = Q(1)
        for k in range(1, 17):
            term *= x/k
            s += term
        next_term = term*x/17
        return s, s + next_term/(1-x/18)
    return series(low)[0], series(high)[1]


def cost(rank, saving):
    lo, hi = log_ratio(73, rank)
    elo, ehi = exp_interval(saving*lo, saving*hi)
    return Q(rank, 73)*elo, Q(rank, 73)*ehi


def moment(local, calls, live, mass, cap, saving):
    low = high = Q(0)
    for rank, count in local.items():
        clo, chi = cost(rank, saving)
        low += calls*count*clo
        high += calls*count*chi
    clo, chi = cost(cap, saving)
    return (low+Q(mass, cap)*clo)/live, (high+Q(mass, cap)*chi)/live


def bracket(local, calls, live, mass, cap):
    left, right = 0, 50_000_000_000_000  # a in [0, 0.05]
    need(moment(local, calls, live, mass, cap, 0)[1] < 1, 'root lower sign')
    need(moment(local, calls, live, mass, cap, right*GRID)[0] > 1, 'root upper sign')
    while right-left > 1:
        mid = (left+right)//2
        low, high = moment(local, calls, live, mass, cap, mid*GRID)
        if high < 1:
            left = mid
        elif low > 1:
            right = mid
        else:
            raise ValueError('interval cannot separate grid sign')
    return left*GRID, right*GRID


def display(x):
    digits = 18
    scaled = x.numerator*10**digits//x.denominator
    return f'{scaled//10**digits}.{scaled%10**digits:0{digits}d}'


def result(selected, replay, route, plan, owners):
    ranks = route_ranks(route)
    max_capacity, groups = hosting(route, plan, owners, replay)
    need(max_capacity == max(ranks) == 48, 'maximal pending-child capacity')
    calls, live, local, mass, idle = profile(replay, plan)
    low, high = bracket(local, calls, live, mass, 48)
    old_low, old_high = bracket(local, calls, live, mass, 51)
    need((low, high) == (Q(1682094870064, 10**15), Q(1682094870065, 10**15)), 'rank-48 root')
    need((old_low, old_high) == (Q(1690054109088, 10**15), Q(1690054109089, 10**15)),
         'rank-51 predecessor root')
    need(moment(local, calls, live, mass, 48, low)[1] < 1 and
         moment(local, calls, live, mass, 48, high)[0] > 1, 'strict endpoint signs')
    kappa = Q(selected['kappa'])
    bit, complex_a = Q(replay['bit_lower']), Q(replay['complex_lower'])
    need(complex_a < low < high < bit, 'supplier ordering')
    cap_k = high/(1+high)
    old_cap_k = old_high/(1+old_high)
    need(kappa < cap_k < old_cap_k, 'kappa cap ordering')
    return {
        'status': 'PASS_FRONTIER1094_FIXED_ROUTE_PACKING_CAP',
        'scope': 'Selected fixed 112-port data-route children and local word; PR1012 coverage; whole-helper hosting into existing children; retained balanced transfer. Relaxation only, no new kappa.',
        'route_sha256': sha((ROOT/ROUTE).read_bytes()),
        'route_rank_counts': {str(r): n for r, n in ranks.items()},
        'pending_child_groups': groups,
        'max_pending_child_capacity': max_capacity,
        'calls': calls, 'live_families': live,
        'local_per_call': {str(r): n for r, n in sorted(local.items())},
        'selected_idle': {str(r): n for r, n in sorted(idle.items())},
        'idle_mass': mass, 'ideal_rank48_children': str(Q(mass, 48)),
        'a_root_bracket': [str(low), str(high)],
        'a_upper_decimal': display(high),
        'kappa_planning_upper_decimal': display(cap_k),
        'selected_fraction_of_cap_decimal': display(kappa/cap_k),
        'max_gain_over_selected_percent_decimal': display(100*(cap_k/kappa-1)),
        'rank51_a_root_bracket': [str(old_low), str(old_high)],
        'rank51_kappa_upper_decimal': display(old_cap_k),
        'selected_kappa': str(kappa),
        'selected_complex_primitive_lower': str(complex_a),
        'bit_primitive_lower': str(bit),
    }


def rejects(why, function, *args):
    try:
        function(*args)
    except ValueError as exc:
        need(why in str(exc), f'control rejected for wrong reason: {exc} (wanted {why})')
    else:
        raise ValueError('control accepted: ' + why)


def controls(replay, route, plan, owners):
    wrong = copy.deepcopy(route)
    wrong['recipes'][0]['idle_children'][0]['rank'] += 1
    rejects('rank/axes', route_ranks, wrong)
    wrong = copy.deepcopy(route)
    child = next(c for c in wrong['recipes'][0]['idle_children'] if c['rank'] == 48)
    child['rank'] = 49
    child['orthogonal_axes'].append(1 << 1024)
    rejects('inventory changed', route_ranks, wrong)
    # Mass-preserving local-word drift, applied consistently to plan and replay
    # so that the plan/replay binding passes and the local-word check must fire.
    wrong_replay, wrong_plan = copy.deepcopy(replay), copy.deepcopy(plan)
    for profile_ in (wrong_replay['complex_profile'], wrong_plan['profile']):
        profile_['1'] += 288
        profile_['2'] -= 144
    rejects('local word changed', profile, wrong_replay, wrong_plan)
    wrong = copy.deepcopy(plan)
    key = next(k for k, (c, _) in wrong['windows'].items() if c == 48)
    wrong['windows'][key][0] = 49
    rejects('window capacity differs', hosting, route, wrong, owners, replay)
    wrong = copy.deepcopy(owners)
    item = next(i for i in wrong if i['offset'] > 0)
    item['offset'] -= 1
    rejects('disjoint prefix', hosting, route, plan, wrong, replay)


def main():
    need(not sys.flags.optimize, 'run without -O')
    selected, replay, route, plan, owners = sources()
    controls(replay, route, plan, owners)
    output = result(selected, replay, route, plan, owners)
    encoded = (json.dumps(output, indent=2, sort_keys=True)+'\n').encode()
    path = HERE/'RESULT.json'
    if sys.argv[1:] == ['--write']:
        path.write_bytes(encoded)
    else:
        need(not sys.argv[1:], 'usage: verify.py [--write]')
        need(path.read_bytes() == encoded, 'RESULT.json differs from exact replay')
    print(output['status'], 'max_idle_rank=48', 'a_upper='+output['a_upper_decimal'],
          'kappa_cap='+output['kappa_planning_upper_decimal'], 'controls=5')


if __name__ == '__main__':
    main()
