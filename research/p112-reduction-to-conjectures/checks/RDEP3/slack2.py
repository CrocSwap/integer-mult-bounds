# impl 2 (independent): d-coordinates. P2 term bound b2 = 7-(dR-1)^+-(dA-1)^+ capped at 6 each; exact floor e = max(1, 9-dR-dA).
# Also a positive control: apply cost >= 7m - LamP - LamQ + sum slack to exact witnesses (per-term weights), must be <= cost.
import sys, os, json
def b2(dR,dA): return 7-min(6,max(0,dR-1))-min(6,max(0,dA-1))
def ex(dR,dA): return max(1,9-dR-dA)
T={(9-dR,9-dA): ex(dR,dA)-b2(dR,dA) for dR in range(9) for dA in range(9)}
exec(open('slack1.py').read().split('assert')[0])
assert T==S, 'impl mismatch'; print('slack tables agree (81 cells)')
if len(sys.argv)>1:
    W='<workdir>/cards'; Tw=W+'/TWINSWAP'; sys.path.insert(0,W+'/ARCHITECT'); sys.path.insert(0,Tw)
    from retract import *
    os.chdir(Tw)
    def wt(X): return f2rank([LAB[t] for t in X])
    def ctl(tag,P,Q):
        assert check(P,Q,masked=True)==0
        cost=0; bound=0
        for p,q in zip(P,Q):
            R=[t for t in range(n) if p[t]!=0]; A=[t for t in range(n) if q[t]!=0]
            c=bdrank(R,A) if R and A else 0; cost+=c
            if c>0: bound+=b2(9-wt(R),9-wt(A))+T[wt(R),wt(A)]
        print(tag,'m',len(P),'cost',cost,'slack-bound',bound,'ok',bound<=cost); assert bound<=cost
    src=open('witness16.py').read().replace("    P,Q=build(Xh,Yh,E,F)\n","    P,Q=build(Xh,Yh,E,F); STASH.append((mode,P,Q))\n")
    STASH=[]; g={'STASH':STASH,'__name__':'w16'}; exec(src,g)
    for mode,P,Q in STASH: ctl('witness16-'+mode,P,Q)
    d=json.load(open('decoder.json')); ctl('MS3a',[[Fr(x) for x in p] for p in d['P']],[[Fr(x) for x in q] for q in d['Q']])
    from swapfam import feasible_search, build_family
    for kr,kc in [(1,1),(2,2),(1,3)]:
        b,e=feasible_search(kr,kc); Xh,Yh,E,F,names=build_family(*e,verbose=False); P,Q=build(Xh,Yh,E,F); ctl(f'swap({kr},{kc})',P,Q)
