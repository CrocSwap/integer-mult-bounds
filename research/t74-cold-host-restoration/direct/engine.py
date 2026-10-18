"""Independent exact verifier for the finite direct-host-restoration domain.

No optimizer or predecessor Python is imported. GF(2)^9 subspaces are reduced
from literal vectors. Equality at a warp/cut is imposed on the preceding gate;
all gates take joins. A forced vector outside any fixed cap proves infeasibility.
Scalar recovery is a separate rational inverse-substitution computation.
"""
from collections import defaultdict, Counter
from fractions import Fraction
from functools import lru_cache
from itertools import permutations
from bisect import bisect_right, bisect_left
import json


def require(p, reason):
    if not p:
        raise ValueError(reason)


@lru_cache(maxsize=100000)
def basis(vectors):
    rows=[0]*9
    for x in vectors:
        require(isinstance(x,int) and 0<=x<512, 'vector outside GF2^9')
        for bit in range(8,-1,-1):
            if x & (1<<bit):
                if rows[bit]:
                    x ^= rows[bit]
                else:
                    rows[bit]=x
                    break
    for bit in range(9):
        if rows[bit]:
            for upper in range(bit+1,9):
                if rows[upper] & (1<<bit): rows[upper] ^= rows[bit]
    return tuple(x for x in reversed(rows) if x)


@lru_cache(maxsize=100000)
def join(a,b): return basis(a+b)


def subset(a,b): return join(a,b)==b


def first_missing(a,b):
    return next((x for x in a if not subset((x,),b)),None)


FULL=basis(tuple(1<<i for i in range(9)))


@lru_cache(maxsize=None)
def port_end(p):
    return basis(tuple(x for x in range(512) if (x&p).bit_count()%2==0))


def regs(e): return tuple(e[1:3] if e[0]=='add' else e[1:2])


