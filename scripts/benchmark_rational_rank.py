#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare complete rank-certificate CLI bundles against a saved source file.

The dense rank-eight fixture is Nick Petalas's PR6272 fixture, using Ali
Romman's PR5789 certificate interface. Prepared with OpenAI Codex assistance.
Timing is opt-in, local evidence; outputs go only to --scratch.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def fixture():
    rng=random.Random(5789)
    left=[[rng.randrange(-4,5) for _ in range(8)] for _ in range(48)]
    right=[[rng.randrange(-4,5) for _ in range(64)] for _ in range(8)]
    return {'schema':'rational-rank-problem/v1','matrix':[
        [str(Fraction(sum(left[i][k]*right[k][j] for k in range(8)),
                      2**(i%5)*3**(j%4))) for j in range(64)] for i in range(48)]}


def bundle(script,problem,certificate,environment):
    command=[sys.executable,'-B','-W','error','-X',
             'pycache_prefix='+str(problem.parent/'bytecode'),str(script),str(problem)]
    start=time.perf_counter_ns()
    result=subprocess.run(command,env=environment,capture_output=True,timeout=120)
    if result.returncode or result.stderr:
        raise RuntimeError('Certificate production failed: '+repr(result.stderr))
    certificate.write_bytes(result.stdout)
    checked=subprocess.run(command+['--check',str(certificate)],env=environment,
                           capture_output=True,timeout=120)
    elapsed=time.perf_counter_ns()-start
    if (checked.returncode or checked.stderr
            or checked.stdout.splitlines()!=[b'PASS_RATIONAL_RANK_CERTIFICATE']):
        raise RuntimeError('Saved certificate check failed: '+repr(checked.stderr))
    return elapsed,sha256(result.stdout).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',required=True,type=Path,help='Unchanged baseline Python source')
    parser.add_argument('--scratch',required=True,type=Path,help='Existing output directory')
    args=parser.parse_args()
    if not args.before.is_file() or not args.scratch.is_dir():
        parser.error('--before must be a file and --scratch an existing directory')
    scratch=args.scratch.resolve();before=args.before.resolve()
    problem=scratch/'rank-problem.json'
    problem.write_bytes(json.dumps(fixture(),sort_keys=True).encode('utf-8'))
    scripts={'before':before,'after':ROOT/'scripts/certify_rational_rank.py'}
    environment=dict(os.environ,PYTHONPATH=str(ROOT/'scripts'),PYTHONDONTWRITEBYTECODE='1')
    environment.pop('PYTHONOPTIMIZE',None)
    environment.pop('PYTHONPYCACHEPREFIX',None)
    samples={side:[] for side in scripts};digests=set()
    # Warm both complete paths; warmup times are excluded, hashes still checked.
    for side,script in scripts.items():
        _,digest=bundle(script,problem,scratch/(side+'-certificate.json'),environment)
        digests.add(digest)
    for pair in range(7):
        for side in (('before','after') if pair%2==0 else ('after','before')):
            elapsed,digest=bundle(scripts[side],problem,scratch/(side+'-certificate.json'),environment)
            samples[side].append(elapsed);digests.add(digest)
    if len(digests)!=1:
        raise RuntimeError('Serialized certificates differ')
    medians={side:statistics.median(values) for side,values in samples.items()}
    report={'schema':'rational-rank-pivot-benchmark/v1',
            'python':sys.version,'platform':platform.platform(),'cpu_count':os.cpu_count(),
            'fixture':{'rows':48,'columns':64,'rank':8},'pairs':7,'warmup_bundles':2,
            'successful_cli_commands':32,'samples_ns':samples,'medians_ns':medians,
            'wall_time_reduction':1-medians['after']/medians['before'],
            'problem_sha256':sha256(problem.read_bytes()).hexdigest(),
            'certificate_sha256':next(iter(digests)),
            'source_sha256':{side:sha256(path.read_bytes()).hexdigest() for side,path in scripts.items()},
            'parser_sha256':sha256((ROOT/'scripts/compare_recursive_invoices.py').read_bytes()).hexdigest(),
            'benchmark_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    (scratch/'benchmark.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':main()
