"""Exact side-role frame chains of the two-stage bit motif, from the real compiled side program.

Producer: Paureel's paired exclusion circuit on h-1 points (sidegen.Excl), lifted to every centre c with a
point order (orders.natural = sidegen, orders.gm = global matching), sharing a node iff |core|>=2 and its
(core, union) key exists. (For |core|>=2 the support is {T : core in T, T - core in union - core}, so this is
exact-support sharing; gmside.build's exact-support rule gives the same DAG.)

Compiler: Paureel's ExclusionCircuit.compile (scripts/exclusion_circuit.py @ c82d09e), re-implemented:
every active node has a gate (ins, outs); pivot = slot of operand 0 (a leaf allocates a fresh source slot);
outs = pivot + one fresh slot per further user; users are gates in node order (operand position) then outputs
in sorted (centre, target) order; outs[k] goes to users[k]. Roles = additions + outputs.

Frames (two-stage-construction.tex + shared_point_circuit.verify_frames): a gate at node n uses the source-span
frame span(n) = span{t_S : S in supp n} on every slot it touches (forward invocation); a source slot is copied
at <t_S> = span(leaf); an output slot is injected at its target-line complement t_T^perp; early mixers at
D0 (= 0 in stage 1), cleanup at D1 (= F). Reverse invocation (stage 2): orthogonal complements in reverse order;
the edge idempotents P_{U2}-P_{U1} are literally the same set (complement chain of a G-orthogonal flag).
So per slot, factor-space chain: 0 < [<t_S>] <= span(n_0) <= ... <= span(n_k) < [t_T^perp] < F, tensored with
P_b (stage 1, second factor fixed triple b) or P_b (x) . (stage 2)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.setrecursionlimit(100000)
from itertools import combinations
import sidegen, orders


def graph_rank(pairs):
    adj = {}
    for a, b in pairs: adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    col = {}; bip = 0
    for s in adj:
        if s in col: continue
        col[s] = 0; st = [s]; ok = True
        while st:
            u = st.pop()
            for w in adj[u]:
                if w not in col: col[w] = 1-col[u]; st.append(w)
                elif col[w] == col[u]: ok = False
        bip += ok
    return len(adj)-bip

ORDERS = {'nat': orders.natural, 'gm': orders.gm}

def build(h, order, exact=False):
    loc = sidegen.Excl(h-1)
    dl = {nd: graph_rank([p for i, p in enumerate(loc.inputs) if loc.support[nd] >> i & 1]) for nd in loc.active}
    trip = list(combinations(range(h), 3)); v = len(trip); var = {t: i+1 for i, t in enumerate(trip)}
    args = [None]*(v+1); core = [0]+[sum(1 << i for i in t) for t in trip]; union = list(core); dn = [0]+[1]*v
    sup = [0]+[1 << i for i in range(v)] if exact else None
    lookup = {}; outputs = {}
    for c in range(h):
        pts = order(h, c); mp = {}
        for nd in sorted(loc.active):
            if loc.args[nd] is None:
                a, b = loc.inputs[nd-1]; mp[nd] = var[tuple(sorted((c, pts[a], pts[b])))]; continue
            a, b = (mp[x] for x in loc.args[nd])
            co = core[a] & core[b]; un = union[a] | union[b]; key = (co, un)
            assert co >> c & 1
            if bin(co).count('1') >= 2 and key in lookup:
                k = lookup[key]; assert dn[k] == dl[nd]; mp[nd] = k
                if exact: assert sup[k] == sup[a] | sup[b]
                continue
            k = len(args); mp[nd] = k; args.append((a, b)); core.append(co); union.append(un); dn.append(dl[nd])
            if exact: assert not sup[a] & sup[b]; sup.append(sup[a] | sup[b])
            if bin(co).count('1') >= 2: lookup[key] = k
        for (x, y), nd in loc.outputs.items():
            outputs[c, tuple(sorted((c, pts[x], pts[y])))] = mp[nd]
    act = set(); st = list(outputs.values())
    while st:
        n = st.pop()
        if n in act: continue
        act.add(n)
        if args[n]: st.extend(args[n])
    return dict(h=h, trip=trip, args=args, dn=dn, outputs=outputs, active=act, sup=sup)

def compile_(G):
    args, act, outputs = G['args'], G['active'], G['outputs']
    users = {x: [] for x in act}
    for n in sorted(act):
        if args[n]:
            for pos, x in enumerate(args[n]): users[x].append(('gate', n, pos))
    for tgt, n in sorted(outputs.items()): users[n].append(('output', tgt))
    edge = {}; src = {}; out = {}; size = 0; hold = []     # hold[slot] = nodes whose gate touched the slot
    for n in sorted(act):
        if args[n]:
            ins = (edge[n, 0], edge[n, 1]); pivot = ins[0]
        else:
            pivot = size; size += 1; ins = (pivot,); src[pivot] = n; hold.append([])
        outs = (pivot,)+tuple(range(size, size+len(users[n])-1))
        for _ in range(len(users[n])-1): hold.append([])
        size += len(users[n])-1
        for s in set(ins+outs): hold[s].append(n)
        for u, s in zip(users[n], outs):
            if u[0] == 'gate': edge[u[1], u[2]] = s
            else: out[s] = u[1]
    adds = sum(1 for n in act if args[n])
    assert size == adds+len(outputs)
    return dict(roles=size, hold=hold, src=src, out=out, adds=adds)

def chain_dims(G, C, s):
    """Factor-space dimension chain of slot s (stage-1 forward order), from 0 to h."""
    h = G['h']; dn = G['dn']; d = [0]
    for n in C['hold'][s]:
        if dn[n] != d[-1]: d.append(dn[n])
    if s in C['out']: d.append(h-1)
    d.append(h)
    assert all(a < b for a, b in zip(d, d[1:])), (s, d)
    return d

def chain_type(G, C, s):
    """(source?, output?, number of nodes held, retired-by-operand-1?)"""
    hold = C['hold'][s]; args = G['args']
    last = hold[-1]
    retire = s not in C['out'] and len(hold) >= 1 and args[last] is not None and False
    return ('src' if s in C['src'] else 'fresh', 'out' if s in C['out'] else 'retire', len(hold))

def inner(r, h):
    """Inner lemma prediction for a rank-r edge pi (x) P_b: children widths."""
    if 2*r > h: return [1]*(h-r)+([2*r-h] if 2*r > h else [])
    return [1]*r

if __name__ == '__main__':
    from collections import Counter
    prod = sys.argv[1]
    for h in map(int, sys.argv[2:]):
        G = build(h, ORDERS[prod]); C = compile_(G)
        ranks = Counter(); types = Counter(); prof = Counter(); seqs = Counter()
        for s in range(C['roles']):
            d = chain_dims(G, C, s); rr = tuple(b-a for a, b in zip(d, d[1:]))
            seqs[rr] += 1; types[chain_type(G, C, s)[:2]] += 1
            for r in rr:
                ranks[r] += 1
                for w in inner(r, h): prof[w] += 1
        sing = prof[1]
        print('%s h=%d R=%d adds=%d outputs=%d  slot types %s  singletons/slot %.3f  blocks %s' % (
            prod, h, C['roles'], C['adds'], len(G['outputs']), dict(types), sing/C['roles'],
            sorted((w, c) for w, c in prof.items() if w > 1)), flush=True)
        print('   top rank sequences', seqs.most_common(12), flush=True)
