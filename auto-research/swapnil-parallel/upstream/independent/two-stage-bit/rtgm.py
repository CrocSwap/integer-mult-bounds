"""Retained-total gm producer for the two-stage bit motif (lever A).

The gm side circuit (gmside / side_chains) with the h direct centre wires replaced by retained point totals
P_c = sum{x_S : c in S}: per centre c, the local pair-exclusion block's grand total (sum of all pairs on the h-1
other points) is lifted like every other node, with exact-support sharing, and given one designated terminal
use ("retained output"). Roles = additions + side outputs + retained uses (compile_ as side_chains, the retained
use is an output user ordered after the side outputs).

Chains: a side output slot ends 0 < ... < t_T^perp (h-1) < F; a retained slot ends at span(P_c) = U_c
(dim h-1, Gram nondegenerate) and then F (rank 1); its copy (PR #36 copied centre) pays U_c -> D0 (rank h-1).
Usage: python3 rtgm.py h...  (prints R, additions, retained extra additions, chain summary)"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); K = os.path.join(HERE, '..', '..')
sys.path[:0] = [os.path.join(K, 'scripts'), HERE]
sys.setrecursionlimit(100000)
from itertools import combinations
from collections import Counter
import sidegen, orders, side_chains


def build(h, order=orders.gm, exact=False, retain=True):
    loc = sidegen.Excl(h - 1)
    tot = loc.pairblock(list(range(h - 1)))[0]          # same node ids (add() dedups by support)
    assert loc.support[tot] == (1 << len(loc.inputs)) - 1
    need = set(loc.active)
    if retain is True:
        st = [tot]
        while st:
            x = st.pop()
            if not x or x in need: continue
            need.add(x)
            if loc.args[x]: st.extend(loc.args[x])
    dl = {nd: side_chains.graph_rank([p for i, p in enumerate(loc.inputs) if loc.support[nd] >> i & 1]) for nd in need}
    trip = list(combinations(range(h), 3)); v = len(trip); var = {t: i + 1 for i, t in enumerate(trip)}
    args = [None] * (v + 1); dn = [0] + [1] * v
    sup = [0] + [1 << i for i in range(v)]; look = {}; outputs = {}; retained = {}
    for c in range(h):
        pts = order(h, c); mp = {}
        for nd in sorted(need):
            if loc.args[nd] is None:
                a, b = loc.inputs[nd - 1]; mp[nd] = var[tuple(sorted((c, pts[a], pts[b])))]; continue
            a, b = (mp[x] for x in loc.args[nd])
            assert not sup[a] & sup[b]
            s = sup[a] | sup[b]; k = look.get(s)
            if k is None:
                k = len(sup); sup.append(s); args.append((a, b)); dn.append(dl[nd]); look[s] = k
            else:
                assert dn[k] == dl[nd]
            mp[nd] = k
        for (x, y), nd in loc.outputs.items():
            outputs[c, tuple(sorted((c, pts[x], pts[y])))] = mp[nd]
        if retain is True: retained[c] = mp[tot]
    if retain == 'search':                               # cheapest totals: star(c) = (x + y) + z over active gm nodes
        retained = search_totals(h, trip, args, dn, sup, outputs)
    roots = list(outputs.values()) + list(retained.values())
    act = set(); st = list(roots)
    while st:
        n = st.pop()
        if n in act: continue
        act.add(n)
        if args[n]: st.extend(args[n])
    return dict(h=h, trip=trip, args=args, dn=dn, outputs=outputs, retained=retained, active=act, sup=sup)


def search_totals(h, trip, args, dn, sup, outputs):
    """For every centre, star(c) as a disjoint union of the fewest active gm nodes (1 or 2 new additions,
    largest node first); appends the new nodes to args/dn/sup and returns {c: node}."""
    act = set(); st = list(outputs.values())
    while st:
        n = st.pop()
        if n in act: continue
        act.add(n)
        if args[n]: st.extend(args[n])
    bysup = {sup[n]: n for n in act}; pc = lambda s: bin(s).count('1'); out = {}
    def new(a, b, c):
        assert not sup[a] & sup[b]
        s = sup[a] | sup[b]
        if s in bysup: return bysup[s]
        pairs = [tuple(q for q in trip[i] if q != c) for i in range(len(trip)) if s >> i & 1]
        k = len(sup); sup.append(s); args.append((a, b)); dn.append(side_chains.graph_rank(pairs)); bysup[s] = k
        return k
    for c in range(h):
        star = sum(1 << i for i, t in enumerate(trip) if c in t)
        subs = sorted([n for n in act if sup[n] & ~star == 0], key=lambda n: (-pc(sup[n]), n))
        best = None
        for x in subs:
            if star ^ sup[x] in bysup: best = (x, bysup[star ^ sup[x]]); break
        if best is None:
            for i, x in enumerate(subs):
                rem = star ^ sup[x]
                if pc(rem) > 2 * pc(sup[x]): break
                for y in subs[i:]:
                    if sup[y] & ~rem == 0 and (rem ^ sup[y]) in bysup: best = (x, y, bysup[rem ^ sup[y]]); break
                if best: break
        if best is None:                                 # greedy exact cover, largest active node first
            rem = star; best = []
            while rem:
                x = next(n for n in subs if sup[n] & ~rem == 0); best.append(x); rem ^= sup[x]
        acc = best[0]
        for x in best[1:]: acc = new(acc, x, c)
        out[c] = acc
        assert sup[out[c]] == star and dn[out[c]] == h - 1
    return out


def compile_(G):
    """side_chains.compile_ with retained uses as extra output users (after the side outputs)."""
    args, act, outputs, retained = G['args'], G['active'], G['outputs'], G['retained']
    users = {x: [] for x in act}
    for n in sorted(act):
        if args[n]:
            for pos, x in enumerate(args[n]): users[x].append(('gate', n, pos))
    for tgt, n in sorted(outputs.items()): users[n].append(('output', tgt))
    for c, n in sorted(retained.items()): users[n].append(('retained', c))
    edge = {}; out = {}; ret = {}; size = 0; hold = []
    for n in sorted(act):
        if args[n]:
            pivot = edge[n, 0]; ins = (edge[n, 0], edge[n, 1])
        else:
            pivot = size; size += 1; ins = (pivot,); hold.append([])
        outs = (pivot,) + tuple(range(size, size + len(users[n]) - 1))
        for _ in range(len(users[n]) - 1): hold.append([])
        size += len(users[n]) - 1
        for s in set(ins + outs): hold[s].append(n)
        for u, s in zip(users[n], outs):
            if u[0] == 'gate': edge[u[1], u[2]] = s
            elif u[0] == 'output': out[s] = u[1]
            else: ret[s] = u[1]
    adds = sum(1 for n in act if args[n])
    assert size == adds + len(outputs) + len(retained)
    return dict(roles=size, hold=hold, out=out, ret=ret, adds=adds)


def chain_dims(G, C, s):
    h = G['h']; dn = G['dn']; d = [0]
    for n in C['hold'][s]:
        if dn[n] != d[-1]: d.append(dn[n])
    if s in C['out']: d.append(h - 1)
    if s in C['ret']: assert d[-1] == h - 1, (s, d)
    d.append(h)
    assert all(a < b for a, b in zip(d, d[1:])), (s, d)
    return d


def side_ranks(h, retain='search'):
    G = build(h, retain=retain); C = compile_(G); rk = Counter()
    for s in range(C['roles']):
        d = chain_dims(G, C, s)
        for a, b in zip(d, d[1:]): rk[b - a] += 1
    return C['roles'], rk, C, G


if __name__ == '__main__':
    for h in map(int, sys.argv[1:]):
        R0, rk0, C0, _ = side_ranks(h, False)
        for mode in (True, 'search'):
            R1, rk1, C1, G1 = side_ranks(h, mode)
            print('h=%d %s gm R=%d adds=%d | retained R=%d adds=%d (+%d adds, +%d roles; old R+h=%d)' % (
                h, mode, R0, C0['adds'], R1, C1['adds'], C1['adds'] - C0['adds'], R1 - R0, R0 + h), flush=True)
