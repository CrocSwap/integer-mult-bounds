#!/usr/bin/env python3
"""PR70 bounded carried-signal exchanges composed with pinned PR71.

PR70 exchanges: Alejandro; PR71 split/next-use compiler: Chafik Boukhalfa.
PR67 profile oracle/cost: Rohan Arun; PR68 live controls: Dominik Scholz.
Composition and integer-entropy pricing prepared with substantial OpenAI
Codex assistance. Discovery heuristic only; exact profiles accept candidates.
"""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import argparse,gzip,json,os,shlex,struct,subprocess,sys,time
if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'round6-pr71/baseline'
sys.path.insert(0,str(BASE/'scripts/experiments'))
import split_pair_engine as compiler
import split_pair_graph as producer
import schedule_variant
import coarse_graph
from binary_frame_math import logs


def main():
 p=argparse.ArgumentParser();p.add_argument('--h',type=int,choices=(23,25),required=True);p.add_argument('--work-dir',type=Path,required=True);p.add_argument('--passes',type=int,default=3);a=p.parse_args()
 a.work_dir.mkdir(parents=True,exist_ok=True)
 source=Path(compiler.__file__)
 expected=json.loads((BASE/'research/split-pair/engine-provenance.json').read_text())['portable_engine_sha256']
 assert sha256(source.read_bytes()).hexdigest()==expected
 executable=a.work_dir/'oracle'
 subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17','-I',str(BASE/'references/frame-compiler/pr48/scripts/partial_swap'),str(BASE/'references/frame-compiler/pr67/research/slot-cost-rank-pair/profile_oracle.cpp'),'-o',str(executable)],check=True)
 compiler.graph=lambda h: schedule_variant.reorder(coarse_graph.graph(h,coarse='columns'));compiler.build=producer.ordered_build(compiler.build,a.h)
 original_match=compiler.match
 def exchange_match(blocks,uses,enabled):
  result=original_match(blocks,uses,enabled)
  edges,chosen,right,stats=result
  initial_cardinality=len(chosen)
  if not a.passes:return result
  owner={x:g for g,b in enumerate(blocks) for x in b['nodes']}
  path=a.work_dir/'matching-oracle.bin'
  with path.open('wb')as stream:
   h=a.h;v=h*(h-1)*(h-2)//6
   stream.write(struct.pack('<6I2Q',h,v,0,len(blocks)+2,0,0,h*(h-1),h*(h-1)))
   stream.write(struct.pack('<2QI',0,0,0));stream.write(struct.pack('<2QI',0,0,h))
   for b in blocks:stream.write(struct.pack('<2QI',*b['frame'],b['rank']))
  oracle=subprocess.Popen([str(executable),str(path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
  weights=[0]+[int(t*sum(logs(t))*10**30//2)for t in range(1,h+1)];cache={}
  def entropy(x,y):
   if (x,y)not in cache:
    oracle.stdin.write(f'{x} {y}\n');oracle.stdin.flush();line=oracle.stdout.readline();assert line
    values=list(map(int,line.split()));assert len(values)==h+1
    cache[x,y]=sum(n*w for n,w in zip(values,weights))
   return cache[x,y]
  def cost(edge):
   g,u,i=edge;p=owner[blocks[g]['inputs'][i]];t=uses[u][1]
   return -entropy(g+2,t+2)+entropy(g+2,1)+entropy(0,p+2)+entropy(p+2,t+2)
  try:
   prices=[]
   for j,e in enumerate(edges):
    prices.append(cost(e))
    if j%20000==0:print('edge prices',j,len(edges),'pairs',len(cache),flush=True)
  finally:
   oracle.stdin.close();assert oracle.wait(timeout=10)==0
  priority=sorted(range(len(edges)),key=lambda e:(prices[e],edges[e]));initial=sum(prices[e]for e in chosen)
  def can(e,drop=None):
   g,u,i=edges[e]
   rows=blocks[g]['outbasis']+[1<<edges[f][2]for f in blocks[g]['selected']if f!=drop]
   return compiler.independent(compiler.basis(rows),1<<i)
  for phase in range(a.passes):
   changes=0
   for e in priority:
    if e in chosen:continue
    g,u,i=edges[e];f=right.get(u)
    if f is not None:
     if prices[e]>=prices[f]:continue
     if not can(e,f if edges[f][0]==g else None):continue
    else:
     f=next((z for z in sorted(blocks[g]['selected'],key=lambda z:(-prices[z],z)) if prices[e]<prices[z]and can(e,z)),None)
     if f is None:continue
    fg,fu,fi=edges[f];chosen.remove(f);blocks[fg]['selected'].remove(f);del right[fu]
    chosen.add(e);blocks[g]['selected'].add(e);assert u not in right;right[u]=e;changes+=1
   stats['carried_signal_exchanges']+=changes
   print('exchanges',phase,changes,flush=True)
   if not changes:break
  assert len(chosen)==len(right)==initial_cardinality
  for g,b in enumerate(blocks):assert len(compiler.basis(b['outbasis']+[1<<edges[e][2]for e in b['selected']]))==len(b['outbasis'])+len(b['selected'])
  stats['exchange_entropy_gain_1e30']=initial-sum(prices[e]for e in chosen)
  stats['exchange_profile_pairs']=len(cache)
  (a.work_dir/f'matching-{a.h}.json').write_text(json.dumps(dict(edges=edges,chosen=sorted(chosen),stats=dict(stats)),separators=(',',':'))+'\n')
  return edges,chosen,right,stats
 compiler.match=exchange_match;compiler.oracles=[];compiler.ORACLE_EXE=str(executable);compiler.ORACLE_INPUT=str(a.work_dir/'compile-oracle.bin');compiler.PENDING_COST=True
 try:result,word=compiler.compile_(a.h,matching=True,reclaim=True,dirty=True)
 finally:
  for process in compiler.oracles:process.stdin.close();assert process.wait(timeout=10)==0
 result.pop('seconds');result['scalar']=compiler.graph(a.h).verify();result['graph_configuration']=dict(producer.configuration(a.h),scalar_node_order='core-reverse',coarse='columns');result['source_sha256']={p.name:sha256(p.read_bytes()).hexdigest()for p in(HERE/'run.py',HERE/'schedule_variant.py',HERE/'coarse_graph.py')}
 raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
 (a.work_dir/f'word-{a.h}.json.gz').write_bytes(gzip.compress(raw,mtime=0))
 (a.work_dir/f'result-{a.h}.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result),flush=True)

if __name__=='__main__':main()
