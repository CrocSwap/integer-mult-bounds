#!/usr/bin/env python3
"""Canonical JSON replay of the unchanged scientific engine.

JSON object keys are strings; rank keys in fresh Python histograms are integers.
Every encoded field and value remains checked. Apache-2.0; OpenAI assistance.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json

HERE=Path(__file__).resolve().parent
ENGINE='d91cfcffe9963b9df42e3874f09b29627edd2565'

def canonical(value):
    encoded=json.dumps(value,allow_nan=False)
    return json.dumps(json.loads(encoded),sort_keys=True,separators=(',',':'),allow_nan=False)

def compare(expected,actual):
    if canonical(expected)!=canonical(actual):
        raise ValueError('Complete scientific receipt mismatch')

def controls():
    actual={'paid':{1:2},'flag':True,'ordered':[1,2]}
    expected=json.loads(json.dumps(actual));compare(expected,actual)
    bads=[{**actual,'paid':{1:3}},{**actual,'flag':1},{**actual,'paid':{1:2.0}},
          {**actual,'ordered':[2,1]},{**actual,'extra':0},{'paid':{1:2},'flag':True}]
    for bad in bads:
        try:compare(expected,bad)
        except ValueError:pass
        else:raise ValueError('Receipt mutation accepted')
    return 6

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    n=controls()
    if not args.self_test:
        path=HERE/'verify.py';raw=path.read_bytes()
        digest=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if path.is_symlink() or digest!=ENGINE:raise ValueError('Scientific engine changed')
        spec=importlib.util.spec_from_file_location('receiver_scientific_engine',path)
        engine=importlib.util.module_from_spec(spec);spec.loader.exec_module(engine)
        fresh=engine.run()
        compare(json.loads((HERE/'RESULT.json').read_bytes()),fresh)
        print(json.dumps(fresh,indent=2,sort_keys=True))
    print('PASS_CANONICAL_RECEIPT_CONTROLS rejected='+str(n))

if __name__=='__main__':main()
