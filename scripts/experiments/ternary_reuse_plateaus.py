#!/usr/bin/env python3
"""Exact equal-span plateau compiler for the PR7 ternary producer.

Research prototype: imports PR7 files from a caller-supplied directory.
It never changes that snapshot or a published multiplication certificate.
"""
from collections import defaultdict, deque
from fractions import Fraction
from functools import lru_cache
from math import comb
from pathlib import Path
from types import SimpleNamespace
import argparse
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[2]


@lru_cache(None)
def rational_basis(rows):
    if not rows:
        return ()
    matrix = [list(map(Fraction, row)) for row in rows]
    rank = 0
    for col in range(len(matrix[0])):
        found = next((j for j in range(rank, len(matrix)) if matrix[j][col]), None)
        if found is None:
            continue
        matrix[rank], matrix[found] = matrix[found], matrix[rank]
        leading = matrix[rank][col]
        matrix[rank] = [x/leading for x in matrix[rank]]
        for j, row in enumerate(matrix):
            if j != rank and row[col]:
                factor = row[col]
                matrix[j] = [x-factor*y for x, y in zip(row, matrix[rank])]
        rank += 1
        if rank == len(matrix):
            break
    return tuple(tuple(row) for row in matrix[:rank])


def kernel_basis(rows, dimension):
    reduced = rational_basis(rows)
    pivots = [next(j for j, x in enumerate(row) if x) for row in reduced]
    vectors = []
    for free in range(dimension):
        if free not in pivots:
            vector = [Fraction(int(j == free)) for j in range(dimension)]
            for row, pivot in zip(reduced, pivots):
                vector[pivot] = -row[free]
            vectors.append(tuple(vector))
    return rational_basis(tuple(vectors))


def core_constraints(h, core):
    first, *rest = sorted(core)
    equations = [tuple(int(j == point)-int(j == first) for j in range(h))
                 for point in rest]
    equations.append(tuple(1-5*int(j == first) for j in range(h)))
    return tuple(equations)


def equal_span_clusters(c, enlarged=False, core2_only=False):
    labels, cores = {}, {}
    for n in sorted(c.active):
        if c.args[n] is None:
            labels[n] = (tuple(Fraction(int(i in c.inputs[n-1])) for i in range(c.h)),)
            cores[n] = frozenset(c.inputs[n-1])
        else:
            a, b = c.args[n]
            labels[n] = rational_basis(labels[a]+labels[b])
            cores[n] = cores[a] & cores[b]
    if enlarged:
        required = {n: () for n in c.active}
        for output, target in c.side:
            triple = c.inputs[target]
            normal = tuple(5*int(j in triple)-2 for j in range(c.h))
            node = c.outputs[output]
            required[node] += (normal,)
        for output, core in c.totals:
            node = c.outputs[output]
            required[node] += core_constraints(c.h, core)
        for n in sorted(c.active, reverse=True):
            required[n] = rational_basis(required[n])
            for p in c.args[n] or ():
                required[p] = rational_basis(required[p]+required[n])
        for n in sorted(c.active):
            if core2_only and len(cores[n]) != 2:
                continue
            constraints = core_constraints(c.h, cores[n])+required[n]
            larger = kernel_basis(constraints, c.h)
            assert rational_basis(labels[n]+larger) == larger
            labels[n] = larger
        for n in c.active:
            for p in c.args[n] or ():
                assert rational_basis(labels[p]+labels[n]) == labels[n]
    by_label = defaultdict(list)
    for n in sorted(c.active):
        key = ('fixed', n) if core2_only and len(cores[n]) != 2 else ('label', labels[n])
        by_label[key].append(n)
    # Distinct nested subspaces have strictly different dimensions, so
    # contracting all equal labels (even disconnected ones) is acyclic.
    groups = {nodes[0]: nodes for nodes in by_label.values()}
    home = {n: root for root, nodes in groups.items() for n in nodes}
    return labels, groups, home


def ternary_rank_pivots(matrix):
    basis = {}
    independent_rows = []
    for i, original in enumerate(matrix):
        row = list(original)
        for pivot in sorted(basis):
            factor = row[pivot]
            if factor:
                row = [(a-factor*b) % 3 for a, b in zip(row, basis[pivot])]
        pivot = next((j for j, value in enumerate(row) if value), None)
        if pivot is not None:
            inverse = row[pivot]  # 1^-1=1, 2^-1=2 in F3.
            basis[pivot] = [(value*inverse) % 3 for value in row]
            independent_rows.append(i)
    return independent_rows, sorted(basis)


