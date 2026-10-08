#!/usr/bin/env python3
"""Frozen aligned graph with protected deferred reconstruction on h25.

Composition for Thomas DiFiore with OpenAI Codex assistance. Apache-2.0.
The pinned PR71 engine and PR69 graph are retained unchanged. Future-unit
completion follows PR79; weighted carry exchanges follow PR70/76. PR84 contributes exact candidate indexes, additional exchange passes and
future-use output routing. Our multi-pair aligned partitions and pricing
composition are checked as literal
finite words, including all physical frames and arbitrary dirty inputs.
"""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
from hashlib import sha256
import argparse,gzip,importlib.util,json,os,shlex,subprocess,tempfile,types
from concurrent.futures import ProcessPoolExecutor
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DEP=ROOT/'references/frame-compiler/pr71'
sys.path.insert(0,str(DEP/'scripts/experiments'))
from binary_frame_replay import replay
from partition_graph import graph
from storage_extension import apply as extend_storage

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def relabel(word,permutation):
    from itertools import combinations
    h,v=word['h'],word['v'];assert sorted(permutation)==list(range(h))
    triples=list(combinations(range(h),3));assert len(triples)==v
    index={triple:i for i,triple in enumerate(triples)}
    def triple(t):return sorted(permutation[x] for x in t)
    mapping={i:index[tuple(triple(t))] for i,t in enumerate(triples)}
    def mask(bits):return sum(1<<permutation[i] for i in range(h) if bits>>i&1)
    word['frames']=[[mask(c),mask(u)] for c,u in word['frames']]
    word['sources']={str(mapping[int(i)]):slot for i,slot in word['sources'].items()}
    scatter=[]
    for a,b in word['scatter']:
        assert v<=a<2*v and b>=2*v
        scatter.append([v+mapping[a-v],b])
    word['scatter']=scatter
    word['outputs']=[[s,g,permutation[common],triple(t)] for s,g,common,t in word['outputs']]
    return word



def check_sources():
    for folder in (DEP,ROOT/'references/frame-compiler/pr69',ROOT/'references/frame-compiler/pr82',ROOT/'references/frame-compiler/pr84'):
        manifest=json.loads((folder/'SOURCE.json').read_text())
        for name,digest in manifest['files'].items():assert sha256((folder/name).read_bytes()).hexdigest()==digest,name
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    required={str((HERE/name).relative_to(ROOT)) for name in ('producer.py','partition_graph.py','storage_extension.py','storage_engine.py','ENGINE-PATCH.diff','check.py','graph_audit.py','independent_check.py','selection.json','PROOF.md')}
    assert required<=set(manifest['files']), 'Incomplete selected source closure'
    for name,digest in manifest['files'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    for stem,ext in (('word','json.gz'),('profile','json'),('transitions','json')):
        assert (HERE/f'{stem}-23.{ext}').read_bytes()==(ROOT/f'research/aligned-exchange-frames/{stem}-23.{ext}').read_bytes(),'Baseline h23 differs'


def compile_axis(h):
    check_sources()
    config=json.loads((HERE/'selection.json').read_text())['axes'][str(h)]
    assert config['engine']==('indexed-pr84' if h==23 else 'indexed-pr84-deferred-span')
    assert config['single_exchange_passes']==3
    assert config['two_exchange_passes']==3
    assert config['output_mode'] in ('baseline','route-late')
    price=config['pricing_permutation'];assert sorted(price)==list(range(h))
    source_path=ROOT/'references/frame-compiler/pr84/scripts/experiments/indexed_cycle_engine.py'
    source=source_path.read_text()
    if h==25:source=extend_storage(source)
    old="for b in blocks:stream.write(struct.pack('<2QI',*b['frame'],b['rank']))"
    new="for b in blocks:stream.write(struct.pack('<2QI',*(permute_mask(mask) for mask in b['frame']),b['rank']))"
    assert source.count(old)==1;source=source.replace(old,new)
    marker=' # Bounded two-donor exchanges after single-edge local optimization.'
    assert source.count(marker)==1
    prefix,suffix=source.split(marker);assert suffix.count('for phase in range(3):')==1
    source=prefix+marker+suffix.replace('for phase in range(3):','for phase in range(TWO_PASSES):')
    engine=types.ModuleType('deferred_span_private_engine')
    engine.__file__=str(DEP/'scripts/experiments/split_pair_engine.py')
    exec(compile(source,str(source_path)+':aligned-indexed','exec'),engine.__dict__)
    engine.permute_mask=lambda bits:sum(1<<price[i] for i in range(h) if bits>>i&1)
    engine.graph=graph;engine.PENDING_COST=True;engine.oracles=[]
    engine.OUTPUT_MODE=config['output_mode'];engine.TWO_PASSES=config['two_exchange_passes']
    with tempfile.TemporaryDirectory(prefix='deferred-span-compile-') as directory:
        work=Path(directory);oracle=work/'oracle'
        subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(DEP/'references/frame-compiler/pr48/scripts/partial_swap'),str(DEP/'references/frame-compiler/pr67/research/slot-cost-rank-pair/profile_oracle.cpp'),'-o',str(oracle)],check=True)
        engine.ORACLE_EXE=str(oracle);engine.ORACLE_INPUT=str(work/'oracle.bin')
        try:compiled,word=engine.compile_(h,matching=True,reclaim=True,dirty=True)
        finally:
            for process in engine.oracles:process.stdin.close();assert process.wait(timeout=10)==0
    compiled.pop('seconds',None)
    compiled['scalar']=graph(h).verify()
    compiled['graph_configuration']=config
    compiled['private_engine_sha256']=sha256(source.encode()).hexdigest()
    word=relabel(word,config['coordinate_permutation'])
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
    assert sha256(raw).hexdigest()==config['expected_word_sha256'],'Selected word differs'
    path=HERE/f'word-{h}.json.gz'
    with path.open('wb') as stream:
        with gzip.GzipFile(filename='',fileobj=stream,mode='wb',mtime=0) as archive:archive.write(raw)
    receipt=replay(path)
    axis=dict(configuration=config,compiled=compiled,replay=receipt,word_sha256=sha256(raw).hexdigest(),gzip_sha256=sha256(path.read_bytes()).hexdigest())
    (HERE/f'axis-{h}.json').write_text(json.dumps(axis,indent=2)+'\n')
    print(f'PASS fresh deferred-span package word h={h}, roles={receipt["roles"]}',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--h',type=int,choices=(23,25));args=parser.parse_args()
    if args.h:compile_axis(args.h)
    else:
        with ProcessPoolExecutor(max_workers=2) as pool:list(pool.map(compile_axis,(23,25)))
