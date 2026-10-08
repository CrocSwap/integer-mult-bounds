"""Portable composition of PR79 balanced/future/exchange engine and PR76 ordering.
All inherited sources and notices remain unmodified. Composition by Rohan Arun
with OpenAI Codex assistance. Apache-2.0; finite conditional witness only.
"""
import sys
if sys.flags.optimize: raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/experiments'))
import balanced_split_graph as graph
import balanced_split_exchange_engine as baseline_engine
import flag_engine
sys.path.insert(0,str(ROOT/'references/frame-compiler/pr76/research/round7-scheduling'))
from schedule_variant import reorder
import argparse,gzip,json,subprocess,os,shlex

def check_flag_engine():
    original=(ROOT/'scripts/experiments/balanced_split_exchange_engine.py').read_text()
    before="for b in blocks:stream.write(struct.pack('<2QI',*b['frame'],b['rank']))"
    after="for b in blocks:stream.write(struct.pack('<2QI',*[sum(1<<COORD_MAP[i] for i in range(h) if mask>>i&1) for mask in b['frame']],b['rank']))"
    assert original.count(before)==1
    expected='# Coordinate-conjugated oracle pricing by Rohan Arun with OpenAI Codex.\n'+original.replace(before,after)
    assert (Path(__file__).parent/'flag_engine.py').read_text()==expected,'Flag engine contains changes beyond oracle coordinate pricing'

def compile_axis(h,work):
    check_flag_engine()
    engine=flag_engine if h==25 else baseline_engine
    if h==25:
        cfg=json.loads((ROOT/f'research/envelope-balanced/order-{h}.json').read_text())
        assert sorted(cfg['order'])==list(range(h))
        engine.COORD_MAP={int(k):v for k,v in cfg['mapping'].items()}
        assert engine.COORD_MAP=={old:new for new,old in enumerate(cfg['order'])}
    work.mkdir(parents=True,exist_ok=True)
    oracle=work/'oracle'
    subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'references/frame-compiler/pr67/research/slot-cost-rank-pair/profile_oracle.cpp'),'-o',str(oracle)],check=True)
    engine.graph=lambda dimension:reorder(graph.graph(dimension))
    engine.build=graph.ordered_build(engine.build,h)
    engine.ORACLE_EXE=str(oracle);engine.ORACLE_INPUT=str(work/'oracle.bin');engine.PENDING_COST=True;engine.oracles=[]
    try:result,word=engine.compile_(h,matching=True,reclaim=True,dirty=True)
    finally:
        for process in engine.oracles:
            process.stdin.close();assert process.wait(timeout=10)==0
    result.pop('seconds',None);result['scalar']=engine.graph(h).verify()
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
    (work/'word.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    (work/'compiler.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS compiled envelope-balanced axis',h,result['roles'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--h',type=int,choices=(23,25),required=True);p.add_argument('--work',type=Path,required=True);args=p.parse_args();compile_axis(args.h,args.work)
