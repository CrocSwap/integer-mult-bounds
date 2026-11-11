"""Full changed-native operator, grid, price, envelope and physical checks.

Retains authenticated predecessor engines and all source notices. Source-aware
verification is distinct from independent human/formal acceptance.
Rohan Arun with OpenAI Codex assistance. Apache-2.0.
Adapted to the exact causal-history two-buffer split by dillona/OpenAI Codex.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import sys,json,gzip,argparse,subprocess,tempfile,io,contextlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source import HERE,read,load,sources,canonical,need
from construct import construct
from derive_grid import derive
def normalized(x):return json.loads(json.dumps(x,default=str))
def delta(a,b):
    d=Counter(a);d.subtract(b);return {r:v for r,v in d.items() if v}
def rejects(fn):
    try:fn()
    except (AssertionError,ValueError):return True
    raise ValueError('Corruption control accepted')
def chart_check(vendor,source,word):
    C=load('step_chart_compiler',vendor/'frozen/clifford_exact.py')
    V=load('step_chart_interpreter',vendor/'frozen/native_verify.py')
    def pairs(w):
        main=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
        return {(e[2],e[3])for e in w['program']if e[0]=='MOVE'}|{(w['initial'][r],w['final'][r])for r in range(w['public'])if r not in main}
    changed=pairs(word)-pairs(source)
    hit=read(HERE/'WITNESS.json');f=hit['frame'];u=source['initial'][hit['pivot']];v=source['final'][hit['pivot']];a=hit['path']['old'];b=hit['path']['new']
    needed=changed|{(u,f),(f,v),(a,f),(f,b),(a,b),(u,v)}
    out=[]
    for a,b in sorted(needed):
        ca,cb=[C.canonical_frame(9,tuple(word['frames'][f]))for f in(a,b)]
        recipe,_=C.lower_child(ca.adjoint().then(cb))
        expected=V.adjoint(V.frame(word['frames'][a],9))+V.frame(word['frames'][b],9)
        actual=V.recipe(recipe);V.equal(actual,expected,'Signed Pauli action and absolute phase')
        need(recipe['rank']==abs(len(word['frames'][a])-len(word['frames'][b])),'Exact chart rank')
        for column in range(512):need(V.state(actual,column)==V.state(expected,column),'All Gaussian columns')
        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4
        need(rejects(lambda:V.equal(V.recipe(bad),expected,'wrong phase')),'Wrong phase rejected')
        out.append({'pair':[a,b],'rank':recipe['rank'],'columns':512})
    return {'new_pairs':sorted(changed),'rechecked_pairs':out,'wrong_phase_rejected':True}

def forward_endpoint(word,rows):
    n=word['public'];unit=1125*2**25
    target=[{r:Q(1)}if r<n else{}for r in range(n+word['owned_fields'])]
    H=word['hosted'];D=set(H['Dports'])
    for i,x in enumerate(word['live']):
        y=x+112
        if i in D:target[y][x]=Q(1)
        else:target[x][y]=Q(-1);target[y]={x:Q(1,2),y:Q(1,2)}
    for x,y in zip(H['X2'],H['Y2']):target[x][y]=Q(-1)
    need(all(row=={k:v*unit for k,v in want.items()}for row,want in zip(rows,target)),'Every forward input/output coefficient and cleared owned row')
    return {'rows':len(rows),'coefficient_positions':len(rows)**2,'grid':1125,'fractional_bits':25}


def run():
    need(__debug__,'Assertions are proof obligations')
    with sources() as (vendor,archive,rank9,bundle,parent,old):
        hit=read(HERE/'WITNESS.json');paths=read(HERE/'PATHS.json');new=construct(old,hit,paths)
        need(canonical(new)==gzip.decompress((HERE/'WORD.json.gz').read_bytes()),'Whole emitted word')
        G=load('rechart_price_engine',bundle/'gate.py');sys.path.insert(0,str(rank9))
        helper_count=sum(read(parent/'NATIVE-RESULT.json')['native']['helpers'].values())+1
        base=G.module('rechart_rank9',rank9/'candidate_gate.py',(
            ('== 1080','== '+str(helper_count)),
            ('fresh_arbitrary_helpers=18 * 1080','fresh_arbitrary_helpers=18 * '+str(helper_count)),
            ('grid.word_run(word), grid.caller_run(caller)','grid.word_run(word, frac=25), grid.caller_run(caller)'),
            ("    exec(compile(src, str(env_path), 'exec'), env.__dict__)",'    assert src.count("(life, peak, owned_count) == (54, 43, 51)") == 1\n    src=src.replace("(life, peak, owned_count) == (54, 43, 51)","(life, peak, owned_count) == (64, 47, 61)")\n    exec(compile(src, str(env_path), \'exec\'), env.__dict__)')))
        I=base.independent(vendor);oldN,N=map(I.native,(old,new));previous=read(parent/'NATIVE-RESULT.json')
        need(normalized(oldN)==previous['native'] and not N['bad_inputs'],'Source inventory and entire changed adjoint')
        need(N['lifetimes']==oldN['lifetimes']+2==64 and N['owned_peak']==47 and N['rises']==oldN['rises'],'Two explicit added owned lifetimes, exact peak and unchanged ascent')
        need(new['owned_fields']==old['owned_fields']+2==61,'Two explicit added owned labels')
        need(delta(N['helpers'],oldN['helpers'])=={4:1,5:1,9:-1} and delta(N['paid'],oldN['paid'])=={3:1,5:1,8:-1},'Exact helper split and paid midpoint delta')
        need(len(new['program'])==len(old['program'])+40 and new['public']==old['public']+1==1498,'Complete emitted instruction and public inventory delta')
        derived,_=derive(new);need(derived['odd_scale']==1125 and derived['fractional_bits']==25,'Fresh minimal common grid')
        audit=G.module('rechart_forward',archive/'audit_native.py',(('2**24','2**25'),('25 - (abs(value) & -abs(value)).bit_length()','26 - (abs(value) & -abs(value)).bit_length()')));forward,grid=audit.replay(new,list(enumerate(new['program'])),set())
        forward_receipt=forward_endpoint(new,forward[0])
        need(grid['odd_grid_lcm']==1125 and grid['owned_rise_mass']==56,'Fresh native grid and owned ascent')
        need(grid['dyadic_height']==derived['fractional_bits'] and grid['maximum_scaled_mass']==derived['scaled_maximum_mass'],'Independent rational/integer grid agreement')
        print('PASS whole source/operator, forward/adjoint, causal charts and fresh native grid',flush=True)
        caller_path=rank9/'dyadic/CALLER.json';C=read(caller_path)
        need(sha256(caller_path.read_bytes()).hexdigest()==G.CALLER,'Exact 18-stage ingredient caller')
        symbolic=I.caller(C);need(not symbolic['bad_outputs'] and normalized(symbolic)==previous['caller'],'Full ingredient caller')
        before=I.invoices(old,C,oldN);invoice=I.invoices(new,C,N)
        need(normalized(before)==previous['invoice'],'Reconstructed source ingredient invoice')
        unadjusted=I.ordinary(old,C,oldN);ordinary=I.ordinary(new,C,N)
        routes=previous['ordinary']['caller_items']['B']['fused_routes'];route_delta=routes-unadjusted['caller_items']['B']['fused_routes']
        surcharge=0
        for e in C['events']:
            if e[0]=='B' and e[1] in ('ADD','SCALE'):
                q=Q(e[4] if e[1]=='ADD' else e[3]);a,d=abs(q.numerator),q.denominator
                surcharge+=4*(a.bit_length()+d.bit_length()+1+(a.bit_count() if e[1]=='ADD' else 0))
        surcharge*=len(C['types']['B']['ports'])
        need(surcharge==previous['ordinary']['extra_B_scalar_surcharge'],'Fresh B surcharge')
        need(unadjusted['conservative_total']+route_delta+surcharge==previous['ordinary']['conservative_total'],'Whole source ordinary bill')
        ordinary['caller_items']['B']['fused_routes']=routes
        for k in ('caller_total','raw_upper','conservative_total'):ordinary[k]+=route_delta
        ordinary['extra_B_scalar_surcharge']=surcharge;ordinary['conservative_total']+=surcharge
        ordinary['margin_to_billion']=10**9-ordinary['conservative_total'];need(ordinary['margin_to_billion']>0,'Ordinary allowance')
        gate,price=G.exact_price(vendor,archive,before,invoice,previous)
        manifest=read(vendor/'INDEPENDENT-SOURCES.json');P=load('rechart_bit_binding',archive/'verify.py');P.bit_binding(I,manifest)
        precision=base.precision(vendor,new,C,gate,manifest)
        need(precision['word']['odd_scale_lcm']==1125 and precision['word']['dyadic_height']==25,'Fresh ingredient precision')
        print('PASS full ingredient invoice, ordinary, precision, both prices and outer gates',flush=True)
        charts=chart_check(vendor,old,new)
        from certificate import controls as temporal_controls, observe, check
        snapshots=observe(old,hit);timed_certificate=check(hit,snapshots)
        controls=temporal_controls(old,hit,paths,snapshots)
        scalar=next(i for i,e in enumerate(new['program'])if e[0]=='ADD')
        controls['wrong_boundary_scalar_coefficient']=bool(I.native(new,mutant=scalar)['bad_inputs'])
        bad=deepcopy(new);i=next(i for i,e in enumerate(bad['program'])if e[0]=='MOVE');bad['program'][i][2]=-1
        controls['wrong_move_source']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);bad['final'][hit['pivot']]=old['final'][hit['pivot']]
        controls['omitted_retiring_output_frame']=rejects(lambda:I.native(bad))
        A=new['public']+old['owned_fields']
        bad=deepcopy(new);bad['program']=[e for e in bad['program']if not(e[0]=='INIT'and e[1]==A)]
        controls['omitted_accumulator_init']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);i=next(i for i,e in enumerate(bad['program'])if e[0]=='CLEAR'and e[1]==A);bad['program'][i][1]=hit['pivot']
        controls['public_erasure_rejected']=rejects(lambda:I.native(bad))
        owned_check=G.module('temporal_owned_census',vendor/'retained/query-only-precision-envelope/envelopes.py',(('(life, peak, owned_count) == (54, 43, 51)','(life, peak, owned_count) == (64, 47, 61)'),))
        need(owned_check.validate_word(new)['lifetimes']==64,'Fresh exact owned census in envelope validator')
        bad=deepcopy(new);bad['program']=[['INIT',A,hit['frame']],['CLEAR',A,hit['frame']]]+bad['program']
        controls['extra_uncharged_owned_lifetime']=rejects(lambda:owned_check.validate_word(bad))
        grid_engine=G.module('rechart_grid_controls',vendor/'retained/odd-native-common-grid/independent_bounds.py')
        controls['insufficient_odd_grid']=rejects(lambda:grid_engine.word_run(new,375,25))
        controls['insufficient_fractional_grid']=rejects(lambda:grid_engine.word_run(new,1125,24))
        need(all(controls.values()),'All native corruption controls')
        physical_checks=[]
        with tempfile.TemporaryDirectory(prefix='rechart-physical-') as tmp:
            path=Path(tmp)/'word.json.gz';path.write_bytes(gzip.compress(canonical(new),mtime=0))
            for command,args in [(vendor/'frozen/verify_host3_odd.py',[path,'1125']),(vendor/'frozen/physical.py',[path,vendor/'frozen/clifford_exact.py','1000000009','11'])]:
                subprocess.run([sys.executable,'-I','-B',str(command),*map(str,args)],check=True);physical_checks.append(command.name)
            digest=sha256(canonical(new)).hexdigest()
            engine=G.module('rechart_signed_routes',rank9/'physical_child.py',(('cca66a7ec924bab47ccd1410968d16e071a01dc6110b5c08040bd207f753d066',digest),))
            capture=io.StringIO()
            with contextlib.redirect_stdout(capture):engine.main(path,vendor/'data/caller.json',caller_path)
            signed_routes=json.loads(capture.getvalue())
            need(signed_routes['status']=='PASS_PHYSICAL_RANK9_ALGEBRA' and signed_routes['paid_calls']==32,'Signed physical fields')
            need(1000*sum(len(row['caller_fields'])*row['ordinary_elementary_units'] for row in signed_routes['bindings'])==routes,'Actual signed-route charge')
        print('PASS affected Gaussian chart columns, phase, corruption controls and finite physical replay',flush=True)
        return normalized(dict(status='PASS_TEMPORAL_CHART306_NATIVE',source_head=read(HERE/'INPUTS.json')['source_head'],word_canonical_sha256=digest,native=N,forward=forward_receipt,grid=grid,derived_grid=derived,caller=symbolic,invoice=invoice,ordinary=ordinary,gate=gate,price=price,precision=precision,charts=charts,timed_certificate=timed_certificate,controls=controls,physical_checks=physical_checks,signed_routes=signed_routes,limitations=['Five inherited framework assumptions remain.','Source-aware retained engines are not independent human/formal acceptance.','The complete 17-stage application is checked separately.']))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();r=run()
    if a.out:
        with a.out.open('x') as f:json.dump(r,f,sort_keys=True,indent=2);f.write('\n')
    else:need(r==read(HERE/'NATIVE-RESULT.json'),'Every frozen native receipt field')
    print(r['status'],r['gate']['claim'],flush=True)
