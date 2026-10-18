# SPDX-License-Identifier: Apache-2.0
"""Source-bound independent audit of a literal PR2853 replica allocation.

The event-clock method credits PR2848's separately implemented owner auditor.
This implementation imports neither that owner auditor, the candidate generator,
nor any predecessor checker. The small rational routine below is adapted from
PR2848 and explicitly credited, not claimed as a new arithmetic implementation.
"""
from pathlib import Path
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
import argparse
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE_HEAD = 'd01045dfb67428679618027dff552f1d032fa999'
SOURCE_FILES = {'NOTICE': {'git_blob': '46411b80b277d7dcd653a6d1999eaf12975b1103',
            'head': 'd01045dfb67428679618027dff552f1d032fa999',
            'path': 'NOTICE',
            'root': 'predecessor',
            'sha256': 'a91b93a731f116ae55b3644c88232b4d996e58bb810e2559dec013f9788f5e4b'},
 'old-claim.json': {'git_blob': 'afaeb2cc19277e465b03489f8e0790333c58d540',
                    'head': 'd01045dfb67428679618027dff552f1d032fa999',
                    'path': 'outer/OUTER-CLAIM.json',
                    'root': 'predecessor',
                    'sha256': 'eb3260be191774b931cff6e562978a2af27bbc6ff666ca8c1d387a2b18dc86fa'},
 'old-dispatch.json': {'git_blob': '693ed0d022791c43d59000718521fded1ef8def7',
                       'head': 'd01045dfb67428679618027dff552f1d032fa999',
                       'path': 'new/borrow-fill/DISPATCH.json',
                       'root': 'predecessor',
                       'sha256': 'fd8132ec8957b908ee6d871216848f18bafc6bd9304acd6185519ee26d97b1ca'},
 'old-fill.json.gz': {'git_blob': 'ed7016fd9a0eeb8dfeb1cf0f4f576e0287634054',
                      'head': 'd01045dfb67428679618027dff552f1d032fa999',
                      'path': 'new/borrow-fill/FILL.json.gz',
                      'root': 'predecessor',
                      'sha256': '36ab8173de9cc5558eb6f6407c97aa015e92b949d30de6b042db4d8427d6600b'},
 'old-order.json': {'git_blob': '7141bd58cc465e28f0189345713ddd366c814ca4',
                    'head': 'd01045dfb67428679618027dff552f1d032fa999',
                    'path': 'new/borrow-fill/ORDER.json',
                    'root': 'predecessor',
                    'sha256': 'aa7c53c188c90fd74421a804f4c6fb13aa1187c06dbac51fa147830a40e00667'},
 'old-profile.json': {'git_blob': 'd8f8b5699f3228685bb1f907c889f6623e0cfb00',
                      'head': 'd01045dfb67428679618027dff552f1d032fa999',
                      'path': 'new/PROFILE.json',
                      'root': 'predecessor',
                      'sha256': 'd034034b6cb5dd82ae4fa69467a58b2b39f2987e8d109e1001b094e56a688bd8'},
 'plan.json': {'git_blob': 'e91bc498997eda211c6a3c18c6844a4ee09f49fa',
               'head': 'd01045dfb67428679618027dff552f1d032fa999',
               'path': 'new/PLAN.json',
               'root': 'predecessor',
               'sha256': '5132aa4aba25c98f5b78936c4281c89dad6912696f93e390cb296f94811f28b1'},
 'providers.json': {'git_blob': '04e8a99e510469c756432229c9e033e58b18f4ba',
                    'head': 'd01045dfb67428679618027dff552f1d032fa999',
                    'path': 'new/BORROW-PROVIDERS.json',
                    'root': 'predecessor',
                    'sha256': 'd4b8c2ecd493a35b99c6c97cd2dfc4131859cce21e98527f45d9fd183c650f7b'},
 'reference-moment.py': {'git_blob': '54f190da110e2ba55f5ae632f8b5a5b738adbf5b',
                         'head': 'c50d12e4720cd1fef2b5a65e337e37de9731879a',
                         'path': 'reference/PR2848-independent_moment.py',
                         'root': 'bundle',
                         'sha256': '1bbc90ebed80bef36b8ca6b348e56d80692b5a3eefd0ed71ec206071c9574e78'},
 'source-readme.md': {'git_blob': '99653b62a5974f9221b6de2ebd14156c5e906d43',
                      'head': 'd01045dfb67428679618027dff552f1d032fa999',
                      'path': 'README.md',
                      'root': 'predecessor',
                      'sha256': '063fc0243ad9d43a31d19a906971062a80a265d4fa2db78b7221533ca8af3aab'},
 'template.json.gz': {'git_blob': '114808c32b1799da53524bdc25cea67efb60009e',
                      'head': 'd01045dfb67428679618027dff552f1d032fa999',
                      'path': 'inputs/GLOBAL-TEMPLATE.json.gz',
                      'root': 'predecessor',
                      'sha256': '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'},
 'word-base.json.gz': {'git_blob': 'b2f6cef3ed87663ff98e5db5371ece263ad0a735',
                       'head': 'd01045dfb67428679618027dff552f1d032fa999',
                       'path': 'new/borrow/words/BORROW-WORD-43base.json.gz',
                       'root': 'predecessor',
                       'sha256': '7f0a0715aa962f24c112ca32d1b57fc275eff0f15eac6eccd684ba702af82f8b'},
 'word-extra.json.gz': {'git_blob': '8e1e87364f03de5638b15292058ed60c96d219d1',
                        'head': 'd01045dfb67428679618027dff552f1d032fa999',
                        'path': 'new/borrow/words/BORROW-WORD-43extra.json.gz',
                        'root': 'predecessor',
                        'sha256': 'c94a0ac238ca72951e4580895334d39f66ea950fa7af62ca2667251a2f796d6e'}}


