"""Prepared independent deferred-K overlay checker. NOT RUN by its author.

Retains accepted native/alias/phase premises; imports only the frozen independent
operator Ring, never the producer/emitter/native evaluator. Root-reviewed request
and the sole peer guard are required before execution.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from collections import Counter
import argparse
import copy
import importlib.util
import json

HERE = Path(__file__).resolve().parent
INPUT = HERE / 'inputs'
BASE_REL = 'race-kappa0033-sol-high-20261024/lanes/algebra/balanced-J-native/BALANCED-J-NATIVE-v1.json'
BASE_SHA = '7f26477b561114e1189d1ac7e00fd5cf5b1aea4881433619c931c12c01eb1ffd'
PASS_REL = 'race-kappa0033-sol-high-20261024/lanes/challenge/balanced-J/RESULT-v1.json'
PASS_SHA = '9a895a972a523ef7a96dccdd31d357d8c6503db961bc8a3d37d13204b47a729d'
CUSTODY_REL = 'race-kappa0033-sol-high-20261024/lanes/source/BALANCED-J-CUSTODY-v1.json'
CUSTODY_SHA = 'a94e060c654b4e3765fd71e1966f51c0b214a585a3ae6f9f4ae5aa5815764c1a'
AUDIT_REL = 'outputs/kappa0033-race-20261024/plan/BALANCED-J-DEFERRED-K-audit/REPORT-v1.md'
AUDIT_SHA = '227397cd725bf55c97a9d760899360e68daca76257060c614dbea687855928a2'
RING_REL = 'race-kappa0033-sol-high-20261024/lanes/challenge/independent_words.py'
RING_SHA = '6c7f7e4e3591eb4a9cf05ac80285615ca6b27c521c5e00ac7501f49fb3c9674f'
HCODE_REL = 'swarm-coupled-caller-sol-high-20261024/agents/caller/PARAMETRIC-HCODE-v14.json'
NORMAL_REL = 'swarm-provider-audit-sol-high-20261024/repository/research/coded-native-caller/NORMALIZERS.json'
Q_BINDING_REL = 'outputs/kappa0033-race-20261024/plan/BALANCED-J-CURRENT-Q-FRAME-audit/BINDING-v1.json'
Q_BINDING_SHA = 'd1b2918c00a0987c763593b9383ee239bdce5a54ad6bec3bf1d1670661eed6e7'
Q_PROOF_SHA = 'fb60187fea8346539abb61a08b1c525825cc84bd7c2847eb44a7c9590f3abee3'
ACTIVE = [0] + list(range(9, 17))
E_FIELDS = [f'y{i}' for i in range(112)] + [f'h{j}' for j in range(8)]
K_FIELDS = [f'k{j}' for j in range(8)]
CORRECTION_KIND = 'DEFERRED_K_STRICT'
QUERY_KIND = 'CURRENT_SOURCE_Q120'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def lift(word, axes=ACTIVE):
    def mask(value):
        return sum(1 << axes[j] for j in range(9) if value >> j & 1)
    result = []
    for gate in word:
        if gate[0] == 'P':
            columns = [1 << j for j in range(25)]
            for j, value in enumerate(gate[1]):
                columns[axes[j]] = mask(value)
            result.append(['P', columns])
        elif gate[0] == 'D':
            quad, linear = [0] * 25, [0] * 25
            for j, value in enumerate(gate[1]):
                quad[axes[j]] = mask(value)
            for j, value in enumerate(gate[2]):
                linear[axes[j]] = value
            result.append(['D', quad, linear])
        elif gate[0] == 'X':
            result.append(['X', mask(gate[1])])
        else:
            need(gate[0] == 'phase', 'known phase-bearing monomial token')
            result.append(list(gate))
    return result


def prerequisites():
    for rel, expected in ((BASE_REL, BASE_SHA), (PASS_REL, PASS_SHA),
                          (CUSTODY_REL, CUSTODY_SHA), (AUDIT_REL, AUDIT_SHA),
                          (RING_REL, RING_SHA), (Q_BINDING_REL, Q_BINDING_SHA)):
        need(digest(INPUT / rel) == expected, 'frozen premise ' + rel)
    base = read(INPUT / BASE_REL)
    accepted = read(INPUT / PASS_REL)
    need(accepted['packet_sha256'] == BASE_SHA and accepted['all_owned_zero_returns'] is True,
         'accepted exact base packet and owned return')
    need(accepted['both_main_inverse_products'] is True and accepted['complete_caller'] is False,
         'retained MAIN inverse premise scope')
    for rel, expected in base['source_pins'].items():
        need(digest(INPUT / rel) == expected, 'frozen base source ' + rel)
    for rel, expected in read(INPUT / Q_BINDING_REL)['source_files'].items():
        need(digest(INPUT / rel) == expected, 'retained actual-Q physical/phase dependency ' + rel)
    normal = read(INPUT / NORMAL_REL)
    matrix = normal['mode_columns']
    hcode = read(INPUT / HCODE_REL)['operations']
    entrances = {op['field']: op['word'] for op in hcode[:120]}
    exits = {op['field']: op['word'] for op in hcode[-120:]}
    need(len(entrances) == len(exits) == 120, 'all actual source K frames')
    # Data-specific real-word premise for the MAIN transpose check below.
    # P/X are real permutations; an even Z4 diagonal/global phase is real.
    for word in list(entrances.values()) + list(exits.values()):
        for gate in word:
            if gate[0] == 'D':
                need(all(value % 2 == 0 for value in gate[2]), 'actual real signed K diagonal')
            elif gate[0] == 'phase':
                need(gate[1] % 2 == 0, 'actual real K absolute phase')
            else:
                need(gate[0] in ('P', 'X'), 'real source monomial alphabet')
    need(base['stage_geometry']['source9_to_stage_axes'] == ACTIVE, 'source-stage embedding')
    need(base['remaining_helper_profile'] == {'4': 28, '7': 7, '8': 39, '9': 318},
         '392 positive helper jobs per direction')
    need(base['inherited_paid_profile'] == {'1': 2193, '2': 412, '3': 510, '4': 127, '5': 40},
         'unchanged source native paid invoice, before full current Q120')
    return base, matrix, entrances, exits


def k_word(entrances, exits, field, inverse=False):
    reference = ('x' + field[1:]) if field.startswith('y') else ('k' + field[1:])
    return (exits if inverse else entrances)[reference]


def free_add(a, b, scalar):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, F()) + scalar * value
        if not out[key]:
            del out[key]
    return out


def free_left(poly, label, sign):
    out = {}
    for (owner, word), coefficient in poly.items():
        if word and word[0] == (label, -sign):
            new_word = word[1:]
        else:
            new_word = ((label, sign),) + word
        out[owner, new_word] = coefficient
    return out


def correction(segment, sign, matrix, entrances, exits):
    """Interpret changed literal tape on129 independent E/K/c0 inputs."""
    names = E_FIELDS + K_FIELDS + ['c0']
    initial = {name: {(i, ()): F(1)} for i, name in enumerate(names)}
    rows = copy.deepcopy(initial)
    norm = {name: False for name in K_FIELDS}
    scratch_chart = 'dirty'
    cleared = False
    copied_port = None
    scratch_normalized = False
    counts = Counter()
    for op in segment['operations']:
        kind = op['op']; counts[kind] += 1
        writes = [op.get('dst')] if kind in ('ADD', 'COPY') else [op.get('field')]
        need(not any(name in E_FIELDS for name in writes), 'strict E write forbidden at every primitive')
        if kind == 'CLEAR':
            need(op['field'] == 'c0' and op.get('owned') is True, 'only existing owned c0 CLEAR')
            rows['c0'] = {}; scratch_chart = None; copied_port = None
            scratch_normalized = False; cleared = True
        elif kind == 'ZERO_RETAG':
            need(op['field'] == 'c0' and cleared and not rows['c0'], 'retag immediately cleared c0')
            chart = op['chart']
            need(chart == 'ground' or chart in ['exact current frame of ' + x for x in E_FIELDS[:112]],
                 'explicit actual source chart')
            scratch_chart = chart; cleared = False
        elif kind == 'COPY':
            need(op['dst'] == 'c0' and op['src'] in E_FIELDS[:112] and not rows['c0'],
                 'copy actual current source port to zero c0')
            need(op.get('owned_zero_destination') is True and
                 scratch_chart == 'exact current frame of ' + op['src'], 'COPY same actual chart')
            rows['c0'] = dict(rows[op['src']]); copied_port = op['src']; cleared = False
        elif kind == 'MONOMIAL':
            field = op['field']
            if field in K_FIELDS:
                inverse = norm[field]
                expected = k_word(entrances, exits, field, inverse)
                need(op['word'] == lift(expected), 'source-stage Km word/phase/spectator binding')
                if 'source_word9' in op:
                    need(op['source_word9'] == expected, 'literal source9 Km word')
                rows[field] = free_left(rows[field], 'Km' + field[1:], -1 if inverse else 1)
                norm[field] = not inverse
            else:
                need(field == 'c0' and copied_port is not None and not scratch_normalized,
                     'one actual source Kp on copied port')
                expected = k_word(entrances, exits, copied_port)
                need(op['word'] == lift(expected), 'source-stage Kp word/phase/spectator binding')
                if 'source_word9' in op:
                    need(op['source_word9'] == expected, 'literal source9 Kp word')
                rows['c0'] = free_left(rows['c0'], 'Kp' + copied_port[1:], 1)
                scratch_normalized = True
            cleared = False
        elif kind == 'ADD':
            dst, src, coefficient = op['dst'], op['src'], F(op['coefficient'])
            need(dst in K_FIELDS and dst != src and coefficient in (1, -1, F(1, 2), F(-1, 2)),
                 'legal distinct unit/half ADD to K only')
            if src == 'c0':
                need(norm[dst] and scratch_normalized, 'gather in actual common K frame')
            else:
                need(src == 'h' + dst[1:] and not norm[dst], 'direct mode update in canonical C8 coordinates')
            rows[dst] = free_add(rows[dst], rows[src], coefficient); cleared = False
        else:
            raise ValueError('unexpected correction primitive ' + kind)
        need(all(rows[name] == initial[name] for name in E_FIELDS), 'all120 E rows preserved at every primitive')
    need(dict(counts) == {'ADD': 1000, 'MONOMIAL': 128, 'COPY': 112, 'CLEAR': 224, 'ZERO_RETAG': 224},
         'chosen strict unit/half correction complete census')
    need(not any(norm.values()) and not rows['c0'] and scratch_chart == 'ground',
         'K physical charts restored and c0 final zero/ground')
    for j in range(8):
        expected = free_add(initial[f'k{j}'], initial[f'h{j}'], sign * F(13))
        for i, value in enumerate(matrix[j]):
            if value:
                term = free_left(free_left(initial[f'y{i}'], 'Kp' + str(i), 1), 'Km' + str(j), -1)
                expected = free_add(expected, term, sign * F(3 * value, 2))
        need(rows[f'k{j}'] == expected, 'all129 independent correction input columns, mode ' + str(j))
    return {'entry_columns': 129, 'strict_source_fields': 120, 'strict_source_preserved_every_primitive': True,
            'c0_dirty_direction_erased': True, 'counts': dict(counts), 'phase_semantics': 'retained actual-word premise'}


def query(segment, inverse=False):
    operations = segment['operations']
    expected_length = 240 if inverse else 120
    need(len(operations) == expected_length, 'all120 current source queries, never old-h substitution')
    for i, field in enumerate(E_FIELDS):
        event = operations[2 * i if inverse else i]
        need(event['op'] == 'GAUSSIAN_Q' and event['field'] == field and event['rank'] == 1 and
             event['axis'] == 0 and event['sign'] == 1 and event.get('paid') is True,
             'actual positive common-central q on current canonical field ' + field)
        need(event.get('phase', 0) == 0 and event.get('absolute_phase', 0) == 0,
             'no extra exterior phase on canonical positive current Q')
        if inverse:
            event = operations[2 * i + 1]
            need(event['op'] == 'MONOMIAL' and event['field'] == field and event['word'] == [['X', 1]],
                 'actual inverse q positive-call central-X lowering')
            need(event.get('phase', 0) == 0 and event.get('absolute_phase', 0) == 0,
                 'phase-zero whole-column central-X')


def layout(packet, base):
    kept_forward = [s for s in base['forward_segments'] if s['kind'] != 'QUERY_OLD_H']
    kept_inverse = [s for s in base['inverse_segments'] if s['kind'] != 'QUERY_OLD_H']
    fs, ins = packet['forward_segments'], packet['inverse_segments']
    need(len(fs) == len(kept_forward) + 2 and len(ins) == len(kept_inverse) + 2, 'exact two inserted segments')
    need(fs[:-2] == kept_forward and ins[2:] == kept_inverse, 'all retained fusedT/native/alias/scalar bytes unchanged')
    need([s['kind'] for s in fs[-2:]] == [QUERY_KIND, CORRECTION_KIND], 'forward full current Q BEFORE correction')
    need([s['kind'] for s in ins[:2]] == [CORRECTION_KIND, QUERY_KIND], 'inverse undo K BEFORE q-inverse')
    return fs, ins


def operator_check(fs, ins):
    spec = importlib.util.spec_from_file_location('retained_independent_deferred_k_ring', INPUT / RING_REL)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    r = module.Ring(); one = r.monomial(); q = r.q(); w, z, d = r.w(1), r.z(1), r.d(1)
    di = r.monomial(d=(0, -1, 0)); R = r.product(q, d)
    c = r.add(one, r.scale(r.product(w, z), -1))
    J = [[c, r.scale(w, -4)], [r.scale(z, 3), r.monomial(coefficient=13)]]
    def replay(segments, inverse=False):
        rows = r.identity(6)
        for segment in segments:
            kind = segment['kind']
            if kind == CORRECTION_KIND:
                ell = r.rowsum(r.leftrow(r.scale(z, 3), rows[2]), rows[3], 13)
                rows[1] = r.rowsum(rows[1], ell, 1 if inverse else -1)
                rows[5] = [{}] * 6
            elif kind == QUERY_KIND:
                operator = r.q(-1) if inverse else q
                rows[2] = r.leftrow(operator, rows[2]); rows[3] = r.leftrow(operator, rows[3])
            elif kind == 'OWNED_SCALAR_LOWERING':
                rows[3] = r.leftrow(r.monomial(coefficient=F(segment['coefficient'])), rows[3]); rows[4] = [{}] * 6
            elif kind == 'COMMON_FRAME_SHEAR_Z':
                rows[3] = r.rowsum(rows[3], r.leftrow(z, rows[2]), segment['sign'])
            elif kind == 'COMMON_FRAME_SHEAR_W':
                rows[2] = r.rowsum(rows[2], r.leftrow(w, rows[3]), segment['sign'])
            elif kind == 'COMPRESSED_PINNED_NATIVE_PROVIDER':
                x, k, y, h = rows[:4]
                if inverse:
                    yy = r.leftrow(di, y); hh = r.rowsum(r.leftrow(di, h), r.leftrow(z, yy), 1)
                    xx = r.rowsum(r.rowsum(r.leftrow(di, x), r.leftrow(q, yy), 1), r.leftrow(r.product(q, w), hh), -1)
                    rows[:4] = [xx, r.leftrow(di, k), yy, hh]
                else:
                    xx = r.rowsum(r.rowsum(r.leftrow(d, x), r.leftrow(R, y), -1), r.leftrow(r.product(R, w), h), 1)
                    rows[:4] = [xx, r.leftrow(d, k), r.leftrow(d, y), r.leftrow(d, r.rowsum(h, r.leftrow(z, y), -1))]
                rows[4] = [{}] * 6; rows[5] = [{}] * 6
            else:
                need(kind in ('COMMON_K_FRAME_ENTRY', 'COMMON_K_FRAME_EXIT', 'INHERITED_ALIAS_WORDS'), 'only authenticated inherited macros compressed')
        return rows
    fwd, inv = replay(fs), replay(ins, True)
    target = [[{} for _ in range(6)] for _ in range(6)]
    target[0][0] = d; target[1][1] = d; target[0][2] = r.scale(R, -1); target[1][3] = r.scale(R, -1)
    for i in range(2):
        for j in range(2):
            target[i + 2][j + 2] = r.product(J[i][j], R)
    need(fwd == target, 'all240 main and arbitrary9owned source-version endpoint (Du-Rv,JRv)')
    identity = r.identity(6); identity[4] = [{}] * 6; identity[5] = [{}] * 6
    need(r.matrix(inv, fwd) == identity and r.matrix(fwd, inv) == identity, 'both MAIN inverse products only')
    # An independently derived inverse: u=D^-1(A+JE), v=R^-1JE.
    expected_inverse = [[{} for _ in range(6)] for _ in range(6)]
    expected_inverse[0][0] = di; expected_inverse[1][1] = di
    for i in range(2):
        for j in range(2):
            expected_inverse[i][j + 2] = r.product(di, J[i][j])
            expected_inverse[i + 2][j + 2] = r.product(di, r.q(-1), J[i][j])
    need(inv == expected_inverse, 'independent ordered inverse formula')
    # Algebraic MAIN raw IT only. Physical C1/C8 are symmetric (not real),
    # actual K words are real orthogonal, hence W^T=Z and Z^T=W. This is
    # transpose, not adjoint: q is not changed to q^-1 by this operation.
    def transpose_poly(poly):
        result = {}
        for (word, powers), coefficient in poly.items():
            reversed_word = tuple(('z' if kind == 'w' else 'w' if kind == 'z' else 'q', index)
                                  for kind, index in reversed(word))
            term = r.product(r.monomial(d=powers), r.monomial(reversed_word, coefficient=coefficient))
            result = r.add(result, term)
        return result
    def transpose_matrix(matrix):
        return [[transpose_poly(matrix[j][i]) for j in range(len(matrix))]
                for i in range(len(matrix[0]))]
    jt = transpose_matrix(J)
    need(jt != J, 'J generally nonsymmetric; never replace J transpose by J')
    raw_it = transpose_matrix(inv)
    want_it = [[{} for _ in range(6)] for _ in range(6)]
    want_it[0][0] = di; want_it[1][1] = di
    for i in range(2):
        for j in range(2):
            want_it[i + 2][j] = r.product(jt[i][j], di)
            want_it[i + 2][j + 2] = r.product(jt[i][j], di, r.q(-1))
    need(raw_it == want_it, 'ordered main F^-T=[[D^-T,0],[J^T D^-T,J^T R^-T]]')
    ft = transpose_matrix(fwd)
    need(r.matrix(raw_it, ft) == identity and r.matrix(ft, raw_it) == identity,
         'both MAIN transpose/inverse products, no helper/owned dual compilation claim')
    bad_forward = list(fs[:-2]) + [fs[-1], fs[-2]]
    need(replay(bad_forward) != target, 'correction from pre-query DJv rejected')
    bad_inverse = [ins[1], ins[0]] + list(ins[2:])
    need(r.matrix(replay(bad_inverse, True), fwd) != identity, 'inverse correction from q^-1E rejected')
    need(replay(fs[:-1]) != target, 'omitted deferred correction rejected')
    return {'forward_rows': [[r.serialize(x) for x in row] for row in fwd],
            'inverse_rows': [[r.serialize(x) for x in row] for row in inv],
            'algebraic_main_raw_IT_rows': [[r.serialize(x) for x in row] for row in raw_it],
            'main_raw_IT_scope': 'Ordered MAIN F^-T only; no literal full native/helper/owned dual emitted or compiled',
            'main_raw_IT_both_products': True, 'J_transpose_not_replaced_by_J': True,
            'both_main_inverse_products': True,
            'operator_controls': ['pre_query_correction_wrong_version', 'inverse_q_before_correction_wrong_order', 'omitted_correction'],
            'nonzero_control_scope': 'formal certificate rejection under retained physical relations, no new physical impulse replay'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--packet', type=Path, required=True)
    parser.add_argument('--packet-sha256', required=True)
    parser.add_argument('--source-q-proof', type=Path, required=True)
    parser.add_argument('--source-q-proof-sha256', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), 'fresh output; preserve all prior receipts')
    need(digest(args.packet) == args.packet_sha256, 'root-reviewed immutable overlay packet')
    need(digest(args.source_q_proof) == args.source_q_proof_sha256,
         'root-reviewed actual common-central Q placement/phase premise')
    need(args.source_q_proof_sha256 == Q_PROOF_SHA, 'exact accepted raw-Q proof version')
    base, matrix, entrances, exits = prerequisites()
    packet = read(args.packet)
    need(packet['base_packet_sha256'] == BASE_SHA, 'exact accepted baseT input')
    need(packet.get('complete_caller', False) is False and packet.get('gain_claimed', False) is False
         and packet.get('new_kappa') is None, 'packet component-only claim boundary')
    if 'stage_geometry' in packet:
        need(packet['stage_geometry'] == base['stage_geometry'], 'packet source geometry agrees with retained base')
    if 'remaining_helper_profile' in packet:
        need(packet['remaining_helper_profile'] == base['remaining_helper_profile'], 'no helper promotion or target deletion')
    fs, ins = layout(packet, base)
    query(fs[-2]); query(ins[1], True)
    forward_correction = correction(fs[-1], -1, matrix, entrances, exits)
    inverse_correction = correction(ins[0], 1, matrix, entrances, exits)
    counters = {}
    for direction, segments in (('forward', fs), ('inverse', ins)):
        counts = dict(Counter(op['op'] for segment in segments for op in segment['operations']))
        expected = {'ADD': 1952, 'MONOMIAL': 1288 if direction == 'inverse' else 1168,
                    'COPY': 136, 'SWAP': 24, 'CLEAR': 272, 'ZERO_RETAG': 272,
                    'GAUSSIAN_Q': 120, 'PROVIDER_5411_INVERSE' if direction == 'inverse' else 'PROVIDER_5402': 1}
        need(counts == expected, 'full external overlay census ' + direction)
        counters[direction] = counts
    operators = operator_check(fs, ins)
    controls = list(operators['operator_controls'])
    bad = copy.deepcopy(fs[-2]); bad['operations'].pop()
    try:
        query(bad)
    except ValueError:
        controls.append('omitted_current_mode_query_rejected')
    else:
        raise ValueError('omitted-query control admitted')
    bad = copy.deepcopy(fs[-2])
    bad['operations'].insert(0, {'op': 'MONOMIAL', 'field': 'y0', 'word': lift(entrances['x0'])})
    try:
        query(bad)
    except ValueError:
        controls.append('K_conjugated_Q_changes_source_map_rejected')
    else:
        raise ValueError('routed-Q source-version control admitted')
    bad = copy.deepcopy(fs[-2]); bad['operations'][0]['absolute_phase'] = 1
    try:
        query(bad)
    except ValueError:
        controls.append('wrong_query_exterior_phase_rejected')
    else:
        raise ValueError('extra positive-Q exterior phase control admitted')
    for label in ('missing_c0_CLEAR', 'wrong_correction_sign', 'wrong_source_phase', 'wrong_destination_stage_Z', 'write_E'):
        bad = copy.deepcopy(fs[-1])
        if label == 'missing_c0_CLEAR':
            index = next(i for i, op in enumerate(bad['operations']) if op['op'] == 'CLEAR'); bad['operations'].pop(index)
        elif label == 'wrong_correction_sign':
            op = next(op for op in bad['operations'] if op['op'] == 'ADD'); op['coefficient'] = str(-F(op['coefficient']))
        elif label == 'wrong_source_phase':
            op = next(op for op in bad['operations'] if op['op'] == 'MONOMIAL'); op['word'].append(['phase', 1])
        elif label == 'wrong_destination_stage_Z':
            op = next(op for op in bad['operations'] if op['op'] == 'MONOMIAL')
            op['word'] = lift(k_word(entrances, exits, op['field']), [0] + list(range(17, 25)))
        else:
            bad['operations'].append({'op': 'ADD', 'dst': 'y0', 'src': 'k0', 'coefficient': '1'})
        try:
            correction(bad, -1, matrix, entrances, exits)
        except ValueError:
            controls.append(label + '_rejected')
        else:
            raise ValueError(label + ' control admitted')
    bad = copy.deepcopy(packet)
    bad['forward_segments'].insert(len(bad['forward_segments']) - 1,
                                   {'kind': 'DESTINATION_J_ENCODING', 'operations': []})
    try:
        layout(bad, base)
    except ValueError:
        controls.append('correction_after_destination_encoding_outside_component_rejected')
    else:
        raise ValueError('destination encoding placement control admitted')
    result = {'schema': 'independent-deferred-k-query-sharing/1',
              'status': 'PASS_LITERAL_DEFERRED_K_COMPONENT_UNDER_RETAINED_NATIVE_SOURCE_PREMISES',
              'overlay_packet_sha256': args.packet_sha256, 'checker_sha256': digest(Path(__file__)),
              'source_q_phase_placement_premise_sha256': args.source_q_proof_sha256,
              'source_q_actual_physical_control': 'Actual Km0^-1 Q Km0 sends delta0 to a delta0-b delta1537; required rawQ gives a delta0+b delta1, retained analytic width1 witness, no new phase execution',
              'base_packet_sha256': BASE_SHA, 'base_pass_sha256': PASS_SHA, 'source_custody_sha256': CUSTODY_SHA,
              'forward_correction': forward_correction, 'inverse_correction': inverse_correction,
              'census': counters, 'main_original_directions': 240, 'owned_entry_directions': 9,
              'helpers': {'count': 392, 'positive_profile_each_direction': {'4': 28, '7': 7, '8': 39, '9': 318},
                          'inverse_helper_composition_claimed': False, 'unchanged_by_exact_retained_segment_equality': True},
              'paid_each_direction': {'1': 2313, '2': 412, '3': 510, '4': 127, '5': 40},
              'paid_delta_vs_baseT_plus_currentQ120': {'1': -8},
              'new_productive_targets': 0, 'existing_thin_query_removed': False,
              'controls': controls, 'operator_certificate': operators,
              'retained_analytic_physical_control_oracles': {
                  'forward_wrong_version': 'Attainable Vprime=(0,mode0*delta0): 13(Q-I)delta0 is nonzero by actual width1 central gate',
                  'inverse_wrong_order': 'Arbitrary E=(0,mode0*delta0): recovered K differs by 13D^-1(Q^-1-I)delta0, nonzero',
                  'omitted_correction': 'Arbitrary nonzero original h leaves Rh missing from K; R invertible',
                  'execution_scope': 'Written source-bound physical witnesses; no new numerical/phase/native evaluation'},
              'raw_native_tape_replayed': False, 'source_phase_census_replayed': False,
              'scope': 'New literal correction/current-source query component only; accepted originalT/native632+9/aliases/phase/allwidth premises retained. Global caller, endpoints, chronology/funding/compiler remain open.',
              'complete_caller': False, 'gain_claimed': False, 'new_kappa': None}
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('status', 'main_original_directions', 'owned_entry_directions', 'complete_caller')}))


if __name__ == '__main__':
    main()
