"""Check the rational-size proof against exact, independently checked programs.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Retained source oracles have their original author and license notices.
"""
import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from budget import audit, bounds, check_size, height, need, ReachableBasis
from fields import Field
from oracles import reduced_word_endpoint, apply_witness


def apply(a='A',direction=1,dst='x'):
    return dict(op='apply',dst=dst,operator=a,direction=direction)


def query(dst='x',src='x',a='A',c=-1,direction=1):
    return dict(op='query',dst=dst,src=src,operator=a,direction=direction,coefficient=c)


def linear(dst,terms):
    return dict(op='linear',dst=dst,terms=[[name,c] for name,c in terms])


def program(left=(),right=(),roles=('x',),operators=('A','B')):
    return dict(schema='inverse-dirty-program/v1',field=0,roles=list(roles),
                operators=list(operators),left=list(left),right=list(right))


def reject(call):
    try:call()
    except ValueError:return
    raise ValueError('invalid case accepted')


def run(small):
    need(sys.get_int_max_str_digits()==0,'run with -X int_max_str_digits=0 for explicit large rationals')
    for source in json.loads((ROOT/'SOURCES.json').read_text())['files']:
        if source['path'].startswith('research/inverse-certificate-bit-bounds/'):
            need(hashlib.sha256((ROOT.parents[1]/source['path']).read_bytes()).hexdigest()==source['sha256'],'source bytes')
    rows=[];dense=0;word_checks=0

    def inspect(name,p,expected=None,literal=True):
        nonlocal dense,word_checks
        record=audit(p);cert=record.pop('certificate')
        if expected:need(cert['verdict']==expected,'expected verdict')
        if literal:
            need((not any(reduced_word_endpoint(p)))==(cert['verdict']=='equal'),'reduced group-word oracle');word_checks+=1
        if cert['verdict']=='different':
            value=apply_witness(p,cert['word'],p['roles'][cert['input']])
            need(value[cert['output']][0]==Q(cert['coefficient']),'independent unipotent matrix witness');dense+=1
        record.update(name=name,certificate_digest=hashlib.sha256(json.dumps(cert,sort_keys=True).encode()).hexdigest())
        rows.append(record)
        return p,cert,record

    inspect('empty',program(), 'equal')
    for name in ('dirty-sandwich','wrong-order'):
        inspect(name,json.loads((ROOT/'vendor'/(name+'.json')).read_text()))
    huge=str(2**16000+1)
    _,_,raw=inspect('large-reducible-input',program([linear('x',[('x',huge+'/'+huge)])]),'equal')
    need(raw['bounds']['explicit_scalar_bits']==32002,'unreduced input size is charged')
    inspect('explicit-16001-bit-scalar',program([linear('x',[('x',huge)])]),'different')
    for degree in ((1,4) if small else (1,2,4,8,16)):
        p=program([query()]*degree+[apply(direction=-1)],[linear('x',[])],operators=('A',))
        _,cert,_=inspect('inverse-tail-'+str(degree),p,'different')
        need(len(cert['word'])==degree,'delayed shortest word')
    for denominator in (3,101,2**127-1):
        steps=[linear('x',[('x','1/'+str(denominator))]),query(a='A',c='2/7'),apply('B',-1)]*3
        inspect('coprime-denominators-'+str(denominator),program(steps,roles=('x',)),'different')
    for bits in (20,160,1024):
        delta=Q(1,2**bits+1)
        rowspec=[(1,1,1),(1,1+delta,1),(1,1,1+delta)]
        p=program([linear('y'+str(i),list(zip(('x0','x1','x2'),map(str,row)))) for i,row in enumerate(rowspec)],
                  [linear('y'+str(i),[]) for i in range(3)],roles=('x0','x1','x2','y0','y1','y2'))
        inspect('nearly-dependent-'+str(bits),p,'different')
    # This isolates determinant amplification from large endpoint magnitude.
    basis=ReachableBasis(Field());scale=2**1024+1
    need(basis.append([Q(1),Q(1)]) and basis.append([Q(1),Q(1)+Q(1,scale)]),'independent close rows')
    coordinates=basis.coordinates([Q(0),Q(1)])
    need(coordinates==[-scale,scale] and max(map(height,coordinates))==1025,'minor denominator amplification')
    rng=random.Random(5343)
    coefficients=['0','1','-1','2/3','-5/7',str(2**80+1),'1/'+str(2**80+7)]
    for index in range(12 if small else 80):
        roles=('x','h','y');steps=[]
        for _ in range(9):
            dst=rng.choice(roles);typ=rng.randrange(3)
            if typ==0:steps.append(linear(dst,[(rng.choice(roles),rng.choice(coefficients)) for j in range(3)]))
            elif typ==1:steps.append(apply(rng.choice(('A','B')),rng.choice((-1,1)),dst))
            else:steps.append(query(dst,rng.choice(roles),rng.choice(('A','B')),rng.choice(coefficients),rng.choice((-1,1))))
        if index%3==0:right=steps+[apply('A',-1,'h'),apply('A',1,'h')]
        else:right=steps[:-1]
        inspect('random-'+str(index),program(steps,right,roles))
    stages=8 if small else 64;steps=[]
    for _ in range(stages):
        steps.extend([linear('h',[('x','1/3')]),apply(),query(src='h',a='B',c='2/5')])
    _,_,stress=inspect('weighted-exponential-word-stress',program(steps+[apply('C',-1),apply('C')],steps,
                                  roles=('x','h'),operators=('A','B','C')),'equal',False)
    stress['unexpanded_x_endpoint_words']=str(2**stages)
    controls=0
    for scalar in ('1e200','0e1000000000','0.125'):
        reject(lambda:bounds(program([linear('x',[('x',scalar)])])));controls+=1
    p=program([apply()]);p['field']=2;reject(lambda:bounds(p));controls+=1
    p=program([query(c='1/0')]);reject(lambda:bounds(p));controls+=1
    p=program([query(c=True)]);reject(lambda:bounds(p));controls+=1
    p,cert,r=inspect('size-contract-control',program([apply()]),'different')
    bad=deepcopy(cert);bad['word']=['A']*r['bounds']['states'];reject(lambda:check_size(r['bounds'],bad));controls+=1
    bad=deepcopy(cert);bad['coefficient']=str(1<<r['bounds']['coefficient_bits']);reject(lambda:check_size(r['bounds'],bad));controls+=1
    p,cert,r=inspect('positive-size-control',program([apply(),apply(direction=-1)]),'equal')
    bad=deepcopy(cert);bad['initial'][0][0]=str(1<<r['bounds']['minor_bits']);reject(lambda:check_size(r['bounds'],bad));controls+=1
    return dict(status='PASS',programs=len(rows),equal=sum(r['checked']['verdict']=='equal' for r in rows),
                different=sum(r['checked']['verdict']=='different' for r in rows),word_oracle_cases=word_checks,
                exact_matrix_witnesses=dense,controls=controls,minor_amplification_bits=1025,cases=rows)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--small',action='store_true');ap.add_argument('--write-result',action='store_true');a=ap.parse_args();r=run(a.small)
    if not a.small:
        if a.write_result:(ROOT/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n')
        else:need(r==json.loads((ROOT/'RESULT.json').read_text()),'receipt differs')
    print(json.dumps({k:v for k,v in r.items() if k!='cases'},sort_keys=True));print('PASS_INVERSE_CERTIFICATE_BIT_BOUNDS')


if __name__=='__main__':main()
