"""Complete p16 price and finite compiler for a changed native profile.

Adapted from Cinna Davis's PR4470 arithmetic, retaining zxv's paid tensor
completion/logarithmic majorant and Jacob Alan Sussman's mixed-job flow.
Apache-2.0. Substantial OpenAI Codex assistance. Native admission is separate.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import math
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,why):
    if not ok:raise ValueError(why)

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    return m

def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

def read(path):
    import gzip
    b=path.read_bytes();return json.loads(gzip.decompress(b) if path.suffix=='.gz' else b)

def assemble(local):
    H={int(k):v for k,v in local['helpers'].items()};N={int(k):v for k,v in local['paid'].items()}
    sys.path.insert(0,str(ROOT/'research/joint-helper-lattice'))
    J=load(ROOT/'research/joint-helper-lattice/verify.py','round2_pinned_controller')
    sys.path.insert(0,str(ROOT/'research/query-thinned-controllers'))
    C=load(ROOT/'research/query-thinned-controllers/controller.py','round2_controller_engine')
    word=J.controller16(C)
    T,P=Counter(),Counter();full=thin=0
    for e in word['physical_events']:
        if e[0]=='LOCAL':full+=1;T.update(H);P.update(N)
        elif e[0]=='QUERY_SHEAR':thin+=1;P[1]+=112
        elif e[0]=='IDLE':P[8*len(e[2])]+=224
    for term in word['diagonal']:T[1+8*sum(term[1:])]+=112
    need(full==18 and thin==15 and sum(H.values())==408,'Complete retained p16 call and input inventory')
    return H,N,T,P,word

def run(local,kappa=None):
    H,N,T,P,word=assemble(local)
    E=load(ROOT/'research/higher-moment-strictification/verify.py','round2_exact_intervals')
    other=load(ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py','round2_second_intervals')
    def margin(c):
        t,p=E.moment(T,1-c),E.moment(P,1-c)
        return t[0]-p[1],t[1]-p[0]
    old_upper=Q('.0030201659771')
    need(margin(old_upper)[0]>0,'Changed complete invoice strictly beats old raw root upper endpoint')
    # Binary search on a fixed rational grid; all final signs use exact intervals.
    lo,hi=0,1000000000000
    grid=10**14
    while hi-lo>1:
        mid=(lo+hi)//2
        if margin(Q(mid,grid))[0]>0:lo=mid
        else:hi=mid
    root_low,root_high=Q(lo,grid),Q(hi,grid)
    need(margin(root_low)[0]>0 and margin(root_high)[1]<0,'Strict changed-profile rational root enclosure')
    if kappa is None:kappa=Q((root_low*10**8).__floor__()-3,10**8)
    tested=kappa+Q(1,10**11)
    need(Q('.003020165')<kappa<tested<root_low,'New multiplication saving with compiler headroom')
    t,u,v,c,b=1-tested,Q(1,5),1024,20,21
    target,paid=E.moment(T,t),E.moment(P,t)
    tl,th=other.moment(T,tested);pl,ph=other.moment(P,tested)
    need(tl>ph and max(tl,target[0])<=min(th,target[1]) and max(pl,paid[0])<=min(ph,paid[1]),'Two independently implemented rational moment engines agree')
    alpha=E.divide(paid,target)
    gamma=E.divide(E.moment(P,t+u),E.mul(E.power(c,u),target))
    delta=E.divide((Q(sum(T.values())*b),)*2,E.mul(E.power(c,tested),target))
    alpha_gap=Q(1,10**11);g=d=Q(97,100)
    need(alpha[1]<1-alpha_gap and gamma[1]<g and delta[1]<d,'All original and productive-completion tails charged')
    need(g**128<Q(1,16) and d**128<Q(1,16),'Both strict tail decay blocks')
    normalized=1/(1+v*alpha_gap)+Q(4,2**32)
    need(normalized<1 and c**64<b**63,'Paid completion, splitting and rounding fit')
    theta,power=Q(63,64),1000
    eta=E.scale(E.power(145,-v*tested),t)
    need(2*(20**v)**64<=(145**v)**63 and eta[0]>theta**power,'Shifted exits and complement capacity')
    need(E.power(145,v*tested)[1]<2**power,'Compiler initial range')
    gap=(tested-kappa)/7;need(gap.numerator==1,'Explicit finite integer grid')
    step=gap.denominator
    def wins(j):return (step*j+1)**power<2**j
    left,right=1,2
    while not wins(right):left,right=right,2*right
    while right-left>1:
        mid=(left+right)//2
        if wins(mid):right=mid
        else:left=mid
    height=step*right
    need(height>8*v and wins(right) and not wins(right-1),'Strict finite uniform-rank integer bound')
    local_scalar=max(x['real_scalar_allowance'] for x in local['native'].values())
    routes=(sum(N.values())+2*408+688)*1000
    need(local_scalar+routes<10**7,'Complete scalar and fixed monomial routing bound')
    scalar_upper=18*10**7+15*1792+32*112*(len(word['physical_events'])+sum(len(word['boundaries'][k+'_program']) for k in ('left','right')))
    need(scalar_upper<10**9,'Raw controller scalar bound')
    bit=read(ROOT/'research/query-thinned-controllers/RESULT.json')['ordinary_BIT']
    atom=Q(bit['atom']);ordinary=(1-atom)*Q(bit['after_cover'])+atom*Q('.0000384599');admitted=Q(bit['admitted'])
    need(atom==Q('.004') and atom>ordinary>admitted>tested and atom<1-ordinary,'Source ordinary BIT admission and stock')
    L=load(ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py','round2_outer_ledger')
    params={'kappa':kappa,'tested_saving':tested,'complex_uniform_saving':kappa+6*gap,
            'b':kappa+5*gap,'a':kappa+4*gap,'q':kappa+3*gap,'bit_saving':admitted,
            'epsilon':1-gap,'beta':1-3*gap,'r0':gap/10,'stop':gap,'layout':gap,'d':gap}
    outer=L.ledger(params);outer['functional_checks']['actual_new_BIT_stock_sublinear']=params['beta']*(1-atom)
    need(len(outer['strict_checks'])==54 and len(outer['functional_checks'])==4,'Whole outer predicate inventory')
    need(all(x>0 for key in ('strict_checks','functional_checks') for x in outer[key].values()),'All outer inequalities strictly positive')
    controls={}
    for name,patch in [('old_BIT',{'bit_saving':Q('.0027')}),('closed_uniform',{'complex_uniform_saving':params['b']}),('unfunded_endpoint',{'kappa':tested}),('closed_epsilon',{'epsilon':Q(1)})]:
        bad=L.ledger(dict(params,**patch));failed=[k for k,x in bad['strict_checks'].items() if x<=0]
        need(failed,'Reject unsupported outer patch '+name);controls[name]=failed
    return encode({'status':'PASS_CHANGED_PROFILE_ARITHMETIC_NATIVE_ADMISSION_SEPARATE','kappa':kappa,
        'gain_over_PR4535':kappa-Q('.003020165'),'raw_root_interval':[root_low,root_high],
        'margin_at_old_root_upper':margin(old_upper),'local_helpers':H,'local_paid':N,'targets':T,'paid':P,
        'productive_fields':sum(T.values()),'paid_calls':sum(P.values()),'rank_mass_surplus':sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items()),
        'strictification':{'tested':tested,'power':v,'cutoff':c,'floor':b,'tail_offset':u,'alpha':E.display(alpha),'gamma':E.display(gamma),'delta':E.display(delta),'normalized_paid_upper':normalized},
        'compiler':{'theta':theta,'logarithm_power':power,'eta':E.display(eta),'gap':gap,'uniform_saving':params['complex_uniform_saving'],'H':height,'N':'2^'+str(height),'integer_test_exponent':right,'word_materialized':False},
        'nonrecursive':{'local_scalar':local_scalar,'local_routes':routes,'raw_scalar_upper':scalar_upper},
        'ordinary_BIT':bit,'outer':outer,'negative_controls':controls,
        'scope':'Exact changed-profile arithmetic only. Requires separately admitted changed native programs, paid transports and absolute phases. Retained compiler/native/precision/tape/analytic/recovery assumptions.'})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--native',type=Path,required=True);ap.add_argument('--kappa');ap.add_argument('--out',type=Path,default=HERE/'ARITHMETIC.json');args=ap.parse_args()
    result=run(read(args.native),Q(args.kappa) if args.kappa else None)
    result['native_receipt_sha256']=sha256(args.native.read_bytes()).hexdigest()
    # Pin all loaded project source modules and the non-module controller/stock
    # records read by the inherited engines. Standard-library files are outside
    # the repository and are recorded instead by the replay's Python version.
    paths={Path(__file__).resolve(),ROOT/'research/joint-helper-lattice/CONTROLLER.json',
           ROOT/'research/query-thinned-controllers/RESULT.json'}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT) and path.is_file():paths.add(path)
    result['source_sha256']={p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','kappa','gain_over_PR4535','raw_root_interval','paid_calls','compiler')},indent=2))