class Model:
    """Acyclic monotone frame lattice; records exact necessary lower frames."""
    def __init__(self,w,insertion=None,host_end=None,operator_fix=False):
        v=w['report']['v'];n=2*v+w['report']['R'];require(w['report']['h']==9,'h !=9')
        self.start=[(p,) for p in w['ports']]+[()]*(n-v)
        self.end=[FULL]*v+[port_end(p) for p in w['ports']]+[FULL]*(n-2*v)
        for q,U in w['start_extra'].items():self.start[int(q)]=basis(tuple(U))
        for q,U in w['helper_final'].items():self.end[int(q)]=basis(tuple(U))
        if host_end:self.end[host_end[0]]=basis(tuple(host_end[1]))
        self.live=set(range(n))-set(w['removed']);self.v=v
        pins={v+t:basis(tuple(w.get('target_levels',{}).get(str(t),()))) for t in range(v)}
        pins.update({q:basis(tuple(U)) for q,U in zip(w['centers'],w['center_frames'])})
        self.events=[];self.positions={};self.gate_frames={};self.histories=defaultdict(list)
        def gate(sec,i,g):
            self.positions[sec,i]=len(self.events)
            self.events.append(('gate',regs(g),sec,i,g[-1]))
        def warp(q,U,E,sec,i):
            self.events.append(('warp',q,basis(tuple(U)),basis(tuple(E)),sec,i))
        if operator_fix:warp(w['warps'][-1][1],(),(),'inverse-prelude',0)
        for i,g in enumerate(w['A']):
            if g[0]=='warp':warp(g[1],g[3],g[4],'A',i)
            else:gate('A',i,g)
        self.events.append(('cut',pins))
        bypos=defaultdict(list)
        for op,rec in enumerate(w['warps'],1):bypos[rec[0]].append((op,rec))
        def insert_at(sec,i):
            if insertion and insertion[0]==sec and insertion[1]==i:
                for j,q in enumerate(insertion[2]):gate('undo',j,['add',host_end[0],q,1,1,[]])
        for i in range(len(w['B'])+1):
            for op,rec in bypos[i]:warp(rec[1],rec[3],rec[4],'Bwarp',op)
            insert_at('B',i)
            if i<len(w['B']):gate('B',i,w['B'][i])
        for i in range(len(w['restore'])+1):
            insert_at('restore',i)
            if i<len(w['restore']):gate('restore',i,w['restore'][i])
        # Equalities cannot be paid by an unrecorded jump immediately before a
        # warp/cut. Their frames must already be attained at the last gate.
        forced=defaultdict(tuple);last=[None]*n;fixed=list(self.start);static=[]
        def fix(q,U,where):
            if last[q] is None:
                if fixed[q]!=U:static.append(dict(kind='static-equality',register=q,where=where))
            else:forced[last[q]]=join(forced[last[q]],U)
        for t,e in enumerate(self.events):
            if e[0]=='gate':
                for q in e[1]:last[q]=t
            elif e[0]=='warp':
                _,q,U,E,sec,i=e;fix(q,U,(sec,i));last[q]=None;fixed[q]=E
            else:
                for q,U in pins.items():fix(q,U,'cut')
        self.violations=static;current=list(self.start);self.lower={}
        def cap(q,U,where):
            if not subset(current[q],U):
                self.violations.append(dict(kind='cap',register=q,where=where,lower=list(current[q]),upper=list(U),missing_vector=first_missing(current[q],U),register_kind='source' if q<v else 'target' if q<2*v else 'helper'))
        for t,e in enumerate(self.events):
            if e[0]=='gate':
                _,rr,sec,i,_=e;L=forced[t]
                for q in rr:L=join(L,current[q])
                self.lower[t]=L
                for q in rr:current[q]=L;self.histories[q].append((t,L))
            elif e[0]=='warp':
                _,q,U,E,sec,i=e;cap(q,U,(sec,i));current[q]=E;self.histories[q].append((t,E))
            else:
                for q,U in pins.items():
                    cap(q,U,'cut');current[q]=join(current[q],U);self.histories[q].append((t,current[q]))
        for q in sorted(self.live):cap(q,self.end[q],'end')
        self.times={q:[t for t,U in h] for q,h in self.histories.items()}

    def floor(self,q,time):
        i=bisect_right(self.times.get(q,()),time)-1
        return self.histories[q][i][1] if i>=0 else self.start[q]

    def literal_check(self,w):
        """Stored frames obey every lower constraint; separate from scalar map."""
        current=list(self.start);paid=Counter();npre=w.get('prelude_events',0)
        for t,e in enumerate(self.events):
            if e[0]=='gate':
                _,rr,sec,i,frame=e;U=basis(tuple(frame))
                require(subset(self.lower[t],U),('literal below floor',sec,i))
                for q in rr:
                    require(subset(current[q],U),('literal nonmonotone',q,sec,i))
                    if len(U)>len(current[q]):paid[len(U)-len(current[q])]+=1
                    current[q]=U
            elif e[0]=='warp':
                _,q,U,E,sec,i=e;require(current[q]==U,('literal warp equality',q,sec,i));current[q]=E
            else:
                for q,U in e[1].items():require(current[q]==U,('literal cut equality',q))
        for q in self.live:
            require(subset(current[q],self.end[q]),('literal end',q))
            if len(self.end[q])>len(current[q]):paid[len(self.end[q])-len(current[q])]+=1
        levels={int(q):basis(tuple(U)) for q,U in w.get('target_levels',{}).items()}
        for q,U0 in zip(w['centers'],w['center_frames']):
            U=basis(tuple(U0));served={levels.get(e[1]-self.v,()) for e in w['cut'] if e[2]==q}
            for T in sorted(served,key=lambda x:-len(x)):
                require(subset(T,U),'center path nonnested')
                if T!=U:paid[len(U)-len(T)]+=1
                U=T
        require(dict(paid)=={int(k):v for k,v in w['report']['local_profile'].items()},'literal paid profile')
        inv=Counter(len(self.end[q])-len(self.start[q]) for q in self.live if q>=2*self.v)
        require(dict(inv)=={int(k):v for k,v in w['report']['width_inventory'].items()},'literal inventory')
        return dict(paid)


def substitute(coeff,e):
    if e[0]=='warp':
        q,op=e[1:3];out={}
        for (r,word),a in coeff.items():
            if r==q:word=word[:-1] if word and word[-1]==op else word+(-op,)
            out[r,word]=out.get((r,word),Fraction(0))+a
        return {k:a for k,a in out.items() if a}
    x=e[1]
    if e[0]=='add':
        a=Fraction(e[3],e[4]);new=defaultdict(Fraction)
        for (r,word),v in list(coeff.items()):
            if r==x:new[e[2],word]-=a*v
        for key,v in new.items():coeff[key]=coeff.get(key,Fraction(0))+v
    else:
        a=Fraction(e[2],e[3])
        for key in list(coeff):
            if key[0]==x:coeff[key]/=a
    return {k:a for k,a in coeff.items() if a}


