"""Exact bounded two-sided signed bi-forest U8 compensation construction.

Stephan Arrington (@steph4n-gh) with substantial Google DeepMind Antigravity
assistance, Apache-2.0.
Target forests follow Ross Richardson PR932, dd-hemant PR816, Oscar Fennell
PR759, and ToikY PR901; target dyadic-forest floor follows woklerx PR961;
two-sided helper shears generalize Ross Richardson PR917 and David Awad PR807
from disjoint helper pairs to arbitrary-depth leaf-before-parent helper forests.
This implementation is new; no pending PR code is imported.
"""
from collections import deque
from fractions import Fraction as Q
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier942-audit/t37-replay.tar.gz'
WORDPIN = 'research/gauge44-barch/construction/barch/LOCAL-PINS-barch-U8.json'
SEED = 35
BASE = '2921874911956718fcaaaf9396fe8267b3cfa9f0'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def load():
    pins = read(HERE / 'SOURCES.json')
    require(pins['base_commit'] == BASE, 'base commit pin mismatch')
    for item in pins['files']:
        path = ROOT / item['path']
        raw = path.read_bytes()
        payload = gzip.decompress(raw) if item.get('encoding') == 'gzip' else raw
        require(hashlib.sha256(payload).hexdigest() == item['sha256'],
                'source pin: ' + item['path'])
    archive_path = ROOT / pins['archive']['path']
    data = {}
    with tarfile.open(archive_path, 'r:gz') as archive:
        for member in pins['archive']['members']:
            raw = archive.extractfile(member['name']).read()
            payload = gzip.decompress(raw) if member.get('encoding') == 'gzip' else raw
            require(hashlib.sha256(payload).hexdigest() == member['sha256'],
                    'archive member pin: ' + member['name'])
            key = Path(member['name']).name.split('.')[0]
            data[key] = json.loads(payload)
    w = data['CANONICAL-WORD']
    ps = data['LOCAL-PROGRAMS']
    checks = data['LOCAL-CHECKS']
    inherited = data['INDEPENDENT-LOCAL-REPLAY']['local']
    u8_pins = read(ROOT / WORDPIN)
    selected = read(ROOT / 'certificates/selected-result.json')
    require(selected['kappa'] == '1661960547713947/1000000000000000000'
            and selected['source_prs'][:4] == [942, 890, 870, 869],
            'selected frontier binding mismatch')
    require(u8_pins['canonical_sha256'] == pins['archive']['members'][0]['sha256'],
            'U8 canonical word pin mismatch')
    for orientation in ('forward', 'backward'):
        require(digest(ps[orientation]) == u8_pins['program_sha256'][orientation]
                == checks[orientation]['sha256'],
                'U8 program binding: ' + orientation)
        checks[orientation]['inherited_prefix_upper'] = inherited[orientation]['prefix_l1_upper']
        checks[orientation]['charged_payload_bits'] = inherited[orientation]['charged_payload_bits']
    return w, ps, checks


@lru_cache(None)
def price_quarter(x):
    """Inherited binary-Horner price of the coefficient x/4, in one component."""
    if not x:
        return 0
    a, d = abs(x), 2
    while d and not a % 2:
        a //= 2
        d -= 1
    return 3 + a.bit_length() - 1 + a.bit_count() + d


def matrix(w):
    rows = sorted({e[1] for e in w['compensation']})
    cols = sorted({e[2] for e in w['compensation']})
    require(len(rows) == 112 and len(cols) == 216, 'U8 compensation shape')
    require(rows == list(range(112, 224)), 'U8 target range')
    require(set(rows).isdisjoint(cols), 'disjoint source/target banks')
    require(all(w['start'][r] == 0 for r in rows + cols), 'common frame zero')
    require(all(w['final'][r] == 1 for r in cols), 'helpers must be unwrapped at entry')
    require(all(op[-1] == 0 for op in w['precondition']), 'precondition frame zero')
    ri = {r: i for i, r in enumerate(rows)}
    ci = {c: i for i, c in enumerate(cols)}
    C = [[0] * len(cols) for _ in rows]
    seen = set()
    for tag, target, source, a, b, frame in w['compensation']:
        require(tag == 'add' and frame == 0, 'compensation instruction')
        require((target, source) not in seen, 'duplicate compensation entry')
        seen.add((target, source))
        q = Q(a, b) * 4
        require(q.denominator == 1 and q.numerator != 0, 'quarter-grid compensation')
        C[ri[target]][ci[source]] = q.numerator
    return rows, cols, C


