#!/usr/bin/env python3
"""Regenerate and verify the selected h=24 partial-gauge complex producer.

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
from partial_gauge.scalar import build
from partial_gauge.lift import run as lift_run
from partial_gauge.word import run as word_run
from partial_gauge.select import run as select_run
from partial_gauge.verify import verify

ROOT=Path(__file__).resolve().parents[1]


def regenerate(work, expected, compiler):
    if sys.flags.optimize:raise ValueError('Run without -O; finite assertions must remain enabled')
    def stage(message):print(message,file=sys.stderr,flush=True)
    def save(name,data):
        path=work/name;path.write_text(json.dumps(data,separators=(',',':'))+'\n');return path
    stage('Building the actual interval/cube scalar DAG')
    scalar=build(24,base=2,central_disjoint=24,output_prefix='complex_cube',output_dir=work)
    dag=work/'complex_cube_24.bin';matcher=work/'matcher'
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
    return dict(regenerated_from_source=True,certificate_equal=True,selected=result,checks=checks)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--certificate',type=Path,default=ROOT/'certificates/partial-gauge-complex-input.json')
    p.add_argument('--work-dir',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--cxx',default=os.environ.get('CXX','c++'))
    a=p.parse_args();expected=json.loads(a.certificate.read_text())
    if a.work_dir:
        a.work_dir.mkdir(parents=True,exist_ok=True);result=regenerate(a.work_dir.resolve(),expected,a.cxx)
    else:
        with tempfile.TemporaryDirectory(prefix='partial-gauge-') as directory:
            result=regenerate(Path(directory),expected,a.cxx)
    encoded=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(encoded)
    else:print(encoded,end='')


if __name__=='__main__':main()
