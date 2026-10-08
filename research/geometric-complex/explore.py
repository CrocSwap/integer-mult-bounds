"""Exact finite experiment: complex side circuits with geometric envelope frames.

This is a research candidate, not a verification of integer multiplication.
All constants are derived from the requested ground size.
"""
from itertools import combinations
from fractions import Fraction as Q
from math import comb, log
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from search_network import log_integer_bounds
from certify import Parameters, constraints, margins
from compact_control_layer import layer_exponents
from prepare_layers import serializable


class Circuit:
    def __init__(self, n, relation):
        self.n = n
        self.triples = list(combinations(range(n), 3))
        self.masks = [sum(1 << i for i in t) for t in self.triples]
        self.v = len(self.triples)
        self.args = [None] * self.v
        self.support = [1 << i for i in range(self.v)]
        self.union = list(self.masks)
        self.lookup = {s:i for i,s in enumerate(self.support)}
        self.outputs = {}
        if relation == 'disjoint':
            for j, target in enumerate(self.masks):
                support = sum(1 << i for i, source in enumerate(self.masks)
                              if not source & target)
                self.outputs[j] = self.total(support)
        elif relation == 'intersection_two':
            # Each ordered pair with intersection two occurs in one pair-star.
            for pair in combinations(range(n), 2):
                p = sum(1 << i for i in pair)
                group = [i for i, mask in enumerate(self.masks) if mask & p == p]
                for j in group:
                    support = sum(1 << i for i in group if i != j)
                    self.outputs[pair,j] = self.total(support)
        else:
            raise ValueError(relation)
        self.relation = relation
        self.active = set()
        stack = list(self.outputs.values())
        while stack:
            node = stack.pop()
            if node in self.active:
                continue
            self.active.add(node)
            if self.args[node] is not None:
                stack.extend(self.args[node])
        self.additions = sum(self.args[z] is not None for z in self.active)

    def total(self, support):
        assert support
        if support in self.lookup:
            return self.lookup[support]
        # Split in a fixed dyadic tree on input indices, independent of target.
        lo = (support & -support).bit_length() - 1
        hi = support.bit_length() - 1
        split = (hi >> ((lo ^ hi).bit_length()-1)) << ((lo ^ hi).bit_length()-1)
        left = support & ((1 << split)-1)
        right = support ^ left
        a,b = self.total(left), self.total(right)
        z = len(self.args)
        self.args.append((a,b))
        self.support.append(support)
        self.union.append(self.union[a] | self.union[b])
        self.lookup[support] = z
        return z

    def verify(self):
        for z in self.active:
            if self.args[z] is not None:
                a,b = self.args[z]
                assert a < z and b < z
                assert not self.support[a] & self.support[b]
                assert self.support[z] == self.support[a] | self.support[b]
                assert self.union[z] == self.union[a] | self.union[b]
                if self.relation == 'disjoint':
                    assert self.union[z].bit_count() >= 4
        for key,z in self.outputs.items():
            if self.relation == 'disjoint':
                target = self.masks[key]
                expected = sum(1 << i for i,t in enumerate(self.masks) if not t & target)
                assert not self.union[z] & target
            else:
                pair,j = key
                p = sum(1 << i for i in pair)
                expected = sum(1 << i for i,t in enumerate(self.masks)
                               if t & p == p and i != j)
            assert self.support[z] == expected
        return dict(relation=self.relation, additions=self.additions,
                    outputs=len(self.outputs), roles=self.additions+len(self.outputs),
                    exact_supports=True, disjoint_addition_supports=True)

    def compile(self):
        """Reversible embedding; slots contain arbitrary values outside tests."""
        users = {z:[] for z in self.active}
        for z in sorted(self.active):
            if self.args[z] is not None:
                for pos,x in enumerate(self.args[z]):
                    users[x].append(('gate',z,pos))
        for key,z in self.outputs.items():
            users[z].append(('output',key))
        edge, sources, outputs, gates = {}, {}, {}, []
        size = 0
        for z in sorted(self.active):
            if self.args[z] is None:
                pivot = size
                size += 1
                ins = (pivot,)
                sources[z] = pivot
            else:
                ins = (edge[z,0],edge[z,1])
                pivot = ins[0]
            outs = (pivot,) + tuple(range(size,size+len(users[z])-1))
            size += len(users[z])-1
            assert len(set(ins)) == len(ins)
            assert set(ins) & set(outs) == {pivot}
            gates.append((z,ins,outs))
            for user,slot in zip(users[z],outs):
                if user[0] == 'gate':
                    edge[user[1],user[2]] = slot
                else:
                    outputs[user[1]] = slot
        assert size == self.additions+len(self.outputs)
        return dict(roles=size,gates=gates,sources=sources,outputs=outputs)


def counts(n, verify=True):
    d,e = Circuit(n,'disjoint'),Circuit(n,'intersection_two')
    dc,ec = (d.verify(),e.verify()) if verify else (
        dict(roles=d.additions+len(d.outputs)),dict(roles=e.additions+len(e.outputs)))
    h = n+1  # One unused coordinate cures alternating residuals.
    v,m = comb(n,3),h**3
    roles = dc['roles']+ec['roles']
    centers = n+1
    N = v**3
    W = 2*N+3*v*v*(roles+centers)
    L = 3*v*v*centers*h
    s = W*m-2*N+2*L
    eta = Q(2*N-2*L,W*m)
    _,loghi = log_integer_bounds(m)
    return dict(n=n,h=h,v=v,m=m,N=N,W=W,L=L,s=s,eta=eta,
                saving_lower=eta/loghi,disjoint=dc,intersection_two=ec,
                side_roles=roles, original_side_roles=v*(comb(n-3,3)+3*(n-3)),
                depth_hypothesis=2 <= s < m**5)


def assembly(ac, n):
    ab = Q(296,10**11)
    beta,zeta = Q(1,1000),Q(1,10000)
    epsilon,c = Q(1999,10000),Q(1)
    ex = layer_exponents(1-ab,1-ac,beta,c)
    lam = 1-Q(2959,10**12)
    lamp = 1-Q(2958,10**12)
    p = Parameters(1-ab,1-ac,epsilon,c,lam,lamp,Q(59,10**11),
                   beta=beta,delta=Q(1,10**6),C1=5-4*beta+zeta)
    cs = constraints(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    cs['packed_overhead'] = lam-ex['internal']
    cs['reserved_axes'] = lamp-ex['preprocessing']
    gs = margins(p,layout_model='nonadjacent',assembly_model='tight-gaussian')
    return dict(parameters=vars(p),recurrence=ex,slacks=cs,margins=gs,
                minimum_margin=min(gs.values()),all_slacks_positive=all(x>0 for x in cs.values()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sizes', type=int, nargs='+', default=[25,28,32])
    args = parser.parse_args()
    for n in args.sizes:
        out=counts(n)
        print(json.dumps(serializable(out),sort_keys=True),flush=True)
        print('saving lower',float(out['saving_lower']), 'depth',out['depth_hypothesis'],flush=True)
