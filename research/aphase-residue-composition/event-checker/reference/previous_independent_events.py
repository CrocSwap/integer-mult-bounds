# SPDX-License-Identifier: Apache-2.0
"""Source-bound independent audit of the T248 three-bin residue exchange.

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
SOURCE_HEAD = 'c50d12e4720cd1fef2b5a65e337e37de9731879a'
SOURCE_FILES = {'LICENSE': {'git_blob': '261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64',
             'path': 'sources/PR2843-LICENSE',
             'sha256': 'c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4'},
 'PR2833-NOTICE': {'git_blob': '46411b80b277d7dcd653a6d1999eaf12975b1103',
                   'path': 'sources/PR2833-NOTICE',
                   'sha256': 'a91b93a731f116ae55b3644c88232b4d996e58bb810e2559dec013f9788f5e4b'},
 'PR2843-NOTICE': {'git_blob': 'df85dcfd9cac7a634523e381d92bb44e459ee51a',
                   'path': 'sources/PR2843-NOTICE',
                   'sha256': 'b1a13e97bf3503b4a52033518dd528d010f57be7b591245bf48910c20320d186'},
 'old-claim.json': {'git_blob': '16125d43c4479676f3aa7593574be30780cd3506',
                    'path': 'CLAIM.json',
                    'sha256': 'aceb1394b3e8f3abcc9b1a0dc82756ab937ffbefc2f37305a229a00ccc5137e9'},
 'old-dispatch.json': {'git_blob': '30e94fd4fcff569217e0d8b2c8fcceb74d6d21e2',
                       'path': 'DISPATCH.json',
                       'sha256': '24d263f53c792558b1639a85e9f6ed4ee8633d36812db82957006bfbb7e523f7'},
 'old-fill.json.gz': {'git_blob': '53afe68fbe69b5c6feb19d15b250446270541f69',
                      'path': 'FILL.json.gz',
                      'sha256': 'aa278ce395bab027ca4cefc835afe8da84a2e0a27ae6cbc3b2fbde287bdb4466'},
 'old-order.json': {'git_blob': '73cc025938918fd7876bbcfc0daf54783d7d2629',
                    'path': 'ORDER.json',
                    'sha256': 'f6b3bcd6ae7e7f0339cd881204bffc095509cf738982a2d8e221cd622cd54fb1'},
 'old-profile.json': {'git_blob': '4b4544c2d6e1b9f6c855bec1527629e6390acd89',
                      'path': 'PROFILE.json',
                      'sha256': 'ea57a40446e596bdcf1348772790ae6be4df9766e4b502c277ee81025226697b'},
 'plan.json': {'git_blob': '5af9dd20821ae5b79778d85cd7183873c5999732',
               'path': 'sources/PR2833-PLAN.json',
               'sha256': '163431bf8d3bc0d9b894994b1a3cfa7947367b2243b3c0b3a97d740195a1cb08'},
 'providers.json': {'git_blob': 'bf7c87b4d1b0fc72b8048751782f9ea6d6657096',
                    'path': 'sources/PR2833-PROVIDERS.json',
                    'sha256': '3666edf67d61b01336e58166ec9edebd72902cc37a2da693b05691ab2a387cda'},
 'reference-moment.py': {'git_blob': '54f190da110e2ba55f5ae632f8b5a5b738adbf5b',
                         'path': 'independent_moment.py',
                         'sha256': '1bbc90ebed80bef36b8ca6b348e56d80692b5a3eefd0ed71ec206071c9574e78'},
 'reference-owners.py': {'git_blob': '694e50094bec370c1f1ba642a21da599c9a005e8',
                         'path': 'independent_owners.py',
                         'sha256': '9fe7199309eb6b20e6187c63ed59d0afc44f5f9070e1ed1271a991d0f210fbf1'},
 'source-readme.md': {'git_blob': 'ae006518cdb79a80d210d7ff013c48716b14a155',
                      'path': 'README.md',
                      'sha256': '4f72c9eace0e7d604554d7e00a377da679aa035b1d754bd4d365dc859f79bf43'},
 'template.json.gz': {'git_blob': '114808c32b1799da53524bdc25cea67efb60009e',
                      'path': 'sources/PR2833-T37-TEMPLATE.json.gz',
                      'sha256': '21297b20f1f2dc76eb9dd8124416068c3cb096bab9df17fa4da19bc68dfe082e'}}
CHANGES = [
    [380, [0, 190, 0, 4, 0, 0], [0, 190, 124, 0, 0, 0]],
    [448, [0, 224, 124, 0, 0, 0], [0, 224, 0, 0, 0, 0]],
    [449, [1, 224, 124, 0, 0, 7], [1, 224, 124, 0, 0, 9]],
    [942, [2, 63, 0, 4, 0, 9], [2, 63, 0, 0, 0, 7]],
    [1632, [4, 0, 0, 4, 0, 18], [4, 0, 0, 4, 0, 0]],
]
CHANGED_BINS = {(0, 0, 0), (124, 0, 0), (0, 4, 0)}


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
        path = predecessor / pin['path']
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
    N = 248
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
    bin_rows = defaultdict(list)
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
        if key in CHANGED_BINS:
            bin_rows[key].append({'row': row, 'width': width, 'event_position': clock['calls'][time]})
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
    bins = []
    for key in sorted(CHANGED_BINS):
        owner, child, port = key
        begin, end = clock['windows'][owner, child]
        used = masks.get(key, 0).bit_count()
        bins.append({'bin': list(key), 'capacity': clock['cap'][child], 'used': used,
                     'idle': clock['cap'][child] - used, 'strict_event_window': [begin, end],
                     'allowed_call_times': [t for t, p in enumerate(clock['calls']) if begin < p < end],
                     'rows': bin_rows[key]})
    return {'roles': len(rows), 'idle': dict(sorted(idle.items())),
            'profile': dict(sorted(profile.items())), 'bins': bins,
            'rank_mass': sum(r * n for r, n in profile.items())}


def verify(predecessor, candidate):
    raw = authenticated_sources(predecessor)
    names = ['ORDER.json', 'DISPATCH.json', 'FILL.json.gz', 'PROFILE.json', 'CANDIDATE.json']
    payload = {name: (candidate / name).read_bytes() for name in names}
    data = {name: decode(value, name) for name, value in payload.items()}
    old = {name: decode(raw['old-' + name.lower()], name) for name in names[:4]}
    need(payload['ORDER.json'] == raw['old-order.json'], 'EXACT_ORDER')
    need(payload['DISPATCH.json'] == raw['old-dispatch.json'], 'EXACT_DISPATCH')
    order = data['ORDER.json']
    dispatch_rows = data['DISPATCH.json']
    dispatch = {(s, r): p for s, r, p in dispatch_rows}
    need(len(dispatch) == len(dispatch_rows) == len(order), 'DISPATCH_UNIQUENESS')
    need(set(dispatch) == {tuple(x) for x in order}, 'DISPATCH_DOMAIN')
    providers = decode(raw['providers.json'], 'providers.json')
    need(all(p in providers for p in dispatch.values()), 'DISPATCH_PROVIDER')
    plan = decode(raw['plan.json'], 'plan.json')
    template = decode(raw['template.json.gz'], 'template.json.gz')
    source_fill, fill = old['FILL.json.gz'], data['FILL.json.gz']
    need(set(source_fill) == set(fill) == {'columns', 'rows', 'dispatch_overrides'}, 'FILL_SCHEMA')
    need(fill['columns'] == ['time', 'helper', 'owner_replica', 'child', 'port', 'offset'], 'FILL_COLUMNS')
    need(fill['dispatch_overrides'] == source_fill['dispatch_overrides'] == [], 'NO_DISPATCH_OVERRIDE')
    before, rows = source_fill['rows'], fill['rows']
    need(len(before) == len(rows), 'EXACT_ROLE_COUNT')
    changes = [[i, a, b] for i, (a, b) in enumerate(zip(before, rows)) if a != b]
    need(changes == CHANGES, 'ONLY_FIVE_DECLARED_EDITS')
    clock = make_clock(order, template)
    profile = {int(r): n for r, n in data['PROFILE.json'].items()}
    old_profile = {int(r): n for r, n in old['PROFILE.json'].items()}
    positive = geometry(rows, order, dispatch, providers, plan, clock, profile)
    baseline = geometry(before, order, dispatch, providers, plan, clock, old_profile)
    delta = {r: profile.get(r, 0) - old_profile.get(r, 0) for r in set(profile) | set(old_profile)}
    delta = {r: n for r, n in delta.items() if n}
    need(delta == {2: -1, 5: -1, 16: -1, 23: 1}, 'EXACT_PAID_DELTA')
    W = 896 * 248
    need(positive['rank_mass'] == baseline['rank_mass'] == W * 73 - 248 * 320, 'RANK_MASS')
    # Geometry controls bypass only the declared-edit guard, so each must reach
    # its named mathematical condition rather than reject an unfamiliar patch.
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
    faulty('ACTIVE_DATA_FAMILY', 380, [0, 190, 0, 12, 0, 0])
    faulty('DUPLICATE_PHYSICAL_FAMILY', 380, [0, 190, 0, 0, 0, 0])
    faulty('BIN_CAPACITY', 449, [1, 224, 124, 0, 0, 10])
    faulty('BIN_OVERLAP', 449, [1, 224, 124, 0, 0, 8])
    faulty('COMPACT_PREFIX', 1632, [4, 0, 0, 4, 0, 18])
    end = clock['windows'][0, 0][1]
    late = next(t for t, pos in enumerate(clock['calls']) if pos >= end
                and not (order[t][1] == 0 and clock['pair'][order[t][0]] == 1))
    faulty('STRICT_EVENT_WINDOW', 942, [late, 63, 0, 0, 0, 7])
    faulty('DUPLICATE_HELPER', 380, [0, 189, 124, 0, 0, 0])
    faulty('ROLE_COUNT', replacement_rows=rows[:-1])
    corrupt_profile = dict(profile)
    corrupt_profile[23] = 0
    faulty('COMPLETE_PROFILE', expected_profile=corrupt_profile)
    lower = Fraction('0.0017186591902484590792119')
    upper = Fraction('0.0017186591902484590792120')
    lower_value, upper_value = moment(profile, lower, W), moment(profile, upper, W)
    need(lower_value[1] < 1 < upper_value[0], 'RATIONAL_ROOT_BRACKET')
    old_claim = decode(raw['old-claim.json'], 'old-claim.json')
    prior = Fraction(old_claim['kappa'])
    target = Fraction('0.001718659190248459079211') - Fraction(1, 10**46) - Fraction(1, 10**70)
    need(prior < target < lower, 'EXACT_FULL_PR2848_COMPARISON')
    need(Fraction(data['CANDIDATE.json']['target']) == target, 'CANDIDATE_TARGET_BINDING')
    old_moment, new_moment = moment(old_profile, prior, W), moment(profile, prior, W)
    need(new_moment[1] < old_moment[0], 'STRICT_MOMENT_DOMINANCE')
    need(moment(profile, upper + Fraction(1, 10**20), W)[0] > 1, 'OVERSTATED_TARGET_CONTROL')
    controls.append({'control': 'OVERSTATED_TARGET', 'verdict': 'REJECTED_BY_POSITIVE_MOMENT_RESIDUAL'})
    need(all((candidate / name).read_bytes() == data_ for name, data_ in payload.items()), 'CANDIDATE_DRIFT')
    authenticated_sources(predecessor)
    return {'status': 'PASS_INDEPENDENT_THREE_BIN_EVENT_CLOCK_PROFILE_AND_MOMENT',
            'baseline_head': SOURCE_HEAD, 'baseline_claim_sha256': sha(raw['old-claim.json']),
            'roles': len(rows), 'calls': len(order), 'replicas': 248,
            'source_events_per_replica': 30, 'expanded_source_events': clock['events'],
            'global_tail_indices': clock['tail'], 'event_coordinate': 'Actual source-event positions; open window endpoints.',
            'edits': changes, 'baseline_bins': baseline['bins'], 'candidate_bins': positive['bins'],
            'baseline_profile': baseline['profile'], 'profile': positive['profile'], 'idle': positive['idle'],
            'profile_delta': delta, 'rank_mass': positive['rank_mass'], 'live': W, 'physical': W + 490,
            'analytic_sign': 'For p=1-a in (0,1), (16+5+2)^p < 16^p+5^p+2^p. Thus H23-H16-H5-H2<0 while rank mass is unchanged.',
            'rational_root_bracket': [str(lower), str(upper)],
            'lower_moment_upper_minus_one': str(lower_value[1] - 1),
            'upper_moment_lower_minus_one': str(upper_value[0] - 1),
            'prior_full_kappa': str(prior), 'target': str(target), 'gain': str(target - prior),
            'strict_moment_improvement_at_prior_lower': str(old_moment[0] - new_moment[1]),
            'controls': controls,
            'candidate_sha256': {name: sha(value) for name, value in payload.items()},
            'source_pin_inventory_sha256': sha(json.dumps(SOURCE_FILES, sort_keys=True, separators=(',', ':')).encode()),
            'source_sha256': {name: sha(value) for name, value in raw.items()},
            'arithmetic_source_sha256': sha(raw['reference-moment.py']),
            'scope': 'Independent literal owner/event-window/family/profile audit with a locally adapted credited PR2848 rational routine. No candidate generator or predecessor checker imported or executed. Native operators, block-norm contract, finite invoice and modern outer admission remain separate obligations; this receipt alone is not an admitted kappa.'}


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
