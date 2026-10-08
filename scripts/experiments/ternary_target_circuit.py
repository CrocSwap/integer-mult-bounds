#!/usr/bin/env python3
"""Direct intersection-two producer and exact small rational-frame controls.

Research prototype only. The recursive scalar templates come from the existing
intersection_circuit experiment. The F3 five-set motif and retained pair totals
follow Zhihao Chen's PR #7, head 6725c6a17b17871a35353fd29157f4ed851bc114.
Nodes used by one side target and no center may use that target's whole
orthogonal complement; this repairs degenerate source spans without a descent.
No target-size construction or new multiplication exponent is asserted.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
import argparse
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from exclusion_circuit import ExclusionCircuit
from intersection_circuit import build


@lru_cache(None)
def basis(rows):
    if not rows:
        return ()
    a = [list(map(Q, row)) for row in rows]
    rank = 0
    for col in range(len(a[0])):
        candidate = next((j for j in range(rank, len(a)) if a[j][col]), None)
        if candidate is None:
            continue
        a[rank], a[candidate] = a[candidate], a[rank]
        pivot = a[rank][col]
        a[rank] = [x/pivot for x in a[rank]]
        for j, row in enumerate(a):
            if j != rank and row[col]:
                factor = row[col]
                a[j] = [x-factor*y for x, y in zip(row, a[rank])]
        rank += 1
        if rank == len(a):
            break
    return tuple(tuple(row) for row in a[:rank])


def kernel(rows, h):
    rows = basis(rows)
    pivots = [next(i for i, x in enumerate(row) if x) for row in rows]
    out = []
    for j in range(h):
        if j not in pivots:
            v = [Q(int(i == j)) for i in range(h)]
            for row, pivot in zip(rows, pivots):
                v[pivot] = -row[j]
            out.append(tuple(v))
    return basis(tuple(out))


@lru_cache(None)
def gram(U):
    sums = [sum(u) for u in U]
    return tuple(tuple(sum(x*y for x, y in zip(u, v))-Q(2, 25)*sums[i]*sums[j]
                       for j, v in enumerate(U)) for i, u in enumerate(U))


@lru_cache(None)
def nonsingular(U):
    return len(basis(gram(U))) == len(U)


def perp(U, h):
    return kernel(tuple(tuple(x-Q(2, 25)*sum(u) for x in u) for u in U), h)


class DirectProducer:
    """SmallProducer-compatible direct side transform plus retained totals."""
    add = ExclusionCircuit.add
    compile = ExclusionCircuit.compile

    def __init__(self, h):
        assert h >= 8
        self.h = h
        self.inputs = list(combinations(range(h), 5))
        self.variables = {t: i+1 for i, t in enumerate(self.inputs)}
        self.support = [0]+[1 << i for i in range(len(self.inputs))]
        self.args = [None]*len(self.support)
        self.lookup = {s: i for i, s in enumerate(self.support)}
        self.outputs, self.side, self.totals = {}, [], []
        self.template_counts = {}
        for degree in (5, 2):
            template = build(h, 5, degree, 2)
            mapping = {0: 0}
            for node in template.active:
                if template.args[node]:
                    a, b = template.args[node]
                    mapping[node] = self.add(mapping[a], mapping[b])
                else:
                    mapping[node] = self.variables[template.inputs[node-1]]
            for target, node in zip(template.targets, template.outputs):
                index = len(self.outputs)
                self.outputs[index] = mapping[node]
                if degree == 5:
                    self.side.append((index, self.variables[target]-1))
                else:
                    self.totals.append((index, target))
            self.template_counts[degree] = template.additions
        self.active = set()
        stack = list(self.outputs.values())
        while stack:
            node = stack.pop()
            if node and node not in self.active:
                self.active.add(node)
                stack.extend(self.args[node] or ())
        self.additions = sum(self.args[n] is not None for n in self.active)
        self.roles = self.additions+len(self.outputs)

    def verify_map(self):
        for node in self.active:
            if self.args[node]:
                a, b = self.args[node]
                assert a < node and b < node
                assert not self.support[a] & self.support[b]
                assert self.support[node] == self.support[a] | self.support[b]
        for i, target in self.side:
            s = set(self.inputs[target])
            expected = sum(1 << j for j, t in enumerate(self.inputs) if len(s & set(t)) == 2)
            assert self.support[self.outputs[i]] == expected
        for i, pair in self.totals:
            expected = sum(1 << j for j, t in enumerate(self.inputs) if set(pair) <= set(t))
            assert self.support[self.outputs[i]] == expected
        for intersection in range(6):
            assert (comb(intersection, 2)-int(intersection == 2)) % 3 == int(intersection == 5)
        return dict(h=self.h, inputs=len(self.inputs), additions=self.additions,
                    outputs=len(self.outputs), roles=self.roles,
                    template_additions=self.template_counts,
                    every_coefficient_exact=True, every_addition_disjoint=True)


def hybrid_labels(c):
    """Nested source spans, enlarged at the downstream single-target regions."""
    v = len(c.inputs)
    descendants = {n: 0 for n in c.active}
    for output, node in c.outputs.items():
        descendants[node] |= 1 << output
    for node in sorted(c.active, reverse=True):
        for parent in c.args[node] or ():
            descendants[parent] |= descendants[node]
    lines = [(tuple(Q(int(j in t)) for j in range(c.h)),) for t in c.inputs]
    complements = [perp(line, c.h) for line in lines]
    labels = {}
    enlarged = []
    bad = []
    for node in sorted(c.active):
        users = descendants[node]
        if users.bit_count() == 1 and users.bit_length() <= v:
            labels[node] = complements[users.bit_length()-1]
            enlarged.append(node)
        elif c.args[node]:
            a, b = c.args[node]
            labels[node] = basis(labels[a]+labels[b])
        else:
            labels[node] = basis(lines[node-1])
        if not nonsingular(labels[node]):
            bad.append(node)
    for node in c.active:
        for parent in c.args[node] or ():
            assert len(basis(labels[parent]+labels[node])) == len(labels[node])
    for i, target in c.side:
        assert len(basis(labels[c.outputs[i]]+complements[target])) == c.h-1
    for i, _ in c.totals:
        assert len(labels[c.outputs[i]]) == c.h-2
    return labels, dict(enlarged_nodes=len(enlarged), degenerate_nodes=bad,
                        all_dag_inclusions_checked=True,
                        label_dimensions=dict(sorted(Counter(map(len, labels.values())).items())))


def frame_control(c, labels):
    """Physical-edge audit of both retained-total invocation orientations."""
    assert all(nonsingular(U) for U in labels.values())
    h, v, code = c.h, len(c.inputs), c.compile()
    full = tuple(tuple(Q(int(i == j)) for j in range(h)) for i in range(h))
    lines = [basis((tuple(int(i in t) for i in range(h)),)) for t in c.inputs]
    complements = [perp(line, h) for line in lines]
    reverse_labels = {n: perp(U, h) for n, U in labels.items()}
    results = []
    for reverse in (False, True):
        frames = lines[:]+[()]*(v+c.roles)
        total = loss = 0

        def gate(wires, U):
            nonlocal total, loss
            for w in set(wires):
                old = frames[w]
                assert nonsingular(old) and nonsingular(U)
                assert len(basis(old+U)) == max(len(old), len(U))
                total += abs(len(U)-len(old))
                loss += max(len(old)-len(U), 0)
                frames[w] = U

        def mix(mode, inverse=False):
            for n, ins, outs in reversed(code['gates']) if inverse else code['gates']:
                U = () if mode == 'low' else full if mode == 'high' else labels[n] if mode == 'node' else reverse_labels[n]
                gate([2*v+s for s in ins+outs], U)

        def copy(bank, mode):
            for t, slot in code['sources'].items():
                j = c.variables[t]-1
                U = () if mode == 'low' else full if mode == 'high' else lines[j] if mode == 'line' else complements[j]
                gate([bank+j, 2*v+slot], U)

        def inject(bank, mode):
            for i, j in c.side:
                U = () if mode == 'low' else full if mode == 'high' else lines[j] if mode == 'line' else complements[j]
                gate([bank+j, 2*v+code['outputs'][i]], U)

        def scatter(bank, U):
            gate(list(range(bank, bank+v))+[2*v+code['outputs'][i] for i, _ in c.totals], U)

        if not reverse:
            mix('low'); scatter(v, ()); inject(v, 'low'); mix('low', True)
            copy(0, 'line'); mix('node'); scatter(v, ()); inject(v, 'perp')
            mix('high', True); copy(0, 'high')
        else:
            copy(v, 'low'); mix('low'); inject(0, 'line'); scatter(0, full)
            mix('perp', True); copy(v, 'perp'); mix('high'); inject(0, 'high')
            scatter(0, full); mix('high', True)
        for j in range(v):
            gate([j], full); gate([v+j], complements[j])
        gate(range(2*v, 2*v+c.roles), full)
        assert loss == comb(h, 2)*(h-2)
        assert total == (2*v+c.roles)*h-2*v+2*loss
        results.append(dict(reverse=reverse, edge_rank_sum=total, downward_rank=loss,
                            every_edge_nested_and_nondegenerate=True))
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, default=10)
    parser.add_argument('--frames', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    start = time.monotonic()
    c = DirectProducer(args.h)
    result = dict(status='SMALL DIRECT TERNARY CIRCUIT; NO NEW KAPPA', producer=c.verify_map())
    labels, check = hybrid_labels(c)
    result['labels'] = check
    if args.frames:
        result['frames'] = frame_control(c, labels)
    result['elapsed_seconds'] = time.monotonic()-start
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
