#!/usr/bin/env python3
"""Independent event invoice and rational outward-rounded prices. No candidate imports.

New audit code by the execution pricing lane with substantial OpenAI Codex help.
Construction credit: Ali Romman; retained source Cao Yifan, Cinna Davis, zxv,
Jacob Alan Sussman. This verifies prices conditional on separately checked semantics.
"""
import argparse, collections, functools, gzip, hashlib, json
from fractions import Fraction as F
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]/'repository'
S=10**65

def ceildiv(a,b): return -((-a)//b)
def need(p,s):
    if not p: raise ValueError(s)
def read(p):
    b=p.read_bytes(); return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def encode(v):
    if isinstance(v,F): return str(v)
    if isinstance(v,dict): return {str(k):encode(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [encode(x) for x in v]
    return v

def census(w):
    c=w['canonical']; frames=c['frames']; dims=list(map(len,frames)); v=c['v']
    need(len(c['start'])==len(c['final'])==2*v+408 and v==len(c['ports']), 'Main/helper ABI')
    def reduce_vector(x,basis):
        for pivot,row in basis:
            if x & (1<<pivot): x ^= row
        return x
    bases=[]
    for frame in frames:
        basis=[]
        for vector in frame:
            row=reduce_vector(vector,basis);need(row>0,'Independent binary frame')
            basis.append((row.bit_length()-1,row));basis.sort(reverse=True)
        bases.append(basis)
    def subset(a,b): return all(reduce_vector(x,bases[b])==0 for x in frames[a])
    all_profiles={}
    for direction,events in w['programs'].items():
        owned={tuple(x) for x in w.get('owned',{}).get(direction,[['C',0]])}
        current={('L',i):f for i,f in enumerate(c['start'])}
        current.update({r:None for r in owned if r[0]=='C'})
        paid=collections.Counter(); types=collections.Counter(); scalar_types=collections.Counter(); tariff=0
        for e in events:
            kind=e[0]; types[kind]+=1
            if kind=='scalar':
                g,frame=e[1:]; dst=tuple(g[1]);scalar_types[g[0]]+=1
                if g[0] in ('clear','copy'): tariff+=2
                else:
                    q=F(*(g[3:] if g[0]=='add' else g[2:]));n,d=abs(q.numerator),q.denominator
                    need(n>0 and d&(d-1)==0,'Dyadic scalar tariff')
                    if g[0]=='scale':
                        need(n&(n-1)==0,'Unit dyadic scale');tariff+=2*(abs(n.bit_length()-d.bit_length())+int(q<0))
                    else:
                        need(g[0]=='add','Tariff opcode');tariff+=2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
                if g[0]=='clear': current[dst]=frame
                else:
                    need(current[dst]==frame,'Scalar destination frame')
                    if g[0] in ('add','copy'): need(current[tuple(g[2])]==frame,'Scalar source frame')
            elif kind=='warp':
                _,dst,op,a,b=e;dst=tuple(dst)
                need(current[dst]==a,'Warp input frame'); current[dst]=b
            elif kind in ('climb','center'):
                if kind=='climb': _,tag,i,a,b,claimed=e; dst=('L',i)
                else: _,i,a,b,claimed=e; dst=('C',i)
                need(current[dst]==a,'Paid input frame')
                # The price is computed from endpoint dimensions, never its JSON rank.
                rank=abs(dims[b]-dims[a]);need(rank==claimed and rank>0,'Paid rank witness')
                need(subset(a,b) if kind=='climb' else subset(a,b) or subset(b,a),'Nested paid frame')
                paid[rank]+=1;current[dst]=b
            elif kind=='zero_retag':
                _,dst,a,b=e;dst=tuple(dst)
                need(current[dst]==a,'Retag frame');current[dst]=b
            else: need(kind in ('phase','adapter'),'Known event kind')
        need([current['L',i] for i in range(2*v+408)]==c['final'],'Final frame census')
        targets=collections.Counter()
        lost=[]
        for i in range(2*v,2*v+408):
            a,b=c['start'][i],current['L',i]
            rank=dims[b]-dims[a];need(rank>0 and subset(a,b),'Productive rank')
            if ('L',i) in owned: lost.append([i,rank])
            else: targets[rank]+=1
        all_profiles[direction]={'paid':paid,'helpers':targets,'event_types':types,'scalar_types':scalar_types,'real_scalar_allowance':tariff,'surrendered_helpers':lost}
    return all_profiles

def invoice():
    wp=REPO/'research/kappa-joint-relations-20261023/WORD.json.gz'
    sp=REPO/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
    cp=REPO/'research/joint-helper-lattice/CONTROLLER.json'
    w=read(wp);source=read(sp);controller=read(cp)
    successor_path=HERE.parent/'sources/pr5387/research/eight-owned-relations/WORD.json.gz'
    successor=census(read(successor_path))
    new=census(w);old=census(source)
    for direction in new:
        need(successor[direction]['paid']==new[direction]['paid'] and successor[direction]['helpers']==new[direction]['helpers'],'Actual PR5387 same profile')
    def whole(local):
        T=collections.Counter();P=collections.Counter();counts=collections.Counter();parts={}
        v=w['canonical']['v']; h=w['canonical']['h']; step=h-1
        for e in controller['physical_events']:
            counts[e[0]]+=1
            if e[0]=='LOCAL':
                direction='backward' if e[3] else 'forward'
                counts[direction]+=1;T.update(local[direction]['helpers']);P.update(local[direction]['paid'])
            elif e[0]=='QUERY_SHEAR': P[1]+=v
            elif e[0]=='IDLE': P[step*len(e[2])]+=2*v
        main=collections.Counter()
        for exponents in controller['diagonal']:
            need(abs(exponents[0])==1 and set(exponents[1:])<= {0,1},'Whole completed main target')
            main[1+step*sum(exponents[1:])]+=v
        T.update(main)
        return {'targets':dict(sorted(T.items())),'paid':dict(sorted(P.items())),
                'productive_fields':sum(T.values()),'paid_calls':sum(P.values()),
                'target_rank_mass':sum(r*n for r,n in T.items()),'paid_rank_mass':sum(r*n for r,n in P.items()),
                'controller_event_types':counts,'main_targets':main}
    candidate,baseline=whole(new),whole(old)
    delta={k:{r:candidate[k].get(r,0)-baseline[k].get(r,0) for r in set(candidate[k])|set(baseline[k]) if candidate[k].get(r,0)!=baseline[k].get(r,0)} for k in ('targets','paid')}
    need(delta=={'targets':{9:-128},'paid':{1:-128,8:-128}},'Actual whole delta')
    need(candidate['paid_calls']==64148 and candidate['productive_fields']==10800,'Whole counts')
    need(candidate['target_rank_mass']-candidate['paid_rank_mass']==752,'Conserved mass surplus')
    inputs={str(p.relative_to(REPO)):digest(p) for p in (wp,sp,cp)}
    inputs[str(successor_path.relative_to(HERE.parents[1]))]=digest(successor_path)
    return {'candidate_head':'4bd6efa51a495a7c7b7754915cf0244e7e60969e','canonical_main':'1ec1119972c9aefe42525172d07b332fcff81cb4',
            'inputs_sha256':inputs,'local_candidate':new,'local_successor':successor,'successor_head':'b1ab650d36f59e5be682a813145b7c67e219e341','local_baseline':old,'candidate':candidate,'baseline':baseline,'delta':delta,
            'semantic_dependency':'Each retained endpoint must independently satisfy ordinary completed-helper ABI; zero_retag validity and owned lifetimes checked by other lanes.'}

# Each pair is [lower,upper] in units 1/S. All interval operations round out.
def mul(a,b):
    q=[x*y for x in a for y in b]; return min(q)//S,ceildiv(max(q),S)
def add(a,b): return a[0]+b[0],a[1]+b[1]
def scale(a,q):
    q=F(q); x=[n*q.numerator for n in a]
    return min(x)//q.denominator,ceildiv(max(x),q.denominator)
def div(a,b):
    need(b[0]>0,'Positive denominator');q=[F(x*S,y) for x in a for y in b]
    return min(q).__floor__(),max(q).__ceil__()
def constant(q):
    q=F(q)*S;return q.__floor__(),q.__ceil__()
def interval(a): return [F(a[0],S),F(a[1],S)]
def decimal(a,digits=30):
    # Display rounding outward as well; exact bounds are always retained.
    factor=10**digits;return [f'{a[0]*factor//S/ factor:.{digits}f}',f'{ceildiv(a[1]*factor,S)/ factor:.{digits}f}']
@functools.lru_cache(None)
def log(rank):
    need(rank>=1,'Positive integer log')
    if rank==1:return (0,0)
    k=rank.bit_length()-1;x=F(rank,2**k);z=(x-1)/(x+1)
    def atanh(q):
        total=F(0);term=q
        for j in range(90):total+=term/F(2*j+1);term*=q*q
        tail=2*term/(181*(1-q*q))
        return constant(2*total)[0],constant(2*total+tail)[1]
    a=atanh(z);b=atanh(F(1,3));return add(a,scale(b,k))
def exp_positive(a):
    need(a[0]>=0 and a[1]< 16*S,'Exp convergence range')
    term=(S,S);total=term
    for n in range(1,1000):
        term=scale(mul(term,a),F(1,n));total=add(total,term)
        # All subsequent exact terms have ratio <= upper(x)/(n+1).
        if term[1]<=2 and a[1] < (n+1)*S:
            tail=ceildiv(term[1]*a[1],(n+1)*S-a[1])
            return total[0],total[1]+tail
    raise ValueError('Exp iteration limit')
@functools.lru_cache(None)
def power(rank,exponent):
    exponent=F(exponent)
    if exponent==0:return(S,S)
    a=scale(log(rank),abs(exponent));result=exp_positive(a)
    return result if exponent>0 else div((S,S),result)
def moment(hist,exponent):
    result=(0,0)
    for r,n in hist.items():result=add(result,scale(power(int(r),exponent),n))
    return result

def validate_invoice_claim(proposed,derived):
    for kind in ('targets','paid'):
        need(proposed[kind]==derived[kind], 'Proposed '+kind+' disagrees with literal event-derived census')
    return True

def prices(data):
    T=data['candidate']['targets'];P=data['candidate']['paid'];tcount=data['candidate']['productive_fields']
    validate_invoice_claim({'targets':dict(T),'paid':dict(P)},data['candidate'])
    def margin(c):
        a,b=moment(T,1-c),moment(P,1-c);return a[0]-b[1],a[1]-b[0]
    low,high=F('.00302667476807'),F('.00302667476808')
    need(margin(low)[0]>0 and margin(high)[1]<0,'Exact fixed-profile root bracket')
    # Independently certify strictly decreasing M(C) on [0,.05]. Since
    # M'(C)=-sum signed n*r^(1-C)*ln(r), bound that sum from below.
    signed={r:T.get(r,0)-P.get(r,0) for r in set(T)|set(P)}
    derivative_bounds=[]
    for j in range(16):
        l,r=F(j,320),F(j+1,320);lower=0
        for rank,n in signed.items():
            b=mul(power(int(rank),1-r if n>0 else 1-l),log(int(rank)))
            lower+=n*b[0 if n>0 else 1]
        need(lower>0,'Strict decreasing raw moment');derivative_bounds.append(F(lower,S))
    rest=[]
    for j in range(128):
        l,r=F(1,20)+F(19*j,2560),F(1,20)+F(19*(j+1),2560)
        upper=sum(n*power(int(rank),1-l if n>0 else 1-r)[1 if n>0 else 0] for rank,n in signed.items())
        need(upper<0,'Negative moment above .05');rest.append(F(upper,S))
    variants={}
    for label,K,C,rho in [('PR5383',F('.00302666'),F('.00302667'),F(1,10**9)),('PR5387',F('.003026674765'),F('.003026674766'),F(1,10**12))]:
        a,b=moment(T,1-C),moment(P,1-C)
        alpha=div(b,a);gamma=div(moment(P,1-C+F(1,5)),mul(power(20,F(1,5)),a))
        delta=div(constant(21*tcount),mul(power(20,C),a))
        alpha_budget=(scale(a,1-rho)[0]-b[1],scale(a,1-rho)[1]-b[0])
        need(alpha[1]<constant(1-rho)[0],'Reserved alpha');need(gamma[1]<constant(F(97,100))[0] and delta[1]<constant(F(97,100))[0],'Charged tails')
        bound=1/(1+1024*rho)+F(4,2**32)
        need(bound<1,'Funded reserve plus both tails')
        need(F(97,100)**128<F(1,16),'Tail block')
        def tensor_tail(a):
            for _ in range(10): a=mul(a,a)
            return F(a[1],S)
        exact_tail_bound=1/(1+1024*rho)+2*tensor_tail(gamma)+2*tensor_tail(delta)
        need(exact_tail_bound<1,'Actual directed two-tail bound')
        need(20**64<21**63 and 2*(20**1024)**64 <= (145**1024)**63,'Shifted exits and shrinkage')
        eta=scale(power(145,-1024*C),1-C);need(F(eta[0],S)>F(63,64)**1000,'Complement capacity')
        need(F(power(145,1024*C)[1],S)<2**1000,'Initial range')
        rounding_fail=1/(1+1024*F(1,10**13))+F(4,2**32)>=1
        predecessor_reserve_rejected=alpha[0]>constant(1-F(1,10**9))[1]
        if label=='PR5387': need(predecessor_reserve_rejected,'Reject old reserve at stronger C')
        variants[label]={'kappa':K,'tested':C,'reserve':rho,'raw_margin':interval(margin(C)),'target_moment':interval(a),'paid_moment':interval(b),
            'alpha':interval(alpha),'gamma':interval(gamma),'delta':interval(delta),'alpha_budget':interval(alpha_budget),
            'coarse_completed_upper':bound,'coarse_completion_slack':1-bound,'actual_completed_upper':exact_tail_bound,
            'eta':interval(eta),'raw_headroom_over_claim':[low-K,high-K],'raw_headroom_over_tested':[low-C,high-C],
            'coarse_rounding_reserve_1e-13_fails':rounding_fail,'predecessor_reserve_1e-9_rejected':predecessor_reserve_rejected,
            'extra_H1_affordable':int(F(alpha_budget[0],S).__ceil__()-1),
            'tail_offset':F(1,5),'power':1024,'cutoff':20,'floor':21}
    next_tested_grid={}
    for C in [F('.003026674767'),F('.003026674768')]:
        a,b=moment(T,1-C),moment(P,1-C);alpha=div(b,a)
        reserved=constant(1-F(1,10**12));budget=(scale(a,1-F(1,10**12))[0]-b[1],scale(a,1-F(1,10**12))[1]-b[0])
        next_tested_grid[str(C)]={'tested':C,'alpha':interval(alpha),'alpha_budget':interval(budget),'strict_alpha_pass':alpha[1]<reserved[0],'strict_alpha_fail':alpha[0]>=reserved[1]}
    need(next_tested_grid[str(F('.003026674767'))]['strict_alpha_pass'],'Next C grid still passes alpha')
    need(next_tested_grid[str(F('.003026674768'))]['strict_alpha_fail'],'Following C grid fails reserved alpha')
    controls={}
    for name,patch in [('unearned_128_H9',{9:128}),('extra_H1',{1:1})]:
        if name.startswith('unearned'):
            bad={'targets':dict(T),'paid':dict(P)};bad['targets'][9]+=128
            mutant_hash=hashlib.sha256(json.dumps(encode(bad),sort_keys=True,separators=(',',':')).encode()).hexdigest()
            try: validate_invoice_claim(bad,data['candidate'])
            except ValueError as error: controls[name]={'status':'invoice_mutant_rejected','reason':str(error),'added_target_count':128,'recomputed_proposed_invoice_sha256':mutant_hash}
            else: raise ValueError('Unearned productive outputs escaped invoice validator')
        else:
            bad=dict(P);bad[1]+=1
            controls[name]={'margin_upper_at_5383':F(moment(T,1-F('.00302667'))[1]-moment(bad,1-F('.00302667'))[0],S)}
            need(controls[name]['margin_upper_at_5383']<0,'Reject unpriced H1')
    return {'status':'PASS_INDEPENDENT_EVENT_INVOICE_AND_EXACT_PRICES','method':'Integer fixed-point outward rounding 10^-65; rational atanh log series and exp Taylor geometric remainder; no author code imports',
            'raw_root_bracket':[low,high],'min_derivative_negation_lower':min(derivative_bounds),'remaining_moment_upper':max(rest),'variants':variants,'next_tested_1e-12_grid':next_tested_grid,'controls':controls,
            'independence_scope':'Fresh implementation of count/parser and interval arithmetic; no PR5377/5383/5387 or PR5384 arithmetic engine reused. Literal word and controller are common primary evidence.',
            'ceiling_scope':'Unique raw crossing of this exact signed profile for 0<C<1; additional root digits are parameter refinement, not a new construction.'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--invoice-only',action='store_true');args=ap.parse_args()
    data=invoice();(HERE/'INVOICE.json').write_text(json.dumps(encode(data),indent=2,sort_keys=True)+'\n')
    if args.invoice_only: print('PASS_LITERAL_EVENT_CENSUS 64148 paid 10800 productive');return
    result=prices(data);result['invoice_sha256']=digest(HERE/'INVOICE.json');result['checker_sha256']=digest(Path(__file__))
    (HERE/'RESULT.json').write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n');print(result['status'])
if __name__=='__main__':main()
