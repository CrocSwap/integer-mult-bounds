"""HELPERLB analyze.py (own code). Inputs needs.pkl (per-frame B_G on #7615), chain.py's LP rebuilt here per slice.
(1) slice validation: for a frame subset Sig, native chains restricted to stops in Sig (dropping stops never raises D)
    must cost >= f(2)*sum_{G in Sig} B_G (free endpoints) and >= C2-LP(Sig) (census endpoints).
(2) slack location: per (a,b) class, per dim, per frame; marginal saving of each non-need stop.
(3) exact kappa of hypothetical invoices (PRICEKIT): helpers at the sound floor (681 single-stop helpers T[2],P[1]x2),
    helpers all zero-cost (one hop), and the C2 optimum (flow decomposed into paths)."""
import pickle, math, collections, sys, json
sys.path.insert(0, '../../PRICEKIT'); sys.path.insert(0, '.')
import pricekit as pk
f = lambda r: r * math.log(r) if r > 0 else 0.0
D = pickle.load(open('needs.pkl', 'rb')); out = D['out']; dimk = D['dimk']; chain = D['chain']; ends = D['ends']
B = {G: o['B'] for G, o in out.items()}; need = {G for G in B if B[G] > 0}
def cost(p): return f(p[-1] - p[0]) - sum(f(p[i + 1] - p[i]) for i in range(len(p) - 1))
def restricted(Sig):
    tot = 0.0
    for h, ch in chain.items():
        a, b = ends[h]; tot += cost([a] + [dimk[x] for x in ch[1:-1] if x in Sig] + [b])
    return tot
full = restricted(set(out)); print('native helper D0/call %.4f' % full)
# ---- (1) per-frame and per-dim slices, free-endpoint floor
bad = 0
for G in out:
    if restricted({G}) + 1e-9 < f(2) * B[G]: bad += 1
print('(1) per-frame slices: %d frames, violations %d' % (len(out), bad))
for d in range(1, 9):
    Sig = {G for G in out if dimk[G] == d}
    print('   dim %d: B %4d  floor %8.2f  native-restricted %8.2f' % (d, sum(B[G] for G in Sig), f(2) * sum(B[G] for G in Sig), restricted(Sig)))
# ---- (2) slack: per class
cls = collections.defaultdict(lambda: [0, 0.0, 0.0, 0, 0])
for h, ch in chain.items():
    a, b = ends[h]; c = cls[(a, b)]; c[0] += 1
    c[1] += cost([dimk[x] for x in ch]); c[2] += cost([a] + [dimk[x] for x in ch[1:-1] if x in need] + [b])
    c[3] += len(ch) - 2; c[4] += sum(1 for x in ch[1:-1] if x in need)
print('(2) class (a,b): n, native D, D need-stops-only, stops, need stops')
for k, c in sorted(cls.items(), key=lambda kv: -kv[1][1]):
    if c[1] > 20: print('   %s n=%4d D=%8.1f need-only=%8.1f stops=%5d needstops=%5d' % (k, c[0], c[1], c[2], c[3], c[4]))
# per dim: stops vs B, and marginal saving of dropping each non-need stop (others kept)
st = collections.Counter(); nn = collections.Counter(); sav = collections.Counter(); savF = collections.Counter()
for h, ch in chain.items():
    p = [dimk[x] for x in ch]
    for i in range(1, len(ch) - 1):
        d = p[i]; st[d] += 1
        if ch[i] not in need:
            nn[d] += 1; s = f(p[i + 1] - p[i - 1]) - f(p[i] - p[i - 1]) - f(p[i + 1] - p[i]); sav[d] += s; savF[ch[i]] += s
print('(2) dim: stops, B, excess, non-need stops, sum single-drop saving of non-need stops')
for d in range(1, 9):
    Bd = sum(B[G] for G in out if dimk[G] == d)
    print('   dim %d: stops %5d B %4d excess %5d nonneed %5d drop-saving %8.1f' % (d, st[d], Bd, st[d] - Bd, nn[d], sav[d]))
# excess at need frames (stops beyond B_G), top frames by excess
ex = sorted(((out[G]['P'] - B[G], G) for G in out), reverse=True)[:12]
print('(2) top frames by excess stops (P_G-B_G): ', [(G, dimk[G], out[G]['P'], B[G]) for e, G in ex])
print('    zero-need frames: %d, their stops %d' % (sum(1 for G in out if B[G] == 0), sum(out[G]['P'] for G in out if B[G] == 0)))
# ---- (3) exact kappa of hypothetical invoices
W = pk.load('../../ATTACK/COURIER226/hit_c226_1.json.gz'); C = pk.load('../../MONOCALLER/7113_CALLER.json')
ci = pk.caller_invoice(C); L = ci['nJ']; nat = pk.native_from_word(W); inv = pk.invoice(ci, nat)
base = pk.price(inv, 20); K0 = float(base['kappa']['lo']); print('(3) control kappa', pk.kstr(base['kappa'], 14), 'D0', float(base['D0']))
n = len(W['initial']); live = set(W['live']); H = W['hosted']
main = live | {r + 112 for r in live} | set(H['X2']) | set(H['Y2'])
dim = [len(b) for b in W['frames']]
hT = collections.Counter(); hP = collections.Counter()
for r in range(n):
    if r not in main: hT[dim[W['final'][r]] - dim[W['initial'][r]]] += L
for e in W['program']:
    if e[0] == 'MOVE' and e[1] < n and e[1] not in main: hP[abs(dim[e[3]] - dim[e[2]])] += L
def kap(addT, addP):
    T = collections.Counter(inv['T']); P = collections.Counter(inv['P'])
    T.subtract(hT); P.subtract(hP); T.update(addT); P.update(addP)
    T = {k: v for k, v in T.items() if v}; P = {k: v for k, v in P.items() if v}
    pr = pk.price(dict(inv, T=T, P=P), 20); return float(pr['kappa']['lo']), float(pr['D0'])
k0, d0 = kap({}, {}); print('    helpers removed (all one-hop, D=0): kappa %s x%.4f D0/call %.2f' % ('%.10f' % k0, k0 / K0, d0 / L))
nB = sum(B.values()); k1, d1 = kap({2: nB * L}, {1: 2 * nB * L})
print('    helpers at sound floor (%d single stops): kappa %s x%.4f D0/call %.2f' % (nB, '%.10f' % k1, k1 / K0, d1 / L))
pickle.dump(dict(cls=dict(cls), st=st, nn=nn, sav=sav, savF=savF, k0=k0, k1=k1), open('analyze.pkl', 'wb'))
