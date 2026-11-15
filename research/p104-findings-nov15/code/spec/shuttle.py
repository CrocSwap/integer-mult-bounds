"""[C-param] SPECBREAK shuttle.py: a new 1-hop public register is kappa-free; a k-hop one costs the hop-split D0 (new-public-register pricing).
Own code + pricekit.py (vendored from #7607). Run here on the #7546 word (data/w7546.json.gz) under the #7113 caller; the lane ran it on the
frontier word. Asserts: replay ok, kappa of the 1-hop shuttle equal to the base kappa to 34 digits, S unchanged, and dD0 of the
0->4->9 helper equal to 17 (f(9) - f(4) - f(5)) exactly (f = r ln r). Prints PASS_SHUTTLE."""
import sys, copy, math, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, '..'))
import pricekit as pk
W0 = pk.load(os.path.join(_HERE, '..', '..', 'data', 'w7546.json.gz')); C = pk.load(os.path.join(_HERE, '..', '..', 'data', '7113_CALLER.json.gz'))
ci = pk.caller_invoice(C)
def kap(W):
    inv = pk.invoice(ci, pk.native_from_word(W)); pr = pk.price(inv, 40); return pr
def add_public(W, chain):
    """append public register h=n with charts chain[0] -> ... -> chain[-1], MOVEs at program end; owned shifted +1"""
    W = copy.deepcopy(W); n = W['public']
    sh = lambda r: r + 1 if r >= n else r
    prog = []
    for e in W['program']:
        e = list(e); e[1] = sh(e[1])
        if e[0] in ('ADD', 'COPY'): e[2] = sh(e[2])
        prog.append(e)
    for a, b in zip(chain, chain[1:]): prog.append(['MOVE', n, a, b, False])
    W['program'] = prog; W['public'] = n + 1
    W['initial'] = W['initial'] + [chain[0]]; W['final'] = W['final'] + [chain[-1]]
    return W
dim = [len(b) for b in W0['frames']]
sp = [frozenset() for _ in dim]
def span(b):
    s = {0}
    for v in b: s |= {x ^ v for x in s}
    return frozenset(s)
sp = [span(b) for b in W0['frames']]
# pick a nested chain 0-dim -> 4-dim -> 9-dim from existing frames
c0 = dim.index(0); c9 = dim.index(9)
c4 = next(i for i in range(len(dim)) if dim[i] == 4)
base = kap(W0)
print('base kappa', pk.kstr(base['kappa'], 34), 'S', base['S'], 'D0', base['D0'])
res = []
for chain in ([c4, c9], [c0, c4, c9]):
    W = add_public(W0, chain); rp = pk.replay(W)
    pr = kap(W); res.append((rp, pr))
    print('chain dims', [dim[c] for c in chain], 'replay ok', rp['ok'], 'public', W['public'],
          'kappa', pk.kstr(pr['kappa'], 34), 'S', pr['S'], 'dD0 total', pr['D0'] - base['D0'])
f = lambda r: r * math.log(r)
print('predicted dD0 for (4,5) split, x17 calls:', 17 * (f(9) - f(4) - f(5)))

(rp1, pr1), (rp2, pr2) = res
assert rp1['ok'] and rp2['ok']
assert pk.kstr(pr1['kappa'], 34) == pk.kstr(base['kappa'], 34) and pr1['S'] == base['S'] and abs(float(pr1['D0'] - base['D0'])) < 1e-9
assert pr2['S'] == base['S'] and abs(float(pr2['D0'] - base['D0']) - 17 * (f(9) - f(4) - f(5))) < 1e-6
print('PASS_SHUTTLE')
