#!/usr/bin/env python3
"""Bounded PR60 reclamation-order probe on Avi Eisenberg's PR62 graph.

Reuses Chafik Boukhalfa's compiler modification and eumemic's independent
word/frame checkers. This diagnostic does not assert a new multiplication
witness. Artifacts and exact target-rejection receipt go under build/.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_community_candidate import moment
import joint_dual_reclaim_compiler as compiler
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare


def summarize(work):
    N,m,W=4073300,575,8146600
    rows=Counter({1:19*N,21:2*N,17:2*N,481:2*N})
    axes=[]
    for h in (23,25):
        path=work/f'word-{h}.bin.profiles.json';f=json.loads(path.read_text())
        receipt=json.loads((work/f'receipt-{h}.json').read_text())['replay']
        if f['R']!=receipt['roles'] or f['rank_sum']!=receipt['rank_mass']:
            raise ValueError('Profile/word mismatch')
        if f['loss']!=h*(h-1) or f['blocks'][h]!=0:
            raise ValueError('Copied-center contract')
        rep=N//f['v'];bank=rep*f['R'];W+=bank
        rows.update({t:n*rep for t,n in enumerate(f['blocks']) if t and n})
        rows.update({h:bank,m-2*h:bank,1:2*N,h-2:2*N})
        axes.append(dict(h=h,roles=f['R'],profile_sha256=sha256(path.read_bytes()).hexdigest()))
    if m*W-sum(t*n for t,n in rows.items())!=1846900:
        raise ValueError('Rank ledger')
    lower,upper=moment(m,W,rows.items(),Q(1,2**14))
    return dict(axes=axes,m=m,W=W,deficit=1846900,target='1/16384',
                moment_lower=str(lower),strict_rejection=lower>1,
                scope='Exact moment screen for this fixed compiled graph only. A multiplication saving needs a larger bit saving; failure here rules out this 2^-14 witness, not other constructions.')


def run(work):
    if sys.flags.optimize: raise ValueError('Assertions must remain enabled')
    work.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('pair_ranked_graph',ROOT/'research/pair-assembly/pair_graph.py')
    graph=importlib.util.module_from_spec(spec);spec.loader.exec_module(graph)
    compiler.graph=graph.graph
    exe=work/'profiles'
    subprocess.run(['c++','-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'scripts/experiments/binary_frame_profiles.cpp'),'-o',str(exe)],check=True)
    for h in (23,25):
        result,word=compiler.compile_(h,matching=True,reclaim=True,dirty=True)
        path=work/f'word-{h}.json.gz'
        path.write_bytes(gzip.compress((json.dumps(word,separators=(',',':'))+'\n').encode(),mtime=0))
        receipt=replay(path)
        (work/f'receipt-{h}.json').write_text(json.dumps(dict(compiler=result,replay=receipt),indent=2)+'\n')
        transitions=work/f'word-{h}.bin';prepare(path,transitions)
        subprocess.run([str(exe),str(transitions)],check=True)
    result=summarize(work)
    (work/'screen.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Strict 2^-14 rejection:',result['strict_rejection'])

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir',type=Path,default=ROOT/'build/pair-ranked-probe')
    run(parser.parse_args().work_dir.resolve())
