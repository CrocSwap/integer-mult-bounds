"""Check a port-routed query cache on the four actual B-to-F windows.

The input logger comes from the circuit-interface and history-encoding
lanes. The route convention comes from the selected supplier. The
residual-syndrome lane supplied the persistent Y-shadow cache history.
Research used OpenAI Codex under the user's direction.
"""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import io
import json
import subprocess
import tarfile


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
ROOT = HERE.parents[4]
BASE = 'bce54fb3f895cbe5cd4c0eb477c3afeed100190f'
ARCHIVE = 'research/community-frontier1042-audit/selected-replay.tar.gz'
PHASES = 't16/global/base/work/complex-nine-native/DATA-PHASES.json'
TEMPLATE = 't16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz'
PLAN = 'research/complex-t16-rare-pattern-exchanges/data/PLAN.json'
PINS = {
    ARCHIVE: '22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754',
    PHASES: 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa',
    TEMPLATE: 'a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518',
    PLAN: '7bd786ba8e66408f02aa9ef446eaf20c1bfe981ea2e4dd1e5a929f0aa7767bc0',
    'word': '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219',
    'R': '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3',
    'logger': 'ac824c98819dc1defef14788bf5215f72323f49a49f1f8bec4ee373558eba82e',
    'borrowed': '6b88cf885e22ef745eee74db04adc7feadfcc63a8248e8873b1a4caf76b21096',
    'algebra': 'a397a9fe8cd9933106aab2f01edee0e16b54cc1c1cede78b6dac90844d5fdbcf',
}
T_PORTS = [21, 37, 47, 76, 81, 87, 92, 110]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def pinned(raw, key):
    need(sha256(raw).hexdigest() == PINS[key], 'Source pin: '+key)
    return raw


def local(path, key, compressed=False, pin_compressed=False):
    raw = path.read_bytes()
    if pin_compressed:
        pinned(raw, key)
    if compressed:
        raw = gzip.decompress(raw)
    if not pin_compressed:
        pinned(raw, key)
    return json.loads(raw)


def git_bytes(path):
    raw = subprocess.run(['git', 'show', BASE+':'+path],
                         cwd=ROOT/'worktrees/k5-centre-sharing',
                         check=True, capture_output=True).stdout
    return pinned(raw, path)


def dot(x, y):
    return (x & y).bit_count() & 1


def port_basis(q):
    # This is the chart fixed in the selected source, with q first.
    j = next(i for i in range(9) if not (q >> i) & 1)
    v = q ^ (1 << j)
    out = []
    for i in range(9):
        x = 1 << i
        if j and (x & 1) != ((x >> j) & 1):
            x ^= 1 | (1 << j)
        out.append(x ^ (v if dot(v, x) else 0))
    need(out[0] == q and all(dot(a, b) == (i == j)
         for i, a in enumerate(out) for j, b in enumerate(out)), 'Orthogonal port chart')
    return out


def route(x, stage, basis):
    if not stage:
        return x
    offset = 9+8*(stage-1)
    out = x & ~(511 | (255 << offset))
    if dot(x, basis[0]):
        out ^= basis[0]
    for k, b in enumerate(basis[1:]):
        if dot(x, b):
            out ^= 1 << (offset+k)
        if (x >> (offset+k)) & 1:
            out ^= b
    return out


def form(axes=(), translation=0):
    """Return the full Z4 Fourier phase, including its linear sign."""
    linear = [2*((translation >> i) & 1) for i in range(73)]
    quadratic = [0]*73
    for axis, coefficient in axes:
        for i in range(73):
            if not (axis >> i) & 1:
                continue
            linear[i] = (linear[i]+coefficient) % 4
            if coefficient & 1:
                quadratic[i] ^= axis & ~((1 << (i+1))-1)
    return linear, quadratic


def translation_between(left, right):
    a, aq = form(left)
    b, bq = form(right)
    need(aq == bq and all((u-v) % 2 == 0 for u, v in zip(a, b)), 'Pure translation defect')
    return sum(1 << i for i, (u, v) in enumerate(zip(a, b)) if (u-v) % 4 == 2)


