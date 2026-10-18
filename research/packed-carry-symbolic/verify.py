#!/usr/bin/env python3
"""All-even-radix interval certificate checker; Apache-2.0.
Prepared for Philipp/mightyOil with substantial OpenAI Codex GPT-6 Astra assistance.
No predecessor carry-table implementation is imported.
"""
import argparse
import ast
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATES = (0, 5, 10, 80, 160)
INPUTS = {'upstream/build/sections/05-layers.tex', 'tests/test_finite_identities.py', 'upstream/LICENSE'}
# Affine endpoints (coefficient of N, constant), B=2N.
CELLS = {'left': ((0, 0), (0, 0)),
         'middle': ((0, 1), (1, -2)),
         'right': ((1, -1), (1, -1))}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def affine(v, n):
    return v[0]*n+v[1]


def nonnegative(v, start):
    # Exact universal implication for every integer N>=start.
    return v[0] >= 0 and affine(v, start) >= 0


def source_check():
    data = json.loads((HERE/'SOURCES.json').read_text())
    rows = [r for r in data['files'] if r['usage']=='input']
    need(len(rows)==len(INPUTS) and {r['path'] for r in rows}==INPUTS, 'source inventory')
    for r in rows:
        b=(ROOT/r['path']).read_bytes()
        need(hashlib.sha256(b).hexdigest()==r['sha256'], 'source sha256')
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['git_blob'], 'source blob')
    tex=(ROOT/'upstream/build/sections/05-layers.tex').read_text()
    text=tex.split(r'\label{eq:eight-packed-additions}',1)[1].split(r'\end{array}',1)[0]
    # Parse the literal named equation, including target, sign, tested source,
    # parity and chronological gate labels. Do not import PR1245's gate arrays.
    pattern=r'([uw])&\\leftarrow&([uw])([+-])c\[\\,([uw])\\equiv([01])\\pmod2\\,\],?\.?&\((\d)\)'
    rows=re.findall(pattern,text)
    need(len(rows)==8,'eight literal rows')
    gates=[]
    for i,(target,repeat,sign,other,parity,label) in enumerate(rows):
        need(target==repeat and target!=other and int(label)==i+1, 'gate binding')
        gates.append((int(target=='w'), 1 if sign=='+' else -1, int(parity)))
    # Separate source encoding from the retained whole-word simulator AST.
    tree=ast.parse((ROOT/'tests/test_finite_identities.py').read_text())
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='packed_steps')
    literal=ast.literal_eval(next(n.value for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='lines' for t in n.targets)))
    need(gates==[(int(t=='z'),s,p) for t,s,p in literal], 'whole-word source disagreement')
    return tuple(gates)


def lift(gates, state, c, a, b):
    """Unwrapped parity translation: U_t=(2g,2h)+offset_t."""
    values=[a,b]
    trace=[list(values)]
    for i,(t,s,p) in enumerate(gates):
        values[t] += s*(c*int(values[1-t]%2==p)+((state>>i)&1))
        trace.append(list(values))
    return trace