class Rejected(ValueError):
    pass


def need(condition, label):
    if not condition:
        raise Rejected(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode(data, name):
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)


def authenticated_sources(predecessor):
    raw = {}
    for name, pin in SOURCE_FILES.items():
        root = HERE if pin.get('root') == 'bundle' else predecessor
        path = root / pin['path']
        need(not path.is_symlink(), 'SOURCE_SYMLINK')
        data = path.read_bytes()
        need(sha(data) == pin['sha256'], 'SOURCE_SHA256')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        need(blob == pin['git_blob'], 'SOURCE_GIT_BLOB')
        raw[name] = data
    return raw


# Credited PR2848 rational atanh/Taylor method, adapted locally so verification
# does not import or execute any inherited checker. For y in [1,2], z<=1/3;
# the 100-term log tail is bounded by 2*z^201/(201*(1-z^2)). For x in [0,1),
# the first omitted exponential term bounds the tail geometrically.
SCALE = 10**45


@lru_cache(None)
def logarithm(x):
    need(x >= 1, 'LOG_ARGUMENT')
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    def unit(y):
        z = (y - 1) / (y + 1)
        power, total = z, Fraction(0)
        for j in range(100):
            total += power / (2 * j + 1)
            power *= z * z
        total *= 2
        return total, total + 2 * power / (201 * (1 - z * z))
    lo, hi = unit(x)
    l2, h2 = unit(Fraction(2))
    lo, hi = lo + k * l2, hi + k * h2
    return Fraction((lo * SCALE).__floor__(), SCALE), Fraction((hi * SCALE).__ceil__(), SCALE)


def exponential(x):
    need(0 <= x < 1, 'EXP_ARGUMENT')
    term = total = Fraction(1)
    for j in range(1, 19):
        term *= x / j
        total += term
    return total, total + term * x / 19 / (1 - x / 20)


def moment(profile, saving, live):
    lo = hi = Fraction(0)
    for rank, count in profile.items():
        need(0 < rank < 73 and count > 0, 'CHILD_PROFILE')
        l, h = logarithm(Fraction(73, rank))
        e0 = exponential(saving * l)[0]
        e1 = exponential(saving * h)[1]
        lo += Fraction(count * rank, 73 * live) * e0
        hi += Fraction(count * rank, 73 * live) * e1
    return Fraction((lo * SCALE).__floor__(), SCALE), Fraction((hi * SCALE).__ceil__(), SCALE)


