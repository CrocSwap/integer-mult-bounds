#!/usr/bin/env python3
"""Build two shear words on the retained independent native paths."""

from collections import Counter, defaultdict, deque
from copy import deepcopy
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
CORE = LANES / 'new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz'
NATIVE = LANES / 'new-native-recipes-20261017'
COMPILER = NATIVE / 'sources/vendor/clifford/clifford_exact.py'
PINS = {
    'core_decompressed': 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa',
    'compiler': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
    'native_freeze': '928c29f5949cddafa3510fe0f95c8b400022ee37410d512c2dcef207bfda2f27',
}


def need(test, message):
    if not test:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def pin_sources():
    raw = gzip.decompress(CORE.read_bytes())
    need(sha256(raw).hexdigest() == PINS['core_decompressed'], 'Core input pin')
    need(digest(COMPILER) == PINS['compiler'], 'Exact compiler pin')
    need(digest(NATIVE / 'FREEZE.json') == PINS['native_freeze'], 'Native freeze pin')
    spec = importlib.util.spec_from_file_location('skeleton_clifford', COMPILER)
    module = importlib.util.module_from_spec(spec)
    # dataclass reads the module registry when it resolves a field type.
    import sys
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return json.loads(raw), module


def keep(event):
    return event[0] != 'scalar' or event[1][0] == 'clear'


def push_word(word, symbol):
    if word and word[-1] == -symbol:
        word.pop()
    else:
        word.append(symbol)


def scan(word, events):
    frames = list(word['start'])
    histories = [[] for _ in frames]
    direct, equal_rank = {}, {}
    active = False
    first, last = None, None
    for index, event in enumerate(events):
        tag = event[0]
        if event[:2] == ['phase', 'A']:
            active, first = True, index + 1
        elif event[:2] == ['phase', 'exit_adapters']:
            active, last = False, index
        if tag == 'climb':
            target, old, new, rank = event[2:6]
            need(frames[target] == old, 'Original climb frame')
            need(len(word['frames'][new]) - len(word['frames'][old]) == rank, 'Original climb rank')
            frames[target] = new
        elif tag == 'warp':
            token, symbol, old, new = event[1:5]
            need(token[0] == 'L', 'All retained warps act on live roles')
            target = token[1]
            need(frames[target] == old, 'Original warp frame')
            frames[target] = new
            push_word(histories[target], symbol)
        if not active or tag not in ('phase', 'climb', 'warp'):
            continue
        target_ranks = defaultdict(list)
        for t in range(112):
            target_ranks[len(word['frames'][frames[112 + t]])].append(t)
        for s in range(112):
            u = frames[s]
            rank = len(word['frames'][u])
            if not 1 <= rank <= 8:
                continue
            for t in target_ranks[rank]:
                v = frames[112 + t]
                record = {
                    'source': s, 'target': t, 'original_cut': index + 1,
                    'source_frame': u, 'target_frame': v, 'rank': rank,
                    'source_prefix_warps': list(histories[s]),
                    'target_prefix_warps': list(histories[112 + t]),
                }
                if u == v:
                    direct.setdefault((s, t), record)
                if not histories[s] and not histories[112 + t]:
                    equal_rank.setdefault((s, t), record)
    need(frames == word['final'], 'Original final frames')
    need(all(not h for h in histories), 'Every signed warp word cancels')
    need(first is not None and last is not None, 'Canonical interval')
    return direct, equal_rank, first, last


