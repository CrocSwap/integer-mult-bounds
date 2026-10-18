"""A sharp changed observation contract at the actual QQ16 post-B1 cut.

Reuses the pinned PR2456 operator algebra/source parser with credit. The new
composition, free-observation inverse, kernel and live-sum macro are below.
"""
from fractions import Fraction as Q
from pathlib import Path
from collections import Counter
import hashlib
import importlib.util
import io
import json
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load():
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    raw = {}
    for item in manifest['files'] + manifest['snapshots']:
        if item.get('usage') == 'provenance':
            continue
        path = (ROOT if item.get('usage') == 'input' else HERE) / item['path']
        data = path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == item['sha256'], 'source SHA256 ' + item['path'])
        need(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
             == item['git_blob'], 'source Git blob')
        raw[item['path']] = data
    spec = importlib.util.spec_from_file_location('qq16_prior_operator_audit', HERE / 'vendor/operator_audit.py')
    module = importlib.util.module_from_spec(spec)
    # Execute exactly the already authenticated bytes; no second source read.
    exec(compile(raw['vendor/operator_audit.py'], spec.origin, 'exec', optimize=0), module.__dict__)
    matrix, routes, native, bindings = module.parse_sources(raw)
    # Reuse only the credited routed primitive/F0 methods. The old constructor
    # inverts PR2443's unread minor, which this changed contract does not need.
    model = module.Model.__new__(module.Model)
    model.R, model.routes, model.native = matrix, routes, native
    need(all(sum(matrix[i][p] * matrix[j][p] for p in ports) == scale * int(i == j)
             for ports, scale in ((module.A, 4), (module.T, 4), (module.U, 48))
             for i in range(8) for j in range(8)), 'actual selected and ordinary Grams')
    return module, model, raw, bindings


def pair_add(o, x, y, ports):
    return {p: o.combine((1, x[p]), (1, y[p])) for p in ports}


def backward(o, m, x, y):
    """All six actual CONSERVED-QQ16 (1) blocks, in ordered charts s=1,t=2."""
    z = m.query(y, o.U + o.T, 2)
    e = m.inject(z, o.A, 2)
    u = dict(y) | {p: o.combine((1, y[p]), (1, e[p])) for p in o.A}
    a, b = m.query(x, o.T, 1), m.query(u, range(112), 1)
    ka = m.inject(a, o.U, 1)
    bt11 = m.inject([o.combine((1, bi), (11, ai)) for bi, ai in zip(b, a)], o.T, 1)
    bt12 = m.inject([o.combine((1, bi), (12, ai)) for bi, ai in zip(b, a)], o.T, 1)
    yy = ({p: o.combine((1, y[p]), (1, ka[p])) for p in o.U}
          | {p: u[p] for p in o.A}
          | {p: o.combine((1, u[p]), (-1, bt11[p])) for p in o.T})
    xx = ({p: o.combine((1, x[p]), (-1, y[p])) for p in o.U}
          | {p: o.combine((1, x[p]), (1, y[p]), (-1, u[p])) for p in o.A}
          | bt12)
    need(pair_add(o, xx, yy, o.A + o.T) == pair_add(o, x, y, o.A + o.T),
         'all sixteen actual selected pair sums conserved')
    return xx, yy


def observe(o, m, original):
    x1, y1 = m.forward(*original)
    x2, y2 = backward(o, m, x1, y1)
    # Record only X1 selected. Every other observation is formed from actual
    # current X2/Y2 fields at the immediate cut, before the next bridge.
    return ({p: x1[p] for p in o.A + o.T}, {p: x2[p] for p in o.U},
            {p: y2[p] for p in o.U}, pair_add(o, x2, y2, o.A + o.T))


def decode(o, m, observed, fault=None):
    early, c, z, sums = observed
    wrong_route = fault == 'physical_alignment_for_logical_route'
    h = m.query(early, o.T, 1, wrong_route)
    kh = m.inject(h, o.U, 1, wrong_route)
    x1 = dict(early) | {p: o.combine((1, c[p]), (1, z[p]),
                         (0 if fault == 'omit_driver' else 1 if fault == 'wrong_driver_sign' else -1, kh[p]))
                         for p in o.U}
    f, old_t = m.query(x1, o.T), m.query(x1, o.A)
    kf = m.inject(f, o.U)
    x = {p: o.combine((1, x1[p]), (0 if fault == 'omit_forward_correction' else 1, kf[p]))
         for p in o.U}
    x.update(m.inject(old_t, o.T))
    rest = [o.combine((1, fi), (-1, oi), (-1, ti))
            for fi, oi, ti in zip(f, m.query(x, o.U), old_t)]
    x.update(m.inject(rest, o.A))
    y = {p: o.combine((1 if fault == 'wrong_original_Y_sign' else -1, c[p])) for p in o.U}
    y.update({p: o.combine((1, sums[p]), (-1, x[p])) for p in o.A + o.T})
    return x, y


