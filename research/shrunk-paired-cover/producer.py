#!/usr/bin/env python3
"""Regenerate and verify the shrunk-frame PR117 complex producer on PR130's cover.

Adapted from icekylinx's PR130 scripts/three_stage_cover_producer.py (Apache-2.0):
the same pinned PR117 DAG, carrier matching, physical word and unrestricted
source-gauge selection, with lift_shrunk.py in place of the full lift and
verify_shrunk.py in place of the full-lift equality check.
Standard-library Python and C++17; generated DAGs and words are temporary.
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

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
from lift_shrunk import run as lift_run
from verify_shrunk import verify
from partial_gauge.word import run as word_run
from three_stage_cover.select import run as select_run


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
    if os.environ.get('SHRUNK_WRITE')=='1':(HERE/'complex-input.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');expected=result
    assert result==expected, 'Regenerated selected certificate differs'
    assert lifted['shrunk_frames']==15697, lifted['shrunk_frames']
    save('selection.json',selection)
    stage('Checking scalar coefficients, actual frames, physical word and readout chains')
    checks=verify(dag,matching,ann,lifted,word,selection['selected'],result)
    return dict(source_pin_verified=True,regenerated_from_source=True,certificate_equal=True,selected=result,checks=checks)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--certificate',type=Path,default=HERE/'complex-input.json')
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