def make_clock(order, template):
    """Expand the actual source schedule; bridges touch both endpoint pairs."""
    blocks = {}
    current = None
    tail = []
    for ix, event in enumerate(template['execution_schedule']):
        if event['kind'] in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            tail.append(ix)
            continue
        if event['kind'] == 'local_cover_sweep':
            current = event['stage']
            need(current not in blocks, 'DUPLICATE_SOURCE_STAGE')
            blocks[current] = []
        need(current is not None, 'SOURCE_EVENT_BEFORE_STAGE')
        blocks[current].append((ix, event))
    need(tail == [30, 31], 'GLOBAL_TERMINAL_TAIL')
    pair = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    cap = {}
    for e in template['idle_children']:
        need(e['child'] not in cap or cap[e['child']] == e['rank'], 'CAPACITY_AGREEMENT')
        cap[e['child']] = e['rank']
    need(len(order) > 0 and len(order) % 9 == 0, 'CALL_DOMAIN')
    need(all(isinstance(x, list) and len(x) == 2 and all(type(v) is int for v in x) for x in order), 'CALL_INTEGER_SCHEMA')
    N = len(order) // 9
    need(len(order) == 9 * N and len({tuple(x) for x in order}) == 9 * N, 'CALL_DOMAIN')
    need({tuple(x) for x in order} == {(s, r) for s in range(9) for r in range(N)}, 'CALL_DOMAIN')
    last_touch = {}
    windows = {}
    calls = []
    projections = defaultdict(list)
    clock = 0
    for stage, replica in order:
        for source_ix, event in blocks[stage]:
            projections[replica].append(source_ix)
            kind = event['kind']
            if kind == 'local_cover_sweep':
                calls.append(clock)
                last_touch[replica, pair[stage]] = clock
            elif kind == 'bridge':
                last_touch[replica, event['src']] = clock
                last_touch[replica, event['dst']] = clock
            elif kind == 'idle_cover_sweep':
                for child in event['child_indices']:
                    if child in cap:
                        need((replica, child) not in windows, 'DUPLICATE_IDLE_WINDOW')
                        windows[replica, child] = (last_touch.get((replica, event['pair']), -1), clock)
            clock += 1
    need(all(v == list(range(30)) for v in projections.values()) and len(projections) == N,
         'SOURCE_EVENT_PROJECTION')
    need(len(calls) == len(order) and len(windows) == N * len(cap), 'COMPLETE_EVENT_CLOCK')
    return {'N': N, 'pair': pair, 'cap': cap, 'calls': calls, 'windows': windows,
            'events': clock, 'tail': tail}


def geometry(rows, order, dispatch, providers, plan, clock, expected_profile=None):
    N = clock['N']
    need(len(rows) == len(order) * 408, 'ROLE_COUNT')
    helper_seen = [0] * len(order)
    families = [set() for _ in order]
    masks = {}
    for row in rows:
        need(len(row) == 6 and all(type(x) is int for x in row), 'INTEGER_ROW')
        time, helper, owner, child, port, offset = row
        need(0 <= time < len(order) and 0 <= helper < 408 and 0 <= owner < N
             and child in clock['cap'] and 0 <= port < 112 and offset >= 0, 'ROW_RANGE')
        stage, active_owner = order[time]
        pair = plan['pairs'][str(child)]
        side = plan['sides'][str(child)]
        family = owner * 896 + (2 * pair + side) * 112 + port
        need(not (owner == active_owner and pair == clock['pair'][stage]), 'ACTIVE_DATA_FAMILY')
        begin, end = clock['windows'][owner, child]
        need(begin < clock['calls'][time] < end, 'STRICT_EVENT_WINDOW')
        need(not (helper_seen[time] >> helper) & 1, 'DUPLICATE_HELPER')
        helper_seen[time] |= 1 << helper
        need(family not in families[time], 'DUPLICATE_PHYSICAL_FAMILY')
        families[time].add(family)
        width = providers[dispatch[stage, active_owner]]['widths'][helper]
        need(offset + width <= clock['cap'][child], 'BIN_CAPACITY')
        key = (owner, child, port)
        bits = ((1 << width) - 1) << offset
        need(not (masks.get(key, 0) & bits), 'BIN_OVERLAP')
        masks[key] = masks.get(key, 0) | bits
    need(all(x == (1 << 408) - 1 for x in helper_seen), 'COMPLETE_HELPERS')
    idle = Counter()
    for owner in range(N):
        for child, capacity in clock['cap'].items():
            for port in range(112):
                used = masks.get((owner, child, port), 0)
                need(not used & (used + 1), 'COMPACT_PREFIX')
                remainder = capacity - used.bit_count()
                if remainder:
                    idle[remainder] += 1
    profile = Counter(idle)
    for stage, replica in order:
        for rank, count in providers[dispatch[stage, replica]]['actual_paid_profile'].items():
            profile[int(rank)] += count
    if expected_profile is not None:
        need(dict(profile) == expected_profile, 'COMPLETE_PROFILE')
    return {'roles': len(rows), 'idle': dict(sorted(idle.items())),
            'profile': dict(sorted(profile.items())),
            'rank_mass': sum(r * n for r, n in profile.items())}


