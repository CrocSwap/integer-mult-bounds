#!/usr/bin/env python3
"""Literal scalar-service census using retained fixed-tape tariff formula.

This does not provide the physical binding or map-slot record ceiling.
"""
import collections
import gzip
import hashlib
import json
import resource
import signal
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def sha(b):return hashlib.sha256(b).hexdigest()
def need(v,m):
    if not v: raise ValueError(m)
def main():
    resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    resource.setrlimit(resource.RLIMIT_CPU,(120,121));signal.alarm(150)
    out=ROOT/'TAPE-SCALAR-RESULT.json';need(not out.exists(),'exclusive output')
    raw=(ROOT.parent/'word7641.json.gz').read_bytes()
    need(sha(raw)=='de43ed04f58133eaef8f8d12a9dae1e6e8aa7f9721044200cc839673d86fd7c1','compressed source pin')
    data=gzip.decompress(raw);need(sha(data)=='6a472688bdf2a1b293df0f4f77427a04a1f87c92fedb5b5a6921cc850c272b4f','raw source pin')
    w=json.loads(data); cr=(ROOT/'vendor/ODD-TYPE-AB-CALLER.json').read_bytes()
    need(sha(cr)=='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc','caller pin')
    c=json.loads(cr); cg=json.loads((ROOT/'vendor/ODD-CALLER-EXACT-GRID.json').read_bytes());need(cg['caller_sha256']==sha(cr),'caller-grid pin')
    src=(ROOT/'vendor/check_odd_fixed_tape_counts.py').read_bytes()
    need(sha(src)=='e6246e9f8fbeae3077d82e585eafd3647c1a8758c58f33c7c13e7efa6c1e42bb','tape source pin')
    op=collections.Counter(e[0] for e in w['program'])
    calls=c['stages'];native=sum(v for k,v in op.items() if k!='MOVE')
    caller=sum(len(c['types'][e[0]]['ports']) for e in c['events'] if e[0]!='J')
    conversions=2*calls*w['public']+2*sum(t['roles']*len(t['ports']) for t in c['types'].values())
    scalar_services=32*(calls*native+caller+conversions)
    scalar_records=[]
    for i,e in enumerate(w['program']):
        if e[0] in ('ADD','COPY','SCALE'):
            q=Fraction(e[2] if e[0]=='SCALE' else e[3]);scalar_records.append((q,'native',i))
    for i,e in enumerate(c['events']):
        if e[0]!='J' and e[1] in ('ADD','SCALE'):
            q=Fraction(e[-1]);scalar_records.append((q,'caller',i))
    odd=int(cg['caller_odd_scale'])
    scalar_records.extend((Fraction(s),'conversion',str(s)) for s in (10125,Fraction(1,10125),odd,Fraction(1,odd)))
    largest=max(scalar_records,key=lambda x:abs(x[0].numerator).bit_length())
    largest_q=max(scalar_records,key=lambda x:abs(x[0]))
    bits=abs(largest[0].numerator).bit_length()
    o={'status':'SCALAR_CENSUS_ONLY','source_raw_sha256':sha(data),'caller_sha256':sha(cr),'fixed_tape_source_sha256':sha(src),
       'opcodes':dict(op),'native_invocations':calls,'native_nonmove_per_call':native,'caller_macros':caller,'conversion_sites':conversions,
       'scalar_macro_inputs':{'native':calls*native,'caller':caller,'conversions':conversions},
       'scalar_services_upper':scalar_services,'scalar_steps_coefficient':scalar_services*2**20,
       'max_literal_numerator_bits':bits,'max_numerator_witness':[str(largest[0]),largest[1],largest[2]],
       'max_absolute_coefficient':[str(largest_q[0]),largest_q[1],largest_q[2]],
       'retained_24bit_numerator_gate_passes':bits<=24,'retained_scalar_magnitude_lt_2pow16_gate_passes':abs(largest_q[0])+1<2**16,
       'scale_assumed_for_comparison':10125,'scope':'Finite tariff substitutions only; requires fresh matching precision, physical/paid binding, signed application, compiler and supplier. Scale 10125 is the author-reported value pending independent grid outcome.'}
    with out.open('x') as f:json.dump(o,f,indent=2);f.write('\n')
    print(json.dumps({'status':o['status'],'services':scalar_services,'numerator_bits':bits,'gates':[o['retained_24bit_numerator_gate_passes'],o['retained_scalar_magnitude_lt_2pow16_gate_passes']]}))
if __name__=='__main__':main()