def inverse_mod3(matrix):
    n = len(matrix)
    a = [[x % 3 for x in row]+[int(i == j) for j in range(n)]
         for i, row in enumerate(matrix)]
    for col in range(n):
        found = next((j for j in range(col, n) if a[j][col]), None)
        assert found is not None
        a[col], a[found] = a[found], a[col]
        factor = a[col][col]
        a[col] = [(factor*x) % 3 for x in a[col]]
        for j in range(n):
            if j != col and a[j][col]:
                factor = a[j][col]
                a[j] = [(x-factor*y) % 3 for x, y in zip(a[j], a[col])]
    assert all(row[:n] == [int(i == j) for j in range(n)] for i, row in enumerate(a))
    return [row[n:] for row in a]


def plateau_plan(c, labels, groups, home):
    incoming = {g: set() for g in groups}
    outgoing = {g: set() for g in groups}
    successors = {g: set() for g in groups}
    predecessors = {g: set() for g in groups}
    for n in sorted(c.active):
        for p in c.args[n] or ():
            if home[p] != home[n]:
                incoming[home[n]].add(p)
                outgoing[home[p]].add((p, ('gate', home[n])))
                successors[home[p]].add(home[n])
                predecessors[home[n]].add(home[p])
    for target, n in c.outputs.items():
        outgoing[home[n]].add((n, ('output', target)))
    ready = deque(sorted(g for g in groups if not predecessors[g]))
    plan = []
    while ready:
        g = ready.popleft()
        nodes = groups[g]
        sources = sorted(incoming[g])
        if c.args[nodes[0]] is None:
            assert len(nodes) == 1
            sources = [nodes[0]]
        index = {n: i for i, n in enumerate(sources)}
        local = {n: [int(i == j) for j in range(len(sources))] for n, i in index.items()}
        for n in nodes:
            if c.args[n]:
                a, b = c.args[n]
                local[n] = [(x+y) % 3 for x, y in zip(local[a], local[b])]
        uses = sorted(outgoing[g])
        matrix = [local[n] for n, _ in uses]
        independent, pivots = ternary_rank_pivots(matrix)
        assert len(independent) == len(pivots)
        square = [[matrix[i][j] for j in pivots] for i in independent]
        inverse = inverse_mod3(square)
        coefficients = []
        for row in matrix:
            coefs = [sum(row[pivots[j]]*inverse[j][k] for j in range(len(pivots))) % 3
                     for k in range(len(pivots))]
            assert all(sum(coefs[k]*matrix[independent[k]][j] for k in range(len(pivots))) % 3 == row[j]
                       for j in range(len(sources)))
            coefficients.append(coefs)
        plan.append(dict(group=g, nodes=nodes, label=labels[nodes[0]], sources=sources,
                         uses=uses, matrix=matrix, independent=independent, pivots=pivots,
                         inverse=inverse, coefficients=coefficients))
        for following in sorted(successors[g]):
            predecessors[following].remove(g)
            if not predecessors[following]:
                ready.append(following)
    assert len(plan) == len(groups), 'Equal-span contraction created a cycle'
    return plan


def compile_plan(c, plan):
    size = 0
    edges = {}
    sources = {}
    outputs = {}
    frame = []
    gates = []
    for block in plan:
        nodes = block['nodes']
        if c.args[nodes[0]] is None:
            ins = [size]
            sources[c.inputs[nodes[0]-1]] = size
            size += 1
            frame.append(())
        else:
            ins = [edges[n, block['group']] for n in block['sources']]
        rank = len(block['pivots'])
        outs = [None]*len(block['uses'])
        for i, j in zip(block['independent'], block['pivots']):
            outs[i] = ins[j]
        fresh = []
        for i in range(len(outs)):
            if outs[i] is None:
                outs[i] = size
                fresh.append(size)
                size += 1
                frame.append(())
        slots = set(ins+outs)
        assert len(slots) == len(ins)+len(outs)-rank
        for slot in slots:
            assert rational_basis(frame[slot]+block['label']) == block['label']
            frame[slot] = block['label']
        for (n, use), slot in zip(block['uses'], outs):
            if use[0] == 'gate':
                edges[n, use[1]] = slot
            else:
                outputs[use[1]] = slot
        gates.append(dict(block=block, ins=ins, outs=outs, fresh=fresh))
    node_labels = {n: block['label'] for block in plan for n in block['nodes']}
    assert all(frame[outputs[t]] == node_labels[c.outputs[t]] for t in outputs)
    return dict(roles=size, sources=sources, outputs=outputs, gates=gates)


