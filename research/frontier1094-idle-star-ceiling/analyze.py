#!/usr/bin/env python3
"""Exact ceiling and star-move optimum for idle rank-48 repartitions on #1094.

Reads the frozen #1094 idle remainder from the selected replay and answers,
for the unhosted idle rank-48 children of each (replica, port) group:

1. relaxation: the best price of *any* within-group repartition with ranks in
   [1, 51] and an unchanged child count (commuting constraints dropped);
2. pair class: an independent recount of PR1252's 48+48 -> 45+51 matching;
3. star class: the exact optimum over disjoint stars, where a centre child
   moves axes to leaves under PR1252's commuting rule, each leaf capped at 51.

Every profile is priced with the pinned multicold engines (exact rationals).
"""
import argparse, random, tarfile, gzip, hashlib, importlib.util, json, sys
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
OWNER_MAP = ROOT / 'research/complex-t16-rare-pattern-exchanges/OWNERS.json.gz'
BASELINE = ROOT / 'research/community-frontier1094-audit/ASSEMBLY.json'
ENGINE_ROOT = ROOT / 'research/complex-k492-owner-repair/vendor/multicold/engines'
ENGINE_SHA256 = {
    'moment': '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482',
    'base_two_moment': 'aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098',
    'outer': 'c1ebb52163a7219504c728a5c2b098bf1e50bf20148a2879c5a74c3cadc7c03c',
}
M, W, DEFICIT, CAP = 73, 14336, 5120, 51
PAIR = 'pair_class_max (PR1252 rule, independent recount)'


REPLAY_TAR = ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBERS = ('hosted/IDLE-REMAINDER-FRAMES.json.gz', 'base/work/complex-nine-native/DATA-PHASES.json',
           'audit/OWNERS-AND-PROFILE.json')


def replay_inputs(root):
    """{member: raw bytes}; read from the committed selected replay unless a
    pre-extracted candidate/strict/global directory is given."""
    if root is not None:
        return {m: (Path(root) / m).read_bytes() for m in MEMBERS}
    with tarfile.open(REPLAY_TAR) as tar:
        return {m: tar.extractfile('candidate/strict/global/' + m).read() for m in MEMBERS}


def parse(name, raw):
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    raw = Path(p).read_bytes()
    return json.loads(gzip.decompress(raw) if str(p).endswith('.gz') else raw)


