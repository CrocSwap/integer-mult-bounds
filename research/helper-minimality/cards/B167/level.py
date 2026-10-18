# B167 LEVEL MODEL (exact frame schedule, F_3 value relaxation).
# Theorem used (WLOG): any legal program can be stably reordered so that meetings are sorted by hull size (1,2,4,8 points of the
# AG(3,2) label cube).  Level l = meetings whose join is a flat of size 2^(l-1).  At level l a register either does not move, or joins
# ONE flat class Psi (|Psi|=2^(l-1)); legal iff prev frame <= Psi <= bound(register).  Within a class, any unimodular remix of the members'
# rows is realisable (Euclid; every op's join stays <= Psi).  Value layer: out = U*in, U in GL_n  <=>  in,out generate the same module;
# relaxed to F_3 (spans equal): UNSAT => provably infeasible for ANY horizon (not only K steps).
import json,sys,itertools,argparse,time
from fractions import Fraction as Q
from ortools.sat.python import cp_model
D=(__import__('os').environ['HM_ROOT']+'/cards/B167/')
inst=json.load(open(D+'inst4567.json'))
cols=inst['cols']; LV={int(k):v for k,v in inst['lines_vec'].items()}
REG={r['id']:r for r in inst['regs']}
FREE=[433,435]
def span(vs):
    s={0}
    for v in vs: s|={x^v for x in s}
    return s
def hull(pts):
    sp=span([LV[p] for p in pts]); return frozenset(l for l in cols if LV[l] in sp)
def flats():
    fl={frozenset()}
    cur={frozenset([p]) for p in cols}; fl|=cur
    ch=True
    while ch:
        ch=False
        for a in list(fl):
            for b in list(fl):
                h=hull(a|b)
                if h not in fl: fl.add(h); ch=True
    return sorted(fl,key=lambda f:(len(f),sorted(f)))
FL=flats(); FID={f:i for i,f in enumerate(FL)}
LEVEL={1:1,2:2,4:3,8:4}
def mod3(fr): 
    p,q=fr.numerator,fr.denominator; return (p*pow(q,-1,3))%3
