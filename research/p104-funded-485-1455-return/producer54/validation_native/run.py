# SPDX-License-Identifier: Apache-2.0
"""Full authenticated native validation for the changed 485/1455 producer.

Based on retained #7480 verify_native.py, attributed there to Rohan Arun,
dillona, and OpenAI Codex assistance. Source closure is authenticated through
its unmodified source.py. Every engine adaptation is counted and logged.
All inventories, prices, grids, envelopes, and physical checks are freshly
computed for the literal candidate. This does not select a public frontier.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from types import ModuleType
import sys,json,gzip,subprocess,tempfile,io,contextlib,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'inputs/pr7480'
CANDIDATE=ROOT/'producer54/reroute'
sys.path.insert(0,str(SOURCE))
from source import read,load,sources,canonical,need
from construct import construct
from derive_grid import derive
from verify_native import normalized,delta,rejects,forward_endpoint

EXPECTED='64fca675b91298868e12f09423b47e0c2327cba7095e35c8919c1953b4ed68b8'
BASELINE='5044adee019f073f286789ccb688ffca76d42b60518242bb4daea818d33d337a'
PATCHES=[]
TIMINGS=[]
def module(name,path,edits=()):
    raw=path.read_text();record={'module':name,'source_name':path.name,'source_sha256':sha256(raw.encode()).hexdigest(),'edits':[]}
    for before,after in edits:
        count=raw.count(before);need(count==1,'Unique adaptation '+repr(before))
        raw=raw.replace(before,after)
        record['edits'].append({'before':before,'after':after,'occurrences':count})
    record['adapted_sha256']=sha256(raw.encode()).hexdigest();PATCHES.append(record)
    obj=ModuleType(name);obj.__file__=str(path);sys.modules[name]=obj
    exec(compile(raw,str(path),'exec'),obj.__dict__)
    return obj

def checkpoint(stage,data=None):
    now=time.time();TIMINGS.append({'stage':stage,'elapsed_seconds':now-STARTED})
    (HERE/'CHECKPOINT.json').write_text(json.dumps(normalized({'stage':stage,'word_canonical_sha256':EXPECTED,'data':data,'timings':TIMINGS}),indent=2)+'\n')
    print('PASS',stage,flush=True)

def charts(vendor,word):
    compiler=load('producer_chart_compiler',vendor/'frozen/clifford_exact.py')
    interpreter=load('producer_chart_interpreter',vendor/'frozen/native_verify.py')
    # Recheck every old/new pair in the two changed public itineraries, even
    # when the same ordered pair already occurred elsewhere in the source.
    affected={(3,721),(721,724),(721,904),(3,724),(724,904)}
    report=[]
    for a,b in sorted(affected):
        ca,cb=(compiler.canonical_frame(9,tuple(word['frames'][f]))for f in(a,b))
        recipe,_=compiler.lower_child(ca.adjoint().then(cb))
        expected=interpreter.adjoint(interpreter.frame(word['frames'][a],9))+interpreter.frame(word['frames'][b],9)
        actual=interpreter.recipe(recipe)
        interpreter.equal(actual,expected,'Signed Pauli action and absolute phase')
        need(recipe['rank']==len(word['frames'][b])-len(word['frames'][a]),'Exact public ascent rank')
        for column in range(512):need(interpreter.state(actual,column)==interpreter.state(expected,column),'Exact full Gaussian column')
        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4
        need(rejects(lambda:interpreter.equal(interpreter.recipe(bad),expected,'Wrong absolute phase')),'Reject wrong phase')
        report.append({'pair':[a,b],'rank':recipe['rank'],'columns':512,'absolute_phase_verified':True})
    return {'all_affected_pairs':report,'wrong_phase_rejected':True}

def run():
    need(__debug__,'Assertions are proof obligations')
    new=read(CANDIDATE/'WORD.json.gz');need(sha256(canonical(new)).hexdigest()==EXPECTED,'Only final short candidate')
    previous=read(SOURCE/'NATIVE-RESULT.json')
    proposal=read(CANDIDATE/'RESULT.json')
    with sources()as(vendor,archive,rank9,bundle,parent,parent_word):
        old=construct(parent_word)
        need(canonical(old)==gzip.decompress((SOURCE/'WORD.json.gz').read_bytes()),'Regenerate frozen #7480 from authenticated #7334 closure')
        need(sha256(canonical(old)).hexdigest()==BASELINE,'Exact source word')
        emitted=[];skip=set(proposal['removed_old_indices'])
        for i,e in enumerate(old['program']):
            if i==proposal['insert_before_old_index']:emitted.extend(proposal['splice'])
            if i not in skip:emitted.append(e)
        need(new==dict(old,program=emitted),'Literal complete emitted splice and unchanged boundary')
        G=load('producer_native_price_engine',bundle/'gate.py');sys.path.insert(0,str(rank9))
        helper_count=sum(previous['native']['helpers'].values())
        base=module('producer_rank9',rank9/'candidate_gate.py',(
            ('== 1080','== '+str(helper_count)),
            ('fresh_arbitrary_helpers=18 * 1080','fresh_arbitrary_helpers=18 * '+str(helper_count)),
            ('grid.word_run(word), grid.caller_run(caller)','grid.word_run(word, frac=25), grid.caller_run(caller)'),
            ("    exec(compile(src, str(env_path), 'exec'), env.__dict__)",'    assert src.count("(life, peak, owned_count) == (54, 43, 51)") == 1\n    src=src.replace("(life, peak, owned_count) == (54, 43, 51)","(life, peak, owned_count) == (74, 50, 68)")\n    exec(compile(src, str(env_path), \'exec\'), env.__dict__)')))
        I=base.independent(vendor)
        oldN,N=map(I.native,(old,new))
        need(normalized(oldN)==previous['native'] and not N['bad_inputs'],'Recomputed source inventory and every candidate adjoint input')
        need(all(N[k]==oldN[k]for k in('lifetimes','owned_peak','rises')),'Unchanged complete owned contract')
        need(new['owned_fields']==old['owned_fields']==68,'Unchanged 68 owned labels')
        need(delta(N['helpers'],oldN['helpers'])=={} and delta(N['paid'],oldN['paid'])=={1:1,3:-1,4:-1,6:1},'Exact paid delta and all helper targets')
        need(N['lifetimes']==74 and N['owned_peak']==50 and len(new['program'])==len(old['program'])+3,'Actual instruction and lifetime counts')
        checkpoint('authenticated source, complete frame and adjoint checks',{'native':N})
        derived,_=derive(new)
        need(derived['odd_scale']==1125 and derived['fractional_bits']==25,'Fresh minimal common grid')
        audit=module('producer_forward',archive/'audit_native.py',(('2**24','2**25'),('25 - (abs(value) & -abs(value)).bit_length()','26 - (abs(value) & -abs(value)).bit_length()')))
        forward,grid=audit.replay(new,list(enumerate(new['program'])),set())
        forward_receipt=forward_endpoint(new,forward[0])
        forward_receipt['copy_guards_checked']=len(forward[3])
        forward_receipt['owned_clear_rows_checked']=len(forward[2])
        need(grid['odd_grid_lcm']==1125 and grid['owned_rise_mass']==56,'Fresh exact grid and owned ascent')
        need(grid['dyadic_height']==derived['fractional_bits'] and grid['maximum_scaled_mass']==derived['scaled_maximum_mass'],'Independent integer and rational grid agreement')
        checkpoint('complete forward grid, COPY guards and all public/owned endpoints',{'grid':grid,'derived_grid':derived})
        caller_path=rank9/'dyadic/CALLER.json';C=read(caller_path)
        need(sha256(caller_path.read_bytes()).hexdigest()==G.CALLER,'Exact 18-stage ingredient caller')
        symbolic=I.caller(C)
        need(not symbolic['bad_outputs'] and normalized(symbolic)==previous['caller'],'Full retained ingredient caller')
        before=I.invoices(old,C,oldN);invoice=I.invoices(new,C,N)
        need(normalized(before)==previous['invoice'],'Recomputed complete source ingredient invoice')
        unadjusted=I.ordinary(old,C,oldN);ordinary=I.ordinary(new,C,N)
        routes=previous['ordinary']['caller_items']['B']['fused_routes'];route_delta=routes-unadjusted['caller_items']['B']['fused_routes']
        surcharge=0
        for e in C['events']:
            if e[0]=='B'and e[1]in('ADD','SCALE'):
                q=Q(e[4]if e[1]=='ADD'else e[3]);a,d=abs(q.numerator),q.denominator
                surcharge+=4*(a.bit_length()+d.bit_length()+1+(a.bit_count()if e[1]=='ADD'else 0))
        surcharge*=len(C['types']['B']['ports'])
        need(surcharge==previous['ordinary']['extra_B_scalar_surcharge'],'Fresh caller scalar surcharge')
        need(unadjusted['conservative_total']+route_delta+surcharge==previous['ordinary']['conservative_total'],'Complete source ordinary bill')
        ordinary['caller_items']['B']['fused_routes']=routes
        for k in('caller_total','raw_upper','conservative_total'):ordinary[k]+=route_delta
        ordinary['extra_B_scalar_surcharge']=surcharge;ordinary['conservative_total']+=surcharge
        ordinary['margin_to_billion']=10**9-ordinary['conservative_total'];need(ordinary['margin_to_billion']>0,'Full ordinary allowance')
        gate,price=G.exact_price(vendor,archive,before,invoice,previous)
        (HERE/'INGREDIENT-PRICE.json').write_text(json.dumps(normalized({'before':before,'after':invoice,'gate':gate,'price':price,'ordinary':ordinary}),indent=2)+'\n')
        manifest=read(vendor/'INDEPENDENT-SOURCES.json');P=load('producer_bit_binding',archive/'verify.py');P.bit_binding(I,manifest)
        precision=base.precision(vendor,new,C,gate,manifest)
        need(precision['word']['odd_scale_lcm']==1125 and precision['word']['dyadic_height']==25,'Fresh ingredient precision')
        checkpoint('complete ingredient invoices, both directed prices, all outer gates and precision',{'gate_claim':gate['claim'],'ordinary':ordinary['conservative_total'],'context_c':precision['context_c']})
        chart_receipt=charts(vendor,new)
        controls={}
        for name,event in(
            ('doubled_early_encoding',['ADD',1455,485,'2/3',3]),
            ('doubled_late_decoding',['ADD',1455,485,'-2/3',724]),
            ('doubled_824_compensation',['ADD',824,54,'-1',721])):
            need(new['program'].count(event)==1,'Unique producer correction')
            controls[name]=bool(I.native(new,mutant=new['program'].index(event))['bad_inputs'])
        bad=deepcopy(new);i=bad['program'].index(['MOVE',485,3,724,False]);bad['program'][i][2]=721
        controls['wrong_move_source']=rejects(lambda:I.native(bad))
        bad=deepcopy(new);bad['final'][485]=721
        controls['wrong_output_frame']=rejects(lambda:I.native(bad))
        owned=module('producer_owned_census',vendor/'retained/query-only-precision-envelope/envelopes.py',(('(life, peak, owned_count) == (54, 43, 51)','(life, peak, owned_count) == (74, 50, 68)'),))
        need(owned.validate_word(new)['lifetimes']==74,'Fresh owned census from envelope validator')
        bad=deepcopy(new);bad['program']=[['INIT',1501,724],['CLEAR',1501,724]]+bad['program']
        controls['extra_uncharged_owned_lifetime']=rejects(lambda:owned.validate_word(bad))
        grid_engine=module('producer_grid_controls',vendor/'retained/odd-native-common-grid/independent_bounds.py')
        controls['insufficient_odd_grid']=rejects(lambda:grid_engine.word_run(new,375,25))
        controls['insufficient_fractional_grid']=rejects(lambda:grid_engine.word_run(new,1125,24))
        need(all(controls.values()),'Every corruption control rejected')
        physical_checks=[]
        with tempfile.TemporaryDirectory(prefix='producer-physical-')as tmp:
            path=Path(tmp)/'word.json.gz';path.write_bytes(gzip.compress(canonical(new),mtime=0))
            for command,args in[(vendor/'frozen/verify_host3_odd.py',[path,'1125']),(vendor/'frozen/physical.py',[path,vendor/'frozen/clifford_exact.py','1000000009','11'])]:
                with(HERE/(command.name+'.log')).open('w')as stream:
                    subprocess.run([sys.executable,'-I','-B',str(command),*map(str,args)],stdout=stream,stderr=subprocess.STDOUT,check=True)
                physical_checks.append(command.name)
                print((HERE/(command.name+'.log')).read_text(),end='',flush=True)
            engine=module('producer_signed_routes',rank9/'physical_child.py',(('cca66a7ec924bab47ccd1410968d16e071a01dc6110b5c08040bd207f753d066',EXPECTED),))
            capture=io.StringIO()
            with contextlib.redirect_stdout(capture):engine.main(path,vendor/'data/caller.json',caller_path)
            signed_routes=json.loads(capture.getvalue())
            need(signed_routes['status']=='PASS_PHYSICAL_RANK9_ALGEBRA'and signed_routes['paid_calls']==32,'Signed physical fields')
            need(1000*sum(len(row['caller_fields'])*row['ordinary_elementary_units']for row in signed_routes['bindings'])==routes,'Actual signed-route elementary charge')
        checkpoint('all affected Gaussian columns and absolute phase, finite physical replay and signed routes')
        return normalized(dict(status='PASS_CHANGED_485_1455_PRODUCER_COMPLETE_NATIVE',source_head='58a9d052143f5d85295ed2d0163591c47f89a331',source_word_canonical_sha256=BASELINE,word_canonical_sha256=EXPECTED,native=N,forward=forward_receipt,grid=grid,derived_grid=derived,caller=symbolic,invoice=invoice,ordinary=ordinary,gate=gate,price=price,precision=precision,charts=chart_receipt,controls=controls,physical_checks=physical_checks,signed_routes=signed_routes,adapter=PATCHES,timings=TIMINGS,limitations=['Five inherited framework assumptions remain.','Source-aware retained engines are not independent human/formal acceptance.','The complete 17-stage signed application is checked separately.']))

if __name__=='__main__':
    STARTED=time.time();result=run()
    (HERE/'NATIVE-RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],result['price']['claim_decimal'],flush=True)