def rational(rows):
    return [{int(j): Q(q) for j, q in row.items()} for row in rows]


def scalar_add(target, source, q):
    return ['scalar', ['add', target, source, q.numerator, q.denominator], 0]


def frames(events, word):
    state, profile = word['start'][:]+[0]*8, Counter()
    for event in events:
        kind = event[0]
        if kind == 'input_target_line':
            _, p, q, sign, before, after, rank = event
            need(q == word['ports'][p] and rank == 1 and state[p] == before, 'Input line frame')
            need((sign, before, after) in ((-1, word['start'][p], 0), (1, 0, word['start'][p])), 'Input line sign')
            state[p] = after
            profile[1] += 1
        elif kind == 'climb':
            _, _, p, before, after, rank = event
            need(state[p] == before, 'Retained native entry')
            state[p] = after
            profile[rank] += 1
        elif kind == 'scalar':
            gate, frame = event[1:]
            need(gate[0] in ('add', 'scale'), 'No erased borrowed value')
            target = gate[1][1]+(704 if gate[1][0] == 'C' else 0)
            need(state[target] == frame, 'Scalar target frame')
            if gate[0] == 'add':
                source = gate[2][1]+(704 if gate[2][0] == 'C' else 0)
                need(source != target and state[source] == frame, 'Scalar source frame')
        else:
            need(kind in ('phase', 'adapter', 'residual_adapter'), 'Known retained event')
    need(state == word['final']+[0]*8, 'All data and borrowed-C endpoints')
    return dict(sorted(profile.items()))


