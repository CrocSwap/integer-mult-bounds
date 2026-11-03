"""Verify the complete-source zero fiber, scoped optimum and its limits."""

import copy
import gzip
import hashlib
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from fiber import (census_forward,census_by_field,certify,decode_family,encode_family,
                   need,replay_zero_operands,scalar_tape)


def check_source(data,expected):
    need(hashlib.sha256(data).hexdigest()==expected,'source byte mismatch')


def bits_for(count,mode):
    data=bytearray((count+7)//8)
    for j in range(count):
        if mode==0:
            bit=0
        elif mode==1:
            bit=1
        else:
            bit=hashlib.sha256(f'family-label:{mode}:{j}'.encode()).digest()[0]&1
        data[j//8]|=bit << (j%8)
    return bytes(data)


def finite(word,cohort):
    cases=[];local_codes=0
    for n,modes in [(1,range(16)),(4,(0,1)),(512,(0,1))]:
        patterns=(0,1,2) if n==1 else (2,)
        for mode in modes:
            tape=scalar_tape(word,mode);coins=[tape[r['event']] for r in cohort]
            for pattern in patterns:
                code=bits_for(2*n*len(cohort),pattern+mode*3 if pattern==2 else pattern)
                inputs=decode_family(word,cohort,n,coins,code)
                need(encode_family(word,cohort,n,coins,inputs)==code,'packed family bijection')
                need(max(abs(v) for row in inputs for v in row)<=1,'bounded entrance coordinates')
                record,stats=replay_zero_operands(word,inputs,tape)
                record=dict(record)
                decoded=[]
                for item in cohort:
                    decoded.extend(record[item['event']])
                need(all(v in (0,1) for v in decoded),'literal residues are the family label')
                need(all(v==((code[j//8] >> (j%8)) & 1) for j,v in enumerate(decoded)),
                     'all independent bits occur in the existing division record')
                for event,values in record.items():
                    if event not in {r['event'] for r in cohort}:
                        need(all(v==tape[event] for v in values),'other residues depend only on the fixed seed')
                cases.append({'complex_coordinates':n,'seed_fixture':mode,'label_fixture':pattern,
                              'label_sha256':hashlib.sha256(code).hexdigest(),**stats})
    # One local enumeration checks every coin and bit, including both scale signs.
    for sign in (-1,1):
        for u in (0,1):
            recovered=[]
            for bit in (0,1):
                x=sign*(bit-u);y,rem=divmod(sign*x+u,2)
                need(y==0 and rem==bit and sign*(2*y+rem-u)==x,'all half fiber endpoints')
                recovered.append(x);local_codes+=1
            need(len(set(recovered))==2,'distinct bounded inputs')
    # Every individual label position changes a legal input without changing the endpoint.
    coins=[j%2 for j in range(len(cohort))];base=bytes((2*len(cohort)+7)//8)
    baseline=decode_family(word,cohort,1,coins,base)
    for j in range(2*len(cohort)):
        bit=bytearray(base);bit[j//8]|=1 << (j%8)
        other=decode_family(word,cohort,1,coins,bytes(bit))
        need(other!=baseline and encode_family(word,cohort,1,coins,other)==bytes(bit),'retained-bit witness')
    # A fixed input pair, independent of the seed, collides on a probability-1/2 cylinder.
    tape=scalar_tape(word,0)
    single=[[0]*2 for _ in range(word['public'])];single[205][0]=1
    need(word['program'][2]==['SCALE',205,'1/2',3] and tape[2]==0,'fixed first-half cylinder')
    _,single_stats=replay_zero_operands(word,single,tape)
    controls=0
    altered=copy.deepcopy(word)
    altered['program'].insert(1,['ADD',778,205,'1',3])
    try:
        certify(altered,cohort)
    except ValueError:
        controls+=1
    else:
        raise ValueError('prior read was accepted')
    _,changed=census_forward(altered)
    need(len(changed)==len(cohort)-1 and 205 not in {r['field'] for r in changed},'first access differs from first write')
    controls+=1
    for u in (0,1):
        legal=[bit for bit in (0,1) if (bit-u)%2==0]
        need(legal==[u],'even entrance grid removes the displayed fiber')
    controls+=1
    # A prior read distinguishes the two inputs in this complete tiny caller.
    need([(x//2,x) for x in (0,1)]==[(0,0),(0,1)],'prior-read countermodel')
    controls+=1
    # A biased zero map moves the common endpoint; it does not restore lost information.
    need([(x//2,1) for x in (0,1)]==[(0,1),(0,1)],'zero-output versus common-fiber distinction')
    controls+=1
    code=bytearray(base);code[-1]|=128
    try:
        decode_family(word,cohort,1,coins,bytes(code))
    except ValueError:
        controls+=1
    else:
        raise ValueError('nonzero padding accepted')
    try:
        decode_family(word,cohort,1,coins,base[:-1])
    except ValueError:
        controls+=1
    else:
        raise ValueError('truncated label accepted')
    bad=copy.deepcopy(baseline);bad[0][0]=1
    try:
        encode_family(word,cohort,1,coins,bad)
    except ValueError:
        controls+=1
    else:
        raise ValueError('input outside the named family accepted')
    wrong=coins.copy();wrong[0]^=1
    need(decode_family(word,cohort,1,wrong,base)!=baseline,'wrong retained seed changes the original input')
    controls+=1
    return {'full_source_replays':len(cases)+1,'literal_event_executions':(len(cases)+1)*len(word['program']),
            'cases':cases,'all_half_fiber_endpoints':local_codes,'individual_retained_bit_witnesses':2*len(cohort),
            'fixed_input_pair_cylinder_probability':'1/2','fixed_pair_replay':single_stats,
            'semantic_and_domain_controls':controls}


def run(generate):
    row=next(x for x in json.loads((HERE/'SOURCES.json').read_text())['files'] if x['usage']=='input')
    data=(ROOT/row['path']).read_bytes();check_source(data,row['sha256'])
    try:
        check_source(data+b'!',row['sha256'])
    except ValueError:
        corrupted=1
    else:
        raise ValueError('source corruption accepted')
    word=json.loads(gzip.decompress(data))
    first,cohort=census_forward(word);other,second=census_by_field(word)
    need(first==other and cohort==second and len(first)==770,'independent complete first-access census')
    need(len(cohort)==43,'source cohort count')
    causal=certify(word,cohort);checks=finite(word,cohort)
    result={'schema_version':1,'status':'PASS_SELECTED_CALLER_ZERO_FIBER',
            'base_commit':'7c49fe32c55de02c2c873655c804b16e4c3fef0a','source_sha256':row['sha256'],
            'cohort':cohort,'cohort_fields':len(cohort),'independent_labels_per_complex_coordinate':2*len(cohort),
            'width_one_complex_coordinates':512,'width_one_retained_bits':512*2*len(cohort),
            'width_one_packed_bytes':512*2*len(cohort)//8,
            'first_native_event':next(j for j,e in enumerate(word['program']) if e[0]=='MOVE'),
            'cohort_after_first_native':[x for x in cohort if x['event']>=9896],
            'causal_proof':causal,'finite_checks':checks,'source_corruption_controls':corrupted,
            'global_minimum_claimed':False,'selected_frontier_changed':False}
    if generate:
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        need(result==json.loads((HERE/'RESULT.json').read_text()),'committed exact receipt')
    print('PASS_SELECTED_CALLER_ZERO_FIBER')
    print(json.dumps({'cohort_fields':len(cohort),'retained_bits_per_coordinate':2*len(cohort),
                      'width_one_bits':result['width_one_retained_bits'],'causal':causal,
                      'full_source_replays':checks['full_source_replays'],
                      'literal_event_executions':checks['literal_event_executions'],
                      'controls':checks['semantic_and_domain_controls'],'source_corruption_controls':corrupted},sort_keys=True))


if __name__=='__main__':
    need(sys.argv[1:] in ([],['--generate']),'verifier arguments')
    run(bool(sys.argv[1:]))
