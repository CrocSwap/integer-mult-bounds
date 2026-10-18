"""Exact eight-stream Fourier test, including actual helper-hosting chronology.

Gaussian integers are pairs of Python integers. No floating-point arithmetic.
The local invocation contract is the retained one in INHERITED-COMPLEX-GEOMETRY;
this checks its composition, not the internal native/circuit implementation.
"""
import collections
import copy
import gzip
import tarfile
import core as C

ZERO = (0, 0)
ONE = (1, 0)


def rotate(z, exponent):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[exponent % 4]


def template():
    with tarfile.open(C.ROOT/C.REPLAY) as archive:
        raw = archive.extractfile('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz').read()
    return C.decode(gzip.decompress(raw))


def prepare(t, phases, owners, replica=0, port=0):
    recipe = next(r for r in phases['recipes'] if r['port'] == port)
    local = {r['stage']: r for r in t['recipe'] if r['kind'] == 'local'}
    helpers = collections.defaultdict(list)
    for r in owners:
        if (r['owner_replica'], r['port']) != (replica, port):
            continue
        axes = recipe['idle_children'][r['child']]['orthogonal_axes']
        axes = list(map(int, axes[r['offset']:r['offset']+r['width']]))
        C.need(len(axes) == r['width'], 'hosted slice length')
        stream, rem = divmod(r['family']-replica*8*112, 112)
        C.need(rem == port and 0 <= stream < 8, 'hosted family mapping')
        helpers[r['stage'], r['replica']].append((stream, axes))
    events = []
    for e in t['execution_schedule']:
        if e['kind'] == 'local_cover_sweep':
            events.append(('helpers', helpers[e['stage'], e['replica']]))
        if e.get('replica') == replica:
            events.append(('data', e))
    return recipe, local, events


def matrix(prepared, frames, u, replica=0, port=0):
    """Eight physical streams at cover g=I and Fourier character u."""
    recipe, local, events = prepared
    rows = {r['child']: r for r in frames if (r['replica'], r['port']) == (replica, port)}
    m = [[ONE if i == j else ZERO for j in range(8)] for i in range(8)]
    uq = C.dot(u, int(recipe['q']))

    def phase(stream, exponent):
        m[stream] = [rotate(z, exponent) for z in m[stream]]

    def shear(dst, src, coefficient):
        m[dst] = [(a+coefficient*c, b+coefficient*d)
                  for (a, b), (c, d) in zip(m[dst], m[src])]

    def frame(level, side):
        if level == -1:
            return (1-side)*uq
        return (u & ((1 << (9+8*level))-1)).bit_count()-side*uq

    for kind, e in events:
        if kind == 'helpers':
            for stream, axes in e:
                phase(stream, sum(C.dot(u, v) for v in axes))
            continue
        kind = e['kind']
        if kind == 'local_cover_sweep':
            stage = e['stage']
            op = local[stage]
            x, y = 2*op['pair'], 2*op['pair']+1
            # Canonical input/output frames include the stored stage adapters.
            for side, stream in enumerate((x, y)):
                phase(stream, -frame(stage-1, side))
            if op['reverse']:
                shear(x, y, -1)
            else:
                shear(y, x, 1)
            for side, stream in enumerate((x, y)):
                phase(stream, frame(stage, side))
        elif kind == 'idle_cover_sweep':
            for side, child in enumerate(e['child_indices']):
                row = rows.get(child)
                axes = [] if row is None else list(map(int, row['orthogonal_axes']))
                if row is not None:
                    C.need(row['family'] == replica*8*112+(2*e['pair']+side)*112+port,
                           'idle family mapping')
                exponent = sum(C.dot(u, v) for v in axes)
                exponent += 2*C.dot(u, int(recipe['idle_children'][child]['translation_after']))
                phase(2*e['pair']+side, exponent)
        elif kind == 'bridge':
            dst, src, c = e['dst'], e['src'], e['coefficient']
            shear(2*dst, 2*src, c)
            shear(2*src+1, 2*dst+1, -c)
        elif kind == 'terminal_Y_translations':
            for pair in e['pairs']:
                phase(2*pair+1, 2*C.dot(u, int(recipe['terminal_Y_translation'])))
        elif kind == 'terminal':
            for pair in range(e['pairs']):
                m[2*pair], m[2*pair+1] = m[2*pair+1], [rotate(z, 2) for z in m[2*pair]]
        else:
            raise ValueError('unhandled data event: '+kind)
    # No bank padding remains on the selected word. At g=I, delta(g)=0.
    return m


