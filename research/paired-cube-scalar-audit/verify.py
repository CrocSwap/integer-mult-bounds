#!/usr/bin/env python3
"""Source-bound exact finite scalar audits, separate from phase/all-size claims."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import independent_bit as B
import independent_sinks as C

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PIN='2c4a380126640abfcdce398ced255d1dd5d1d007'
INPUT_CLOSURE_PIN='fdbe5b41248b50e759a0749e7aefff65ffcd7116ef73994e633c392895428fe1'
CHECKER_PINS={'independent_bit.py':'0ceac13910e1d50b2145062fc5db38a3709d82e85bf5d8ff000a0d64a36b104b',
              'independent_sinks.py':'2e22beab7b7a84c94a31743b16ade95af8430bf6257ff3efb5432c75f197a319'}
AUDIT_SOURCES={'LICENSE','NOTICE','README.md','independent_bit.py','independent_sinks.py',
               'test_bit.py','test_sinks.py','test_source.py','verify.py'}

def require(condition,message):
    if not condition:
        raise ValueError(message)

def canonical(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()

def check_source_manifest(data,read_upstream,read_audit):
    require(data['upstream_commit']==PIN,'wrong upstream revision')
    require(type(data['audit_sha256']) is dict and set(data['audit_sha256'])==AUDIT_SOURCES,
            'incomplete audit source closure')
    require(canonical({k:data[k] for k in ('upstream_sha256','complex_canonical_sha256')})==INPUT_CLOSURE_PIN,
            'wrong frozen input closure')
    for name,digest in CHECKER_PINS.items():
        require(data['audit_sha256'][name]==digest,'wrong reviewed checker pin: '+name)
    for path,digest in data['upstream_sha256'].items():
        require(hashlib.sha256(read_upstream(path)).hexdigest()==digest,'upstream source changed: '+path)
    for path,digest in data['audit_sha256'].items():
        require(hashlib.sha256(read_audit(path)).hexdigest()==digest,'audit source changed: '+path)
    return data

def source_lock():
    return check_source_manifest(json.loads((HERE/'SOURCE.json').read_bytes()),
                                 lambda p:(ROOT/p).read_bytes(),lambda p:(HERE/p).read_bytes())

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complex-work-dir',type=Path,
                        help='directory containing regenerated graph.json, selection.json and frames.json')
    parser.add_argument('--bit-only',action='store_true')
    args=parser.parse_args()
    if not args.bit_only and args.complex_work_dir is None:
        parser.error('--complex-work-dir is required for the complex audit')
    lock=source_lock()
    bit=B.check(B.load(ROOT/'research/paired-cube-bit/out/graph_p12.json'),
                B.load(ROOT/'references/paired-cube/bit-physical/word_p12.json.gz'),
                B.load(ROOT/'references/paired-cube/bit-physical/kchron_p12.json'),controls=True)
    result={'upstream_commit':PIN,'bit':bit}
    if not args.bit_only:
        read=lambda path:json.loads(path.read_bytes())
        raw={name:read(args.complex_work_dir/filename) for name,filename in
             [('graph','graph.json'),('word','selection.json'),('witness','frames.json')]}
        for name,obj in raw.items():
            require(canonical(obj)==lock['complex_canonical_sha256'][name],
                    'regenerated complex witness changed: '+name)
        result['complex']=C.audit_raw(raw['graph'],raw['word'],raw['witness'],
            B.load(ROOT/'research/paired-cube-frame-refinement/selected/physical-frames.json.gz'),
            read(ROOT/'references/paired-cube/physical/pairs.json')['pairs'],
            read(ROOT/'research/terminal-sinks/sinks.json')['sinks'])
    result['scope']='Exact finite scalar identities with mathematical controls. General phases, '
    result['scope']+='frame/cost theorems, uniform compiler, analytic and fixed-tape interfaces remain hypotheses.'
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':
    main()