def matching(graph, prefer_diagonal=False):
    adjacency = {s: sorted(t for a, t in graph if a == s) for s in range(112)}
    left = {s: s for s in range(112) if prefer_diagonal and (s, s) in graph}
    right = {t: s for s, t in left.items()}
    for start in range(112):
        if start in left:
            continue
        queue = deque([start])
        seen_left, predecessor = {start}, {}
        end = None
        while queue and end is None:
            s = queue.popleft()
            for t in adjacency[s]:
                if t in predecessor:
                    continue
                predecessor[t] = s
                if t not in right:
                    end = t
                    break
                next_s = right[t]
                if next_s not in seen_left:
                    seen_left.add(next_s)
                    queue.append(next_s)
        if end is None:
            continue
        t = end
        while True:
            s = predecessor[t]
            old_t = left.get(s)
            left[s], right[t] = t, s
            if old_t is None:
                break
            t = old_t
    # An alternating reachability set gives a vertex cover of the same size.
    seen_left = set(range(112)) - set(left)
    seen_right = set()
    queue = deque(seen_left)
    while queue:
        s = queue.popleft()
        for t in adjacency[s]:
            if left.get(s) == t or t in seen_right:
                continue
            seen_right.add(t)
            if t in right and right[t] not in seen_left:
                seen_left.add(right[t])
                queue.append(right[t])
    cover_left = set(range(112)) - seen_left
    need(all(s in cover_left or t in seen_right for s, t in graph), 'Matching vertex cover')
    need(len(cover_left) + len(seen_right) == len(left), 'Matching and cover sizes')
    return left, {'source_vertices': sorted(cover_left), 'target_vertices': sorted(seen_right)}


def kop(ce, columns):
    rows = ce.transpose(tuple(columns), 9)
    inverse_transpose = ce.transpose(ce.inv(rows, 9), 9)
    quadratic = tuple((1 << i) ^ sum(ce.parity(x & y) << j
                      for j, y in enumerate(inverse_transpose))
                      for i, x in enumerate(inverse_transpose))
    return ce.perm(9, rows).then(ce.diag(9, quadratic))


def equal(a, b):
    return a.tab == b.tab and a.zero_state() == b.zero_state()


def circuit_columns(circuit):
    out = []
    for source in range(512):
        address, phase = source, 0
        for event in circuit:
            tag = event[0]
            if tag == 'P':
                address = sum(((row & address).bit_count() & 1) << i
                              for i, row in enumerate(event[1]))
            elif tag == 'X':
                address ^= event[1]
            elif tag == 'D':
                quadratic, linear = event[1:]
                phase += sum(linear[i] for i in range(9) if address >> i & 1)
                phase += 2 * sum(((quadratic[i] >> (i + 1)) & (address >> (i + 1))).bit_count()
                                 for i in range(9) if address >> i & 1)
            else:
                need(tag == 'phase', 'A monomial circuit has no Fourier gate')
                phase += event[1]
        out.append((address, phase % 4))
    return out


def recipe_columns(recipe):
    out = []
    for source in range(512):
        phase = recipe['phase'] + sum(recipe['linear_Z4'][i] for i in range(9) if source >> i & 1)
        phase += 2 * sum(((recipe['quadratic_rows'][i] >> (i + 1)) & (source >> (i + 1))).bit_count()
                         for i in range(9) if source >> i & 1)
        address = recipe['offset'] ^ sum(((row & source).bit_count() & 1) << i
                                        for i, row in enumerate(recipe['matrix_rows']))
        out.append((address, phase % 4))
    return out


def monomial_record(ce, op):
    compiled, recipe = ce.monomial(op)
    need(equal(compiled, op), 'Exact monomial table and phase')
    need(circuit_columns(op.circuit) == recipe_columns(recipe), 'All 512 monomial columns')
    return {'recipe': recipe, 'circuit': op.circuit}


def make_edges(ce, word, graph, chosen):
    records = []
    full = ce.fourier(9)
    for s, t in sorted(chosen.items()):
        record = deepcopy(graph[s, t])
        u, v, rank = record['source_frame'], record['target_frame'], record['rank']
        ub, vb = word['frames'][u], word['frames'][v]
        ku = kop(ce, ce.basis_extend(ub, 9))
        kv = kop(ce, ce.basis_extend(vb, 9))
        tu, tv = ce.canonical_frame(9, ub), ce.canonical_frame(9, vb)
        hr = ce.fourier(9, range(rank))
        need(equal(ku.adjoint().then(hr).then(ku), tu), 'Actual source frame factorization')
        need(equal(kv.adjoint().then(hr).then(kv), tv), 'Actual target frame factorization')
        p = ku.adjoint().then(kv)
        need(equal(tu.then(p), p.then(tv)), 'Exact physical and logical intertwining')
        positive, negative = monomial_record(ce, p), monomial_record(ce, p.adjoint())
        table, inverse = recipe_columns(positive['recipe']), recipe_columns(negative['recipe'])
        need(all(inverse[j] == (i, (-phase) % 4) for i, (j, phase) in enumerate(table)), 'All reciprocal columns')
        full_product = full.adjoint().then(p).then(full)
        full_compiled, full_recipe = ce.monomial(full_product)
        need(equal(full_compiled, full_product), 'FULL response view is monomial')
        wrong = dict(positive['recipe'], phase=(positive['recipe']['phase'] + 1) % 4)
        need(recipe_columns(wrong) != table, 'Wrong global phase is rejected')
        record.update({
            'view_id': s, 'source_frame_basis': ub, 'target_frame_basis': vb,
            'source_factor_columns': ce.basis_extend(ub, 9),
            'target_factor_columns': ce.basis_extend(vb, 9),
            'positive': positive, 'negative': negative,
            'response': positive, 'inverse_response': negative,
            'full_conjugate_response': {'recipe': full_recipe, 'circuit': full_compiled.circuit},
        })
        records.append(record)
    return records


