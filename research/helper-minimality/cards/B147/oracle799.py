"""B126: B102 oracle ported to #664 (promoted canonical word out664/promo/local; pricing 72*local+EXTRA, m=73, W=7168).
API (see NOTES.md):
  O=Oracle()                     load word, frame lattice, tags, pricing
  O.seq0() -> {'A':[..],'B':[..],'tail':[..]}   op lists (op=[kind,t,s,num,den,frame_id])
  O.evaluate(seq) -> dict(cen_viol, fin_raise, profile, mass, b, kappa, legal)  forward min-frame join cascade
        (legal = no centre frame exceeded, no final cap raised; no-op pass = 0 violations)
  O.price(profile) -> (b,kappa)   exact root from 72*local profile + B76 extras (reproduces shipped 1.654108529511355e-3)
  O.replay_rows(seq) -> exact Fraction row state (value check);  O.same_values(seq)
  O.region(block) -> set of register ids (S3/S4 packets + their tags) for a block key string
  O.conflict(o1,o2): ops that do not commute (value order matters)
"""
import sys,gzip,json
sys.path.insert(0,(__import__('os').environ['HM_ROOT']+'/cards/B99/work'))
from collections import Counter
from fractions import Fraction as Q
import lib  # only lib.climbs is used
from decimal import Decimal as D, localcontext
EXTRA={1:1,3:1,44:1,48:2396}  # PLAN.json(#799) minus 72*local
CW664=(__import__('os').environ['HM_ROOT']+'/inputs/words/799-X4-CANONICAL-WORD.json.gz')
M=73;W=7168
def root(H):
    with localcontext() as c:
        c.prec=40
        terms=[(D(r)*D(n)/D(M*W),(D(M)/D(r)).ln()) for r,n in H.items() if n]
        lo=D(0);hi=D('0.01')
        for _ in range(200):
            a=(lo+hi)/2
            if sum(p*(a*l).exp() for p,l in terms)<1:lo=a
            else:hi=a
        return (lo+hi)/2
def regs(e): return [e[1]]+([e[2]] if e[0]=='add' else [])
class Oracle:
    def __init__(s):
        d=json.load(gzip.open(CW664));s.d=d
        s.fr=[tuple(f) for f in d['frames']]
        s.bas=[lib_basis(f) for f in d['frames']]
        s.id={b:i for i,b in enumerate(s.bas)}
        s.jm={}
        s.tag={}  # no TAGS for #664
        s.start=list(d['start']);s.final=list(d['final'])
    def dim(s,f): return len(s.bas[f])
    def join(s,a,b):
        if a==b: return a
        k=(a,b) if a<b else (b,a)
        r=s.jm.get(k)
        if r is None:
            bb=lib_basis(s.bas[a]+s.bas[b])
            if bb not in s.id: s.id[bb]=len(s.bas);s.bas.append(bb)
            r=s.jm[k]=s.id[bb]
        return r
    def sub(s,a,b): return a==b or s.join(a,b)==b
    def seq0(s): return {p:[list(e) for e in s.d[p]] for p in ('A','B','tail')}
    def evaluate(s,seq):
        d=s.d;cur=list(s.start);F=s.join;res={}
        out={'A':[],'B':[],'tail':[]};viol=[]
        def run(part):
            for e in seq[part]:
                rs=regs(e);f=e[-1] if e[-1] is not None else s.id[()] if () in s.id else 0
                for q in rs: f=F(f,cur[q])
                for q in rs: cur[q]=f
                out[part].append(e[:-1]+[f])
        run('A')
        for k,c in enumerate(d['centers']):
            cf=d['center_frames'][k]
            if not s.sub(cur[c],cf): viol.append(c)
            cur[c]=F(cur[c],cf)
        run('B');run('tail')
        fin=list(s.final);nf=[]
        for q in range(len(fin)):
            if not s.sub(cur[q],fin[q]): nf.append(q);fin[q]=F(fin[q],cur[q])
        dd=dict(d,frames=s.bas)
        cl=lib.climbs(dd,A=out['A'],B=out['B'],tail=out['tail'],final=fin)
        prof=Counter(w for _,w,_ in cl)
        r=dict(cen_viol=viol,fin_raise=nf,profile=prof,legal=not viol and not nf,mass=sum(k*v for k,v in prof.items()),neg=sum(1 for _,w,_ in cl if w<0))
        r['b'],r['kappa']=s.price(prof)
        return r
    def price(s,prof):
        H=Counter(EXTRA)
        for w,n in prof.items(): H[w]+=72*n
        b=root(H);return b,b/(1+b)
    def replay_rows(s,seq):
        rows=[{i:Q(1)} if i<112 else {} for i in range(728)]
        for p in ('A','B','tail'):
            for e in seq[p]:
                if e[0]=='add':
                    q=Q(e[3],e[4]);rt=rows[e[1]]
                    for j,x in list(rows[e[2]].items()):
                        z=rt.get(j,0)+q*x
                        if z:rt[j]=z
                        else:rt.pop(j,None)
                else:
                    q=Q(e[2],e[3]);rows[e[1]]={j:q*x for j,x in rows[e[1]].items()}
        return rows
    def region(s,block):
        return {r for r,t in s.tag.items() if t[0] in('S3_packet_copy','S4_slot_copy') and (t[1]==block or t[1].startswith('('+block+','))}
def conflict(o1,o2):
    w1=o1[1];r1=o1[2] if o1[0]=='add' else None
    w2=o2[1];r2=o2[2] if o2[0]=='add' else None
    if w1==w2: return o1[0]!='add' or o2[0]!='add'   # add/add same target commute; scale conflicts
    return w1==r2 or w2==r1
def lib_basis(vs):
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
if __name__=='__main__':
    import time;t=time.time();O=Oracle();s=O.seq0();r=O.evaluate(s)
    print({k:(v if k!='profile' else sorted(v.items())) for k,v in r.items()},time.time()-t)
