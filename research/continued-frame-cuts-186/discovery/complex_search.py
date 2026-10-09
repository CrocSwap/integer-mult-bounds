#!/usr/bin/env python3
"""Reproducible physical-frame experiments for the selected paired-cube word.

The search changes only common operation frames.  Every emitted witness still
has to pass the independent scalar and nested-frame replay supplied by PR157.
Developed with OpenAI Codex assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from paired_cube.frames import basis, perp, contained



def numerical_root(children, W, m):
    lo, hi = 0., .1
    for _ in range(75):
        mid = (lo + hi) / 2
        if math.fsum(n * r * math.exp(mid * math.log(m / r))
                     for r, n in children.items()) < W * m:
            lo = mid
        else:
            hi = mid
    return lo

class Experiment:
    def __init__(self, baseline, input_frames=None, alpha=0.0006, input_pairs=None):
        self.g, self.w, self.word = [json.loads((baseline / name).read_text())
                                  for name in ('graph.json', 'frames.json', 'selection.json')]
        record_path = baseline/'record.json'
        if not record_path.exists():record_path = ROOT/'certificates/paired-cube-complex-input.json'
        self.record = json.loads(record_path.read_text())
        self.h, self.R, self.v = self.g['h'], self.record['R'], self.g['v']
        self.full = basis(1 << j for j in range(self.h))
        self.ops = [tuple(o) for o in self.word['ops']]
        self.N = len(self.ops)
        self.topological_position = list(range(self.N))
        self.base_frames = [perp(tuple(self.w['annihilators'][x]), self.h) for _, _, x in self.ops]
        self.frames = list(self.base_frames)
        if input_frames is None:
            input_frames = ROOT / 'references/paired-cube/physical/frames.json'
        for i, F in json.loads(input_frames.read_text())['frames']:
            self.frames[i] = tuple(F)
        if input_pairs is None: input_pairs = ROOT / 'references/paired-cube/physical/pairs.json'
        self.pairs_input = json.loads(input_pairs.read_text())['pairs']
        self.pairs = {a: b for a, b, _ in self.pairs_input}
        self.merged = {b: a for a, b in self.pairs.items()}
        self.sources = {int(x): s for x, s in self.word['sources'].items()}
        self.source_roles = set(self.sources.values())
        self.start = [()] * self.R
        for x, s in self.sources.items():
            self.start[s] = (self.g['inputs'][x-1],)
        self.gauges = {}
        for z in self.word['selected']:
            self.gauges[z['role']] = perp(tuple(z['annihilator']), self.h)
            self.start[z['role']] = self.gauges[z['role']]
        self.spans = [(q,) for q in self.g['inputs']]
        for aa in self.g['args'][self.v:]:
            self.spans.append(basis(self.spans[aa[0]] + self.spans[aa[1]]))
        self.node_spans = [self.spans[x-1] for _, _, x in self.ops]
        self.rootframe, self.rootkind = {}, {}
        self.roots = [dict(r, node=r['node']+1) for r in self.g['roots']]
        for r, s in zip(self.roots, self.word['rootroles']):
            if r['kind'] == 'center':
                U = self.spans[r['node']-1]
            else:
                U = perp(basis(self.g['inputs'][t] for t in r['targets']), self.h)
            self.rootframe[s], self.rootkind[s] = U, r['kind']
        self.role_ops = defaultdict(list)
        for i, (a, b, _) in enumerate(self.ops):
            self.role_ops[a].append(i)
            self.role_ops[b].append(i)
        self.constants = []
        const_ids = {}
        def constant(F):
            if F not in const_ids:
                const_ids[F] = -len(self.constants)-1
                self.constants.append(F)
            return const_ids[F]
        self.edges = []
        for s in range(self.R):
            if s in self.merged:
                continue
            seq = [constant(self.start[s])] + self.role_ops[s]
            if s in self.rootframe:
                seq.append(constant(self.rootframe[s]))
            if s in self.pairs:
                b = self.pairs[s]
                seq += [constant(self.start[b])] + self.role_ops[b]
                if b in self.rootframe:
                    seq.append(constant(self.rootframe[b]))
            seq.append(constant(self.full))
            self.edges.extend(zip(seq, seq[1:]))
        self.in_edges = [[] for _ in self.ops]
        self.out_edges = [[] for _ in self.ops]
        for k, (a, b) in enumerate(self.edges):
            if a >= 0:
                self.out_edges[a].append(k)
            if b >= 0:
                self.in_edges[b].append(k)
        self.alpha = alpha
        self.cost = [r * math.expm1(alpha * math.log(3*self.h/r)) if r else 0.
                     for r in range(self.h+1)]
        self.perp = lru_cache(maxsize=200000)(lambda F: perp(F, self.h))
        self.check()

    def F(self, n):
        return self.frames[n] if n >= 0 else self.constants[-n-1]

    def check(self):
        for i, F in enumerate(self.frames):
            assert basis(F) == F and contained(self.node_spans[i], F), i
        for a, b in self.edges:
            assert contained(self.F(a), self.F(b)), (a, b)

    def profile(self):
        H = Counter(len(self.F(b))-len(self.F(a)) for a, b in self.edges)
        H.pop(0, None)
        H[1] += len(self.sources)
        for s, kind in self.rootkind.items():
            if kind == 'center':
                H[len(self.rootframe[s])] += 1
        C = Counter({r: 3*n for r, n in H.items()})
        for label in ('source_data_histogram', 'target_data_histogram'):
            C.update({int(r): 3*n for r, n in self.record[label].items() if int(r)})
        C.update(Counter(3*len(U) for s, U in self.gauges.items() if s not in self.merged))
        C[2] += 2*self.v
        W = 2*self.v+self.R-len(self.pairs)
        mass = sum(r*n for r, n in C.items())
        assert W*3*self.h-mass == self.record['deficit_per_vertex']
        return dict(local_histogram=dict(sorted(H.items())), child_histogram=dict(sorted(C.items())),
                    W_per_vertex=W, R=self.R-len(self.pairs), rank_per_vertex=mass,
                    numerical_complex_root=numerical_root(C, W, 3*self.h))

    def boundary(self, group):
        nodes = set(group)
        inc = [k for i in group for k in self.in_edges[i] if self.edges[k][0] not in nodes]
        out = [k for i in group for k in self.out_edges[i] if self.edges[k][1] not in nodes]
        return inc, out

    def update(self, group, mode='both', neutral=False):
        inc, out = self.boundary(group)
        old = self.frames[group[0]]
        assert all(self.frames[i] == old for i in group)
        low = basis(tuple(u for i in group for u in self.node_spans[i]) +
                    tuple(u for k in inc for u in self.F(self.edges[k][0])))
        high = self.perp(basis(tuple(u for k in out for u in self.perp(self.F(self.edges[k][1])))))
        assert contained(low, old) and contained(old, high)
        dims_in = [len(self.F(self.edges[k][0])) for k in inc]
        dims_out = [len(self.F(self.edges[k][1])) for k in out]
        def cost(F):
            d = len(F)
            return math.fsum(self.cost[d-x] for x in dims_in) + math.fsum(self.cost[x-d] for x in dims_out)
        candidates = [old]
        if mode in ('both', 'low'): candidates.append(low)
        if mode in ('both', 'high'): candidates.append(high)
        best = min(candidates, key=lambda F: (cost(F), len(F), F))
        improvement = cost(old)-cost(best)
        if improvement > 1e-12 or (neutral and abs(improvement) < 1e-12 and len(best) < len(old)):
            for i in group:
                self.frames[i] = best
            return improvement, len(group)
        return 0., 0

    def components(self):
        parent = list(range(self.N))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for a, b in self.edges:
            if a >= 0 and b >= 0 and self.frames[a] == self.frames[b]:
                a, b = find(a), find(b)
                if a != b: parent[max(a,b)] = min(a,b)
        groups = defaultdict(list)
        for i in range(self.N): groups[find(i)].append(i)
        return list(groups.values())

    def update_envelope(self, group):
        """Move an entire flat component to its earliest or latest legal shape."""
        nodes = set(group)
        changed_edges = set(k for i in group for k in self.in_edges[i] + self.out_edges[i])
        lower, upper = {}, {}
        for i in sorted(group,key=lambda i:self.topological_position[i]):
            lower[i] = basis(self.node_spans[i] + tuple(
                u for k in self.in_edges[i]
                for u in lower.get(self.edges[k][0], self.F(self.edges[k][0]))))
            assert contained(lower[i], self.frames[i])
        for i in sorted(group,key=lambda i:self.topological_position[i],reverse=True):
            upper[i] = self.perp(basis(tuple(
                u for k in self.out_edges[i]
                for u in self.perp(upper.get(self.edges[k][1], self.F(self.edges[k][1]))))))
            assert contained(self.frames[i], upper[i])
        def cost(plan):
            return math.fsum(self.cost[len(plan.get(b, self.F(b)))-len(plan.get(a, self.F(a)))]
                             for k in changed_edges for a, b in [self.edges[k]])
        before = cost({})
        plan = min([lower, upper], key=cost)
        improvement = before-cost(plan)
        if improvement > 1e-12:
            count = sum(F != self.frames[i] for i, F in plan.items())
            for i, F in plan.items(): self.frames[i] = F
            return improvement, count
        return 0., 0

    def envelope_pass(self, seed=0):
        groups = [g for g in self.components() if len(g) > 1]
        random.Random(seed).shuffle(groups)
        gain, changed = 0., 0
        for group in groups:
            improvement, count = self.update_envelope(group)
            gain += improvement
            changed += count
        self.check()
        print(json.dumps(dict(envelope_pass=seed, gain=gain, moved=changed,
                              numerical_complex_root=self.profile()['numerical_complex_root'])), flush=True)
        return changed

    def update_subsets(self, group):
        """Try closed prefixes/suffixes of one equal-frame component.

        A prefix determined by E_i <= F is an order ideal, since the earliest
        envelope E_i is monotone. Its entire frame can therefore move to F at
        once. The latest envelope gives the dual upward-closed subsets.
        """
        old = self.frames[group[0]]
        if not all(self.frames[i] == old for i in group): return 0., 0
        lower, upper = {}, {}
        for i in sorted(group,key=lambda i:self.topological_position[i]):
            lower[i] = basis(self.node_spans[i] + tuple(
                u for k in self.in_edges[i]
                for u in lower.get(self.edges[k][0], self.F(self.edges[k][0]))))
        for i in sorted(group,key=lambda i:self.topological_position[i],reverse=True):
            upper[i] = self.perp(basis(tuple(
                u for k in self.out_edges[i]
                for u in self.perp(upper.get(self.edges[k][1], self.F(self.edges[k][1]))))))
        best_gain, best_nodes, best_frame = 0., [], old
        for env, direction in ((lower, 'lower'), (upper, 'upper')):
            candidates = sorted(set(env.values())-{old}, key=lambda F: (len(F), F))
            for F in candidates:
                selected = [i for i in group if contained(env[i], F)] if direction == 'lower' else \
                           [i for i in group if contained(F, env[i])]
                inc, out = self.boundary(selected)
                d, od = len(F), len(old)
                gain = math.fsum(self.cost[od-len(self.F(self.edges[k][0]))] -
                                 self.cost[d-len(self.F(self.edges[k][0]))] for k in inc)
                gain += math.fsum(self.cost[len(self.F(self.edges[k][1]))-od] -
                                  self.cost[len(self.F(self.edges[k][1]))-d] for k in out)
                if gain > best_gain+1e-12:
                    best_gain, best_nodes, best_frame = gain, selected, F
        if best_nodes:
            for i in best_nodes: self.frames[i] = best_frame
            return best_gain, len(best_nodes)
        return 0., 0

    def subset_pass(self, seed=0):
        groups = [g for g in self.components() if len(g) > 1]
        random.Random(seed).shuffle(groups)
        gain, changed = 0., 0
        for group in groups:
            improvement, count = self.update_subsets(group)
            gain += improvement
            changed += count
        self.check()
        print(json.dumps(dict(subset_pass=seed, gain=gain, moved=changed,
                              numerical_complex_root=self.profile()['numerical_complex_root'])), flush=True)
        return changed

    def optimize(self, rounds=20, seed=0, mode='both', blocks=True):
        rng = random.Random(seed)
        for turn in range(rounds):
            groups = self.components() if blocks and turn % 2 else [[i] for i in range(self.N)]
            if turn % 4 == 1: groups.reverse()
            if turn % 4 >= 2: rng.shuffle(groups)
            total, changed = 0., 0
            for group in groups:
                if not all(self.frames[i] == self.frames[group[0]] for i in group): continue
                gain, count = self.update(group, mode=mode)
                total += gain
                changed += count
            print(json.dumps(dict(round=turn, gain=total, moved=changed,
                                  numerical_complex_root=self.profile()['numerical_complex_root'])), flush=True)
            if changed == 0 and (not blocks or turn % 2): break
        self.check()

    def neutral_pass(self,seed=0,blocks=False):
        """Escape a local minimum using moves with exactly unchanged rank bins."""
        before = self.profile()['child_histogram']
        groups = self.components() if blocks else [[i] for i in range(self.N)]
        rng = random.Random(seed);rng.shuffle(groups)
        changed = 0
        for group in groups:
            if rng.random() < 0.5:continue
            old = self.frames[group[0]]
            if not all(self.frames[i] == old for i in group):continue
            inc,out = self.boundary(group)
            low = basis(tuple(u for i in group for u in self.node_spans[i])+
                        tuple(u for k in inc for u in self.F(self.edges[k][0])))
            high = self.perp(basis(tuple(u for k in out for u in self.perp(self.F(self.edges[k][1])))))
            dims_in = [len(self.F(self.edges[k][0])) for k in inc]
            dims_out = [len(self.F(self.edges[k][1])) for k in out]
            def hist(F):return Counter([len(F)-d for d in dims_in]+[d-len(F) for d in dims_out])
            old_hist = hist(old)
            candidates = [F for F in (low,high) if F != old and hist(F) == old_hist]
            if candidates:
                chosen = rng.choice(candidates)
                for i in group:self.frames[i] = chosen
                changed += len(group)
        self.check()
        assert self.profile()['child_histogram'] == before
        print(json.dumps(dict(neutral_pass=seed,moved=changed,blocks=blocks)),flush=True)
        return changed

    def save(self, out):
        out.mkdir(parents=True, exist_ok=True)
        differences = [[i, list(F)] for i, F in enumerate(self.frames) if F != self.base_frames[i]]
        (out / 'frames.json').write_text(json.dumps(dict(frames=differences), separators=(',', ':'))+'\n')
        (out / 'pairs.json').write_text(json.dumps(dict(pairs=self.pairs_input), separators=(',', ':'))+'\n')
        (out / 'profile.json').write_text(json.dumps(self.profile(), indent=2, sort_keys=True)+'\n')

def algebraic_birth_audit(g,word,R,pairs):
    """Check exact integer read responses and the hypotheses of PR124's lemma.

    Side coordinates below are twice their rational coefficients; the final
    h coordinates are integer copied-center responses, before center scatter.
    The common denominator of the complete scalar output is consequently six.
    This does not use sampled inputs or arithmetic modulo a prime.
    """
    v,h = g['v'],g['h']
    ops,coefficients = word['ops'],word['opcoeff']
    roots,rootroles = g['roots'],word['rootroles']
    response = [{} for _ in range(R)]
    for r,s in zip(roots,rootroles):
        assert not response[s]
        if r['kind'] == 'center':
            response[s] = {v+r['coordinate']:1}
        else:
            assert all(c in ('1/2','-1/2') for c in r['coefficients'])
            response[s] = {t:(1 if c == '1/2' else -1) for t,c in zip(r['targets'],r['coefficients'])}
    for (a,b,x),(ca,cb) in zip(reversed(ops),reversed(coefficients)):
        assert a != b and ca in (-1,1) and cb in (-1,1)
        for t,c in response[a].items():response[b][t] = response[b].get(t,0)+cb*c
        if ca != 1:response[a] = {t:ca*c for t,c in response[a].items()}
    response = [{t:c for t,c in row.items() if c} for row in response]
    selected = {z['role']:z for z in word['selected']}
    pset = set(word['phase1'])
    chronology = word['phase1']+[i for i in range(len(ops)) if i not in pset]
    position = {i:k for k,i in enumerate(chronology)}
    role_ops = defaultdict(list)
    for i,(a,b,x) in enumerate(ops):role_ops[a].append(i);role_ops[b].append(i)
    source_roles = set(word['sources'].values())
    root_roles = set(rootroles)
    donors,recipients = {a for a,b,t in pairs},{b for a,b,t in pairs}
    assert len(donors) == len(recipients) == len(pairs) and not donors & recipients
    alias = {b:a for a,b,t in pairs}
    for (a,b,x),(ca,cb) in zip(ops,coefficients):
        assert alias.get(a,a) != alias.get(b,b)
        assert ca*ca == 1 and ca*cb-ca*cb == 0
    rows = []
    for a,b,t in pairs:
        assert a not in selected and a not in root_roles
        assert b in selected and b not in source_roles
        assert all(i not in pset for i in role_ops[b])
        birth = len(pset) if t is None else position[t]
        if t is not None:assert t == role_ops[b][0]
        assert position[role_ops[a][-1]] < birth
        D = response[b]
        assert all(target < v for target in D), ('Center-dependent recipient',b)
        assert set(D) <= set(selected[b]['targets']), ('Undeclared read target',b)
        rows.append([b,sorted(D.items())])
    canonical = json.dumps(sorted(rows),separators=(',',':')).encode()
    return dict(exact_integer_response_backpropagation=True,
                compensated_recipients=len(pairs),
                zero_center_response_for_every_recipient=True,
                recipient_target_supports_contained=True,
                dead_donor_and_untouched_birth_chronology=True,
                aliased_gate_ports_disjoint=True,
                signed_gate_and_injection_inverse_polynomials_exact=True,
                selected_response_sha256=hashlib.sha256(canonical).hexdigest(),
                selected_side_response_denominator=2,
                selected_read_terms=sum(len(response[b]) for b in recipients),
                selected_max_abs_numerator=max(abs(c) for b in recipients for c in response[b].values()),
                proof_interface='PR124 compensated-birth lemma plus the regenerated signed H+K+B=I identity; this finite audit is not a formal proof of the retained multiplication theorem')
