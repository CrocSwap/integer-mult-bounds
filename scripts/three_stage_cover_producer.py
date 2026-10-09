#!/usr/bin/env python3
"""Regenerate and verify the selected pinned PR117 generalized-subspace complex producer.

Standard-library Python and C++17; generated DAGs and words are temporary.
Copyright 2026 icekylinx, Apache-2.0. Adapted from the credited round-six handoff.
"""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
from importlib.util import spec_from_file_location, module_from_spec
import hashlib
from three_stage_cover.lift import run as lift_run
from partial_gauge.word import run as word_run
from three_stage_cover.select import run as select_run
from three_stage_cover.verify import verify

ROOT=Path(__file__).resolve().parents[1]


def regenerate(work, expected, compiler):
    if sys.flags.optimize:raise ValueError('Run without -O; finite assertions must remain enabled')
    def stage(message):print(message,file=sys.stderr,flush=True)
    def save(name,data):
        path=work/name;path.write_text(json.dumps(data,separators=(',',':'))+'\n');return path
    stage('Replaying the pinned PR117 scalar DAG')
    reference=ROOT/'references/three-stage-cover/pr117'
    source=json.loads((reference/'SOURCE.json').read_text())
    assert source['commit']=='cbb05ce504d571546d9b7794c186a613c659c3bf'
    for name,digest in source['files'].items():
        assert hashlib.sha256((reference/name).read_bytes()).hexdigest()==digest, 'Source binding differs: '+name
    witness=reference/'dag.json.gz'
    assert hashlib.sha256(witness.read_bytes()).hexdigest()=='3c034d0aae388ef567a454826f4f48b26fd8a94c71e8ffed4835271b349a783b'
    spec=spec_from_file_location('pr117_replayed',reference/'replayed.py')
    module=module_from_spec(spec);spec.loader.exec_module(module)
    scalar=module.build(witness,work/'selected')
    dag=work/'selected.bin';matcher=work/'matcher'
    subprocess.run([*shlex.split(compiler),'-O3','-std=c++17',str(ROOT/'scripts/partial_gauge/match.cpp'),'-o',str(matcher)],check=True)
    stage('Constructing compatible carrier matching')
    matching=json.loads(subprocess.check_output([str(matcher),str(dag),str(dag.with_suffix('.labels'))],text=True))
    matchfile=save('matching.json',matching)
    stage('Lifting exact binary frames backward through dependencies and carriers')
    lifted,ann=lift_run(dag,matchfile);liftfile=save('lifted.json',lifted);annfile=save('annihilators.json',ann)
    stage('Constructing physical M and its retained-center dependency closure')
    word=word_run(dag,matchfile,annfile,liftfile);wordfile=save('word.json',word)
    stage('Selecting partial source gauges with reverse readouts')
    result,selection=select_run(dag,annfile,liftfile,wordfile)
    result=json.loads(json.dumps(result))
    assert result==expected, 'Regenerated selected certificate differs'
    save('selection.json',selection)
    stage('Checking scalar coefficients, actual frames, physical word and readout chains')
    checks=verify(dag,matching,ann,lifted,word,selection['selected'],result)
    return dict(source_pin_verified=True,regenerated_from_source=True,certificate_equal=True,selected=result,checks=checks)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--certificate',type=Path,default=ROOT/'certificates/three-stage-cover-complex-input.json')
    p.add_argument('--work-dir',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--cxx',default=os.environ.get('CXX','c++'))
    a=p.parse_args();expected=json.loads(a.certificate.read_text())
    if a.work_dir:
        a.work_dir.mkdir(parents=True,exist_ok=True);result=regenerate(a.work_dir.resolve(),expected,a.cxx)
    else:
        with tempfile.TemporaryDirectory(prefix='three-stage-cover-') as directory:
            result=regenerate(Path(directory),expected,a.cxx)
    encoded=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(encoded)
    else:print(encoded,end='')


if __name__=='__main__':main()
