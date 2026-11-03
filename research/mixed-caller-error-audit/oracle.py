#!/usr/bin/env python3
"""Independent formal-C4 polynomial audit; author programs remain inert bytes.

Gaussian Fraction coefficients retain eighteen distinct stage variables.
Small operator blocks multiply on the left for prefixes and right for suffixes.
Prepared by ToikY with OpenAI Codex assistance; predecessor credit retained.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST_SHA = '8ef153f281be3784f7dacffc5f02b9e04406344ec7b759fa1b4adc22bb48f591'
N, D = 34, 18
ZERO_KEY = (0,)*(D+1)
PINS = {
 'inputs/CONTROLLER.json': (38228,'4aa7ee4e1bc4853200cf97474695054057cc354bc1778f35b6554a365aac412c','4f7d7a2f13b13966b10c7b583d28d1bed210364c'),
 'inputs/AUTHOR-RESULT.json': (2317,'ef032148e01035f1dd9d3fa7966921f44b66fdb21d512d16cea9c9d783d120ee','bd439dc71edc92d017170375779834e4cf326e8a'),
 'inputs/AUTHOR-PROOF.md': (6244,'fb9f349fc516a619c26fad9869d6cc31c29fa7da673e34a58eeedc91e2fdb15c','91635ddc9ceccee3daff0c07d055f935164fd254'),
 'inputs/AUTHOR-bounds.py': (4022,'4fb6222b4c88ebc603e5f3a2b1310670211d033402fbec010dc6bace2973dc17','c17e99605d19849d3898039753956ed870705380'),
 'inputs/AUTHOR-verify.py': (6480,'a5097813c4e425936642cf1e922ad27ab13828deccbcaec9802b99c6a0ded2d9','caed52ccf26dc946c17450f98da54320280fa87a'),
}
MATH_KEYS = ('prefix_row_envelopes','suffix_row_envelopes','errors','prefix','maxima',
             'common_error','prefix_cell_envelope_sha256','suffix_cell_envelope_sha256')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def decode(raw):
    def unique(items):
        out = {}
        for key,value in items:
            require(key not in out,'duplicate JSON key')
            out[key] = value
        return out
    def bad(value):
        raise ValueError('nonfinite JSON: '+value)
    def floating(value):
        number = float(value)
        require(math.isfinite(number),'nonfinite JSON number')
        return number
    return json.loads(raw,object_pairs_hook=unique,parse_constant=bad,parse_float=floating)


def read(path):
    with path.open('rb') as handle:
        raw = handle.read(8*1024*1024+1)
    require(len(raw)<=8*1024*1024,'eight-MiB file capacity')
    return raw


def authenticate(raw,manifest):
    require(hashlib.sha256(manifest).hexdigest()==MANIFEST_SHA,'source manifest SHA256')
    require(set(raw)==set(PINS),'five-file source closure')
    for path,(length,digest,blob) in PINS.items():
        value = raw[path]
        require(len(value)==length,'source length: '+path)
        require(hashlib.sha256(value).hexdigest()==digest,'source SHA256: '+path)
        framed = b'blob '+str(len(value)).encode()+b'\0'+value
        require(hashlib.sha1(framed).hexdigest()==blob,'source Git blob: '+path)


def mono(real=1,imag=0,q=0,stages=()):
    powers = tuple(int(k in stages) for k in range(1,D+1))
    value = (F(real),F(imag))
    return {(q%4,)+powers:value} if any(value) else {}


def add(a,b):
    out = dict(a)
    for key,(r,i) in b.items():
        x,y = out.get(key,(F(0),F(0)))
        if x+r or y+i:
            out[key] = (x+r,y+i)
        else:
            out.pop(key,None)
    return out


def multiply(a,b):
    out = {}
    for x,(ar,ai) in a.items():
        for y,(br,bi) in b.items():
            key = ((x[0]+y[0])%4,)+tuple(u+v for u,v in zip(x[1:],y[1:]))
            value = (ar*br-ai*bi,ar*bi+ai*br)
            old = out.get(key,(F(0),F(0)))
            value = (old[0]+value[0],old[1]+value[1])
            if any(value):out[key]=value
            else:out.pop(key,None)
    require(len(out)<=4096,'polynomial term capacity')
    return out


def block(event):
    op = event[0]
    one = mono()
    if op=='ADD':
        _,a,b,c=event
        return [a,b],[(a,a,one),(a,b,mono(F(c))),(b,b,one)]
    if op=='SCALE':
        return [event[1]],[(event[1],event[1],mono(F(event[2])))]
    if op=='SWAP':
        a,b=event[1:]
        return [a,b],[(a,b,one),(b,a,one)]
    if op=='QUERY':
        _,a,b,power=event
        return [a,b],[(a,a,one),(a,b,mono(q=power)),(b,b,one)]
    if op=='LOCAL':
        _,stage,b,a=event
        return [a,b],[(a,a,mono(stages=(stage,))),(a,b,mono(q=-1,stages=(stage,))),(b,b,mono(stages=(stage,)))]
    if op=='Q_POWER':
        return [event[1]],[(event[1],event[1],mono(q=event[2]))]
    if op=='LAMBDA':
        a,sign=event[1:]
        factor=add(mono(F(1,2),F(sign,2)),mono(F(1,2),F(-sign,2),q=2))
        return [a],[(a,a,factor)]
    if op in ('IDLE','IDLE_ONE'):
        roles,stages=(event[1:3],event[3]) if op=='IDLE' else ([event[1]],event[2])
        return roles,[(a,a,mono(stages=stages)) for a in roles]
    raise ValueError('unknown operator')


def identity():
    return [{i:mono()} for i in range(N)]


def left(matrix,roles,entries):
    old = {r:matrix[r] for r in roles}
    for r in roles:
        row = {}
        for a,b,factor in entries:
            if a!=r:continue
            for column,value in old[b].items():
                result=add(row.get(column,{}),multiply(factor,value))
                if result:row[column]=result
                else:row.pop(column,None)
        matrix[r]=row


def right(matrix,roles,entries):
    for row in matrix:
        old = {r:row.get(r,{}) for r in roles}
        for column in roles:
            result = {}
            for a,b,factor in entries:
                if b==column:result=add(result,multiply(old[a],factor))
            if result:row[column]=result
            else:row.pop(column,None)


def characters(poly):
    values = [{} for _ in range(4)]
    units = ((1,0),(0,1),(-1,0),(0,-1))
    for key,(real,imag) in poly.items():
        for character in range(4):
            ar,ai=units[(character*key[0])%4]
            coefficient=(real*ar-imag*ai,real*ai+imag*ar)
            old=values[character].get(key[1:],(F(0),F(0)))
            coefficient=(old[0]+coefficient[0],old[1]+coefficient[1])
            if any(coefficient):values[character][key[1:]]=coefficient
            else:values[character].pop(key[1:],None)
    return values


def cell_bound(poly):
    return max(sum((abs(r)+abs(i) for r,i in value.values()),F(0)) for value in characters(poly))


def envelope(matrix):
    cells = [[F(0) for _ in range(N)] for _ in range(N)]
    for r,row in enumerate(matrix):
        for column,poly in row.items():cells[r][column]=cell_bound(poly)
    return cells,[sum(row,F(0)) for row in cells]


def injection(event,normalizers=True):
    op=event[0]
    if op in ('ADD','SCALE'):return 'scalar',[event[1]],F(1)
    if op=='LAMBDA':return 'scalar',[event[1]] if normalizers else [],F(9,2)
    if op=='LOCAL':return 'local',event[2:4],F(1)
    if op=='QUERY':return 'query',[event[1]],F(1)
    if op in ('IDLE','IDLE_ONE'):return 'idle',event[1:3] if op=='IDLE' else [event[1]],F(1)
    return 'scalar',[],F(0)


def serialize_cells(cells):
    return [[str(value) for value in row] for row in cells]


def endpoint(matrix,diagonal):
    expected=[]
    for power,reserved,*stages in diagonal:
        require(type(power) is int and reserved==0 and len(stages)==D,'literal diagonal grammar')
        require(all(type(value) is int and value>=0 for value in stages),'diagonal stage exponents')
        expected.append({(power%4,)+tuple(stages):(F(1),F(0))})
    require(all(row=={r:expected[r]} for r,row in enumerate(matrix)),'complete formal endpoint')


def tables(word):
    events=word['events']
    prefix_cells,prefix_rows=[],[]
    matrix=identity()
    for t in range(len(events)+1):
        cells,rows=envelope(matrix)
        prefix_cells.append(serialize_cells(cells));prefix_rows.append(list(map(str,rows)))
        if t<len(events):left(matrix,*block(events[t]))
    endpoint(matrix,word['diagonal'])
    suffix_cells,suffix_rows=[None]*(len(events)+1),[None]*(len(events)+1)
    errors={name:[F(0)]*N for name in ('scalar','local','query','idle')}
    lower=[F(0)]*N;signs=[{} for _ in range(N)]
    matrix=identity()
    for boundary in range(len(events),-1,-1):
        cells,rows=envelope(matrix)
        suffix_cells[boundary]=serialize_cells(cells);suffix_rows[boundary]=list(map(str,rows))
        if not boundary:continue
        event=events[boundary-1];name,roles,weight=injection(event)
        for r in range(N):errors[name][r]+=weight*sum((cells[r][c] for c in roles),F(0))
        _,roles,_=injection(event,False)
        for r in range(N):
            choices=[]
            for column in roles:
                real=sum((x for x,y in matrix[r].get(column,{}).values()),F(0))
                imag=sum((y for x,y in matrix[r].get(column,{}).values()),F(0))
                require(not imag,'lower scalar specialization real')
                lower[r]+=abs(real)
                if real:choices.append((column,1 if real>0 else -1))
            if choices:signs[r][boundary-1]=choices
        right(matrix,*block(event))
    return prefix_cells,prefix_rows,suffix_cells,suffix_rows,errors,lower,signs


def lower_forward(events,choices):
    state=[F(0)]*N
    for t,event in enumerate(events):
        roles,entries=block(event)
        old=list(state)
        for r in roles:
            value=F(0)
            for a,b,poly in entries:
                if a==r:value+=sum((x for x,y in poly.values()),F(0))*old[b]
            state[r]=value
        for r,sign in choices.get(t,[]):state[r]+=sign
    return state


def normalizer(sign):
    one=(F(1),F(0));zero=(F(0),F(0));si=(F(0),F(sign))
    a=(F(1,2),F(sign,2));b=(F(1,2),F(-sign,2))
    matrices=[[[one,(F(0),F(-sign))],[zero,one]],[[a,zero],[zero,one]],
              [[one,zero],[zero,(F(1),F(sign))]],[[one,zero],[(F(0),F(-sign)),one]]]
    current=[[one,zero]+[zero]*4,[zero,one]+[zero]*4]
    def cmul(x,y):return (x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
    for step,operator in enumerate(matrices):
        result=[]
        for row in operator:
            values=[]
            for column in range(6):
                products=[cmul(row[k],current[k][column]) for k in range(2)]
                values.append(tuple(sum((v[j] for v in products),F(0)) for j in range(2)))
            result.append(values)
        current=result
        updated=0 if step<2 else 1
        current[updated][2+step]=one
    require([row[:2] for row in current]==[[a,b],[b,a]],'literal normalizer input columns')
    squared=[sum((real*real+imag*imag for real,imag in [current[0][2+j],current[1][2+j]]),F(0)) for j in range(4)]
    require(squared==[F(1),F(2),F(1),F(1)],'all four normalizer error columns')
    return {'sign':sign,'input_columns':[[list(map(str,z)) for z in row[:2]] for row in current],
            'error_columns':[[list(map(str,z)) for z in row[2:]] for row in current],
            'squared_error_norms':list(map(str,squared))}


def controls(raw,manifest):
    even=add(mono(F(1,2)),mono(F(1,2),q=2));odd=add(mono(F(1,2)),mono(F(-1,2),q=2))
    require(cell_bound(even)+cell_bound(odd)==2,'cell maxima before row sum')
    stage=add(mono(stages=(1,)),mono(-1,stages=(2,)))
    require(cell_bound(stage)==2 and sum(x for x,y in stage.values())==0,'stage specialization not upper bound')
    require(add(mono(q=4),mono(-1))=={},'central C4 reduction')
    changed=dict(raw);name='inputs/CONTROLLER.json';changed[name]=b'X'+changed[name][1:]
    try:authenticate(changed,manifest)
    except ValueError as error:require('SHA256' in str(error),'source mutation guard')
    else:raise ValueError('source mutation accepted')
    return {'cellwise_character_maximum_before_row_sum':True,'stage_aliasing_rejected':True,
            'central_C4_relation':True,'source_byte_mutation_rejected':True}


def compute():
    manifest=read(ROOT/'SOURCE-PINS.json');raw={path:read(ROOT/path) for path in PINS}
    authenticate(raw,manifest)
    word=decode(raw['inputs/CONTROLLER.json'])
    require(type(word.get('roles')) is int and word['roles']==N and type(word.get('stages')) is int and word['stages']==D,'typed source dimensions')
    require(type(word.get('events')) is list and len(word['events'])==570,'570 source events')
    pc,pr,sc,sr,errors,lower,signs=tables(word)
    prefix=max((F(value),t,r) for t,row in enumerate(pr) for r,value in enumerate(row))
    output=max(range(N),key=lambda r:(lower[r],-r));actual=lower_forward(word['events'],signs[output])
    require(actual[output]==lower[output],'literal lower witness forward/reverse agreement')
    digest=lambda value:hashlib.sha256((json.dumps(value,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
    mathematical={'prefix_row_envelopes':pr,'suffix_row_envelopes':sr,
       'prefix_cell_envelope_sha256':digest(pc),'suffix_cell_envelope_sha256':digest(sc),
       'errors':{key:list(map(str,values)) for key,values in errors.items()},
       'maxima':{key:str(max(values)) for key,values in errors.items()},
       'prefix':[str(prefix[0]),prefix[1],prefix[2]],
       'common_error':str(max(sum(values[r] for values in errors.values()) for r in range(N)))}
    author=decode(raw['inputs/AUTHOR-RESULT.json'])
    require(all(canonical(mathematical[key])==canonical(author[key]) for key in ('prefix','errors','maxima','common_error')),'author quantitative arrays agree')
    require(str(lower[output])==author['lower_witness']['amplification'] and output==author['lower_witness']['output'],'author lower witness agreement')
    require(256<lower[output]<=F(mathematical['common_error'])<512,'uniform guard separation')
    return {'schema_version':1,'source_manifest_sha256':MANIFEST_SHA,'method':'Formal C4 Gaussian-Fraction polynomial blocks; distinct18-stage exponents; no author or primary executable import',
       'mathematical':mathematical,'normalizers':[normalizer(1),normalizer(-1)],
       'lower_witness':{'output':output,'amplification':str(lower[output]),'final_fields':list(map(str,actual)),
                       'injections':[[t,choices] for t,choices in sorted(signs[output].items())]},
       'controls':controls(raw,manifest),'limits':['Abstract field-Hilbert operator/error contract only; scalar Q=D=1 specialization used only for the explicit lower witness.',
       'All571prefix/suffix row envelopes and complete cell digests are derived independently; no physical rounding, tape, supplier,kappa or frontier admission.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--emit',action='store_true');args=parser.parse_args()
    result=compute()
    if args.emit:print(canonical(result))
    else:
        require(canonical(decode(read(ROOT/'ORACLE.json')))==canonical(result),'strict oracle receipt drift')
        primary=decode(read(ROOT/'RESULT.json'))
        primary=primary.get('mathematical',primary)
        require(all(canonical(primary[key])==canonical(result['mathematical'][key]) for key in MATH_KEYS),'independent primary mathematical comparison')
        print('PASS_INDEPENDENT_MIXED_CALLER_ERROR_AUDIT')


if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError) as error:
        print('FAIL: '+str(error),file=sys.stderr);sys.exit(1)
