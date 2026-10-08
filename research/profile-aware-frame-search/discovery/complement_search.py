"""Frozen PR62 experiments: choose the invertible completion by future liveness.

All source/output rows and matched carriers remain fixed. The algorithm varies
which independent unit rows complete their basis; unused coordinates retire.
Choosing them with future regions in mind changes which signals can be recycled.
This is discovery. A fresh physical replay/profile is required for a witness.
"""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,sys,time

ROOT=Path(__file__).resolve().parents[2]
UP=ROOT/'work/matrix-synthesis/bridge/pr62'
HERE=Path(__file__).resolve().parent

def load(path,name):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def compiler_source():
    p=UP/'scripts/experiments/binary_frame_compiler.py'
    text=p.read_text(encoding='utf-8')
    text=text.replace("ROOT=Path(__file__).resolve().parents[2]/'references/frame-compiler/pr48'",
                      'ROOT=Path('+repr(str(UP/'references/frame-compiler/pr48'))+')')
    text=text.replace('t0=time.time();c,blocks,uses,value_uses,owner,signal,order,contains=build(h);v=len(c.inputs)',
        't0=time.time();c,blocks,uses,value_uses,owner,signal,order,contains=build(h);v=len(c.inputs)\n place={g:i for i,g in enumerate(order)}')
    old="""   for i in range(len(ins)):
    if independent(echelon,1<<i):rows.append(1<<i);labels.append(('retire',i));echelon=basis(rows)"""
    new="""   if COMPLETION_MODE.startswith('future-span'):
    fresh_basis={}
    for i,y in enumerate(b['inputs']):
     r=signal[y];expr=1<<i
     while r:
      pivot=r.bit_length()-1
      if pivot not in fresh_basis:fresh_basis[pivot]=(r,expr);break
      old,old_expr=fresh_basis[pivot];r^=old;expr^=old_expr
    targets={uses[u][1] for y in b['inputs'] for u in value_uses[y]
             if uses[u][2] is None and place[uses[u][1]]>place[g]
             and contains(b['frame'],blocks[uses[u][1]]['frame'])}
    for target in sorted(targets,key=lambda gg:place[gg])[:24]:
     residues={}
     for x in blocks[target]['outvalues']:
      r=signal[x];expr=0
      for pivot in sorted(fresh_basis,reverse=True):
       if r>>pivot&1:
        rr,ee=fresh_basis[pivot];r^=rr;expr^=ee
      while r:
       pivot=r.bit_length()-1
       if pivot not in residues:residues[pivot]=(r,expr);break
       rr,ee=residues[pivot];r^=rr;expr^=ee
      if not r and expr and independent(echelon,expr):
       rows.append(expr);labels.append(('retire-predictive',expr));echelon=basis(rows);stats['future_complement_rows']+=1
   if COMPLETION_MODE.startswith('kernel'):
    fresh_basis={};kernel=[]
    for i,y in enumerate(b['inputs']):
     r=signal[y];expr=1<<i
     while r:
      pivot=r.bit_length()-1
      if pivot not in fresh_basis:fresh_basis[pivot]=(r,expr);break
      old,old_expr=fresh_basis[pivot];r^=old;expr^=old_expr
     if not r:kernel.append(expr)
    if COMPLETION_MODE=='kernel-sparse':kernel.sort(key=lambda r:(r.bit_count(),r))
    if COMPLETION_MODE=='kernel-reverse':kernel.reverse()
    for r in kernel:
     if independent(echelon,r):
      rows.append(r);labels.append(('retire-zero',r));echelon=basis(rows);stats['zero_complement_rows']+=1
   unit_order=list(range(len(ins)))
   def future_score(i):
    y=b['inputs'][i]
    targets=[target for u in value_uses[y] for _,target,terminal in [uses[u]]
             if terminal is None and place[target]>place[g] and contains(b['frame'],blocks[target]['frame'])]
    near=min((place[target]-place[g] for target in targets),default=10**9)
    if COMPLETION_MODE=='future-near':return (near,-len(targets),i)
    if COMPLETION_MODE=='future-far':return (-near,-len(targets),i)
    if COMPLETION_MODE=='future-many':return (-len(targets),near,i)
    if COMPLETION_MODE=='small-support':return (signal[y].bit_count(),near,i)
    if COMPLETION_MODE=='large-support':return (-signal[y].bit_count(),near,i)
    if COMPLETION_MODE=='reverse':return (-i,)
    return (i,)
   unit_order.sort(key=future_score)
   for i in unit_order:
    if independent(echelon,1<<i):rows.append(1<<i);labels.append(('retire',i));echelon=basis(rows)"""
    assert old in text
    text=text.replace(old,new)
    text=text.replace('else:retired.add(s);spare.append(s)',
        "else:\n     if kind=='retire-zero':assert not slots[s]\n     retired.add(s);spare.append(s)")
    # Reclamation rank is independently selectable from the complement idea.
    text=text.replace('for s in sorted(retired):',
        "for s in sorted(retired,key=lambda s:((-blocks[frames[s]]['rank'],s) if RANK_PRIORITY else (s,))):")
    return 'COMPLETION_MODE="ascending"\nRANK_PRIORITY=False\n'+text

def main():
    p=argparse.ArgumentParser();p.add_argument('--h',type=int,required=True)
    p.add_argument('--mode',choices=['ascending','reverse','future-near','future-far','future-many','small-support','large-support','kernel','kernel-sparse','kernel-reverse','future-span'],required=True)
    p.add_argument('--rank-priority',action='store_true');p.add_argument('--dirty',action='store_true')
    p.add_argument('--matching-cache',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    source=a.output/'compiler.py';source.write_text(compiler_source(),encoding='utf-8',newline='\n')
    compiler=load(source,'new_completion_compiler')
    compiler.graph=load(UP/'research/pair-assembly/pair_graph.py','frozen62_pair_graph').graph
    compiler.COMPLETION_MODE=a.mode;compiler.RANK_PRIORITY=a.rank_priority
    if a.matching_cache:
        cache=json.loads(a.matching_cache.read_text(encoding='utf-8'))
        assert cache['graph_sha256']==hashlib.sha256((UP/'research/pair-assembly/pair_graph.py').read_bytes()).hexdigest()
        def cached_match(blocks,uses,enabled):
            assert enabled
            from collections import Counter
            edges=[(g,u,i)for g,b in enumerate(blocks)for u,i in b['candidates']]
            assert [list(e)for e in edges]==cache['edges']
            chosen=set(cache['chosen']);right={}
            for e in chosen:
                g,u,i=edges[e];assert u not in right;right[u]=e;blocks[g]['selected'].add(e)
            for g,b in enumerate(blocks):
                assert len(compiler.basis(b['outbasis']+[1<<edges[e][2]for e in b['selected']]))==len(b['outbasis'])+len(b['selected'])
            return edges,chosen,right,Counter(cache['stats'])
        compiler.match=cached_match
    started=time.time();result,word=compiler.compile_(a.h,matching=True,reclaim=True,dirty=a.dirty)
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode('utf-8')
    word_path=a.output/f'word-{a.h}.json.gz'
    with word_path.open('wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',mtime=0) as z:z.write(raw)
    result['completion_mode']=a.mode;result['rank_priority']=a.rank_priority
    result['word_sha256']=hashlib.sha256(raw).hexdigest();result['compiler_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    (a.output/f'compiled-{a.h}.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'h':a.h,'mode':a.mode,'roles':result['roles'],'seconds':time.time()-started,'word':str(word_path)}),flush=True)

if __name__=='__main__':main()