def recovery(w,model):
    op=len(w['warps']);start,c,*_=w['warps'][-1]
    last=max(i for i,e in enumerate(w['B']) if c in regs(e));coeff={(c,()):Fraction(1)}
    bypos=defaultdict(list)
    for oi,rec in enumerate(w['warps'],1):
        if oi!=op:bypos[rec[0]].append(['warp',rec[1],oi])
    rows=[];boundary_checks=0
    def sample(sec,slot,index):
        nonlocal boundary_checks
        require(all(not word for q,word in coeff),'nonscalar recovery not in this finite domain')
        expr={r:a for (r,_),a in coeff.items()};L=()
        for r in expr:L=join(L,model.floor(r,model.positions[sec,index]))
        if sec=='B':
            require(not any(e[1] in expr for e in bypos[slot]),'participating warp at insertion boundary')
            boundary_checks+=1
        rows.append(dict(section=sec,slot=slot,expression={str(r):str(a) for r,a in expr.items()},floor_join=list(L),rank=len(L),additions=len(expr)-(c in expr),scale=expr.get(c)!=1))
    for i in range(start,len(w['B'])):
        for e in bypos[i]:coeff=substitute(coeff,e)
        coeff=substitute(coeff,w['B'][i])
        if i>=last:sample('B',i+1,i)
    for e in bypos[len(w['B'])]:coeff=substitute(coeff,e)
    for i,e in enumerate(w['restore']):
        coeff=substitute(coeff,e);sample('restore',i+1,i)
    return rows,boundary_checks


def slot_classes(w,rows):
    touch=defaultdict(list);nB=len(w['B'])
    for i,e in enumerate(w['B']+w['restore']):
        for q in regs(e):touch[q].append((2*i+1,'gate',i))
    for oi,rec in enumerate(w['warps'],1):touch[rec[1]].append((2*rec[0],'warp',oi))
    for q in touch:touch[q].sort()
    seen={}
    for row in rows:
        if row['rank']!=8:continue
        at=row['slot'] if row['section']=='B' else nB+row['slot'];cut=2*at+1;keys=[]
        for q in sorted(map(int,row['expression'])):
            ts=touch[q];i=bisect_left([t[0] for t in ts],cut)
            keys.append((q,ts[i-1] if i else None,ts[i] if i<len(ts) else None))
        key=json.dumps([row['expression'],row['floor_join'],keys],sort_keys=True)
        if key not in seen:seen[key]=dict(row=row,equivalent_slots=[])
        seen[key]['equivalent_slots'].append([row['section'],row['slot']])
    return list(seen.values())


def check_case(name,w,full=True):
    model=Model(w);require(not model.violations,('baseline lower frame violation',name,model.violations[:1]));model.literal_check(w)
    rows,boundaries=recovery(w,model);h,c=map(int,name[2:].split('_'));require(c==w['warps'][-1][1],'case host mismatch')
    classes=slot_classes(w,rows);results=[]
    if full:
        for ci,cl in enumerate(classes):
            row=cl['row'];require(row['expression'].get(str(c))=='1','nonunit host coefficient')
            qs=[int(q) for q,a in row['expression'].items() if int(q)!=c and Fraction(a)]
            for ordering in permutations(qs):
                m=Model(w,(row['section'],row['slot'],ordering),(c,row['floor_join']),True)
                require(m.violations,('unexpected feasible width8 class',name,ci,ordering))
                targets=[v for v in m.violations if v.get('register_kind')=='target' and v.get('where')=='end']
                witness=targets[0] if targets else m.violations[0]
                results.append(dict(class_id=ci,order=list(ordering),witness=witness,has_target_end_witness=bool(targets)))
    row_bytes=json.dumps(rows,sort_keys=True,separators=(',',':')).encode()
    import hashlib
    return dict(case=name,slots=len(rows),B_boundary_checks=boundaries,min_rank=min(r['rank'] for r in rows),rank_histogram=dict(Counter(r['rank'] for r in rows)),rows_sha256=hashlib.sha256(row_bytes).hexdigest(),classes=len(classes),orders=len(results),target_end_witnesses=sum(r['has_target_end_witness'] for r in results),results=results)


