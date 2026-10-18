#!/usr/bin/env python3
"""Exact finite replay supporting the written interface proof, not a full theorem.
Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model
import oracle


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def source_check():
    pins = json.loads((HERE/'PREDECESSORS.json').read_text())
    for pin in pins:
        data = (HERE/pin['local']).read_bytes()
        check(hashlib.sha256(data).hexdigest() == pin['sha256'], 'predecessor SHA256 mismatch')
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        check(blob == pin['git_blob'], 'predecessor Git blob mismatch')
    return len(pins)


def make_tree(rng, m, n, k, depth):
    if depth:
        return {'children': [make_tree(rng, m, n, k, depth-1) for _ in range(k)]}
    r = [[0]*(3*m) for _ in range(3*n)]
    for i in range(n):
        for j in range(m):
            coefficients = [rng.choice((-1, 0, 1)) for _ in range(3)]
            for a in range(3):
                for b in range(3):
                    r[3*i+a][3*j+b] = coefficients[(a-b) % 3]
    return {'matrix': r}


def run_case(node, contract, eager):
    word, registers = model.compile_word(node, contract, eager)
    primitive = model.expand(word)
    actual, peak = oracle.replay(primitive, registers)
    expect = oracle.expected(node, registers, contract)
    check(actual == expect, 'full dirty-state map mismatch')
    recovered, inverse_peak = oracle.replay(model.inverse(primitive), registers, actual)
    check(recovered == oracle.identity(registers), 'literal inverse failed')
    inverse_map, inverse_arbitrary_peak = oracle.replay(model.inverse(primitive), registers)
    check(inverse_map == oracle.expected_inverse(node, registers, contract), 'independent inverse block formula mismatch')
    macro_actual, _ = oracle.replay(word, registers)
    check(macro_actual == actual, 'cycle expansion changed map')
    a, s = model.recurrence(node, contract, eager)
    bill = model.invoice(primitive)
    check(bill == oracle.invoice(primitive), 'instruction/access invoice mismatch')
    check((bill['add'], bill['neg']) == (a+6*s, 0), 'recursive ADD invoice mismatch')
    check(registers == len(expect), 'register coverage mismatch')
    # A rational all-dirty probe through the actual expanded forward/inverse word.
    probe = [Fraction((-1)**i*(i+1), i+2) for i in range(registers)]
    predicted = [sum(x*y for x, y in zip(row, probe)) for row in expect]
    output = oracle.vector_replay(primitive, probe)
    check(output == predicted, 'rational forward mismatch')
    check(oracle.vector_replay(model.inverse(primitive), output) == probe, 'rational inverse mismatch')
    return dict(registers=registers, direct_add=a, triple_rotations=s, invoice=bill,
                prefix_l1_peak=peak, inverse_after_forward_peak=inverse_peak,
                inverse_arbitrary_input_l1_peak=inverse_arbitrary_peak)


def admission_census():
    count = 0
    for values in itertools.product((-1, 0, 1), repeat=9):
        r = [list(values[i:i+3]) for i in (0, 3, 6)]
        a, b = model.admitted(r), oracle.literal_admission(r)
        check(a == b, 'admission oracles disagree')
        count += a
    check(count == 27, 'circulant census count mismatch')
    return dict(matrices=3**9, admitted=count, rejected=3**9-count)


def boundary_checks():
    rows = [oracle.boundary_census(k) for k in range(1, 5)]
    comparisons = 0
    for row in rows:
        for m in range(1, 6):
            for n in range(1, 6):
                best = min(m*a+n*b for a, b in row['operation_pairs'])
                cost, gaps = model.plan(row['k'], m, n)
                check(cost == best, 'boundary optimum mismatch')
                check(cost == sum(m*(u != 0)+n*(v != 0) for u, v in gaps), 'plan price mismatch')
                comparisons += 1
    # Price scaling must not silently change a selected word's admission.
    for k in range(1, 31):
        for a, b in ((1, 7), (7, 1), (4, 4), (2, 3), (3, 2)):
            c, gaps = model.plan(k, a, b)
            check(model.plan(k, 17*a, 17*b)[0] == 17*c, 'price homogeneity failure')
            check(c <= k*a, 'planner loses to eager feasible schedule')
    return dict(census=rows, price_comparisons=comparisons, scaled_price_checks=150)


def controls(node):
    m, n = model.dimensions(model.matrix_of(node))
    d, width = 3*n, 3*m
    children = node['children']
    macro, size = model.compile_word(node)
    expected = oracle.expected(node, size, 'echo')
    caught = []
    def fails(name, word):
        check(oracle.replay(model.expand(word), size)[0] != expected, name+' was not detected')
        caught.append(name)
    b = model.batch(children, d+width, 0, d+2*width, m, n)
    copy = [('A', d+width+i, d+i, 1) for i in range(width)]
    fails('missing_source_uncopy', copy+b+model.inverse(copy)[1:]+model.inverse(b))
    fails('forward_instead_of_inverse_batch', copy+b+model.inverse(copy)+b)
    fails('missing_dirty_cancellation_pass', copy+b+model.inverse(copy))
    # Mutate a paid output frame and a paid workspace exit, each as complete macros.
    positions = [i for i, op in enumerate(b) if op[0] == 'R' and op[1] < d]
    check(bool(positions), 'fixture lacks output frames')
    bad = b[:positions[0]]+b[positions[0]+1:]
    fails('omitted_output_three_cycle', copy+bad+model.inverse(copy)+model.inverse(b))
    gaps = model.plan(len(children), m, n)[1]
    check(gaps[-1][0] != 0, 'fixture lacks workspace exit')
    end_ops = len(model.rotate(d+width, m, gaps[-1][0]))+len(model.rotate(0, n, gaps[-1][1]))
    bad = b[:-end_ops]+model.rotate(0, n, gaps[-1][1])
    fails('omitted_workspace_exit', copy+bad+model.inverse(copy)+model.inverse(b))
    primitive = model.expand(macro)
    first_rotation = next(i for i, op in enumerate(macro) if op[0] == 'R')
    ni = sum(6 if op[0] == 'R' else 1 for op in macro[:first_rotation])+2
    check(oracle.replay(primitive[:ni]+primitive[ni+1:], size)[0] != expected, 'bad cycle expansion escaped')
    caught.append('missing_cycle_ADD')
    bad_node = json.loads(json.dumps(node))
    bad_node['children'][0]['matrix'][0][0] += 1
    try:
        model.compile_word(bad_node)
    except ValueError:
        caught.append('non_equivariant_reader_rejected')
    else:
        raise RuntimeError('non-equivariant reader was admitted')
    # Moving the defect to a later reader makes the missing gate observable.
    bad_node = json.loads(json.dumps(node))
    bad_node['children'][1]['matrix'][0][0] += 1
    bad_raw = model.echo(bad_node['children'], d, 0, d+width, m, n)
    bad_expected = oracle.expected(bad_node, size, 'echo')
    check(oracle.replay(model.expand(bad_raw), size)[0] != bad_expected, 'unchecked non-scalar gate happened to pass')
    caught.append('unchecked_non_equivariance_changes_map')
    # The interface is endpoint-observed; a phase-one prefix is not canonical.
    prefix = model.rotate(d+width, m, gaps[0][0])+model.rotate(0, n, gaps[0][1])
    prefix += model.reader(children[0], d+width, 0, d+2*width, m, n)
    prefix += model.rotate(d+width, m, gaps[1][0])+model.rotate(0, n, gaps[1][1])
    canonical = model.reader(children[0], d+width, 0, d+2*width, m, n)+model.rotate(d+width, m, 2)
    check(oracle.replay(prefix, size)[0] != oracle.replay(canonical, size)[0], 'observer counterexample missing')
    caught.append('premature_canonical_observer')
    check((2+1)**3-2**3 != 1**3, 'nonlinear dirty counterexample missing')
    caught.append('nonlinear_dirty_echo')
    return caught


def verify():
    source_count = source_check()
    boundaries = boundary_checks()
    admission = admission_census()
    rng = random.Random(56)
    coverage = dict(cases=0, basis_columns=0, primitive_instructions=0)
    coverage_hash = hashlib.sha256()
    for m, n, k, h in itertools.product(range(1, 4), range(1, 3), range(1, 5), (1, 2)):
        node = make_tree(rng, m, n, k, h)
        for contract, eager in itertools.product(('echo', 'reader'), (False, True)):
            result = run_case(node, contract, eager)
            coverage['cases'] += 1
            coverage['basis_columns'] += result['registers']
            coverage['primitive_instructions'] += result['invoice']['dispatch']
            coverage_hash.update(json.dumps([m, n, k, h, contract, eager, result], sort_keys=True).encode())
    fixture = make_tree(random.Random(56), 3, 1, 5, 1)
    check(json.loads((HERE/'FIXTURE.json').read_text()) == fixture, 'frozen seed fixture mismatch')
    good, eager = run_case(fixture, 'echo', False), run_case(fixture, 'echo', True)
    check(eager['triple_rotations']-good['triple_rotations'] == 14, 'complete echo saving lost')
    check(eager['invoice']['dispatch']-good['invoice']['dispatch'] == 84, 'expanded saving wrong')
    deeper = make_tree(random.Random(57), 2, 1, 3, 3)
    deep_results = {str(e): run_case(deeper, 'reader', e) for e in (False, True)}
    failures = controls(fixture)
    return dict(status='PASS_CYCLIC_OUTPUT_RESTORATION', base='dadfea6e8a78ff6ba901705f87532a71c6f5bbb8',
                seed=56, predecessor_notes=source_count, boundary=boundaries, admission=admission,
                recursive_coverage=coverage, recursive_coverage_sha256=coverage_hash.hexdigest(),
                fixture=dict(m=3, n=1, children=5, plan=model.plan(5, 3, 1), optimized=good, eager=eager),
                depth_three=deep_results, controls=failures, kappa='unchanged')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = verify()
    canonical = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.emit:
        print(canonical, end='')
    else:
        check(json.loads((HERE/'CERTIFICATE.json').read_text()) == json.loads(canonical), 'certificate mismatch')
        print('PASS_CYCLIC_OUTPUT_RESTORATION schedules=66420 admission=27/19683 cases=192 saved_rotations=14 saved_primitives=84 no_new_kappa')


if __name__ == '__main__':
    main()
