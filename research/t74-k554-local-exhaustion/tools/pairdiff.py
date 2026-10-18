"""Replace a cancelling read pair (t += c*s at i1, t -= c*s at i2) by reads of the writers of s between i1 and i2.
usage: pairdiff.py WORD out [maxwrites]"""
import sys, json, time
from fractions import Fraction as Q
import _paths
import harness as H
word, out = sys.argv[1], sys.argv[2]; maxw = int(sys.argv[3]) if len(sys.argv) > 3 else 2
P = H.Pricer(word); B = P.base['B']; NB = len(B)
coef = lambda g: Q(g[3], g[4])
reads = {}
for i, g in enumerate(B):
    if g[0] == 'add': reads.setdefault(g[2], []).append(i)
cands = []
for s, rl in reads.items():
    for a in range(len(rl)):
        for b in range(a + 1, len(rl)):
            i1, i2 = rl[a], rl[b]
            if B[i1][1] != B[i2][1] or coef(B[i1]) != -coef(B[i2]): continue
            t = B[i1][1]
            ws = [j for j in range(i1 + 1, i2) if B[j][1] == s]
            if not ws or len(ws) > maxw: continue
            if any(B[j][0] != 'add' for j in ws): continue
            cands.append((s, t, i1, i2, ws))
print('pairs', len(cands), flush=True)
res = []
for s, t, i1, i2, ws in cands:
    c2 = coef(B[i2])
    for mode in ('at_write', 'after_write', 'at_late'):
        ins = []
        ok = True
        for j in ws:
            u = B[j][2]; al = coef(B[j]); lam = c2 * al
            if mode == 'at_write': p = j
            elif mode == 'after_write': p = j + 1
            else:
                # u must be unchanged between j and i2
                if any(B[k][1] == u for k in range(j, i2)): ok = False; break
                p = i2
            ins.append((p, ['add', t, u, lam.numerator, lam.denominator, []]))
        if not ok: continue
        ed = dict(delete=[i1, i2], insert=sorted(ins, key=lambda x: x[0]), tail=[], prepend=[])
        t0 = time.time(); r = P.price(ed, timeout=180)
        res.append(dict(s=s, t=t, i1=i1, i2=i2, ws=ws, mode=mode, status=r.get('status'), delta=r.get('delta'), profile=r.get('profile'), ed=ed))
        flag = '  <<< GAIN' if r.get('delta') is not None and r['delta'] < 0 else ''
        print(s, t, i1, i2, ws, mode, r.get('status'), r.get('delta'), '%.1fs' % (time.time() - t0), flag, flush=True)
        json.dump(res, open(out, 'w'), indent=1)
