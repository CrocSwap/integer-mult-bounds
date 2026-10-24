"""Check the frozen consumer and precision packets with exact arithmetic.

Read data only. Do not import a producer or the upstream phase module.
Use physical source arrays for the precision replay.
"""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import lru_cache
import gzip
from hashlib import sha1, sha256
from itertools import product
import json
from pathlib import Path
import shutil
import tarfile


ROOT = Path('/Users/aliromman/Projects/IntegerMultiplicationBounds')
LANES = ROOT / 'work/centre-encoding-campaign-20261014/lanes'
HERE = Path(__file__).resolve().parent
CONSUMER = HERE.parent / 'common-f-review-20261015'
PRECISION = HERE.parent / 'common-f-precision-20261015'
PACKET = LANES / 'paired-package-review/upstream-followthrough-20261015'
I = tuple(1 << j for j in range(73))
SELECTED = (0, 7, 20, 27, 36, 46, 57, 111, 21, 37, 47, 76, 81, 87, 92, 110)
PINS = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def hashbytes(raw):
    return sha256(raw).hexdigest()


def checked(path, pin):
    raw = path.read_bytes()
    need(hashbytes(raw) == pin, 'Source pin: ' + str(path))
    PINS[str(path.relative_to(ROOT))] = pin
    return raw


def encoded(obj):
    return json.dumps(obj, separators=(',', ':')).encode()


def phase_word(terms):
    counts = Counter()
    for v, c in terms:
        if v:
            counts[v] += c
    return tuple(sorted((v, c % 4) for v, c in counts.items() if c % 4))


