#!/usr/bin/env python3
"""BANK: own fold + pivot + histogram tool for banked-transfer circuits (lane BANK, Nov 18).
Network: tokens >=0 are MOVE event indices (paid slots, value = sent form), tokens <0 are inputs ~r.
forms[node] = {token: Fraction}; node = move index (form sent) or FIRST+r (terminal r).
moves[k] = (src_chart, dst_chart).  Paid hist = Counter |dim dst - dim src| over moves (pricekit rule)."""
import gzip, json, sys, os
from collections import Counter, defaultdict
from fractions import Fraction as Q
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pricekit as pk

def load(p):
    return json.load(gzip.open(p, 'rt') if p.endswith('.gz') else open(p))

class Net:
    def __init__(s, first, init, final, moves, forms):
        s.first, s.init, s.final, s.moves, s.forms = first, init, final, moves, forms
    def chart_of_node(s, k):           # chart where node's form is evaluated
        return s.moves[k][0] if k < s.first else s.final[k - s.first]
    def chart_of_tok(s, t):            # chart where token's value is available
        return s.init[~t] if t < 0 else s.moves[t][1]
    def copy(s):
        return Net(s.first, s.init, s.final, dict(s.moves), dict(s.forms))

def axpy(row, src, a):
    for k, v in src.items():
        w = row.get(k, 0) + a * v
        if w: row[k] = w
        else: row.pop(k, None)

def fold(W):
    n = W['public']; N = n + W['owned_fields']
    rows = [{~r: Q(1)} for r in range(n)] + [None] * W['owned_fields']
    ch = list(W['initial']) + [None] * W['owned_fields']
    moves, forms = {}, {}
    for i, e in enumerate(W['program']):
        op, r = e[0], e[1]
        if op == 'INIT': rows[r], ch[r] = {}, e[2]; continue
        if op == 'MOVE':
            assert ch[r] == e[2]
            moves[i] = (e[2], e[3]); forms[i] = rows[r]; rows[r] = {i: Q(1)}; ch[r] = e[3]
        elif op == 'CLEAR': assert ch[r] == e[-1]; rows[r] = ch[r] = None
        elif op == 'SCALE':
            assert ch[r] == e[-1]; c = Q(e[2]); rows[r] = {k: v * c for k, v in rows[r].items()}
        elif op == 'ADD':
            assert ch[r] == e[-1] == ch[e[2]] and e[2] != r
            rows[r] = dict(rows[r]); axpy(rows[r], rows[e[2]], Q(e[3]))
        else: raise ValueError(op)
    assert ch[:n] == W['final']
    first = len(W['program'])
    for r in range(n): forms[first + r] = rows[r]
    return Net(first, list(W['initial']), list(W['final']), moves, forms)

def transpose(net):
    f = net.first
    def rv(x):
        if x < 0: return f + ~x
        if x >= f: return ~(x - f)
        return x
    forms = {k: {} for k in net.moves}; forms.update({f + r: {} for r in range(len(net.init))})
    for node, row in net.forms.items():
        for d, c in row.items(): forms[rv(d)][rv(node)] = c
    return Net(f, net.final, net.init, {k: (b, a) for k, (a, b) in net.moves.items()}, forms)

def schedule(net):
    """locality + acyclicity; returns a topological order of nodes."""
    indeg = {k: 0 for k in net.forms}; out = defaultdict(list)
    for k, row in net.forms.items():
        c = net.chart_of_node(k)
        for d in row:
            assert net.chart_of_tok(d) == c, ('nonlocal', k, d)
            if d >= 0: indeg[k] += 1; out[d].append(k)
    order = [k for k, v in indeg.items() if v == 0]; i = 0
    while i < len(order):
        for m in out[order[i]]:
            indeg[m] -= 1
            if indeg[m] == 0: order.append(m)
        i += 1
    assert len(order) == len(net.forms), 'cycle'
    return order

def pivot(net, drop, lead, F, gamma, sender, receiver):
    """PROOF s1 algebra (own implementation). gamma/sender/receiver: {token: Fraction}."""
    B = net.moves[drop][1]
    uses = {m: row[drop] for m, row in net.forms.items() if drop in row}
    C = net.moves[lead][1]
    assert lead in gamma and set(gamma) <= set(uses)
    assert all(m < net.first and net.moves[m] == (B, C) for m in uses), 'readers not all B->C'
    Y = {}
    for m, g in gamma.items(): axpy(Y, net.forms[m], g)
    s = Y.get(drop, 0); assert s
    forms = dict(net.forms); del forms[drop]; forms[lead] = dict(sender)
    for m, a in uses.items():
        if m != lead:
            r = dict(net.forms[m]); axpy(r, Y, -a / s); assert drop not in r; forms[m] = r
    YC = {lead: Q(1)}; axpy(YC, receiver, Q(-1))           # Y recovered at C = W - D
    rec = {}
    for m, a in uses.items():
        r = {k: -v / gamma[lead] for k, v in gamma.items() if k != lead} if m == lead else {m: Q(1)}
        axpy(r, YC, a / s); rec[m] = r
    for k, row in list(forms.items()):
        hit = row.keys() & rec.keys()
        if hit:
            new = {i: v for i, v in row.items() if i not in hit}
            for i in hit: axpy(new, rec[i], row[i])
            forms[k] = new
    moves = dict(net.moves); del moves[drop]; moves[lead] = (F, C)
    return Net(net.first, net.init, net.final, moves, forms)

