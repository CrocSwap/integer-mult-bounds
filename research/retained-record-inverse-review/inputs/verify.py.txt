"""Verify the source join, all signed transfers, moments and retained inverse."""

import gzip
import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from sampler import execute, native, need, pack_remainders, pair, quantized, restore_division, route
from ledger import analyze, reverse, tail_certificate


def check_source(data, expected):
    need(hashlib.sha256(data).hexdigest()==expected,'source hash mismatch')


def cpair(x,y):
    a,b=x;c,d=y
    return ((a-b+c+d)/2,(a+b+d-c)/2),((a+b+c-d)/2,(b-a+c+d)/2)


def finite(word):
    pairs=0
    for a,b,c,d in itertools.product(range(-3,4),repeat=4):
        x,y=(a,b),(c,d)
        actual=[pair(x,y,s) for s in (-1,1)]
        for s,out in zip((-1,1),actual):
            need(pair(*out,s,True)==(x,y),'pair exact inverse')
        target=cpair(tuple(map(Q,x)),tuple(map(Q,y)))
        need(all(Q(actual[0][j][k]+actual[1][j][k],2)==target[j][k]
                 for j in range(2) for k in range(2)),'pair exact mean')
        mse=sum((Q(out[j][k])-target[j][k])**2 for out in actual for j in range(2) for k in range(2))/2
        need(mse==((a+b+c+d)%2),'pair conditional second moment')
        pairs+=1
    wide=0
    for bit in (0,1,17,64,257,1024):
        for signs in itertools.product((-1,1),repeat=2):
            x=(signs[0]*(1 << bit)+1,-(1 << bit));y=(signs[1]*(1 << bit),3)
            for s in (-1,1):
                need(pair(*pair(x,y,s),s,True)==(x,y),'unbounded integer pair')
                wide+=1
    scalars=0
    coefficients=sorted({Q(e[-2]) for e in word['program'] if e[0] in {'ADD','SCALE'}})
    for q in coefficients:
        for v in range(-32,33):
            outputs=[quantized([(v,-v)],q,u)[0] for u in range(q.denominator)]
            need(sum(x for x,y in outputs)==q.numerator*v,'scalar exact mean real')
            need(sum(y for x,y in outputs)==-q.numerator*v,'scalar exact mean imaginary')
            need(sum((Q(x)-q*v)**2+(Q(y)+q*v)**2 for x,y in outputs)/q.denominator<=Q(1,2),'scalar variance')
            scalars+=1
    divisions=0
    for q in sorted({Q(e[2]) for e in word['program'] if e[0]=='SCALE' and Q(e[2]).denominator>1}):
        for v in range(-128,129):
            for u in range(q.denominator):
                original=[(v,1-v)]
                packed=pack_remainders(original,q,u)
                need(restore_division(quantized(original,q,u),q,u,packed)==original,'division exact residue inverse')
                divisions+=1
    # Exhaust every fresh seed of a mixed two-pair/scalar trajectory.
    x,y=(Q(1),Q(1)),(Q(2),Q(-1))
    a,b=cpair(x,y);a=tuple(v-Q(3,4)*w for v,w in zip(a,b));b=tuple(v/2 for v in b)
    expected=cpair(a,b)
    totals=[[Q(0),Q(0)],[Q(0),Q(0)]]
    cases=0
    for s,u,v,t in itertools.product((-1,1),range(4),range(2),(-1,1)):
        a,b=pair((1,1),(2,-1),s)
        inc=quantized([b],Q(-3,4),u)[0];a=tuple(x+y for x,y in zip(a,inc))
        rem=pack_remainders([b],Q(1,2),v);b=quantized([b],Q(1,2),v)[0]
        out=pair(a,b,t)
        for j in range(2):
            for k in range(2):totals[j][k]+=out[j][k]
        a,b=pair(*out,t,True);b=restore_division([b],Q(1,2),v,rem)[0]
        inc=quantized([b],Q(-3,4),u)[0];a=tuple(x-y for x,y in zip(a,inc))
        need(pair(a,b,s,True)==((1,1),(2,-1)),'mixed inverse')
        cases+=1
    need(all(totals[j][k]/cases==expected[j][k] for j in range(2) for k in range(2)),'mixed exact mean')
    controls=0
    try:
        pair((0,0),(1,0),True)
    except ValueError:
        controls+=1
    else:
        raise ValueError('boolean pair seed accepted')
    original=[(1,0)]
    q=Q(1,2)
    need(quantized(original,q,0)==quantized([(0,0)],q,0),'lost division residue collision')
    controls+=1
    need(pair(*pair((0,0),(1,0),1),-1,True)!=((0,0),(1,0)),'wrong inverse seed witness')
    controls+=1
    reused=Q(0);fresh=Q(0)
    for u in range(2):
        x=quantized([(1,0)],q,u)[0][0]
        reused+=Q(quantized([(x,0)],q,u)[0][0])-Q(x,2)
        for v in range(2):fresh+=Q(quantized([(x,0)],q,v)[0][0])-Q(x,2)
    need(reused/2==Q(1,4) and fresh==0,'adaptive reused-seed bias')
    controls+=1
    toy={'program':[['MOVE',0,0,1,False],['COPY',1,0,'1',1],['ADD',0,1,'-1',1],['CLEAR',1,1]]}
    weights=[(1,0),(0,0),(0,0),(0,0)]
    _,row=reverse(toy,weights,3,0)
    need(not row,'signed COPY cancellation')
    _,row=reverse(toy,weights,4,1)
    need(not row,'CLEAR kills later error')
    _,row=reverse(toy,weights,2,1)
    need(row=={0:Q(1)},'CLEAR does not erase earlier prefix excursion')
    controls+=3
    return {'pair_inputs':pairs,'wide_pair_roundtrips':wide,'scalar_contexts':scalars,
            'division_roundtrips':divisions,'mixed_seed_trajectories':cases,'semantic_controls':controls}


