from reuse import *
from retime import Word,raise_closure,apply_ch,join as rjoin
from cxcheck import check
import hostmodel as HM
import copy
def repair(w,maxn=400):
    """make frame chains legal by raising gate frames (cascade). returns new word or None"""
    w=copy.deepcopy(w)
    W=Word(w)
    for it in range(2000):
        bad=None
        for r in range(W.n):
            cur=W.start[r]
            for i in W.pos[r]:
                if W.sm(cur)&~W.sm(W.F[i]):bad=(r,i,cur);break
                cur=W.F[i]
            if bad:break
        if not bad:
            for i,e in enumerate(W.ops):
                (w['A'][i] if i<W.na else w['B'][i-W.na])[-1]=list(W.F[i])
            return w
        r,i,cur=bad
        nf=rjoin(W.F[i],cur)
        ch=raise_closure(W,i,nf,maxn)
        if ch is None:return None
        apply_ch(W,ch)
    return None
if __name__=='__main__':
    w=load();w['R']=w['report']['R']
    prs,tl=find_pairs.__wrapped__(w) if hasattr(find_pairs,'__wrapped__') else (None,None)

def find_pairs_loose(word):
    R=word['R'] if 'R' in word else word['report']['R'];n=240+R;P=word['ports']
    tl=timeline(word);ops=[e for _,e in tl]
    uses=defaultdict(list)
    for i,e in enumerate(ops):
        F=basis(e[-1]) if e[-1] is not None else None
        for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):uses[r].append((i,F))
    first={r:uses[r][0][0] for r in range(2*v,n)};last={r:uses[r][-1][0] for r in range(2*v,n)}
    ffr={r:(uses[r][0][1] or ()) for r in range(2*v,n)}
    rows=[{r:Q(1)} if r<v else {} for r in range(n)]
    cur=[()]*n
    for r in range(v):cur[r]=(P[r],)
    lasts=defaultdict(list)
    for h,l in last.items():lasts[l].append(h)
    out=[]
    for i,e in enumerate(ops):
        if e[-1] is not None:
            F=basis(e[-1])
            for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):cur[r]=F
        apply(e,rows)
        for h1 in lasts.get(i,[]):
            F1=cur[h1]
            for h2 in range(2*v,n):
                if h2==h1 or first[h2]<=i:continue
                F2=ffr[h2]
                if not span(F1)<=span(F2):continue
                cands=[k for k in range(n) if k!=h1 and rows[k] and k!=h2 and span(cur[k])<=span(F2)]
                sol=solve(rows[h1],cands,rows)
                if sol is not None:out.append((h1,h2,i,sol,F1))
    return out,tl
if __name__=='__main__':
    w=load();w['R']=w['report']['R']
    base,_=check(w,full=False)
    r0=HM.evaluate(base['local_profile'],[9]*560)
    prs,tl=find_pairs_loose(w);print('loose pairs',len(prs))
    good=0
    for (h1,h2,i,sol,F1) in prs:
        w2=rewrite(w,h1,h2,i,sol,tl)
        w3=repair(w2)
        if w3 is None:print(h1,h2,'repair failed');continue
        try:
            rep,_=check(w3,full=True)
        except AssertionError as e:
            print(h1,h2,'check failed',str(e)[:60]);continue
        r=HM.evaluate(rep['local_profile'],[9]*(w3['R']))
        print(h1,h2,'ok R',w3['R'],'b %.6e %+.3f%%'%(r['b'],100*(r['b']/r0['b']-1)),rep['local_profile'])
        good+=1
    print('good',good)