def emit(events, edges, direction):
    by_cut = defaultdict(list)
    for edge in edges:
        by_cut[edge['original_cut']].append(edge)
    out = []
    for index, event in enumerate(events):
        if keep(event):
            out.append(deepcopy(event))
        for edge in by_cut[index + 1]:
            s, t, u, v = (edge[k] for k in ('source', 'target', 'source_frame', 'target_frame'))
            identifier = edge['view_id']
            if direction == 'forward':
                out.extend([
                    ['monomial_view', ['L', s], identifier, 1, u, v],
                    ['scalar', ['add', ['L', 112 + t], ['L', s], 1, 1], v],
                    ['monomial_view', ['L', s], identifier, -1, v, u],
                ])
            else:
                out.extend([
                    ['monomial_view', ['L', 112 + t], identifier, -1, v, u],
                    ['scalar', ['add', ['L', s], ['L', 112 + t], -1, 1], u],
                    ['monomial_view', ['L', 112 + t], identifier, 1, u, v],
                ])
    need(set(by_cut) <= set(range(1, len(events) + 1)), 'All transfer cuts are emitted')
    return out


def left_operator(row, kind, identifier, power):
    out = {}
    token = (kind, identifier, power)
    inverse = (kind, identifier, -power)
    for (source, operators), coefficient in row.items():
        changed = operators[1:] if operators and operators[0] == inverse else (token,) + operators
        out[source, changed] = coefficient
    return out


def replay(events, word, edges):
    n = len(word['start'])
    state = {p: {(p, ()): 1} for p in range(n + 8)}
    frames = dict(enumerate(word['start']))
    frames.update({n + p: 0 for p in range(8)})
    active_zeros = set()
    edge_map = {e['view_id']: e for e in edges}
    def slot(token):
        kind, index = token
        if kind == 'L':
            need(0 <= index < n, 'Live role range')
            return index
        if kind == 'C':
            need(0 <= index < 8, 'Owned role range')
            return n + index
        need(kind == 'Z', 'Private role namespace')
        return ('Z', index)
    for event in events:
        tag = event[0]
        if tag == 'scalar':
            gate, frame = event[1:]
            target = slot(gate[1])
            if gate[0] == 'clear':
                need(target == n, 'Only original owned C0 is cleared')
                state[target], frames[target] = {}, frame
            else:
                need(gate[0] == 'add' and gate[3] in (-1, 1) and gate[4] == 1, 'Only unit transfers remain')
                source = slot(gate[2])
                need(source != target and frames[source] == frames[target] == frame, 'Equal-frame transfer')
                for key, coefficient in state[source].items():
                    state[target][key] = state[target].get(key, 0) + gate[3] * coefficient
                    if not state[target][key]:
                        del state[target][key]
        elif tag == 'climb':
            target, old, new, rank = event[2:6]
            need(frames[target] == old, 'Retained native source frame')
            need(len(word['frames'][new]) - len(word['frames'][old]) == rank, 'Retained child rank')
            frames[target] = new
        elif tag == 'warp':
            target, symbol, old, new = slot(event[1]), event[2], event[3], event[4]
            need(frames[target] == old, 'Retained warp source frame')
            frames[target] = new
            state[target] = left_operator(state[target], 'K', abs(symbol), 1 if symbol > 0 else -1)
        elif tag == 'monomial_view':
            target, identifier, power, old, new = slot(event[1]), *event[2:]
            edge = edge_map[identifier]
            pair = (edge['source_frame'], edge['target_frame'])
            need((old, new) == (pair if power == 1 else pair[::-1]), 'View has the checked frames')
            need(frames[target] == old, 'View source frame')
            frames[target] = new
            state[target] = left_operator(state[target], 'P', identifier, power)
        elif tag == 'zero_buffer':
            target = ('Z', event[2])
            if event[1] == 'alloc':
                need(target not in active_zeros, 'Private zero allocation')
                state[target], frames[target] = {}, 1
                active_zeros.add(target)
            else:
                need(target in active_zeros and not state[target], 'Private zero restoration')
                active_zeros.remove(target)
        else:
            need(tag in ('phase', 'adapter', 'residual_adapter'), 'Known complete event')
    need(not active_zeros, 'No private zero role remains live')
    need([frames[p] for p in range(n)] == word['final'], 'Every live endpoint frame')
    need(all(frames[n + p] == 0 for p in range(8)), 'Owned endpoint frames')
    return state