def gf_basis(vectors):
    pivots = {}
    for value in vectors:
        need(type(value) is int and 0 <= value < 512, 'FRAME_INTEGER_RANGE')
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    for bit in sorted(pivots):
        for other in pivots:
            if other > bit and (pivots[other] >> bit) & 1:
                pivots[other] ^= pivots[bit]
    return tuple(pivots[x] for x in sorted(pivots, reverse=True))


def literal_provider(word, registered):
    """Recount literal native frame chains; do not treat the report as a price oracle."""
    v, h, R = (word['report'][x] for x in ('v', 'h', 'R'))
    need((v, h, R) == (112, 9, 480), 'SOURCE_NATIVE_GEOMETRY')
    n = 2 * v + R
    removed = set(word['removed'])
    live = set(range(n)) - removed
    helpers = sorted(live - set(range(2 * v)))
    full = gf_basis([1 << i for i in range(h)])
    start = [(p,) for p in word['ports']] + [()] * (v + R)
    end = [full] * v + [gf_basis([x for x in range(1, 512) if not (x & p).bit_count() % 2]) for p in word['ports']] + [full] * R
    for r, frame in word['start_extra'].items():
        start[int(r)] = gf_basis(frame)
    for r, frame in word['helper_final'].items():
        end[int(r)] = gf_basis(frame)
    cur = start[:]
    paid = Counter()
    def climb(register, frame):
        frame = gf_basis(frame)
        need(register in live and gf_basis(cur[register] + frame) == frame, 'SOURCE_FRAME_MONOTONE')
        jump = len(frame) - len(cur[register])
        if jump:
            paid[jump] += 1
        cur[register] = frame
    def scalar(event):
        need(event[0] in ('add', 'scale'), 'SOURCE_SCALAR_GATE')
        for register in event[1:3] if event[0] == 'add' else event[1:2]:
            climb(register, event[-1])
    for i, event in enumerate(word['A']):
        if event[0] == 'warp':
            need(i < word['prelude_events'], 'SOURCE_PRELUDE_WARP')
            need(cur[event[1]] == gf_basis(event[3]), 'SOURCE_PRELUDE_FRAME')
            cur[event[1]] = gf_basis(event[4])
        else:
            scalar(event)
    levels = {int(t): gf_basis(frame) for t, frame in word['target_levels'].items()}
    need(all(cur[v + t] == levels.get(t, ()) for t in range(v)), 'SOURCE_TARGET_CENTRE_LEVEL')
    for register, frame in zip(word['centers'], word['center_frames']):
        frame = gf_basis(frame)
        need(cur[register] == frame, 'SOURCE_CENTRE_FRAME')
        served = {levels.get(e[1] - v, ()) for e in word['cut'] if e[2] == register}
        for target in sorted(served, key=lambda x: -len(x)):
            need(gf_basis(target + frame) == frame, 'SOURCE_CENTRE_NESTED_PATH')
            if target != frame:
                paid[len(frame) - len(target)] += 1
            frame = target
    warps = defaultdict(list)
    for record in word['warps']:
        warps[record[0]].append(record)
    for pos in range(len(word['B']) + 1):
        for _, register, columns, before, after in warps[pos]:
            need(cur[register] == gf_basis(before), 'SOURCE_B_WARP_FRAME')
            cur[register] = gf_basis(after)
        if pos < len(word['B']):
            scalar(word['B'][pos])
    for event in word['restore']:
        scalar(event)
    for register in sorted(live):
        climb(register, end[register])
    widths = [len(end[r]) - len(start[r]) for r in helpers]
    profile = dict(sorted(paid.items()))
    need(len(helpers) == 408 and len(removed) == 72 and len(word['helper_final']) == 72 and len(word['centers']) == 8, 'SOURCE_FULL_STOCK')
    need(profile == {int(k): v for k, v in word['report']['local_profile'].items()}, 'SOURCE_LITERAL_PROFILE')
    need(dict(Counter(widths)) == {int(k): v for k, v in word['report']['width_inventory'].items()}, 'SOURCE_LITERAL_INVENTORY')
    need(widths == registered['widths'], 'SOURCE_REGISTERED_ORDERED_WIDTHS')
    need(profile == {int(k): v for k, v in registered['actual_paid_profile'].items()}, 'SOURCE_REGISTERED_PAID_PROFILE')
    return {'helpers': helpers, 'widths': widths, 'inventory': dict(sorted(Counter(widths).items())),
            'profile': profile, 'local_rank_mass': sum(k * v for k, v in profile.items()),
            'private_zero_buffers': 72, 'centres': 8, 'removed_helper_registers': 72}


