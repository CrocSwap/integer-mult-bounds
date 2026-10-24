#!/usr/bin/env python3
"""Independent stdlib census; no retained evaluators or expected profile inputs.
Cao Yifan/Cinna Davis and predecessor construction credit retained. AI assistance.
"""
import argparse, collections, copy, gzip, hashlib, json, pathlib, platform, subprocess, sys, time
from fractions import Fraction
C=collections.Counter
PIN='a5df48c55ea806d7952b65acc9c76d878ff09b13'
WORD='research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
CTRL='research/joint-helper-lattice/CONTROLLER.json'

def need(x,msg):
    if not x: raise ValueError(msg)
def hist(x): return {str(k):v for k,v in sorted(x.items()) if v}
def basis(rows):
    b={}
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k in b:x^=b[k]
            else:b[k]=x;break
    return b
def contained(rows,b):
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k not in b:return False
            x^=b[k]
    return True

def local_census(w):
    c=w['canonical'];fs=c['frames'];bs=[basis(f) for f in fs]
    need(c['v']==112 and c['h']==9 and len(c['start'])==len(c['final'])==632,'local fixed ports/fields')
    need(all(len(b)==len(f) for b,f in zip(bs,fs)),'frame lists are independent bases')
    H=C()
    for r in range(224,632):
        a,b=c['start'][r],c['final'][r]
        need(len(fs[a])<len(fs[b]) and contained(fs[a],bs[b]),'strict helper endpoint inclusion')
        H[len(fs[b])-len(fs[a])]+=1
    directions={}
    for d,p in sorted(w['programs'].items()):
        current={('L',i):f for i,f in enumerate(c['start'])};current['C',0]=None
        counts=C();paid=C();climbs=C();centers=C();scalarops=C();adapters=C();primitives=0;last_phase=None
        for e in p:
            typ=e[0];counts[typ]+=1
            if typ in ('climb','center'):
                if typ=='climb':
                    _,part,i,a,b,rank=e;role=('L',i)
                    need(len(fs[a])<len(fs[b]) and contained(fs[a],bs[b]),'strict paid climb inclusion')
                else:
                    _,i,a,b,rank=e;role=('C',i)
                    need((len(fs[a])<len(fs[b]) and contained(fs[a],bs[b])) or (len(fs[b])<len(fs[a]) and contained(fs[b],bs[a])),'nested centre edge')
                need(current[role]==a and rank==abs(len(fs[b])-len(fs[a])),'paid event source frame and rank')
                current[role]=b;paid[rank]+=1;(climbs if typ=='climb' else centers)[rank]+=1
            elif typ=='warp':
                _,r,op,a,b=e;r=tuple(r);need(current[r]==a,'warp source frame');current[r]=b
            elif typ=='scalar':
                g,f=e[1:];op=g[0];r=tuple(g[1]);scalarops[op]+=1
                if op=='clear':need(r==('C',0),'only owned centre clear');current[r]=f;primitives+=1;continue
                need(current[r]==f,'scalar target frame')
                if op in ('add','copy'):
                    s=tuple(g[2]);need(current[s]==f and r!=s,'scalar source frame/distinctness')
                    if op=='copy':need(r==('C',0),'only owned centre copy');primitives+=1
                    else:
                        q=Fraction(g[3],g[4]);n,den=abs(q.numerator),q.denominator
                        need(n>0 and den&(den-1)==0,'dyadic ADD')
                        primitives+=3+n.bit_length()-1+n.bit_count()+den.bit_length()-1
                else:
                    need(op=='scale','known scalar opcode');q=Fraction(g[2],g[3]);n,den=abs(q.numerator),q.denominator
                    need(n>0 and n&(n-1)==0 and den&(den-1)==0,'dyadic SCALE')
                    primitives+=abs(n.bit_length()-den.bit_length())+int(q<0)
            elif typ=='adapter':adapters[e[1]]+=1
            elif typ=='phase':last_phase=e[1]
            else:need(False,'unknown literal local opcode')
        need([current['L',i] for i in range(632)]==c['final'],'all final frame references')
        need(last_phase=='done' and counts['center']==8 and centers==C({8:8}),'all eight owned centre transports charged')
        need(adapters==C({'old_to_new':224,'new_to_old':224}),'entry and exit adapter marker coverage')
        directions[d]={'paid':hist(paid),'climbs':hist(climbs),'centers':hist(centers),'event_counts':dict(sorted(counts.items())),'scalar_opcodes':dict(sorted(scalarops.items())),'real_scalar_allowance':2*primitives,'adapter_markers':dict(sorted(adapters.items()))}
    need(directions['forward']['paid']==directions['backward']['paid'],'dual paid profile agreement')
    return H,C({int(k):v for k,v in directions['forward']['paid'].items()}),directions