def check_endpoint(state, n, edges, direction):
    wanted = {p: {(p, ()): 1} for p in range(n + 8)}
    wanted[n] = {}
    for e in edges:
        s, t, identifier = e['source'], e['target'], e['view_id']
        if direction == 'forward':
            wanted[112 + t][s, (('P', identifier, 1),)] = 1
        else:
            wanted[s][112 + t, (('P', identifier, -1),)] = -1
    need(all(state[p] == wanted[p] for p in range(n + 8)), 'All arbitrary input columns')
    need(all(not row for p, row in state.items() if isinstance(p, tuple)), 'All private zero columns')


def verify_native_dependencies(provider, word):
    directory = NATIVE / provider
    receipt_path = directory / 'GENERATION-RECEIPT.json'
    receipt = json.loads(receipt_path.read_text())
    need(receipt['status'] == 'PASS_FRESH_SOURCE_NATIVE_RECIPES', 'Native generation status')
    for name, pin in receipt['output_sha256'].items():
        need(digest(directory / name) == pin, 'Native recipe pin: ' + name)
    canonical = json.loads(gzip.decompress((directory / 'CANONICAL-WORD.json.gz').read_bytes()))
    for key in ('frames', 'start', 'final', 'warps', 'warp_edges'):
        need(canonical[key] == word[key], 'Native canonical field: ' + key)
    residuals = json.loads((directory / 'RESIDUAL-ADAPTERS.json').read_text())
    classes = {(word['start'][p], word['final'][p]) for p in range(224, len(word['start']))}
    for start, final in classes:
        if final != 1:
            need(f'{start}:{final}' in residuals['recipes'], 'Proper helper residual recipe')
    return {'generation_receipt_sha256': digest(receipt_path),
            'recipe_sha256': receipt['output_sha256'],
            'helper_endpoint_classes': [list(x) for x in sorted(classes)]}