def plan_label(node, plan):
    # Only used by this small exact prototype, not the intended large compiler.
    return next(block['label'] for block in plan if node in block['nodes'])


def add3(a, b):
    a1, a2 = a
    b1, b2 = b
    aa, bb = a1 | a2, b1 | b2
    return ((b1 & ~aa) | (a1 & ~bb) | (a2 & b2),
            (b2 & ~aa) | (a2 & ~bb) | (a1 & b1))


def linear3(coefficients, values):
    result = (0, 0)
    for coefficient, value in zip(coefficients, values):
        if coefficient:
            result = add3(result, value if coefficient == 1 else (value[1], value[0]))
    return result


def apply_gate(values, gate, inverse=False):
    b, ins, outs = gate['block'], gate['ins'], gate['outs']
    pivots, independent = b['pivots'], b['independent']
    if not inverse:
        saved = [values[slot] for slot in ins]
        for i, j in zip(independent, pivots):
            values[ins[j]] = linear3(b['matrix'][i], saved)
        leading = [values[ins[j]] for j in pivots]
        for i, slot in enumerate(outs):
            if i not in independent:
                values[slot] = add3(values[slot], linear3(b['coefficients'][i], leading))
    else:
        leading = [values[ins[j]] for j in pivots]
        for i, slot in enumerate(outs):
            if i not in independent:
                correction = linear3(b['coefficients'][i], leading)
                values[slot] = add3(values[slot], (correction[1], correction[0]))
        residuals = []
        for i, value in zip(independent, leading):
            correction = linear3([coef if j not in pivots else 0
                                  for j, coef in enumerate(b['matrix'][i])],
                                 [values[slot] for slot in ins])
            residuals.append(add3(value, (correction[1], correction[0])))
        recovered = [linear3(row, residuals) for row in b['inverse']]
        for j, value in zip(pivots, recovered):
            values[ins[j]] = value


def audit_coefficients(c, code):
    values = [(0, 0)]*code['roles']
    for triple, slot in code['sources'].items():
        values[slot] = (1 << (c.variables[triple]-1), 0)
    for gate in code['gates']:
        apply_gate(values, gate)
    for target, slot in code['outputs'].items():
        assert values[slot] == (c.support[c.outputs[target]], 0)
    for gate in reversed(code['gates']):
        apply_gate(values, gate, inverse=True)
    expected = [(0, 0)]*code['roles']
    for triple, slot in code['sources'].items():
        expected[slot] = (1 << (c.variables[triple]-1), 0)
    assert values == expected
    # Every arbitrary scratch basis at once: no sampling of dirty values.
    if code['roles'] > 20000:
        return dict(all_producer_coefficients_exact=True,
                    dirty_inverse='Follows from each checked invertible completion; whole-bank symbolic stress test omitted above 20000 roles.')
    values = [(1 << i, 0) for i in range(code['roles'])]
    expected = list(values)
    for gate in code['gates']:
        apply_gate(values, gate)
    for gate in reversed(code['gates']):
        apply_gate(values, gate, inverse=True)
    assert values == expected
    return dict(all_producer_coefficients_exact=True, every_dirty_basis_restored_by_inverse=True)