def apply(net, direction, *a):
    if direction == 'transpose': return transpose(pivot(transpose(net), *a))
    return pivot(net, *a)

def hist(net, dim):
    return +Counter(r for r in (abs(dim[b] - dim[a]) for a, b in net.moves.values()) if r)

# ---------------- values mod p (numpy) for endpoint checks and search
P1 = 2147483629
def inv(x, p): return pow(x, -1, p)
def fmod(q, p): return q.numerator % p * inv(q.denominator % p, p) % p

def values(net, p=P1, order=None):
    import numpy as np
    n = len(net.init); order = order or schedule(net); V = {}
    for k in order:
        v = np.zeros(n, dtype=np.int64)
        for d, c in net.forms[k].items():
            cm = fmod(c, p)
            if d < 0: v[~d] = (v[~d] + cm) % p
            else: v = (v + cm * V[d]) % p
        V[k] = v
    return V

def terminals_equal(n1, n2, p=P1):
    import numpy as np
    V1, V2 = values(n1, p), values(n2, p)
    return all(np.array_equal(V1[n1.first + r], V2[n2.first + r]) for r in range(len(n1.init)))

# ---------------- pricing
CALLER = os.path.join(os.path.dirname(__file__), '..', 'STACK', 'dl', 'data', 'CALLER.json.gz')
def price(W, paid, digits=16):
    base = pk.native_from_word(W)
    nat = pk.native_from_hist(dict(paid), dict(base['T']), base['Dports'])
    C = pk.load(CALLER); inv_ = pk.invoice(pk.caller_invoice(C), nat)
    return pk.price(inv_, digits), inv_

def edits_from_pivots(path):
    out = []
    for e in load(path):
        cv = lambda L: {int(k): Q(v) for k, v in L}
        out.append((e['direction'], e['remove'], e['pivot'], e['source_chart'],
                    cv(e['combination']), cv(e['sender']), cv(e['receiver'])))
    return out

if __name__ == '__main__':   # control: reproduce #7674 from t7669 + their 15 pivots (DATA file)
    W = load(sys.argv[1]); dim = [len(f) for f in W['frames']]
    net0 = fold(W); schedule(net0); h0 = hist(net0, dim)
    pr0, _ = price(W, h0); print('parent paid', sum(h0.values()), pk.kstr(pr0['kappa'], 16), 'S', pr0['S'])
    net = net0
    for ed in edits_from_pivots(sys.argv[2]):
        d, drop, lead, F = ed[:4]
        rb = (abs(dim[net.moves[drop][1]] - dim[net.moves[drop][0]]), abs(dim[net.moves[lead][1]] - dim[net.moves[lead][0]]))
        net = apply(net, d, drop, lead, F, *ed[4:]); schedule(net)
        print(d, drop, lead, 'ranks drop,lead_old', rb, '-> lead_new', abs(dim[net.moves[lead][1]] - dim[net.moves[lead][0]]))
    h = hist(net, dim); dh = {r: h[r] - h0[r] for r in set(h) | set(h0) if h[r] != h0[r]}
    print('paid', sum(h.values()), 'delta per native', dict(sorted(dh.items())))
    print('terminals equal mod p:', terminals_equal(net0, net), terminals_equal(net0, net, 2147483587))
    pr, inv_ = price(W, h, 20); print('kappa', pk.kstr(pr['kappa'], 18), 'S', pr['S'], pk.cite('t7669+15piv', pr))
    import pickle; pickle.dump(net, open(os.path.join(os.path.dirname(__file__), 'net7674.pkl'), 'wb'))

def price_net(W, net, dim, digits=20):
    """PRICEKIT price with helper targets taken from the circuit's own boundary (width may differ from W)."""
    h = W['hosted']; mains = set(W['live']) | {r + 112 for r in W['live']} | set(h.get('X2', [])) | set(h.get('Y2', []))
    from collections import Counter
    T = +Counter(dim[net.final[r]] - dim[net.init[r]] for r in range(len(net.init)) if r not in mains)
    nat = pk.native_from_hist(dict(hist(net, dim)), dict(T), h.get('Dports', []))
    C = pk.load(CALLER); inv_ = pk.invoice(pk.caller_invoice(C), nat)
    return pk.price(inv_, digits), inv_

def load_graph(path):
    """their p104-banked graph JSON (DATA) -> Net"""
    g = json.load(gzip.open(path, 'rt') if path.endswith('.gz') else open(path))
    moves = {k: (a, b) for k, a, b in g['moves']}
    forms = {k: {int(t): Q(c) for t, c in row} for k, row in g['forms']}
    return Net(g['first_output'], g['initial'], g['final'], moves, forms)