@lru_cache(None)
def polynomial(terms):
    """Return the linear bit planes and the upper quadratic bit plane."""
    low = high = cross = 0
    for v, c in terms:
        if c & 1:
            high ^= low & v
            low ^= v
            bits = v
            while bits:
                bit = bits & -bits
                j = bit.bit_length() - 1
                cross ^= (v & (bit - 1)) << (j * (j - 1) // 2)
                bits ^= bit
        if c & 2:
            high ^= v
    return low, high, cross


def phase_sum(a, b):
    return a[0] ^ b[0], a[1] ^ b[1] ^ (a[0] & b[0]), a[2] ^ b[2]


def phase_negative(a):
    return a[0], a[1] ^ a[0], a[2]


def act(matrix, vector):
    answer = 0
    while vector:
        bit = vector & -vector
        answer ^= matrix[bit.bit_length() - 1]
        vector ^= bit
    return answer


@lru_cache(None)
def compose(left, right):
    return tuple(act(left, v) for v in right)


@lru_cache(None)
def transport(matrix, terms, shift=0):
    return phase_word(tuple((act(matrix, v), c) for v, c in terms) + ((shift, 2),))


def binary_rank(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


@lru_cache(None)
def phase_rank(terms):
    # A signed parity has polarization vv^T over F2.
    rows = [0] * 73
    for v, c in terms:
        if c & 1:
            bits = v
            while bits:
                bit = bits & -bits
                rows[bit.bit_length() - 1] ^= v
                bits ^= bit
    return binary_rank(rows)


def phase_kernel_check():
    forms = coefficients = 0
    for n in range(1, 4):
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        for diagonal in product(range(4), repeat=n):
            for edges in product(range(2), repeat=len(pairs)):
                rows = [(a & 1) << i for i, a in enumerate(diagonal)]
                for (i, j), b in zip(pairs, edges):
                    rows[i] ^= b << j
                    rows[j] ^= b << i
                rank = binary_rank(rows)
                kernel = []
                for character in range(1 << n):
                    real = imag = 0
                    for x in range(1 << n):
                        q = sum(a for i, a in enumerate(diagonal) if x >> i & 1)
                        q += 2 * sum(b for (i, j), b in zip(pairs, edges)
                                     if x >> i & 1 and x >> j & 1)
                        q += 2 * (character & x).bit_count()
                        z = ((1, 0), (0, 1), (-1, 0), (0, -1))[q % 4]
                        real += z[0]
                        imag += z[1]
                    kernel.append((Q(real, 1 << n), Q(imag, 1 << n)))
                nonzero = [(a, b) for a, b in kernel if a or b]
                need(len(nonzero) == 1 << rank, 'Fourier support')
                need(all(a*a + b*b == Q(1, 1 << rank) for a, b in nonzero), 'Fourier norm')
                need(sum(abs(a) + abs(b) for a, b in kernel) == 1 << ((rank + 1)//2), 'Real box norm')
                need(max(max(a.denominator, b.denominator) for a, b in kernel)
                     == 1 << ((rank + 1)//2), 'Component denominator')
                forms += 1
                coefficients += len(kernel)
    c8 = []
    for character in range(256):
        real = imag = 0
        for x in range(256):
            exponent = (x.bit_count()+2*(character & x).bit_count()) % 4
            z = ((1, 0), (0, 1), (-1, 0), (0, -1))[exponent]
            real += z[0]
            imag += z[1]
        c8.append((Q(real, 256), Q(imag, 256)))
    need(all(a*a+b*b == Q(1, 256) for a, b in c8), 'C8 coefficient norm')
    need(sum(abs(a)+abs(b) for a, b in c8) == 16, 'C8 box norm')
    return {'forms': forms, 'coefficients': coefficients, 'C8_coefficients': len(c8),
            'method': 'Direct Gaussian Fourier sums'}


def source_data():
    manifests = [(CONSUMER, 'CONSUMER-MANIFEST.json',
                  'ca8f0cad4f445a8a13215a91b49f9cbfa9eb872e2bfed6b52feccdb948174419'),
                 (PRECISION, 'MANIFEST.json',
                  'f298bd0ad8fc3269204308cc9fee7a8809de9c5b1ef48da9de2efc742eaa50b8')]
    for folder, name, pin in manifests:
        manifest = json.loads(checked(folder/name, pin))
        for child, expected in manifest['files'].items():
            checked(folder/child, expected)
    local = json.loads(checked(CONSUMER/'REVIEW.json',
                              '8e8e444d8d36cfe24b7f40d61ff07ab48542fbab07a72bf323f44b8d4b0661c1'))
    for child, pin in local['files'].items():
        checked(CONSUMER/child, pin)
    need(local['status'] == 'PASS_INDEPENDENT_COMMON_F_LOCAL_REVIEW', 'Local component review')
    native_review = json.loads(checked(PACKET/'common-frame-source/evidence/NATIVE-REVIEW.json',
        'e9e9287a4a4d1be3c802899a42f70ff5dd5efd1e144a48bd585386fe234832e5'))
    need(native_review['status'] == 'PASS_INDEPENDENT_CONSERVED_QQ16_FULL_COVER_NATIVE_COMPONENTS',
         'Whole QQ16 native review')
    checked(LANES/'interface-proof/ORIGINAL-COMPLEX-MODES-REVIEW.json',
            '8b8c4d814b44c2fc42cf9ad995f8451512309fcfc46bea9317ebe4b4d79e8a4d')
    checked(LANES/'encoded-controller/QQ16-CONSERVED-CONTROLLER.md',
            'e18594af767a26b0202e857d45202f5f563db2a190b81a7ade8fd62fcef850b9')
    archive = ROOT/'worktrees/k5-persistent-cleanup/research/community-frontier1094-audit/selected-replay.tar.gz'
    checked(archive, 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6')
    members = {
        'template': ('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz',
                     '2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
        'phases': ('candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json',
                   'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'),
        'old_word': ('candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz',
                     '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219')}
    data = {}
    with tarfile.open(archive) as stream:
        for key, (name, pin) in members.items():
            raw = stream.extractfile(name).read()
            need(hashbytes(raw) == pin, 'Archive member: ' + name)
            PINS['archive-member:' + name] = pin
            data[key] = json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)
    data['word'] = json.loads(checked(PACKET/'common-frame-results/COMMON-F-RESTORATION-WORD.json',
        'c1fa3fe3596d939bbc42c0a41ad0078b43b74dca51fa41d7e3407736af07a74e'))
    data['native'] = json.loads(checked(PACKET/'common-frame-results/COMMON-F-NATIVE-RECIPES.json',
        '8b58ab9d9983d8b105387923464e8c7a5639b95b1efbe193aa83e9de18949e6e'))
    data['source'] = json.loads(gzip.decompress(checked(PACKET/'base/research/joint-query/certificate.json.gz',
        'a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7')))
    upstream = json.loads((PRECISION/'upstream-2603/FETCH.json').read_text())
    need(upstream['commit'] == '961288204c6138deac2bf8cf6ea348560bcf56d6', 'Upstream commit')
    for entry in upstream['files']:
        raw = (PRECISION/'upstream-2603'/entry['file']).read_bytes()
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == entry['git_blob'],
             'Upstream Git blob: ' + entry['file'])
    return data


def family(replica, pair, side, port):
    return 896*replica + 224*pair + 112*side + port


def canonical(q, level, side):
    if level < 0:
        return polynomial(((q, 1),)) if side == 0 else (0, 0, 0)
    words = tuple((v, 1) for v in I[:9+8*level])
    return polynomial(words + (((q, -1),) if side else ()))


def prepare_jobs(data):
    template, phases, old = data['template'], data['phases']['recipes'], data['old_word']
    events, calls = template['execution_schedule'], template['calls']
    need(len(events) == 482 and len(calls) == 144, 'Source schedule size')
    deadlines, touches, positions = {}, defaultdict(list), {}
    for at, e in enumerate(events):
        if e['kind'] == 'local_cover_sweep':
            c = calls[e['time']]
            touches[c['replica'], c['pair']].append(at)
            positions[e['time']] = at
        elif e['kind'] == 'bridge':
            touches[e['replica'], e['dst']].append(at)
            touches[e['replica'], e['src']].append(at)
        elif e['kind'] == 'idle_cover_sweep':
            for side, child in enumerate(e['child_indices']):
                deadlines[e['replica'], child] = at, side
    jobs, suffixes, covered = defaultdict(list), defaultdict(list), defaultdict(set)
    for job in template['hosting']['pooled_slots']:
        at, side = deadlines[job['owner_replica'], job['child']]
        e = events[at]
        release = max([-1] + [t for t in touches[job['owner_replica'], e['pair']] if t < at])
        need(release < positions[job['time']] < at, 'Whole helper window')
        f = family(job['owner_replica'], e['pair'], side, job['port'])
        reg = 224 + job['helper']
        width = len(old['frames'][old['final'][reg]]) - len(old['frames'][old['start'][reg]])
        need(width == job['width'] and f == job['family'], 'Helper owner and width')
        offset = job['offset']
        child = phases[job['port']]['idle_children'][job['child']]
        axes = child['orthogonal_axes'][offset:offset+width]
        need(len(axes) == width and width > 0, 'Helper axes')
        start = 1 + 8*(e['from_level']+1) + offset
        spectators = [j for j in range(73) if j not in range(start, start+width)][:9-width]
        route = [3, job['child'], offset] if width == 9 else [4, job['child'], offset, width, spectators]
        need(calls[job['time']]['owners'][reg] == [f, route], 'Literal helper route')
        key = job['owner_replica'], job['child'], job['port']
        slots = set(range(offset, offset+width))
        need(not slots & covered[key], 'Repeated helper axis')
        covered[key].update(slots)
        jobs[job['time']].append((f, polynomial(tuple((v, 1) for v in axes))))
    for job in template['idle_children']:
        at, side = deadlines[job['replica'], job['child']]
        e = events[at]
        f = family(job['replica'], e['pair'], side, job['port'])
        child = phases[job['port']]['idle_children'][job['child']]
        axes = child['orthogonal_axes'][job['pending_offset']:]
        need(f == job['family'] and len(axes) == job['rank'], 'Idle suffix owner and axes')
        key = job['replica'], job['child'], job['port']
        slots = set(range(job['pending_offset'], len(child['orthogonal_axes'])))
        need(not slots & covered[key], 'Repeated suffix axis')
        covered[key].update(slots)
        suffixes[at].append((f, polynomial(tuple((v, 1) for v in axes))))
    for (replica, child), (at, side) in deadlines.items():
        for port in range(112):
            need(covered[replica, child, port] == set(range(phases[port]['idle_children'][child]['rank'])),
                 'Incomplete idle partition')
    return jobs, suffixes, {'helper_jobs': sum(map(len, jobs.values())),
                            'idle_suffixes': sum(map(len, suffixes.values())), 'idle_windows': len(deadlines)//2}


def early_owner_separation(data):
    template = data['template']
    events, calls = template['execution_schedule'], template['calls']
    answer = []
    for replica in range(16):
        first = next(at for at, e in enumerate(events) if e['kind'] == 'local_cover_sweep'
                     and e['replica'] == replica and e['stage'] == 0)
        second = next(at for at, e in enumerate(events) if e['kind'] == 'local_cover_sweep'
                      and e['replica'] == replica and e['stage'] == 1)
        pair0 = set(range(896*replica, 896*replica+224))
        windows = {}
        for name, low, high in [('before_F0', 0, first), ('F0_to_B1', first+1, second)]:
            helper = active = idle = bridge = 0
            for at in range(low, high):
                e = events[at]
                if e['kind'] == 'local_cover_sweep':
                    owners = calls[e['time']]['owners']
                    helper += len(pair0 & {f for f, _ in owners[224:]})
                    active += len(pair0 & {f for f, _ in owners[:224]})
                if e.get('replica') == replica:
                    idle += int(e['kind'] == 'idle_cover_sweep' and e['pair'] == 0)
                    bridge += int(e['kind'] == 'bridge' and (e['dst'] == 0 or e['src'] == 0))
            need(helper == active == idle == bridge == 0, 'Early pair0 owner separation')
            windows[name] = {'helper_uses': helper, 'active_uses': active,
                             'idle_events': idle, 'bridge_events': bridge}
        answer.append({'replica': replica, 'F0_event': first, 'B1_event': second, 'windows': windows})
    return answer


def consumer_replay(data, jobs, suffixes, ports, mutation=None):
    phases, template = data['phases']['recipes'], data['template']
    frames = [canonical(phases[f % 112]['q'], -1, f//112 % 2) for f in range(14336)]
    extra, protected = set(), {}
    bridge_number, counts = Counter(), Counter()
    intervals, live, peak = [], {}, 0
    ports = set(ports)
    return_ports = set(range(112)) - ports
    if mutation == 'missing_return':
        return_ports.remove(min(return_ports))

    def update(f, phase):
        frames[f] = phase_sum(frames[f], phase)
        if f in protected:
            origin, old = protected[f]
            protected[f] = origin, phase_sum(old, phase)

    def check_pair(replica, pair, level):
        for side in range(2):
            for port in range(112):
                f = family(replica, pair, side, port)
                want = canonical(phases[port]['q'], level, side)
                if f in extra:
                    want = phase_sum(want, polynomial(((phases[port]['q'], 1),)))
                need(frames[f] == want, 'Complete native phase')

    for at, e in enumerate(template['execution_schedule']):
        kind, replica = e['kind'], e.get('replica')
        if kind == 'local_cover_sweep':
            call = template['calls'][e['time']]
            stage, pair = call['stage'], call['pair']
            need(call['replica'] == replica and stage == e['stage'], 'Actual call identity')
            owners = call['owners']
            need(len(owners) == len({owner[0] for owner in owners}) == 704, 'No owner alias')
            check_pair(replica, pair, stage - 1)
            for side in range(2):
                for port in range(112):
                    f = family(replica, pair, side, port)
                    need(owners[side*112+port] == [f, [1, stage, port]], 'Ordered active owner')
                    need(f not in extra and f not in protected, 'Active call reads a changed type or protected value')
                    frames[f] = canonical(phases[port]['q'], stage, side)
            for f, phase in jobs[e['time']]:
                counts['helper_jobs_on_extra_line_fields'] += int(f in extra)
                counts['helper_jobs_on_protected_fields'] += int(f in protected)
                update(f, phase)
            if stage == 0:
                slot = min(set(range(16)) - {value[1] for value in live.values()})
                live[replica] = at, slot
                peak = max(peak, len(live))
            if stage == 1:
                need(pair == 0, 'Repair pair')
                start, slot = live.pop(replica)
                intervals.append([replica, slot, start, at])
                for port in range(112):
                    f = family(replica, 0, 1, port)
                    update(f, polynomial(((phases[port]['q'], 1),)))
                    if port in return_ports:
                        update(f, polynomial(((phases[port]['q'], -1),)))
                    else:
                        extra.add(f)
                    if port in ports:
                        for side in range(2):
                            f = family(replica, 0, side, port)
                            raw_phase = polynomial(tuple((v, 1) for v in I[:17]) +
                                                   (((phases[port]['q'], -1),) if side == 0 else ()))
                            protected[f] = f, raw_phase
            counts['active_owner_sets'] += 1
        elif kind == 'idle_cover_sweep':
            for f, phase in suffixes[at]:
                update(f, phase)
            for side, child in enumerate(e['child_indices']):
                for port in range(112):
                    f = family(replica, e['pair'], side, port)
                    update(f, polynomial(((phases[port]['idle_children'][child]['translation_after'], 2),)))
            check_pair(replica, e['pair'], e['to_level'])
            counts['complete_idle_events'] += 1
        elif kind == 'bridge':
            number = bridge_number[replica]
            bridge_number[replica] += 1
            need((number < 6) == (e['source_event'] <= 18), 'First six literal source bridges')
            counts['selected_bridge_instances'] += int(number < 6 and bool(ports))
            for side in range(2):
                for port in range(112):
                    a, b = [family(replica, e[key], side, port) for key in ('dst', 'src')]
                    if port not in ports:
                        need(frames[a] == frames[b], 'Ordinary bridge phase')
                        need(a not in protected and b not in protected, 'Ordinary bridge uses protected data')
                    elif number < 6:
                        if mutation == 'missing_swap_' + str(number):
                            continue
                        frames[a], frames[b] = frames[b], frames[a]
                        ea, eb = a in extra, b in extra
                        extra.discard(a)
                        extra.discard(b)
                        if ea:
                            extra.add(b)
                        if eb:
                            extra.add(a)
                        pa, pb = protected.pop(a, None), protected.pop(b, None)
                        if pa:
                            protected[b] = pa
                        if pb:
                            protected[a] = pb
            counts['bridges'] += 1
        elif kind == 'terminal_Y_translations':
            for pair in e['pairs']:
                check_pair(replica, pair, 8)
                for port in set(range(112)) - ports:
                    update(family(replica, pair, 1, port), polynomial(((phases[port]['q'], 2),)))
        elif kind == 'terminal':
            for pair in range(e['pairs']):
                for port in set(range(112)) - ports:
                    x, y = [family(replica, pair, side, port) for side in range(2)]
                    need(x not in protected and y not in protected, 'Terminal uses protected data')
                    frames[x], frames[y] = frames[y], frames[x]
        elif kind == 'bank_padding_cover_sweep':
            need(not template['bank_padding']['children'], 'Source bank padding')
        else:
            need(kind == 'translate_every_live_family' and at == 481, 'Final cover correction')
            need(e['families'] == [0, 14336] and e['charged_calls_per_cover'] == 14336,
                 'All-live correction extent')
            # The final lines are immediately before this retained event.
            for replica0 in range(16):
                for port in ports:
                    x, y = [family(replica0, 0, side, port) for side in range(2)]
                    full = polynomial(tuple((v, 1) for v in I))
                    need(protected[x] == (x, phase_sum(full, polynomial(((phases[port]['q'], -1),)))),
                         'Raw X phase before correction')
                    need(protected[y] == (y, full), 'Raw Y phase before correction')
                    if mutation != 'missing_endpoint_line':
                        update(x, polynomial(((phases[port]['q'], 1),)))
                    need(protected[x] == (x, full), 'Final positive X correction')
            counts['retained_cover_corrections'] += 1
    need(not live and peak == 4, 'Record allocation peak')
    need(set(bridge_number.values()) == {9}, 'Nine bridges in every replica')
    expected = {family(r, 0, side, p) for r in range(16) for side in range(2) for p in ports}
    need(set(protected) == expected and {v[0] for v in protected.values()} == expected,
         'Protected output support and unique origins')
    overlap = max(sum(start <= at < end for _, _, start, end in intervals) for at in range(482))
    need(overlap == peak, 'Independent interval overlap count')
    counts.update(global_events=482, protected_outputs=len(expected), record_sets=peak,
                  whole_cover_records=16*peak, interval_overlap=overlap)
    return {'counts': dict(counts), 'record_intervals': intervals}


def scalar_swap():
    a, b = (Q(1), Q(0)), (Q(0), Q(1))
    add = lambda x, y, c: tuple(u+c*v for u, v in zip(x, y))
    a = add(a, b, 1)
    b = add(b, a, -1)
    a = add(a, b, 1)
    need((a, b) == ((0, 1), (-1, 0)), 'Swap prefixes before sign')
    b = tuple(-v for v in b)
    need((a, b) == ((0, 1), (1, 0)), 'Swap on arbitrary physical arrays')
    return {'complex_adds': 3, 'sign_scales': 1, 'real_scalar_allowance': 26,
            'fractional_reserve': 0, 'component_bound': 'H_a+H_b'}


def consumer_word_and_invoice(data):
    literal = json.loads((CONSUMER/'CONSUMER.word.json').read_text())
    need(literal['final_three_bridges_on_retired_ports'] == literal['terminal_on_retired_ports'] == [],
         'Literal omitted bridge and terminal word')
    cases = {}
    common = data['word']['capture_after_F0'] + data['word']['repair_after_B1']
    for name, ports in [('selected_16', SELECTED), ('whole_pair_112', tuple(range(112)))]:
        patch = literal['variants'][name]
        others = [p for p in range(112) if p not in ports]
        returns = [dict(op='line', field='Y'+str(p), port=p, rank=1, sign=-1) for p in others]
        endpoint = [dict(op='line', field='X'+str(p), port=p, rank=1, sign=1) for p in ports]
        swaps = []
        for side in ('X', 'Y'):
            for p in ports:
                a, b = side+'_dst:'+str(p), side+'_src:'+str(p)
                swaps += [dict(op='add', dst=a, src=b, c=1), dict(op='add', dst=b, src=a, c=-1),
                          dict(op='add', dst=a, src=b, c=1), dict(op='scale', field=b, c=-1)]
        need(patch['retired_ports'] == list(ports) and patch['return_after_repair'] == returns
             and patch['final_pair0_X_correction'] == endpoint
             and patch['port_swap_each_first_six_bridge'] == swaps, 'Literal patch operations')
        profile = Counter(e['rank'] for e in common+returns+endpoint if e['op'] in ('line', 'stage'))
        need(profile == {1:224, 8:16}, 'Literal added native profile')
        w = len(ports)
        cases[name] = {'native_profile': dict(profile), 'native_mass': sum(r*n for r, n in profile.items()),
                       'wrappers': 2*sum(profile.values()), 'two_boundary_bridge_allowance': 4*(112-w)*8+4*w*26,
                       'all_nine_bridge_allowance': 18*(112-w)*8+12*w*26}
        need(cases[name]['two_boundary_bridge_allowance'] == 3584+72*w
             and cases[name]['all_nine_bridge_allowance'] == 16128+168*w, 'Bridge scalar formulas')
    scalar = 0
    for e in common:
        if e['op'] == 'clear':
            scalar += 2
        elif e['op'] in ('add', 'scale'):
            c = Q(e['c'])
            a, b = abs(c.numerator), c.denominator
            need(a > 0 and b & (b-1) == 0, 'Scalar coefficient')
            if e['op'] == 'add':
                scalar += 2*(2+a.bit_length()+a.bit_count()+b.bit_length()-1)
            else:
                need(a & (a-1) == 0, 'Scale numerator')
                scalar += 2*(abs(a.bit_length()-b.bit_length())+int(c < 0))
    need(scalar == 16338 and sum(e['op'] == 'map' for e in common) == 208, 'Repair scalar and map invoice')
    return {'cases': cases, 'added_scalar_allowance': scalar, 'added_cover_maps': 208,
            'all_subset_native_profile': {'1':224, '8':16},
            'all_subset_mass_identity': '240+(112-w)+w=352'}


def precision_replay(data, return_ports, wrong_owner_order=False):
    word, native = data['word'], data['native']
    old, full = tuple((v, 1) for v in I[:9]), tuple((v, 1) for v in I[:17])
    source_frames = {'E'+str(p): old for p in SELECTED}
    source_frames.update({'X'+str(p): full for p in range(112)})
    source_frames.update({'Y'+str(p): full+((native['line_'+str(p)]['label'], -1),) for p in range(112)})
    rows, frames = {}, {}
    for p in SELECTED:
        f = 'X'+str(p)
        rows[f] = {('E'+str(p), I): (Q(1), ())}
        frames[f] = old
    for f in ['R'+str(p) for p in SELECTED] + ['C']:
        rows[f] = {('dirt:'+f, I): (Q(1), ())}
        source_frames['dirt:'+f] = ()
        frames[f] = ()
    events = word['capture_after_F0'] + [{'op':'boundary'}] + word['repair_after_B1']
    events += [dict(op='line', field='Y'+str(p), port=p, sign=-1, rank=1) for p in return_ports]
    history, debt_max, weight_max = [], {}, Counter()
    terms_count = factorization_checks = 0
    physical_operators = set()
    private = False

    def append_phase(row, delta):
        return {key: (c, phase_word(phase+delta)) for key, (c, phase) in row.items()}

    for at, e in enumerate(events):
        op, touched = e['op'], []
        if op == 'boundary':
            for side in ('X', 'Y'):
                for p in range(112):
                    f = side+str(p)
                    rows[f] = {(f, I): (Q(1), ())}
                    frames[f] = source_frames[f]
                    touched.append(f)
        elif op == 'clear':
            f = e['field']
            need(f.startswith('R') or f == 'C', 'Owned CLEAR')
            rows[f] = {}
            frames[f] = {'identity': (), 'old': old, 'current': full}[e['frame']]
            touched = [f]
        elif op == 'add':
            dst, src = e['dst'], e['src']
            need(polynomial(phase_word(frames[dst])) == polynomial(phase_word(frames[src])), 'ADD phase')
            result = dict(rows[dst])
            for key, (coefficient, phase) in rows[src].items():
                coefficient *= Q(e['c'])
                if key in result:
                    a, other = result[key]
                    need(polynomial(other) == polynomial(phase), 'Equal physical source phase')
                    coefficient += a
                if coefficient:
                    result[key] = coefficient, phase
                else:
                    result.pop(key, None)
            rows[dst] = result
            touched = [dst]
        elif op == 'scale':
            f = e['field']
            rows[f] = {key: (c*Q(e['c']), phase) for key, (c, phase) in rows[f].items() if c*Q(e['c'])}
            touched = [f]
        elif op in ('line', 'stage'):
            f = e['field']
            if op == 'line':
                need(e['rank'] == 1, 'Physical line rank')
                delta = ((native['line_'+str(e['port'])]['label'], e['sign']),)
            else:
                need(e['rank'] == 8 and e['stage'] == e['sign'] == 1, 'Record lift')
                delta = tuple((v, 1) for v in I[9:17])
            rows[f] = append_phase(rows[f], delta)
            frames[f] = phase_word(frames[f]+delta)
            touched = [f]
        elif op == 'map':
            f, g, shift = e['field'], tuple(e['g']), e['shift']
            need(len(g) == 73 and compose(g, g) == I, 'Full owner involution')
            moved = {}
            for (source, owner), (c, phase) in rows[f].items():
                matrix = compose(owner, g) if wrong_owner_order else compose(g, owner)
                need((source, matrix) not in moved, 'Bijective source owner map')
                moved[source, matrix] = c, transport(g, phase, shift)
            rows[f] = moved
            frames[f] = transport(g, frames[f], shift)
            touched = [f]
        elif op == 'private_begin':
            need(not private, 'Private begin')
            private = True
        else:
            need(op == 'private_end' and private and not rows['C'], 'Private end')
            private = False
        for f in touched:
            weights, bound_debt = Counter(), 0
            for (source, owner), (c, physical_phase) in rows[f].items():
                need(c.denominator & (c.denominator-1) == 0, 'Dyadic coefficient')
                expected = phase_word(frames[f] + tuple((act(owner, v), -a) for v, a in source_frames[source]))
                need(polynomial(physical_phase) == polynomial(expected), 'Physical phase and right-owner factorization')
                factorization_checks += 1
                rank = phase_rank(physical_phase)
                d = c.denominator.bit_length() - (abs(c.numerator) & -abs(c.numerator)).bit_length()
                weights[rank] += abs(c)
                debt_max[rank] = max(debt_max.get(rank, -1000), d)
                bound_debt = max(bound_debt, d+(rank+1)//2)
                terms_count += 1
                physical_operators.add((source, owner, polynomial(physical_phase)))
            for rank, value in weights.items():
                weight_max[rank] = max(weight_max[rank], value)
            gain = sum(value*(1 << ((rank+1)//2)) for rank, value in weights.items())
            history.append([at, f, bound_debt, str(gain), [[r, str(w)] for r, w in sorted(weights.items())]])
    need(not private and all(not rows['R'+str(p)] for p in SELECTED) and not rows['C'], 'Owned outputs zero')
    for p in set(range(112)) - set(SELECTED):
        wanted = ((native['line_'+str(p)]['label'], -1),) if p in return_ports else ()
        need(rows['Y'+str(p)] == {('X'+str(p), I): (Q(-1), phase_word(wanted))}, 'Ordinary Y physical row')
    if not set(return_ports) & set(SELECTED):
        need(debt_max == {0:1, 1:1, 8:2}, 'All-layer debt census')
        need(weight_max == {0:Q(136), 1:Q(136), 8:Q(412)}, 'All-layer weight census')
    need(max(row[2] for row in history) > 5 and max(Q(row[3]) for row in history) > 4096,
         'Reduced term-grid and triangle certificates')
    return {'events': len(events), 'changed_field_boundaries': len(history), 'term_checks': terms_count,
            'factorization_checks': factorization_checks, 'distinct_physical_operators': len(physical_operators),
            'distinct_phase_polynomials': len({item[2] for item in physical_operators}),
            'distinct_owner_and_phase_operators': len({(item[1], item[2]) for item in physical_operators}),
            'scalar_denominator_debt_by_phase_rank': {str(r): d for r, d in sorted(debt_max.items())},
            'coefficient_weight_envelope_by_phase_rank': {str(r): str(w) for r, w in sorted(weight_max.items())},
            'prefix_table_sha256': hashbytes(encoded(history)),
            'one_layer_gain_witness': max(history, key=lambda row: Q(row[3])),
            'source_model': 'Independent raw physical arrays; no source frame is used to update a term.'}


def endpoint_recipes(data):
    labels = []
    registry = data['source']['map_registry']
    for p in range(112):
        recipe = data['native']['line_'+str(p)]
        left, right, q = tuple(recipe['left_columns']), tuple(recipe['right_columns']), recipe['label']
        need(compose(left, right) == I and compose(right, left) == I, 'Native wrapper inverse')
        need(left[0] == q and recipe['positive_left_translation'] == 0, 'Positive C_q recipe')
        need(q == data['phases']['recipes'][p]['q'], 'Native line uses the actual port')
        event = next(e for e in data['source']['programs']['F_2'] if e[0] == 'cover_map' and e[1] == ['L', p])
        route = tuple(registry[event[2]]['owner_right_matrix_columns'])
        need(act(route, q) == q, 'Actual F2 route fixes q')
        need(polynomial(((q, 1), (q, -1))) == (0, 0, 0), 'Positive line cancels the raw X inverse')
        labels.append(q)
    return {'positive_line_recipes': len(labels), 'F2_fixed_normals': labels}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=HERE/'INDEPENDENT.json')
    args = parser.parse_args()
    need(args.out.resolve().parent == HERE, 'Review output directory')
    need(shutil.disk_usage(HERE).free >= 3*1024**3, 'Three GiB free')
    data = source_data()
    jobs, suffixes, partition = prepare_jobs(data)
    published_consumer = json.loads((CONSUMER/'CONSUMER.json').read_text())
    consumers = {}
    for name, ports in [('selected_16', SELECTED), ('whole_pair_112', tuple(range(112))), ('empty_set', ())]:
        result = consumer_replay(data, jobs, suffixes, ports)
        if name in published_consumer['checks']:
            expected = published_consumer['checks'][name]
            need(result['record_intervals'] == expected['owned_record_intervals'], 'Published record intervals')
            need(result['counts']['helper_jobs_on_extra_line_fields'] == expected['old_helper_jobs_on_extra_line_fields'],
                 'Published helper count')
        consumers[name] = result
    controls = {}
    for mutation in ('missing_return', 'missing_swap_0', 'missing_swap_1', 'missing_endpoint_line'):
        try:
            consumer_replay(data, jobs, suffixes, SELECTED, mutation)
        except ValueError as error:
            controls[mutation] = str(error)
        else:
            raise ValueError('Consumer control accepted: ' + mutation)
    precision = {}
    published_precision = json.loads((PRECISION/'PRECISION.json').read_text())
    for name, ports in [('common_F', ()), ('selected_16_return', tuple(p for p in range(112) if p not in SELECTED)),
                        ('old_mixed_return', tuple(range(112)))]:
        result = precision_replay(data, ports)
        expected = published_precision['cases'][name]
        for key in ('events', 'changed_field_boundaries', 'term_checks', 'scalar_denominator_debt_by_phase_rank',
                    'coefficient_weight_envelope_by_phase_rank', 'prefix_table_sha256', 'one_layer_gain_witness'):
            need(result[key] == expected[key], 'Independent physical census: '+name+'/'+key)
        precision[name] = result
    try:
        precision_replay(data, (), True)
    except ValueError as error:
        controls['reversed_owner_composition'] = str(error)
    else:
        raise ValueError('Reversed owner composition control accepted')
    invoice = consumer_word_and_invoice(data)
    result = {'status': 'PASS_INDEPENDENT_COMMON_F_CONSUMER_AND_PRECISION_REVIEW',
              'producer_or_upstream_module_imported': False, 'source_pins': PINS,
              'consumer': consumers, 'complete_helper_partition': partition,
              'early_pair0_owner_separation': early_owner_separation(data),
              'native_endpoint_recipes': endpoint_recipes(data), 'added_invoice': invoice,
              'physical_swap': scalar_swap(), 'precision': precision,
              'phase_kernel': phase_kernel_check(), 'negative_controls': controls,
              'findings': [{'severity': 'nonmaterial census label',
                  'location': 'PRECISION.md: Phase bound and actual census; PRECISION.json: distinct_relative_phase_operators',
                  'observation': 'The value 4804 counts cache keys (frame tuple, source label, owner matrix). It is not the number of distinct phase operators. The canonical physical census has at most 856 source-owner-phase terms.',
                  'effect': 'No change to any prefix bound or acceptance of the conditional precision theorem.',
                  'suggested_wording': '4804 distinct relative-phase cache keys'}],
              'inherited_contracts': ['Exact local common-F recovery on arbitrary inputs',
                  'QQ16 whole helper outputs and active/helper zero cross-dependence',
                  'Fixed-owner native helper endpoint and all-cover final correction'],
              'omitted': ['Full upstream suite', 'Old child kernel suite', 'Physical entry guarantees from F0 and B1',
                  'Approximate children', 'Scalar primitive interiors', 'Child internal precision',
                  'New record and child hosting', 'Global controller precision', 'Other output target map',
                  'Complete supplier or kappa claim']}
    need(shutil.disk_usage(HERE).free >= 3*1024**3, 'Three GiB free at completion')
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': result['status'], 'sha256': hashbytes(args.out.read_bytes()),
                      'consumer_counts': {name: value['counts'] for name, value in consumers.items()},
                      'precision_prefix_hashes': {name: value['prefix_table_sha256'] for name, value in precision.items()}}))


if __name__ == '__main__':
    main()