def generate(gates):
    cells=[]
    for state,c,a,b in product(STATES,(0,1),(0,1),(0,1)):
        trace=lift(gates,state,c,a,b)
        for left,right in product(CELLS, repeat=2):
            names=(left,right)
            n=4
            xy=[affine(CELLS[name][0],n) for name in names]
            quotients=[[(2*xy[t]+v[t])//(2*n) for t in (0,1)] for v in trace]
            cells.append({'state':state,'control':c,'parities':[a,b],'cells':list(names),'quotients':quotients})
    return {'schema_version':1,'parameter':'B=2N, integer N>=2', 'cells':cells}


def expected():
    # Polynomials are [constant,N,N^2].
    out={}
    for state,c in product(STATES,(0,1)):
        if c==0:
            out[(state,c)]={0:[0,0,4]} if state==0 else {0:[0,-2,4],state:[0,2,0]}
        elif state==0:
            out[(state,c)]={0:[0,-4,4],**{s:[0,1,0] for s in STATES[1:]}}
        else:
            out[(state,c)]={}
    return out


def verify_certificate(cert,gates):
    need(cert.get('schema_version')==1 and cert.get('parameter')=='B=2N, integer N>=2','certificate schema')
    inventory=set(product(STATES,(0,1),(0,1),(0,1),CELLS,CELLS))
    counts=defaultdict(lambda:defaultdict(lambda:[0,0,0]))
    coverage=defaultdict(lambda:[0,0,0])
    inequalities=carry_checks=matching=0
    for row in cert['cells']:
        state,c=row['state'],row['control'];a,b=row['parities'];names=row['cells']
        key=(state,c,a,b,*names)
        need(key in inventory,'duplicate or out-of-domain cell');inventory.remove(key)
        trace=lift(gates,state,c,a,b)
        qs=row['quotients']
        need(len(qs)==9 and all(len(q)==2 and all(type(x)==int for x in q) for q in qs),'integer quotient witnesses')
        nmin=3 if 'middle' in names else 2
        need(qs[0]==[0,0],'initial quotient')
        lengths=[]
        for t,name in enumerate(names):
            lo,hi=CELLS[name]
            # Endpoints cover g=0, 1..N-2, N-1 without overlap.
            lengths.append((hi[0]-lo[0],hi[1]-lo[1]+1))
            for k in range(9):
                q=qs[k][t];v=trace[k][t]
                lower=(2*lo[0]-2*q,2*lo[1]+v)
                upper=(2-2*hi[0]+2*q,-1-2*hi[1]-v)
                need(nonnegative(lower,nmin) and nonnegative(upper,nmin),'universal floor inequality')
                inequalities+=2
        outgoing=0
        for i,(t,s,p) in enumerate(gates):
            delta=qs[i+1][t]-qs[i][t]
            need(delta in (0,s) and qs[i+1][1-t]==qs[i][1-t],'signed outgoing carry')
            outgoing|=int(delta!=0)<<i;carry_checks+=1
        errors=[(-2*qs[-1][0],trace[-1][0]-(a^c)),(-2*qs[-1][1],trace[-1][1]-b)]
        match=all(v==(0,0) for v in errors)
        if not match:
            # A single identically nonzero residue difference proves disagreement.
            need(any(nonnegative((u,v-1),nmin) or nonnegative((-u,-v-1),nmin) for u,v in errors),'uniform mismatch')
        ax,bx=lengths[0];ay,by=lengths[1]
        weight=[bx*by,ax*by+ay*bx,ax*ay]
        for i in range(3):coverage[(state,c)][i]+=weight[i]
        if match:
            need(outgoing in STATES,'matching-state closure')
            for i in range(3):counts[(state,c)][outgoing][i]+=weight[i]
            matching+=1
    need(not inventory,'missing symbolic cell')
    need(all(v==[0,0,4] for v in coverage.values()) and len(coverage)==10,'complete radix square')
    got={k:dict(v) for k,v in counts.items()}
    for key,target in expected().items():
        need(got.get(key,{})==target,'transition polynomial mismatch')
    # Incoming signed carry pairs cancel on every inactive suffix coordinate.
    for state in STATES:
        for target in (0,1):
            need(sum(s*((state>>i)&1) for i,(t,s,p) in enumerate(gates) if t==target)==0,'suffix cancellation')
    return {'symbolic_cells':360,'affine_inequalities':inequalities,'signed_carry_checks':carry_checks,
            'matching_cells':matching,'transition_rows':10,'covered_radices':'every even integer B>=4',
            'polynomials':{f'{s}:{c}':{str(k):v for k,v in expected()[(s,c)].items()} for s,c in product(STATES,(0,1))}}


def whole_word_checks():
    spec=importlib.util.spec_from_file_location('retained',ROOT/'tests/test_finite_identities.py')
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    rows=[];total=0
    # Complete dirty fields including the inactive suffix. This is finite
    # source binding, not the all-radix proof above.
    for k,f in ((2,2),(2,3),(3,2)):
        modulus=1<<(k*f)
        for bits in product((0,1),repeat=f-1):
            x=sum(v<<(k*i) for i,v in enumerate(bits));fail=0
            for y,z in product(range(modulus),repeat=2):
                fail+=source.packed_steps(x,y,z,k,f,0)!=(x,y^x,z)
            ones=[i for i,v in enumerate(bits) if v]
            agreement=Fraction(1)
            for i,j in zip(ones,ones[1:]):agreement*=1-Fraction(2,(1<<k)**(j-i))
            need(Fraction(fail,modulus**2)==1-agreement,'whole-word fiber count')
            total+=modulus**2;rows.append([k,f,x,fail,modulus**2])
    return {'complete_word_states':total,'fibers':rows}


def controls(cert,gates):
    import copy
    mutations=[]
    bad=copy.deepcopy(cert);bad['cells'][0]['quotients'][1][0]=1;mutations.append(('false quotient',bad,gates))
    bad=copy.deepcopy(cert);bad['cells'].pop();mutations.append(('missing boundary cell',bad,gates))
    bad=copy.deepcopy(cert);bad['cells'][-1]=bad['cells'][0];mutations.append(('duplicate cell',bad,gates))
    for i in (0,3,7):
        g=list(gates);t,s,p=g[i];g[i]=(t,-s,p);mutations.append((f'gate {i+1} sign',cert,g))
    g=list(gates);t,s,p=g[4];g[4]=(t,s,1-p);mutations.append(('gate5 parity',cert,g))
    for name,bad,g in mutations:
        try:verify_certificate(bad,g)
        except (ValueError,KeyError):pass
        else:raise ValueError('accepted mutation '+name)
    # Odd radices do not preserve parity under normalization: explicit failure.
    x,y,z=1,0,0;B=3;values=[y,z]
    for t,s,p in gates:values[t]=(values[t]+s*x*int(values[1-t]%2==p))%B
    need(values!=[1,0],'odd radix control')
    # Target-only agreement misses an actually corrupted dirty temporary.
    spec=importlib.util.spec_from_file_location('control_source',ROOT/'tests/test_finite_identities.py')
    source=importlib.util.module_from_spec(spec);spec.loader.exec_module(source)
    got=source.packed_steps(65,65,0,6,3,0)
    need(got[1]==0 and got[2]!=0,'dirty target control')
    return {'rejected_certificate_or_gate_mutations':[m[0] for m in mutations],
            'odd_radix_witness':{'B':3,'input':[1,0,0],'actual':values,'ideal':[1,0]},
            'target_only_witness':{'input':[65,65,0],'actual':list(got),'ideal':[65,0,0]}}


def run():
    gates=source_check()
    cert=json.loads((HERE/'CERTIFICATE.json').read_text())
    proof=verify_certificate(cert,gates)
    return {'proof':proof,'finite_binding':whole_word_checks(),'controls':controls(cert,gates)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--generate',action='store_true');parser.add_argument('--write',type=Path);args=parser.parse_args()
    if args.generate:
        with (HERE/'CERTIFICATE.json').open('x') as f:json.dump(generate(source_check()),f,indent=2);f.write('\n')
    result=run()
    if args.write:
        with args.write.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    else:
        expected_result=json.loads((HERE/'EXPECTED.json').read_text())
        need(result==expected_result,'expected evidence drift')
    print('PASS_SYMBOLIC_PACKED_CARRY cells=360 all_even_B>=4 no_new_kappa')

if __name__=='__main__':main()