def audit_wrapper(c, code, require_identity=True):
    """All input and dirty-scratch basis symbols, not random evaluations."""
    v, r = len(c.inputs), code['roles']
    rows = [(1 << i, 0) for i in range(2*v+r)]
    x, y, z = rows[:v], rows[v:2*v], rows[2*v:]
    original = (list(x), list(y), list(z))
    def update(bank, index, value, sign=1):
        bank[index] = add3(bank[index], value if sign == 1 else (value[1], value[0]))
    def mix(sign):
        for gate in code['gates'] if sign == 1 else reversed(code['gates']):
            apply_gate(z, gate, inverse=sign != 1)
    def copy(sign, bank):
        for triple, slot in code['sources'].items():
            update(z, slot, bank[c.variables[triple]-1], sign)
    def inject(sign, bank):
        for output, target in c.side:
            update(bank, target, z[code['outputs'][output]], -sign)
    def scatter(sign, bank):
        for output, core in c.totals:
            for target, triple in enumerate(c.inputs):
                if set(core) <= set(triple):
                    update(bank, target, z[code['outputs'][output]], sign)
    def invoke(source, target, reverse=False):
        ops = [(mix, 1), (scatter, -1), (inject, -1), (mix, -1),
               (copy, 1), (mix, 1), (scatter, 1), (inject, 1), (mix, -1), (copy, -1)]
        if reverse:
            ops = [(op, -sign) for op, sign in reversed(ops)]
        for op, sign in ops:
            if op is mix:
                op(sign)
            else:
                op(sign, source if op is copy else target)
    signal_map = [(0, 0)]*v
    for output, target in c.side:
        signal_map[target] = add3(signal_map[target], (0, c.support[c.outputs[output]]))
    for output, core in c.totals:
        for target, triple in enumerate(c.inputs):
            if set(core) <= set(triple):
                signal_map[target] = add3(signal_map[target], (c.support[c.outputs[output]], 0))
    is_identity = signal_map == [(1 << j, 0) for j in range(v)]
    if require_identity:
        assert is_identity
    invoke(x, y)
    assert x == original[0] and z == original[2]
    assert y == [add3(a, b) for a, b in zip(original[1], signal_map)]
    invoke(x, y, reverse=True)
    assert (x, y, z) == original
    if require_identity:
        invoke(x, y)
        invoke(y, x, reverse=True)
        invoke(x, y)
        x[:] = [(b, a) for a, b in x]
        assert x == original[1] and y == original[0] and z == original[2]
    return dict(all_basis_symbols=2*v+r, forward_inverse_exact=True,
                intended_central_minus_side_map_exact=True,
                intended_map_is_identity=is_identity,
                dirty_wrapper_restores_every_scratch=True,
                corrected_three_shear_exchange=require_identity)



def audit_frames(c, code):
    """Every physical edge, in both invocation directions, over exact Q."""
    h, v, r = c.h, len(c.inputs), code['roles']
    zero = ()
    full = tuple(tuple(Fraction(int(i == j)) for j in range(h)) for i in range(h))
    lines = [(tuple(Fraction(int(i in triple)) for i in range(h)),) for triple in c.inputs]
    @lru_cache(None)
    def perp(space):
        return kernel_basis(tuple(tuple(x-Fraction(2, 25)*sum(row) for x in row)
                                  for row in space), h)
    @lru_cache(None)
    def transition(old, new):
        larger = new if len(new) >= len(old) else old
        assert rational_basis(old+new) == larger
        return abs(len(new)-len(old)), max(0, len(old)-len(new))
    results = []
    for inverse in (False, True):
        frames = list(lines)+[zero]*(v+r)
        total = loss = 0
        def gate(slots, label):
            nonlocal total, loss
            for slot in set(slots):
                rank, decrease = transition(frames[slot], label)
                total += rank
                loss += decrease
                frames[slot] = label
        def mix(mode, reverse=False):
            for item in reversed(code['gates']) if reverse else code['gates']:
                label = zero if mode == 'low' else full if mode == 'high' else item['block']['label']
                if mode == 'perp':
                    label = perp(label)
                gate([2*v+slot for slot in item['ins']+item['outs']], label)
        def copy(bank, mode):
            for triple, slot in code['sources'].items():
                target = c.variables[triple]-1
                label = zero if mode == 'low' else full if mode == 'high' else lines[target]
                if mode == 'perp':
                    label = perp(label)
                gate((bank+target, 2*v+slot), label)
        def inject(bank, mode):
            pieces = [[] for _ in c.inputs]
            for output, target in c.side:
                pieces[target].append(2*v+code['outputs'][output])
            for target, slots in enumerate(pieces):
                label = zero if mode == 'low' else full if mode == 'high' else lines[target]
                if mode == 'perp':
                    label = perp(label)
                gate([bank+target]+slots, label)
        def scatter(bank, label):
            gate(list(range(bank, bank+v))+[2*v+code['outputs'][o] for o, _ in c.totals], label)
        if not inverse:
            mix('low'); scatter(v, zero); inject(v, 'low'); mix('low', True)
            copy(0, 'line'); mix('node'); scatter(v, zero); inject(v, 'perp')
            mix('high', True); copy(0, 'high')
        else:
            copy(v, 'low'); mix('low'); inject(0, 'line'); scatter(0, full)
            mix('perp', True); copy(v, 'perp'); mix('high'); inject(0, 'high')
            scatter(0, full); mix('high', True)
        for target in range(v):
            gate([target], full)
            gate([v+target], perp(lines[target]))
        gate(range(2*v, 2*v+r), full)
        assert loss == len(c.totals)*(h-2)
        assert total == (2*v+r)*h-2*v+2*loss
        results.append(dict(inverse=inverse, total_rank=total, loss=loss,
                            all_physical_edges_nested=True))
    return results


