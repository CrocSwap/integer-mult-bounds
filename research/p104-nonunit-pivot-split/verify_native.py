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
    needed=changed|{(3,1027),(1027,127),(3,127)}
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

def run(physical=True):
    with sources() as (vendor,archive,rank9,bundle,parent,source):
        hit=read(HERE/'WITNESS.json'); word=construct(source,hit)
        need(canonical(word)==gzip.decompress((HERE/'WORD.json.gz').read_bytes()),'Entire regenerated candidate')
        need(hit['pivot']==639 and hit['cut']==37583 and hit['frame']==1027,'Frozen nonunit-pivot rank-nine split')
        need(len(word['program'])==len(source['program'])+886 and word['public']==1492,'880 ADD and6 SCALE instructions; one independent helper')
        G=load('static_source_gate',bundle/'gate.py')
        base=G.module('static_rank9_gate',rank9/'candidate_gate.py',(
            ('== 1080','== 1092'),('fresh_arbitrary_helpers=18 * 1080','fresh_arbitrary_helpers=18 * 1092'),
            ('grid.word_run(word), grid.caller_run(caller)','grid.word_run(word, frac=25), grid.caller_run(caller)')))
        I=base.independent(vendor); old=I.native(source); native=I.native(word)
        need(not old['bad_inputs'] and not native['bad_inputs'],'Complete arbitrary-input adjoint')
        need(delta(native['paid'],old['paid'])=={},'Entire paid profile unchanged')
        need(delta(native['helpers'],old['helpers'])=={4:1,5:1,9:-1},'Exact rank-nine split into5+4')
        need(all(native[k]==old[k] for k in ('rises','owned_peak','lifetimes')),'Owned inventory unchanged')
        from derive_grid import derive
        derived,_=derive(word)
        need(derived['odd_scale']==1125 and derived['fractional_bits']==25,'Fresh rational common grid including all pre-products')
        audit=G.module('static_forward',archive/'audit_native.py',(
            ('2**24','2**25'),('25 - (abs(value) & -abs(value)).bit_length()','26 - (abs(value) & -abs(value)).bit_length()')))
        forward,grid=audit.replay(word,list(enumerate(word['program'])),set())
        forward_receipt=forward_endpoint(word,forward[0])
        need(grid['odd_grid_lcm']==1125 and grid['owned_rise_mass']==56,'Grid and owned ascent mass')
        need(grid['dyadic_height']==derived['fractional_bits'] and grid['maximum_scaled_mass']==derived['scaled_maximum_mass'],'Independent rational/integer grid and mass agreement')
        print('PASS source reconstruction, whole cut, adjoint and independent forward map',flush=True)
        caller_path=rank9/'dyadic/CALLER.json'; caller=read(caller_path); previous=read(parent/'NATIVE-RESULT.json')
        need(sha256(caller_path.read_bytes()).hexdigest()==G.CALLER,'Pinned signed caller')
        symbolic=I.caller(caller)
        need(not symbolic['bad_outputs'] and symbolic==previous['caller'],'Exact signed formal caller')
        before=I.invoices(source,caller,old); invoice=I.invoices(word,caller,native)
        need(encode(before)==previous['invoice'],'Entire source invoice')
        need(delta(invoice['P'],before['P'])=={} and delta(invoice['T'],before['T'])=={4:18,5:18,9:-18},'Complete changed invoice')
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
        need(precision['word']['odd_scale_lcm']==1125 and precision['word']['dyadic_height']==25,'Recomputed signed caller precision')
        print('PASS full signed caller, ordinary bill, two exact price engines, precision and compiler gates',flush=True)
        charts=chart_check(vendor,source,word)
        controls={}
        grid_engine=G.module('static_grid_controls',vendor/'retained/odd-native-common-grid/independent_bounds.py')
        controls['insufficient_odd_grid']=rejected(lambda:grid_engine.word_run(word,375,25))
        controls['insufficient_fractional_grid']=rejected(lambda:grid_engine.word_run(word,1125,24))
        bad=deepcopy(hit);bad['a']['643']='2'
        controls['wrong_prefix']=rejected(lambda:construct(source,bad))
        bad=deepcopy(hit);bad['b']['643']='1/2'
        controls['wrong_suffix']=rejected(lambda:construct(source,bad))
        bad=deepcopy(hit);bad['frame']=734
        controls['wrong_cut_frame']=rejected(lambda:construct(source,bad))
        from split import basis
        Gbasis=basis(*[{int(k):Q(v)for k,v in hit[s].items()}for s in('c','d')],hit['pivot'],3)
        Jbasis=basis(*[{int(k):Q(v)for k,v in hit[s].items()}for s in('a','b')],hit['pivot'],1027)
        need((len(Gbasis),len(Jbasis))==(426,17),'Boundary and cut basis lengths')
        prepared,spec=prepare(source,hit)
        need(prepared==source and spec['cut_after']==37583,'Neutral placement leaves every source byte and cut unchanged')
        split_after=spec['cut_after']
        for name,index in [('missing_cut_correction',len(Gbasis)+split_after+1),
                           ('missing_successor_correction',len(Gbasis)+len(Jbasis)+split_after+1)]:
            bad=deepcopy(word);bad['program'].pop(index)
            controls[name]=bool(I.native(bad)['bad_inputs'])
        bad=deepcopy(hit);bad['c']['639']='3'
        controls['wrong_boundary_functional']=rejected(lambda:construct(source,bad))
        bad=deepcopy(hit);bad['d']['639']='-7867/8'
        controls['wrong_boundary_direction']=rejected(lambda:construct(source,bad))
        for name,index in [('missing_initial_basis',0),('missing_final_basis',len(word['program'])-1)]:
            bad=deepcopy(word);bad['program'].pop(index)
            controls[name]=bool(I.native(bad)['bad_inputs'])
        bad=deepcopy(word);bad['initial'][-1]=3
        controls['wrong_successor_frame']=rejected(lambda:I.native(bad))
        bad=deepcopy(hit);bad['ranks']=[4,5]
        controls['wrong_target_ranks']=rejected(lambda:construct(source,bad))
        bad=deepcopy(hit);bad['paths'][0]['hi']=bad['paths'][0]['moves'][0]
        controls['incomplete_retiming_interval']=rejected(lambda:prepare(source,bad))
        bad=deepcopy(hit);bad['paid_delta']={'1':1}
        controls['wrong_paid_declaration']=rejected(lambda:prepare(source,bad))
        # A nonzero pivot can still be a forbidden reciprocal. The new
        # unit choice must implement the same row/column basis over Q.
        from split import inverse
        from support import L
        toy_a,toy_b={1:Q(1)},{0:Q(7),1:Q(1)}
        toy=basis(toy_a,toy_b,0,3)
        def unit(q):
            for x in (abs(q.numerator),q.denominator):
                if not x:return False
                for prime in (2,3,5):
                    while x%prime==0:x//=prime
                if x!=1:return False
            return True
        rows={r:{r:Q(1)} for r in (0,1)}
        for e in toy:
            if e[0]=='SCALE':rows[e[1]]={k:Q(e[-2])*v for k,v in rows[e[1]].items()}
            else:L.add(rows[e[1]],rows[e[2]],Q(e[-2]))
        controls['nonzero_nonunit_pivot_repaired']=(rows[0]==toy_a and
            all(sum(v*toy_b.get(k,0) for k,v in row.items())==int(r==0) for r,row in rows.items()) and
            all(unit(Q(e[-2])) for e in toy+inverse(toy) if e[0]=='SCALE'))
        controls['old_nonunit_reciprocal_rejected']=(not unit(1/Q(hit['d']['639'])) and
            Gbasis[:4]==[['ADD',639,802,'1',3],['ADD',802,639,'-1',3],['ADD',639,802,'1',3],['SCALE',802,'-1',3]])
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
        return encode(dict(status='PASS_P104_NONUNIT_PIVOT_NATIVE',source_head='020d581d9856b6db83e448c3f20418bc63b72c34',
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