def rowcost(row):
    return sum(map(price_quarter, row))


def apply_target_forest(C, T):
    D = [row[:] for row in C]
    for child, par, sign, _ in T:
        D[child] = [a - sign * b for a, b in zip(C[child], C[par])]
    return D


def apply_helper_forest(D, H):
    E = [row[:] for row in D]
    for child, par, sign, _ in H:
        for i in range(len(E)):
            E[i][child] = D[i][child] - sign * D[i][par]
    return E


def forest(vectors, tag):
    """Kruskal on signed vector differences plus superroot, deterministic ties."""
    n = len(vectors)
    edges = [(rowcost(vectors[i]), -1, i, 0) for i in range(n)]
    for i in range(n):
        vi = vectors[i]
        for j in range(i):
            vj = vectors[j]
            for sign in (-1, 1):
                w = 8 + sum(price_quarter(a - sign * b) for a, b in zip(vi, vj))
                edges.append((w, j, i, sign))
    edges.sort(key=lambda e: (e[0], digest([SEED, list(e)])))
    parent = list(range(n + 1))

    def root(i):
        i += 1
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    chosen = []
    for weight, a, b, sign in edges:
        ar, br = root(a), root(b)
        if ar != br:
            parent[ar] = br
            chosen.append([weight, a, b, sign])
            if len(chosen) == n:
                break
    adj = {i: [] for i in range(-1, n)}
    for weight, a, b, sign in chosen:
        adj[a].append((b, sign))
        adj[b].append((a, sign))
    visited = {-1}
    queue = deque([(-1, 0)])
    oriented = []
    while queue:
        a, depth = queue.popleft()
        for b, sign in sorted(adj[a]):
            if b not in visited:
                visited.add(b)
                queue.append((b, depth + 1))
                if a != -1:
                    oriented.append([b, a, sign, depth])
    require(len(visited) == n + 1, 'forest connectivity')
    oriented.sort(key=lambda x: (-x[3], x[0], x[1]))
    transformed = [v[:] for v in vectors]
    for child, par, sign, _ in oriented:
        transformed[child] = [a - sign * b for a, b in zip(vectors[child], vectors[par])]
    total = sum(e[0] for e in chosen)
    require(total == sum(map(rowcost, transformed)) + 8 * len(oriented), 'forest pricing')
    max_depth = max((x[3] for x in oriented), default=0)
    return oriented, transformed, {
        'tag': tag,
        'edges': len(edges),
        'forest_edges': len(oriented),
        'roots': n - len(oriented),
        'max_depth': max_depth,
        'price': total,
        'chosen': chosen,
        'census_sha256': digest(edges),
    }


def disjoint_helper_pairs(D):
    """PR917-style disjoint helper-pair comparator evaluated on D = T_0 C."""
    columns = list(map(list, zip(*D)))
    n = len(columns)
    costs = list(map(rowcost, columns))
    census = hashlib.sha256()
    profitable = []
    count = 0
    for a in range(n):
        ca = columns[a]
        for b in range(n):
            if a == b:
                continue
            cb = columns[b]
            for sign in (-1, 1):
                gain = costs[b] - rowcost([v - sign * u for u, v in zip(ca, cb)]) - 8
                rec = [a, b, sign, gain]
                census.update(canonical(rec) + b'\n')
                count += 1
                if gain > 0:
                    profitable.append(rec)
    profitable.sort(key=lambda x: (-x[3], digest([SEED, x])))
    used = set()
    selected = []
    for a, b, sign, gain in profitable:
        if a not in used and b not in used:
            used.update((a, b))
            selected.append([a, b, sign, gain])
    E = [row[:] for row in D]
    for a, b, sign, _gain in selected:
        for row in E:
            row[b] -= sign * row[a]
    actual_gain = sum(map(rowcost, D)) - sum(map(rowcost, E)) - 8 * len(selected)
    require(actual_gain == sum(x[3] for x in selected), 'disjoint helper gains')
    return selected, E, {
        'cases': count,
        'profitable': len(profitable),
        'selected_pairs': len(selected),
        'census_sha256': census.hexdigest(),
        'gain': actual_gain,
    }


