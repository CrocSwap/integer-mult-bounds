#!/usr/bin/env python3
"""Recount the retained ordinary model and signed caller surcharges.

This is an accounting diagnostic. MOVE ranks are counted from declared frame
dimensions, not a substitute for native or physical binding. No supplier
admission or complete changed-grid conversion theorem is claimed.
"""
import collections
import gzip
import hashlib
import json
import resource
import signal
import sys
from fractions import Fraction
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent
V = ROOT / 'vendor'
def sha(b): return hashlib.sha256(b).hexdigest()
def need(ok, text):
    if not ok: raise ValueError(text)

def main():
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (120, 121))
    signal.alarm(150)
    out = ROOT / 'ORDINARY-RESULT.json'
    need(not out.exists(), 'exclusive output')
    raw = (ROOT.parent/'word7641.json.gz').read_bytes()
    need(sha(raw)=='de43ed04f58133eaef8f8d12a9dae1e6e8aa7f9721044200cc839673d86fd7c1','source compressed pin')
    data=gzip.decompress(raw)
    need(sha(data)=='6a472688bdf2a1b293df0f4f77427a04a1f87c92fedb5b5a6921cc850c272b4f','source decompressed pin')
    W=json.loads(data)
    caller_raw=(V/'ODD-TYPE-AB-CALLER.json').read_bytes()
    need(sha(caller_raw)=='255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc','caller pin')
    C=json.loads(caller_raw)
    source=(V/'independent.py').read_bytes()
    need(sha(source)=='21f46a8340331abb1486b50bd4e04453f1968b0a5950d86ff7780dd368590874','ordinary source pin')
    text=source.decode(); part=text[text.index('def ordinary('):text.index('def main(')]
    edits=[('calls=18;', "calls=C['stages'];"),
           ('queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)', "queryroute=sum(p*1000*(2+(e[4]==-1)) for e in qr)\n  fusedroute=sum(36500*p for e in C['events'] if e[:2]==[ty,'IDLE_ODD'])"),
           ('idle_routes=idleroute,query_routes=queryroute)', 'idle_routes=idleroute,query_routes=queryroute,fused_routes=fusedroute)')]
    for before,after in edits:
        need(part.count(before)==1,'unique ordinary adaptation')
        part=part.replace(before,after)
    engine=ModuleType('ordinary_recount');engine.F=Fraction;engine.Counter=collections.Counter
    exec(compile(part,'independent-ordinary-pinned','exec'),engine.__dict__)
    moves=collections.Counter()
    for e in W['program']:
        if e[0]=='MOVE':
            rank=abs(len(W['frames'][e[2]])-len(W['frames'][e[3]]))
            need(rank>0,'nonzero declared MOVE rank')
            moves[rank]+=1
    mains=set(W['live']) | {r+112 for r in W['live']} | set(W['hosted']['X2']) | set(W['hosted']['Y2'])
    helpers=collections.Counter(len(W['frames'][W['final'][r]])-len(W['frames'][W['initial'][r]]) for r in range(W['public']) if r not in mains)
    need(all(r>0 for r in helpers),'positive helper ranks')
    lifetimes=sum(e[0]=='INIT' for e in W['program'])
    need(lifetimes==234 and lifetimes==sum(e[0]=='CLEAR' for e in W['program']),'declared lifecycle count')
    N={'paid':dict(moves),'helpers':dict(helpers),'lifetimes':lifetimes}
    base=engine.ordinary(W,C,N)
    surcharge=0
    for e in C['events']:
        if e[0]=='J' or e[1] not in ('ADD','SCALE'): continue
        q=Fraction(e[-1]);a,d=abs(q.numerator),q.denominator
        surcharge+=len(C['types'][e[0]]['ports'])*4*(a.bit_length()+d.bit_length()+1+(a.bit_count() if e[1]=='ADD' else 0))
    conversions=2*sum(t['roles']*len(t['ports']) for t in C['types'].values())
    cg=json.loads((V/'ODD-CALLER-EXACT-GRID.json').read_bytes())
    need(cg['caller_sha256']==sha(caller_raw),'caller grid pin')
    odd=int(cg['caller_odd_scale'])
    caller_conversions=conversions*4*(odd.bit_length()+1+odd.bit_count())
    total=base['conservative_total']+surcharge+caller_conversions
    # Quantify a possible increased native-grid conversion charge separately.
    # The actual primitive conversion implementation and overlap with the
    # retained per-input conversion allowance are not established here.
    native_conversion_sites=2*C['stages']*W['public']
    def conversion_rate(scale): return 4*(scale.bit_length()+1+scale.bit_count())
    native_extra=native_conversion_sites*(conversion_rate(10125)-conversion_rate(1125))
    record={'status':'RETAINED_MODEL_ACCOUNTING_ONLY','source_word_raw_sha256':sha(data),'caller_sha256':sha(caller_raw),
            'source_engine_sha256':sha(source),'adapted_ordinary_sha256':sha(part.encode()),'declared_inventory':N,
            'base':base,'all_caller_scalar_surcharge':surcharge,'charged_caller_odd_conversions':caller_conversions,
            'retained_signed_model_total':total,'retained_signed_model_margin':10**9-total,
            'native_scale_comparison':{'old':1125,'new':10125,'conversion_sites':native_conversion_sites,
               'rate_old':conversion_rate(1125),'rate_new':conversion_rate(10125),'increment_if_all_sites_charged_at_rate_delta':native_extra,
               'status':'sensitivity_only_overlap_with_retained_conversion_unresolved'},
            'source_7641_reported_ordinary':878834276,
            'limitations':['Declared dimension rank inventory only; no native, physical, signed or compiler admission.',
                'Numerical source-unit model, not measured implementation cost.',
                'Changed native grid conversion overlap, precision/storage, lifetime supplier and all physical costs remain open.']}
    with out.open('x') as f: json.dump(record,f,indent=2); f.write('\n')
    print(json.dumps({'status':record['status'],'base':base['conservative_total'],'signed_model':total,'sensitivity':native_extra}))

if __name__=='__main__': main()
