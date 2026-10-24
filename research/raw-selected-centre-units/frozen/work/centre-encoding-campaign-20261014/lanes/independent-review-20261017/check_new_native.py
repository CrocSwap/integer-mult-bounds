"""Check new-core native recipes with a separate exact interpreter."""

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import resource
import time


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
SOURCE = LANES / 'new-native-recipes-20261017'
INTERPRETER = LANES / 'interface-proof/verify_native_lift.py'
INTERPRETER_PIN = '087ad4cc683e5caf1f2a8cd62d5f65c9b4dde2636593b417f8f5099a29875c8b'
CLEAN = LANES / 'new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz'
CLEAN_PIN = 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa'
PINS = {
    'base': {
        'CANONICAL-WORD.json.gz': 'bd6f84f6e7be075064f04e6141568d295631a3feab1efa75ff0326e6efa4f472',
        'LOCAL-PROGRAMS.json.gz': '4048b4494793f31c6c9ce85a7de584c53cafae0cd5c119eb1084b221cfe04ad9',
        'CLIFFORD-RECIPES.json': '580dee1ca6d0a2971bc1dbe93558b8331bfa61662ce1736b24d944a55127b4f0',
        'RESIDUAL-ADAPTERS.json': '8a6130051284adf76ec932bc2a190058cc99efbed5d862bee819e3bc8c29a31b',
        'LITERAL-DUAL-WARP-RECIPES.json': 'e880f4e6ff6308675b766bfa63d472c1050b01f17fac78f8810b04eedc6e0a6e',
    },
    'extra': {
        'CANONICAL-WORD.json.gz': '1cf1714fc2a26c18b2b380827054246550c1402fde379745f626ff61f4ee6224',
        'LOCAL-PROGRAMS.json.gz': '4048b4494793f31c6c9ce85a7de584c53cafae0cd5c119eb1084b221cfe04ad9',
        'CLIFFORD-RECIPES.json': 'f3c678f44ac8c116376d707b088516b0c17744a8508f2863843b912738d2024e',
        'RESIDUAL-ADAPTERS.json': 'dd8d70e07ae6ecc028d7691611966fcaee946279964736997af0aa78c61c2282',
        'LITERAL-DUAL-WARP-RECIPES.json': '0bafa16eea7a49af963346117cf61ca638859748752d5f0ed47a18fe6c4594ff',
    },
}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def pinned(path, pin):
    raw = path.read_bytes()
    if path.suffix == '.gz':
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, 'Input pin: ' + str(path))
    return json.loads(raw)


def rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            p = value.bit_length() - 1
            if p not in pivots:
                pivots[p] = value
                break
            value ^= pivots[p]
    return len(pivots)


def raw_k(columns, native, dual=False):
    matrix = native.transpose(tuple(columns))
    columns_inverse = native.transpose(native.inverse(matrix))
    quadratic = tuple((1 << i) ^ sum(native.parity(a & b) << j
                      for j, b in enumerate(columns_inverse))
                      for i, a in enumerate(columns_inverse))
    linear = tuple(((-1 if dual else 1) * ((row >> i) & 1)) % 4
                   for i, row in enumerate(quadratic))
    return (('P', matrix), ('D', quadratic, linear))


def fields(event):
    if event[0] == 'warp':
        return [tuple(event[1])]
    if event[0] == 'scalar':
        return [tuple(x) for x in event[1][1:] if isinstance(x, list)]
    return []


