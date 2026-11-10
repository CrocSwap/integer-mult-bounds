"""Full changed-native operator, grid, price, envelope and physical checks.

Retains authenticated predecessor engines and all source notices. Source-aware
verification is distinct from independent human/formal acceptance.
Rohan Arun with OpenAI Codex assistance. Apache-2.0.
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
def run():
    need(__debug__,'Assertions are proof obligations')
    with sources() as (vendor,archive,rank9,bundle,parent,old):
        changes=read(HERE/'CHANGES.json');new=construct(old,changes)
        need(canonical(new)==gzip.decompress((HERE/'WORD.json.gz').read_bytes()),'Whole emitted word')
        G=load('rechart_price_engine',bundle/'gate.py');sys.path.insert(0,str(rank9))
        helper_count=sum(read(parent/'NATIVE-RESULT.json')['native']['helpers'].values())
        base=G.module('rechart_rank9',rank9/'candidate_gate.py',(
            ('== 1080','== '+str(helper_count)),
            ('fresh_arbitrary_helpers=18 * 1080','fresh_arbitrary_helpers=18 * '+str(helper_count))))
        I=base.independent(vendor);oldN,N=map(I.native,(old,new));previous=read(parent/'NATIVE-RESULT.json')
        need(normalized(oldN)==previous['native'] and not N['bad_inputs'],'Source inventory and entire changed adjoint')
        need(all(N[k]==oldN[k] for k in ('lifetimes','owned_peak','rises')),'Owned inventory unchanged')
        early=read(HERE/'EARLY-RESULT.json')
        need(normalized(dict(T=delta(N['helpers'],oldN['helpers']),P=delta(N['paid'],oldN['paid'])))==early['native_delta'],'Exact target and paid deltas')
        # Recharting changes no scalar operation or normalized chronological map.
        strip=lambda w:[[e[0],*e[1:-1]] for e in w['program'] if e[0] in ('ADD','COPY','SCALE')]
        need(strip(old)==strip(new),'Every scalar coefficient, operand and chronological order unchanged')
        derived,_=derive(new);need(derived['odd_scale']==1125 and derived['fractional_bits']==24,'Fresh minimal common grid')
        audit=load('rechart_forward',archive/'audit_native.py');forward,grid=audit.replay(new,list(enumerate(new['program'])),set())
        saved_modules={k:sys.modules.get(k) for k in ('source','construct','support','split')};saved_path=list(sys.path)
        try:
            for k in saved_modules:sys.modules.pop(k,None)
            sys.path.insert(0,str(parent))
            parent_checks=load('rechart_parent_checks',parent/'verify_native.py')
        finally:
            sys.path[:]=saved_path
            for k,v in saved_modules.items():
                if v is None:sys.modules.pop(k,None)
                else:sys.modules[k]=v
        forward_receipt=parent_checks.forward_endpoint(new,forward[0])
        need(grid['odd_grid_lcm']==1125 and grid['owned_rise_mass']==56,'Fresh native grid and owned ascent')
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
        need(precision['word']['odd_scale_lcm']==1125 and precision['word']['dyadic_height']==24,'Fresh ingredient precision')
        print('PASS full ingredient invoice, ordinary, precision, both prices and outer gates',flush=True)
        charts=parent_checks.chart_check(vendor,old,new)
        controls={}
        bad=deepcopy(changes);bad['initial'][0][1]=-1
        controls['wrong_source_input']=rejects(lambda:construct(old,bad))
        bad=deepcopy(changes);bad['scalar'][0][1]=-1
        controls['wrong_source_scalar']=rejects(lambda:construct(old,bad))
        bad=deepcopy(changes);bad['scalar'].append(bad['scalar'][0])
        controls['duplicate_scalar_edit']=rejects(lambda:construct(old,bad))
        scalar=next(i for i,e in enumerate(new['program']) if e[0]=='ADD')
        controls['wrong_scalar_coefficient']=bool(I.native(new,mutant=scalar)['bad_inputs'])
        bad=deepcopy(new);i=next(i for i,e in enumerate(bad['program']) if e[0]=='MOVE');bad['program'][i][2]=-1
        controls['wrong_move_source']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);r=changes['initial'][0][0];bad['initial'][r]=old['initial'][r]
        controls['omitted_input_rechart']=rejects(lambda:I.native(bad))
        grid_engine=G.module('rechart_grid_controls',vendor/'retained/odd-native-common-grid/independent_bounds.py')
        controls['insufficient_odd_grid']=rejects(lambda:grid_engine.word_run(new,375,24))
        controls['insufficient_fractional_grid']=rejects(lambda:grid_engine.word_run(new,1125,23))
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
        return normalized(dict(status='PASS_GLOBAL_INPUT_RECHART_NATIVE',source_head=read(HERE/'INPUTS.json')['source_head'],word_canonical_sha256=digest,native=N,forward=forward_receipt,grid=grid,derived_grid=derived,caller=symbolic,invoice=invoice,ordinary=ordinary,gate=gate,price=price,precision=precision,charts=charts,controls=controls,physical_checks=physical_checks,signed_routes=signed_routes,limitations=['Five inherited framework assumptions remain.','Source-aware retained engines are not independent human/formal acceptance.','The complete 17-stage application is checked separately.']))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();r=run()
    if a.out:
        with a.out.open('x') as f:json.dump(r,f,sort_keys=True,indent=2);f.write('\n')
    else:need(r==read(HERE/'NATIVE-RESULT.json'),'Every frozen native receipt field')
    print(r['status'],r['gate']['claim'],flush=True)
