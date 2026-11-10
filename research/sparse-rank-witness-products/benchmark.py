#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Alternating cold CLI produce/save/check bundles; preserve every raw sample."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
from time import perf_counter_ns
from fixtures import dense_fixture
from verify import engines,HERE,ROOT


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--pairs',type=int,default=7);args=ap.parse_args()
    if args.output.exists() or not 3<=args.pairs<=20:ap.error('use a fresh output and 3..20 pairs')
    engines() # Authenticate reference and support before timing any code.
    paths={'before':HERE/'baseline.py','after':ROOT/'scripts/certify_rational_rank.py'}
    measured=[*paths.values(),HERE/'fixtures.py',HERE/'benchmark.py',HERE/'verify.py',
              ROOT/'scripts/compare_recursive_invoices.py']
    source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in measured}
    env=dict(os.environ,PYTHONPATH=str(ROOT/'scripts'),PYTHONDONTWRITEBYTECODE='1')
    for key in ('PYTHONOPTIMIZE','PYTHONPYCACHEPREFIX'):env.pop(key,None)
    samples={key:[] for key in paths};hashes=set();failures=[]
    with tempfile.TemporaryDirectory(prefix='rank-products-benchmark-') as temp:
        p=Path(temp)/'problem.json';p.write_bytes((json.dumps(dense_fixture(),sort_keys=True)+'\n').encode())
        input_hash=sha256(p.read_bytes()).hexdigest()
        for pair in range(args.pairs):
            for side in (('before','after') if pair%2==0 else ('after','before')):
                certificate=Path(temp)/(side+'-certificate.json')
                cmd=[sys.executable,'-X','pycache_prefix='+str(Path(temp)/'unused-bytecode'),
                     '-W','error','-B',str(paths[side]),str(p)]
                start=perf_counter_ns()
                result=subprocess.run(cmd,capture_output=True,env=env,cwd=temp,timeout=120)
                certificate.write_bytes(result.stdout)
                check=subprocess.run(cmd+['--check',str(certificate)],capture_output=True,env=env,cwd=temp,timeout=120)
                elapsed=perf_counter_ns()-start
                if result.returncode or result.stderr or check.returncode or check.stderr or check.stdout not in (b'PASS_RATIONAL_RANK_CERTIFICATE\n',b'PASS_RATIONAL_RANK_CERTIFICATE\r\n'):
                    failures.append({'side':side,'produce_exit':result.returncode,'check_exit':check.returncode,
                                     'stderr':(result.stderr+check.stderr).decode(errors='replace'),
                                     'check_stdout':check.stdout.decode(errors='replace')})
                samples[side].append(elapsed);hashes.add(sha256(result.stdout).hexdigest())
    if len(hashes)!=1:raise ValueError('certificate bytes changed; timing comparison invalid')
    if source_hashes!={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in measured}:
        raise ValueError('measured source changed during benchmark')
    medians={side:statistics.median(values) for side,values in samples.items()}
    report={'platform':platform.platform(),'python':sys.version,'cpu_count':os.cpu_count(),
            'fixture':'Nick Petalas PR6272 dense 48x64 rank-eight rational interface; synthetic',
            'samples_ns':samples,'median_ns':medians,'wall_time_reduction':1-medians['after']/medians['before'],
            'certificate_sha256':next(iter(hashes)),'problem_sha256':input_hash,'failures':failures,
            'source_sha256':source_hashes,
            'scope':'Complete fresh producer + save + fresh checker; startup, parsing, all predicates and serialization included.',
            'new_kappa':None}
    args.output.write_bytes((json.dumps(report,indent=2,sort_keys=True)+'\n').encode())
    if failures:raise ValueError('timed commands failed; see retained report')
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':main()