def verify(predecessor, candidate):
    raw = authenticated_sources(predecessor)
    names = ['ORDER.json', 'DISPATCH.json', 'FILL.json.gz', 'PROFILE.json', 'CANDIDATE.json']
    payload = {name: (candidate / name).read_bytes() for name in names}
    data = {name: decode(value, name) for name, value in payload.items()}
    barrier = data['CANDIDATE.json']
    need(barrier['source_head'] == SOURCE_HEAD and barrier['comparison_head'] == SOURCE_HEAD, 'CANDIDATE_SOURCE_HEAD')
    need(barrier['comparison_claim_sha256'] == sha(raw['old-claim.json']), 'CANDIDATE_COMPARATOR_PIN')
    need(all(barrier['candidate_sha256'][name] == sha(payload[name]) for name in names[:4]), 'CANDIDATE_PAYLOAD_BINDING')
    old = {name: decode(raw['old-' + name.lower()], name) for name in names[:4]}
    order = data['ORDER.json']
    dispatch_rows = data['DISPATCH.json']
    need(all(isinstance(x, list) and len(x) == 3 and type(x[0]) is int and type(x[1]) is int and isinstance(x[2], str) for x in dispatch_rows), 'DISPATCH_SCHEMA')
    dispatch = {(s, r): p for s, r, p in dispatch_rows}
    need(len(dispatch) == len(dispatch_rows) == len(order), 'DISPATCH_UNIQUENESS')
    need(set(dispatch) == {tuple(x) for x in order}, 'DISPATCH_DOMAIN')
    providers = decode(raw['providers.json'], 'providers.json')
    need(set(providers) == {'gauge44', 'extra'} and all(p in providers for p in dispatch.values()), 'DISPATCH_PROVIDER')
    provider_checks = {name: literal_provider(decode(raw['word-' + suffix + '.json.gz'], 'word.json.gz'), providers[name]) for name, suffix in [('gauge44', 'base'), ('extra', 'extra')]}
    plan = decode(raw['plan.json'], 'plan.json')
    template = decode(raw['template.json.gz'], 'template.json.gz')
    fill = data['FILL.json.gz']
    need(set(fill) == {'columns', 'rows', 'dispatch_overrides'}, 'FILL_SCHEMA')
    need(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'FILL_COLUMNS')
    need(fill['dispatch_overrides'] == [], 'NO_DISPATCH_OVERRIDE')
    rows = fill['rows']
    clock = make_clock(order, template)
    N = clock['N']
    need(type(barrier['replicas']) is int and N == barrier['replicas'], 'REPLICA_BINDING')
    profile = {int(r): n for r, n in data['PROFILE.json'].items()}
    need(all(type(n) is int and n > 0 for n in profile.values()), 'POSITIVE_INTEGER_PROFILE')
    need(profile == {int(r): n for r, n in barrier['profile'].items()}, 'CANDIDATE_PROFILE_BINDING')
    positive = geometry(rows, order, dispatch, providers, plan, clock, profile)
    need(positive['idle'] == {int(r): n for r, n in barrier['idle'].items()}, 'CANDIDATE_IDLE_BINDING')
    old_order = old['ORDER.json']
    old_dispatch = {(s, r): p for s, r, p in old['DISPATCH.json']}
    old_profile = {int(r): n for r, n in old['PROFILE.json'].items()}
    old_clock = make_clock(old_order, template)
    need(old_clock['N'] == 74 and plan['T'] == 74, 'P53_BASELINE_T74')
    baseline = geometry(old['FILL.json.gz']['rows'], old_order, old_dispatch, providers, plan, old_clock, old_profile)
    W, old_W = 896 * N, 896 * 74
    need(positive['rank_mass'] == W * 73 - N * 320 and baseline['rank_mass'] == old_W * 73 - 74 * 320, 'RANK_MASS')
    normalized_delta = {r: Fraction(profile.get(r, 0), N) - Fraction(old_profile.get(r, 0), 74) for r in set(profile) | set(old_profile)}
    normalized_delta = {r: str(n) for r, n in normalized_delta.items() if n}
    controls = []
    def faulty(label, index=None, replacement=None, replacement_rows=None, expected_profile=profile):
        changed = rows[:]
        if index is not None:
            changed[index] = replacement
        if replacement_rows is not None:
            changed = replacement_rows
        try:
            geometry(changed, order, dispatch, providers, plan, clock, expected_profile)
        except Rejected as error:
            need(str(error) == label, 'WRONG_CONTROL_REJECTION:' + label + ':' + str(error))
            controls.append({'control': label, 'verdict': 'REJECTED_BY_NAMED_PREDICATE'})
        else:
            raise Rejected('CONTROL_ACCEPTED:' + label)
    # Select faults from the literal witness, rather than hardcoding H23 row IDs.
    first = rows[0]
    t, h, owner, child, port, offset = first
    active_child = next(c for c in clock['cap'] if plan['pairs'][str(c)] == clock['pair'][order[t][0]])
    faulty('ACTIVE_DATA_FAMILY', 0, [t, h, order[t][1], active_child, port, 0])
    j = next(i for i, row in enumerate(rows) if i > 0 and row[0] == t)
    duplicate_family = rows[j][:]
    duplicate_family[2:] = [owner, child, port, 0]
    faulty('DUPLICATE_PHYSICAL_FAMILY', j, duplicate_family)
    width = providers[dispatch[tuple(order[t])]]['widths'][h]
    faulty('BIN_CAPACITY', 0, [t, h, owner, child, port, clock['cap'][child] - width + 1])
    bybin = defaultdict(list)
    for i, row in enumerate(rows):
        tt, hh, oo, cc, pp, ff = row
        ww = providers[dispatch[tuple(order[tt])]]['widths'][hh]
        bybin[oo, cc, pp].append((i, ff, ww))
    overlapping = next(records for records in bybin.values() if len(records) > 1)
    earlier, later = overlapping[0], overlapping[1]
    overlap = rows[later[0]][:]
    overlap[5] = earlier[1]
    # If the earlier interval ends too near the capacity, offset0 still overlaps
    # some earlier member in this prefix; choose a pair that is explicitly safe.
    if overlap[5] + later[2] > clock['cap'][overlap[3]]:
        pair = next((xs[a], xs[b]) for xs in bybin.values() for a in range(len(xs)) for b in range(a + 1, len(xs)) if xs[a][1] + xs[b][2] <= clock['cap'][rows[xs[b][0]][3]])
        earlier, later = pair
        overlap = rows[later[0]][:]
        overlap[5] = earlier[1]
    faulty('BIN_OVERLAP', later[0], overlap)
    gap_key, gap_records = next((key, xs) for key, xs in bybin.items() if max(o + w for _, o, w in xs) < clock['cap'][key[1]])
    gap_index, _, _ = max(gap_records, key=lambda x: x[1])
    gap = rows[gap_index][:]
    gap[5] += 1
    faulty('COMPACT_PREFIX', gap_index, gap)
    expired = None
    for i, row in enumerate(rows):
        tt, hh, oo, cc, pp, ff = row
        begin, end = clock['windows'][oo, cc]
        for tt2, pos in enumerate(clock['calls']):
            if not begin < pos < end and not (order[tt2][1] == oo and clock['pair'][order[tt2][0]] == plan['pairs'][str(cc)]):
                expired = i, [tt2, hh, oo, cc, pp, ff]
                break
        if expired is not None:
            break
    need(expired is not None, 'WINDOW_CONTROL_EXISTS')
    faulty('STRICT_EVENT_WINDOW', expired[0], expired[1])
    duplicate_helper = rows[j][:]
    duplicate_helper[1] = h
    faulty('DUPLICATE_HELPER', j, duplicate_helper)
    faulty('ROLE_COUNT', replacement_rows=rows[:-1])
    corrupt_profile = dict(profile)
    corrupt_profile[1] = corrupt_profile.get(1, 0) + 1
    faulty('COMPLETE_PROFILE', expected_profile=corrupt_profile)
    lower, upper = Fraction(barrier['complex_lower']), Fraction(barrier['complex_upper'])
    need(0 < lower < upper < Fraction(1, 100), 'ROOT_BRACKET_ORDER')
    lower_value, upper_value = moment(profile, lower, W), moment(profile, upper, W)
    need(lower_value[1] < 1 < upper_value[0], 'RATIONAL_ROOT_BRACKET')
    old_claim = decode(raw['old-claim.json'], 'old-claim.json')
    prior = Fraction(old_claim['kappa_rational'])
    need(prior == Fraction(old_claim['kappa']), 'SOURCE_FULL_DECIMAL_RATIONAL_EQUALITY')
    target = Fraction(barrier['target'])
    need(target == lower - Fraction(1, 10**46) - Fraction(1, 10**70), 'MODERN_OUTER_TARGET_CONVENTION')
    need(prior < target < lower, 'EXACT_FULL_PR2853_COMPARISON')
    old_moment, new_moment = moment(old_profile, prior, old_W), moment(profile, prior, W)
    need(new_moment[1] < old_moment[0], 'STRICT_NORMALIZED_MOMENT_DOMINANCE')
    need(moment(profile, upper + Fraction(1, 10**20), W)[0] > 1, 'OVERSTATED_TARGET_CONTROL')
    controls.append({'control': 'OVERSTATED_TARGET', 'verdict': 'REJECTED_BY_POSITIVE_MOMENT_RESIDUAL'})
    need(all((candidate / name).read_bytes() == value for name, value in payload.items()), 'CANDIDATE_DRIFT')
    authenticated_sources(predecessor)
    return {'status': 'PASS_INDEPENDENT_P53_EVENT_CLOCK_PROFILE_AND_MOMENT',
            'baseline_head': SOURCE_HEAD, 'baseline_claim_sha256': sha(raw['old-claim.json']),
            'roles': len(rows), 'calls': len(order), 'replicas': N, 'provider_literal_checks': provider_checks,
            'source_events_per_replica': 30, 'expanded_source_events': clock['events'],
            'global_tail_indices': clock['tail'], 'event_coordinate': 'Actual source-event positions; strict open window endpoints.',
            'baseline_profile': baseline['profile'], 'profile': positive['profile'], 'idle': positive['idle'],
            'normalized_profile_delta_per_replica': normalized_delta, 'rank_mass': positive['rank_mass'],
            'live': W, 'physical': W + 490,
            'physical_extras': {'helpers': 408, 'private_zero_buffers': 72, 'centres': 8, 'coefficient_fields': 2},
            'rational_root_bracket': [str(lower), str(upper)],
            'lower_moment_upper_minus_one': str(lower_value[1] - 1),
            'upper_moment_lower_minus_one': str(upper_value[0] - 1),
            'prior_full_kappa': str(prior), 'target': str(target), 'gain': str(target - prior),
            'strict_normalized_moment_improvement_at_prior_lower': str(old_moment[0] - new_moment[1]),
            'controls': controls, 'candidate_sha256': {name: sha(value) for name, value in payload.items()},
            'source_pin_inventory_sha256': sha(json.dumps(SOURCE_FILES, sort_keys=True, separators=(',', ':')).encode()),
            'source_sha256': {name: sha(value) for name, value in raw.items()},
            'arithmetic_source_sha256': sha(raw['reference-moment.py']),
            'scope': 'Independent literal P53 word frame/width recount and owner/event-window/family/profile audit, using a locally adapted credited PR2848 rational routine. No candidate generator or predecessor checker imported or executed. Full native phases/operators, block-norm, precision/invoice and modern outer admission remain separate obligations; this receipt alone is not an admitted kappa.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predecessor', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    predecessor, candidate, out = args.predecessor.resolve(), args.candidate.resolve(), args.out.resolve()
    need(not out.exists(), 'FRESH_OUTPUT')
    need(not out.is_relative_to(HERE) and not out.is_relative_to(candidate)
         and not out.is_relative_to(predecessor), 'OUTPUT_OUTSIDE_INPUTS')
    result = verify(predecessor, candidate)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], 'roles=' + str(result['roles']), 'controls=' + str(len(result['controls'])))


if __name__ == '__main__':
    main()