def main():
    core, ce = pin_sources()
    payload = {'schema': 'independent-native-monomial-shears-v1', 'source_pins': PINS,
               'warp_convention': 'Use the retained forward signed K implementation in both directions.',
               'providers': {}}
    receipt = {'status': 'PASS_INDEPENDENT_NATIVE_MONOMIAL_SHEARS', 'providers': {}}
    for provider, item in core['providers'].items():
        word, original = item['canonical'], item['programs']
        need(len(word['start']) == 632 and len(word['zero_buffers']) == 91, 'Original live and private stock')
        skeleton = [e for e in original['forward'] if keep(e)]
        need(skeleton == [e for e in original['backward'] if keep(e)], 'Both stripped skeletons are byte-equal')
        native = verify_native_dependencies(provider, word)
        direct, candidates, first, last = scan(word, original['forward'])
        direct_match, direct_cover = matching(direct)
        chosen, cover = matching(candidates, prefer_diagonal=True)
        need(len(chosen) == 112, 'Complete equal-rank matching')
        edges = make_edges(ce, word, candidates, chosen)
        programs = {direction: emit(original[direction], edges, direction)
                    for direction in ('forward', 'backward')}
        for direction, events in programs.items():
            state = replay(events, word, edges)
            check_endpoint(state, 632, edges, direction)
            retained = [e for e in events if e[0] != 'monomial_view' and not (e[0] == 'scalar' and e[1][0] == 'add')]
            need(retained == skeleton, 'Every retained native event and wrapper is unchanged')
        profile = Counter(e[5] for e in skeleton if e[0] == 'climb')
        need(dict(profile) == {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20}, 'Native child profile')
        need(sum(k * v for k, v in profile.items()) == 5073, 'Native rank mass')
        scalar_count = Counter(e[1][0] for e in programs['forward'] if e[0] == 'scalar')
        need(dict(scalar_count) == {'clear': 16, 'add': 112}, 'Complete scalar event count')
        # The first malformed view must fail before a transfer can use it.
        bad = deepcopy(programs['forward'])
        position = next(i for i, e in enumerate(bad) if e[0] == 'monomial_view')
        bad[position][4] = -1
        rejected = False
        try:
            replay(bad, word, edges)
        except ValueError:
            rejected = True
        need(rejected, 'Wrong view frame is rejected')
        bad = deepcopy(programs['backward'])
        position = next(i for i, e in enumerate(bad) if e[0] == 'scalar' and e[1][0] == 'add')
        bad[position][1][3] = 1
        rejected = False
        try:
            check_endpoint(replay(bad, word, edges), 632, edges, 'backward')
        except ValueError:
            rejected = True
        need(rejected, 'Wrong backward sign is rejected')
        payload['providers'][provider] = {
            'canonical': word, 'native_dependencies': native, 'canonical_cut_range': [first, last],
            'direct_equal_frame_graph': {'edges': [list(x) for x in sorted(direct)],
                                         'matching': sorted(map(list, direct_match.items())), 'vertex_cover': direct_cover},
            'equal_rank_zero_warp_graph': {'edges': [list(x) for x in sorted(candidates)],
                                           'matching': sorted(map(list, chosen.items())), 'vertex_cover': cover},
            'transfers': edges, 'programs': programs,
        }
        receipt['providers'][provider] = {
            'live_roles': 632, 'arbitrary_helper_roles': 408, 'owned_C_roles': 8, 'private_zero_roles': 91,
            'arbitrary_symbolic_columns_per_word': 640, 'complete_words': 2,
            'direct_equal_frame_edges': len(direct), 'direct_maximum_matching': len(direct_match),
            'equal_rank_empty_warp_edges': len(candidates), 'chosen_matching_size': len(edges),
            'chosen_diagonal_ports': sum(e['source'] == e['target'] for e in edges),
            'selected_ranks': dict(sorted(Counter(e['rank'] for e in edges).items())),
            'all_net_warp_words_empty': True, 'all_selected_prefix_warp_words_empty': True,
            'exact_intertwining_checks': 112, 'explicit_monomial_column_checks': 112 * 512 * 2,
            'full_conjugated_response_rank_zero': True,
            'native_child_profile': dict(sorted(profile.items())), 'native_children': sum(profile.values()),
            'native_rank_mass': 5073, 'retained_warp_events': 240,
            'retained_endpoint_adapters': sum(e[0] == 'adapter' for e in skeleton),
            'retained_residual_adapters': sum(e[0] == 'residual_adapter' for e in skeleton),
            'retained_private_allocations': sum(e[:2] == ['zero_buffer', 'alloc'] for e in skeleton),
            'new_complex_monomial_array_maps': 224, 'new_unit_complex_ADDs': 112,
            'retained_complex_CLEARs': 16, 'top_level_real_scalar_bound': 928,
            'additional_native_children': 0, 'additional_private_arrays': 0,
            'controls': ['Wrong global phase', 'Wrong view frame', 'Wrong backward ADD sign'],
        }
        print(provider, 'PASS', receipt['providers'][provider], flush=True)
    raw = encoded(payload)
    (HERE / 'INDEPENDENT-SKELETON-PROGRAMS.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    receipt['payload_decompressed_sha256'] = sha256(raw).hexdigest()
    receipt['producer_sha256'] = digest(Path(__file__))
    receipt['source_pins'] = PINS
    receipt['scope'] = ('Two local shear words with a unitary monomial block response. '
                        'No global controller, owner reassignment, precision invoice, or complete kappa claim.')
    (HERE / 'INDEPENDENT-SKELETON.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    main()
