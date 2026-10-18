import sys,time,pickle,itertools
sys.path.insert(0,(__import__('os').environ['HM_ROOT']+'/cards/B147'))
from oracle799 import *
from collections import defaultdict,Counter
O=Oracle();s=O.seq0();B=s['B'];d=O.d
base=O.evaluate(s);K0=base['kappa'];R0=O.replay_rows(s)
EMPTY=O.id.get(())
tgt=lambda q:112<=q<224
PRE=lambda i,e:i<120 and e[0]=='add' and tgt(e[1]) and e[2]>=224
firstw={}
for i,e in enumerate(B):
    if e[1] not in firstw:firstw[e[1]]=i
pairs=[]
for h,ci in firstw.items():
    e=B[ci]
    if h<224 or e[0]!='add' or (e[3],e[4])!=(1,1) or tgt(e[2]) or e[2]==h: continue
    r=e[2]
    pre=[i for i in range(ci) if B[i][0]=='add' and B[i][2]==h]
    if any(not tgt(B[i][1]) for i in pre): continue
    end=len(B)
    for j in range(ci+1,len(B)):
        if B[j][1] in (h,r): end=j;break
    reads=[j for j in range(ci+1,end) if B[j][0]=='add' and tgt(B[j][1]) and B[j][2] in (h,r) and B[j][1]!=B[j][2]]
    pairs.append(dict(h=h,r=r,ci=ci,pre=pre,end=end,reads=reads))
def moves(p):
    ms=[];used=set()
    for j in p['reads']:
        g=B[j];t=g[1];a,b=g[3],g[4]
        if g[2]==p['h']:
            pi=[i for i in p['pre'] if i not in used and B[i][1]==t and (B[i][3],B[i][4])==(-a,b)]
            if not pi: continue
            used.add(pi[0]);ms.append(('h2r',j,pi[0],t))
        else:
            ms.append(('r2h',j,max(p['pre'])+1 if p['pre'] else p['ci'],t,p['h']))
    return ms
def build(mvs):
    Bn=[list(e) for e in B];dele=set();ins=defaultdict(list)
    for m in mvs:
        if m[0]=='h2r':
            Bn[m[1]][2]=B[m[1]][2] and [p for p in pairs if m[1] in p['reads']][0]['r'];dele.add(m[2])
        else:
            Bn[m[1]][2]=[p for p in pairs if m[1] in p['reads']][0]['r'] if False else None
    return Bn
# simpler explicit build
pr_of={}
for p in pairs:
    for j in p['reads']: pr_of[j]=p
def build(mvs):
    Bn=[list(e) for e in B];dele=set();ins=defaultdict(list)
    for m in mvs:
        p=pr_of[m[1]]
        if m[0]=='h2r': Bn[m[1]][2]=p['r'];dele.add(m[2])
        else:
            Bn[m[1]][2]=p['h'];g=B[m[1]]
            ins[m[2]].append(['add',m[3],p['h'],-g[3],g[4],EMPTY])
    out=[]
    for i,e in enumerate(Bn):
        for x in ins.get(i,[]):out.append(x)
        if i in dele:continue
        out.append(e)
    s2=dict(s);s2['B']=out;return s2
def pre_targets(Bx): return {e[1] for i,e in enumerate(Bx[:130]) if e[0]=='add' and tgt(e[1]) and e[2]>=224}
T0=pre_targets(B)
def ev(mvs):
    s2=build(mvs)
    if O.replay_rows(s2)!=R0: return None
    r=O.evaluate(s2)
    T=pre_targets(s2['B'])
    return dict(legal=r['legal'],dk=float(r['kappa']-K0),net=len(T0-T)-len(T-T0),nfin=len(r['fin_raise']),ncen=len(r['cen_viol']))
if __name__=='__main__':
    print(len(pairs),'pairs',sum(len(p['reads']) for p in pairs),'reads',sum(len(moves(p)) for p in pairs),'moves')
    t0=time.time();res={}
    for pi,p in enumerate(pairs):
        ms=moves(p)
        if not ms: continue
        res[('pair',pi)]=ev(ms)
        for m in ms: res[('single',pi,m)]=ev([m])
    print(time.time()-t0)
    leg=[(k,v) for k,v in res.items() if v and v['legal']]
    print('evaluated',len(res),'inexact',sum(1 for v in res.values() if v is None),'legal',len(leg))
    for k,v in leg[:20]:print(k,v)
    print(Counter((k[0],v['legal'],v['net']) for k,v in res.items() if v))
    pickle.dump(res,open('ex1.pkl','wb'))