def target(u):
    return [[rotate(ONE, u.bit_count()) if i == j else ZERO for j in range(8)] for i in range(8)]


def require_equal(prepared, before, after, u):
    a, b = matrix(prepared, before, u), matrix(prepared, after, u)
    C.need(a == b, 'physical stream operator differs')


def report(old, new, phases, owners):
    t = template()
    prepared = prepare(t, phases, owners)
    # The entire emitted replica-0 chronology is used, plus all local sweeps
    # on other replicas that host one of its data families at this port.
    tests = [0]+[1 << i for i in range(73)]+[(1 << 73)-1]
    tests += [(1 << i) | (1 << (i+1)) for i in range(72)]
    for u in tests:
        C.need(matrix(prepared, old, u) == target(u), 'baseline stream test failed')
    u = 32
    a, b = matrix(prepared, old, u), matrix(prepared, new, u)
    C.need(a == target(u) and b != a, 'missing optimized-assignment counterexample')
    # A smaller witness isolates the rule itself: move just e5 from X3's
    # child 8 to X0's child 12. Both children are unhosted and owner-free.
    simple = copy.deepcopy(old)
    bykey = {C.label(r): r for r in simple}
    src, dst = bykey[0, 0, 8], bykey[0, 0, 12]
    C.need(src['hosted'] == dst['hosted'] == 0, 'counterexample child hosted')
    src['orthogonal_axes'].remove(u)
    src['rank'] -= 1
    dst['orthogonal_axes'].append(u)
    dst['rank'] += 1
    structural = C.check_assignment(old, simple, phases, owners)
    c = matrix(prepared, simple, u)
    C.need(c != a, 'missing one-axis counterexample')
    for candidate in (new, simple):
        try:
            require_equal(prepared, old, candidate, u)
        except ValueError as error:
            C.need(str(error) == 'physical stream operator differs', 'unexpected rejection')
        else:
            raise ValueError('semantic control accepted')
    oldrows = [r for r in old if r['replica'] == r['port'] == 0]
    newrows = [r for r in new if r['replica'] == r['port'] == 0]
    C.need(C.legacy_flattened_operator(oldrows, prepared[0]) ==
           C.legacy_flattened_operator(newrows, prepared[0]), 'legacy check no longer accepts witness')
    differences = [[i, j, list(a[i][j]), list(b[i][j])] for i in range(8) for j in range(8) if a[i][j] != b[i][j]]
    return dict(status='PASS_EXACT_PHYSICAL_STREAM_OBSTRUCTION', admitted=False,
                replica=0, port=0, q=prepared[0]['q'], cover='identity', fourier_character=u,
                stream_order=['X0', 'Y0', 'X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3'],
                gaussian_integer_format='[real, imaginary]', baseline_modes=len(tests),
                hosted_occurrences=sum(len(e) for kind, e in prepared[2] if kind == 'helpers'),
                schedule_sha256=C.digest(t['execution_schedule']), baseline=a,
                optimized=b, differences=differences, single_move=c,
                single_move_definition=dict(axis=32, source_child=8, destination_child=12,
                    source_family=672, destination_family=0, ranks=[47,49]),
                single_move_structural_check=structural, legacy_flattened_accepts=True,
                semantic_controls_rejected=2)
