"""Check separation and every rounded output against exact independent endpoints.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Retained test factories and dense oracle are credited in SOURCES.json.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from detector import budget, detect
from literal import replay
from witness import construct


def need(value, message):
    if not value:
        raise ValueError(message)


def reject(call):
    try:
        call()
    except (ValueError,TypeError):
        return
    raise ValueError('invalid case accepted')


def run(small):
    for row in json.loads((ROOT/'SOURCES.json').read_text())['files']:
        if '/vendor/' in row['path']:
            need(hashlib.sha256((ROOT.parents[1]/row['path']).read_bytes()).hexdigest()==row['sha256'], 'source bytes')
    spec=importlib.util.spec_from_file_location('_orthogonal_cases',ROOT/'vendor/orthogonal/verify.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    digest=hashlib.sha256();cases=[];zero=nonzero=0
    max_bits=0
    def inspect(p,word=None,parameter=Q(1,4),input_index=0,output_index=0,dense=True,label='case'):
        nonlocal zero,nonzero,max_bits
        if word is None:
            w=construct(p,parameter);word=w['word'];parameter=Q(w['parameter'])
            input_index,output_index=w['input'],w['output']
        r=detect(p,word,parameter,input_index,output_index)
        exact=replay(p,word,parameter,input_index)
        if dense:
            w={'word':word,'dimension':len(word)+1,'parameter':str(parameter),'input':input_index}
            need(exact==old.dense_replay(p,w),'separate dense exact endpoint')
        plan=r['plan'];scale=1 << plan['bits'];eta=plan['separation']
        value=exact[output_index][0]
        if value:
            need(abs(value)>=eta,'nonzero separation bound')
            nonzero+=1
        else:zero+=1
        need(r['nonzero']==bool(value),'dyadic classification')
        distance=max(abs(Q(x,scale)-y) for a,b in zip(r['endpoint_integers'],exact) for x,y in zip(a,b))
        need(distance<=plan['error']<=eta/4,'complete data and coefficient error')
        need(r['matrix_products']==plan['calls']*(len(word)+1)**2,'dense product invoice')
        need(r['data_roundings']==plan['steps']*(len(word)+1),'complete rounding invoice')
        max_bits=max(max_bits,plan['bits'])
        encoded={'label':label,'nonzero':r['nonzero'],'bits':plan['bits'],
                 'separation_denominator_bits':plan['coefficient_denominator_bits'],
                 'matrix_products':r['matrix_products'],'data_roundings':r['data_roundings'],
                 'dimension':len(word)+1}
        digest.update(json.dumps(r['endpoint_integers']).encode());cases.append(encoded)
        return r
    wrong=json.loads((ROOT/'vendor/orthogonal/vendor/wrong-order.json').read_text())
    inspect(wrong,label='commutator')
    inspect(wrong,parameter=Q(1,2**80),label='tiny-parameter')
    sandwich=json.loads((ROOT/'vendor/orthogonal/vendor/dirty-sandwich.json').read_text())
    inspect(sandwich,word=['A','B','A'],label='equal-dirty-sandwich')
    for j in range(len(sandwich['left'])):
        p=deepcopy(sandwich);del p['left'][j];inspect(p,label='deleted-sandwich-'+str(j))
    tiny=old.program();tiny['left']=[old.linear('x',[['x',str(1+Q(1,2**80))]])]
    inspect(tiny,label='tiny-scalar-discrepancy')
    huge=old.program();huge['left']=[old.apply('x','A',1),old.linear('x',[['x',2**100]])]
    huge['right']=[old.linear('x',[['x',2**100]])]
    inspect(huge,label='large-scalar-gain')
    self_query=old.program();self_query['left']=[old.query('x','x','A',-1,'3/7')]
    inspect(self_query,label='rational-aliased-query')
    dirty=old.program(['x','h']);dirty['left']=[old.apply('h','B',-1)]
    inspect(dirty,label='dirty-return')
    for count in (1,2,4):
        p=old.grid_roots(count)
        inspect(p,label='selected-grid-'+str(count))
        inspect(p,word=['A'],parameter=Q(1,4),label='cancelled-grid-'+str(count))
    rng=random.Random(53155326)
    for k in range(8 if small else 80):
        p=old.program(['x','h','y'])
        for side in ('left','right'):
            for _ in range(rng.randint(2,7)):
                dst,src=rng.choice(p['roles']),rng.choice(p['roles']);a=rng.choice(p['operators']);sign=rng.choice((-1,1))
                kind=rng.randrange(3)
                if kind==0:ins=old.apply(dst,a,sign)
                elif kind==1:ins=old.query(dst,src,a,sign,str(Q(rng.randint(-3,3),rng.randint(1,7))))
                else:ins=old.linear(dst,[[src,str(Q(rng.randint(-3,3),rng.randint(1,7)))],[dst,1]])
                p[side].append(ins)
        if k%4==0:
            p['right']=deepcopy(p['left'])+[old.apply('h','A',1),old.apply('h','A',-1)]
        if old.group_difference(p):inspect(p,label='random-'+str(k))
        else:inspect(p,word=['A','B','A'],input_index=k%3,output_index=(k//3)%3,label='random-equal-'+str(k))
    depth=4 if small else 16
    stress=inspect(old.stress(depth),dense=False,label='inverse-series-stress')
    controls=0
    for parameter in (Q(0),Q(-1,8),Q(1,2)):
        reject(lambda: detect(wrong,['A','B'],parameter,0,0));controls+=1
    for word,i,o in [(['C'],0,0),(['A'],True,0),(['A'],0,2)]:
        reject(lambda: detect(wrong,word,Q(1,4),i,o));controls+=1
    bad=deepcopy(wrong);bad['field']=2
    reject(lambda: detect(bad,['A'],Q(1,4),0,0));controls+=1
    return dict(status='PASS',cases=cases,zero=zero,nonzero=nonzero,rejecting_controls=controls,
                maximum_fractional_bits=max_bits,stress_lowest_degree_words=2**depth,
                digest=digest.hexdigest())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--small',action='store_true');ap.add_argument('--write-result',action='store_true')
    a=ap.parse_args();r=run(a.small)
    if not a.small:
        if a.write_result:(ROOT/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
        else:need(r==json.loads((ROOT/'RESULT.json').read_text()),'receipt differs')
    print(json.dumps(r,sort_keys=True));print('PASS_ORTHOGONAL_WITNESS_PRECISION')


if __name__=='__main__':main()
