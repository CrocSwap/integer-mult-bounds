from kern import *
from cxcheck import check
import hostmodel as HM
def span(F):
    s={0}
    for b in F:s|={x^b for x in s}
    return s
def dup_pairs(col):
    key=defaultdict(list)
    for h,c in enumerate(col):
        if not c:continue
        ts=sorted(c);f=c[ts[0]]
        key[tuple((t,c[t]/f) for t in ts)].append(h)
    out=[]
    for g in key.values():
        if len(g)==2:out.append(tuple(g))
    return out
def build_pre(col,plan,first):
    """plan: list of (pivot, donor, E_basis_tuple) with proportional columns. returns pre ops (register ids absolute) and start dict"""
    pre=[];start={}
    for p,d,E in sorted(plan,key=lambda x:len(x[2])):
        cp,cd=col[p],col[d]
        t0=sorted(cd)[0];c=cp[t0]/cd[t0]
        assert all(cp.get(t,0)==c*cd.get(t,0) for t in set(cp)|set(cd))
        q=-c
        pre.append(['add',2*v+d,2*v+p,q.numerator,q.denominator,list(E)])
        start[2*v+p]=list(E)
    return pre,start
if __name__=='__main__':
    w=load();w['R']=w['report']['R'];col,first=setup(w)
    base,_=check(w);print('base profile',base['local_profile'])
    pairs=dup_pairs(col);print(len(pairs))
    plan=[]
    for a,b in pairs:
        I=span(first[a])&span(first[b]);x=[y for y in I if y]
        assert len(x)==1
        plan.append((a,b,(x[0],)))
    pre,start=build_pre(col,plan,first)
    rep,edges=check(w,pre=pre,start=start)
    print('exact ok',rep.get('exact_arbitrary_dirt'),rep['exact_inverse_transpose'],'comp cols',rep['comp_cols'],'profile',rep['local_profile'],'sumwidth',sum(rep['widths']))
    r0=HM.evaluate({1:1912,2:784,3:168,4:224,5:392,8:24},[9]*560)
    r=HM.evaluate(rep['local_profile'],rep['widths'])
    print('b base',r0['b'],'b kernel56',r['b'],'%+.3f%%'%(100*(r['b']/r0['b']-1)),'W',r['W'],r['banks'])
