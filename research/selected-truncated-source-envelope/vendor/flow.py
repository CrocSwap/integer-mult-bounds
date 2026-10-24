#!/usr/bin/env python3
"""Capped whole-integer lockstep flow, retaining unmatched jobs as paid exits.

Generalizes Jacob Alan Sussman's separated multinomial construction.
zxv with substantial OpenAI Codex assistance. Apache-2.0.
This is a finite flow, not a theorem that it attains the mixed-root saving.
"""
from collections import Counter
from functools import lru_cache
from math import comb, prod


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Flow:
    def __init__(self, targets, paid, n, extra_height=0, height_base=None):
        self.T, self.P, self.n = dict(targets), dict(paid), n
        self.K = tuple(sorted(targets))
        self.m, self.kmin, self.rmax = max(targets), min(targets), max(paid)
        need(2 <= self.kmin <= self.m and self.rmax < self.m <= n,
             'finite direct-flow rank contract')
        need(all(isinstance(v, int) and v > 0 for x in (targets, paid)
                 for v in x.values()), 'positive integer inventories')
        self.cap = n//self.m
        self.height_base = self.kmin if height_base is None else height_base
        need(isinstance(self.height_base, int) and self.height_base >= 2, 'integer height base')
        self.G, least = 0, 1
        while least*self.height_base <= self.cap:
            self.G += 1
            least *= self.height_base
        need(isinstance(extra_height, int) and extra_height >= 0, 'nonnegative extra height')
        self.G += extra_height
        self.zero = (0,)*len(self.K)

    @lru_cache(None)
    def column(self, a):
        return prod(k**v for k, v in zip(self.K, a))

    @lru_cache(None)
    def points(self, height, cap):
        """(a, u(a)) at fixed degree; exact multinomial integer weights."""
        result = {}

        def visit(i, remaining, c, weight, a):
            if i == len(self.K):
                if remaining == 0 and c <= cap:
                    result[a] = weight
                return
            k, w = self.K[i], self.T[self.K[i]]
            for count in range(remaining+1):
                new_c = c*k**count
                if new_c > cap:
                    break
                visit(i+1, remaining-count, new_c,
                      weight*comb(remaining, count)*w**count, a+(count,))

        if cap >= 1:
            visit(0, height, 1, 1, ())
        return result

    @lru_cache(None)
    def units(self, depth, rho):
        return self.points(self.G-depth, self.cap//rho)

    @lru_cache(None)
    def demand(self, depth, rho):
        result = Counter()
        for a, count in self.units(depth, rho).items():
            for i, k in enumerate(self.K):
                b = list(a)
                b[i] += 1
                result[tuple(b)] += count*self.T[k]
        return result

    def merged(self):
        sources, exits, boundary = Counter(), Counter(), Counter()
        units = columns = 0
        matched = 0
        path_counts = Counter({1:1})
        for b, count in self.demand(0, 1).items():
            sources[self.column(b)] += count
        for depth in range(self.G+1):
            following = Counter()
            for rho, paths in path_counts.items():
                batch = self.units(depth, rho)
                units += paths*sum(batch.values())
                columns += paths*sum(count*rho*self.column(a) for a, count in batch.items())
                for rank, repetitions in self.P.items():
                    new_rho = rho*rank
                    copies = paths*repetitions
                    if depth == self.G:
                        need(set(batch) <= {self.zero}, 'leaf degree zero')
                        exits[new_rho] += copies*batch.get(self.zero, 0)
                        continue
                    child = self.demand(depth+1, new_rho)
                    if new_rho <= self.cap:
                        following[new_rho] += copies
                    for b in set(batch) | set(child):
                        supply, demand = batch.get(b, 0), child.get(b, 0)
                        e = new_rho*self.column(b)
                        consumed = min(supply, demand)
                        matched += copies*consumed
                        if supply > demand:
                            exits[e] += copies*(supply-demand)
                            boundary[e] += copies*(supply-demand)
                        elif demand > supply:
                            need(supply == 0, 'Pascal demand cannot exceed present supply')
                            sources[e] += copies*(demand-supply)
            path_counts = following
        sources, exits, boundary = +sources, +exits, +boundary
        need(sources and all(1 <= s <= self.n for s in sources),
             'all sources are positive and fit parent')
        if self.height_base <= self.kmin:
            need(all(self.n < self.m*s for s in sources), 'default top source bound')
        need(all(1 <= e < self.n and self.m*e <= self.rmax*self.n for e in exits),
             'all paid exits strictly smaller than parent')
        need(all(self.m*e > self.kmin*self.n for e in boundary),
             'premature exits have a failed boundary term')
        mass = lambda h: sum(k*v for k, v in h.items())
        surplus = mass(self.T)-mass(self.P)
        need(mass(sources)-mass(exits) == surplus*columns,
             'exact rank-one telescoping identity')
        W, P = sum(self.T.values()), sum(self.P.values())
        bound = sum(P**d*W**(self.G-d) for d in range(self.G+1))
        need(units <= bound and sum(sources.values()) <= W*units,
             'full integer unit/source count bounds')
        return {'n': self.n, 'height': self.G, 'sources': sources, 'exits': exits,
                'boundary_exits': boundary, 'units': units, 'column_mass': columns,
                'source_count': sum(sources.values()), 'matched_jobs': matched,
                'minimum_source': min(sources), 'all_sources_above_n_over_m':
                    all(self.n < self.m*s for s in sources),
                'rank_one_surplus': surplus, 'unit_count_upper': bound}

    def literal(self, paid_word, class_limit=200000):
        """Every round returns before the next; no merging of round paths."""
        need(Counter(paid_word) == Counter(self.P), 'literal paid word matches invoice')
        sources, exits = Counter(), Counter()
        classes = 0

        def process(depth, rho, incoming):
            nonlocal classes
            classes += 1
            need(classes <= class_limit, 'literal replay class limit')
            wanted = self.demand(depth, rho)
            need(all(v <= wanted.get(b, 0) for b, v in incoming.items()),
                 'all incoming whole jobs fit child slots')
            for b, count in wanted.items():
                missing = count-incoming.get(b, 0)
                if missing:
                    sources[rho*self.column(b)] += missing
            batch = self.units(depth, rho)
            for rank in paid_word:
                new_rho = rho*rank
                if depth == self.G:
                    for a, count in batch.items():
                        exits[new_rho*self.column(a)] += count
                    continue
                child = self.demand(depth+1, new_rho)
                passed = Counter()
                for b, count in batch.items():
                    consumed = min(count, child.get(b, 0))
                    if consumed:
                        passed[b] = consumed
                    if count > consumed:
                        exits[new_rho*self.column(b)] += count-consumed
                # All unconsumed exits and this entire child return at this
                # paid position, before any later parent round is issued.
                process(depth+1, new_rho, passed)

        process(0, 1, Counter())
        return {'sources': +sources, 'exits': +exits, 'classes': classes}


def approximate_leaves(targets, paid, maximum, checkpoints, extra_height=0, height_base=None):
    """Exploratory floating point recurrence; never an acceptance certificate."""
    m = max(targets)
    leaves = list(map(float, range(maximum+1)))
    saved = {}
    previous_cap = None
    for n in range(m, maximum+1):
        cap = n//m
        if cap != previous_cap:
            recipe = Flow(targets, paid, n, extra_height, height_base).merged()
            source, exit = recipe['sources'], recipe['exits']
            count = recipe['source_count']
            exit_charge = sum(v*leaves[e] for e, v in exit.items())
            previous_cap = cap
        leaves[n] = (sum(v*leaves[n-s] for s, v in source.items())+exit_charge)/count
        if n in checkpoints:
            from math import log
            saved[n] = {'leaves_approx': leaves[n],
                        'effective_saving_approx': 1-log(leaves[n])/log(n),
                        'source_types': len(source), 'exit_types': len(exit),
                        'boundary_exit_types': len(recipe['boundary_exits'])}
    return saved