def local_context_control(n, producer):
    """Positive compiler saving on one context, with its actual nonidentity map."""
    local = producer(n)
    local.verify()
    total = local.triple(list(range(n)), local.variables)[()]
    active = set(local.active)
    stack = [total]
    while stack:
        node = stack.pop()
        if node in active:
            continue
        active.add(node)
        stack.extend(local.args[node] or ())
    inputs = [(0, 1)+tuple(i+2 for i in triple) for triple in local.inputs]
    outputs = {j: local.outputs[triple] for j, triple in enumerate(local.inputs)}
    outputs[len(inputs)] = total
    additions = sum(local.args[node] is not None for node in active)
    c = SimpleNamespace(h=n+2, inputs=inputs, variables={t:i+1 for i,t in enumerate(inputs)},
                        args=local.args, support=local.support, active=active,
                        outputs=outputs, side=[(j,j) for j in range(len(inputs))],
                        totals=[(len(inputs),(0,1))], additions=additions,
                        roles=additions+len(outputs))
    labels, groups, home = equal_span_clusters(c, enlarged=True, core2_only=True)
    code = compile_plan(c, plateau_plan(c, labels, groups, home))
    coefficients = audit_coefficients(c, code)
    frames = audit_frames(c, code)
    wrapper = audit_wrapper(c, code, require_identity=False)
    return dict(local_ground_size=n, ambient_h=n+2, input_count=len(inputs),
                original_roles=c.roles, new_roles=code['roles'],
                saved_roles=c.roles-code['roles'], producer_coefficients=coefficients,
                physical_frames=frames, dirty_wrapper=wrapper,
                scope='One common-pair context only. The intended central-minus-side map is checked directly; it is not asserted to be the full identity.')


def audit(h, producer, enlarged=False, labeler=None, core2_only=False):
    started = time.monotonic()
    c = producer(h)
    c.verify_map()
    if labeler is None:
        labels, groups, home = equal_span_clusters(c, enlarged=enlarged or core2_only, core2_only=core2_only)
        label_check = {'source': 'unique-common-pair enlarged' if core2_only else 'core-enlarged' if enlarged else 'source-spans'}
    else:
        labels, label_check = labeler(c)
        assert not label_check['degenerate_nodes']
        by_label = defaultdict(list)
        for node in sorted(c.active):
            by_label[labels[node]].append(node)
        groups = {nodes[0]: nodes for nodes in by_label.values()}
        home = {node: root for root, nodes in groups.items() for node in nodes}
    plan = plateau_plan(c, labels, groups, home)
    code = compile_plan(c, plan)
    checks = audit_coefficients(c, code)
    physical_frames = audit_frames(c, code)
    wrapper = audit_wrapper(c, code) if h <= 10 else {'omitted': 'Large full dirty-basis wrapper; local exact inversion and JLV suffice for the written general proof.'}
    sizes = defaultdict(int)
    for group in groups.values():
        sizes[len(group)] += 1
    return dict(h=h, producer=producer.__name__, core2_only=core2_only, label_check=label_check, enlarged_frames=enlarged, inputs=len(c.inputs), original_additions=c.additions,
                output_uses=len(c.outputs), original_roles=c.roles, new_roles=code['roles'],
                saved_roles=c.roles-code['roles'], cluster_count=len(groups),
                largest_cluster=max(map(len, groups.values())),
                cluster_size_histogram=dict(sorted(sizes.items())),
                forward_frames_nested=True, reverse_complement_frames_nested=True,
                central_loss_unchanged=comb(h, 2)*(h-2),
                coefficient_checks=checks, physical_frames=physical_frames,
                wrapper_checks=wrapper, elapsed_seconds=time.monotonic()-started)


if __name__ == '__main__':
    from math import comb
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pr7-scripts', type=Path, default=ROOT/'scripts')
    parser.add_argument('--h', nargs='+', type=int, default=[8, 10])
    parser.add_argument('--enlarged', action='store_true')
    parser.add_argument('--direct', action='store_true')
    parser.add_argument('--core2-only', action='store_true')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT/'scripts'))
    sys.path.insert(0, str(args.pr7_scripts))
    from prime_field_checks import SmallProducer
    if args.direct:
        from ternary_target_circuit import DirectProducer, hybrid_labels
    for h in args.h:
        result = audit(h, DirectProducer if args.direct else SmallProducer,
                       enlarged=args.enlarged, labeler=hybrid_labels if args.direct else None, core2_only=args.core2_only)
        print(json.dumps(result, sort_keys=True), flush=True)