def decimal(q, places):
    return '0.' + str(q.numerator * 10**places // q.denominator).zfill(places)


def dot(a, b): return (a & b).bit_count() & 1


def load_engine(name):
    path = ENGINE_ROOT / (name + '.py')
    assert sha(path) == ENGINE_SHA256[name], name
    spec = importlib.util.spec_from_file_location('idlestar_' + name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def price(profile, bad, baseline, eng):
    """Exact complex endpoint and kappa; the outer recipe is PR1252's
    math_support.price (retained #1094 recipe), re-stated here."""
    moment, base_two, outer = eng
    assert M * W - sum(r * n for r, n in profile.items()) == DEFICIT
    assert M * M > 2 * max(profile) ** 2
    endpoint = Q(moment.certify(profile, M, W, bad)['lower'])
    for z, accept in ((endpoint, True), (endpoint + Q(1, 10**24), False)):
        lo, hi = moment.moment(profile, M, W, z, bad)
        blo, bhi = base_two.moment(M, W, list(profile.items()), z)
        if bad:
            slo, shi = base_two.moment(M, W, [(1, 32 * M * M * sum(profile.values()))], z)
            blo += slo / 10**16; bhi += shi / 10**16
        assert (hi < 1 and bhi < 1) if accept else (lo > 1 and blo > 1)
    bit = Q(baseline['bit_lower']); eta = beta = Q(1, 10**24)
    s = min(bit, (1 - beta) * endpoint) - Q(1, 10**27)
    chain = [Q(384599, 10**10)]
    for _ in range(7):
        old = chain[-1]; a = (1 - s) * s + s * old
        gap = min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s)
        assert old < a < s < 1 - a and gap > 0
        chain.append(a)
    q = chain[-1] * (1 - 2 * eta)
    ticks = (1 - eta) * q / (1 + q) * 10**18
    kappa = Q((ticks.numerator - 1) // ticks.denominator, 10**18)
    bridge = {'semantic': {'C0': {'base': 2, 'exponent': 210000}, 'strict_literal_gap': 1},
              'rows': {'degree_gap': Q(10**6) - Q(51 * 20161, 25)}}
    assembled = outer.assembly(chain[-1], endpoint, bridge, kappa, eta=eta, beta=beta)
    assert len(assembled['strict_constraints']) == 47
    assert all(x > 0 for x in assembled['strict_constraints'].values())
    try:
        outer.assembly(chain[-1], endpoint, bridge, kappa + Q(1, 10**18), eta=eta, beta=beta)
    except AssertionError:
        pass
    else:
        raise AssertionError('next kappa grid point accepted')
    return dict(endpoint=str(endpoint), endpoint_decimal=decimal(endpoint, 24),
                kappa=str(kappa), kappa_decimal=decimal(kappa, 18))


def group_context(rows, recipe):
    ys = [int(s[k]) for s in recipe['stage_alignment'] for k in ('entry_Y', 'exit_Y')]
    ys.append(int(recipe['terminal_Y_translation']))
    xs = [int(s[k]) for s in recipe['stage_alignment'] for k in ('entry_X', 'exit_X')]
    stage = ys + xs
    axes = [list(map(int, r['orthogonal_axes'])) for r in rows]
    trans = [int(recipe['idle_children'][r['child']]['translation_after']) for r in rows]
    k = len(rows)
    # movable[d][l]: axes of donor d commuting with every axis of leaf l, all
    # stage X/Y and terminal Y translations, and both terminal translations.
    movable = [[None] * k for _ in range(k)]
    for d in range(k):
        for l in range(k):
            if d != l:
                fixed = axes[l] + stage + [trans[d], trans[l]]
                movable[d][l] = frozenset(i for i, v in enumerate(axes[d])
                                          if all(dot(v, x) == 0 for x in fixed))
    return movable


def pair_edge(movable, i, j):
    return len(movable[i][j]) >= 3 or len(movable[j][i]) >= 3


def max_matching(k, edge):
    @lru_cache(None)
    def best(mask):
        if not mask: return 0
        i = (mask & -mask).bit_length() - 1
        rest = mask & ~(1 << i)
        value = best(rest)
        for j in range(i + 1, k):
            if rest >> j & 1 and edge(i, j):
                value = max(value, 1 + best(rest & ~(1 << j)))
        return value
    return best((1 << k) - 1)


def star_flow(movable, centre, leaves, need):
    """Max axes the centre can send: leaf l takes <= need distinct axes from
    movable[centre][l]; each centre axis moves once (bipartite b-matching).
    Returns {leaf: sorted centre-axis indices}."""
    slots = [(l, t) for l in leaves for t in range(need)]
    match = {}
    def augment(s, seen):
        l = slots[s][0]
        for ax in sorted(movable[centre][l]):
            if ax in seen: continue
            seen.add(ax)
            if ax not in match or augment(match[ax], seen):
                match[ax] = s; return True
        return False
    for s in range(len(slots)):
        augment(s, set())
    sent = {l: [] for l in leaves}
    for ax, s in match.items():
        sent[slots[s][0]].append(ax)
    return {l: sorted(v) for l, v in sent.items()}


def cost(vec, a):
    return sum(r ** (1 - a) for r in vec)


def partitions(items):
    if not items: yield []; return
    first, rest = items[0], items[1:]
    for p in partitions(rest):
        yield [[first]] + p
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]


def best_star(k, movable, a):
    """Exact optimum of the disjoint-star class for one group at test exponent a.

    Enumerate set partitions of the k children; each block is a star with one
    centre (or a singleton). Leaves receive up to CAP-48 = 3 axes from the centre.
    Returns (sorted rank vector, [(centre, leaf, centre-axis indices)])."""
    best = None
    for part in partitions(list(range(k))):
        vec, moves = [], []
        for block in part:
            if len(block) == 1:
                vec.append(48); continue
            options = []
            for c in block:
                leaves = [x for x in block if x != c]
                sent = star_flow(movable, c, leaves, CAP - 48)
                v = [48 - sum(map(len, sent.values()))] + [48 + len(sent[l]) for l in leaves]
                options.append((cost(v, a), v, [(c, l, sent[l]) for l in leaves if sent[l]]))
            _, v, mv = min(options, key=lambda o: o[0])
            vec.extend(v); moves.extend(mv)
        if best is None or cost(vec, a) < best[0] - 1e-12:
            best = (cost(vec, a), sorted(vec), moves)
    return best[1], best[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--replay-root', type=Path,
                    help='Optional extracted candidate/strict/global of selected-replay.tar.gz')
    ap.add_argument('--no-price', action='store_true')
    ap.add_argument('--check', action='store_true',
                    help='Recompute and compare with the committed RESULT.json and STAR-MOVES.json.gz; write nothing')
    args = ap.parse_args()
    raw = replay_inputs(args.replay_root)
    frames, phases, audit = (parse(m, raw[m]) for m in MEMBERS)
    owners = read(OWNER_MAP); baseline = json.loads(BASELINE.read_text())
    recipes = {x['port']: x for x in phases['recipes']}
    roles = {(x['owner_replica'], x['port'], x['child']) for x in owners}
    base_profile = Counter({int(k): v for k, v in audit['paid_profile'].items()})
    assert sum(r * n for r, n in base_profile.items()) == M * W - DEFICIT

    eligible, owner48 = defaultdict(list), defaultdict(list)
    for row in frames:
        if row['rank'] == 48 and row['hosted'] == 0 and row['pending_offset'] == 0:
            key = (row['replica'], row['port'], row['child'])
            (owner48 if key in roles else eligible)[row['replica'], row['port']].append(row)
    n_elig = sum(map(len, eligible.values())); n_owner = sum(map(len, owner48.values()))
    assert n_elig + n_owner == base_profile[48] and n_owner == 0  # owner map uses no idle 48
    sizes = Counter(len(v) for v in eligible.values())

    a_test = 0.0016756  # near the endpoint; star choice is checked below to be a-invariant
    pairs_total, relax, star = 0, Counter(), Counter()
    star_alt = Counter(); star_moves = []
    for key, rows in sorted(eligible.items()):
        k = len(rows)
        relax.update([CAP] * (k - 1) + [48 * k - CAP * (k - 1)] if k > 1 else [48])
        movable = group_context(rows, recipes[key[1]])
        pairs_total += max_matching(k, lambda i, j: pair_edge(movable, i, j))
        vec, moves = best_star(k, movable, a_test)
        star.update(vec); star_alt.update(best_star(k, movable, 0.01)[0])
        for c, l, idx in moves:
            ca = list(map(int, rows[c]['orthogonal_axes']))
            star_moves.append(dict(replica=key[0], port=key[1], centre_child=rows[c]['child'],
                                   leaf_child=rows[l]['child'], moved_axes=[str(ca[i]) for i in idx]))

    def with48(counter):
        p = Counter(base_profile); p[48] -= sum(counter.values()); p.update(counter)
        return {r: n for r, n in sorted((+p).items())}

    pair_profile = Counter(base_profile); pair_profile[48] -= 2 * pairs_total
    pair_profile[45] += pairs_total; pair_profile[51] += pairs_total
    profiles = {
        'baseline_1094': {r: n for r, n in sorted(base_profile.items())},
        PAIR: {r: n for r, n in sorted((+pair_profile).items())},
        'star_class_optimum': with48(star),
        'relaxation_ceiling': with48(relax),
    }
    result = dict(
        status='PASS_IDLE48_REPARTITION_CEILING',
        replay_archive={str(REPLAY_TAR.relative_to(ROOT)): sha(REPLAY_TAR)},
        inputs={m: hashlib.sha256(raw[m]).hexdigest() for m in MEMBERS}
               | {str(OWNER_MAP.relative_to(ROOT)): sha(OWNER_MAP), str(BASELINE.relative_to(ROOT)): sha(BASELINE)},
        eligible_children=n_elig, owner_slot_rank48_children=n_owner,
        groups=len(eligible), group_size_histogram={str(k): v for k, v in sorted(sizes.items())},
        pair_class_maximum_pairs=pairs_total,
        star_vector_invariant_between_a=[a_test, 0.01], star_vector_invariant=(star == star_alt),
        star_rank_histogram={str(k): v for k, v in sorted(star.items())},
        relaxation_rank_histogram={str(k): v for k, v in sorted(relax.items())},
        profiles={name: {str(r): n for r, n in p.items()} for name, p in profiles.items()},
    )
    assert star == star_alt
    if not args.no_price:
        eng = tuple(load_engine(n) for n in ('moment', 'base_two_moment', 'outer'))
        result['prices'] = {}
        for name, p in profiles.items():
            result['prices'][name] = dict(native=price(p, False, baseline, eng),
                                          conservative=price(p, True, baseline, eng))
            print(name, result['prices'][name]['native']['kappa_decimal'], file=sys.stderr)
        P = {n: Q(v['native']['kappa']) for n, v in result['prices'].items()}
        assert P['baseline_1094'] == Q(baseline['kappa'])
        assert P['baseline_1094'] < P[PAIR] < P['star_class_optimum'] < P['relaxation_ceiling']
        # Control: deterministic random within-group repartitions (ranks in [1, 51],
        # same child count and group mass) never price above the ceiling.
        rng = random.Random(1094); controls = []
        for _ in range(4):
            alt = Counter()
            for rows in eligible.values():
                vec = [48] * len(rows)
                for _ in range(6):
                    i, j = rng.randrange(len(vec)), rng.randrange(len(vec))
                    t = min(rng.randint(0, 6), vec[i] - 1, CAP - vec[j]) if i != j else 0
                    vec[i] -= t; vec[j] += t
                alt.update(vec)
            kap = Q(price(with48(alt), False, baseline, eng)['kappa'])
            assert kap <= P['relaxation_ceiling']
            controls.append(dict(max_rank=max(alt), kappa=str(kap), below_ceiling=True))
        result['random_repartition_controls'] = controls
    overlay = dict(schema='idle48-star-moves/1', source_frames_sha256=hashlib.sha256(raw[MEMBERS[0]]).hexdigest(),
                   moves=star_moves, profile=result['profiles']['star_class_optimum'])
    payload = json.dumps(overlay, sort_keys=True, separators=(',', ':')).encode()
    result['star_moves'] = len(star_moves)
    result['star_moves_payload_sha256'] = hashlib.sha256(payload).hexdigest()
    text = json.dumps(result, indent=2) + '\n'
    if args.check:
        assert (OUT / 'RESULT.json').read_text() == text, 'RESULT.json differs'
        assert gzip.decompress((OUT / 'STAR-MOVES.json.gz').read_bytes()) == payload, 'STAR-MOVES differs'
        print('PASS_IDLE48_REPARTITION_CEILING_RECOMPUTED', 'pairs=%d' % pairs_total)
        return
    gz = bytearray(gzip.compress(payload, mtime=0)); gz[9] = 255
    (OUT / 'STAR-MOVES.json.gz').write_bytes(bytes(gz))
    (OUT / 'RESULT.json').write_text(text)
    print(result['status'], 'pairs=%d' % pairs_total)


if __name__ == '__main__':
    main()
