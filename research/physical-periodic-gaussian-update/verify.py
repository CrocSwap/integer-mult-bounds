#!/usr/bin/env python3
"""Actual original coefficients, complete local-tape update and fail-closed receipt."""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys
import time
import machine as m
P=Path(__file__).resolve().parent
ROOT=P.parents[1]

def need(v,label):
    if not v:raise ValueError(label)

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module;spec.loader.exec_module(module);return module

def authenticate():
    document=json.loads((P/'SOURCES.json').read_text());hashes={}
    for row in document['files']:
        if row['usage']=='input':
            raw=(ROOT/row['path']).read_bytes();h=hashlib.sha256(raw).hexdigest()
            need(h==row['sha256'],'source SHA '+row['path']);hashes[row['path']]=h
    for row in document['external_sources']:
        raw=(P/row['vendored_path']).read_bytes();h=hashlib.sha256(raw).hexdigest()
        need(h==row['sha256'],'captured source SHA');hashes[row['vendored_path']]=h
    return hashes

def tape(meter,values,bits):
    # Fixture serialization only: not called by measured update.
    t=m.Tape(meter,len(values)*bits)
    t.cells[1:-1]=bytes((v>>j)&1 for v in values for j in range(bits));return t

def decode(t):
    value=sum(b<<i for i,b in enumerate(t.cells[1:-1]));return value-(1<<80) if value>>79 else value

def difference(after,before):return {k:after[k]-before[k] for k in before}

def rejection(fn,label):
    try:fn()
    except (ValueError,TypeError):return label
    raise ValueError('control accepted '+label)

def arithmetic():
    rng=random.Random(71);cases=0;rejected=[]
    for _ in range(120):
        met=m.Meter();x=rng.randrange(-(1<<37),1<<37);v=rng.randrange(1<<33);z=rng.randrange(-(1<<73),1<<73)
        c=tape(met,[v],33);y=tape(met,[x],80);a=tape(met,[z],80);r=m.Tape(met,80)
        m.muladd(c,y,a);need(decode(a)==z+x*v,'exact signed multiply-add')
        m.rounded(a,r);q=trunc(z+x*v);need(decode(r)==q,'signed truncation')
        u=tape(met,[x],80);out=m.Tape(met,80);m.subtract_emit(u,r,out);out.rewind()
        need(decode(out)==x-q,'signed subtraction');need(all(t.head==1 for t in (c,y,a,r,out)),'word heads');cases+=1
    # Actual rounding helper mutation: omit negative discarded-bit correction.
    text=(P/'machine.py').read_text().replace('if negative and discard:', 'if False:')
    env={'__name__':'rounding_mutant'};exec(compile(text,'rounding_mutant','exec'),env)
    met=m.Meter();a=tape(met,[-(1<<33)-1],80);r=m.Tape(met,80);env['rounded'](a,r)
    need(decode(r)!=-1,'negative-rounding mutant discriminator');rejected.append('missing_negative_truncation_correction')
    return {'exact_signed_cases':cases,'rejected':rejected}

