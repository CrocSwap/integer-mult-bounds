# B171: B172 Lawler certificate generalised to an arbitrary word (#799 canonical). Single process.
import gzip,json,csv,collections,sys
from fractions import Fraction as Q
def basis(vs):
    b={}
    for x in vs:
        for p in sorted(b,reverse=True):
            if x>>p&1:x^=b[p]
        if x:
            p=x.bit_length()-1
            for q in b:
                if b[q]>>p&1:b[q]^=x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))
def ok(F,ports):return all(((f&p).bit_count()%2==0) for f in F for p in ports)
def load(path):
    d=json.load(gzip.open(path));v=d['v']
    ops=[(e[1],e[2] if e[0]=='add' else None,e) for p in ('A','B','tail') for e in d[p]]
    return d,v,ops
def run(path,withcenter=False,skipzero=False):
    d,v,ops=load(path);n=len(d['start']);P=d['ports']
    fr=[basis(d['frames'][f]) for f in d['start']]
    # exact rows to find copies
    rows=[{i:Q(1)} if i<v else {} for i in range(n)]
    SEQ=[];Lpre=[];copies=[];fill=set();nzero=0
    site={int(x['reg']):x['site'][:2] for x in csv.DictReader(open((__import__('os').environ['HM_ROOT']+'/inputs/ledger_helpers.csv')))}
    for t,s,e in ops:
        if e[0]=='add':
            q=Q(e[3],e[4])
            if t not in fill and not rows[t] and rows[s]:
                fill.add(t)
                if site.get(t) in('S3','S4'): copies.append((site[t],s,t,len(SEQ)))
            rt=rows[t]
            for j,x in list(rows[s].items()):
                z=rt.get(j,0)+q*x
                if z: rt[j]=z
                else: rt.pop(j,None)
            zero=not rows[s]   # value-zero add: the source row is empty, nothing is delivered
            SEQ.append((t,s));Lpre.append((fr[t],fr[s]))
            if zero: nzero+=1
            if not (skipzero and zero): fr[t]=basis(list(fr[t])+list(fr[s]))
        else:
            q=Q(e[2],e[3]);rows[t]={j:q*x for j,x in rows[t].items()}
    run.nzero=nzero
    return d,v,SEQ,Lpre,copies,P
def taint_from(SEQ,v,P,q,k,sink):
    T=set([q-v]) if v<=q<2*v else set(); lab={q}
    for t,s in SEQ[k+1:]:
        if s in lab and t not in sink:
            lab.add(t)
            if v<=t<2*v:T.add(t-v)
    return T
def lawler(visits,base,prec=()):
    n=len(visits);rem=set(range(n));order=[]
    while rem:
        J=basis(list(base)+[f for i in rem for f in visits[i][0]])
        good=[i for i in rem if ok(J,visits[i][1])]
        if not good:return None,rem
        i=good[0];order.append(i);rem.discard(i)
    return order[::-1],None
def certify(d,v,SEQ,Lpre,copies,P):
    out=collections.Counter();bad=[]
    for kind,a,b,k in copies:
        # k = index of the copy op; visits are ops k+1..; base = a's frame before copy
        base=Lpre[k][1];sink={a,b};V=[];chain=[]
        for x in (a,b):
            for kk in range(k+1,len(SEQ)):
                t,s=SEQ[kk]
                if x not in (t,s):continue
                qq=s if t==x else t
                g=Lpre[kk][1] if t==x else Lpre[kk][0]
                T=taint_from(SEQ,v,P,qq,kk,sink)
                V.append((g,[P[w] for w in T]));chain.append(x)
        o,rem=lawler(V,base)
        # each chain alone
        sa=[lawler([V[i] for i in range(len(V)) if chain[i]==x],base)[0] is not None for x in (a,b)]
        # two-visit conflict?
        out[(kind,'PASS' if o else 'FAIL','chains-alone-ok' if all(sa) else 'chain-alone-FAIL')]+=1
        if o:bad.append((kind,a,b,k,o))
    return out,bad
if __name__=='__main__':
    path=sys.argv[1] if len(sys.argv)>1 else (__import__('os').environ['HM_ROOT']+'/inputs/words/799-X4-CANONICAL-WORD.json.gz')
    d,v,SEQ,Lpre,copies,P=run(path)
    print('ops',len(SEQ),'copies',collections.Counter(c[0] for c in copies))
    out,bad=certify(d,v,SEQ,Lpre,copies,P)
    for k,c in sorted(out.items()):print(k,c)
    print('passing copies',len(bad));print(bad[:10])
    # robustness to the g hypothesis: recompute the partner frames g skipping the value-zero adds (source row empty), re-run Lawler
    d,v,SEQ,Lpre,copies,P=run(path,skipzero=True)
    out,bad=certify(d,v,SEQ,Lpre,copies,P)
    print('value-zero adds skipped',run.nzero)
    print('skip-zero',dict(sorted(out.items())))
    print('skip-zero passing copies',len(bad))
