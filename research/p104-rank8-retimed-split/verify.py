#!/usr/bin/env python3
"""Exact successor replay, attributed source engines and complete signed pricing.
Prepared for dillona with substantial OpenAI Codex assistance. Apache-2.0.
The pinned source engines use assertions: optimized Python is rejected explicitly.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,gzip,json,subprocess,sys,tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source import sources,load,read,canonical,need,HERE
from construct import construct,prepare
if not __debug__:raise RuntimeError('Run without -O: pinned source engines use assertions')
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

def chart_check(base,source,word):
    vendor=base/'shared-wire-split-composition'
    C=load('step_chart_compiler',vendor/'frozen/clifford_exact.py')
    V=load('step_chart_interpreter',vendor/'frozen/native_verify.py')
    def pairs(w):
        main=set(w['live'])|{r+112 for r in w['live']}|set(w['hosted']['X2'])|set(w['hosted']['Y2'])
        return {(e[2],e[3])for e in w['program']if e[0]=='MOVE'}|{(w['initial'][r],w['final'][r])for r in range(w['public'])if r not in main}
    changed=pairs(word)-pairs(source)
    needed=changed|{(3,745),(745,747),(3,747),(3,245),(745,245)}
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
    with sources()as(base,source,predecessor):
        witness=read(HERE/'WITNESS.json');prepared,spec=prepare(source,witness)
        word=construct(source,witness)
        need(canonical(word)==gzip.decompress((HERE/'WORD.json.gz').read_bytes()),'Entire regenerated word payload')
        need(witness['pivot']==1468 and witness['frame']==745 and witness['cut']==37420,'Frozen simple split')
        need(len(word['program'])==len(source['program'])+15 and word['public']==source['public']+1,'One extra MOVE and fourteen ordinary ADDs')
        vendor=base/'shared-wire-split-composition';previous=base/'shared-wire-stop-fusion'
        I=load('step_native_adjoint',vendor/'independent.py')
        old=I.native(source);native=I.native(word)
        need(not old['bad_inputs']and not native['bad_inputs'],'Exact all-input adjoint of source and candidate')
        need(delta(native['paid'],old['paid'])=={3:2,6:-1},'Exact local paid delta')
        need(delta(native['helpers'],old['helpers'])=={3:1,5:1,8:-1},'Exact local productive delta')
        need(all(native[k]==old[k]for k in('rises','owned_peak','lifetimes')),'Unchanged owned-ascent/lifetime inventory')
        print('PASS source reconstruction, exact split prefix/suffix, complete adjoint and frame law',flush=True)
        audit=load('step_forward_grid',previous/'audit_native.py')
        forward,grid=audit.replay(word,list(enumerate(word['program'])),set())
        forward_receipt=forward_endpoint(word,forward[0])
        need(grid['odd_grid_lcm']==1125 and grid['owned_rise_mass']==56,'Retained exact grid and owned ascent mass')
        caller=read(vendor/'data/caller.json');caller_result=I.caller(caller)
        need(not caller_result['bad_outputs'],'Exact formal paired QUERY-only caller')
        baseline=I.invoices(source,caller,old);invoice=I.invoices(word,caller,native)
        need(delta(invoice['P'],baseline['P'])=={3:36,6:-18}and delta(invoice['T'],baseline['T'])=={3:18,5:18,8:-18},'Complete invoice over all 18 LOCALs')
        need(invoice['S']==baseline['S']==1520 and invoice['empty_root_credits']==0,'Rank surplus and no empty-root credits')
        ordinary=I.ordinary(word,caller,native);need(ordinary['conservative_total']<10**9,'Full conservative ordinary bill')
        old_result=read(predecessor/'RESULT.json')
        need(encode(baseline)==old_result['invoice'],'Rebuilt invoice equals exact #7105 invoice')
        E=load('step_primary_price',vendor/'interval_gate.py')
        P=load('step_price_constructor',previous/'verify.py')
        source_gate=old_result['gate']
        gate,gain=P.certify_price(E,baseline,invoice,{'raw_lower':source_gate['raw_bracket'][0],'raw_upper':source_gate['raw_bracket'][1],'numeric_BIT_price':source_gate['BIT_pin'],'claim':source_gate['claim']})
        A=load('step_independent_price',previous/'audit_price.py')
        signed=Counter(invoice['T']);signed.subtract(invoice['P'])
        diagnostic,interval,_=A.crossing(signed)
        need(Q(gate['claim'])<interval[0] and Q(source_gate['raw_bracket'][1])<Q(gate['claim']),'Independent new crossing above old ceiling')
        old_signed=Counter(baseline['T']);old_signed.subtract(baseline['P'])
        need(A.raw_margin(old_signed,Q(gate['claim']))[1]<0,'Old complete invoice rejects the new claim')
        manifest=read(vendor/'INDEPENDENT-SOURCES.json');P.bit_binding(I,manifest)
        precision=load('step_precision_reuse',vendor/'precision_replay.py').run(word,caller,gate,manifest)
        print('PASS complete invoice, ordinary bill, BIT binding, two exact price engines, compiler and 54+4 outer gates',flush=True)
        charts=chart_check(base,source,word)
        controls={}
        bad=deepcopy(witness);bad['b']['843']='2'
        controls['wrong_suffix']=rejected(lambda:construct(source,bad))
        bad=deepcopy(witness);bad['paths'][0]['lo']=0
        controls['intervening_contact']=rejected(lambda:construct(source,bad))
        from split import basis
        boundary=basis(*[{int(k):Q(v)for k,v in witness[z].items()} for z in ('c','d')],witness['pivot'],3)
        cut=len(boundary)+spec['cut_after'];bad=deepcopy(word);bad['program'].pop(cut+1)
        controls['missing_cut_correction']=bool(I.native(bad)['bad_inputs'])
        bad=deepcopy(word);bad['program'].pop(cut+5)
        controls['missing_successor_correction']=bool(I.native(bad)['bad_inputs'])
        bad=deepcopy(word);bad['initial'][-1]=3
        controls['wrong_successor_frame']=rejected(lambda:I.native(bad))
        need(all(controls.values()),'All construction and endpoint rejection controls')
        physical_checks=[]
        if physical:
            with tempfile.TemporaryDirectory(prefix='step-physical-')as tmp:
                path=Path(tmp)/'word.json.gz';path.write_bytes(gzip.compress(canonical(word),mtime=0))
                commands=[(vendor/'frozen/verify_host3_odd.py',[path,'1125']),
                          (vendor/'frozen/physical.py',[path,vendor/'frozen/clifford_exact.py','1000000009','11'])]
                for command,args in commands:
                    subprocess.run([sys.executable,'-I','-B',str(command),*map(str,args)],check=True)
                    physical_checks.append(command.name)
        print('PASS exact Gaussian columns, prefix precision and physical finite replay',flush=True)
        return encode({'status':'PASS_P104_RANK8_RETIMED_SPLIT','source_head':'92b09a2bd2a8f6f2e0fb502068c1259350c2a8c8','word_canonical_sha256':sha256(canonical(word)).hexdigest(),'native':native,'forward':forward_receipt,'grid':grid,'caller':caller_result,'invoice':invoice,'ordinary':ordinary,'gate':gate,'gain':gain,'independent_raw_bracket':interval,'diagnostic_crossing':diagnostic,'precision':precision,'charts':charts,'controls':controls,'physical_checks':physical_checks,'limitations':['Source-aware attributed engine reuse, not independent human or kernel review.','All inherited five assumptions and #7105 inherited exact odd-return, owned-ascent, caller, BIT and physical-tariff contracts remain.','No materialized uniform rounded multiplier or selected-frontier change.']})

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path);p.add_argument('--skip-physical',action='store_true');a=p.parse_args()
    result=run(not a.skip_physical)
    if a.out:
        with a.out.open('x')as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    else:need(result==read(HERE/'RESULT.json'),'Complete frozen receipt')
    print(result['status'],result['gate']['claim'],flush=True)
if __name__=='__main__':main()
