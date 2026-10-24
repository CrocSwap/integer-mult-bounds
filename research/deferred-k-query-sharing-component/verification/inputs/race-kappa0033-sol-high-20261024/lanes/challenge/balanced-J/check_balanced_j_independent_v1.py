"""Root-only independent boundary/owned interpreter; retained native ABI is a premise."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from collections import Counter
import argparse
import copy
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PACKET = ROOT / 'race-kappa0033-sol-high-20261024/lanes/algebra/balanced-J-native/BALANCED-J-NATIVE-v1.json'
PACKET_SHA = '7f26477b561114e1189d1ac7e00fd5cf5b1aea4881433619c931c12c01eb1ffd'
ENGINE = HERE.parent / 'independent_words.py'
ENGINE_SHA = '6c7f7e4e3591eb4a9cf05ac80285615ca6b27c521c5e00ac7501f49fb3c9674f'
RETAINED_RECEIPTS = {
    'swarm-coupled-caller-sol-high-20261024/agents/challenge/HELPER-ALIAS-RESULT-v2.json': '18225bcb8ec394c97b0f367df566359c2d822d8ed06d60fe1a20dc557ca52837',
    'swarm-coupled-caller-sol-high-20261024/agents/challenge/INVERSE-DELTA-RESULT-v2.json': '45a893a1ad9bc0cf9a0cef67e024dcb9e90acef3ed06e50b96b1be4bdd5488cb',
    'swarm-coupled-caller-sol-high-20261024/agents/challenge/PARAMETRIC-LOCAL-RESULT-v14.json': '675e8f45d322fd613208ef27f60dfde267e01519d1323212e0a5bca1ce15961a'}

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_bytes())

ACTIVE = [0] + list(range(9, 17))

def lift(word):
    def mask(m):
        return sum(1 << ACTIVE[j] for j in range(9) if m >> j & 1)
    out = []
    for op in word:
        if op[0] == 'P':
            columns = [1 << j for j in range(25)]
            for j, m in enumerate(op[1]):
                columns[ACTIVE[j]] = mask(m)
            out.append(['P', columns])
        elif op[0] == 'D':
            quadratic, linear = [0] * 25, [0] * 25
            for j, m in enumerate(op[1]):
                quadratic[ACTIVE[j]] = mask(m)
            for j, c in enumerate(op[2]):
                linear[ACTIVE[j]] = c
            out.append(['D', quadratic, linear])
        elif op[0] == 'X':
            out.append(['X', mask(op[1])])
        else:
            need(op[0] == 'phase', 'known exact monomial token')
            out.append(op)
    return out

def source_record(op):
    result = {k: v for k, v in op.items() if k not in ('source_word9', 'lift')}
    result['word'] = op['source_word9']
    return result

def static_binding(p):
    for path, expected in RETAINED_RECEIPTS.items():
        need(sha(ROOT / path) == expected, 'retained phase/native/helper receipt ' + path)
    for path, expected in p['source_pins'].items():
        need(sha(ROOT / path) == expected, 'pinned source ' + path)
    need(p['stage_geometry']['source9_to_stage_axes'] == ACTIVE, 'literal stage geometry')
    need(p['owned']['fields'] == ['c' + str(i) for i in range(9)], 'exact native9 allocation')
    need(p['remaining_helper_count'] == 392 and p['remaining_helper_profile'] == {'4': 28, '7': 7, '8': 39, '9': 318}, 'positive helper premise')
    caller = ROOT / 'swarm-coupled-caller-sol-high-20261024/agents/caller'
    hf = read(caller / 'PARAMETRIC-HCODE-v14.json')['operations']
    sf = read(caller / 'PUBLIC-PROMOTED-CANDIDATE-v13.json')['operations']
    si = read(caller / 'PUBLIC-PROMOTED-INVERSE-v13.json')['operations']
    fi = next(i for i, x in enumerate(sf) if x['op'] == 'PROVIDER_5402')
    ii = next(i for i, x in enumerate(si) if x['op'] == 'PROVIDER_5411_INVERSE')
    aliases = {
        'forward_alias_pre': [x for x in sf[:fi] if x['op'] == 'MONOMIAL' and ('source_owner' in x or x.get('whole_job_boundary') == 'before provider')],
        'forward_alias_post': sf[fi + 1:],
        'inverse_alias_pre': si[:ii],
        'inverse_alias_post': [x for x in si[ii + 1:] if x['op'] == 'MONOMIAL' and ('source_owner' in x or x.get('whole_job_boundary') == 'after raw inverse')]}
    M = read(ROOT / 'swarm-provider-audit-sol-high-20261024/repository/research/coded-native-caller/NORMALIZERS.json')['mode_columns']
    need(len(M) == 8 and all(len(row) == 112 for row in M), 'M shape')
    need(all(sum(M[a][i] * M[b][i] for i in range(112)) == 56 * (a == b) for a in range(8) for b in range(8)), 'actual M Gram, hence ZW=14')
    for direction in ('forward', 'inverse'):
        segs = p[direction + '_segments']
        counts = Counter(op['op'] for seg in segs for op in seg['operations'])
        need(dict(counts) == p[direction + '_counts'], 'literal packet census')
        need(all(counts[k] == v for k, v in {'ADD': 960, 'MONOMIAL': 1040, 'COPY': 32, 'SWAP': 24, 'CLEAR': 64, 'ZERO_RETAG': 64, 'GAUSSIAN_Q': 8}.items()) and 'SCALE' not in counts, 'exact native boundary alphabet/bill')
        raw = next(s for s in segs if s['kind'] == 'COMPRESSED_PINNED_NATIVE_PROVIDER')['operations']
        need(len(raw) == 1, 'one pinned raw call')
        roles = raw[0]['roles']
        need(roles == {'x': list(range(112)), 'y': list(range(112, 224)), 'h': p['coupled_h_owners'], 'k': p['promoted_old_H8_owners']}, 'all240 actual raw role bindings')
        need(len(set(sum(roles.values(), []))) == 240, 'all independent main owners')
        need(raw[0]['owned_fields'] == p['owned']['fields'] and raw[0]['owned_exit'] == 'zero', 'native9 erasure premise')
        need(raw[0]['op'] == ('PROVIDER_5402' if direction == 'forward' else 'PROVIDER_5411_INVERSE'), 'actual direction-specific raw call')
        for seg in segs:
            kind = seg['kind']
            if kind == 'INHERITED_ALIAS_WORDS':
                need(len(seg['operations']) == 400 and [source_record(x) for x in seg['operations']] == aliases[seg['label']], 'all400 direction-specific aliases at boundary')
            if kind.startswith('COMMON_K_FRAME'):
                reference = hf[:120] if kind.endswith('ENTRY') else hf[-120:]
                reference = [{**x, 'field': ('y' + x['field'][1:]) if x['field'].startswith('x') else ('h' + x['field'][1:])} for x in reference]
                need([source_record(x) for x in seg['operations']] == reference, 'exact pinned K words/frame orientation')
            if kind == 'INHERITED_ALIAS_WORDS' or kind.startswith('COMMON_K_FRAME'):
                for op in seg['operations']:
                    need(op['word'] == lift(op['source_word9']), 'all25-axis phases and spectator lifts exact')
            if kind.startswith('COMMON_FRAME_SHEAR_'):
                z = kind.endswith('_Z')
                expected = [{'op': 'ADD', 'dst': f'h{k}' if z else f'y{i}', 'src': f'y{i}' if z else f'h{k}', 'coefficient': str(F(seg['sign'] * value, 2))} for k, row in enumerate(M) for i, value in enumerate(row) if value]
                need(seg['operations'] == expected and len(expected) == 448, 'literal448 signed rectangular shear')
    return {'source_pins': len(p['source_pins']), 'direction_alias_maps': 800, 'actual_M_entries_per_shear': 448, 'retained_receipts': RETAINED_RECEIPTS, 'source_phase_replayed': False}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    need(not args.output.exists(), 'fresh result')
    need(sha(PACKET) == PACKET_SHA and sha(ENGINE) == ENGINE_SHA, 'frozen packet and independent engine')
    p = read(PACKET)
    binding = static_binding(p)
    spec = importlib.util.spec_from_file_location('own_balanced_independent_ring', ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    r = module.Ring()
    one = r.monomial()
    q, w, z, d = r.q(), r.w(1), r.z(1), r.d(1)
    di = r.monomial(d=(0, -1, 0))
    c = r.add(one, r.scale(r.product(w, z), -1))
    R = r.product(q, d)

    def add(a, b, scalar=1):
        return r.rowsum(a, b, scalar)

    def left(a, row):
        return r.leftrow(a, row)

    # Interpret every instruction in an episode on distinct h8,k8,c8,c0 inputs.
    # Only after this exact25-input test may its uniform modewise result be compressed.
    def episode(seg):
        names = [f'h{i}' for i in range(8)] + [f'k{i}' for i in range(8)] + [f'c{i}' for i in range(9)]
        rows = {name: [one if i == j else {} for j in range(25)] for i, name in enumerate(names)}
        initial = copy.deepcopy(rows)
        tags = {name: ('h' + name[1:]) if name.startswith('h') else 'ground' if name.startswith('k') else 'dirty' for name in names}
        cleared = None
        snapshots = []
        for op in seg['operations']:
            kind = op['op']
            if kind == 'CLEAR':
                f = op['field']; need(f in names[17:] and op['owned'] is True, 'CLEAR only c1..c8')
                rows[f] = [{} for _ in range(25)]; tags[f] = None; cleared = f
            elif kind == 'ZERO_RETAG':
                f = op['field']; need(f == cleared and not any(rows[f]) and op['premise'] == 'immediately preceding owned CLEAR', 'retag actual immediately cleared field')
                chart = op['chart']; tags[f] = chart.replace('exact current frame of ', '') if chart != 'ground' else 'ground'; cleared = None
            elif kind == 'COPY':
                dst, src = op['dst'], op['src']; need(dst in names[17:] and src in names[:8] and not any(rows[dst]) and op['owned_zero_destination'] is True and tags[dst] == tags[src], 'COPY actual zero with source chart')
                rows[dst] = list(rows[src]); cleared = None
            elif kind == 'ADD':
                dst, src = op['dst'], op['src']; scalar = F(op['coefficient'])
                need(dst != src and scalar in (1, -1, F(1, 2), F(-1, 2)), 'legal distinct-field dyadic ADD')
                rows[dst] = add(rows[dst], rows[src], scalar); cleared = None
            elif kind == 'SWAP':
                a, b = op['fields']; need(a in names[:8] and b in names[17:] and op['includes_chart'] is True, 'whole field/chart SWAP')
                rows[a], rows[b] = rows[b], rows[a]; tags[a], tags[b] = tags[b], tags[a]; cleared = None
            elif kind == 'GAUSSIAN_Q':
                f = op['field']; need(f in names[17:] and op['rank'] == 1 and op['axis'] == 0 and op['sign'] == 1 and op['paid'] is True, 'positive rank1 Q on owned copy')
                rows[f] = left(q, rows[f]); snapshots.append(list(rows[f])); cleared = None
            else:
                raise ValueError('unexpected episode primitive')
        is_query = seg['kind'] == 'QUERY_OLD_H'
        for i in range(8):
            want_h = initial[f'h{i}'] if is_query else left(r.monomial(coefficient=F(seg['coefficient'])), initial[f'h{i}'])
            want_k = add(initial[f'k{i}'], left(q, initial[f'h{i}']), -1 if seg['label'] == 'query_original_h' else 1) if is_query else initial[f'k{i}']
            need(rows[f'h{i}'] == want_h and rows[f'k{i}'] == want_k, 'all distinct modewise columns exact')
            need(not any(rows[f'c{i+1}']) and tags[f'c{i+1}'] == 'ground', 'each owned slot final zero/ground')
        need(rows['c0'] == initial['c0'], 'c0 remains arbitrary and unread before raw native erasure')
        if is_query:
            need(snapshots == [left(q, initial[f'h{i}']) for i in range(8)], 'query actual independent old-h columns')
        return F(seg.get('coefficient', 1))

    def replay(segments, inverse=False):
        rows = r.identity(6)
        queries = []
        for seg in segments:
            kind = seg['kind']
            if kind == 'OWNED_SCALAR_LOWERING':
                scalar = episode(seg); rows[3] = left(r.monomial(coefficient=scalar), rows[3]); rows[4] = [{}] * 6
            elif kind == 'QUERY_OLD_H':
                episode(seg); query = left(q, rows[3]); queries.append(query)
                rows[1] = add(rows[1], query, 1 if inverse else -1); rows[4] = [{}] * 6
            elif kind == 'COMMON_FRAME_SHEAR_Z':
                rows[3] = add(rows[3], left(z, rows[2]), seg['sign'])
            elif kind == 'COMMON_FRAME_SHEAR_W':
                rows[2] = add(rows[2], left(w, rows[3]), seg['sign'])
            elif kind == 'COMPRESSED_PINNED_NATIVE_PROVIDER':
                need(not any(rows[4]), 'all8 scratch released before native')
                x, k, y, h = rows[:4]
                if inverse:
                    # Ordered actual recovery, independently of producer raw matrix.
                    yy = left(di, y)
                    hh = add(left(di, h), left(z, yy))
                    xx = add(add(left(di, x), left(q, yy)), left(r.product(q, w), hh), -1)
                    rows[:4] = [xx, left(di, k), yy, hh]
                else:
                    rows[:4] = [add(add(left(d, x), left(R, y), -1), left(r.product(R, w), h)), left(d, k), left(d, y), left(d, add(h, left(z, y), -1))]
                rows[4] = [{}] * 6; rows[5] = [{}] * 6
            else:
                need(kind in ('COMMON_K_FRAME_ENTRY', 'COMMON_K_FRAME_EXIT', 'INHERITED_ALIAS_WORDS'), 'only authenticated common frames/aliases compressed')
        return rows, queries

    fs, ins = p['forward_segments'], p['inverse_segments']
    fwd, fq = replay(fs)
    inv, iq = replay(ins, True)
    J = [[c, r.scale(w, -4)], [r.scale(z, 3), r.monomial(coefficient=13)]]
    need(r.matrix(J, J) == r.identity(2), 'ordered J involution')
    need(r.matrix([[r.scale(z, 3), r.monomial(coefficient=13)]], J) == [[{}, one]], 'old-h row of J')
    full_R = [[R, {}], [{}, R]]
    need(r.matrix(full_R, J) == r.matrix(J, full_R), 'only full R intertwining')
    target = [[{} for _ in range(6)] for _ in range(6)]
    target[0][0] = d; target[1][1] = d; target[0][2] = r.scale(R, -1); target[1][3] = r.scale(R, -1)
    for i in range(2):
        for j in range(2):
            target[i + 2][j + 2] = r.product(d, J[i][j])
    need(fwd == target, 'T=(Du-Rv,DJv), all240+9 columns')
    identity = r.identity(6); identity[4] = [{}] * 6; identity[5] = [{}] * 6
    need(r.matrix(inv, fwd) == identity and r.matrix(fwd, inv) == identity, 'both functional main inverse products')
    need(fq == [[{}, {}, {}, q, {}, {}]] and r.matrix(iq, fwd) == fq, 'forward and recovered inverse query are exact original h')
    need(all(not row[4] and not row[5] for row in fwd + inv) and not any(fwd[4] + fwd[5] + inv[4] + inv[5]), 'all arbitrary9 owned inputs absent and final zero')
    for matrix in (fwd, inv):
        for i, row in enumerate(matrix):
            for j, poly in enumerate(row):
                r.typecheck(poly, ('p', 'h', 'p', 'h', 'h', 'h')[i], ('p', 'h', 'p', 'h', 'h', 'h')[j])
    controls = []
    bad = [s for s in fs if s['label'] != 'output_h_half2']
    need(replay(bad)[0] != fwd, 'half deletion detected'); controls.append('missing_second_half')
    bad = copy.deepcopy(fs); item = bad.pop(0); bad.insert(next(i for i,s in enumerate(bad) if s['label'] == 'forward_alias_pre'), item)
    need(replay(bad)[0] != fwd, 'query version detected'); controls.append('query_encoded_h_instead_of_original_h')
    bad = copy.deepcopy(ins); a = next(i for i,s in enumerate(bad) if s['label'] == 'y_minus_W_hP'); bad[a],bad[a+1] = bad[a+1],bad[a]
    need(r.matrix(replay(bad, True)[0], fwd) != identity, 'recovery order detected'); controls.append('Z_before_updated_y_recovery')
    bad = copy.deepcopy(ins); item = bad.pop(); bad.insert(next(i for i,s in enumerate(bad) if s['label'] == 'common_K_entry'), item)
    need(r.matrix(replay(bad, True)[0], fwd) != identity, 'early inverse query detected'); controls.append('inverse_query_before_old_h_recovery')
    for kind in ('OWNED_SCALAR_LOWERING', 'QUERY_OLD_H'):
        bad = copy.deepcopy(next(s for s in fs if s['kind'] == kind)); bad['operations'] = bad['operations'][1:]
        try:
            episode(bad)
        except ValueError:
            controls.append(kind + '_missing_CLEAR_rejected')
        else:
            raise ValueError('dirty COPY control admitted')
    # Distinct from six producer controls: do not erase the operator order D J.
    jd = [[r.product(J[i][j], d) for j in range(2)] for i in range(2)]
    need(jd != [row[2:4] for row in fwd[2:4]], 'JD is not silently substituted for DJ')
    controls.append('returned_JD_substitution_rejected_in_noncommuting_ring')
    out = {'schema': 'independent-balanced-J-native-result/1', 'status': 'PASS_INDEPENDENT_LITERAL_BOUNDARY_MAIN_INVERSE_UNDER_RETAINED_NATIVE_ABI',
           'packet_sha256': PACKET_SHA, 'checker_sha256': sha(Path(__file__)), 'independent_ring_sha256': ENGINE_SHA,
           'main_original_directions': 240, 'arbitrary_owned_entry_directions': 9,
           'literal_episode_independent_columns': 25, 'source_bindings': binding,
           'all_owned_zero_returns': True, 'both_main_inverse_products': True, 'J_squared_identity': True,
           'only_full_R_intertwining': True, 'returned_V_order': 'D J v',
           'counts_forward': p['forward_counts'], 'counts_inverse': p['inverse_counts'], 'controls': controls,
           'forward_rows': [[r.serialize(a) for a in row] for row in fwd], 'inverse_rows': [[r.serialize(a) for a in row] for row in inv],
           'forward_query_rows': [[r.serialize(a) for a in row] for row in fq], 'inverse_query_rows': [[r.serialize(a) for a in row] for row in iq],
           'helpers': '392 positive C_r in each direction, not helper inverse composition',
           'independence': 'No producer checker/evaluator import; own frozen Ring; every scalar/query instruction interpreted on distinct owner inputs; K/M/aliases checked against pinned records; raw direction ABIs and source phase/allwidth endpoint are retained premises.',
           'expanded_native_word_replayed': False, 'phase_census_replayed': False,
           'optional_current_source_120_queries_installed': False, 'complete_caller': False, 'gain_claimed': False, 'new_kappa': None}
    args.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ('status', 'main_original_directions', 'arbitrary_owned_entry_directions', 'both_main_inverse_products', 'complete_caller')}, sort_keys=True))

if __name__ == '__main__':
    main()
