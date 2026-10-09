#!/usr/bin/env python3
"""Regenerate only the pinned PR118 scalar graph and matched physical profile."""
import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
from pr118_sources import check_base,PACKAGE

sys.dont_write_bytecode=True
if not __debug__:raise SystemExit('Assertions required')
EXPECTED={
    'graph.bin':'4ef7308feb5cbe0da4f35f8fe69eba89ec8f4cc7de174bc5468843e4e89f9a44',
    'graph.labels':'8d5133c205191ad80f19deae946a51ebcb546fd8a0302c8e8f0c5575f122bfc0',
    'graph.json':'1a1b287daccb0929f6e24e3648f57a9b2835ef4779df051eb8441e1b89b34c03',
    'matched.json':'1f633cae6f1eee1a0fbe3c7af30fa041553ca47417c83fb3b591230dbcdff586',
}


def generate(repo,output):
    repo=repo.resolve();binding=check_base(repo)
    output.mkdir(parents=True,exist_ok=False)
    source=repo/PACKAGE/'producer.py'
    spec=importlib.util.spec_from_file_location('checked_replayed_producer',source)
    producer=importlib.util.module_from_spec(spec);spec.loader.exec_module(producer)
    producer.build(24,output/'graph',24)
    compiler=shlex.split(os.environ.get('CXX','c++'))
    binary=output/'matcher'
    subprocess.run([*compiler,'-O3','-std=c++17',str(repo/'scripts/endpoint_gauge/match_complex_general.cpp'),'-o',str(binary)],check=True)
    row=json.loads(subprocess.check_output([str(binary),str(output/'graph.bin'),str(output/'graph.labels')],text=True))
    assert (row['h'],row['v'],row['c'],row['q'],row['matched'],row['R'])==(24,2024,91770,8120,71185,28705)
    (output/'matched.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
    observed={name:sha256((output/name).read_bytes()).hexdigest() for name in EXPECTED}
    assert observed==EXPECTED
    receipt=dict(source_binding=binding,generated_hashes=observed,
        pair_root_order='numeric i, not aligned parity order',
        scope='Exact scalar support/center/scatter/frame replay plus matching; deferred word and assembly not rerun here')
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    return receipt


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();generate(a.repo,a.output)
    print('PASS pinned PR118 scalar graph and matching',flush=True)


if __name__=='__main__':main()