def expected_controller(p,a):
    thick={0,2*p,*range(1,2*p,2)};b=p-1-a
    keep=sum(1<<i for i in [*range(1,2*p-2,2),*range(0,2*a,2),*range(3*(p-1)-b,3*(p-1))])
    events=[];idle_index=0
    def idle(pair,selected):
        nonlocal idle_index
        if keep>>idle_index&1:
            selected=[s for s in selected if s in thick]
            if selected:events.append(['IDLE',pair,selected])
        idle_index+=1
    def local(stage,pair,back):
        events.append(['LOCAL' if stage in thick else 'QUERY_SHEAR',stage,pair,back])
        if stage%2 and stage<=2*p-3:idle((stage+1)//2,range(stage+1))
        elif stage%2==0 and 2<=stage<=2*p-2:idle(stage//2,[stage])
        elif stage==2*p:
            for j in range(p-1):idle(j,range(2*j+3,2*p+1))
    def bridge(dst,src,c):events.extend([['ADD',2*dst,2*src,c],['ADD',2*src+1,2*dst+1,-c]])
    local(0,0,False)
    for j in range(p):
        local(2*j+1,j,True)
        if j<p-1:bridge(j,j+1,1)
        local(2*j+2,j,False)
        if j<p-1:bridge(j,j+1,-1)
    for j in reversed(range(p-1)):bridge(j+1,j,1)
    for j in range(p):events.append(['SIGNED_SWAP',2*j,2*j+1])
    return events,keep,thick

def assemble(w,ctrl):
    H,N,dirs=local_census(w);p,a=ctrl['pairs'],ctrl['prefix_pairs']
    need((p,a,ctrl['kind'],ctrl['ambient_rank'])==(16,7,'complex',145),'fixed controller contract')
    events,keep,thick=expected_controller(p,a)
    need(events==ctrl['physical_events'] and keep==ctrl['keep_mask'],'every controller event matches independent emission')
    T=C();P=C();components={'local_paid':C(),'copied_queries':C(),'whole_idles':C(),'helper_targets':C(),'main_targets':C()};counts=C()
    for e in ctrl['physical_events']:
        counts[e[0]]+=1
        if e[0]=='LOCAL':components['helper_targets'].update(H);components['local_paid'].update(N)
        elif e[0]=='QUERY_SHEAR':components['copied_queries'][1]+=112
        elif e[0]=='IDLE':need(e[2] and len(e[2])==len(set(e[2])),'nonempty distinct idle stages');components['whole_idles'][8*len(e[2])]+=224
    for t in ctrl['diagonal']:
        need(len(t)==34 and t[0] in (-1,1) and all(x in (0,1) for x in t[1:]),'central unit normalizer and unsquared stage factors')
        need({s for s,x in enumerate(t[1:]) if x}<=thick,'no removed stage output credit')
        components['main_targets'][1+8*sum(t[1:])]+=112
    interval_main=C({145:224});interval_idle=C()
    for length in (a,p-1-a):
        for j in range(1,length+1):interval_main[1+8*(j+1)]+=224;interval_idle[8*(j+1)]+=224
    need(components['main_targets']==interval_main and components['whole_idles']==interval_idle,'literal target/idle census agrees with prefix/suffix intervals')
    need((counts['LOCAL'],counts['QUERY_SHEAR'],counts['IDLE'])==(18,15,15),'full/thin/idle multiplicity contract')
    T.update(components['helper_targets']);T.update(components['main_targets'])
    for name in ('local_paid','copied_queries','whole_idles'):P.update(components[name])
    boundary={}
    for side in ('left','right'):
        prog=ctrl['boundaries'][side+'_program'];cnt=C(e[0] for e in prog)
        need(all(Fraction(e[-1]) in (-1,1) for e in prog if e[0] in ('ADD','SCALE')),'unit scalar boundary normalizers')
        matrix=[[Fraction(i==j) for j in range(32)] for i in range(32)]
        for e in prog:
            if e[0]=='SWAP':matrix[e[1]],matrix[e[2]]=matrix[e[2]],matrix[e[1]]
            elif e[0]=='SCALE':matrix[e[1]]=[Fraction(e[2])*v for v in matrix[e[1]]]
            elif e[0]=='ADD':matrix[e[1]]=[x+Fraction(e[3])*y for x,y in zip(matrix[e[1]],matrix[e[2]])]
            else:need(False,'known boundary scalar opcode')
        need(matrix==[[Fraction(x) for x in row] for row in ctrl['boundaries'][side]],'literal scalar boundary program equals declared matrix')
        boundary[side]={'operations':dict(sorted(cnt.items())),'length':len(prog),'matrix_reproduced':True}
    local_scalar=max(x['real_scalar_allowance'] for x in dirs.values());routes=(sum(N.values())+2*408+688)*1000
    scalar_bound=18*10**7+15*1792+32*112*(len(events)+sum(v['length'] for v in boundary.values()))
    need(local_scalar+routes<10**7 and scalar_bound<10**9,'complete retained scalar/routing allowance')
    return {'local_helpers':hist(H),'local_paid':hist(N),'local_directions':dirs,'targets':hist(T),'paid':hist(P),'components':{k:hist(v) for k,v in components.items()},'controller_event_counts':dict(sorted(counts.items())),'productive_fields':sum(T.values()),'paid_calls':sum(P.values()),'target_rank_mass':sum(r*n for r,n in T.items()),'paid_rank_mass':sum(r*n for r,n in P.items()),'rank_mass_surplus':sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items()),'normalizers':{'central_exponents':hist(C(t[0] for t in ctrl['diagonal'])),'main_diagonal_terms':len(ctrl['diagonal']),'boundary_programs':boundary,'native_adapter_markers_per_orientation':448,'extra_recursive_children_for_unit_scalar_normalizers':0},'nonrecursive':{'local_scalar':local_scalar,'local_routes':routes,'local_scalar_plus_routes':local_scalar+routes,'raw_scalar_upper':scalar_bound}}

