"""Finite bill for the banked five-stage bit word, generalized from the source527/p10 finite_check.run (Dylan Crow, with
Anthropic Claude assistance).  The arithmetic is the original line by line; the changes are explicit parameters:
  * h, m = 5h, v, R, replicas T, literal stock, literal paid histogram, weighted/unit additions and the forward and
    inverse cancellation-free row bounds are inputs (from this package's receipts);
  * NCOPY, the copied-centre temporaries per invocation and 5*NCOPY copy/erase episodes per replica (the original
    writes h for both, since the paired cube has h centres; the E8 word has 9 retained totals at h = 8);
  * the 2h-dimensional rational route template: [[p*, k*], [k*, p*]] for the reference port line q* of the label
    family under its form (original: a triple line under G = I - J/9, denominators 1,2,3,6; E8: a root line under
    <x,y>/2), recomputed and factored into elementary operations, exact inverse replay, omitted factor rejected;
  * K, the conservative extra bank-selector calls, by the original formula 2*5*T*((live-1) + R*m*factors) with
    factors = maxops + (m-1) + m (maxops of the actual charts; an ungauged word has only the identity chart, 0 ops).
Bridged word B_K (DaysSky, assisted with Claude): x['Kpairs'] (default 2) gives S = 2K + 1 invocations, m = S h,
S invocations' additions plus 6(K-1)v twin-bridge additions, route families 2S(2v + R) + 2Kv (each invocation routes
its 2v data and R helper roles in and out; the terminal exchange moves the 2Kv data roles), S*NCOPY*T copy/erase
episodes and the selector bill 2*S*T*(...) (receipts_k.py).  K = 2 gives exactly finite_g.py's 5, 6v, 20v + 10R + 4v
and 5*NCOPY*T; the p = 10 regression path is five-stage and unchanged.
usage: python3 finite_k.py e8 RECEIPTS.json OUT.json  |  python3 finite_k.py regression P10_RECEIPT_DIR"""
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import json, sys, os, importlib.util, gzip
HERE=os.path.dirname(os.path.abspath(__file__))
def ceilq(x): return -((-x.numerator)//x.denominator)
def cutoff_log2(delta,C):
    assert 0<delta<=1 and isinstance(C,int) and C>=1
    return max(1,ceilq(36/delta**2),ceilq(2*(4+(C-1).bit_length())/delta))
def mm(A,B): return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def route_template(h,q,form,g=None,ginv=None):
    """[[g p* g^-1, g k*], [k* g^-1, p*]] with p* = q q^T G/<q,q>; G given by form(x,y) on coordinate vectors
    (bilinear); g = I (the original's reference port) unless a port isometry is given."""
    I=lambda n:[[Q(i==j)for j in range(n)]for i in range(n)]
    Gq=[sum(form(i,j)*q[j] for j in range(h)) for i in range(h)]; nq=sum(q[i]*Gq[i] for i in range(h))
    P=[[Q(q[i])*Gq[j]/nq for j in range(h)]for i in range(h)]
    K=[[Q(i==j)-P[i][j]for j in range(h)]for i in range(h)]
    if g is None: TL,TR,BL=P,K,K
    else: TL,TR,BL=mm(mm(g,P),ginv),mm(g,K),mm(K,ginv)
    rho=[TL[i]+TR[i]for i in range(h)]+[BL[i]+P[i]for i in range(h)]
    a=[r[:]for r in rho];factors=[]
    for j in range(2*h):
        p=next(i for i in range(j,2*h)if a[i][j])
        if p!=j:a[j],a[p]=a[p],a[j];factors.append(('swap',j,p,None))
        if a[j][j]!=1:
            c=1/a[j][j];a[j]=[c*x for x in a[j]];factors.append(('scale',j,None,c))
        for i in range(2*h):
            if i!=j and a[i][j]:
                c=-a[i][j];a[i]=[x+c*y for x,y in zip(a[i],a[j])];factors.append(('add',i,j,c))
    assert a==I(2*h)
    def replay(omit=None):
        a=I(2*h)
        for z in reversed(range(len(factors))):
            if z==omit:continue
            kind,i,j,c=factors[z]
            if kind=='swap':a[i],a[j]=a[j],a[i]
            elif kind=='scale':a[i]=[x/c for x in a[i]]
            else:a[i]=[x-c*y for x,y in zip(a[i],a[j])]
        return a
    assert replay()==rho
    omit=next((i for i,f in enumerate(factors)if f[0]=='add'),0)   # original: the first addition; a route without additions: the first factor
    assert factors and replay(omit)!=rho
    counts=dict(Counter(f[0]for f in factors));denoms=sorted({c.denominator for kind,i,j,c in factors if c is not None})
    serialization=[[kind,i,j,None if c is None else str(c)]for kind,i,j,c in factors]
    return dict(factors=len(factors),factor_counts=counts,denominators=denoms,
        factor_program_sha256=sha256(json.dumps(serialization,separators=(',',':')).encode()).hexdigest(),
        exact_inverse_reconstruction=True,missing_addition_rejected=True)
def bill(x):
    """x: dict with h,m,v,R,T,stock,literal(hist),ncopy,weighted,unit,fwd_row,inv_row,K,coarse,moment_module,route."""
    h,m,v,R,T,stock,ncopy=x['h'],x['m'],x['v'],x['R'],x['T'],x['stock'],x['ncopy']
    literal=Counter(x['literal']);E=sum(literal.values());mass=sum(r*c for r,c in literal.items())
    KP=x.get('Kpairs',2);S=2*KP+1
    assert m==S*h and 0<max(literal)<m
    t=1
    while m**t<=2*max(literal)**t: t+=1          # least halving degree; t = 1 is the original half-shrink (PR234: ratio 5/6, degree four)
    assert m*stock-mass==T*x['deficit']
    d=m*m;N=2*m
    weighted=T*(S*x['weighted']+6*(KP-1)*v);unit=T*(S*x['unit']+6*(KP-1)*v)
    J=T*(2*S*(2*v+R)+2*KP*v);good=8*m*m+8;high=16*(d+1)**2;K=x['K']
    payload=64*x['fwd_row']**3*x['inv_row']**2;assert payload<2**104
    fallback=6*N*(N-1)+3*N+6*(N-1);assert fallback<32*m*m
    coefficient=unit+J*high+J*(stock+ncopy)+E*good+E*(128*N**3)+16*m**3+S*ncopy*T+E+K+1
    assert coefficient<2**80 and 2*m**3*10**16<2**80 and 0<K<2**40 and stock+ncopy<2**80
    mod=x['moment_module'];c=Q(x['coarse']);lo,hi=mod.moment(dict(literal),m,stock,c,True)
    delta_tau=1-hi;delta1=1-Q(mass,m*stock)-Q(1,10**16)*32*m*E/stock;assert delta_tau>0 and delta1>0
    chain=[Q(384599,10**10)];gaps=[]
    for j in range(3):
        old=chain[-1];a=(1-c)*c+c*old;ds=dict(atom=c-a,borrowing=1-a-c,remainder=1-a-c*(1-old),stock=1-c);assert old<a<c<1-a and min(ds.values())>0
        delta=min(ds.values());L=cutoff_log2(delta,coefficient);assert Q(L)*delta**2>=36 and Q(L)*delta>=2*(4+(coefficient-1).bit_length())
        gaps.append(dict(stage=j+1,minimum_gap=str(delta),cutoff_log2_at_charged_coefficient=str(L)));chain.append(a)
    controls=[]
    for name,test in [('zero cutoff gap',lambda:cutoff_log2(Q(0),coefficient)),('negative constant',lambda:cutoff_log2(Q(1,2),0))]:
        try:test()
        except AssertionError:controls.append(name)
        else:raise AssertionError('bad finite cutoff accepted')
    return dict(coefficient=coefficient,coefficient_bits=coefficient.bit_length(),low_matrix_power=d,strict_upper='q^'+str(d+1),
        positive_rank_children=E,rank_mass=mass,weighted_additions=weighted,unit_expanded_additions=unit,route_families=J,
        copy_erase_episodes=S*ncopy*T,payload_prefix_upper=payload,payload_prefix_bits=payload.bit_length(),
        delta_tau_lower=str(delta_tau),delta_linear=str(delta1),bootstrap_chain=list(map(str,chain)),gaps=gaps,
        row_reserve=dict(internal_coefficient=t*(d+1),external_complex_coefficient=20161,**({'halving_degree':t} if t>1 else {})),route=x['route'],rejected_controls=controls)
def load_moment():
    s=importlib.util.spec_from_file_location('m',os.path.join(HERE,'..','..','pricing','moment.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def hist(x): return Counter({int(k):v for k,v in x.items() if v})
if __name__=='__main__':
    mod=load_moment()
    if sys.argv[1]=='regression':
        d=sys.argv[2]; raw=json.load(open(d+'/raw.json')); sc=json.load(open(d+'/scalar.json')); bk=json.load(open(d+'/banks.json'))['banks']
        ma=json.load(open(d+'/math.json'))['mathematics']; fin=json.load(open(d+'/finite.json')); gl=json.load(open(d+'/global_result.json'))
        h=raw['h'];m=5*h;H=hist(raw['five_stage_profile']['histogram'])
        for a,cnt in hist(raw.get('completion_rank_histogram',raw['auxiliary_entrance_rank_histogram'])).items():
            H[5*a]-=cnt
            if not H[5*a]: del H[5*a]
        T=bk['physical_replicas']; literal=Counter({r:T*c for r,c in H.items()})
        q=[int(i<3) for i in range(h)]; form=lambda i,j: Q(int(i==j))-Q(1,9)
        x=dict(h=h,m=m,v=raw['v'],R=raw['physical_R'],T=T,stock=bk['literal_stock'],literal=literal,ncopy=h,deficit=4*raw['v']-5*h*(h-2),
               weighted=sc['forward']['weighted_additions'],unit=sc['forward']['literal_unit_additions'],fwd_row=sc['forward']['max_intermediate_row_l1'],
               inv_row=sc['inverse']['max_intermediate_row_l1'],K=bk['conservative_extra_selector_calls'],coarse=ma['bit_coarse'],moment_module=mod,
               route=route_template(h,q,form))
        r=bill(x)
        assert r['coefficient']==fin['q_power_bound']['coefficient'],(r['coefficient'],fin['q_power_bound'])
        assert r['bootstrap_chain']==fin['bootstrap']['chain'] and r['delta_tau_lower']==fin['moment']['delta_tau_lower'] and r['delta_linear']==fin['moment']['delta_linear']
        assert r['route']['factor_counts']==fin['rational_route']['factor_counts'] and r['route']['factor_program_sha256']==fin['rational_route']['factor_program_sha256']
        assert r['route']['denominators']==[1,2,3,6]
        print('PASS regression: on the p = 10 receipts in',d,'the generalized bill reproduces the coefficient',r['coefficient'],
              ', the moment gaps, the bootstrap chain and the 40-dimensional route program (sha',r['route']['factor_program_sha256'][:12]+'...)')
    else:
        x=json.load(open(sys.argv[2]))
        q=x['qstar']; form=lambda i,j: Q(int(i==j),2)       # E8 form <x,y>/2 in Construction-A coordinates
        x['route']=route_template(x['h'],q,form); x['moment_module']=mod; x['literal']=hist(x['literal'])
        # every port: route conjugated by its W(E8) reflection word (the original's coordinate permutations are free
        # relabelings; here the isometry is a rational program and is charged as part of the port route)
        w=json.load(gzip.open(x['word'],'rt')); Lw=w['lines']; h=x['h']
        ip=lambda a,b: Q(sum(u*t for u,t in zip(a,b)),2)
        def refl(r):
            return [[Q(int(i==j))-Q(r[i]*r[j],2)*2/ip(r,r) for j in range(h)] for i in range(h)]
        isom={0:[[Q(int(i==j)) for j in range(h)] for i in range(h)]}; fr=[0]
        while fr:
            nx=[]
            for a_ in fr:
                for b_ in range(len(Lw)):
                    if b_ in isom or abs(ip(Lw[a_],Lw[b_]))!=1: continue
                    d_=[u-t for u,t in zip(Lw[a_],Lw[b_])] if ip(Lw[a_],Lw[b_])==1 else [u+t for u,t in zip(Lw[a_],Lw[b_])]
                    isom[b_]=mm(refl(d_),isom[a_]); nx.append(b_)
            fr=nx
        assert len(isom)==len(Lw) and Lw[0]==q
        ports=[]; allden=set(); maxf=0
        for t,g in isom.items():
            ginv=[[g[j][i]*1 for j in range(h)] for i in range(h)]          # G = I/2 is scalar, so g^-1 = g^T
            assert mm(g,ginv)==[[Q(int(i==j)) for j in range(h)] for i in range(h)]
            gq=[sum(g[i][j]*q[j] for j in range(h)) for i in range(h)]; assert gq==Lw[t] or gq==[-u for u in Lw[t]]
            r_=route_template(h,q,form,g,ginv); allden|=set(r_['denominators']); maxf=max(maxf,r_['factors'])
        assert all(d_&(d_-1)==0 for d_ in allden), allden          # powers of two: units modulo every odd prime q
        x['route']['all_ports']=dict(ports=len(isom),max_factors=maxf,denominators=sorted(allden))
        r=bill(x); r.pop('route') if False else None
        json.dump({k:(v if not isinstance(v,Counter) else dict(v)) for k,v in r.items()},open(sys.argv[3],'w'),indent=1,default=str)
        print('PASS finite bill (E8, K = %d, m = %d): coefficient %d (%d bits) < 2^80, q-power bound %s, payload prefix %d bits < 104, delta_tau %s, reference route %s; all %d port routes exact elementary programs, at most %d factors, denominators %s (powers of two: units modulo every odd q)'%(
            x.get('Kpairs',2),x['m'],r['coefficient'],r['coefficient_bits'],r['strict_upper'],r['payload_prefix_bits'],r['delta_tau_lower'][:14],r['route']['factor_counts'],r['route']['all_ports']['ports'],r['route']['all_ports']['max_factors'],r['route']['all_ports']['denominators']))
