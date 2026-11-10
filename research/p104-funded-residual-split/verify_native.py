#!/usr/bin/env python3
"""Source-bound exact split, full signed invoice and finite physical verification.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse, contextlib, gzip, io, json, subprocess, sys, tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source import sources,load,read,canonical,need,HERE
from construct import construct,prepare
if not __debug__: raise RuntimeError('Run without -O: source engines use assertions')
sys.dont_write_bytecode=True

def delta(a,b):
    c=Counter(a);c.subtract(b);return {r:n for r,n in sorted(c.items())if n}

def rejected(action):
    try:action()
    except (ValueError,AssertionError):return True
    raise ValueError('Invalid control was accepted')

def encode(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {str(k):encode(v)for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode(v)for v in value]
    return value

def chart_check(vendor,source,word):
    C=load('step_chart_compiler',vendor/'frozen/clifford_exact.py')
    V=load('step_chart_interpreter',vendor/'frozen/native_verify.py')
    def pairs(w):
        main=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
        return {(e[2],e[3])for e in w['program']if e[0]=='MOVE'}|{(w['initial'][r],w['final'][r])for r in range(w['public'])if r not in main}
    changed=pairs(word)-pairs(source)
    needed=changed|{(3,246),(246,127),(3,127),(232,246)}
    out=[]
    for a,b in sorted(needed):
        ca,cb=[C.canonical_frame(9,tuple(word['frames'][f]))for f in(a,b)]
        recipe,_=C.lower_child(ca.adjoint().then(cb))
        expected=V.adjoint(V.frame(word['frames'][a],9))+V.frame(word['frames'][b],9)
        actual=V.recipe(recipe);V.equal(actual,expected,'Signed Pauli action and absolute phase')
        need(recipe['rank']==abs(len(word['frames'][a])-len(word['frames'][b])),'Exact chart rank')
        for column in range(512):need(V.state(actual,column)==V.state(expected,column),'All Gaussian columns')
        bad=deepcopy(recipe);bad['left']['phase']=(bad['left']['phase']+1)%4
        need(rejected(lambda:V.equal(V.recipe(bad),expected,'wrong phase')),'Wrong phase rejected')
        out.append({'pair':[a,b],'rank':recipe['rank'],'columns':512})
    return {'new_pairs':sorted(changed),'rechecked_pairs':out,'wrong_phase_rejected':True}

def forward_endpoint(word,rows):
    n=word['public'];unit=1125*2**24
    target=[{r:Q(1)}if r<n else{}for r in range(n+word['owned_fields'])]
    H=word['hosted'];D=set(H['Dports'])
    for i,x in enumerate(word['live']):
        y=x+112
        if i in D:target[y][x]=Q(1)
        else:target[x][y]=Q(-1);target[y]={x:Q(1,2),y:Q(1,2)}
    for x,y in zip(H['X2'],H['Y2']):target[x][y]=Q(-1)
    need(all(row=={k:v*unit for k,v in want.items()}for row,want in zip(rows,target)),'Every forward input/output coefficient and cleared owned row')
    return {'rows':len(rows),'coefficient_positions':len(rows)**2,'grid':1125,'fractional_bits':24}

def run(physical=True):
    with sources() as (vendor,archive,rank9,bundle,parent,source):
        hit=read(HERE/'WITNESS.json'); word=construct(source,hit)
        need(canonical(word)==gzip.decompress((HERE/'WORD.json.gz').read_bytes()),'Entire regenerated candidate')
        need(hit['pivot']==236 and hit['cut']==45209 and hit['frame']==246,'Frozen residual three-role cut')
        need(len(word['program'])==len(source['program'])+29 and word['public']==1487,'28 scalar instructions, one added MOVE and one independent helper')
        G=load('static_source_gate',bundle/'gate.py')
        base=G.module('static_rank9_gate',rank9/'candidate_gate.py',(
            ('== 1080','== 1087'),('fresh_arbitrary_helpers=18 * 1080','fresh_arbitrary_helpers=18 * 1087')))
        I=base.independent(vendor); old=I.native(source); native=I.native(word)
        need(not old['bad_inputs'] and not native['bad_inputs'],'Complete arbitrary-input adjoint')
        need(delta(native['paid'],old['paid'])=={1:1,4:1,5:-1},'Entire paid rank-five subdivision charged')
        need(delta(native['helpers'],old['helpers'])=={1:1,8:1,9:-1},'Exact rank-nine split')
        need(all(native[k]==old[k] for k in ('rises','owned_peak','lifetimes')),'Owned inventory unchanged')
        from derive_grid import derive
        derived,_=derive(word)
        need(derived['odd_scale']==1125 and derived['fractional_bits']==24,'Fresh rational common grid including all pre-products')
        audit=load('static_forward',archive/'audit_native.py')
        forward,grid=audit.replay(word,list(enumerate(word['program'])),set())
        forward_receipt=forward_endpoint(word,forward[0])
        need(grid['odd_grid_lcm']==1125 and grid['owned_rise_mass']==56,'Grid and owned ascent mass')
        print('PASS source reconstruction, whole cut, adjoint and independent forward map',flush=True)
        caller_path=rank9/'dyadic/CALLER.json'; caller=read(caller_path); previous=read(parent/'NATIVE-RESULT.json')
        need(sha256(caller_path.read_bytes()).hexdigest()==G.CALLER,'Pinned signed caller')
        symbolic=I.caller(caller)
        need(not symbolic['bad_outputs'] and symbolic==previous['caller'],'Exact signed formal caller')
        before=I.invoices(source,caller,old); invoice=I.invoices(word,caller,native)
        need(encode(before)==previous['invoice'],'Entire source invoice')
        need(delta(invoice['P'],before['P'])=={1:18,4:18,5:-18} and delta(invoice['T'],before['T'])=={1:18,8:18,9:-18},'Complete changed invoice')
        need(invoice['S']==before['S']==1520 and invoice['empty_root_credits']==0,'Surplus and no empty credit')
        unadjusted=I.ordinary(source,caller,old); ordinary=I.ordinary(word,caller,native)
        routes=previous['ordinary']['caller_items']['B']['fused_routes']
        route_delta=routes-unadjusted['caller_items']['B']['fused_routes']
        surcharge=0
        for e in caller['events']:
            if e[0]=='B' and e[1] in ('ADD','SCALE'):
                q=Q(e[4] if e[1]=='ADD' else e[3]);a,d=abs(q.numerator),q.denominator
                surcharge+=4*(a.bit_length()+d.bit_length()+1+(a.bit_count() if e[1]=='ADD' else 0))
        surcharge*=len(caller['types']['B']['ports'])
        need(surcharge==previous['ordinary']['extra_B_scalar_surcharge'],'Recomputed B scalar surcharge')
        need(unadjusted['conservative_total']+route_delta+surcharge==previous['ordinary']['conservative_total'],'Reconstructed source ordinary bill')
        ordinary['caller_items']['B']['fused_routes']=routes
        for key in ('caller_total','raw_upper','conservative_total'):ordinary[key]+=route_delta
        ordinary['extra_B_scalar_surcharge']=surcharge;ordinary['conservative_total']+=surcharge
        ordinary['margin_to_billion']=10**9-ordinary['conservative_total']
        need(ordinary['margin_to_billion']>0,'Complete conservative ordinary bill')
        gate,price=G.exact_price(vendor,archive,before,invoice,previous)
        manifest=read(vendor/'INDEPENDENT-SOURCES.json')
        P=load('static_bit_binding',archive/'verify.py');P.bit_binding(I,manifest)
        precision=base.precision(vendor,word,caller,gate,manifest)
        need(precision['word']['odd_scale_lcm']==1125 and precision['word']['dyadic_height']==24,'Recomputed signed caller precision')
        print('PASS full signed caller, ordinary bill, two exact price engines, precision and compiler gates',flush=True)
        charts=chart_check(vendor,source,word)
        controls={}
        grid_engine=G.module('static_grid_controls',vendor/'retained/odd-native-common-grid/independent_bounds.py')
        controls['insufficient_odd_grid']=rejected(lambda:grid_engine.word_run(word,375,24))
        controls['insufficient_fractional_grid']=rejected(lambda:grid_engine.word_run(word,1125,23))
        bad=deepcopy(hit);bad['a']['789']='2'
        controls['wrong_prefix']=rejected(lambda:construct(source,bad))
        bad=deepcopy(hit);bad['b']['789']='2'
        controls['wrong_suffix']=rejected(lambda:construct(source,bad))
        bad=deepcopy(hit);bad['frame']=734
        controls['wrong_cut_frame']=rejected(lambda:construct(source,bad))
        from split import basis
        Gbasis=basis(*[{int(k):Q(v)for k,v in hit[s].items()}for s in('c','d')],hit['pivot'],3)
        Jbasis=basis(*[{int(k):Q(v)for k,v in hit[s].items()}for s in('a','b')],hit['pivot'],246)
        need((len(Gbasis),len(Jbasis))==(7,7),'Boundary and cut basis lengths')
        prepared,spec=prepare(source,hit)
        split_after=spec['cut_after']
        for name,index in [('missing_cut_correction',len(Gbasis)+split_after+1),
                           ('missing_successor_correction',len(Gbasis)+len(Jbasis)+split_after+1)]:
            bad=deepcopy(word);bad['program'].pop(index)
            controls[name]=bool(I.native(bad)['bad_inputs'])
        for role in (789,472,1359):
            bad=deepcopy(hit);bad['paths']=[p for p in bad['paths'] if p['role']!=role]
            controls['missing_retiming_'+str(role)]=rejected(lambda:construct(source,bad))
        bad=deepcopy(hit);bad['paths'][0]['lo']-=1
        controls['intervening_scalar_contact']=rejected(lambda:construct(source,bad))
        bad=deepcopy(hit);bad['paths'][0]['moves']=[]
        controls['omitted_old_move']=rejected(lambda:construct(source,bad))
        bad=deepcopy(hit);bad['paths'].append(deepcopy(bad['paths'][0]))
        controls['duplicate_retimed_role']=rejected(lambda:construct(source,bad))
        bad=deepcopy(word);bad['initial'][-1]=3
        controls['wrong_successor_frame']=rejected(lambda:I.native(bad))
        bad=deepcopy(hit);bad['paid_delta']={}
        controls['unpaid_subdivisions']=rejected(lambda:prepare(source,bad))
        bad=deepcopy(hit);bad['paths'][0]['new_paid']=[2]
        controls['wrong_declared_path_ranks']=rejected(lambda:prepare(source,bad))
        need(all(controls.values()),'All split rejection controls')
        physical_checks=[]; signed_routes=None
        if physical:
            with tempfile.TemporaryDirectory(prefix='static-physical-') as tmp:
                path=Path(tmp)/'word.json.gz';path.write_bytes(gzip.compress(canonical(word),mtime=0))
                for command,args in [(vendor/'frozen/verify_host3_odd.py',[path,'1125']),
                                     (vendor/'frozen/physical.py',[path,vendor/'frozen/clifford_exact.py','1000000009','11'])]:
                    subprocess.run([sys.executable,'-I','-B',str(command),*map(str,args)],check=True)
                    physical_checks.append(command.name)
                physical_engine=G.module('static_signed_routes',rank9/'physical_child.py',(
                    ('cca66a7ec924bab47ccd1410968d16e071a01dc6110b5c08040bd207f753d066',sha256(canonical(word)).hexdigest()),))
                capture=io.StringIO()
                with contextlib.redirect_stdout(capture):physical_engine.main(path,vendor/'data/caller.json',caller_path)
                signed_routes=json.loads(capture.getvalue())
                need(signed_routes['status']=='PASS_PHYSICAL_RANK9_ALGEBRA' and signed_routes['paid_calls']==32,'Signed physical route replay')
                need(1000*sum(len(row['caller_fields'])*row['ordinary_elementary_units'] for row in signed_routes['bindings'])==routes==1168000,'Actual signed route ordinary charge')
                physical_checks.append('physical_child.py')
        print('PASS chart columns and phase, rejection controls and finite physical replay',flush=True)
        return encode(dict(status='PASS_P104_FUNDED_RESIDUAL_NATIVE',source_head='092255ac8e9ed07ea59fee87c9711a5d72b10750',
            word_canonical_sha256=sha256(canonical(word)).hexdigest(),native=native,forward=forward_receipt,grid=grid,derived_grid=derived,
            caller=symbolic,invoice=invoice,ordinary=ordinary,gate=gate,price=price,precision=precision,
            charts=charts,controls=controls,physical_checks=physical_checks,signed_routes=signed_routes,
            limitations=['Source-aware reuse of attributed engines, not independent human or kernel review.',
            'The five framework assumptions remain; the current17-stage application is checked separately by verify.py.',
            'Finite physical checks and source-unit bills do not constitute a complete multiplication theorem.']))

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);p.add_argument('--skip-physical',action='store_true');a=p.parse_args()
    result=run(not a.skip_physical)
    if a.out:
        with a.out.open('x') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    else:need(result==read(HERE/'NATIVE-RESULT.json'),'Every frozen receipt field')
    print(result['status'],result['gate']['claim'],flush=True)
if __name__=='__main__':main()
