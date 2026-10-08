"""Composable carried-signal exchanges for an inherited frame compiler.

PR70 exchange methodology: Alejandro Zarzuelo Urdiales.
PR76 integer profile-entropy pricing and one-edge passes: Dominik Scholz,
commit 2333abcea79793fe301b479a7c971cc2be45596c, with OpenAI assistance.
The selected two-edge cycles and factory packaging are prepared for
Thomas DiFiore with substantial OpenAI Codex assistance. Apache-2.0.
Every candidate still needs complete dirty replay and actual paid profiles.
"""
from pathlib import Path
from types import SimpleNamespace
import json,struct,subprocess,importlib.util,sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MATH_PATH=ROOT/'references/frame-compiler/pr71/scripts/experiments/binary_frame_math.py'
_math_spec=importlib.util.spec_from_file_location('aligned_exchange_pinned_math',MATH_PATH)
_math=importlib.util.module_from_spec(_math_spec)
_math_spec.loader.exec_module(_math)
logs=_math.logs


def install(compiler, oracle_executable, h, work_dir, passes=3,
            two_passes=1, permutation=None, record_matching=False):
    """Mutate this private compiler's matching callback; leave synthesis intact."""
    a=SimpleNamespace(h=h,work_dir=Path(work_dir),passes=passes,
                      two_passes=two_passes,price_coordinates=permutation is not None)
    assert h in (23,25) and passes==3 and two_passes==1, 'Changed selected exchange configuration'
    assert permutation is not None, 'Selected policy requires explicit coordinate pricing'
    a.work_dir.mkdir(parents=True,exist_ok=True)
    executable=Path(oracle_executable)
    if permutation is not None:assert sorted(permutation)==list(range(h))
    def permute_mask(bits):return sum(1<<permutation[i] for i in range(h) if bits>>i&1)
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
      for b in blocks:
       frame=tuple(permute_mask(v) for v in b['frame']) if a.price_coordinates else b['frame']
       stream.write(struct.pack('<2QI',*frame,b['rank']))
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
     # A bounded weighted two-edge cycle: exchange f,z for e,w, with
     # g(e)=g(z), g(w)=g(f), use(e)=use(f), use(w)=use(z).
     # The two donor blocks differ, so each local independence check is exact.
     # Both use assignments remain unique and cardinality remains unchanged.
     by_block_use={(g,u):j for j,(g,u,i) in enumerate(edges)}
     assert len(by_block_use)==len(edges)
     for phase in range(a.two_passes):
      changes=0
      for e in priority:
       if e in chosen:continue
       g,u,i=edges[e];f=right.get(u)
       if f is None:continue
       fg=edges[f][0]
       if fg==g:continue
       best=None
       for z in sorted(blocks[g]['selected']):
        w=by_block_use.get((fg,edges[z][1]))
        if w is None or w in chosen:continue
        delta=prices[e]+prices[w]-prices[f]-prices[z]
        if delta>=0:continue
        if not can(e,z) or not can(w,f):continue
        key=(delta,z,w)
        if best is None or key<best:best=key
       if best is None:continue
       _,z,w=best
       for old_edge in (f,z):
        old_g,old_u,_=edges[old_edge]
        chosen.remove(old_edge);blocks[old_g]['selected'].remove(old_edge);del right[old_u]
       for new_edge in (e,w):
        new_g,new_u,_=edges[new_edge]
        chosen.add(new_edge);blocks[new_g]['selected'].add(new_edge);assert new_u not in right;right[new_u]=new_edge
       changes+=1
      stats['carried_two_exchange_pairs']+=changes
      print('two-edge exchanges',phase,changes,flush=True)
      if not changes:break
     assert len(chosen)==len(right)==initial_cardinality
     for g,b in enumerate(blocks):assert len(compiler.basis(b['outbasis']+[1<<edges[e][2]for e in b['selected']]))==len(b['outbasis'])+len(b['selected'])
     stats['exchange_entropy_gain_1e30']=initial-sum(prices[e]for e in chosen)
     stats['exchange_profile_pairs']=len(cache)
     if record_matching:(a.work_dir/f'matching-{a.h}.json').write_text(json.dumps(dict(edges=edges,chosen=sorted(chosen),stats=dict(stats)),separators=(',',':'))+'\n')
     return edges,chosen,right,stats
    compiler.match=exchange_match
    return original_match