DEC=0
LEMMA=0
def build(drop=(),free=None,levels=4,tgt=None):
    regs=[r for r in inst['regs'] if r['id'] not in drop]; R=len(regs); ids=[r['id'] for r in regs]
    free=set(FREE)-set(drop) if free is None else set(free)
    bset=[frozenset(l for l in cols if LV[l] in set(r['bound'])) for r in regs]
    m=cp_model.CpModel()
    nf=len(FL)
    same_={}
    # class var per reg per level (0 none, else flat id of size 2^(l-1))
    c=[[None]*(levels+1) for _ in range(R)]; phi=[[None]*(levels+1) for _ in range(R)]
    for i,r in enumerate(regs):
        init=FID[frozenset([r['id']])] if r['id'] in cols else 0
        phi[i][0]=m.NewConstant(init)
        for l in range(1,levels+1):
            ok=[0]+[FID[f] for f in FL if len(f) and LEVEL[len(f)]==l and f<=bset[i]]
            c[i][l]=m.NewIntVarFromDomain(cp_model.Domain.FromValues(ok),f'c{i}_{l}')
            phi[i][l]=m.NewIntVar(0,nf-1,f'phi{i}_{l}')
            tab=[]
            for pid in range(nf):
                tab.append((pid,0,pid))
                for cid in ok[1:]:
                    if FL[pid]<=FL[cid]: tab.append((pid,cid,cid))
            m.AddAllowedAssignments([phi[i][l-1],c[i][l],phi[i][l]],tab)
    # values over F3
    x=[[[None]*len(cols) for _ in range(R)] for _ in range(levels+1)]
    for l in range(levels+1):
        for i,r in enumerate(regs):
            for jj,j in enumerate(cols):
                if l==0: x[l][i][jj]=m.NewConstant(1 if r['id']==j else 0)
                else: x[l][i][jj]=m.NewIntVar(0,2,f'x{l}_{i}_{jj}')
    for l in range(1,levels+1):
        inc=[m.NewBoolVar(f'in{l}_{i}') for i in range(R)]
        for i in range(R):
            m.Add(c[i][l]!=0).OnlyEnforceIf(inc[i]); m.Add(c[i][l]==0).OnlyEnforceIf(inc[i].Not())
        same={}
        same_[l]=same
        for i in range(R):
            for k in range(i+1,R):
                b=m.NewBoolVar(f's{l}_{i}_{k}')
                m.Add(c[i][l]==c[k][l]).OnlyEnforceIf([b]); 
                # b <=> c_i==c_k and nonzero
                e=m.NewBoolVar('')
                m.Add(c[i][l]==c[k][l]).OnlyEnforceIf(e); m.Add(c[i][l]!=c[k][l]).OnlyEnforceIf(e.Not())
                m.AddBoolAnd([e,inc[i]]).OnlyEnforceIf(b); m.AddBoolOr([e.Not(),inc[i].Not()]).OnlyEnforceIf(b.Not())
                same[i,k]=b; same[k,i]=b
        for name,(src,dst) in (('A',(x[l-1],x[l])),('B',(x[l],x[l-1]))):
            M=[[None]*R for _ in range(R)]
            for i in range(R):
                for k in range(R):
                    if i==k:
                        M[i][k]=m.NewIntVar(0,2,'')
                        m.Add(M[i][k]==1).OnlyEnforceIf(inc[i].Not())
                    else:
                        M[i][k]=m.NewIntVar(0,2,'')
                        m.Add(M[i][k]==0).OnlyEnforceIf(same[i,k].Not())
            for i in range(R):
                for jj in range(len(cols)):
                    terms=[]
                    for k in range(R):
                        pr=m.NewIntVar(0,4,''); m.AddMultiplicationEquality(pr,[M[i][k],src[k][jj]]); terms.append(pr)
                    q=m.NewIntVar(0,2*R,''); m.Add(sum(terms)==3*q+dst[i][jj])
    # final frame must contain the hull of the target support (and sit inside the bound)
    for i,r in enumerate(regs):
        if r['id'] in free: continue
        S=[int(j) for j in r['row'].keys()]
        lo=hull(S); ok=[FID[f] for f in FL if lo<=f<=bset[i]]
        m.AddAllowedAssignments([phi[i][levels]],[(v,) for v in ok])
    # final
    for i,r in enumerate(regs):
        if r['id'] in free: continue
        sg=m.NewIntVar(1,2,'')
        for jj,j in enumerate(cols):
            t=mod3(Q(r['row'].get(str(j),'0')))
            # x == sg*t mod 3
            q=m.NewIntVar(0,4,''); m.Add(sg*t==3*q+x[levels][i][jj]) if False else None
            pr=m.NewIntVar(0,4,''); m.AddMultiplicationEquality(pr,[sg,m.NewConstant(t)])
            qq=m.NewIntVar(0,2,''); m.Add(pr==3*qq+x[levels][i][jj])
    if LEMMA:
        # implied by the frame argument: a tight register whose target support hull == its (non-whole) bound must join exactly that flat at
        # that level, and a plane stopper needs a whole-bound partner in its plane class.
        for i,r in enumerate(regs):
            if r['id'] in free: continue
            S=[int(j) for j in r['row'].keys()]; hu=hull(S)
            if hu==bset[i] and len(hu) in (2,4):
                l=LEVEL[len(hu)]; m.Add(c[i][l]==FID[hu])
                for l2 in range(l+1,levels+1): m.Add(c[i][l2]==0)
                if len(hu)==4:
                    wl=[k for k in range(R) if len(bset[k])==8]
                    m.Add(sum(same_[l][i,k] for k in wl)>=1)
    if DEC:
        order=[c[i][l] for l in range(1,levels+1) for i in range(R)]
        m.AddDecisionStrategy(order,cp_model.CHOOSE_FIRST,cp_model.SELECT_RANDOM_HALF if DEC==2 else cp_model.SELECT_MIN_VALUE)
    return m,dict(c=c,phi=phi,x=x,ids=ids,regs=regs,R=R,levels=levels)
def show(s,h):
    ids=h['ids']
    for l in range(1,h['levels']+1):
        cls={}
        for i in range(h['R']):
            v=s.Value(h['c'][i][l])
            if v: cls.setdefault(v,[]).append(ids[i])
        print('LEVEL',l,{tuple(sorted(FL[v])):mem for v,mem in cls.items()})
    for i in range(h['R']):
        print(ids[i],[s.Value(h['phi'][i][l]) and sorted(FL[s.Value(h['phi'][i][l])]) for l in range(0,h['levels']+1)])
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--drop',default='');ap.add_argument('--time',type=float,default=300)
    ap.add_argument('--workers',type=int,default=1);ap.add_argument('--free',default=None);ap.add_argument('--seed',type=int,default=1);ap.add_argument('--dec',type=int,default=0);ap.add_argument('--lemma',type=int,default=0)
    a=ap.parse_args()
    drop=tuple(int(s) for s in a.drop.split(',') if s)
    free=None if a.free is None else [int(s) for s in a.free.split(',') if s]
    DEC=a.dec; LEMMA=a.lemma
    m,h=build(drop,free)
    s=cp_model.CpSolver(); s.parameters.num_workers=min(2,a.workers); s.parameters.max_time_in_seconds=a.time; s.parameters.random_seed=a.seed
    t0=time.time(); st=s.Solve(m); print('STATUS',s.StatusName(st),'time %.1f'%(time.time()-t0),'drop',drop,'free',free)
    if st in (cp_model.OPTIMAL,cp_model.FEASIBLE): show(s,h)