def free(o):
    result, index = [], 0
    for ports in (o.A + o.T, o.U, o.U, o.A + o.T):
        result.append({p: o.variable(index + j) for j, p in enumerate(ports)})
        index += len(ports)
    need(index == 224, '16 early plus 208 live arrays')
    return tuple(result)


def serial_rows(o, rows):
    """Canonical complete operator content, independent of interned map IDs."""
    out = []
    for block in rows:
        for p, row in sorted(block.items()):
            terms = []
            for (variable, index), coefficient in row.items():
                matrix, shift = o.MAPS[index]
                terms.append((variable, matrix, shift, str(coefficient)))
            out.append((p, sorted(terms)))
    return json.dumps(out, separators=(',', ':')).encode()


def live_sum_check(o, raw):
    """Exact phase/content read of current selected sums with source restoration.

    Source endpoint X=F_U1, Y=F_U1 C_q^-1. The C_q normalization and inverse
    use the credited positive child / monomial recipes. The ordinary-port
    normalization/sum/restoration pattern already appears in PR2492; its use
    here implements the changed selected-output contract. No cover map is needed.
    """
    member = 't16/global/base/work/complex-nine-native/DATA-PHASES.json'
    with tarfile.open(fileobj=io.BytesIO(raw['research/community-frontier1042-audit/selected-replay.tar.gz']), mode='r:gz') as ar:
        data = ar.extractfile(member).read()
    need(hashlib.sha256(data).hexdigest() == o.MEMBERS[member], 'phase source pin')
    records = json.loads(data)['recipes']
    words, columns, normals = [], 0, {}
    for p in o.A + o.T:
        q = records[p]['q']
        normals[p] = q
        need(records[p]['port'] == p and 0 < q < 512, 'selected native line binding')
        words += [['clear', p], ['line_Y', p, 1], ['add_X', p], ['add_Y', p], ['line_Y', p, -1]]
        pivot = (q & -q).bit_length() - 1
        basis = (q,) + tuple(1 << j for j in range(9) if j != pivot)
        inverses = {o.act(basis, x): x for x in range(512)}
        need(len(inverses) == 512, 'invertible native monomial basis')
        for x in range(512):
            for sign in (1, -1):
                middle = inverses[x]
                offset = 0 if sign == 1 else q
                actual = {o.act(basis, middle) ^ offset: (1, 1),
                          o.act(basis, middle ^ 1) ^ offset: (1, -1)}
                expected = {x: (1, sign), x ^ q: (1, -sign)}
                need(actual == expected, 'exact signed Gaussian kernel column, denominator two')
                columns += 1
        need(any((q & w).bit_count() & 1 for w in range(512)), 'nonidentity native line')
    need(len(words) == 80, 'complete sum-read event count')

    def replay(program):
        for w in range(512):
            phase = {p: -((normals[p] & w).bit_count() & 1) for p in normals}
            output = {p: [0, 0, 1] for p in normals}  # independent owned output dirt
            for event in program:
                op, p = event[:2]
                if op == 'clear':
                    output[p] = [0, 0, 0]
                elif op == 'line_Y':
                    phase[p] += event[2] * ((normals[p] & w).bit_count() & 1)
                elif op == 'add_X':
                    output[p][0] += 1
                elif op == 'add_Y':
                    need(phase[p] % 4 == 0, 'common physical chart for selected sum')
                    output[p][1] += 1
                else:
                    raise ValueError('unknown native sum event')
            for p, q in normals.items():
                need(output[p] == [1, 1, 0], 'correct sum independent of owned output dirt')
                need(phase[p] % 4 == -((q & w).bit_count() & 1) % 4, 'physical Y restoration')

    replay(words)
    faults = {
        'missing_normalization': [e for e in words if not(e[0] == 'line_Y' and e[2] == 1)],
        'missing_restoration': [e for e in words if not(e[0] == 'line_Y' and e[2] == -1)],
        'missing_output_clear': [e for e in words if e[0] != 'clear'],
        'missing_X_read': [e for e in words if e[0] != 'add_X'],
        'wrong_normalization_sign': [e[:2] + [-1] if e[0] == 'line_Y' and e[2] == 1 else e for e in words],
    }
    rejected = []
    for name, program in faults.items():
        try:
            replay(program)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('ineffective native-sum fault: ' + name)
    return {'program': words, 'selected_ports': list(o.A + o.T), 'events': 80,
            'positive_rank_one_children': 32, 'monomial_wrappers': 64,
            'signed_ADDs': 32, 'CLEARs': 16, 'new_owned_outputs': 16,
            'cover_maps': 0, 'native_signed_columns': columns,
            'native_macro_controls': rejected,
            'primitive_scalar_allowance': 2 * (32 * 4 + 16)}


