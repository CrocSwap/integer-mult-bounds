"""PR87 congruent splits with coordinate prices, null-circuit clearing and carrier exchanges.
Rohan Arun with OpenAI Codex assistance. Apache-2.0; all inherited checks retained.
"""
import sys
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
import json,gzip,subprocess,types,argparse,os,shlex
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts/experiments'))
import indexed_cycle_graph as graph

def configuration(h):
 assert type(h)is int and h in (23,25)
 config=json.loads((HERE/f'config-{h}.json').read_text())
 expected=dict(graph.EXPECTED_CONFIGS[h],groups=[4,4,1],output_mode='baseline')
 assert config==expected, 'Pinned PR87 configuration changed'
 return config

graph.configuration=configuration

def source_for(h):
 assert h in (23,25)
 source=(ROOT/'scripts/experiments/indexed_cycle_engine.py').read_text()
 before="for b in blocks:stream.write(struct.pack('<2QI',*b['frame'],b['rank']))"
 after="for b in blocks:stream.write(struct.pack('<2QI',*[sum(1<<COORD_MAP[i] for i in range(h) if mask>>i&1) for mask in b['frame']],b['rank']))"
 assert source.count(before)==1;source=source.replace(before,after)
 if h in (23,25):
  marker=' assert len(chosen)==len(right)==initial_count';assert source.count(marker)==1;source=source.replace(marker,(HERE/'exchanges.txt').read_text()+marker)
 start=source.index(' def acquire(g,anchors):');end=source.index(' for step,g in enumerate(order):')
 source=source[:start]+(HERE/'kernel_acquire.txt').read_text()+source[end:]
 return source

def compile_axis(h,work):
 work.mkdir(parents=True,exist_ok=True);source=source_for(h)
 engine=types.ModuleType('geometric_pricing_engine');engine.__file__=str(ROOT/'scripts/experiments/experimental_engine.py');exec(compile(source,str(HERE/'compiler.py')+':derived_engine','exec'),engine.__dict__)
 cfg=graph.configuration(h);engine.graph=graph.graph;engine.COORD_MAP=dict(enumerate(cfg['coordinate_permutation']));engine.MAX_CYCLE=3;engine.OUTPUT_MODE=cfg['output_mode'];engine.PENDING_COST=True;engine.oracles=[]
 oracle=work/'oracle';subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(ROOT/'references/frame-compiler/pr48/scripts/partial_swap'),str(ROOT/'references/frame-compiler/pr67/research/slot-cost-rank-pair/profile_oracle.cpp'),'-o',str(oracle)],check=True)
 engine.ORACLE_EXE=str(oracle);engine.ORACLE_INPUT=str(work/'oracle.bin')
 try:result,word=engine.compile_(h,matching=True,reclaim=True,dirty=True)
 finally:
  for proc in engine.oracles:proc.stdin.close();assert proc.wait(timeout=15)==0
 result.pop('seconds',None);result['scalar']=graph.graph(h).verify()
 (work/'original.json.gz').write_bytes(gzip.compress((json.dumps(word,separators=(',',':'))+'\n').encode(),mtime=0));(work/'compiler.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS compiled',h,result['roles'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--h',type=int,choices=(23,25),required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args();compile_axis(a.h,a.work)
