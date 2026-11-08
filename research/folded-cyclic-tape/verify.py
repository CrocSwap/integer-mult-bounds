"""Actual Reference Schur fixture through the physical folded caller.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Exact source-matrix expectations use the separately authored allocation
review. Fixture loading and diagnostic host arithmetic are outside the
claimed online tape execution.
"""
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-receipt', type=Path)
    args = parser.parse_args()
    source = load('folded_reference_binding', HERE / 'reference_source.py')
    authenticated = source.authenticated_inputs(HERE)
    raw = {name: authenticated[name] for name in
           (source.REFERENCE, source.EXACT, source.GAUSSIAN, source.INTERVALS)}
    del authenticated
    pages = load('folded_physical_pages', HERE / 'pages.py')
    independent = load('folded_matrix_expectation', HERE / 'allocation_review.py')
    parameters = (9, 1, 1, 2, 3, 32)
    reference = source.make_reference(raw, parameters)
    reference.require_narrow_gap()
    selected = [reference.selected[j] for j in range(9)]
    need(selected == [0, 1, 2, 3, 4, 6, 7, 8, 9], 'original selected targets')
    entries = [[reference.entry('narrow', i, j) for j in selected] for i in selected]
    original = [[Q(entry.value) for entry in row] for row in entries]
    boundary = list(range(1, 9))
    matrix = pages.schur(original, [0], boundary)
    independent_reference, independent_selected, independent_original, expected_matrix = (
        independent.source_fixture(lambda values: source.make_reference(raw, values)))
    need(independent_selected == selected and independent_original == original
         and expected_matrix == matrix, 'independent original Schur construction')
    plan = pages.prepare(matrix, 4, 16, radius=1)
    n, precision, width = plan['n'], plan['precision'], plan['width']
    need((n, precision, width) == (8, 25, 30), 'actual Reference allocation')
    unit = 1 << precision
    right_hand_sides = []
    for offset in (0, 3):
        right_hand_sides.extend((
            [(3*i+offset) % 7 - 3 for i in range(n)],
            [(5*i+offset) % 5 - 2 for i in range(n)]))
    right_hand_sides = [[value*(unit//8) for value in row] for row in right_hand_sides]
    for k in (0, 2):
        need(max(abs(a)+abs(b) for a, b in zip(right_hand_sides[k],
                                              right_hand_sides[k+1])) <= unit,
             'two-component source radius')
    expected_words = [pages.rounded_oracle(plan, rhs) for rhs in right_hand_sides]
    independent_rounded = [independent.apply_rounded(plan, [Q(x, unit) for x in rhs])[0]
                           for rhs in right_hand_sides]
    need(all([Q(x, unit) for x in row] == other
             for row, other in zip(expected_words, independent_rounded)),
         'separate rational completed-row semantics')
    inverse = independent.inverse(matrix)
    need(independent.mul(matrix, inverse) ==
         [[Q(i == j) for j in range(n)] for i in range(n)],
         'every original matrix inverse identity entry')
    exact_outputs = [independent.action(inverse, [Q(x, unit) for x in row])
                     for row in right_hand_sides]
    sys.path[:0] = [str(HERE), str(HERE.parent / 'physical-gaussian-core')]
    import gaussian_sources
    with gaussian_sources.opened():
        from folded_consumer import FoldedSolve
        from factor_tapes import EncodedFactors, emit
        from check_support import no_decode
        from session import erase_marker
        from words import BLANK

        owner = FoldedSolve()
        with EncodedFactors(plan, len(right_hand_sides)) as prepared:
            input_tape = emit([x for row in right_hand_sides for x in row], prepared.counts[3])
            inputs = (*prepared.streams, input_tape, *(c.tape for c in prepared.counts))
            before = [(bytes(t.cells), t.head) for t in inputs]
            private = tuple(dict((id(t), t) for t in owner.private_tapes()).values())
            observed = (*private, *inputs)
            def meters():
                return {name: sum(getattr(t.meter, name) for t in observed)
                        for name in ('reads', 'writes', 'moves')}
            initial = meters()
            with no_decode():
                output = owner.run(*prepared.streams, input_tape, *prepared.counts)
            actual = []
            for _ in range(n * len(right_hand_sides)):
                integer = 0
                for bit in range(width):
                    value = output.read()
                    need(value in (0, 1), 'complete physical binary return')
                    integer |= value << bit
                    output.step(1)
                if integer & (1 << (width-1)):
                    integer -= 1 << width
                actual.append(integer)
            need(output.read() == BLANK, 'exact multiple-RHS return length')
            need(actual == [x for row in expected_words for x in row],
                 'actual physical output equals complete rounded page oracle')
            need(before == [(bytes(t.cells), t.head) for t in inputs],
                 'all borrowed bytes and heads restored')
            with no_decode():
                owner.consume()
            final = meters()
            need(owner.closed and not owner.pending and not owner.pool.live
                 and owner.solver.closed and not owner.solver.pool.live,
                 'closed physical caller and child')
            need(all(t.head == 1 and all(value == BLANK for value in t.cells)
                     for t in private), 'all retained private backing erased at origin')
            calls = dict(owner.solver.word.calls)
            need(calls == {'base': len(right_hand_sides)*n*(2*plan['band']+1), 'fft': 0},
                 'complete actual scalar product count')
            transport = dict(primitive_actions={name: final[name]-initial[name] for name in initial},
                             retained_owned_cells=sum(len(t.cells) for t in private),
                             owned_roles=len(private), borrowed_cells=sum(len(t.cells) for t in inputs),
                             scalar_word_calls=calls, parent_pool_peak=owner.pool.peak,
                             primitive_scope='Finite-alphabet reads/writes/moves through literal return consumption and erasure; host oracles and preparation excluded')
            input_tape.clear()
            erase_marker(input_tape)
        need(all(t.head == 1 and all(value == BLANK for value in t.cells) for t in inputs),
             'prepared factor, descriptor and fixture-input cleanup')

    actual_rows = [[Q(value, unit) for value in actual[k*n:(k+1)*n]]
                   for k in range(len(right_hand_sides))]
    maximum_error = max(abs(actual_rows[k][i]-exact_outputs[k][i])
                        + abs(actual_rows[k+1][i]-exact_outputs[k+1][i])
                        for k in (0, 2) for i in range(n))
    need(maximum_error <= plan['error_bound'] <= Q(1, 1 << 16),
         'actual physical result against original Schur inverse')
    wrap_entries = sum(entry.lift != 0 and entry.value != 0 for row in entries for entry in row)
    need(wrap_entries > 0 and list(reference.holes) == [5], 'genuine wrap and identity hole')
    no_wrap = [[Q(0) if entry.lift else Q(entry.value) for entry in row] for row in entries]
    no_wrap_matrix = [[no_wrap[i][j]-no_wrap[i][0]*no_wrap[0][j]/no_wrap[0][0]
                       for j in boundary] for i in boundary]
    no_wrap_inverse = independent.inverse(no_wrap_matrix)
    wrong_wrap_error = max(abs(actual_rows[k][i]-independent.action(
                              no_wrap_inverse, [Q(x, unit) for x in right_hand_sides[k]])[i])
                           for k in range(len(right_hand_sides)) for i in range(n))
    wrong_order_error = max(abs(actual_rows[k][plan['permutation'][i]]-exact_outputs[k][i])
                            for k in range(len(right_hand_sides)) for i in range(n))
    need(wrong_wrap_error > plan['error_bound'], 'omitted actual-source wrap detected')
    need(wrong_order_error > plan['error_bound'], 'omitted physical unfold detected')
    receipt = dict(status='PASS_PHYSICAL_FOLDED_REFERENCE', base_commit='7c49fe32c55de02c2c873655c804b16e4c3fef0a',
                   source=source.source_receipt(reference), selected_targets=selected,
                   eliminated_sources=[0], boundary_sources=boundary, wrap_entries=wrap_entries,
                   identity_holes=list(reference.holes), right_hand_sides=len(right_hand_sides),
                   allocation={name: str(plan[name]) if isinstance(plan[name], Q) else plan[name]
                               for name in ('n','band','target','radius','gap','mass','precision','width',
                                            'coefficient_constant','solve_constant','error_bound',
                                            'forward_radius','solution_radius')},
                   maximum_component_l1_error=str(maximum_error),
                   maximum_error_float=float(maximum_error),
                   wrong_wrap_error=str(wrong_wrap_error), wrong_order_error=str(wrong_order_error),
                   output_words=actual,
                   output_sha256=sha256(json.dumps(actual,separators=(',',':')).encode()).hexdigest(),
                   transport=transport,
                   source_sha256={name: sha256((HERE/name).read_bytes()).hexdigest()
                                  for name in ('folded_consumer.py','pages.py','factor_tapes.py',
                                               'allocation_review.py','reference_source.py')},
                   controls=['omit_periodic_entries','omit_unfold'],
                   scope='One exact source-bound Schur solve; no Schur RHS assembly/recovery or full periodic inverse')
    source.clear_reference(reference)
    source.clear_reference(independent_reference)
    if args.write_receipt:
        with args.write_receipt.open('x') as destination:
            json.dump(receipt, destination, indent=2, sort_keys=True)
            destination.write('\n')
    print(json.dumps(receipt, sort_keys=True))
    print('PASS_PHYSICAL_FOLDED_REFERENCE')


if __name__ == '__main__':
    main()
