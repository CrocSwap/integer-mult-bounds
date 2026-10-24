"""Independent literal audit of frozen changed-G word and phase coverage.

Does not import the producer's evaluator or mutate the candidate. Exact
native K_G phases belong to the separately recorded physical verifier.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/'research/warp-interface-20261022'

def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    return m

def read(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)

def span(b):
    out={0}
    for v in b:out|={x^v for x in tuple(out)}
    assert len(out)==1<<len(b)
    return frozenset(out)

def image(columns,x):
    y=0
    for i,c in enumerate(columns):
        if x>>i&1:y^=c
    return y

def add(dst,src,coefficient):
    for key,value in src.items():
        new=dst.get(key,Q(0))+coefficient*value
        if new:dst[key]=new
        elif key in dst:del dst[key]

def identity(r):return {(r,()):Q(1)}

def replay(c,program,direction,maps):
    rows={('L',i):identity(('L',i)) for i in range(632)}
    rows['C',0]=identity(('C',0))
    current={('L',i):f for i,f in enumerate(c['start'])};current['C',0]=None
    spaces=[span(b) for b in c['frames']]
    paid=Counter();counts=Counter();nontrivial=0;scalar_cost=0
    for index,e in enumerate(program):
        kind=e[0];counts[kind]+=1
        if kind in ('climb','center'):
            if kind=='climb':_,_,r,a,b,rank=e;role=('L',r);assert spaces[a]<spaces[b]
            else:_,r,a,b,rank=e;role=('C',r);assert spaces[a]<spaces[b] or spaces[b]<spaces[a]
            assert current[role]==a and rank==abs(len(c['frames'][b])-len(c['frames'][a]))
            current[role]=b;paid[rank]+=1
        elif kind=='scalar':
            g,f=e[1:];dst=tuple(g[1]);action=g[0]
            if action=='clear':assert dst==('C',0);rows[dst]={};current[dst]=f;scalar_cost+=2;continue
            assert current[dst]==f
            if action in ('add','copy'):
                src=tuple(g[2]);assert current[src]==f
                if action=='copy':assert dst==('C',0);rows[dst]=dict(rows[src]);scalar_cost+=2
                else:
                    coefficient=Q(g[3],g[4]);assert dst!=src and coefficient and coefficient.denominator&(coefficient.denominator-1)==0
                    numerator,denominator=abs(coefficient.numerator),coefficient.denominator
                    scalar_cost+=2*(3+numerator.bit_length()-1+numerator.bit_count()+denominator.bit_length()-1)
                    add(rows[dst],rows[src],coefficient)
            else:
                assert action=='scale';coefficient=Q(g[2],g[3])
                assert coefficient and abs(coefficient.numerator)&(abs(coefficient.numerator)-1)==0 and coefficient.denominator&(coefficient.denominator-1)==0
                scalar_cost+=2*(abs(abs(coefficient.numerator).bit_length()-coefficient.denominator.bit_length())+int(coefficient<0))
                rows[dst]={k:coefficient*v for k,v in rows[dst].items()}
        elif kind=='warp':
            _,r,op,a,b=e;role=tuple(r);assert current[role]==a
            assert frozenset(maps[op][x] for x in spaces[a])==spaces[b]
            symbol=op+(1000000 if op>0 else -1000000) if direction=='backward' else op
            transformed={}
            for (variable,word),coefficient in rows[role].items():
                newword=word[1:] if word and word[0]==-symbol else (symbol,)+word
                key=variable,newword;transformed[key]=transformed.get(key,Q(0))+coefficient
            rows[role]={k:v for k,v in transformed.items() if v};current[role]=b
            nontrivial+=int(0<len(c['frames'][a])<9)
        else:assert kind in ('phase','adapter','residual_adapter')
    assert [current['L',i] for i in range(632)]==c['final'] and not rows['C',0]
    for i in range(632):
        wanted=identity(('L',i))
        if direction=='forward' and 112<=i<224:add(wanted,identity(('L',i-112)),Q(1))
        if direction=='backward' and i<112:add(wanted,identity(('L',i+112)),Q(-1))
        assert rows['L',i]==wanted,('bad endpoint',direction,i)
    return {'direction':direction,'all_632_independent_data_helper_columns':True,'owned_C_entry_arbitrary_and_cleared':True,'paid':dict(sorted(paid.items())),'nontrivial_warp_occurrences':nontrivial,'event_counts':dict(counts),'real_scalar_allowance':scalar_cost}

def price_audit(H,N,oldN,native_checks):
    A=read(ROOT/'research/kappa-interface-round2-20261022/ARITHMETIC.json')
    word=read(ROOT/'research/joint-helper-lattice/CONTROLLER.json')
    T,P=Counter(),Counter();full=thin=0
    for event in word['physical_events']:
        if event[0]=='LOCAL':T.update(H);P.update(N);full+=1
        elif event[0]=='QUERY_SHEAR':P[1]+=112;thin+=1
        elif event[0]=='IDLE':P[8*len(event[2])]+=224
    for term in word['diagonal']:T[1+8*sum(term[1:])]+=112
    assert (full,thin)==(18,15)
    assert dict(T)=={int(k):v for k,v in A['targets'].items()}
    assert dict(P)=={int(k):v for k,v in A['paid'].items()}
    delta={r:oldN[r]-N[r] for r in oldN.keys()|N.keys() if oldN[r]!=N[r]}
    assert delta=={1:36,2:-24,3:-12,4:12}
    assert sum(r*n for r,n in delta.items())==0 and sum(delta.values())==12
    E=load(ROOT/'research/higher-moment-strictification/verify.py','independent_price_power_bounds')
    O=load(ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py','independent_price_second_bounds')
    low,high=map(Q,A['raw_root_interval']);tested=Q(A['strictification']['tested']);kappa=Q(A['kappa'])
    signs={}
    for name,saving in [('raw_lower',low),('raw_upper',high),('old_raw_upper',Q('.0030201659771')),('tested',tested)]:
        et,ep=E.moment(T,1-saving),E.moment(P,1-saving)
        ot,op=O.moment(T,saving),O.moment(P,saving)
        assert max(et[0],ot[0])<=min(et[1],ot[1]) and max(ep[0],op[0])<=min(ep[1],op[1])
        em=(et[0]-ep[1],et[1]-ep[0]);om=(ot[0]-op[1],ot[1]-op[0])
        assert (em[1]<0 and om[1]<0) if name=='raw_upper' else (em[0]>0 and om[0]>0)
        signs[name]={'saving':str(saving),'both_engines_same_strict_sign':-1 if name=='raw_upper' else 1}
    assert kappa==Q('.00302152') and kappa<tested<low<high
    assert Q(A['gain_over_PR4535'])==kappa-Q('.003020165')==Q(271,200000000)
    t,u,v=1-tested,Q(1,5),1024
    tm,pm=E.moment(T,t),E.moment(P,t)
    alpha=E.divide(pm,tm)
    gamma=E.divide(E.moment(P,t+u),E.mul(E.power(20,u),tm))
    completion=E.divide((Q(sum(T.values())*21),)*2,E.mul(E.power(20,tested),tm))
    assert alpha[1]<1-Q(1,10**9) and gamma[1]<Q(97,100) and completion[1]<Q(97,100)
    assert Q(97,100)**128<Q(1,16)
    assert 1/(1+Q(v,10**9))+Q(4,2**32)<1 and 20**64<21**63
    eta=E.scale(E.power(145,-v*tested),t)
    assert 2*(20**v)**64<=(145**v)**63 and eta[0]>Q(63,64)**1000
    assert E.power(145,v*tested)[1]<2**1000
    gap=(tested-kappa)/7;assert gap==Q(1,700000000)
    step=gap.denominator;j=A['compiler']['integer_test_exponent'];height=A['compiler']['H']
    assert height==step*j and height>8*v
    assert (step*j+1)**1000<2**j and (step*(j-1)+1)**1000>=2**(j-1)
    assert Q(A['compiler']['uniform_saving'])==kappa+6*gap and A['compiler']['word_materialized'] is False
    route_classes={x['event_counts']['warp']+x['event_counts']['adapter'] for x in native_checks}
    assert route_classes=={688}
    routes=(sum(N.values())+2*408+688)*1000
    local_scalar=max(x['real_scalar_allowance'] for x in native_checks)
    assert routes==4802000 and local_scalar==158168 and routes+local_scalar<10**7
    scalar_upper=18*10**7+15*1792+32*112*(len(word['physical_events'])+sum(len(word['boundaries'][k+'_program']) for k in ('left','right')))
    assert scalar_upper==A['nonrecursive']['raw_scalar_upper']<10**9
    assert sum(P.values())==64404 and sum(T.values())==10928
    assert sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items())==752
    return {'local_old_minus_new':delta,'global_moment_gain':'216*(3+4^t-2*2^t-3^t)>0 for every 0<t<1',
            'uniform_gain_proof':'g(1)=0; gprime/3^t=2log2*((4/3)^t-(2/3)^t)-log3 is increasing and at 1=(4/3)log2-log3<0 because 16<27. Thus g decreases to 0.',
            'raw_root_two_engine_signs':signs,'all_tail_and_integer_compiler_inequalities_rechecked':True,'route_classes':{'warp':240,'main_endpoint_adapter':448,'total':688},
            'local_route_allowance':routes,'local_scalar_allowance':local_scalar,'raw_scalar_upper':scalar_upper,
            'general_G_cost_scope':'A changed nine-axis K_G remains a fixed monomial recipe of the same bounded dimension and Z4 coefficient class. The inherited1000-per-category route cap is retained; no measured fixed-tape cost or new asymptotic movement theorem is claimed.'}

def run():
    start=time.perf_counter()
    actual=SOURCE/'ACTUAL-WORD.json.gz';freeze=read(SOURCE/'ACTUAL-WORD-FREEZE.json')
    raw=actual.read_bytes();assert sha256(raw).hexdigest()==freeze['compressed_sha256']
    assert sha256(gzip.decompress(raw)).hexdigest()==freeze['canonical_payload_sha256']
    data=read(actual);c,programs=data['canonical'],data['programs']
    for name,want in freeze['discovery_sha256'].items():assert sha256((SOURCE/name).read_bytes()).hexdigest()==want
    source=read(SOURCE/'CANDIDATE-WORD.json.gz');assert source['programs']==programs
    jp=ROOT/'research/joint-helper-lattice/native_joint.py';sys.path.insert(0,str(jp.parent))
    J=load(jp,'independent_baseline_construct');base,old,*_=J.construct()
    assert c['frames'][:len(base['frames'])]==base['frames']
    assert c['start']==base['start'] and c['final']==base['final'] and c['ports']==base['ports']
    assert not any(k in c for k in ('A','B','cleanup','compensation','edges'))
    def paid_edges(p):return {(e[3],e[4]) for e in p if e[0]=='climb'}
    def warp_edges(p):return {(e[2],e[3],e[4]) for e in p if e[0]=='warp'}
    assert paid_edges(programs['forward'])==paid_edges(programs['backward'])
    assert warp_edges(programs['forward'])==warp_edges(programs['backward'])
    assert c['warp_edges']==[list(x) for x in sorted({(1 if op>0 else -1,abs(op),a,b) for op,a,b in warp_edges(programs['forward'])})]
    oldG={w['op']:w['G_columns'] for w in base['warps']};newG={w['op']:w['G_columns'] for w in c['warps']}
    assert set(newG)==set(oldG)==set(range(1,73))
    maps={}
    for op,columns in newG.items():
        assert len(columns)==9 and all(isinstance(x,int) and 0<x<512 for x in columns)
        images=[image(columns,x) for x in range(512)];assert len(set(images))==512
        inverse=[0]*512
        for x,y in enumerate(images):inverse[y]=x
        maps[op],maps[-op]=images,inverse
    checks=[];changed_scalar=0
    for d,p in programs.items():
        assert [e[1] for e in p if e[0]=='scalar']==[e[1] for e in old[d] if e[0]=='scalar']
        assert [(e[1],e[2]) for e in p if e[0]=='warp']==[(e[1],e[2]) for e in old[d] if e[0]=='warp']
        assert [e for e in p if e[0] in ('phase','center','adapter','residual_adapter')]==[e for e in old[d] if e[0] in ('phase','center','adapter','residual_adapter')]
        changed_scalar=sum(e[2]!=f[2] for e,f in zip([e for e in p if e[0]=='scalar'],[e for e in old[d] if e[0]=='scalar']))
        checks.append(replay(c,p,d,maps))
    expected={1:2201,2:412,3:506,4:135,5:36,8:8}
    assert all(x['paid']==expected for x in checks)
    H=Counter(len(c['frames'][c['final'][i]])-len(c['frames'][c['start'][i]]) for i in range(224,632))
    assert H=={4:28,7:7,8:47,9:326}
    oldN=Counter(e[5] for e in old['forward'] if e[0]=='climb');oldN.update(e[4] for e in old['forward'] if e[0]=='center')
    arithmetic=price_audit(H,Counter(expected),oldN,checks)
    result={'status':'PASS_INDEPENDENT_CHANGED_G_SEMANTIC_AND_COVERAGE_AUDIT','actual_payload_sha256':freeze['canonical_payload_sha256'],'native':checks,'unchanged_helpers':dict(H),
            'baseline_frame_prefix_unchanged':True,'forward_backward_phase_class_coverage_identical':True,'all_logical_symbols_opcodes_coefficients_order_and_inert_markers_unchanged':True,
            'changed_scalar_contacts_per_direction':changed_scalar,'changed_G_operators':[op for op in newG if newG[op]!=oldG[op]],
            'arithmetic_and_route_audit':arithmetic,
            'physical_admission_scope':'Invertible G and all exact binary transported-frame incidences checked here. New K_G absolute phases and fixed-cost monomial lowerings are certified by the separate physical admission receipt, not inferred from this formal replay.',
            'claim':'The unchanged arbitrary-input free-group identity applies to any consistent invertible interpretation of the independently numbered warp symbols. It does not require original G values or relations between different operators.',
            'source_sha256':{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),actual,SOURCE/'ACTUAL-WORD-FREEZE.json',jp,ROOT/'research/joint-helper-lattice/CONTROLLER.json',ROOT/'research/higher-moment-strictification/verify.py',ROOT/'research/kappa-rebuild/architecture/mixed_target_probe.py',ROOT/'research/kappa-interface-round2-20261022/price_profile.py',ROOT/'research/kappa-interface-round2-20261022/ARITHMETIC.json')},'elapsed_seconds':time.perf_counter()-start}
    (HERE/'audit-result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