def review(provider, native, clean):
    started = time.monotonic()
    data = {name: pinned(SOURCE / provider / name, pin) for name, pin in PINS[provider].items()}
    c = data['CANONICAL-WORD.json.gz']
    original = data['LOCAL-PROGRAMS.json.gz']
    phase = data['CLIFFORD-RECIPES.json']
    residual = data['RESIDUAL-ADAPTERS.json']
    frames = [native.frame(tuple(v), 9) for v in c['frames']]
    need(len(frames) == 1130 and c['h'] == 9 and c['v'] == 112 and c['R'] == 408, 'Canonical dimensions')
    need(all(rank(v) == len(v) for v in c['frames']), 'Every frame is a basis')
    edges = set(map(tuple, c['edges'])) | {(a, b) for f in c['center_frames'] for a, b in ((f, 0), (0, f))}
    children = {(r['old'], r['new']): r for r in phase['children']}
    need(len(children) == len(phase['children']) == 3036 and set(children) == edges, 'Exact child coverage')
    for i, ((a, b), record) in enumerate(sorted(children.items())):
        va, vb = c['frames'][a], c['frames'][b]
        need(rank(va + vb) == max(len(va), len(vb)), 'Nested child spaces')
        need(record['rank'] == abs(len(vb) - len(va)), 'Child rank')
        native.equal(native.recipe(record), native.adjoint(frames[a]) + frames[b], 'Child ' + str((a, b)))
        if i % 200 == 0:
            print(provider, 'independent phase edges', i, '/', len(children), flush=True)

    endpoints = {(r['role'], r['port']): r for r in phase['endpoint_adapters']}
    need(len(endpoints) == len(phase['endpoint_adapters']) == 224, 'Unique endpoint recipes')
    need(set(endpoints) == {(role, p) for role in ('source', 'target') for p in range(112)}, 'All data endpoints')
    for (role, p), record in endpoints.items():
        conventional = (('C', c['ports'][p], 1),) if role == 'source' else (('C', c['ports'][p], -1),) + native.fourier(9)
        f = c['start'][p] if role == 'source' else c['final'][112 + p]
        need(record['frame'] == f and record['rank'] == 0, 'Endpoint frame and rank')
        native.equal(native.recipe(record), native.adjoint(conventional) + frames[f], 'Endpoint ' + str((role, p)))
    need(set(c['start'][112:224]) == {0} and set(c['final'][:112]) == {1}, 'Other data endpoints')
    native.equal(frames[0], (), 'Identity frame')
    native.equal(frames[1], native.fourier(9), 'FULL frame')

    warps = {r['op']: r for r in c['warps']}
    need(len(warps) == len(c['warps']) == 72, 'Unique logical warps')
    need(set(residual['warps']) == set(map(str, warps)), 'Raw warp coverage')
    logical = {}
    for op, w in warps.items():
        record = residual['warps'][str(op)]
        need(all(record[k] == w[k] for k in ('op', 'from_frame', 'to_frame', 'G_columns')), 'Raw warp metadata')
        logical[op] = raw_k(w['G_columns'], native)
        native.equal(native.monomial(record['K']), logical[op], 'Raw K ' + str(op))
    physical = {(r['sign'], r['op'], r['old'], r['new']): r for r in phase['warps']}
    need(len(physical) == len(phase['warps']) == 180 and set(physical) == set(map(tuple, c['warp_edges'])), 'Physical warp coverage')
    for (sign, op, a, b), record in physical.items():
        need(sign in (-1, 1) and record['rank'] == 0 and record['G_columns'] == warps[op]['G_columns'], 'Warp metadata')
        operator = logical[op] if sign > 0 else native.adjoint(logical[op])
        native.equal(native.recipe(record), native.adjoint(frames[a]) + operator + frames[b], 'Physical K ' + str((sign, op, a, b)))

    dual_list = data['LITERAL-DUAL-WARP-RECIPES.json']['warps']
    dual = {(r['sign'], r['op'], r['old'], r['new']): r for r in dual_list}
    need(len(dual) == len(dual_list) == 180 and set(dual) == set(physical), 'Literal dual coverage')
    different_dual = 0
    for (sign, op, a, b), record in dual.items():
        need(record['orientation'] == 'backward_literal_dual' and record['rank'] == 0 and record['G_columns'] == warps[op]['G_columns'], 'Literal dual metadata')
        operator = raw_k(warps[op]['G_columns'], native, True)
        if sign < 0:
            operator = native.adjoint(operator)
        native.equal(native.recipe(record), native.adjoint(frames[a]) + operator + frames[b], 'Literal dual K ' + str((sign, op, a, b)))
        different_dual += record['left'] != physical[sign, op, a, b]['left']
    need(different_dual == 172, 'Literal dual differs from source K in 172 classes')

    wrappers = residual['recipes']
    wrapped = {r for r in range(224, 632) if c['start'][r] != 0 or c['final'][r] != 1}
    needed_wrappers = {str(c['start'][r]) + (':' + str(c['final'][r]) if c['final'][r] != 1 else '') for r in wrapped}
    need(set(wrappers) == needed_wrappers and len(wrappers) == 56 and len(wrapped) == 195, 'Wrapper class and helper coverage')
    for key, record in wrappers.items():
        a, b = record['frame'], record.get('terminal', 1)
        va, vb = c['frames'][a], c['frames'][b]
        width = len(vb) - len(va)
        need(rank(va + vb) == len(vb) and 0 < width <= 9, 'Residual nested frames')
        need(record['rank'] == width and record['entrance_rank'] == len(va) and record['vectors'] == va, 'Residual entry metadata')
        if b != 1:
            need(record['terminal_rank'] == len(vb) and record['terminal_vectors'] == vb, 'Proper residual terminal metadata')
        product = native.adjoint(frames[a]) + frames[b]
        native.equal(native.recipe(record), product, 'Residual ' + key)
        wrapped_product = native.adjoint(native.monomial(record['right'])) + product + native.adjoint(native.monomial(record['left']))
        native.equal(wrapped_product, native.fourier(width), 'Coordinate wrapper ' + key)

    invoices = {}
    for orientation, events in clean['providers'][provider]['programs'].items():
        need(clean['providers'][provider]['canonical'] == c, 'Clean word canonical binding')
        native_tags = {'climb', 'warp', 'adapter', 'residual_adapter'}
        need([e for e in events if e[0] in native_tags] == [e for e in original[orientation] if e[0] in native_tags], 'Every retained native record')
        entry = events.index(['phase', 'entry_adapters'])
        cleanup = events.index(['phase', 'full_frame_cleanup'])
        need(not {f[1] for e in events[:entry] for f in fields(e) if f[0] == 'L'} & wrapped, 'No wrapper helper access before entry wrapper')
        post = {r for r in range(224, 632) if c['final'][r] != 1}
        need(not {f[1] for e in events[cleanup:] for f in fields(e) if f[0] == 'L'} & post, 'No proper-terminal helper access after its core')
        counts = Counter()
        adapter_records = []
        wrapper_records = []
        for e in events:
            if e[0] == 'climb':
                _, _, _, a, b, width = e
                need((a, b) in children and children[a, b]['rank'] == width, 'Paid child occurrence binding')
                counts['climb'] += 1
            elif e[0] == 'warp':
                op, a, b = e[2:]
                need((1 if op > 0 else -1, abs(op), a, b) in physical, 'Physical warp occurrence binding')
                counts['warp'] += 1
            elif e[0] == 'adapter':
                _, direction, r, f = e
                need(direction in ('old_to_new', 'new_to_old'), 'Adapter direction')
                need(f == (c['start'][r] if direction == 'old_to_new' else c['final'][r]), 'Adapter boundary binding')
                if direction == 'old_to_new':
                    need(r not in wrapped, 'No duplicate helper entry wrapper')
                    need(r < 112 or f == 0, 'Only source ports need ordinary entry adapters')
                else:
                    need(r not in post, 'No wrong FULL adapter on a proper terminal helper')
                    need(112 <= r < 224 or f == 1, 'Only target ports need ordinary exit adapters')
                adapter_records.append((direction, r))
                counts['adapter'] += 1
            elif e[0] == 'residual_adapter':
                _, position, r, a, *tail = e
                b = tail[0] if tail else 1
                need(position in ('pre', 'post') and r in wrapped and a == c['start'][r] and b == c['final'][r], 'Residual occurrence binding')
                wrapper_records.append((position, r))
                counts['residual_adapter'] += 1
        need(set(adapter_records) == {('old_to_new', r) for r in range(632) if r not in wrapped} | {('new_to_old', r) for r in range(632) if r not in post}, 'All ordinary adapter occurrences')
        need(len(adapter_records) == len(set(adapter_records)), 'No repeated ordinary adapter')
        need(set(wrapper_records) == {(position, r) for position in ('pre', 'post') for r in wrapped} and len(wrapper_records) == 390, 'All wrapper occurrences')
        need(counts == Counter(climb=3507, warp=240, adapter=978, residual_adapter=390), 'Native occurrence inventory')
        invoices[orientation] = dict(counts)

    child = native.recipe(next(iter(children.values())))
    corrupt = child + (('phase', 1),)
    need(native.tableau(corrupt) == native.tableau(child) and native.state(corrupt) != native.state(child), 'Global phase negative control')
    proper = next(r for r in wrappers.values() if r.get('terminal', 1) != 1)
    correct = native.adjoint(frames[proper['frame']]) + frames[proper['terminal']]
    wrong = native.adjoint(frames[proper['frame']]) + frames[1]
    need(native.tableau(correct) != native.tableau(wrong), 'Wrong FULL terminal negative control')
    need(any(native.tableau(logical[op]) != native.tableau(raw_k(warps[op]['G_columns'], native, True)) for op in logical), 'Conjugation changes some warp operators')
    return {'status': 'PASS_INDEPENDENT_NATIVE_CORE_LIFT', 'pins': PINS[provider],
            'frames': len(frames), 'child_classes': len(children), 'endpoint_classes': len(endpoints),
            'raw_warps': len(warps), 'physical_warp_classes': len(physical), 'residual_classes': len(wrappers),
            'literal_dual_classes': len(dual), 'literal_dual_recipes_different_from_forward': different_dual,
            'wrapped_helpers': len(wrapped), 'native_occurrences': invoices,
            'helper_width_profile': dict(sorted(Counter(len(c['frames'][c['final'][r]]) - len(c['frames'][c['start'][r]]) for r in range(224, 632)).items())),
            'negative_controls': ['wrong global phase with equal Pauli action', 'wrong FULL terminal', 'literal conjugate K can differ from K'],
            'seconds': time.monotonic() - started}


def main(args):
    need(sha256(INTERPRETER.read_bytes()).hexdigest() == INTERPRETER_PIN, 'Independent interpreter pin')
    spec = importlib.util.spec_from_file_location('independent_native_interpreter', INTERPRETER)
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    clean = pinned(CLEAN, CLEAN_PIN)
    result = {'status': 'PASS_INDEPENDENT_NEW_CORE_NATIVE_RECIPES', 'interpreter_sha256': INTERPRETER_PIN,
              'clean_payload_sha256': CLEAN_PIN, 'method': 'Independent Pauli conjugation and exact 512-entry Gaussian zero-state vectors; no generator or Clifford compiler import',
              'scope': 'Local phase-aware native lift. The whole scalar map is in the separate logical review. Global hosting, owner, controller, and recursive supplier admission remain separate.',
              'backward_binding': 'Both a consistent K choice and the literal inverse-transpose choice conjugate(K) have exact rank-zero recipes. The literal dual differs in 172 of 180 physical classes per provider.',
              'providers': {name: review(name, native, clean) for name in args.providers}}
    result['max_rss_bytes'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--providers', nargs='+', choices=['base', 'extra'], default=['base'])
    parser.add_argument('--out', type=Path, required=True)
    main(parser.parse_args())
