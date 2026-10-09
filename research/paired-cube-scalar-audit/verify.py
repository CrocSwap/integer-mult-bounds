#!/usr/bin/env python3
"""Source-bound exact selected181 scalar audits; general phase contracts excluded."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import independent_bit as B
import independent_sinks as C

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(100000)
PIN='7fb2194801e3a10f54772c7f0d5505035a4fc0ad'
SELECT='research/paired-cube-local-168/selected/complex/'
INPUT_CLOSURE_PIN='21a3820abbbcf03fc385fe3a7321aefc38ba2d57899216e5b269236242996c4d'
CHECKER_PINS={'independent_bit.py':'0ceac13910e1d50b2145062fc5db38a3709d82e85bf5d8ff000a0d64a36b104b',
              'independent_sinks.py':'6345a9b3a899ccdf40a2a97062fb01b0abe6e989aad938656b706f80e77586df'}
AUDIT_SOURCES={'LICENSE','NOTICE','README.md','independent_bit.py','independent_sinks.py',
               'test_bit.py','test_sinks.py','test_signed.py','test_source.py','verify.py'}
JOINT_KEYS=('upstream_sha256','complex_canonical_sha256','precision_sha256')

def require(condition,message):
    if not condition:raise ValueError(message)

def canonical(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def check_source_manifest(data,read_upstream,read_audit,read_precision=None):
    require(data['upstream_commit']==PIN,'wrong upstream revision')
    require(type(data['audit_sha256']) is dict and set(data['audit_sha256'])==AUDIT_SOURCES,
            'incomplete audit source closure')
    require(canonical({k:data[k] for k in JOINT_KEYS})==INPUT_CLOSURE_PIN,'wrong frozen input closure')
    require(type(data['upstream_sha256']) is dict and len(data['upstream_sha256'])==1700,
            'incomplete native181 source closure')
    require(set(data['complex_canonical_sha256'])=={'graph','word','witness','operation_frames','pairs','sinks'},
            'incomplete raw complex canonical binding')
    for name,digest in CHECKER_PINS.items():
        require(data['audit_sha256'][name]==digest,'wrong reviewed checker pin: '+name)
    for path,digest in data['upstream_sha256'].items():
        require(hashlib.sha256(read_upstream(path)).hexdigest()==digest,'upstream source changed: '+path)
    for path,digest in data['audit_sha256'].items():
        require(hashlib.sha256(read_audit(path)).hexdigest()==digest,'audit source changed: '+path)
    read_precision=read_precision or (lambda p:(ROOT/p).read_bytes())
    for path,digest in data['precision_sha256'].items():
        require(hashlib.sha256(read_precision(path)).hexdigest()==digest,'precision source changed: '+path)
    return data

def source_lock():
    return check_source_manifest(json.loads((HERE/'SOURCE.json').read_bytes()),
                                 lambda p:(ROOT/p).read_bytes(),lambda p:(HERE/p).read_bytes())

def load_complex(lock,work_dir=None):
    raw={name:B.load(ROOT/SELECT/filename) for name,filename in
         [('graph','graph.json.gz'),('word','word.json.gz'),('witness','frames.json.gz'),
          ('operation_frames','physical-frames.json.gz'),('pairs','physical-pairs.json.gz')]}
    raw['sinks']=[[item['role'],item['pivot']] for item in B.load(ROOT/SELECT/'sinks.json')['sinks']]
    if work_dir is not None:
        for name,filename in [('graph','graph.json'),('word','selection.json'),('witness','frames.json')]:raw[name]=B.load(work_dir/filename)
    for name,value in raw.items():require(canonical(value)==lock['complex_canonical_sha256'][name],'selected complex witness changed: '+name)
    return raw

def bind_precision_inputs():
    path=ROOT/'research/precision-certificate/profile_binding.py'
    spec=importlib.util.spec_from_file_location('selected181_native_profile_binding',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    inputs={name:B.load(path.parent/'inputs'/name) for name in module.INPUT_NAMES}
    return module.check_native_inputs(ROOT,inputs)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complex-work-dir',type=Path,
                        help='optional external181 raw graph/selection/frames, checked against exact selected canonical hashes')
    parser.add_argument('--bit-only',action='store_true')
    args=parser.parse_args();lock=source_lock();binding=bind_precision_inputs()
    bit=B.check(B.load(ROOT/'research/paired-cube-bit/out/graph_p12.json'),
                B.load(ROOT/'references/paired-cube/bit-physical/word_p12.json.gz'),
                B.load(ROOT/'references/paired-cube/bit-physical/kchron_p12.json'),controls=True)
    result={'upstream_commit':PIN,'native_profile_binding':binding,'bit':bit}
    if not args.bit_only:
        raw=load_complex(lock,args.complex_work_dir)
        result['complex']=C.audit_raw(raw['graph'],raw['word'],raw['witness'],raw['operation_frames'],raw['pairs'],raw['sinks'])
    result['scope']='Exact finite scalar maps on pinned raw selected181 inputs, including signed reflections. '
    result['scope']+='Native profile binding is consistency evidence; general phase/cost, weighted compiler, analytic and fixed-tape interfaces remain hypotheses.'
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':main()
