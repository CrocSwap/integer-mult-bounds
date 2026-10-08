"""Local source-pinned experiments on PR71's anchored split/live construction."""
from pathlib import Path
from fractions import Fraction as Q
import argparse,gzip,hashlib,importlib.util,json,math,subprocess,sys,time
HERE=Path(__file__).resolve().parent
UPSTREAM=HERE.parent/'pr71'
PIN='1bef94fd40a746452548c84a4a8f8834670a3113'
ZIG=HERE.parents[1]/'matrix-synthesis/toolchain/zig-x86_64-windows-0.14.1/zig.exe'
CIRCUITS=''' def acquire(g,anchors):
  if reclaim:
   bb={};circuits=[];candidates=[]
   def ins(s):
    row=slots[s];expr=1<<s
    while row:
     p=row.bit_length()-1
     if p not in bb:bb[p]=(row,expr);return None
     old,e=bb[p];row^=old;expr^=e
    return expr
   for s in anchors:
    e=ins(s)
    if e is not None:circuits.append(e)
   for s,target in pending.items():
    if contains(blocks[frames[s]]['frame'],blocks[g]['frame']) and contains(blocks[g]['frame'],blocks[target]['frame']):
     e=ins(s);stats['live_anchor_candidates']+=1
     if e is not None:circuits.append(e)
   for s in sorted(retired,key=lambda s:(-blocks[frames[s]]['rank'],s)):
    if not contains(blocks[frames[s]]['frame'],blocks[g]['frame']):continue
    e=ins(s)
    if e is not None:assert e>>s&1;candidates.append((s,e));circuits.append(e)
   circuits=sorted(set(circuits),key=lambda e:(e.bit_count(),e))[:64]
   prices={}
   def price(s):
    if s not in prices:prices[s]=profile_cost(s,g)
    return prices[s]
   def bits(e):
    out=[]
    while e:
     bit=e&-e;out.append(bit.bit_length()-1);e^=bit
    return out
   expanded=[(e,bits(e))for e in circuits]
   best=None
   for s,e in candidates:
    cost=sum(price(z)for z in bits(e));count=e.bit_count()
    for phase in range(2):
     changed=False
     for circuit,zz in expanded:
      if circuit>>s&1:continue
      delta=sum((-price(z)if e>>z&1 else price(z))for z in zz)
      alternative=e^circuit;newcount=alternative.bit_count()
      if (cost+delta,newcount)<(cost,count):e=alternative;cost+=delta;count=newcount;changed=True;stats['zero_circuit_toggles']+=1
     if not changed:break
    aa=bits(e^(1<<s));key=(cost,len(aa),s)
    if best is None or key<best[0]:best=(key,s,aa)
   if best is not None:
    _,s,aa=best
    fresh=slots[s]
    for z in aa:fresh^=slots[z]
    assert not fresh,'Alternative clearing relation changed signal'
    for a in aa:
     if a in pending:
      assert contains(blocks[g]['frame'],blocks[pending[a]]['frame'])
      stats['live_anchor_xors']+=1
     xor(s,a,g)
    assert not slots[s];retired.remove(s);stats['reclaimed']+=1;stats['clearing_xors']+=len(aa);return s
  return new(g)
'''
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def main():
 p=argparse.ArgumentParser();p.add_argument('--h',type=int,choices=(23,25),required=True);p.add_argument('--strategy',choices=('native','nonlinear','circuits','gate','circuit_gate','carry'),default='nonlinear');a=p.parse_args()
 runner_bytes=Path(__file__).read_bytes();runner_hash=hashlib.sha256(runner_bytes).hexdigest();runner_copy=HERE/f'runner-{runner_hash}.py'
 if not runner_copy.exists():runner_copy.write_bytes(runner_bytes)
 assert subprocess.check_output(['git','-C',str(UPSTREAM),'rev-parse','HEAD'],text=True).strip()==PIN
 source=UPSTREAM/'scripts/experiments/split_pair_engine.py';text=source.read_text()
 needle="ROOT=Path(__file__).resolve().parents[2]/'references/frame-compiler/pr48'"
 assert needle in text;text=text.replace(needle,'ROOT=Path('+repr(str(UPSTREAM/'references/frame-compiler/pr48'))+')')
 if a.strategy!='native':
  old='weights=[0]+[int(t*sum(logs(t))*10**30//2) for t in range(1,h+1)]'
  new='''from fractions import Fraction as Q
 alpha=Q(12854322426487,250000000000000000)
 def moment_weight(t):
  z=alpha*sum(logs(Q(575,t)))/2
  term=Q(1);excess=Q()
  for j in range(1,19):term=term*z/j;excess+=term
  value=t*excess*10**30
  return -(value.numerator//value.denominator)
 weights=[0]+[moment_weight(t)for t in range(1,h+1)]'''
  assert old in text;text=text.replace(old,new)
 if a.strategy in ('circuits','circuit_gate'):
  start=text.index(' def acquire(g,anchors):');end=text.index(' for step,g in enumerate(order):',start)
  text=text[:start]+CIRCUITS+text[end:]
 if a.strategy in ('gate','circuit_gate'):
  needle='   if best is not None:\n    _,s,aa=best'
  gate='''   if best is not None:
    delta=best[0][0]+profile_entropy(0,g+2)+profile_entropy(g+2,1)+moment_weight(h)+moment_weight(575-2*h)
    if delta>=0:
     stats['declined_unfavourable_reclaims']+=1
     return new(g)
    _,s,aa=best'''
  assert text.count(needle)==1;text=text.replace(needle,gate)
 directory=HERE/a.strategy/f'h{a.h}';directory.mkdir(parents=True,exist_ok=True)
 compiler_path=HERE/f'engine-{a.strategy}-{hashlib.sha256(text.encode()).hexdigest()[:12]}.py'
 if compiler_path.exists():assert compiler_path.read_text()==text
 else:compiler_path.write_text(text)
 sys.path.insert(0,str(UPSTREAM/'scripts/experiments'))
 compiler=load('local71_engine_'+a.strategy,compiler_path)
 producer=load('local71_producer',UPSTREAM/'scripts/experiments/split_pair_graph.py')
 compiler.graph=producer.graph;compiler.build=producer.ordered_build(compiler.build,a.h);compiler.PENDING_COST=True
 cache=HERE/f'matching-h{a.h}.json';native_match=compiler.match
 def carry_exchange(blocks,uses,edges,chosen,right,stats):
  if a.strategy!='carry':return edges,chosen,right,stats
  from binary_frame_math import logs
  alpha=Q(12854322426487,250000000000000000)
  def weight(t):
   z=alpha*sum(logs(Q(575,t)))/2;term=Q(1);total=Q()
   for j in range(1,19):term=term*z/j;total+=term
   value=t*total*10**30;return value.numerator//value.denominator
  weights=[0]+[weight(t)for t in range(1,a.h+1)];prices={}
  oracle_file=HERE/f'pair-profiles-h{a.h}.jsonl'
  for line in oracle_file.read_text().splitlines():
   d=json.loads(line);assert sum(t*n for t,n in enumerate(d['blocks']))==d['rank'];prices[d['a'],d['b']]=sum(n*w for n,w in zip(d['blocks'],weights))
  owner={x:g for g,b in enumerate(blocks)for x in b['nodes']}
  def price(g,t):
   rank_g=0 if g==0 else(a.h if g==1 else blocks[g-2]['rank']);rank_t=0 if t==0 else(a.h if t==1 else blocks[t-2]['rank'])
   if rank_g==rank_t:return 0
   return prices[g,t]
  costs=[]
  for g,u,i in edges:
   producer=owner[blocks[g]['inputs'][i]];target=uses[u][1]
   costs.append(price(g+2,target+2)-price(g+2,1)-price(0,producer+2)-price(producer+2,target+2))
  priority=sorted(range(len(edges)),key=lambda e:(costs[e],edges[e]));initial=sum(costs[e]for e in chosen)
  def can(e,drop=None):
   g,u,i=edges[e];rows=blocks[g]['outbasis']+[1<<edges[f][2]for f in blocks[g]['selected']if f!=drop]
   return compiler.independent(compiler.basis(rows),1<<i)
  for phase in range(3):
   changes=0
   for e in priority:
    if e in chosen:continue
    g,u,i=edges[e];f=right.get(u)
    if f is not None:
     if costs[e]>=costs[f]or not can(e,f if edges[f][0]==g else None):continue
    else:
     f=next((z for z in sorted(blocks[g]['selected'],key=lambda z:(-costs[z],z))if costs[e]<costs[z]and can(e,z)),None)
     if f is None:continue
    fg,fu,fi=edges[f];chosen.remove(f);blocks[fg]['selected'].remove(f);del right[fu]
    chosen.add(e);blocks[g]['selected'].add(e);assert u not in right;right[u]=e;changes+=1
   stats['moment_carry_exchanges']+=changes;print('carry exchanges',phase,changes,flush=True)
   if not changes:break
  assert len(chosen)==len(right)
  for g,b in enumerate(blocks):assert len(compiler.basis(b['outbasis']+[1<<edges[e][2]for e in b['selected']]))==len(b['outbasis'])+len(b['selected'])
  stats['quantized_carry_objective_gain']=initial-sum(costs[e]for e in chosen)
  compiler.CARRY_ORACLE_SHA256=digest(oracle_file)
  return edges,chosen,right,stats
 def cached_match(blocks,uses,enabled):
  expected=[(g,u,i)for g,b in enumerate(blocks)for u,i in b['candidates']]
  if enabled and cache.exists():
   data=json.loads(cache.read_text());assert data['source_pin']==PIN;edges=list(map(tuple,data['edges']));assert edges==expected
   chosen=set(data['chosen']);right={}
   for e in chosen:
    g,u,i=edges[e];blocks[g]['selected'].add(e);assert u not in right;right[u]=e
   for g,b in enumerate(blocks):assert len(compiler.basis(b['outbasis']+[1<<edges[e][2]for e in b['selected']]))==len(b['outbasis'])+len(b['selected'])
   print('reused matching',len(chosen),flush=True);return carry_exchange(blocks,uses,edges,chosen,right,compiler.Counter(data['stats']))
  result=native_match(blocks,uses,enabled);edges,chosen,right,stats=result
  cache.write_text(json.dumps(dict(source_pin=PIN,edges=edges,chosen=sorted(chosen),stats=dict(stats)))+'\n');return carry_exchange(blocks,uses,edges,chosen,right,stats)
 compiler.match=cached_match
 oracle=HERE/'profile-oracle.exe';oracle_source=UPSTREAM/'references/frame-compiler/pr67/research/slot-cost-rank-pair/profile_oracle.cpp'
 if not oracle.exists():subprocess.run([str(ZIG),'c++','-O3','-std=c++17','-I',str(UPSTREAM/'references/frame-compiler/pr48/scripts/partial_swap'),str(oracle_source),'-o',str(oracle)],check=True)
 compiler.oracles=[];compiler.ORACLE_EXE=str(oracle);compiler.ORACLE_INPUT=str(directory/'oracle-input.bin')
 began=time.perf_counter()
 try:result,word=compiler.compile_(a.h,matching=True,reclaim=True,dirty=True)
 finally:
  for process in compiler.oracles:
   process.stdin.close();assert process.wait(timeout=10)==0
 raw=(json.dumps(word,separators=(',',':'))+'\n').encode();path=directory/'word.json.gz'
 with path.open('xb')as out:
  with gzip.GzipFile(fileobj=out,mode='wb',mtime=0)as archive:archive.write(raw)
 receipt=dict(source_pin=PIN,strategy=a.strategy,compiled=result,word_sha256=hashlib.sha256(raw).hexdigest(),gzip_sha256=digest(path),source_engine_sha256=digest(source),local_engine_sha256=digest(compiler_path),local_engine=compiler_path.name,runner_sha256=runner_hash,runner=runner_copy.name,graph_source_sha256=digest(UPSTREAM/'scripts/experiments/split_pair_graph.py'),oracle_source_sha256=digest(oracle_source),elapsed_seconds=time.perf_counter()-began,
  scope='proposal with full compiler dirty basis both orientations; independent paid profile and assembly required',no_global_optimality_claim=True)
 if a.strategy=='carry':receipt['carry_oracle_sha256']=compiler.CARRY_ORACLE_SHA256
 (directory/'compiled.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(dict(strategy=a.strategy,h=a.h,R=result['roles'],xor=result['elementary_xors'],word=str(path))),flush=True)
if __name__=='__main__':main()