def addition(target, source, q):
    q = Q(q)
    require(target != source and q, 'invalid addition')
    return ['add', target, source, q.numerator, q.denominator, 0]


def emit_biforest_panel(targets, sources, T, H, E):
    # Target forest preparation: y[c] -= s * y[p] in deepest-first (leaf-before-parent) order.
    prepT = [addition(targets[c], targets[p], -s) for c, p, s, _ in T]
    # Helper forest preparation: h[p] += s * h[c] in deepest-first (leaf-before-parent) order.
    # Because every child c finishes accumulating from its own descendants before donating
    # into h[p], H^-1 has zero ancestor cross-terms and replaces column c by D_c - s * D_p.
    prepH = [addition(sources[p], sources[c], s) for c, p, s, _ in H]
    residual = [
        addition(t, sources[j], Q(x, 4))
        for t, row in zip(targets, E)
        for j, x in enumerate(row)
        if x
    ]

    def inverse(es):
        return [addition(e[1], e[2], -Q(e[3], e[4])) for e in reversed(es)]

    return prepT + prepH + residual + inverse(prepH) + inverse(prepT)


def construct(w):
    targets, sources, C = matrix(w)
    baseline_price = sum(map(rowcost, C))
    T0, D0, tree0 = forest(C, 'T0')
    pairs0, E_pairs0, pair_meta = disjoint_helper_pairs(D0)
    disjoint_pair_price = sum(map(rowcost, E_pairs0)) + 8 * (len(T0) + len(pairs0))
    require(disjoint_pair_price == tree0['price'] - pair_meta['gain'],
            'disjoint pair comparator price')

    trajectory = [{
        'step': 'T0',
        'kind': 'target_forest',
        'target_edges': len(T0),
        'helper_edges': 0,
        'residual_price': sum(map(rowcost, D0)),
        'total_panel_price': tree0['price'],
    }]

    T_cur = T0
    D_cur = D0
    H_cur = []
    treeH_first = None
    treeT_final = None
    treeH_final = None

    for iteration in range(1, 6):
        cols_D = list(map(list, zip(*D_cur)))
        H_next, cols_E, treeH = forest(cols_D, f'H{iteration}')
        if iteration == 1:
            treeH_first = treeH
        E_cur = list(map(list, zip(*cols_E)))
        price_after_H = treeH['price'] + 8 * len(T_cur)
        require(price_after_H == sum(map(rowcost, E_cur)) + 8 * (len(T_cur) + len(H_next)),
                'bi-forest H pricing')
        trajectory.append({
            'step': f'H{iteration}',
            'kind': 'helper_forest',
            'target_edges': len(T_cur),
            'helper_edges': len(H_next),
            'residual_price': sum(map(rowcost, E_cur)),
            'total_panel_price': price_after_H,
        })
        H_cur = H_next

        C_right = apply_helper_forest(C, H_cur)
        T_next, E_after_T, treeT = forest(C_right, f'T{iteration}')
        price_after_T = treeT['price'] + 8 * len(H_cur)
        require(price_after_T == sum(map(rowcost, E_after_T)) + 8 * (len(T_next) + len(H_cur)),
                'bi-forest T pricing')
        trajectory.append({
            'step': f'T{iteration}',
            'kind': 'target_forest',
            'target_edges': len(T_next),
            'helper_edges': len(H_cur),
            'residual_price': sum(map(rowcost, E_after_T)),
            'total_panel_price': price_after_T,
        })
        T_cur = T_next
        D_cur = apply_target_forest(C, T_cur)
        treeT_final = treeT
        treeH_final = treeH

    E_final = apply_helper_forest(D_cur, H_cur)
    final_price = sum(map(rowcost, E_final)) + 8 * (len(T_cur) + len(H_cur))
    # Verify coordinate-wise fixed point: neither side can strictly improve 7,930.
    _, _, check_H = forest(list(map(list, zip(*D_cur))), 'H_fixed_check')
    require(check_H['price'] + 8 * len(T_cur) == final_price,
            'H5 is not coordinate-wise minimal for T5')
    require(treeT_final['price'] + 8 * len(H_cur) == final_price,
            'T5 is not coordinate-wise minimal for H5')

    panel = emit_biforest_panel(targets, sources, T_cur, H_cur, E_final)
    residual_additions = sum(1 for row in E_final for x in row if x)
    require(len(panel) == residual_additions + 2 * (len(T_cur) + len(H_cur)),
            'panel addition count')

    recipe = {
        'seed': SEED,
        'targets': targets,
        'sources': sources,
        'initial_target_forest': T0,
        'initial_target_search': {
            'edges': tree0['edges'],
            'forest_edges': tree0['forest_edges'],
            'roots': tree0['roots'],
            'max_depth': tree0['max_depth'],
            'price': tree0['price'],
            'census_sha256': tree0['census_sha256'],
        },
        'disjoint_helper_comparator': {
            **pair_meta,
            'panel_price': disjoint_pair_price,
            'pairs': pairs0,
        },
        'one_pass_helper_search': {
            'edges': treeH_first['edges'],
            'forest_edges': treeH_first['forest_edges'],
            'roots': treeH_first['roots'],
            'max_depth': treeH_first['max_depth'],
            'panel_price': treeH_first['price'] + 8 * len(T0),
            'census_sha256': treeH_first['census_sha256'],
        },
        'alternating_trajectory': trajectory,
        'target_forest': T_cur,
        'helper_forest': H_cur,
        'fixed_point_target_search': {
            'edges': treeT_final['edges'],
            'forest_edges': treeT_final['forest_edges'],
            'roots': treeT_final['roots'],
            'max_depth': treeT_final['max_depth'],
            'price_with_helpers': final_price,
            'census_sha256': treeT_final['census_sha256'],
        },
        'fixed_point_helper_search': {
            'edges': treeH_final['edges'],
            'forest_edges': treeH_final['forest_edges'],
            'roots': treeH_final['roots'],
            'max_depth': treeH_final['max_depth'],
            'price_with_targets': final_price,
            'census_sha256': check_H['census_sha256'],
        },
        'baseline_panel_price': baseline_price,
        'target_only_panel_price': tree0['price'],
        'disjoint_pair_panel_price': disjoint_pair_price,
        'one_pass_biforest_panel_price': treeH_first['price'] + 8 * len(T0),
        'two_sided_biforest_panel_price': final_price,
        'baseline_additions': len(w['compensation']),
        'candidate_additions': len(panel),
        'residual_additions': residual_additions,
        'residual_quarters_sha256': digest(E_final),
        'panel_sha256': digest(panel),
    }
    require(recipe['baseline_panel_price'] > recipe['target_only_panel_price']
            > recipe['disjoint_pair_panel_price'] > recipe['one_pass_biforest_panel_price']
            > recipe['two_sided_biforest_panel_price'], 'strict stage progression failed')
    return panel, recipe