def verify_derivation(parent,w,h,c):
    """Literal hosting transformation, independently checked without a solver.

    Gate frames may be the supplied certified refit; scalar gates, every fixed
    interface, initial correction, warp and inverse-reverse cleanup are bound.
    G is independently checked, rather than assuming the builder's completion.
    """
    v=parent['report']['v'];n=2*v+parent['report']['R'];B=parent['B']
    def unframe(gs):return [g[:-1] for g in gs]
    require(str(c) in parent['helper_final'] and str(c) not in parent['start_extra'],'host not cold')
    require(str(h) in parent['start_extra'],'hostee not entering')
    require(not any(c in regs(g) for g in parent['restore']),'host in restore')
    require(not any(rec[1] in (c,h) for rec in parent['warps']),'prior host/hostee warp')
    pos=[i for i,g in enumerate(B) if h in regs(g)]
    j=next(i for i in pos if not(B[i][0]=='add' and B[i][2]==h and v<=B[i][1]<2*v))
    reads=[i for i in pos if i<j];readset=set(reads)
    require(max((i for i,g in enumerate(B) if c in regs(g)),default=-1)<j,'host not retired')
    out=[]
    for i,g0 in enumerate(B):
        if i in readset:continue
        g=list(g0)
        if i>=j:
            for k in (1,2) if g[0]=='add' else (1,):
                if g[k]==h:g[k]=c
        out.append(g)
    require(unframe(out)==unframe(w['B']),'derived B scalar word')
    for sec in ('A','restore'):require(unframe(parent[sec])==unframe(w[sec]),('unchanged scalar section',sec))
    for sec in ('precondition','compensation','cut','ports','centers','center_frames','target_levels','prelude_events'):
        require(parent.get(sec)==w.get(sec),('unchanged interface',sec))
    shift=lambda x:x-sum(i<x for i in reads)
    expected_warps=[[shift(rec[0])]+rec[1:] for rec in parent['warps']]
    require(w['warps'][:-1]==expected_warps,'retained warps')
    position,host,G,U,E=w['warps'][-1]
    require(position==shift(j) and host==c,'new warp position/host')
    require(basis(tuple(U))==basis(tuple(parent['helper_final'][str(c)])),'new warp input frame')
    require(len(G)==9 and len(basis(tuple(G)))==9,'new warp noninvertible')
    def apply(x):
        y=0
        for bit in range(9):
            if x>>bit&1:y^=G[bit]
        return y
    require(basis(tuple(map(apply,U)))==basis(tuple(E)),'G(U) != E')
    vec=defaultdict(Fraction)
    for i in reads:g=B[i];vec[g[1]]+=Fraction(g[3],g[4])
    for g in reversed(parent['precondition']):
        if g[0]=='add':vec[g[1]]-=Fraction(g[3],g[4])*vec[g[2]]
        elif g[1] in vec:vec[g[1]]/=Fraction(g[2],g[3])
    extra=[dict(target=t,source=c,operator_word=[len(w['warps'])],coefficient=str(a)) for t,a in sorted(vec.items()) if a]
    require(w['initial_corrections']==parent['initial_corrections']+extra,'pulled-back initial corrections')
    ends=dict(parent['helper_final']);del ends[str(c)];starts=dict(parent['start_extra']);del starts[str(h)]
    require(w['helper_final']==ends and w['start_extra']==starts,'changed helper endpoints')
    require(w['removed']==parent['removed']+[h],'removed helper list')
    bypos=defaultdict(list)
    for op,rec in enumerate(w['warps'],1):bypos[rec[0]].append(['warp',rec[1],op])
    forward=list(w['A'][w.get('prelude_events',0):])
    for i in range(len(w['B'])+1):
        forward.extend(bypos[i])
        if i<len(w['B']):forward.append(w['B'][i])
    forward.extend(w['restore']);restored=set(map(int,w['helper_final']))
    def buf(q):return q+n if q in restored else q
    cleanup=[]
    for g in reversed([g for g in forward if g[0]=='warp' or not(v<=g[1]<2*v)]):
        if g[0]=='warp':cleanup.append(['warp',buf(g[1]),-g[2],list(FULL)])
        elif g[0]=='add':cleanup.append(['add',buf(g[1]),buf(g[2]),-g[3],g[4],list(FULL)])
        else:cleanup.append(['scale',buf(g[1]),g[3],g[2],list(FULL)])
    require(unframe(cleanup)==unframe(w['cleanup']),'derived inverse-reverse cleanup')
    require(all(basis(tuple(g[-1]))==FULL for g in w['cleanup']),'cleanup not FULL')
    return dict(hostee=h,host=c,first_write=j,anticipatory_reads=reads,initial_corrections=len(extra),status='PASS_LITERAL_HOSTING_DERIVATION')
