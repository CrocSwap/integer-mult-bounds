"""PR162 generalized-carrier construction helper, DaysSky et al. Apache-2.0.
Extracted unchanged function only; no foreign producer invocation.
"""
from collections import defaultdict
from functools import lru_cache
from paired_cube.frames import basis,perp,contained
@lru_cache(maxsize=None)
def join(A,B):
 if A==B or not B:return A
 if not A:return B
 return basis(A+B)
@lru_cache(maxsize=None)
def orthogonal(S,A):return all((s&a).bit_count()%2==0 for s in S for a in A)
def extended_arcs(g, frozen):
    """Greedy extension of the frozen arcs.  gspan[x]: span of every value that reaches x through DAG or arc edges;
    gann[x]: annihilator of the intersection of every root frame reachable from x.  An arc x -> t is legal iff
    gspan[x] is orthogonal to gann[t] and t does not reach x."""
    h = g['h']; inputs = g['inputs']
    args = [None] + [None if a is None else [x + 1 for x in a] for a in g['args']]
    roots = [dict(r, node=r['node'] + 1) for r in g['roots']]
    v, n = len(inputs), len(args)
    spans = [()] * n
    for i, u in enumerate(inputs): spans[i + 1] = (u,)
    for x in range(v + 1, n): spans[x] = basis(spans[args[x][0]] + spans[args[x][1]])
    rann = [perp(spans[r['node']], h) if r.get('kind', 'side') == 'center' else basis(inputs[t] for t in r['targets'])
            for r in roots]
    active = set(range(1, v + 1)); todo = [r['node'] for r in roots]
    while todo:
        x = todo.pop()
        if x in active: continue
        active.add(x)
        if args[x]: todo.extend(args[x])
    succ = [set() for _ in args]; pred = [set() for _ in args]; direct = [[] for _ in args]
    uses = defaultdict(list)
    for x in sorted(active):
        if args[x]:
            for j, y in enumerate(args[x]): succ[y].add(x); pred[x].add(y); uses[y].append(2 * x + j)
    for j, r in enumerate(roots): direct[r['node']].extend(rann[j]); uses[r['node']].append((1 << 31) | j)
    gann = [None] * n; gspan = list(spans)
    for x in sorted(active, reverse=True): gann[x] = basis(direct[x] + [z for y in succ[x] for z in gann[y]])
    plain = list(gann)                                       # DAG-only intersections, for the candidate screen
    ancestors = {}
    def above(x):
        if x not in ancestors:
            seen = set(); stack = [x]
            while stack:
                y = stack.pop()
                if args[y]:
                    for z in args[y]:
                        if z not in seen: seen.add(z); stack.append(z)
            ancestors[x] = seen
        return ancestors[x]
    arcs = {}; used = set()
    def value(code): return roots[code & 0x7fffffff]['node'] if code >> 31 else args[code // 2][code & 1]
    def add(x, code, check):
        t = None if code >> 31 else code // 2
        At = rann[code & 0x7fffffff] if t is None else gann[t]
        if check:
            if not orthogonal(gspan[x], At): return False
            if t is not None:
                stack = [t]; seen = {t}
                while stack:
                    y = stack.pop()
                    if y == x: return False
                    for z in succ[y]:
                        if z not in seen: seen.add(z); stack.append(z)
        arcs[x] = code; used.add(code)
        work = [(x, At)]
        while work:
            y, extra = work.pop(); new = join(gann[y], extra)
            if new == gann[y]: continue
            gann[y] = new
            for z in pred[y]: work.append((z, new))
        if t is not None:
            succ[x].add(t); pred[t].add(x); work = [(t, gspan[x])]
            while work:
                y, extra = work.pop(); new = join(gspan[y], extra)
                if new == gspan[y]: continue
                gspan[y] = new
                for z in succ[y]: work.append((z, new))
        return True
    for x, code in frozen: assert add(x, code, True), ('frozen arc rejected', x, code)
    for x in sorted(active):
        if not args[x]: continue
        for j, y in enumerate(args[x]):
            other = args[x][1 - j]
            for code in uses[y]:
                if code == 2 * x + j or x in arcs or code in used: continue
                if code >> 31: screen = rann[code & 0x7fffffff]
                else:
                    t = code // 2
                    if t < x and t in above(x): continue
                    screen = plain[t]
                if not orthogonal(spans[other], screen): continue
                if sum(1 for u in uses[value(code)] if u not in used) <= 1: continue    # every value keeps a free use
                add(x, code, True)
    return sorted([x, code] for x, code in arcs.items())
