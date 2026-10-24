"""One prepared helper removes two paid jobs in the PR4610 backward word.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The source word is by Cao Yifan. The row convention and scalar allowance
follow the credited native work of Cinna Davis and zxv.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
PHASE = 'research/kappa-round3-warp-20261022/PHASE-VALIDATION.json.gz'
PAYLOAD = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
RELATION = {230: 1, 324: -1, 326: 1, 328: 1, 333: -1}
OLD_PAID = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}
NEW_PAID = dict(OLD_PAID)
NEW_PAID[1] -= 1
NEW_PAID[8] -= 1
OLD_HELPERS = {4: 28, 7: 7, 8: 47, 9: 326}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def encode(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encode(v) for v in x]
    return x


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def authenticate():
    pins = read(HERE / 'SOURCES.json')
    for row in pins['files']:
        if row['usage'] != 'input':
            continue
        p = ROOT
        for part in Path(row['path']).parts:
            p /= part
            need(not p.is_symlink(), 'No source aliases')
        raw = p.read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'Changed source: ' + row['path'])
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'Source Git blob')
    need(sha256(gzip.decompress((ROOT / SOURCE).read_bytes())).hexdigest() == PAYLOAD, 'Exact source payload')
    return pins


def span(basis):
    out = {0}
    for vector in basis:
        need(isinstance(vector, int) and 0 <= vector < 512, 'Binary frame coordinate')
        out |= {v ^ vector for v in tuple(out)}
    need(len(out) == 2 ** len(basis), 'Independent frame basis')
    return out


def add(dst, src, q):
    for k, v in tuple(src.items()):
        value = dst.get(k, Q(0)) + q * v
        if value:
            dst[k] = value
        else:
            dst.pop(k, None)


def allowance(g):
    if g[0] in ('clear', 'copy'):
        return 2
    q = Q(*g[3:]) if g[0] == 'add' else Q(*g[2:])
    n, d = abs(q.numerator), q.denominator
    need(n > 0 and d & (d - 1) == 0, 'Nonzero dyadic scalar')
    if g[0] == 'scale':
        need(n & (n - 1) == 0, 'Dyadic unit SCALE')
        return 2 * (abs(n.bit_length() - d.bit_length()) + int(q < 0))
    need(g[0] == 'add', 'Known scalar operation')
    return 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)


def construct(source):
    c = source['canonical']
    old = source['programs']['backward']
    need(old[11205] == ['climb', 'warp_retimed', 92, 310, 254, 4], 'Snapshot source event')
    need(old[11332] == ['center', 0, 0, 254, 8], 'Center source event')
    need(old[15584] == ['climb', 'warp_retimed', 92, 254, 1, 1], 'Zero source event')
    need(all(c['start'][h] == 0 and c['final'][h] == 1 for h in RELATION), 'Five cold full-ended helpers')
    word = [['scalar', ['clear', ['L', 230]], 0]]
    word += [['scalar', ['add', ['L', 230], ['L', h], -q, 1], 0]
             for h, q in RELATION.items() if h != 230]
    for i, event in enumerate(old):
        if i == 11332:
            word += [['scalar', ['clear', ['C', 0]], 254],
                     ['scalar', ['copy', ['C', 0], ['C', 1]], 254],
                     ['scalar', ['clear', ['C', 1]], 254]]
        elif i == 15584:
            word.append(['zero_retag', ['L', 92], 254, 1])
        else:
            word.append(deepcopy(event))
        if i == 11205:
            word += [['scalar', ['clear', ['C', 1]], 254],
                     ['scalar', ['copy', ['C', 1], ['L', 92]], 254]]
    word.append(['scalar', ['clear', ['L', 230]], 1])
    physical = deepcopy(c)
    physical.pop('local_profile')
    return {'schema': 'owned-helper-relation-word/1', 'canonical': physical,
            'paid_profiles': {'forward': OLD_PAID, 'backward': NEW_PAID},
            'owned': {'forward': [['C', 0]], 'backward': [['C', 0], ['C', 1], ['L', 230]]},
            'programs': {'forward': deepcopy(source['programs']['forward']), 'backward': word}}


def replay(c, program, backward, specialized):
    """Run every event on all independent entry columns and exact frames."""
    owned = {('C', 0)} | ({('C', 1), ('L', 230)} if specialized else set())
    roles = {('L', i) for i in range(632)} | owned
    rows = {r: {(r, ()): Q(1)} for r in roles}
    frames = {('L', i): f for i, f in enumerate(c['start'])}
    frames.update({r: None for r in owned if r[0] == 'C'})
    spaces = [span(b) for b in c['frames']]
    paid = Counter()
    cost, max_l1, denominator, zero_count = 0, Q(1), 1, 0
    for e in program:
        kind, touched = e[0], None
        if kind == 'scalar':
            g, frame = e[1:]
            dst = tuple(g[1]); touched = dst
            need(dst in rows and 0 <= frame < len(spaces), 'Declared scalar destination and frame')
            cost += allowance(g)
            if g[0] == 'clear':
                need(dst in owned, 'Only owned fields can be erased')
                rows[dst] = {}; frames[dst] = frame
            else:
                need(frames[dst] == frame, 'Exact scalar destination frame')
                if g[0] in ('add', 'copy'):
                    src = tuple(g[2])
                    need(src in rows and frames[src] == frame and dst != src, 'Exact scalar source frame')
                    if g[0] == 'copy':
                        need(dst in owned and not rows[dst], 'COPY into cleared owned storage')
                        rows[dst] = dict(rows[src])
                    else:
                        add(rows[dst], rows[src], Q(g[3], g[4]))
                else:
                    need(g[0] == 'scale', 'Known scalar operation')
                    rows[dst] = {k: Q(g[2], g[3]) * v for k, v in rows[dst].items()}
        elif kind == 'warp':
            _, role, op, old, new = e
            dst = tuple(role); touched = dst
            need(frames[dst] == old and 1 <= abs(op) <= len(c['warps']), 'Exact warp input')
            symbol = (1 if op > 0 else -1) * (abs(op) + (10**6 if backward else 0))
            rows[dst] = {(r, w[1:] if w and w[0] == -symbol else (symbol,) + w): q
                         for (r, w), q in rows[dst].items()}
            frames[dst] = new
        elif kind in ('climb', 'center'):
            if kind == 'climb':
                _, _, i, old, new, rank = e
                dst = ('L', i)
                need(spaces[old] < spaces[new], 'Ascending paid climb')
            else:
                _, i, old, new, rank = e
                dst = ('C', i)
                need(spaces[old] < spaces[new] or spaces[new] < spaces[old], 'Nested paid center')
            need(frames[dst] == old and rank == abs(len(c['frames'][new]) - len(c['frames'][old])), 'Exact paid rank and frame')
            frames[dst] = new; paid[rank] += 1
        elif kind == 'zero_retag':
            _, role, old, new = e
            dst = tuple(role)
            need(specialized and backward and dst == ('L', 92), 'Declared zero identity')
            need(frames[dst] == old and not rows[dst], 'Zero identity requires an identically zero full row')
            need((old, new) == (254, 1), 'Declared zero frame change')
            frames[dst] = new; zero_count += 1
        else:
            need(kind in ('phase', 'adapter'), 'Known inert source marker')
        if touched is not None:
            max_l1 = max(max_l1, sum(map(abs, rows[touched].values()), Q(0)))
            denominator = max(denominator, max((q.denominator for q in rows[touched].values()), default=1))
    need([frames['L', i] for i in range(632)] == c['final'], 'Every final native frame')
    for i in range(632):
        r = ('L', i)
        if r in owned:
            continue
        expected = {(r, ()): Q(1)}
        if i < 112 if backward else 112 <= i < 224:
            expected[(('L', i + 112 if backward else i - 112), ())] = Q(-1 if backward else 1)
        need(rows[r] == expected, 'Every independent main/helper endpoint: ' + str(i))
    need(all(not rows[r] for r in owned), 'Every owned entry column is erased at return')
    need(zero_count == int(specialized), 'Exactly one checked zero identity')
    helpers = Counter()
    for i in range(224, 632):
        if ('L', i) in owned:
            continue
        a, b = c['start'][i], c['final'][i]
        need(spaces[a] < spaces[b], 'Strict independent productive helper')
        helpers[len(c['frames'][b]) - len(c['frames'][a])] += 1
    return {'paid': dict(sorted(paid.items())), 'helpers': dict(sorted(helpers.items())),
            'independent_persistent_columns': 631 if specialized else 632,
            'independent_owned_entry_columns': len(owned), 'owned_outputs_zero': True,
            'real_scalar_allowance': cost, 'max_formal_prefix_l1': str(max_l1),
            'max_denominator': denominator, 'zero_identities': zero_count}


def independent_source_identities(source):
    """Use the predecessor row engine on the unrestricted original word."""
    v = load('research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py', 'owned_relation_source_rows')
    rows = {('L', i): v.identity(('L', i)) for i in range(632)}
    rows['C', 0] = v.identity(('C', 0))
    delta = {(('L', i), ()): Q(q) for i, q in RELATION.items()}
    saved = None
    for index, e in enumerate(source['programs']['backward']):
        if e[0] == 'scalar':
            g = e[1]; dst = tuple(g[1])
            if g[0] == 'clear': rows[dst] = {}
            elif g[0] == 'copy': rows[dst] = dict(rows[tuple(g[2])])
            elif g[0] == 'scale': rows[dst] = {k: Q(g[2], g[3]) * a for k, a in rows[dst].items()}
            else: v.add(rows[dst], rows[tuple(g[2])], Q(g[3], g[4]))
        elif e[0] == 'warp':
            dst = tuple(e[1]); rows[dst] = v.warp(rows[dst], e[2], True)
        if index == 11205: saved = dict(rows['L', 92])
        if index == 11332:
            diff = dict(rows['C', 0]); v.add(diff, saved, -1)
            need(diff == {k: q / 4 for k, q in delta.items()}, 'Independent exact center minus snapshot = Delta/4')
        if index == 15584:
            need(rows['L', 92] == {k: -q / 4 for k, q in delta.items()}, 'Independent exact zero-site row = -Delta/4')
    need(all(rows['L', i] == v.expected(('L', i), [], True, False) for i in range(632)), 'Independent unrestricted source endpoints')
    return {'source_event_indices_are_zero_based': True, 'snapshot_after': 11205,
            'center_replaced': 11332, 'zero_identity_at': 15584,
            'snapshot_terms_before_substitution': len(saved), 'copy_coefficient': '1',
            'center_minus_snapshot': 'Delta/4', 'zero_site_row': '-Delta/4', 'relation': RELATION}


def phase_inheritance(source, candidate):
    receipt = read(ROOT / PHASE)
    need(receipt['status'] == 'PASS_JOINT_HELPER_MAPS_ALL_ACTUAL_ABSOLUTE_PHASES' and
         receipt['actual_word_canonical_sha256'] == PAYLOAD, 'Authenticated source absolute-phase receipt')
    physical = deepcopy(source['canonical']); physical.pop('local_profile')
    need(candidate['canonical'] == physical, 'Every frame, native map and main adapter unchanged')
    for direction, program in candidate['programs'].items():
        old = source['programs'][direction]
        for kind in ('warp', 'adapter', 'phase'):
            need([e for e in program if e[0] == kind] == [e for e in old if e[0] == kind], 'Exact inherited ' + kind + ' sequence')
        old_paid = Counter(tuple(e) for e in old if e[0] in ('climb', 'center'))
        new_paid = Counter(tuple(e) for e in program if e[0] in ('climb', 'center'))
        expected = Counter() if direction == 'forward' else Counter(tuple(old[i]) for i in (11332, 15584))
        need(old_paid - new_paid == expected and not new_paid - old_paid, 'Only the two proved jobs are removed')
    return {'new_gaussian_operators': 0, 'new_native_maps': 0,
            'all_retained_paid_events_and_warps_from_source': True,
            'absolute_phase_receipt_reused': PHASE,
            'source_amplitudes_and_phase_lowering_freshly_replayed': False,
            'new_operations': 'Same-frame COPY, owned CLEAR/ADD, and physical identity on a proved zero row.'}


def controls(c, candidate):
    controls = {}
    base = candidate['programs']['backward']
    variants = {}
    bad = deepcopy(base); bad[1][1][3] *= -1; variants['wrong_relation_sign'] = bad
    variants['missing_owned_input_clear'] = deepcopy(base[1:])
    bad = deepcopy(base)
    next(e for e in bad if e[0] == 'scalar' and e[1][:2] == ['copy', ['C', 1]])[1][2] = ['L', 63]
    variants['wrong_snapshot_source'] = bad
    bad = deepcopy(base); next(e for e in bad if e[0] == 'zero_retag')[2] = 0
    variants['wrong_zero_input_frame'] = bad
    bad = deepcopy(base); next(e for e in bad if e[0] == 'climb')[5] += 1
    variants['under_or_overstated_paid_rank'] = bad
    bad = deepcopy(base)
    next(e for e in bad if e[0] == 'scalar' and e[1][:2] == ['copy', ['C', 0]])[2] = 0
    variants['wrong_copy_gauge'] = bad
    variants['uncleared_owned_output'] = deepcopy(base[:-1])
    for name, program in variants.items():
        try:
            replay(c, program, True, True)
        except ValueError as err:
            controls[name] = str(err)
        else:
            raise ValueError('Control accepted: ' + name)
    return controls