def run(generate=False):
    corrupt=0
    for item in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if item['usage']=='input':
            data=(ROOT/item['path']).read_bytes();check_source(data,item['sha256'])
            try:
                check_source(data+b'!',item['sha256'])
            except ValueError:
                corrupt+=1
            else:
                raise ValueError('corrupt source accepted')
    word=json.loads(gzip.decompress((ROOT/'research/p104-helper470-twin-rung-removal/WORD.json.gz').read_bytes()))
    with tempfile.TemporaryDirectory() as tmp:
        folder=Path(tmp)
        subprocess.run([sys.executable,'-I','-Werror','-B',str(HERE/'produce.py'),tmp],check=True,timeout=900)
        sources=json.loads((folder/'source-summary.json').read_text());bound=json.loads((folder/'native.json').read_text())
        ledger,weights=analyze(word,bound['ranks']);ledger['tail']=tail_certificate(ledger['prefix_peaks'])
        checks=finite(word)
        initial={r:[(((r*17+j*29)%23)-11,((r*31+j*7)%19)-9) for j in range(512)] for r in range(word['public'])}
        def seeds(j,k,d):
            return int.from_bytes(hashlib.sha256(f'selected-absolute-fixture:{j}:{k}'.encode()).digest()[:8],'little')%d
        output,caller=execute(word,bound['recipes'],initial,seeds)
        need(caller['native_seed_bits']==ledger['native_seed_bits_per_tensor_axis'] and
             caller['scalar_seed_bits']==ledger['scalar_seed_bits'] and
             caller['division_residue_bits']==512*ledger['division_residue_bits_per_complex_coordinate'],'exact caller budget')
        (folder/'fixture.json').write_text(json.dumps({'initial':initial,'output':output},separators=(',',':')))
        key,rec=next((key,r) for key,r in bound['recipes'].items() if r['rank']==8)
        values=[((j%11)-5,(j%7)-3) for j in range(512**2)]
        bits=[1 if k%3 else -1 for k in range(16)]
        routes=route(rec['left']),route(rec['right'])
        transformed=native(values,routes,8,bits,2)
        need(native(transformed,routes,8,bits,2,True)==values,'rank-eight full tensor inverse')
        tensor={'coordinates':len(values),'active_stages':16,
                'output_sha256':hashlib.sha256(repr(transformed).encode()).hexdigest()}
        exact_input=[(a << 16,b << 16) for a,b in values]
        exact_output=native(exact_input,routes,8,bits,2)
        need(native(exact_input,routes,8,[-v for v in bits],2)==exact_output,'exact tensor seed independence')
        tensor['exact_output_sha256']=hashlib.sha256(repr(exact_output).encode()).hexdigest()
        (folder/'tensor-fixture.json').write_text(json.dumps({'edge':list(map(int,key.split(','))),
            'initial':exact_input,'output':exact_output},separators=(',',':')))
        subprocess.run([sys.executable,'-I','-Werror','-B',str(HERE/'endpoint.py'),tmp],check=True,timeout=180)
        endpoint=json.loads((folder/'endpoint.json').read_text())
        for r,err in enumerate(endpoint['squared_errors']):
            am,ass=ledger['final_scores'][r][2:]
            need(Q(err)<=256*(am+2*ass)**2,'decoded numerical endpoint bound')
    result={'schema_version':1,'status':'PASS_SELECTED_ABSOLUTE_STOCHASTIC_CALLER',
            'base_commit':'7c49fe32c55de02c2c873655c804b16e4c3fef0a','source':sources,
            'ledger':ledger,'finite':checks,'caller':caller,'endpoint':endpoint,'tensor':tensor,
            'source_corruption_controls':corrupt,'selected_frontier_changed':False}
    result=json.loads(json.dumps(result,default=str))
    if generate:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result==json.loads((HERE/'RESULT.json').read_text()),'committed exact receipt')
    print('PASS_SELECTED_ABSOLUTE_STOCHASTIC_CALLER')
    print(json.dumps({k:result[k] for k in ('source','finite','caller','tensor','source_corruption_controls')},sort_keys=True))


if __name__=='__main__':
    need(sys.argv[1:] in ([],['--generate']), 'verify arguments')
    run(bool(sys.argv[1:]))
