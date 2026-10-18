#!/usr/bin/env python3
"""Zero-retention QQ16 comparison. Arham Tahir with OpenAI Codex; Apache-2.0.

Independent ordered replay of published QQ16 equations. No predecessor Python
is imported or executed. Native kernels remain explicit child contracts.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AXES = tuple(1 << i for i in range(73))
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
V = A + T
U = tuple(p for p in range(112) if p not in V)
F17 = tuple((v, 1) for v in AXES[:17])
F25 = tuple((v, 1) for v in AXES[:25])
BLOCK = AXES[17:25]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    raw = {}
    for item in pins['files']:
        if item['usage'] == 'input':
            data = (ROOT / item['path']).read_bytes()
            need(digest(data) == item['sha256'], 'source hash: ' + item['path'])
            raw[item['path']] = data
    for item in pins['pending_sources']:
        data = (HERE / item['local_path']).read_bytes()
        need(digest(data) == item['sha256'], 'pending source hash')
    return raw


def act(g, v):
    out = 0
    while v:
        bit = v & -v
        out ^= g[bit.bit_length() - 1]
        v ^= bit
    return out


@lru_cache(None)
def product(g, h):
    return tuple(act(g, v) for v in h)


@lru_cache(None)
def phase(terms):
    linear, cross = [0] * 73, [0] * 73
    for v, c in terms:
        bits = [i for i in range(73) if (v >> i) & 1]
        for i in bits:
            linear[i] = (linear[i] + c) % 4
            if c % 2:
                for j in bits:
                    if j > i:
                        cross[i] ^= 1 << j
    return tuple(linear), tuple(cross)


def move(terms, g, shift):
    return tuple((act(g, v), c) for v, c in terms) + ((shift, 2),)


@lru_cache(None)
def alignment(g, frame):
    before = phase(frame)
    after = phase(tuple((act(g, v), c) for v, c in frame))
    need(before[1] == after[1], 'nonlinear frame discrepancy')
    diffs = [(x - y) % 4 for x, y in zip(before[0], after[0])]
    need(all(d in (0, 2) for d in diffs), 'odd frame discrepancy')
    b = sum((d // 2) << i for i, d in enumerate(diffs))
    need(phase(move(frame, g, b)) == before, 'full frame polynomial')
    return b


def load(raw):
    packet = json.loads(gzip.decompress(raw['research/joint-query/certificate.json.gz']))
    need(tuple(packet['A_ports']) == A and tuple(packet['T_ports']) == T
         and tuple(packet['U_ports']) == U, 'actual port partition')
    R = [[Q(row.get(str(p), 0)) for p in range(112)] for row in packet['R_rows']]
    name = 't16/global/base/work/complex-nine-native/DATA-PHASES.json'
    member_pins = {
        name: 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
        'slots/local/CANONICAL-WORD.json.gz': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
        'slots/local/LOCAL-PROGRAMS.json.gz': '241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a',
    }
    decoded = {}
    with tarfile.open(fileobj=io.BytesIO(raw['research/community-frontier1042-audit/selected-replay.tar.gz']), mode='r:gz') as tar:
        for member, pin in member_pins.items():
            matches = [m for m in tar.getmembers() if m.name == member]
            need(len(matches) == 1 and matches[0].isfile(), 'unique source member')
            data = tar.extractfile(matches[0]).read()
            need(digest(data) == pin, 'archive member hash')
            decoded[member] = json.loads(gzip.decompress(data) if member.endswith('.gz') else data)
    phases = decoded[name]
    source_word = decoded['slots/local/CANONICAL-WORD.json.gz']
    programs = decoded['slots/local/LOCAL-PROGRAMS.json.gz']
    rows = [{i: Q(1)} for i in range(712)]
    def index(token): return token[1] + (704 if token[0] == 'C' else 0)
    for event in programs['forward']:
        if event == ['phase', 'centers']: break
        if event[0] != 'scalar': continue
        op = event[1]; at = index(op[1])
        if op[0] == 'clear': rows[at] = {}
        elif op[0] == 'scale': rows[at] = {j: c * Q(op[2], op[3]) for j, c in rows[at].items()}
        else:
            need(op[0] in ('copy', 'add'), 'known source scalar gate')
            src = rows[index(op[2])]
            rows[at] = dict(src) if op[0] == 'copy' else add(rows[at], src, Q(op[3], op[4]))
    else: raise ValueError('missing source centre boundary')
    need(R == [[rows[c].get(p, Q(0)) for p in range(112)] for c in source_word['centers']],
         'R reconstructed from immutable selected scalar prefix')
    routes = {0: [AXES] * 112, 1: [], 2: []}
    labels = []
    registry = {tuple(m['owner_right_matrix_columns']) for m in packet['map_registry'].values()}
    for p, record in enumerate(phases['recipes']):
        q = record['q']; basis = tuple(record['idle_children'][0]['orthogonal_axes'][:8])
        need(record['port'] == p and q == source_word['ports'][p] and q < 512, 'source port label')
        basis9 = (q,) + basis
        need(all((a & b).bit_count() % 2 == (i == j)
                 for i, a in enumerate(basis9) for j, b in enumerate(basis9)), 'actual orthonormal basis')
        labels.append(q)
        for stage in (1, 2):
            swaps = [b ^ AXES[9 + 8 * (stage - 1) + i] for i, b in enumerate(basis)]
            g = tuple(v ^ act(swaps, sum(((v & s).bit_count() % 2) << i
                                         for i, s in enumerate(swaps))) for v in AXES)
            need(product(g, g) == AXES and g in registry, 'actual involutive route')
            need(all((a & b).bit_count() % 2 == (i == j)
                     for i, a in enumerate(g) for j, b in enumerate(g)), 'route orthogonality')
            routes[stage].append(g)
    for subset, mass in ((A, 4), (T, 4), (U, 48)):
        need(all(sum(R[i][p] * R[j][p] for p in subset) == mass * (i == j)
                 for i in range(8) for j in range(8)), 'Gram identity')
    need(all(sum(R[k][p] ** 2 for k in range(8)) == 4 for p in range(112)), 'four terms per port')
    return R, routes, labels


def add(left, right, coefficient=1):
    result = dict(left)
    for key, value in right.items():
        new = result.get(key, Q(0)) + coefficient * value
        if new: result[key] = new
        else: result.pop(key, None)
    return result


def routed(g, row):
    return {(source, product(g, h)): c for (source, h), c in row.items()}


def query(R, routes, stage, bank, subset):
    rows = [{} for _ in range(8)]
    for k in range(8):
        for p in subset:
            if R[k][p]: rows[k] = add(rows[k], routed(routes[stage][p], bank[p]), R[k][p])
    return rows


def inject(R, routes, stage, q, subset):
    out = [{} for _ in range(112)]
    for p in subset:
        for k in range(8):
            if R[k][p]: out[p] = add(out[p], routed(routes[stage][p], q[k]), R[k][p] / 4)
    return out


def forward(R, routes, x, y):
    """Separate implementation of the published F0, then conserved B1 map."""
    full = query(R, routes, 0, x, range(112))
    old_t = query(R, routes, 0, x, T)
    kfull = inject(R, routes, 0, full, U + T)
    old = inject(R, routes, 0, old_t, A)
    x1 = [add(x[p], kfull[p], -1) if p in U else (old[p] if p in A else kfull[p]) for p in range(112)]
    y1 = [add(y[p], x1[p]) if p in U else add(add(x[p], y[p]), x1[p], -1) for p in range(112)]
    future = inject(R, routes, 2, query(R, routes, 2, y1, U + T), A)
    u = [add(y1[p], future[p]) for p in range(112)]
    a = query(R, routes, 1, x1, T); b = query(R, routes, 1, u, range(112))
    ku = inject(R, routes, 1, a, U); pa = inject(R, routes, 1, a, T); pb = inject(R, routes, 1, b, T)
    y2 = [add(y1[p], ku[p]) if p in U else (u[p] if p in A else add(add(u[p], pb[p], -1), pa[p], -11)) for p in range(112)]
    x2 = [add(x1[p], y1[p], -1) if p in U else add(add(x1[p], y1[p]), y2[p], -1) for p in range(112)]
    return x2, y2, x1, y1


def word(R):
    w = []
    def emit(op, *args): w.append([op, *args])
    def clear(name, frame='wide'): emit('clear', name, frame)
    def plus(dst, src, c=1): emit('add', dst, src, str(c))
    def maps(stage, names, inverse=False):
        for side, p in names: emit('map', side + str(p), stage, p, inverse)
    for p in range(112):
        for out, src in (('Z', 'X'), ('W', 'Y')):
            clear(out + str(p), 'current' if src == 'X' else 'hole' + str(p))
            plus(out + str(p), src + str(p))
            if src == 'Y': emit('line', out + str(p), p, 1)
            emit('stage', out + str(p), 1)
    for p in V: plus('Z' + str(p), 'W' + str(p))
    names = [('W', p) for p in range(112)] + [('Z', p) for p in T]
    maps(1, names); emit('begin', 'B1_current_query', 8)
    for k in range(8):
        clear('F' + str(k))
        for p in range(112):
            if R[k][p]: plus('F' + str(k), 'W' + str(p), R[k][p])
    for p in U + T:
        if p in T:
            clear('W' + str(p)); plus('W' + str(p), 'Z' + str(p))
        for k in range(8):
            if R[k][p]: plus('W' + str(p), 'F' + str(k), -R[k][p] / 4)
    for k in range(8): clear('F' + str(k), 'identity')
    emit('end', 'B1_current_query', 8); maps(1, names, True)
    names = [('W', p) for p in range(112)]
    maps(2, names); emit('begin', 'future_logger_inverse', 8)
    for k in range(8):
        clear('F' + str(k))
        for p in U + T:
            if R[k][p]: plus('F' + str(k), 'W' + str(p), R[k][p])
    for p in A:
        for k in range(8):
            if R[k][p]: plus('W' + str(p), 'F' + str(k), -R[k][p] / 4)
    for k in range(8): clear('F' + str(k), 'identity')
    emit('end', 'future_logger_inverse', 8); maps(2, names, True)
    for p in range(112): plus('Z' + str(p), 'W' + str(p), 1 if p in U else -1)
    emit('checkpoint', 'original_F0_outputs')
    for p in range(112): plus('W' + str(p), 'Z' + str(p), -1 if p in U else 1)
    emit('begin', 'F0_inverse', 16)
    for k in range(8):
        clear('F' + str(k)); clear('G' + str(k))
        for p in T:
            if R[k][p]: plus('F' + str(k), 'Z' + str(p), R[k][p])
        for p in A:
            if R[k][p]: plus('G' + str(k), 'Z' + str(p), R[k][p])
    for p in U:
        for k in range(8):
            if R[k][p]: plus('Z' + str(p), 'F' + str(k), R[k][p] / 4)
    for k in range(8):
        plus('F' + str(k), 'G' + str(k), -1)
        for p in U:
            if R[k][p]: plus('F' + str(k), 'Z' + str(p), -R[k][p])
    for p in V:
        clear('Z' + str(p))
        for k in range(8):
            if R[k][p]: plus('Z' + str(p), ('F' if p in A else 'G') + str(k), R[k][p] / 4)
    for side in ('F', 'G'):
        for k in range(8): clear(side + str(k), 'identity')
    emit('end', 'F0_inverse', 16)
    for p in V: plus('W' + str(p), 'Z' + str(p), -1)
    for p in range(112):
        for side in ('Z', 'W'): emit('stage', side + str(p), -1)
    return w


def replay(w, routes, labels, x2, y2, expected, middle=None):
    owned = {s + str(p) for s in ('Z', 'W') for p in range(112)}
    rows = {name: {(name, AXES): Q(1)} for name in owned}; frames = {name: () for name in owned}
    for side, bank in (('X', x2), ('Y', y2)):
        for p in range(112):
            name = side + str(p); rows[name] = bank[p]
            frames[name] = F17 + (((labels[p], -1),) if side == 'Y' else ())
    borrowed = {n: dict(r) for n, r in rows.items() if n[0] in ('X', 'Y')}
    borrowed_frames = {n: frames[n] for n in borrowed}
    active = set(); counts = Counter()
    for index, e in enumerate(w):
        op = e[0]; counts[op] += 1
        if op == 'begin':
            need(not active, 'overlapping private sweeps')
            active = {'F' + str(k) for k in range(8)}
            if e[2] == 16: active |= {'G' + str(k) for k in range(8)}
            need(e[2] == len(active), 'private scratch count')
            for name in active: rows[name], frames[name] = {(name, AXES): Q(1)}, ()
        elif op == 'end':
            need(len(active) == e[2], 'private boundary')
            need(all(not rows[n] and phase(frames[n]) == phase(()) for n in active), 'scratch leak')
            for name in active: del rows[name], frames[name]
            active = set()
        elif op == 'clear':
            _, name, f = e; need(name in owned | active, 'clear borrowed input'); rows[name] = {}
            frames[name] = {'wide': F25, 'current': F17, 'identity': ()}.get(f)
            if f.startswith('hole'): frames[name] = F17 + ((labels[int(f[4:])], -1),)
            need(frames[name] is not None, 'unknown clear frame')
        elif op == 'add':
            _, dst, src, q = e
            need(dst in owned | active and dst != src, 'ADD ownership/alias')
            need(dst in rows and src in rows, 'nonlive ADD role')
            need(phase(frames[dst]) == phase(frames[src]), 'ADD frame mismatch ' + str(index))
            q = Q(q); need(abs(q) in (1, Q(1, 4)), 'unpriced coefficient')
            rows[dst] = add(rows[dst], rows[src], q)
            counts['unit_ADD' if abs(q) == 1 else 'quarter_ADD'] += 1
        elif op == 'line':
            _, name, p, sign = e
            need(not active and name in owned and sign in (-1, 1), 'line boundary')
            frames[name] += ((labels[p], sign),)
        elif op == 'stage':
            _, name, sign = e
            need(not active and name in owned and sign in (-1, 1), 'stage boundary')
            frames[name] += tuple((v, sign) for v in BLOCK)
        elif op == 'map':
            _, name, stage, p, inverse = e[:5]
            need(not active and name in owned and stage in (1, 2), 'map inside private sweep')
            g = routes[stage][p]; b = alignment(g, F25)
            if inverse: b = act(g, b)
            if len(e) > 5 and e[5] == 'omit_shift': b = 0
            frames[name] = move(frames[name], g, b); rows[name] = routed(g, rows[name])
        elif op == 'checkpoint':
            need(not active, 'incomplete sweep at checkpoint')
            if middle is not None:
                need([rows['Z' + str(p)] for p in range(112)] == middle[0]
                     and [rows['W' + str(p)] for p in range(112)] == middle[1], 'inverse B1 checkpoint')
        else: raise ValueError('unknown event')
    need(not active, 'unterminated private sweep')
    for side, bank in zip(('Z', 'W'), expected):
        for p in range(112):
            name = side + str(p)
            need(rows[name] == bank[p], 'wrong output ' + name)
            need(phase(frames[name]) == phase(F17), 'wrong final frame')
    need(all(rows[n] == r and frames[n] == borrowed_frames[n] for n, r in borrowed.items()), 'borrowed restoration')
    return counts


def inverse_formula(R, routes, x2, y2):
    """Equation (8) specialized to conserved sums, independently of the word."""
    a = query(R, routes, 1, y2, range(112))
    pa = inject(R, routes, 1, a, T); ka = inject(R, routes, 1, a, U)
    u = [add(y2[p], ka[p], -1) if p in U else
         (dict(y2[p]) if p in A else add(add(y2[p], x2[p]), pa[p], -1)) for p in range(112)]
    correction = inject(R, routes, 2, query(R, routes, 2, u, U + T), A)
    y1 = [add(u[p], correction[p], -1) for p in range(112)]
    x1 = [add(x2[p], y1[p]) if p in U else add(add(x2[p], y2[p]), y1[p], -1) for p in range(112)]
    f = query(R, routes, 0, x1, T); c = query(R, routes, 0, x1, A)
    kf = inject(R, routes, 0, f, U)
    x0 = [add(x1[p], kf[p]) if p in U else {} for p in range(112)]
    rz = query(R, routes, 0, x1, U)
    old_a = [add(add({key: -11 * v for key, v in f[k].items()}, rz[k], -1), c[k], -1) for k in range(8)]
    ia = inject(R, routes, 0, old_a, A); it = inject(R, routes, 0, c, T)
    for p in V: x0[p] = ia[p] if p in A else it[p]
    y0 = [add(y1[p], x1[p], -1) if p in U else add(add(x1[p], y1[p]), x0[p], -1) for p in range(112)]
    return x0, y0


def kernel_checks(labels):
    def mul(a, b): return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]
    powers = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for mask in range(256):
        pos = neg = (1, 0)
        for j in range(8):
            pos = mul(pos, (1, -1 if mask >> j & 1 else 1))
            neg = mul(neg, (1, 1 if mask >> j & 1 else -1))
        h = mask.bit_count()
        need(pos == tuple(16 * x for x in powers[-h % 4]), 'positive rank8 factorization')
        need(neg == tuple(16 * x for x in powers[h % 4]), 'negative rank8 factorization')
        need(neg == tuple(16 * x for x in powers[-(8-h) % 4]), 'negative translation wrapper')
    permutation = list(AXES)
    for i in range(8): permutation[i], permutation[17+i] = permutation[17+i], permutation[i]
    need(product(tuple(permutation), tuple(permutation)) == AXES, 'rank8 wrapper inverse')
    need(tuple(permutation[:8]) == BLOCK, 'rank8 wrapper active block')
    for q in labels:
        need(q and q.bit_count() % 2, 'intrinsic line')
        pivot = (q & -q).bit_length() - 1
        basis = (q,) + tuple(1 << i for i in range(9) if i != pivot)
        inverse = {act(basis, x): x for x in range(512)}
        need(len(inverse) == 512, 'rank1 wrapper invertibility')
        for address in range(512):
            middle = inverse[address]
            lowered = {act(basis, middle): (1, 1), act(basis, middle ^ 1): (1, -1)}
            need(lowered == {address: (1, 1), address ^ q: (1, -1)}, 'rank1 child kernel')
    return {'rank8_difference_coefficients': 256, 'rank1_basis_columns': 112 * 512,
            'lowering': 'one positive child and two monomial wrappers per signed line/block'}


def direct_map_checks(routes, records):
    """Independent character sums on a complete basis for degree-two phases."""
    characters = [0] + list(AXES) + [AXES[i] ^ AXES[j] for i in range(73) for j in range(i + 1, 73)]
    checked = 0
    for stage, port, shift in records:
        g = routes[stage][port]
        for z in characters:
            lhs = (sum((z & g[j]).bit_count() % 2 for j in range(25))
                   + 2 * ((z & shift).bit_count() % 2)) % 4
            rhs = (z & ((1 << 25) - 1)).bit_count() % 4
            need(lhs == rhs, 'literal character/frame identity')
            checked += 1
    return checked


def compute():
    raw = authenticate(); R, routes, labels = load(raw); w = word(R)
    original = [[{(side + str(p), AXES): Q(1)} for p in range(112)] for side in ('x', 'y')]
    x2, y2, x1, y1 = forward(R, routes, *original)
    counts = replay(w, routes, labels, x2, y2, original, (x1, y1))
    current = [[{(side + str(p), AXES): Q(1)} for p in range(112)] for side in ('X', 'Y')]
    inv = inverse_formula(R, routes, *current)
    replay(w, routes, labels, *current, inv)
    need(forward(R, routes, *inv)[:2] == tuple(current), 'other inverse order')
    frame_records = []
    for s in (1, 2):
        for p, g in enumerate(routes[s]):
            b = alignment(g, F25); need(act(g, b) == b, 'route involution')
            frame_records.append([s, p, b])
    controls = {}
    def reject(name, mutate):
        bad = deepcopy(w); mutate(bad)
        try: replay(bad, routes, labels, *current, inv)
        except (ValueError, KeyError) as error: controls[name] = str(error)
        else: raise ValueError('ineffective control: ' + name)
    def first(seq, op): return next(i for i, e in enumerate(seq) if e[0] == op)
    reject('missing input line', lambda b: b.pop(first(b, 'line')))
    reject('missing frame upgrade', lambda b: b.pop(first(b, 'stage')))
    def wrong_current_sign(b):
        e = next(e for e in b if e[0] == 'add' and e[1].startswith('W')
                 and int(e[1][1:]) in U and e[2].startswith('F'))
        e[3] = str(-Q(e[3]))
    reject('wrong source-query sign', wrong_current_sign)
    reject('missing output clear', lambda b: b.pop(0))
    reject('borrowed clear', lambda b: b[0].__setitem__(1, 'X0'))
    def wrong_future_chart(b):
        for e in b:
            if e[0] == 'map' and e[2] == 2: e[2] = 1
    reject('future chart replaced by current chart', wrong_future_chart)
    reject('missing output downgrade', lambda b: b.pop())
    reject('scratch leakage', lambda b: b.pop(next(i for i, e in enumerate(b) if e == ['clear', 'F0', 'identity'])))
    def wrong_future_sign(b):
        e = next(e for e in b if e[0] == 'add' and e[1].startswith('W')
                 and int(e[1][1:]) in A and e[2].startswith('F'))
        e[3] = str(-Q(e[3]))
    reject('missing future inverse', wrong_future_sign)
    reject('wrong F0 inverse', lambda b: next(e for e in b if e[:3] == ['add', 'F0', 'G0']).__setitem__(3, '1'))
    nz = next((s, p) for s, p, shift in frame_records if shift)
    reject('missing payload translation', lambda b: next(e for e in b if e[0] == 'map' and (e[2], e[3]) == nz).append('omit_shift'))
    def cross_private(b):
        e = b.pop(first(b, 'map')); b.insert(first(b, 'begin') + 1, e)
    reject('cover map inside private body', cross_private)
    invoice = {'rank_one_children': counts['line'], 'rank_eight_children': counts['stage'],
               'native_rank_mass': counts['line'] + 8 * counts['stage'],
               'native_monomial_wrappers': 2 * (counts['line'] + counts['stage']),
               'full_cover_maps': counts['map'], 'unit_ADDs': counts['unit_ADD'],
               'quarter_ADDs': counts['quarter_ADD'], 'CLEARs': counts['clear'],
               'real_scalar_primitive_allowance': 8 * counts['unit_ADD'] + 12 * counts['quarter_ADD'] + 2 * counts['clear'],
               'owned_full_cover_outputs': 224, 'early_record_banks': 0,
               'peak_local_owned_scratch': 16, 'untouched_borrowed_current_fields': 224}
    need(invoice['native_rank_mass'] > 352 and invoice['full_cover_maps'] > 208, 'comparison scope')
    noncommuting = sum(product(routes[1][p], routes[2][p]) != product(routes[2][p], routes[1][p]) for p in range(112))
    need(noncommuting > 0, 'nonconstant/noncommuting chart evidence')
    operators = [[[[source, list(g), str(c)] for (source, g), c in sorted(row.items())] for row in bank] for bank in inv]
    result = {'status': 'PASS_QQ16_ZERO_RETENTION_COMPARISON', 'invoice': invoice, 'events': len(w),
              'trace': dict(counts), 'controls': controls, 'two_sided_formal_inverse': True,
              'output_operator_sha256': digest(canonical(operators)),
              'operator_terms': sum(len(row) for bank in inv for row in bank),
              'noncommuting_chart_pairs': noncommuting,
              'frame_maps': frame_records, 'native_factorizations': kernel_checks(labels),
              'independent_phase_character_checks': direct_map_checks(routes, frame_records),
              'comparison': {'predecessor_pr': 2540, 'predecessor_head': '630d557af5088f66b45c447969cee9576600e50b',
                             'native_rank_mass_delta': 3344, 'early_record_bank_delta': -16,
                             'native_child_delta': {'1': -112, '8': 432},
                             'moment_numerator_lower_bound_for_0_le_a_le_1': 320},
              'source_sha256': {p: digest(b) for p, b in raw.items()},
              'limits': 'Finite added local word. Native child kernels/hosting, physical banks/maps, precision, original F0/B1 native core replay and complete controller/supplier are inherited or open. No new kappa or optimum.'}
    return result, w


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true', help='create absent receipts, never overwrite')
    args = ap.parse_args(); result, w = compute()
    for name, obj in (('RESULT.json', result), ('WORD.json', w)):
        path = HERE / name
        if args.write:
            with path.open('x', encoding='utf-8', newline='\n') as stream:
                if name == 'WORD.json': stream.write('[\n' + ',\n'.join('  ' + json.dumps(e) for e in obj) + '\n]\n')
                else: json.dump(obj, stream, indent=2, sort_keys=True); stream.write('\n')
        else:
            need(canonical(json.loads(path.read_text(encoding='utf-8'))) == canonical(obj), 'receipt mismatch: ' + name)
    print(result['status'], json.dumps(result['invoice'], sort_keys=True), 'no_new_kappa')


if __name__ == '__main__':
    main()