def trunc(n):return (-1 if n<0 else 1)*(abs(n)//(1<<33))

def source_packet(cached):
    packet=json.loads((P/'COEFFICIENTS.json').read_text())
    if not cached:
        sys.path.insert(0,str(ROOT/'research/rational-unitary-fft'))
        from gaussian_reference import Reference
        from gaussian import INTERVALS
        old=load('original_periodic_service',P/'inputs/service.py')
        ref=Reference({INTERVALS:(ROOT/INTERVALS).read_bytes()},384,1,2,4,18,320);plan=old.prepare(ref)
        actual={'source_service_sha256':hashlib.sha256((P/'inputs/service.py').read_bytes()).hexdigest(),'plan':plan.record(),'rows':plan.rows}
        need(canonical(packet)==canonical(actual),'all original coefficient preparation')
    need(packet['plan']['reference']=='4001280a290db7fe1afbbbed80704821796da86c3de8f86516b8debaf099591c','unchanged Reference')
    need((packet['plan']['bits'],packet['plan']['steps'],packet['plan']['rows'])==(33,276,385),'source precision/iteration/rows')
    rows=packet['rows'];need(len(rows)==385 and rows[192]==[],'whole period and hole')
    for i,row in enumerate(rows):
        if i==192:continue
        j=i-(i>192);columns=[]
        for h in (-4,-3,-2,-1,1,2,3,4):
            k=(j+h)%384;columns.append(k+(k>=192))
        need([c for c,v in row]==columns,'exact periodic source support')
        need(all(type(v)is int and 0<=v<1<<33 for c,v in row),'unsigned coefficient extent')
    return packet

def fixture():
    s=1<<33;u=[(((i*17)%65-32)*s//64,((i*29)%65-32)*s//64) for i in range(385)]
    u[0]=(s//2,s//2);u[-1]=(-s,0);u[192]=(s//4,-s//2)
    return tuple(u),tuple((8*a,8*b) for a,b in u)

def oracle(rows,u,y):
    return tuple(tuple(u[i][k]-trunc(sum(v*y[c][k] for c,v in row)) for k in range(2)) for i,row in enumerate(rows))

def check_output(output,expected):
    need(bytes(output.cells[1:-1])==bytes((v>>j)&1 for pair in expected for v in pair for j in range(80)),'whole770-component endpoint')

def run_case(owner,coeff,u,y,expected):
    meter=owner.m;ut=tape(meter,[v for z in u for v in z],80);yt=tape(meter,[v for z in y for v in z],80)
    ports=(coeff,ut,yt,owner.output,*owner.private());ids=[id(t.cells) for t in ports];before=[bytes(t.cells) for t in (coeff,ut,yt)]
    baseline=meter.record();output=owner.run(coeff,ut,yt);bill=difference(meter.record(),baseline)
    check_output(output,expected);need(ids==[id(t.cells) for t in ports],'backing identities')
    need(before==[bytes(t.cells) for t in (coeff,ut,yt)],'borrowed inputs unchanged')
    need(all(t.head==1 for t in ports),'all canonical heads')
    need(all(all(v==m.BLANK for v in t.cells[1:-1]) for t in owner.private()),'retained scratch erased')
    rejected=rejection(lambda:owner.run(coeff,ut,yt),'pending output')
    # Pending remains a guard even if a caller moves to the end of its output.
    owner.output.skip(385*160);rejection(lambda:owner.run(coeff,ut,yt),'pending output at end')
    owner.output.rewind();before_consume=meter.record();owner.consume();consume=difference(meter.record(),before_consume)
    need(owner.output.head==1 and all(v==m.BLANK for v in owner.output.cells[1:-1]),'physical output consumption')
    return bill,consume,rejected

def physical(packet):
    rows=packet['rows'];u,y=fixture();expected=oracle(rows,u,y);meter=m.Meter()
    coeff=tape(meter,[v for row in rows for c,v in row],33);base=meter.record();owner=m.Update(meter);construction=difference(meter.record(),base)
    bill,consume,_=run_case(owner,coeff,u,y,expected)
    zero=((0,0),)*385;zero_bill,zero_consume,_=run_case(owner,coeff,zero,zero,zero)
    need(consume==zero_consume,'fixed complete consumption')
    corrections=sum(sum(v*y[c][k] for c,v in row)<0 and sum(v*y[c][k] for c,v in row)%(1<<33)!=0 for row in rows for k in range(2))
    delta={'reads':161,'writes':80,'moves':162,'control':324}
    need(bill=={k:zero_bill[k]+corrections*delta[k] for k in bill},'complete data-dependent correction invoice')
    upper={k:zero_bill[k]+770*delta[k] for k in bill}
    early=tuple(tuple(u[i][k]-sum(trunc(v*y[c][k]) for c,v in row) for k in range(2)) for i,row in enumerate(rows))
    need(early!=expected,'per-offset truncation changes endpoint')
    # One actual cyclic-control mutation must fail on original full-size ports.
    env={'__name__':'cyclic_mutant'};text=(P/'machine.py').read_text().replace('if j==383:current.rewind()', 'if j==383:pass')
    exec(compile(text,'cyclic_mutant','exec'),env);mutant=env['Update'](meter)
    ut=tape(meter,[v for z in u for v in z],80);yt=tape(meter,[v for z in y for v in z],80)
    rejection(lambda:mutant.run(coeff,ut,yt),'missing cyclic return')
    # Aliases reject before any measured cell action, including metadata inspection.
    met=m.Meter();test=m.Update(met);ct=tape(met,[0]*3072,33);input_t=tape(met,[0]*770,80);before=met.record()
    rejection(lambda:test.run(ct,input_t,input_t),'aliased current/input');need(met.record()==before,'alias preflight before reads')
    return dict(construction=construction,update=bill,zero_update=zero_bill,output_consume=consume,
                universal_update_upper=upper,negative_discard_corrections=corrections,
                per_offset_rounding_different_rows=sum(a!=b for a,b in zip(early,expected)),
                input_sha256=digest((u,y)),output_sha256=digest(expected),
                private_retained_cells=sum(len(t.cells) for t in owner.private()),output_cells=len(owner.output.cells),
                rejected=['missing_cyclic_return','aliased_current_input','pending_output','pending_output_at_end'])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',type=Path);parser.add_argument('--cached',action='store_true');args=parser.parse_args()
    start=time.monotonic();sources=authenticate();frozen=None
    if args.record is None:
        frozen=json.loads((P/'RESULT.json').read_text())
        for section in ('construction','update','zero_update','output_consume','universal_update_upper'):
            need(all(type(v)is int for v in frozen['physical'][section].values()),'typed integer invoice')
    tree=ast.parse((P/'machine.py').read_text());local_count=sum(len({a.arg for a in f.args.args}|{x.id for x in ast.walk(f) if isinstance(x,ast.Name) and isinstance(x.ctx,ast.Store)}) for f in ast.walk(tree) if isinstance(f,ast.FunctionDef))
    need(local_count<=96,'fixed controller shape budget')
    controls=arithmetic();packet=source_packet(args.cached);result={'status':'PASS_PHYSICAL_PERIODIC_UPDATE','controls':controls,'physical':physical(packet),
        'static':{'machine_source_bytes':len((P/'machine.py').read_bytes()),'source_local_names':local_count,'fixed_controller_scalar_bits_upper':4096,'fixed_constant_bits_upper':1024,'program_location_bits':32,'fixed_role_reference_bits':40,'total_retained_cells':449445,'total_retained_backing_bits':1348335},
        'source_hashes':sources,'coefficient_sha256':hashlib.sha256((P/'COEFFICIENTS.json').read_bytes()).hexdigest(),
        'code_hashes':{f:hashlib.sha256((P/f).read_bytes()).hexdigest() for f in ('machine.py','verify.py')}}
    if args.record:args.record.write_text(json.dumps(result,indent=2)+'\n')
    else:need(canonical(frozen)==canonical(result),'complete typed frozen receipt')
    print(json.dumps({'status':result['status'],'source_setup_replayed':not args.cached,'seconds':time.monotonic()-start,'receipt_sha256':digest(result)},sort_keys=True))

if __name__=='__main__':main()
