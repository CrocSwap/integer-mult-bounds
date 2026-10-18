#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent binding and phase-exact interpretation of R2 FULL cleanup.

Only the source-pinned Sagar Thakrar Clifford audit kernel is executed.
The producer and its native verifier are read as provenance, never imported.
"""
import argparse
import copy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE = 'research/rank7-shared-restore-fanin/evidence/'
KERNEL = 'research/frontier1094-recipes-exact-seed76/clifford.py'
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
PHASES = ['zero_frame_precondition', 'entry_adapters', 'A', 'centers', 'B',
          'cleanup_tail', 'final', 'exit_adapters', 'full_frame_cleanup', 'done']


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = dict(pairs)
    need(len(result) == len(pairs), 'duplicate JSON key')
    return result


def parse(raw):
    need(len(raw) < 16 * 1024 * 1024, 'artifact capacity')
    return json.loads(raw, object_pairs_hook=unique)


def read(path):
    raw = path.read_bytes()
    return parse(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def span(basis):
    result = {0}
    for vector in basis:
        need(type(vector) is int and 0 < vector < 512 and vector not in result,
             'independent binary frame')
        result |= {x ^ vector for x in result}
    return frozenset(result)


def authenticate():
    blobs = {}
    for row in read(PACKAGE / 'SOURCES.json')['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(digest(raw) == row['sha256'], 'source pin: ' + row['path'])
            blobs[row['path']] = raw
    need({KERNEL, SOURCE + 'NATIVE-RECEIPT.json', SOURCE + 'WORD-base.json.gz',
          SOURCE + 'WORD-extra.json.gz'} <= set(blobs), 'source inventory')
    return blobs


def load_provider(blobs, tag):
    receipt = parse(blobs[SOURCE + 'NATIVE-RECEIPT.json'])['providers'][tag]
    raw_word = blobs[SOURCE + f'WORD-{tag}.json.gz']
    need(digest(raw_word) == receipt['word_sha256'], 'source/native word binding')
    artifacts = []
    for name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'CLIFFORD-RECIPES.json'):
        filename = ('LOCAL-PROGRAMS.json.gz' if name.startswith('LOCAL') else
                    tag + '-' + name + ('.gz' if name.endswith('.json') else ''))
        raw = (PACKAGE / 'data' / filename).read_bytes()
        original = gzip.decompress(raw) if name.endswith('.json') else raw
        need(digest(original) == receipt['complete_native_files']['local/' + name],
             'published native artifact: ' + tag + '/' + name)
        artifacts.append(parse(original if name.endswith('.json') else gzip.decompress(original)))
    return parse(gzip.decompress(raw_word)), artifacts


def source_binding(word, canonical):
    """Derive the full cleanup and compact/private namespaces from literal data."""
    need((word['report']['h'], word['report']['v'], word['report']['R']) == (9, 112, 480), 'source domain')
    need((canonical['h'], canonical['v'], canonical['R']) == (9, 112, 408), 'native domain')
    kept = [r for r in range(704) if r not in word['removed']]
    need(len(kept) == 632 and canonical['helper_origin'] == kept[224:], 'compact register map')
    mapping = {r: i for i, r in enumerate(kept)}
    need(canonical['frames'][1] == FULL, 'FULL frame identity')
    spaces = [span(f) for f in canonical['frames']]
    frame_ids = {s: i for i, s in enumerate(spaces)}
    need(len(frame_ids) == len(spaces), 'unique native frames')
    private = sorted(int(r) for r, f in word['helper_final'].items() if len(f) < 9)
    zeros = [mapping[r] for r in private]
    need(len(zeros) == 91 and canonical['zero_buffers'] == zeros, 'private-buffer inventory')
    need(all(spaces[canonical['final'][mapping[r]]] == span(f)
             for r, f in ((int(k), v) for k, v in word['helper_final'].items())), 'helper terminals')

    def reg(r):
        need(type(r) is int, 'source register type')
        if r >= 704:
            need(r - 704 in private, 'private source owner')
            return ['Z', mapping[r - 704]]
        need(r in mapping, 'retained source register')
        return mapping[r]

    expected = []
    for gate in word['cleanup']:
        need(gate[-1] == FULL, 'source cleanup FULL frame')
        kind = gate[0]
        if kind == 'warp':
            need(len(gate) == 4, 'source cleanup warp schema')
            expected.append(['warp', reg(gate[1]), gate[2], 1, 1])
        else:
            need(kind in ('add', 'scale'), 'source cleanup scalar kind')
            n = 2 if kind == 'add' else 1
            need(len(gate) == n + 4 and all(type(x) is int and x for x in gate[-3:-1]),
                 'source cleanup scalar schema')
            expected.append([kind, *(reg(r) for r in gate[1:1+n]), *gate[-3:-1], 1])
    need(canonical['cleanup'] == expected, 'source/canonical complete cleanup')

    # The R2-specific leading inverse uses private zero roles for narrow-ended helpers.
    inverse = []
    for gate in reversed(word['restore']):
        kind = gate[0]
        n = 2 if kind == 'add' else 1
        operands = [r + 704 if r in private else r for r in gate[1:1+n]]
        a, b = gate[-3:-1]
        a, b = (-a, b) if kind == 'add' else (b, a)
        inverse.append([kind, *operands, a, b, FULL])
    need(len(inverse) == 204 and word['cleanup'][:204] == inverse, 'R2 literal inverse cleanup prefix')

    need(len(word['warps']) == len(canonical['warps']) == 72, 'source warp inventory')
    columns = {}
    for op, (raw, native) in enumerate(zip(word['warps'], canonical['warps']), 1):
        pos, lender, cols, old, new = raw
        need(native == {'B_pos': pos, 'lender': mapping[lender], 'G_columns': cols,
                        'from_frame': frame_ids[span(old)],
                        'to_frame': frame_ids[span(new)], 'op': op}, 'source warp definition')
        columns[op] = cols
    return columns, {'literal_cleanup_gates': len(expected), 'R2_inverse_prefix': len(inverse),
                     'private_buffers': len(zeros), 'live_registers': len(kept)}


def role(r):
    return r.copy() if isinstance(r, list) else ['L', r]


def expected_body(canonical, backward):
    result = []
    for gate in canonical['cleanup']:
        if gate[0] == 'warp':
            result.append(['warp', role(gate[1]), gate[2], 1, 1])
        elif gate[0] == 'add':
            _, dst, src, a, b, f = gate
            if backward:
                dst, src, a = src, dst, -a
            result.append(['scalar', ['add', role(dst), role(src), a, b], f])
        else:
            _, dst, a, b, f = gate
            if backward:
                a, b = b, a
            result.append(['scalar', ['scale', role(dst), a, b], f])
    return result


def cleanup_stream(program):
    def contains_private(value):
        return isinstance(value, list) and (value[:1] == ['Z'] or any(contains_private(x) for x in value))

    sections, phases = {}, []
    for event in program:
        need(type(event) is list and event, 'native event schema')
        if event[0] == 'phase':
            need(len(event) == 2, 'phase schema')
            phases.append(event[1])
            need(phases == PHASES[:len(phases)], 'native phase order')
            sections[event[1]] = []
        else:
            need(phases, 'event before phase')
            if phases[-1] != 'full_frame_cleanup':
                need(event[0] != 'zero_buffer' and not contains_private(event),
                     'private namespace confined to cleanup')
            sections[phases[-1]].append(event)
    need(phases == PHASES and not sections['done'], 'complete native phases')
    return sections['full_frame_cleanup']


def bind_stream(canonical, stream, backward):
    zeros = canonical['zero_buffers']
    alloc = [['zero_buffer', 'alloc', r] for r in zeros]
    free = [['zero_buffer', 'free', r] for r in zeros]
    wrappers = []
    for r in range(224, 632):
        a, b = canonical['start'][r], canonical['final'][r]
        if a != 0 or b != 1:
            wrappers.append(['residual_adapter', 'post', r, a] + ([b] if b != 1 else []))
    body = expected_body(canonical, backward)
    need(stream[:len(alloc)] == alloc, 'all private allocations precede cleanup')
    need(stream[len(alloc):len(alloc)+len(body)] == body, 'complete cleanup event binding')
    need(stream[len(alloc)+len(body):] == free + wrappers, 'frees then residual posts')
    active, touched, warp_keys, scalars = set(), set(), set(), 0
    for event in stream:
        kind = event[0]
        if kind == 'zero_buffer':
            _, action, r = event
            if action == 'alloc':
                need(r not in active, 'unique private allocation')
                active.add(r)
            else:
                need(r in active, 'free only live private role')
                active.remove(r)
            continue
        if kind == 'residual_adapter':
            need(not active, 'post adapters follow all frees')
            continue
        if kind == 'warp':
            _, target, op, old, new = event
            need(old == new == 1 and op != 0, 'cleanup warp FULL boundary')
            operands = [target]
            warp_keys.add((-1 if op < 0 else 1, abs(op), old, new))
        else:
            need(kind == 'scalar' and event[2] == 1, 'cleanup scalar FULL boundary')
            op = event[1]
            need(op[0] in ('add', 'scale'), 'cleanup scalar operation')
            operands = op[1:3] if op[0] == 'add' else op[1:2]
            scalars += 1
        for namespace, r in operands:
            if namespace == 'Z':
                need(r in active, 'private access in allocated lifetime')
            else:
                need(namespace == 'L' and 0 <= r < 632 and canonical['final'][r] == 1,
                     'only FULL-ended live roles touched')
            touched.add((namespace, r))
    need(not active, 'all private roles freed')
    need(len(warp_keys) == 72, 'used cleanup warp inventory')
    return sorted(warp_keys), {'cleanup_events': len(stream), 'scalar_events': scalars,
        'warp_events': sum(e[0] == 'warp' for e in stream), 'allocations': len(alloc),
        'frees': len(free), 'residual_posts': len(wrappers),
        'touched_live_roles': sum(ns == 'L' for ns, _ in touched),
        'touched_private_roles': sum(ns == 'Z' for ns, _ in touched)}


def source_operator(kernel, columns):
    """K_G = D_(I+G^-T G^-1) P_G; columns and rows kept distinct.

    Invert by all 512 images, not by the producer's elimination procedure.
    """
    need(len(columns) == 9 and all(type(c) is int and 0 <= c < 512 for c in columns), 'G schema')
    images = []
    for x in range(512):
        y = 0
        for i, column in enumerate(columns):
            if x >> i & 1:
                y ^= column
        images.append(y)
    need(len(set(images)) == 512, 'G invertibility')
    inverse = {y: x for x, y in enumerate(images)}
    invcols = [inverse[1 << i] for i in range(9)]
    form = [sum((((invcols[i] & invcols[j]).bit_count() % 2) ^ (i == j)) << j
                for j in range(9)) for i in range(9)]
    linear = [form[i] >> i & 1 for i in range(9)]
    rows = [sum((columns[j] >> i & 1) << j for j in range(9)) for i in range(9)]
    return [('P', rows), ('D', form, linear)]


def conjugate(circuit):
    result = []
    for gate in circuit:
        if gate[0] == 'C':
            result.append(('C', gate[1], -gate[2]))
        elif gate[0] == 'D':
            result.append(('D', gate[1], [(-x) % 4 for x in gate[2]]))
        elif gate[0] == 'PH':
            result.append(('PH', -gate[1] % 4))
        else:
            need(gate[0] in ('P', 'X'), 'native conjugate gate')
            result.append(gate)
    return result


def check_warp(kernel, rec, columns, key, cache):
    sign, op, old, new = key
    need((rec['sign'], rec['op'], rec['old'], rec['new']) == key and old == new == 1,
         'native warp key binding')
    need(rec['G_columns'] == columns, 'native source G binding')
    need(rec['rank'] == 0 and rec['right'] is None, 'cleanup warp rank zero')
    need(kernel.well_formed(rec['left']), 'native monomial schema')
    cache_key = json.dumps([rec, columns, key], sort_keys=True)
    if cache_key in cache:
        return
    logical = source_operator(kernel, columns)
    if sign < 0:
        logical = kernel.adjoint(logical)
    expected = kernel.fourier(9, -1) + logical + kernel.fourier(9)
    actual = kernel.monomial(rec['left'])
    need(kernel.same_operator(actual, expected), 'forward phase-exact cleanup operator')
    need(kernel.same_operator(conjugate(actual), conjugate(expected)), 'dual phase-exact cleanup operator')
    cache.add(cache_key)


def native_semantics(kernel, recipes, columns, keys, cache):
    index = {(r['sign'], r['op'], r['old'], r['new']): r for r in recipes['warps']}
    need(len(index) == len(recipes['warps']), 'unique native warp keys')
    for key in keys:
        need(tuple(key) in index, 'cleanup recipe coverage')
        check_warp(kernel, index[tuple(key)], columns[key[1]], tuple(key), cache)
    return index


def cleanup_zero_return(stream, dirty_private=None):
    """Exact free-group rows on 632 arbitrary vector inputs, clean private roles.

    Scalars are rational. Operator words are noncommutative and cancel only
    adjacent inverse symbols; no equality between different warp IDs is used.
    This checks the cleanup alone, without taking its earlier prefix on trust.
    """
    rows = {('L', r): {(r, ()): Fraction(1)} for r in range(632)}
    active, freed, max_terms = set(), [], 1
    for event in stream:
        kind = event[0]
        if kind == 'residual_adapter':
            continue  # The audited cleanup body ends before these post wrappers.
        if kind == 'zero_buffer':
            _, action, r = event
            if action == 'alloc':
                need(r not in active and ('Z', r) not in rows, 'private allocation uniqueness')
                rows['Z', r] = {(632, ()): Fraction(1)} if r == dirty_private else {}
                active.add(r)
            else:
                need(r in active, 'private free lifetime')
                need(not rows['Z', r], 'private zero at actual free')
                active.remove(r)
                freed.append(r)
            continue
        operands = [event[1]] if kind == 'warp' else (
            event[1][1:3] if event[1][0] == 'add' else event[1][1:2])
        for namespace, r in operands:
            need(namespace == 'L' or (namespace == 'Z' and r in active), 'private execution lifetime')
        if kind == 'warp':
            target, symbol = tuple(event[1]), event[2]
            transformed = {}
            for (column, word), value in rows[target].items():
                reduced = word[1:] if word and word[0] == -symbol else (symbol,) + word
                transformed[column, reduced] = value
            rows[target] = transformed
        else:
            need(kind == 'scalar', 'cleanup execution kind')
            op = event[1]
            target, q = tuple(op[1]), Fraction(*op[-2:])
            if op[0] == 'scale':
                rows[target] = {key: q * value for key, value in rows[target].items()}
            else:
                need(op[0] == 'add', 'cleanup execution scalar')
                for key, value in list(rows[tuple(op[2])].items()):
                    new = rows[target].get(key, 0) + q * value
                    if new:
                        rows[target][key] = new
                    else:
                        rows[target].pop(key, None)
        max_terms = max(max_terms, len(rows[target]))
    need(not active and len(freed) == 91, 'complete zero-return inventory')
    need(all(rows['L', r] == {(r, ()): 1} for r in range(112, 224)), 'cleanup preserves every target')
    serialized = [[r, [[column, list(word), q.numerator, q.denominator]
                       for (column, word), q in sorted(rows['L', r].items())]] for r in range(632)]
    return {'arbitrary_live_vector_inputs': 632, 'private_zeros_at_free': len(freed),
            'unchanged_target_rows': 112, 'maximum_row_terms': max_terms,
            'changed_live_rows': sum(rows['L', r] != {(r, ()): 1} for r in range(632)),
            'final_live_free_operator_sha256': digest(json.dumps(serialized, separators=(',', ':')).encode())}


def rejected(label, reason, action):
    try:
        action()
    except ValueError as error:
        need(str(error) == reason, 'wrong rejection for ' + label + ': ' + str(error))
        return label
    raise ValueError('accepted semantic mutant: ' + label)


def controls(kernel, word, canonical, programs, columns, keys, index):
    """Mutations run after authentication and reach the named semantic predicate."""
    result = []
    for orientation in ('forward', 'backward'):
        stream = cleanup_stream(programs[orientation])
        scalar_at = next(i for i, e in enumerate(stream) if e[0] == 'scalar')
        warp_at = next(i for i, e in enumerate(stream) if e[0] == 'warp')
        free_at = next(i for i, e in enumerate(stream) if e[:2] == ['zero_buffer', 'free'])
        for name in ('wrong_scalar_sign', 'missing_inverse_step', 'wrong_warp_sign',
                     'private_alias_to_live', 'early_free', 'early_residual_post'):
            bad = copy.deepcopy(stream)
            reason = 'complete cleanup event binding'
            if name == 'wrong_scalar_sign':
                bad[scalar_at][1][-2] *= -1
            elif name == 'missing_inverse_step':
                del bad[scalar_at]
            elif name == 'wrong_warp_sign':
                bad[warp_at][2] *= -1
            elif name == 'private_alias_to_live':
                e = next(e for e in bad if e[0] == 'scalar' and any(isinstance(r, list) and r[0] == 'Z' for r in e[1]))
                next(r for r in e[1] if isinstance(r, list) and r[0] == 'Z')[0] = 'L'
            elif name == 'early_free':
                bad.insert(scalar_at, bad.pop(free_at))
            else:
                bad.insert(scalar_at, bad.pop())
            need(bad != stream, 'nonvacuous event mutant')
            result.append(rejected(orientation + ':' + name, reason,
                lambda: bind_stream(canonical, bad, orientation == 'backward')))
        private_write = next(i for i, e in enumerate(stream)
                             if e[0] == 'scalar' and e[1][1][0] == 'Z' and e[1][0] == 'add')
        z = stream[private_write][1][1][1]
        bad = copy.deepcopy(stream)
        bad[private_write][1][-2] *= -1
        result.append(rejected(orientation + ':private_write_sign', 'private zero at actual free',
                               lambda: cleanup_zero_return(bad)))
        bad = copy.deepcopy(stream)
        release = bad.index(['zero_buffer', 'free', z])
        bad.insert(private_write + 1, bad.pop(release))
        result.append(rejected(orientation + ':nonzero_early_free', 'private zero at actual free',
                               lambda: cleanup_zero_return(bad)))
        result.append(rejected(orientation + ':dirty_private_entrance', 'private zero at actual free',
                               lambda: cleanup_zero_return(stream, dirty_private=z)))
    key = tuple(keys[0])
    original = index[key]
    for name in ('global_phase', 'translation', 'quadratic_phase', 'row_permutation', 'wrong_rank'):
        bad = copy.deepcopy(original)
        reason = 'forward phase-exact cleanup operator'
        left = bad['left']
        if name == 'global_phase':
            left['phase'] = (left['phase'] + 1) % 4
        elif name == 'translation':
            left['offset'] ^= 1
        elif name == 'quadratic_phase':
            left['quadratic_rows'][0] ^= 2
            left['quadratic_rows'][1] ^= 1
        elif name == 'row_permutation':
            left['matrix_rows'][0], left['matrix_rows'][1] = left['matrix_rows'][1], left['matrix_rows'][0]
        else:
            bad['rank'] = 1
            reason = 'cleanup warp rank zero'
        need(bad != original, 'nonvacuous native mutant')
        result.append(rejected('native:' + name, reason,
            lambda: check_warp(kernel, bad, columns[key[1]], key, set())))
    bad = copy.deepcopy(word)
    bad['cleanup'][0][3] *= -1
    bad_canonical = copy.deepcopy(canonical)
    bad_canonical['cleanup'][0][3] *= -1
    result.append(rejected('source:coordinated_inverse_sign', 'R2 literal inverse cleanup prefix',
        lambda: source_binding(bad, bad_canonical)))
    bad = copy.deepcopy(canonical)
    bad['zero_buffers'][0] = bad['zero_buffers'][1]
    result.append(rejected('source:private_inventory_alias', 'private-buffer inventory',
        lambda: source_binding(word, bad)))
    bad_program = copy.deepcopy(programs['forward'])
    bad_program.insert(1, ['zero_buffer', 'alloc', canonical['zero_buffers'][0]])
    result.append(rejected('source:private_allocation_in_prefix', 'private namespace confined to cleanup',
        lambda: cleanup_stream(bad_program)))
    return result


def verify():
    blobs = authenticate()
    kernel = types.ModuleType('pinned_independent_clifford')
    exec(compile(blobs[KERNEL], KERNEL, 'exec'), kernel.__dict__)
    need(kernel.same_operator([('C', 1, 1), ('C', 1, 1)], [('X', 1)]), 'kernel C-square calibration')
    need(not kernel.same_operator([('PH', 1)], []), 'kernel global-phase calibration')
    cache, providers = set(), {}
    for tag in ('base', 'extra'):
        word, (canonical, programs, recipes) = load_provider(blobs, tag)
        columns, source_report = source_binding(word, canonical)
        need(set(programs) == {'forward', 'backward'}, 'both native orientations')
        reports, zero_reports, used = {}, {}, None
        for orientation in ('forward', 'backward'):
            keys, reports[orientation] = bind_stream(canonical, cleanup_stream(programs[orientation]),
                                                    orientation == 'backward')
            need(used is None or used == keys, 'same cleanup warp keys in dual')
            used = keys
            zero_reports[orientation] = cleanup_zero_return(cleanup_stream(programs[orientation]))
        index = native_semantics(kernel, recipes, columns, used, cache)
        faults = controls(kernel, word, canonical, programs, columns, used, index)
        providers[tag] = {'source_binding': source_report, 'event_binding': reports, 'zero_return': zero_reports,
            'native_warp_keys': [list(key) for key in used], 'phase_exact_recipes': len(used),
            'complex_columns_per_identity': 512, 'orientations': 2, 'semantic_rejections': faults}
    return {'status': 'PASS_PR3044_NATIVE_CLEANUP', 'providers': providers,
            'distinct_source_bound_native_recipes': len(cache), 'kernel_calibrations': 2,
            'scope': 'Native cleanup equals the literal FULL-frame cleanup on its full input space. '
                     'All 91 clean private roles return to zero for arbitrary live entrance vectors. '
                     'Original source/helper restoration still needs the prefix; '
                     'no native-prefix, physical executor, supplier or kappa admission.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true', help='print the deterministic receipt without comparing it')
    args = parser.parse_args()
    result = verify()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == read(PACKAGE / 'RESULT.json'), 'saved result equality')
        print('PASS_PR3044_NATIVE_CLEANUP providers=2 recipes=72 columns=512 orientations=2 '
              'cleanup_gates=5208 semantic_controls=52 no_new_kappa')


if __name__ == '__main__':
    main()
