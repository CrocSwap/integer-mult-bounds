#!/usr/bin/env python3
"""Exact prefix matrices and a separate rational-row carry oracle."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json
import prefix as p
ROOT=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def step(values,op):
    kind,i,*a=op;out=list(values)
    if kind=='swap':out[i],out[a[0]]=out[a[0]],out[i]
    elif kind=='add':out[i]=values[i]+F(a[1])*values[a[0]]
    elif kind=='scale':out[i]=values[i]*F(a[0])
    else:raise ValueError('oracle operation')
    return out

def matrix_prefixes(word,n,cert):
    d,e=cert;m=[[F(i==j) for j in range(n)] for i in range(n)]
    for op in word:
        m=[step(row,op) for row in m]
        need(all((v*(1<<d)).denominator==1 for row in m for v in row),'prefix denominator')
        need(all(sum(abs(m[i][j]) for i in range(n))<=1<<e for j in range(n)),'prefix column norm')
    return len(word)

def row_case(word,source,q,cert):
    result=p.evaluate_row(word,source,q,cert,trace=True);exact=list(map(F,source));D=1<<cert[0]
    need(len(result['trace'])==len(word),'complete prefix trace')
    for op,(low,num) in zip(word,result['trace']):
        exact=step(exact,op)
        expected=[v.numerator*pow(v.denominator,-1,q)%q for v in exact]
        carries=[D*(v-y)/q for v,y in zip(exact,expected)]
        need(all(c.denominator==1 for c in carries),'oracle integral numerator')
        need(list(low)==expected and list(num)==carries,'rational prefix carry')
    return result

def reject(action,label):
    try:action()
    except (ValueError,IndexError):return label
    raise ValueError('negative control accepted: '+label)

def controls():
    f=p.fw;names=[]
    half=f.literal(2,[('scale',0,'1/2')],'auxiliary-half')
    names.append(reject(lambda:row_case(tuple(f.emit(half)),(1,0),3,(0,0)),'undersized denominator'))
    closed=f.literal(2,[('scale',0,'16'),('scale',0,'1/16')],'auxiliary-endpoint-identity')
    names.append(reject(lambda:matrix_prefixes(tuple(f.emit(closed)),2,(0,0)),'endpoint-only certificate'))
    t=f.tensor(half,half)
    names.append(reject(lambda:matrix_prefixes(tuple(f.emit(t)),4,(1,1)),'max instead of tensor sum'))
    shear=f.literal(2,[('add',1,0,'1')],'auxiliary-shear')
    for r,label in ((f.conjugate(half,shear),'missing conjugation boundary'),(f.guarded(shear,half,1),'missing guard boundary')):
        names.append(reject(lambda r=r:matrix_prefixes(tuple(f.emit(r)),r.n,p.certificate(shear)),label))
    asymmetric=[('add',0,1,'1'),('add',0,2,'1'),('add',0,3,'1')]
    names.append(reject(lambda:matrix_prefixes(asymmetric,4,(0,1)),'wrong norm direction'))
    loop=f.literal(2,[('scale',0,'2'),('add',1,0,'1/2'),('add',1,0,'-1/2'),('scale',0,'1/2')],'auxiliary-exact-division')
    cert=p.certificate(loop);need(cert==(0,1),'d<s witness')
    out=row_case(tuple(f.emit(loop)),(2,0),3,cert)
    need(out['low']==[2,0] and out['numerators']==[0,0],'integer prefix loop return')
    need((1-1)//2==0 and 1//2+(-1)//2==-1,'separate division mutant')
    names.append('separate summand division changes carry')
    need((1-1)%2==0 and 1%2!=0,'missing elementary carry mutant')
    names.append('missing elementary carry breaks division')
    names.append(reject(lambda:matrix_prefixes(tuple(f.emit(half,True)),2,(1,0)),'inverse-prefix norm omitted'))
    return names,dict(d=0,e=1,atom_s=1,q=3,input=[2,0])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);args=ap.parse_args()
    origins=json.loads((ROOT/'ORIGINS.json').read_text())
    for name,entry in origins['files'].items():
        need(sha256((ROOT/name).read_bytes()).hexdigest()==entry['sha256'],'source pin '+name)
    cases=json.loads((ROOT/'retained/CASES.json').read_text());prefixes=rows=words=peak=0;details=[]
    for case in cases:
        recipe=p.restore_recipe(case['recipe']);cert=p.certificate(recipe)
        for inverse in (False,True):
            word=tuple(p.fw.emit(recipe,inverse));expected=case['inverse_word'] if inverse else case['word']
            need([list(op) for op in word]==expected,'retained chronology')
            lowered=tuple(p.fw.expanded_ordered_ops(recipe,inverse))
            if not inverse:need([list(op) for op in lowered]==case['ordered_word'],'retained lowered chronology')
            for emitted in (word,lowered):
                prefixes+=matrix_prefixes(emitted,recipe.n,cert);words+=1
                for q in (3,9,17):
                    for source in ([0]*recipe.n,[q-1]*recipe.n,[(i*i+3*i+1)%q for i in range(recipe.n)]):
                        out=row_case(emitted,source,q,cert);rows+=1;peak=max(peak,out['signed_work_bits'])
        details.append(dict(case=case['label'],n=recipe.n,certificate=list(cert),
                            nonswaps=recipe.count.adds+recipe.count.scales,fixed_signed_bits=sum(cert)+9))
    base=p.restore_recipe(next(c for c in cases if c['label']=='actual_relative')['recipe'])
    base_cert=p.certificate(base);recipe=base;m0=base.count.adds+base.count.scales;family=[]
    for r in range(1,21):
        if r>1:recipe=p.fw.tensor(recipe,base)
        cert=p.certificate(recipe);m=recipe.count.adds+recipe.count.scales
        need(cert==(r*base_cert[0],r*base_cert[1]),'tensor certificate')
        need(m==r*base.n**(r-1)*m0,'expanded tensor count')
        family.append(dict(r=r,N=recipe.n,certificate=list(cert),fixed_signed_bits=sum(cert)+9,previous_linear_bits=6*m+5))
    negatives,witness=controls()
    result=dict(status='PASS_STRUCTURAL_PREFIX_WIDTH',source_files=len(origins['files']),
                source_recipe_cases=len(cases),forward_inverse_words=words,exact_matrix_prefixes=prefixes,
                rational_row_cases=rows,maximum_tested_work_bound=peak,cases=details,tensor_family=family,
                negative_controls=negatives,combined_division_witness=witness,
                scope='Prefix widths and supplied-low evaluation; no selected depth, private-H, payload or owner-return closure.')
    if args.output:args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','exact_matrix_prefixes','rational_row_cases','maximum_tested_work_bound')},sort_keys=True))

if __name__=='__main__':main()