def scalar(e, backward):
    _, t, s, a, b, _ = e
    if backward:
        t, s, a = s, t, -a
    return ['scalar', ['add', ['L', t], ['L', s], a, b], 0]


def replace_programs(w, original, panel):
    result = {}
    begin = 1 + len(w['precondition'])
    end = begin + len(w['compensation'])
    for name, events in original.items():
        require(events[0] == ['phase', 'zero_frame_precondition'], 'program phase')
        require(events[end] == ['phase', 'entry_adapters'], 'compensation boundary')
        require(events[begin:end] == [scalar(e, name == 'backward') for e in w['compensation']],
                'literal compensation binding')
        result[name] = (events[:begin]
                        + [scalar(e, name == 'backward') for e in panel]
                        + events[end:])
        require([e for e in events if e[0] != 'scalar'] ==
                [e for e in result[name] if e[0] != 'scalar'],
                'non-scalar preservation')
    return result


def lower(op):
    """Literal inherited (unoptimized) binary Horner with dirty work erased."""
    tag, target = op[0], tuple(op[1])
    work = ('W', 0)
    require(target != work, 'work aliases target')
    if tag == 'clear':
        return [('clear', target)]
    if tag == 'copy':
        return [('copy', target, tuple(op[2]))]
    if tag == 'scale':
        q = Q(op[2], op[3])
        a, b = abs(q.numerator), q.denominator
        require(a and a & (a - 1) == 0 and b & (b - 1) == 0,
                'scale not signed power of two')
        shift = a.bit_length() - b.bit_length()
        return ([('double' if shift > 0 else 'halve', target)] * abs(shift)
                + ([('negate', target)] if q < 0 else []))
    require(tag == 'add', 'unknown scalar operation')
    source = tuple(op[2])
    q = Q(op[3], op[4])
    a, b = abs(q.numerator), q.denominator
    require(source not in (target, work) and q and b & (b - 1) == 0,
            'invalid dyadic add')
    ops = [('clear', work)]
    for i, bit in enumerate(bin(a)[2:]):
        if i:
            ops.append(('double', work))
        if bit == '1':
            ops.append(('add', work, source, 1))
    ops += [('halve', work)] * (b.bit_length() - 1)
    ops += [('add', target, work, 1 if q > 0 else -1), ('clear', work)]
    return ops


