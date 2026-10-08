#!/usr/bin/env python3
"""Rebuild the selected graph, physical words, profiles and exact certificate."""
import argparse
import gzip
import json
import os
from pathlib import Path
import shlex
import subprocess
from support import HERE, ROOT, SELECTED, EXP, load, write_json, config, permutation
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
from arithmetic import certify, independent_audit
from geometry import relabel
import carry_exchanges


def binaries(work):
    oracle, profiler = work/'profile-oracle', work/'profiles'
    for source, output in ((HERE/'profile_oracle.cpp', oracle), (EXP/'binary_frame_profiles.cpp', profiler)):
        subprocess.run([*shlex.split(os.environ.get('CXX', 'c++')), '-O3', '-std=c++17',
                        '-I', str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),
                        str(source), '-o', str(output)], check=True)
    return oracle, profiler


def generate_axis(h, work, oracle, profiler):
    compiler = load(HERE/'compiler.py', 'balanced_split_compiler')
    graph = load(HERE/'graph.py', 'balanced_split_graph')
    compiler.graph = lambda dimension: graph.graph(dimension, groups=(1, 1, 2), anchor='first',
        coarse='half' if h == 23 else 'rows', coarse_shift=2 if h == 23 else 0, node_order='envelope')
    compiler.CONFIG = config(h)
    compiler.ORACLE_EXE = str(oracle)
    compiler.ORACLE_INPUT = str(work/f'oracle-{h}.bin')
    compiler.oracles = []
    carry_exchanges.install(compiler, h, work, passes=3, two_cycles=True, two_paths=True)
    try:
        compiled, word = compiler.compile_(h, matching=True, reclaim=True, dirty=True)
    finally:
        for process in compiler.oracles:
            process.stdin.close()
            assert process.wait() == 0, 'Discovery oracle failed'
    compiled.pop('seconds')
    original = (json.dumps(word, separators=(',', ':'))+'\n').encode()
    (work/f'original-{h}.json.gz').write_bytes(gzip.compress(original, mtime=0))
    word = relabel(word, permutation(h))
    raw = (json.dumps(word, separators=(',', ':'))+'\n').encode()
    packed = work/f'word-{h}.json.gz'
    with packed.open('wb') as stream:
        with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as archive:
            archive.write(raw)
    receipt = replay(packed)
    transition = work/f'word-{h}.bin'
    prepared = prepare(packed, transition)
    subprocess.run([str(profiler), str(transition)], check=True)
    prof = json.loads(Path(str(transition)+'.profiles.json').read_text())
    for name, data in [('compiled', compiled), ('replay', receipt), ('profile', prof), ('transitions', prepared), ('config', config(h))]:
        write_json(work/f'{name}-{h}.json', data)
    print(f'PASS rebuilt graph, word, dirty basis and exact profile h={h}', flush=True)


def combine(work):
    constructor = load(ROOT/'research/pair-assembly/frame/frame_verify.py', 'balanced_split_profile')
    constructor.check_sources()
    profiles = [json.loads((work/f'profile-{h}.json').read_text()) for h in (23, 25)]
    words = {'axes': {str(h): {'replay': json.loads((work/f'replay-{h}.json').read_text())} for h in (23, 25)}}
    constructor.WIRES_S = 2*4073300+sum(4073300//f['v']*f['R'] for f in profiles)
    constructor.MASS_S = 575*constructor.WIRES_S-1846900
    return constructor.profile(profiles, words)


def finish(work):
    certificate = certify(combine(work))
    write_json(work/'certificate.json', certificate)
    audit = independent_audit(json.loads((work/'certificate.json').read_text()))
    write_json(work/'audit.json', audit)
    print('PASS exact conditional kappa', certificate['kappa'], flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--axis', type=int, choices=(23, 25))
    p.add_argument('--assemble-only', action='store_true')
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if not args.assemble_only:
        oracle, profiler = binaries(args.output)
        for h in (args.axis,) if args.axis else (23, 25):
            generate_axis(h, args.output, oracle, profiler)
    if args.assemble_only or args.axis is None:
        finish(args.output)


if __name__ == '__main__':
    main()
