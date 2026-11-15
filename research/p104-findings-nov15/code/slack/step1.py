"""DYINGPAIR step 1 [C-param]: price two-arm B layouts (L=17, nl=8) where c own roles entering left stage k die after stage d (< nl-1).
Caps: 'lemma' |S_k|-4 with S_k = roles alive on both sides of the boundary (NONNEST capS). Penalty variant: DYINGGEN Lemma 2 adds |E|-1
extra roles (here 1 for a pair, entering at d+1 and living to the centre); Floor' check |Z_j| >= 2(j+1)+2-b_j with b_j <= #dead roles."""
import sys; sys.path.insert(0,'.')
from layout_price import invoice, price, two_arm
L=17; nl=8
Zof=lambda ms:[sum(1 for m in ms if k in m) for k in range(L)]
def capS(ms):
    cap=[]
    for k in range(L-1):
        if k==nl-1: cap.append(0); continue
        S=sum(1 for m in ms if k in m and k+1 in m); cap.append(max(S-4,0))
    return cap
def dying(specs):
    """specs: list of (arm, k, d, c, extra): in arm 'L' (stages 0..nl-1) or 'R' (mirror), c of the roles entering at arm-depth k now live k..d; extra roles enter at d+1."""
    ms=two_arm()
    for arm,k,d,c,extra in specs:
        if arm=='L': full=set(range(k,nl)); new=set(range(k,d+1)); ex=set(range(d+1,nl))
        else: full=set(range(nl,L-k)); new=set(range(L-1-d,L-k)); ex=set(range(nl,L-1-d))
        for _ in range(c): ms.remove(full); ms.append(set(new))
        for _ in range(extra): ms.append(set(ex))
    return ms
def floor_ok(ms, ndead):
    Z=Zof(ms); return all(Z[j]>=2*(j+1)+2-ndead for j in range(nl))
def go(lab, specs, ndead):
    ms=dying(specs); T,P,Z=invoice(ms,L,capS(ms)); r=price(T,P,lab+(' FLOOR-FAIL' if not floor_ok(ms,ndead) else ''),quiet=False); return r
B=go('B control', [], 0)
best=[]
for c in (1,2):
    for k in range(0,nl-2):
        for d in range(k,nl-2):
            for extra in ((0,1) if c==2 else (0,)):
                r=go('%s k=%d d=%d extra=%d (one arm)'%('pair' if c==2 else 'single',k,d,extra),[('L',k,d,c,extra)],c)
                best.append((min(x/y for x,y in zip(r,B)),c,k,d,extra))
print('--- per-layout min ratio over 3 columns vs B, >= 1.005 passes:')
for t in sorted(best,reverse=True)[:12]: print('  %.4f c=%d k=%d d=%d extra=%d'%t)
print('pass count', sum(1 for t in best if t[0]>=1.005), 'of', len(best))
for (k,d) in ((0,3),(1,4),(0,1),(1,2)):
    for extra in (0,1):
        r=go('pair per arm k=%d d=%d extra=%d'%(k,d,extra),[('L',k,d,2,extra),('R',k,d,2,extra)],2)
