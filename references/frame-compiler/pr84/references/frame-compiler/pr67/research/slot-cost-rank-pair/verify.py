#!/usr/bin/env python3
"""Replay, profile, or deterministically rebuild all-rank profile-cost words.

PR62 graph: Avi Eisenberg, assisted by Claude; PR60 compiler: Chafik
Boukhalfa, derived from eumemic PR57, with OpenAI Codex assistance.
Profile-cost selection experiment: Rohan Arun with OpenAI Codex assistance.
Apache-2.0; inherited notices and mathematical dependencies remain applicable.
"""
import sys
sys.dont_write_bytecode = True
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
import argparse, gzip, importlib.util, json, os, shlex, subprocess, tempfile
from hashlib import sha256
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EXP=ROOT/'scripts/experiments'
sys.path[:0]=[str(EXP),str(ROOT/'scripts')]
from binary_frame_replay import replay
from binary_frame_profile_prepare import prepare
import binary_frame_math as arithmetic

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def sha(path):return sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rebuild',action='store_true',help='Recompile both words and compare to committed witnesses')
    p.add_argument('--work-dir',type=Path,default=ROOT/'build/slot-cost-rank-pair')
    a=p.parse_args()
    records=json.loads((HERE/'frame-compiler.json').read_text())
    for name,digest in records['source_sha256'].items():
        assert sha(ROOT/name)==digest, 'Changed source: '+name
    for name,digest in records['artifact_sha256'].items():
        assert sha(HERE/name)==digest, 'Changed artifact: '+name
    a.work_dir.mkdir(parents=True,exist_ok=True)
    profiles=[]
    with tempfile.TemporaryDirectory(prefix='verify-',dir=a.work_dir) as temporary:
        work=Path(temporary)
        env=dict(os.environ,TMPDIR=str(work))
        if a.rebuild:
            oracle=work/'profile-oracle'
            subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(HERE/'profile_oracle.cpp'),'-o',str(oracle)],check=True,env=env)
            compiler=load(HERE/'compiler.py','all_rank_cost_compiler')
            compiler.graph=load(ROOT/'research/pair-assembly/pair_graph.py','pinned_pair_graph').graph
            for h in (23,25):
                compiler.oracles=[]
                compiler.ORACLE_EXE=str(oracle)
                compiler.ORACLE_INPUT=str(work/f'oracle-input-{h}.bin')
                try:
                    result,word=compiler.compile_(h,matching=True,reclaim=True,dirty=True)
                finally:
                    for proc in compiler.oracles:
                        proc.stdin.close()
                        assert proc.wait()==0, 'Discovery profile oracle failed'
                result.pop('seconds')
                assert json.loads(json.dumps(result))==records['axes'][str(h)]['compiled']
                raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
                assert sha256(raw).hexdigest()==records['axes'][str(h)]['word_sha256']
                assert raw==gzip.decompress((HERE/f'frame-word-{h}.json.gz').read_bytes())
                print(f'PASS deterministic all-rank rebuild h={h}',flush=True)
        binary=work/'profiles'
        subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(EXP/'binary_frame_profiles.cpp'),'-o',str(binary)],check=True,env=env)
        for h in (23,25):
            word=HERE/f'frame-word-{h}.json.gz'
            receipt=replay(word)
            assert json.loads(json.dumps(receipt))==records['axes'][str(h)]['replay']
            transitions=work/f'word{h}.bin'
            prepared=json.loads(json.dumps(prepare(word,transitions)))
            assert prepared==json.loads((HERE/f'frame-transitions-{h}.json').read_text())
            subprocess.run([str(binary),str(transitions)],check=True,env=env)
            profile=json.loads(Path(str(transitions)+'.profiles.json').read_text())
            assert profile==json.loads((HERE/f'frame-profiles-{h}.json').read_text())
            profiles.append(profile)
            print(f'PASS h={h}: complete dirty basis in both orientations, frame paths, fixed profiles',flush=True)
        constructor=load(ROOT/'research/pair-assembly/frame/frame_verify.py','inherited_profile_constructor')
        constructor.check_sources()
        constructor.WIRES_S=2*4073300+sum(4073300//f['v']*f['R'] for f in profiles)
        constructor.MASS_S=575*constructor.WIRES_S-1846900
        actual=arithmetic.js(constructor.profile(profiles,records))
        expected=json.loads((HERE/'paired-candidate.json').read_text())['bit']
        assert json.loads(json.dumps(actual))==expected
        print('PASS complete paid profile, literal rank identity and pinned artifacts',flush=True)

if __name__=='__main__':main()
