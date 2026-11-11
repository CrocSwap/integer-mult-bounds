"""Exact two-donor normalized support inventory on the pinned #7277 word."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import runpy
from signal import SIGALRM, alarm, signal
from time import monotonic

HEAD = 'ed090b57ed88f8859e5ff4643645099e6ba856ea'
WORD = 'round30/complex/source/inputs/WORD.json.gz'
EARLY = 'round30/complex/source/inputs/EARLY-RESULT.json'
CORE = 'round41/independent/replay_core.py'
LEAD_PRICE = 'round41/lead/r41-price-support/PRICE.json'
LEAD_SUPPORT = 'round41/lead/r41-price-support/SUPPORT.json'
INDEPENDENT = 'round41/independent/RESULT.json'
PINS = {
    'round30/complex/audit.py': '67b006627fd4e07c349f48f31e6d541c62804416bdc85f664a3607dd1b386efb',
    'round30/complex/source/inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    EARLY: '691025fe95c7938a6da211244d4d5b6187d88a9de1acff0862eeb7f0ce7deaa7',
    WORD: '2c523ce6fdd6092d758fedc3602a0bcedb692b9766f1e41f903351ba4dee1756',
    'round30/complex/source/powers.py': 'c0c460b464d7c836fb887010b57119be322aae686736b86820aae3544d380bee',
    CORE: 'fd7a1a7f9cb8f71caa5e0d89ed16ea056503fa283bc05f655eb0da7e8d5fc6e0',
    INDEPENDENT: '1b993aa8c66ffce5d2d9f13cafae320c62230722d599d251fa61afc6534b1bc7',
    LEAD_PRICE: '1efe8b52e02a8db0ac6a04cdf6b943e515badee5fc0b7bea6ea3fe4a30fd1d01',
    LEAD_SUPPORT: 'c31c8425e2a99fe15a9ffa48662dacca4eda2b778d55ceceae2978a9bdb12f3c',
}
R42_UPPER = [
    '55568818205146215263695136468307142417029952282393/31250000000000000000000000000000000000000000000',
    '889101091282339444219122183492914278672479236518509/500000000000000000000000000000000000000000000000',
]


def load(roots):
    result = {}
    for key, digest in PINS.items():
        root, path = key.split('/', 1)
        file = roots[root] / path
        raw = file.read_bytes()
        assert sha256(raw).hexdigest() == digest, ('changed dependency', key)
        result[key] = file, raw
    return result


def decode(raw):
    def unique(pairs):
        result = dict(pairs)
        assert len(result) == len(pairs), 'duplicate JSON key'
        return result
    return json.loads(raw, object_pairs_hook=unique)


def write(out, name, value):
    tmp = out / (name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
    tmp.replace(out / name)


def solve(target, left, right):
    """Use two independent coordinate equations and check every coordinate."""
    xd, x = target
    ud, u = left
    vd, v = right
    assert x and u and v and xd > 0 and ud > 0 and vd > 0
    indices = u.keys() | v.keys()
    i = min(indices)
    ui, vi = u.get(i, 0), v.get(i, 0)
    for j in sorted(indices - {i}):
        determinant = ui * v.get(j, 0) - vi * u.get(j, 0)
        if determinant:
            break
    else:
        return 'dependent', None
    xi, xj = x.get(i, 0), x.get(j, 0)
    a = xi * v.get(j, 0) - xj * vi
    b = ui * xj - u.get(j, 0) * xi
    if any(x.get(k, 0) * determinant != a * u.get(k, 0) + b * v.get(k, 0)
           for k in x.keys() | indices):
        return 'nonzero_residual', None
    if not a or not b:
        return 'single_donor', None
    return 'supported', ([i, j], Q(a * ud, determinant * xd), Q(b * vd, determinant * xd))


def controls():
    x = (6, {0: -1, 2: 5, 3: 4})
    u = (2, {0: 1, 2: 1})
    v = (3, {0: 1, 2: -2, 3: -2})
    assert solve(x, u, v) == ('supported', ([0, 2], Q(1, 3), Q(-1)))
    assert solve((6, {0: -1, 2: 5, 3: -4}), u, v)[0] == 'nonzero_residual'
    assert solve((6, {0: -1, 2: 5, 3: 4, 4: 1}), u, v)[0] == 'nonzero_residual'
    assert solve(x, u, (7, {0: -4, 2: -4}))[0] == 'dependent'
    assert solve(u, u, v)[0] == 'single_donor'
    return ['signed_rational_coefficients', 'off_pivot_sign_rejected', 'outside_union_rejected',
            'dependent_pair_and_zero_coefficient_distinguished']


def receipt_stock(data, word):
    prior_price, lead, other = [decode(data[name][1]) for name in (LEAD_PRICE, LEAD_SUPPORT, INDEPENDENT)]
    assert lead['head'] == prior_price['head'] == other['scientific_head'] == HEAD
    assert lead['price_sha256'] == PINS[LEAD_PRICE] and other['core_sha256'] == PINS[CORE]
    assert lead['full_tape_exhausted'] and other['scope_exhausted']
    assert not lead['unresolved'] and not other['exact_zero_moves']
    assert lead['support_survivor_sites'] == other['match_count'] == 0
    census = {}
    for site, a, b in zip(prior_price['sites'], lead['rows'], other['records'], strict=True):
        t = site['clock']
        op, owner, source, destination, owned = word['program'][t]
        assert op == 'MOVE' and owned and t not in census
        assert (owner, source, destination) == (site['role'], site['source'], site['destination'])
        assert (t, owner, source, destination, site['rank']) == (
            b['literal_index'], b['role'], b['from'], b['to'], b['rank'])
        assert (t, owner, source, destination) == (a['clock'], a['role'], a['source'], a['destination'])
        assert a['moved_row_nonzero'] and not a['matches'] and not b['matches']
        assert a['live_other_roles'] == b['live_destination_roles']
        n = b['nonzero_destination_roles']
        assert n == a['nonzero_peer_rows']
        census[t] = site | {'nonzero_donors': n, 'pairs': n * (n - 1) // 2}
    assert len(census) == 47 and sum(bool(r['pairs']) for r in census.values()) == 44
    assert sum(r['pairs'] for r in census.values()) == 2767
    return prior_price, census


class SoftCap(Exception):
    """Stop between exact tests, preserving completed coverage."""


def run(roots, out, seconds, pair_cap, started):
    checks = controls()
    data = load(roots)
    word = decode(gzip.decompress(data[WORD][1]))
    prior_price, census = receipt_stock(data, word)
    audit = runpy.run_path(str(data['round30/complex/audit.py'][0]))
    power = runpy.run_path(str(data['round30/complex/source/powers.py'][0]))['power']
    _, rank, _, edges, _, _, copies, paid, productive, _ = audit['read_model']()
    assert audit['HEAD'] == HEAD and copies == prior_price['copies'] == 17 and len(edges) == 137891
    assert dict(paid) == {int(k): v for k, v in prior_price['original_paid'].items()}
    assert dict(productive) == {int(k): v for k, v in prior_price['original_productive'].items()}
    k = Q(decode(data[EARLY][1])['price']['independent_raw_bracket'][1])
    assert k == Q(prior_price['crossing_upper'])
    for r in census.values():
        assert r['rank'] == rank(r['source'], r['destination'], True)
    tariff = cache(lambda r: power(r, k))

    def price(hist):
        lo = hi = Q(0)
        for r, count in hist.items():
            a, b = tariff(r)
            lo += count * (a if count >= 0 else b)
            hi += count * (b if count >= 0 else a)
        return list(map(str, (lo, hi)))

    net = productive.copy()
    net.subtract(paid)
    baseline = price(net)
    assert baseline == prior_price['baseline_interval'] and Q(baseline[1]) < 0

    def quote(clocks):
        assert len(clocks) == len(set(clocks))
        ranks = Counter(census[t]['rank'] for t in clocks)
        debits = {r: n * copies for r, n in ranks.items()}
        assert all(n <= paid[r] for r, n in debits.items())
        new = net.copy()
        new.update(debits)
        return dict(removed_ranks_per_copy=dict(ranks), saving_interval=price(debits),
                    complete_margin_interval=price(new))

    eligible = [t for t, site in census.items() if site['pairs']]
    whole = quote(eligible)
    assert list(map(Q, whole['saving_interval'])) == list(map(Q, R42_UPPER))
    write(out, 'PRICE.json', dict(head=HEAD, pins=PINS, crossing_upper=str(k), copies=copies,
          baseline_interval=baseline, original_paid=dict(paid), original_productive=dict(productive),
          eligible_sites=len(eligible), pairs=2767, cap=pair_cap, seconds_cap=seconds,
          sites=list(census.values()), whole_optimistic_upper=whole,
          local_change_per_copy=dict(add_CLEAR=1, add_INIT=1, add_COPY=1, add_ADD=1, remove_MOVE=1,
                                     net_literal_events=3, new_owner_slots=0),
          grant='Remove each eligible owned MOVE once across all copies, granting all other costs free.'))
    if Q(whole['complete_margin_interval'][1]) <= 0:
        return

    progress, witnesses, visited_sites = {}, [], set()
    solved = 0
    deadline = started + seconds - 2

    def visit(t, role, source, destination, size, charts, rows, live):
        nonlocal solved
        site = census[t]
        assert (role, source, destination, size) == tuple(site[k] for k in ('role', 'source', 'destination', 'rank'))
        assert role in live and rows[role][1]
        donors = [r for r, chart in enumerate(charts) if r != role and chart == destination and rows[r][1]]
        assert len(donors) == site['nonzero_donors']
        visited_sites.add(t)
        counts = progress[t] = Counter()
        for a, b in combinations(donors, 2):
            if solved >= pair_cap or monotonic() >= deadline:
                raise SoftCap
            status, result = solve(rows[role], rows[a], rows[b])
            counts[status] += 1
            solved += 1
            if result is not None:
                pivots, alpha, beta = result
                snapshot = [(rows[r][0], rows[r][1].copy()) for r in (role, a, b)]
                witnesses.append(dict(clock=t, role=role, donor_roles=[a, b], coefficients=[str(alpha), str(beta)],
                                      pivots=pivots, normalized_rows=snapshot,
                                      proposed_events=[['CLEAR', role, source], ['INIT', role, destination],
                                                       ['COPY', role, a, str(alpha), destination],
                                                       ['ADD', role, b, str(beta), destination]]))

    core = runpy.run_path(str(data[CORE][0]))
    assert core['HEAD'] == HEAD and core['SHA'] == PINS[WORD]
    core_report = None
    try:
        core_report = core['audit'](word, started, seconds - 2, visit)
    except SoftCap:
        pass
    remaining = {t: site['pairs'] - sum(progress.get(t, {}).values()) for t, site in census.items()
                 if site['pairs'] > sum(progress.get(t, {}).values())}
    assert sum(remaining.values()) + solved == 2767
    status_counts = Counter()
    for row in progress.values():
        status_counts.update(row)
    assert sum(status_counts.values()) == solved and status_counts['single_donor'] == 0
    if core_report and core_report['scope_exhausted']:
        assert len(visited_sites) == 47 and not remaining and not core_report['exact_zero_moves']
        assert core_report['paid_owned_histogram'] == core['OWNED_PAID']
    possible = sorted(set(remaining) | {w['clock'] for w in witnesses})
    write(out, 'SUPPORT.json', dict(head=HEAD, pins=PINS, controls=checks,
          price_sha256=sha256((out / 'PRICE.json').read_bytes()).hexdigest(),
          visited_pairs=solved, unvisited_pairs=sum(remaining.values()), unvisited_by_clock=remaining,
          status_counts=dict(status_counts), site_status_counts={t: dict(c) for t, c in progress.items()},
          support_witnesses=witnesses, surviving_sites=len({w['clock'] for w in witnesses}),
          whole_post_support_optimistic_upper=quote(possible), core_receipt=core_report,
          scope_exhausted=not remaining, status='support_only' if witnesses else 'capped' if remaining else 'excluded',
          pending_costs=['lawful signed coefficients and physical phase', 'ordinary COPY/ADD and setup',
                         'ownership, dirty restoration, recovery, precision and tape', 'complete independent replay']))


def main():
    p = ArgumentParser()
    p.add_argument('round30', type=Path, nargs='?')
    p.add_argument('round41', type=Path, nargs='?')
    p.add_argument('out', type=Path, nargs='?')
    p.add_argument('--seconds', type=int, default=120, choices=range(3, 121), metavar='3..120')
    p.add_argument('--pairs', type=int, default=2767, choices=range(1, 2768), metavar='1..2767')
    p.add_argument('--controls-only', action='store_true')
    a = p.parse_args()
    if a.controls_only:
        print(json.dumps(controls()))
        return
    if None in (a.round30, a.round41, a.out):
        p.error('explicit Round 30 and Round 41 roots and a fresh output are required')
    a.out.mkdir()

    def timeout(*_):
        raise TimeoutError('hard runner deadline')

    signal(SIGALRM, timeout)
    alarm(a.seconds)
    try:
        run({'round30': a.round30, 'round41': a.round41}, a.out, a.seconds, a.pairs, monotonic())
    except TimeoutError:
        write(a.out, 'TIMEOUT.json', dict(head=HEAD, status='hard_timeout', pairs_unverified=2767,
                                       price_saved=(a.out / 'PRICE.json').is_file(), seconds_cap=a.seconds))
        raise SystemExit(2)
    finally:
        alarm(0)


if __name__ == '__main__':
    main()