def run():
    o, m, raw, bindings = load()
    original = o.independent_pair()
    observed = observe(o, m, original)
    need(decode(o, m, observed) == original, 'reconstruction of all 224 arbitrary input arrays')
    arbitrary = free(o)
    need(observe(o, m, decode(o, m, arbitrary)) == arbitrary,
         'arbitrary 224-coordinate record/live data admits a two-sided inverse')
    # The early coordinates parametrize the ENTIRE kernel of the live read.
    zero_live = (arbitrary[0], {p: {} for p in o.U}, {p: {} for p in o.U},
                 {p: {} for p in o.A + o.T})
    hidden = decode(o, m, zero_live)
    need(observe(o, m, hidden) == zero_live, 'sixteen arbitrary-array kernel coordinates')
    controls = {}
    for fault in ('omit_driver', 'wrong_driver_sign', 'omit_forward_correction',
                  'wrong_original_Y_sign', 'physical_alignment_for_logical_route'):
        changed = decode(o, m, observed, fault)
        residual = o.first_residual(original, changed)
        need(residual is not None, 'effective decoder failure ' + fault)
        controls[fault] = residual
        if fault == 'physical_alignment_for_logical_route':
            need(all(o.forget_payload(changed[b][p]) == original[b][p] for b in range(2) for p in range(112)),
                 'wrong physical route invisible on payload-constant data')
    # Every one of the sixteen early arrays is independently indispensable
    # to THIS attaining record; no uniqueness or port-set optimality is claimed.
    omitted = []
    for p in o.A + o.T:
        singleton = ({v: (o.variable(0) if v == p else {}) for v in o.A + o.T}, *zero_live[1:])
        nonzero = decode(o, m, singleton)
        need(any(row for block in nonzero for row in block.values()) and observe(o, m, nonzero) == singleton,
             'nonzero invisible input for missing early coordinate')
        omitted.append(p)
    # Add arbitrary unrelated-bank inputs: the pinned first two events touch
    # pair0 only. No downstream event or final-cut availability is extrapolated.
    macro = live_sum_check(o, raw)
    return {'status': 'PASS_QQ16_SIXTEEN_RECORD_CUT', 'formal_original_arrays': 224,
            'retained_early_arrays': 16, 'live_observation_arrays': 208,
            'live_current_fields_read': 224, 'live_operator_rank_per_array_dimension': 208,
            'unobserved_kernel_rank_per_array_dimension': 16,
            'first_cut': 'complete F0', 'decode_cut': 'complete B_1_2 before next bridge',
            'observation_blocks': ['X1_A/T retained', 'X2_U current', 'Y2_U current', '(X2+Y2)_A/T current'],
            'identities': ['decode observe = I_224', 'observe decode = I_224',
                           'kernel(live) is isomorphic to sixteen arbitrary array coordinates'],
            'kernel_operator_sha256': hashlib.sha256(serial_rows(o, hidden)).hexdigest(),
            'observation_operator_sha256': hashlib.sha256(serial_rows(o, observed)).hexdigest(),
            'source_routes': bindings, 'missing_record_port_witnesses': omitted,
            'negative_controls': controls, 'local_selected_sum_read': macro,
            'scope': 'Sharp linear retention for this changed immediate-cut contract, with a local sum-read macro; no full physical decoder, budget, supplier or new kappa.'}