def primitives(events):
    for event in events:
        if event[0] == 'scalar':
            yield from lower(event[1])


def fraction_replay(events, n=728, centers=8):
    """Fresh full arbitrary-input scalar projection; nonscalars checked separately."""
    refs = [('L', i) for i in range(n)] + [('C', i) for i in range(centers)] + [('W', 0)]
    state = {r: {i: Q(1)} for i, r in enumerate(refs)}
    env = {r: Q(1) for r in refs}
    peak = Q(1)
    count = 0
    grid = 0
    for op in primitives(events):
        tag, t = op[:2]
        count += 1
        if tag == 'clear':
            state[t] = {}
            env[t] = Q(0)
        elif tag == 'copy':
            state[t] = dict(state[op[2]])
            env[t] = env[op[2]]
        elif tag in ('double', 'halve', 'negate'):
            q = {'double': Q(2), 'halve': Q(1, 2), 'negate': Q(-1)}[tag]
            state[t] = {i: q * x for i, x in state[t].items()}
            env[t] *= abs(q)
        else:
            _, _, s, sign = op
            env[t] += env[s]
            for i, x in list(state[s].items()):
                value = state[t].get(i, Q(0)) + sign * x
                if value:
                    state[t][i] = value
                else:
                    state[t].pop(i, None)
        peak = max(peak, env[t])
        grid = max(grid, max((x.denominator.bit_length() - 1 for x in state[t].values()), default=0))
    return state, {
        'real_primitives': 2 * count,
        'prefix_l1': str(peak),
        'prefix_bits': peak.numerator.bit_length() - peak.denominator.bit_length() + 1,
        'maximum_denominator_power': grid,
    }


def endpoint(state, backward, n=728, v=112):
    for i in range(n):
        expected = {i: Q(1)}
        if backward and i < v:
            expected[v + i] = Q(-1)
        if not backward and v <= i < 2 * v:
            expected[i - v] = Q(1)
        require(state['L', i] == expected, 'endpoint logical row ' + str(i))
    require(all(not row for r, row in state.items() if r[0] != 'L'),
            'private input not cleared')
