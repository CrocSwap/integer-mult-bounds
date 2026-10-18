#!/usr/bin/env python3
"""Exact, scoped reader-compatible restoration evidence. Apache-2.0."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('restoration_backend', HERE / 'backend.py')
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)
independent_spec = importlib.util.spec_from_file_location('independent_restoration_check', HERE / 'independent_check.py')
independent = importlib.util.module_from_spec(independent_spec)
independent_spec.loader.exec_module(independent)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def pmat(p):
    return [[int(p[i] == j) for j in range(len(p))] for i in range(len(p))]


def transpose(a):
    return list(map(list, zip(*a)))


def matrix_data(perms, readers):
    n = len(perms[0])
    prefix = identity(n)
    prefixes, defects = [], []
    for p, h in zip(perms, readers):
        prefixes.append(prefix)
        changed = matmul([h], prefix)[0]
        defects.append([x - y for x, y in zip(changed, h)])
        prefix = matmul(pmat(p), prefix)
    return prefixes, defects, prefix


def direct(perms, readers, z, y, eager, shared=False):
    """Literal state replay; does not use the matrix criterion or backend."""
    z, y = list(z), list(y)
    for i, (p, h) in enumerate(zip(perms, readers)):
        y[0 if shared else i] += sum(a * b for a, b in zip(h, z))
        z = [z[j] for j in p]
        if eager:
            out = [0] * len(p)
            for j, src in enumerate(p):
                out[src] = z[j]
            z = out
    if not eager:
        # Restore by literal reverse-inverse factors, independently of product.
        for p in reversed(perms):
            out = [0] * len(p)
            for j, src in enumerate(p):
                out[src] = z[j]
            z = out
    return z + y


def census():
    # Entire declared domain, no random search or heuristic stopping.
    ps = list(itertools.permutations(range(2)))
    hs = list(itertools.product((-1, 0, 1), repeat=2))
    cases = independent_ok = shared_ok = cancellation_only = 0
    for perms in itertools.product(ps, repeat=3):
        for readers in itertools.product(hs, repeat=3):
            _, defects, _ = matrix_data(perms, readers)
            expected = all(not any(d) for d in defects)
            total = [sum(d[j] for d in defects) for j in range(2)]
            expected_shared = not any(total)
            observed, observed_shared = True, True
            for z in ((1, 0), (0, 1)):
                observed &= direct(perms, readers, z, [0]*3, True) == direct(perms, readers, z, [0]*3, False)
                observed_shared &= direct(perms, readers, z, [0], True, True) == direct(perms, readers, z, [0], False, True)
            require(observed == expected, 'independent-output criterion disagreement')
            require(observed_shared == expected_shared, 'shared-output criterion disagreement')
            cases += 1
            independent_ok += expected
            shared_ok += expected_shared
            cancellation_only += expected_shared and not expected
    return {'dimension': 2, 'children': 3, 'permutation_alphabet_size': 2,
            'reader_alphabet': [-1, 0, 1], 'cases': cases,
            'independent_output_accepted': independent_ok,
            'shared_final_output_accepted': shared_ok,
            'shared_only_cancellation_cases': cancellation_only,
            'basis_vectors_per_semantics': 2,
            'stopping_rule': 'exhaust all 2^3 * 9^3 cases'}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def pins():
    source = json.loads((HERE / 'SOURCE-PINS.json').read_text())
    for item in source['retained_sources']:
        data = (HERE / item['local_path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item['sha256'], 'retained source SHA256 mismatch')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require(blob == item['git_blob'], 'retained source Git blob mismatch')
    selected = json.loads((HERE / 'sources/BASE-SELECTED.json').read_text())
    require(selected['kappa'] == source['selected_kappa'], 'base selected context mismatch')
    return source


def source_permutation(matrix):
    return [row.index(1) for row in matrix]


def compile_external_perm(p, n_outputs):
    # A one-child batch with zero reader isolates a permutation and its inverse.
    pack = backend.compile_batch([p], [[0] * len(p)], eager=True)
    # Relocate the scratch register from n+1 to n+n_outputs.
    n = len(p)
    segment = next(s for s in pack['segments'] if s['kind'] == 'forward')
    return [('add', n+n_outputs if d == n+1 else d,
             n+n_outputs if s == n+1 else s, sign)
            for _, d, s, sign in pack['program'][segment['start']:segment['stop']]]


def make_receipt():
    source = pins()
    # Convention: new[j] = old[p[j]]. G2 is inverse to cycle notation (0123).
    perms = [[1, 0, 3, 2, 5, 4, 7, 6],
             [3, 0, 1, 2, 7, 4, 5, 6],
             [4, 5, 6, 7, 0, 1, 2, 3]]
    readers = [[1,0,0,0,0,0,0,0], [1,1,0,0,0,0,0,0], [1,0,1,0,0,0,0,0]]
    prefixes, defects, product = matrix_data(perms, readers)
    require(all(not any(d) for d in defects), 'fixture not compatible')
    require(matmul(pmat(perms[0]), pmat(perms[1])) != matmul(pmat(perms[1]), pmat(perms[0])), 'fixture must be noncommuting')
    eager = backend.compile_batch(perms, readers, eager=True)
    deferred = backend.compile_batch(perms, readers, eager=False)
    require(pmat(deferred['composed']) == product, 'backend/matrix product disagreement')
    n, r = 8, 3
    # One full basis per arbitrary dirty workspace/output coordinate, plus mixed data.
    inputs = [[int(i == j) for i in range(n+r)] + [0] for j in range(n+r)]
    inputs += [[-7, 4, 0, 9, -2, 13, 5, -11, 31, -17, 2, 0], [0]*12]
    for initial in inputs:
        a, ai = backend.execute(eager['program'], initial)
        b, bi = backend.execute(deferred['program'], initial)
        expected = direct(perms, readers, initial[:n], initial[n:n+r], True) + [0]
        require(a == b == expected, 'literal backend all-input basis failure')
        # Literal inverse must restore every state register, including scratch.
        inv = [(op, d, s, -sign) for op, d, s, sign in reversed(deferred['program'])]
        restored, _ = backend.execute(inv, b)
        require(restored == initial, 'literal inverse failure')
    sample = inputs[-2]
    _, invoice_e = backend.execute(eager['program'], sample)
    _, invoice_d = backend.execute(deferred['program'], sample)
    categories = {}
    for name, pack in [('eager', eager), ('deferred', deferred)]:
        counts = {}
        for seg in pack['segments']:
            counts[seg['kind']] = counts.get(seg['kind'], 0) + seg['stop']-seg['start']
        categories[name] = counts
    require(len(eager['program']) == 173 and len(deferred['program']) == 113, 'literal invoice changed')

    # Catalytic wrapper removes all observable dependence on incoming dirt.
    # Immutable source x occupies addresses 12..19. B = I + cyclic shift,
    # expanded literally as two source additions per workspace coordinate.
    pre_reads = [('add', n+i, j, -h) for i, row in enumerate(readers)
                 for j, h in enumerate(row) if h]
    load = [('add', j, n+r+1+k, 1) for j in range(n)
            for k in (j, (j+1) % n)]
    unload = [(op, d, s, -sign) for op, d, s, sign in reversed(load)]
    wrapped_e = pre_reads + load + eager['program'] + unload
    wrapped_d = pre_reads + load + deferred['program'] + unload
    wrapped_inputs = [[int(i == j) for i in range(20)] for j in range(20) if j != 11]
    wrapped_inputs.append([-7,4,0,9,-2,13,5,-11,31,-17,2,0,3,-5,8,2,1,0,-4,6])
    for initial in wrapped_inputs:
        a, _ = backend.execute(wrapped_e, initial)
        b, _ = backend.execute(wrapped_d, initial)
        x = initial[12:]
        bx = [x[j] + x[(j+1) % n] for j in range(n)]
        expected = initial[:]
        for i, h in enumerate(readers):
            expected[n+i] += sum(c*v for c,v in zip(h,bx))
        require(a == b == expected, 'catalytic wrapper or dirty independence failed')
        inverse = [(op,d,s,-sign) for op,d,s,sign in reversed(wrapped_d)]
        restored, _ = backend.execute(inverse, b)
        require(restored == initial, 'wrapped inverse failed')
    _, wrapped_ie = backend.execute(wrapped_e, wrapped_inputs[-1])
    _, wrapped_id = backend.execute(wrapped_d, wrapped_inputs[-1])
    require(len(wrapped_e) == 210 and len(wrapped_d) == 150, 'wrapped invoice changed')
    wrapper = {'source_matrix': 'B x has coordinate x[j] + x[(j+1) mod 8]',
               'source_addresses': list(range(12,20)), 'basis_cases': 19, 'mixed_cases': 1,
               'pre_read_adds': len(pre_reads), 'B_adds_each_direction': len(load),
               'eager_program_sha256': digest(wrapped_e), 'deferred_program_sha256': digest(wrapped_d),
               'invoice_eager': wrapped_ie, 'invoice_deferred': wrapped_id}

    controls = {}
    dirty_only = [1]+[0]*19
    missing_pre = load + deferred['program'] + unload
    bad_state, _ = backend.execute(missing_pre, dirty_only)
    require(bad_state[8:11] != [0]*3 and bad_state[:8] == dirty_only[:8], 'missing pre-read must expose dirt')
    controls['missing_catalytic_pre_reads'] = bad_state[8:11]
    source_only = [0]*12 + [1] + [0]*7
    missing_unload = pre_reads + load + deferred['program']
    bad_state, _ = backend.execute(missing_unload, source_only)
    require(any(bad_state[:8]), 'unpaid inverse B must fail restoration')
    controls['missing_inverse_B'] = bad_state[:8]
    bad_readers = [h[:] for h in readers]
    bad_readers[1] = [1,0,0,0,0,0,0,0]
    _, bad_defects, _ = matrix_data(perms, bad_readers)
    witness = [1]+[0]*7
    a = direct(perms, bad_readers, witness, [0]*r, True)
    b = direct(perms, bad_readers, witness, [0]*r, False)
    require(any(bad_defects[1]) and a != b, 'incompatible reader not detected')
    controls['incompatible_reader'] = {'input_workspace': witness, 'eager_outputs': a[n:], 'deferred_outputs': b[n:], 'defect': bad_defects[1]}
    require(direct(perms, bad_readers, [0]*n, [0]*r, True) == direct(perms, bad_readers, [0]*n, [0]*r, False), 'zero-workspace masking changed')
    controls['zero_workspace_hides_bad_reader'] = True
    # Keep emitted reader and forward events; omit final restore.
    unrestored = [event for seg in deferred['segments'] if seg['kind'] != 'restore'
                  for event in deferred['program'][seg['start']:seg['stop']]]
    initial = witness+[0]*(r+1)
    no_restore, _ = backend.execute(unrestored, initial)
    require(no_restore[:n] != witness, 'missing restore control ineffective')
    controls['missing_final_restore'] = no_restore[:n]
    wrong_order = unrestored[:]
    for p in perms: # WRONG: inverse factors must execute in reverse order.
        wrong_order += compile_external_perm(source_permutation(transpose(pmat(p))), r)
    bad_state, _ = backend.execute(wrong_order, initial)
    require(bad_state[:n] != witness, 'inverse-order control ineffective')
    controls['wrong_inverse_order'] = bad_state[:n]
    # Remove one reader ADD: workspace restoration still succeeds, output fails.
    omitted = list(deferred['program'])
    del omitted[0]
    bad_state, _ = backend.execute(omitted, initial)
    expected = direct(perms, readers, witness, [0]*r, True)+[0]
    require(bad_state[:n] == witness and bad_state != expected, 'missing reader control ineffective')
    controls['missing_reader'] = bad_state[n:n+r]
    controls['dropped_scalar_charge'] = {'actual_add_instructions': 113, 'unpaid_claim': 112}
    require(sum(categories['deferred'].values()) != 112, 'unpaid instruction not detected')
    # Shared final-output cancellation is deliberately outside independent-output admission.
    cp = [[1,0], [0,1], [0,1]]
    ch = [[0,0], [1,0], [0,1]]
    _, cd, _ = matrix_data(cp, ch)
    require(any(any(row) for row in cd) and not any(sum(row[j] for row in cd) for j in range(2)), 'cancellation fixture failed')
    require(direct(cp,ch,[1,0],[0,0,0],True) != direct(cp,ch,[1,0],[0,0,0],False), 'distinct cancellation control failed')
    require(direct(cp,ch,[1,0],[0],True,True) == direct(cp,ch,[1,0],[0],False,True), 'shared cancellation identity failed')
    controls['shared_target_cancellation'] = cd
    # Backend admission controls: these are contract rejections, not counterexamples.
    rejections = 0
    for program, state in [([('add',0,0,1)],[1]), ([('add',0,1,0)],[1,2]), ([('add',0,2,1)],[1,2])]:
        try:
            backend.execute(program, state)
        except (ValueError, TypeError):
            rejections += 1
    require(rejections == 3, 'backend contract rejection missing')
    controls['backend_contract_rejections'] = rejections
    return {'format': 'invariant-reader-restoration-v1',
            'status': 'exact scoped interface and finite literal invoice; no new kappa',
            'base_commit': source['base_commit'], 'seed': 50,
            'source_pins_sha256': hashlib.sha256((HERE/'SOURCE-PINS.json').read_bytes()).hexdigest(),
            'fixture': {'permutations_new_from_old': perms, 'readers': readers,
                        'prefix_permutations': [source_permutation(p) for p in prefixes],
                        'reader_defects': defects, 'composed_permutation': source_permutation(product),
                        'input_basis_cases': n+r, 'mixed_or_zero_cases': 2,
                        'clean_temp_registers_in_data': 1, 'clean_accumulator_registers': 1},
            'programs': {'eager_sha256': digest(eager['program']), 'deferred_sha256': digest(deferred['program']),
                         'eager_adds': len(eager['program']), 'deferred_adds': len(deferred['program']),
                         'categories': categories},
            'invoice_eager': invoice_e, 'invoice_deferred': invoice_d,
            'catalytic_wrapper': wrapper, 'independent_symbolic_check': independent.check(),
            'finite_census': census(), 'negative_controls': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='authoring/export mode; normal verification compares stored receipt')
    args = parser.parse_args()
    receipt = make_receipt()
    if args.write:
        args.write.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
        print('WROTE_READER_RESTORATION_RECEIPT', args.write)
        return
    expected = json.loads((HERE/'CERTIFICATE.json').read_text())
    require(receipt == expected, 'stored certificate differs from recomputed evidence')
    print('PASS_INVARIANT_READER_RESTORATION cases=5832 wrapped_adds=210->150 no_new_kappa')

if __name__ == '__main__':
    main()
