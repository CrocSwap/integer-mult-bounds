# Depth-2 joint edit: main m's stop G is blocked by exactly one contact (partner p, lattice-locked: p's neighbour A
# not inside P / B not containing N).  First edit p's neighbour stop Z in {A,B} (drop or re-stop, any legal edit with
# cost < +LIM), then re-scan m's stop G on the edited word.  Keep pairs with total exact f-cost < 0.
import sys, pickle, jl, scan3, pricekit as pk
LIM = float(sys.argv[3]) if len(sys.argv)>3 else 0.05
from collections import Counter; STAT=Counter()
W = pk.load(sys.argv[1]); M = jl.Word(W); out = []; tried = 0
regs = sorted(M.mains)
for m in regs:
    o = M.path(m)
    for gi in range(1, len(o) - 1):
        P, G, N = o[gi - 1], o[gi], o[gi + 1]
        Gops = [i for i in M.ops[m] if M.tag[i] == G]; cache = {}
        bl = [i for i in Gops if not scan3.opts_for(M, m, i, [P, N], M.ops[m], cache)]
        STAT['bl%d'%min(len(bl),2)]+=1
        if len(bl) != 1: continue
        e = M.ev[bl[0]]; p = e[2] if e[1] == m else e[1]
        if p >= M.n: continue
        po = M.path(p); k = po.index(G)
        for Z in {po[k - 1] if k > 1 else None, po[k + 1] if k + 2 < len(po) else None} - {None}:
            eds = scan3.scan_main(M, p, thresh=LIM, onlyG=Z); STAT['Z']+=1; STAT['Zlegal']+=bool(eds)
            eds.sort(key=lambda r: r['d'])
            for ed in eds[:6]:
                tried += 1
                W1 = M.rebuild(ed['ov']); M1 = jl.Word(W1)
                if G not in M1.path(m): continue
                sec = scan3.scan_main(M1, m, thresh=-ed['d'] - 1e-9, onlyG=G)
                for s2 in sec:
                    out.append(dict(m=m, G=G, p=p, Z=Z, e1=ed, e2=s2, d=ed['d'] + s2['d']))
                    print('PAIR', m, G, 'partner', p, Z, 'd1 %.4f d2 %.4f tot %.4f' % (ed['d'], s2['d'], ed['d'] + s2['d']), flush=True)
print('tried', tried, 'pairs', len(out), dict(STAT))
pickle.dump(out, open(sys.argv[2], 'wb'))
