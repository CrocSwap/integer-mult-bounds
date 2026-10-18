#!/usr/bin/env python3
"""Measured full classify calls on five large immutable payloads; not a gate.

ywz65, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import importlib.util
import json
from pathlib import Path
import platform
import statistics
import time

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('paired_verifier',HERE/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)


def run(rounds):
    fast,old=v.setup();data=old.corpus(old.bound_inputs())
    largest=sorted([(len(gzip.decompress(raw)),name,raw) for name,raw in data.items()
                    if name.endswith('.json.gz')],reverse=True)[:5]
    rows=[]
    for size,name,raw in largest:
        changed=gzip.compress(b'\n'+gzip.decompress(raw)+b'\n',mtime=123)
        times={'original':[],'paired':[]}
        functions={'original':fast.original_classify,'paired':fast.classify}
        for trial in range(rounds):
            for key in (('original','paired') if trial%2==0 else ('paired','original')):
                start=time.perf_counter();result=functions[key](name,raw,changed)
                elapsed=time.perf_counter()-start
                v.require(result=={'cls':'json-format'},'benchmark result differs')
                times[key].append(elapsed)
        medians={k:statistics.median(x) for k,x in times.items()}
        row={'file':name,'body_bytes':size,'seconds':times,'median_seconds':medians,
             'median_ratio':medians['original']/medians['paired']}
        rows.append(row);print(name,round(row['median_ratio'],3),flush=True)
    return {'scope':'five largest frozen compressed JSON files, whitespace-only reformat, complete classify including decompression and parsing; no setup or fixture-generation timing',
            'python':platform.python_version(),'platform':platform.platform(),
            'alternating_order_trials':rounds,'files':rows,
            'aggregate_median_ratio':sum(x['median_seconds']['original'] for x in rows)/sum(x['median_seconds']['paired'] for x in rows),
            'limits':'Machine/load-dependent observation, no threshold gate. Mismatches are parsed again by the original fallback and may be slower. Equal-byte fast path unchanged.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--rounds',type=int,default=3);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();v.require(args.rounds>=1,'positive trial count required');result=run(args.rounds)
    with args.out.open('x',encoding='utf-8',newline='\n') as out:
        json.dump(result,out,indent=2,sort_keys=True);out.write('\n')
