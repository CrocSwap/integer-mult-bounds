import gzip,json,sys
from fractions import Fraction as F
def load(p=__import__('os').environ['EO_ROOT']+'/inputs/words/w1018.json.gz'):
    return json.load(gzip.open(p))
def apply(e,rows):
    if e[0]=='add':
        t,s=e[1:3];q=F(e[3],e[4]);dst=rows[t]
        for k,x in list(rows[s].items()):
            a=dst.get(k,F(0))+q*x
            if a:dst[k]=a
            else:dst.pop(k,None)
    else:
        t=e[1];q=F(e[2],e[3]);rows[t]={k:q*x for k,x in rows[t].items()}
def build(w):
    v=w['report']['v'];n=2*v+w['report']['R']
    main=w['A']+w['cut']+w['B']
    raw=[{k:F(1)} for k in range(n)]
    for e in main:apply(e,raw)
    dirt=[{} for _ in range(n)]
    for y in range(v,2*v):dirt[y]={k:a for k,a in raw[y].items() if k>=2*v}
    for e in w['precondition']:apply(e,dirt)
    comp=[['add',y,k,-a.numerator,a.denominator,[]] for y in range(v,2*v) for k,a in sorted(dirt[y].items())]
    early=w.get('early_cleanup',[]);eid={i for i,U in early}
    tail=[(('E',i),w['cleanup'][i][:-1]+[U]) for i,U in early]
    prog=[(('P',i),e) for i,e in enumerate(w['precondition'])]+[(('C',i),e) for i,e in enumerate(comp)]
    for sec in ('A','cut','B'):
        prog+= [((sec,i),e) for i,e in enumerate(w[sec])]
    prog+=tail+[(('L',i),e) for i,e in enumerate(w['cleanup']) if i not in eid]
    return prog,comp
if __name__=='__main__':
    w=load();prog,comp=build(w)
    print(len(prog),len(comp))
    import collections
    print(collections.Counter(e[0] for _,e in prog))
    print('comp helpers',len({e[2] for e in comp}),'centers',w['centers'])
    print([ (t,e) for t,e in prog if e[0]=='scale' and t[0]!='P'][:5])