def main():
    path = LANES/'history-encoding/check_backward_cut_source.py'
    pinned(path.read_bytes(), 'algebra')
    spec = importlib.util.spec_from_file_location('carried_alias_algebra', path)
    algebra = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(algebra)
    word = local(ROOT/'work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz', 'word', True, True)
    R = rational(local(LANES/'circuit-interface/INTERFACE.json', 'R')['R'])
    module = LANES/'circuit-interface/borrowed-centres'
    logger = local(module/'INPUT-SOURCE-FAMILY-PROGRAMS.json.gz', 'logger', True)
    borrowed = local(module/'BORROWED-CENTRES-PROGRAMS.json.gz', 'borrowed', True)['programs']
    need(logger['T_ports'] == T_PORTS, 'Actual log ports')
    K = [{k: row[p]/4 for k, row in enumerate(R) if p in row} for p in range(112)]
    RT = [{k: row[p] for k, p in enumerate(T_PORTS) if p in row} for row in R]
    RT_inverse = [K[p] for p in T_PORTS]
    need([algebra.combine(row, RT) for row in RT_inverse] == [{k: Q(1)} for k in range(8)], 'Exact selected inverse')
    query = [algebra.combine(row, R) for row in RT_inverse]
    capture = [scalar_add(['C', k], ['L', 112+p], q)
               for k, row in enumerate(query) for p, q in sorted(row.items())]
    unload = [scalar_add(['C', k], ['L', 112+p], Q(-1)) for k, p in enumerate(T_PORTS)]
    need(len(capture) == 424 and algebra.scalar_bound(capture) == 4224, 'Normalized capture invoice')
    need(len(unload) == 8 and algebra.scalar_bound(unload) == 64, 'Alias unload invoice')
    identity = [{i: Q(1)} for i in range(712)]
    before = algebra.replay(capture, identity)
    after = algebra.replay(logger['programs']['logger'], before)
    base_after = algebra.replay(logger['programs']['logger'], identity)
    need(after[:704] == base_after[:704], 'Capture has no data or helper effect')
    for k, p in enumerate(T_PORTS):
        want = {112+j: q for j, q in query[k].items()}
        need(after[112+p] == want, 'Logged selected output is the captured query')
        want[704+k] = Q(1)
        need(after[704+k] == want, 'All arbitrary borrowed cache inputs are retained')
    captured_profile = frames(capture+logger['programs']['logger'], word)
    need(sum(r*n for r, n in captured_profile.items()) == 5538, 'Captured logger native mass')
    # The next call starts after both aliases have the same native map.
    alias_input = [row.copy() for row in identity]
    for k, p in enumerate(T_PORTS):
        alias_input[704+k][112+p] = Q(1)
    need(algebra.replay(unload, alias_input) == identity, 'Alias unload on all712 input columns')
    need(algebra.replay(unload+borrowed['forward'], alias_input) ==
         algebra.replay(borrowed['forward'], identity), 'The complete following forward word')
    frames(unload+borrowed['forward'], word)
    baseline_residual = []
    for k, p in enumerate(T_PORTS):
        row = {p: Q(1)}
        algebra.add(row, query[k], Q(-1))
        baseline_residual.append(row)
    witness = next((k, p, q) for k, row in enumerate(baseline_residual) for p, q in sorted(row.items()))
    need(witness[2] != 0, 'An old selected baseline does not have alias closure')

    archive = git_bytes(ARCHIVE)
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as stream:
        phase = json.loads(pinned(stream.extractfile(PHASES).read(), PHASES))
        template = json.loads(gzip.decompress(pinned(stream.extractfile(TEMPLATE).read(), TEMPLATE)))
    plan = json.loads(git_bytes(PLAN))
    need((plan['K'], plan['T'], plan['M'], plan['L'], plan['live']) == (4, 16, 73, 9, 14336), 'Selected supplier dimensions')
    need(Counter(c['stage'] for c in plan['provider_calls']) == {s: 16 for s in range(9)}, 'Selected replica schedule')
    schedule = template['execution_schedule']
    windows = []
    for stage in (1, 3, 5, 7):
        start = next(i for i, e in enumerate(schedule) if e.get('kind') == 'local_cover_sweep' and e.get('stage') == stage)
        end = next(i for i, e in enumerate(schedule) if e.get('kind') == 'local_cover_sweep' and e.get('stage') == stage+1)
        pair = (stage-1)//2
        between = schedule[start+1:end]
        for event in between:
            if event['kind'] == 'bridge':
                need(event['dst'] == pair and event['src'] == pair+1, 'The bridge leaves the active Y source unchanged')
            elif event['kind'] == 'idle_cover_sweep':
                need(event['pair'] != pair, 'No idle transform touches the active Y source')
            else:
                need(False, 'An unaccounted event lies in the cache window')
        windows.append({'backward_stage': stage, 'forward_stage': stage+1,
                        'pair': pair, 'intervening_events': between})
    need(template['route_semantics']['data'].startswith('physical cover class d*rho(stage,port)'), 'Actual data route convention')

    histories, phase_count, eigenvalue_count = [], 0, 0
    for k, p in enumerate(T_PORTS):
        item, q = phase['recipes'][p], word['ports'][p]
        need(item['q'] == q, 'Phase recipe port label')
        basis = port_basis(q)
        units = [1 << i for i in range(9)]
        eta = translation_between([(b, 1) for b in basis], [(u, 1) for u in units])
        for z in range(512):
            left = (sum(dot(z, u) for u in units)-dot(z, q)) % 4
            right = (sum(dot(z, b) for b in basis[1:])+2*dot(z, eta)) % 4
            need(left == right, 'All exact local hole eigenvalues, including phase')
            eigenvalue_count += 1
        history = []
        for stage in range(9):
            align = item['stage_alignment'][stage]
            exterior = [(1 << i, 1) for i in range(9, 9+8*stage)]
            old = [] if stage == 0 else [(route(1 << i, stage, basis), 1)
                     for i in range(9+8*(stage-1))]+[(q, -1)]
            entry_sign = route(align['entry_Y'], stage, basis)
            need(form(old, entry_sign) == form(exterior), 'Exact cache input frame equals the local Y input frame')
            local_axes = units if stage == 8 else basis[1:]
            local_sign = 0 if stage == 8 else eta
            owner_axes = [route(a, stage, basis) for a in local_axes]
            new = [(route(a, stage, basis), 1) for a, _ in exterior]+[(a, 1) for a in owner_axes]
            new_sign = align['exit_Y'] ^ route(local_sign, stage, basis)
            target = [(1 << i, 1) for i in range(9+8*stage)]
            if stage != 8:
                target.append((q, -1))
            need(form(new, new_sign) == form(target), 'Exact cache output frame and scalar phase')
            phase_count += 2
            history.append({'stage': stage, 'local_register': ['C', k], 'data_port': p,
                            'label': q, 'owner_route': {'right_cover_translation': 'rho(stage,label)',
                            'same_address_gather_as_data_Y': True},
                            'entry_translation_owner_coordinates': align['entry_Y'],
                            'child_rank': len(local_axes), 'local_child_axes': local_axes,
                            'local_translation_after_child': local_sign,
                            'exit_translation_owner_coordinates': align['exit_Y'],
                            'owner_child_axes': owner_axes,
                            'capture_before_local_word': stage in (1, 3, 5, 7),
                            'unload_before_local_word': stage in (2, 4, 6, 8)})
        need(sum(h['child_rank'] for h in history) == 73, 'One complete independent owner job')
        histories.append({'cache': k, 'label': q, 'port': p, 'local_hole_translation': eta,
                          'hole_child_chart_columns': basis[1:]+[q], 'history': history})

    payload = {'schema': 'carried-query-alias-v1', 'source_base': BASE, 'source_pins': PINS,
               'T_ports': T_PORTS, 'query_rows': algebra.serial(query), 'capture': capture, 'unload': unload,
               'captured_backward_word': capture+logger['programs']['logger'],
               'following_forward_word': unload+borrowed['forward'], 'windows': windows, 'histories': histories,
               'owner_contract': 'Eight independent inputs h per replica. Local C aliases their port-routed fields. Final output is F73 h after the existing full-cover translation.',
               'closure_scope': 'The cache owner is restored after each window. The data source code G is not removed by this theorem.',
               'global_cover_correction': template['cover_final_correction']['formula']}
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    (HERE/'CARRIED-QUERY-ALIAS-PROGRAMS.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    receipt = {'status': 'PASS_CARRIED_QUERY_ALIAS', 'source_base': BASE, 'source_pins': PINS,
               'payload_sha256': sha256(raw).hexdigest(), 'local_input_columns': 712,
               'arbitrary_helpers_restored': 480, 'arbitrary_cache_inputs': 8,
               'capture': {'ADDs': 424, 'real_primitives': 4224},
               'unload': {'ADDs': 8, 'real_primitives': 64},
               'four_window_scalar_overhead_per_replica': 17152,
               'captured_logger_scalar_bound': 228166+4224,
               'captured_logger_native_profile': captured_profile,
               'local_hole_eigenvalues': eigenvalue_count, 'exact_73_axis_frame_identities': phase_count,
               'windows': windows, 'owner_profile_per_field': {8: 8, 9: 1},
               'paid_rank_per_owner': 73, 'productive_rank_per_independent_owner': 73,
               'owner_count_per_replica': 8, 'replicas': 16,
               'baseline_failure_witness': {'cache': witness[0], 'input_Y_port': witness[1], 'residual': str(witness[2])},
               'excluded_claims': ['Source G restoration', 'Full global data controller', 'Owner admission or final live-row count',
                                   'Full recursive cost or precision invoice', 'A change in kappa'],
               'native_scope': 'New hole and owner phases are exact. Retained local child kernels and their endpoint adapters are inherited from the pinned words.'}
    (HERE/'CARRIED-QUERY-ALIAS.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(receipt['status'])
    print('columns=712 hole_eigenvalues=4096 frame_identities=144 windows=4')
    print('owner_rank=8*8+9=73 capture_plus_unload=4288 per_window')
    print('payload_sha256='+receipt['payload_sha256'])


if __name__ == '__main__':
    main()
