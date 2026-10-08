"""Frozen-through-PR62 local reclamation experiment; no external operations."""
from pathlib import Path
import argparse,gzip,hashlib,importlib.util,json,sys,time
import math

HERE=Path(__file__).resolve().parent
FROZEN=HERE.parents[1]/'matrix-synthesis/bridge/pr62'

ACQUIRE=''' def acquire(g,anchors):
  if reclaim:
   bb={}
   def ins(s,add=True):
    row=slots[s];expr=1<<s
    while row:
     p=row.bit_length()-1
     if p not in bb:
      if add:bb[p]=(row,expr)
      return None
     old,e=bb[p];row^=old;expr^=e
    return expr
   for s in anchors:ins(s)
   eligible=[s for s in retired if contains(blocks[frames[s]]['frame'],blocks[g]['frame'])]
   candidates=[]
   if STRATEGY in ('all_collateral','anchor_first'):
    zeros=[s for s in eligible if not slots[s]]
    if zeros:
     s=min(zeros,key=lambda s:(-blocks[frames[s]]['rank'],s))
     retired.remove(s);stats['reclaimed']+=1;stats['zero_signal_reclaims']+=1
     return s
   def candidate(s,e):
    assert e>>s&1;e^=1<<s;aa=[]
    while e:
     bit=e&-e;aa.append(bit.bit_length()-1);e^=bit
    growth=sum(blocks[g]['rank']-blocks[frames[z]]['rank'] for z in set([s]+aa))
    collateral=[z for z in aa if z in retired and blocks[frames[z]]['rank']<blocks[g]['rank']]
    collateral_growth=sum(blocks[g]['rank']-blocks[frames[z]]['rank'] for z in collateral)
    if COLLECT_PAIRS:
     for z in set([s]+aa):
      LOCAL_PAIRS.add((frames[z]+2,g+2));LOCAL_PAIRS.add((frames[z]+2,1))
     LOCAL_PAIRS.add((g+2,1))
    price=0.0
    if STRATEGY=='profile_cost':
     price=PROFILE_COST(frames[s]+2,g+2,blocks[g]['rank']-blocks[frames[s]]['rank'])-PROFILE_COST(frames[s]+2,1,h-blocks[frames[s]]['rank'])
     for z in set(aa):
      if frames[z]!=g:
       price+=PROFILE_COST(frames[z]+2,g+2,blocks[g]['rank']-blocks[frames[z]]['rank'])+PROFILE_COST(g+2,1,h-blocks[g]['rank'])-PROFILE_COST(frames[z]+2,1,h-blocks[frames[z]]['rank'])
    candidates.append((s,aa,growth,len(collateral),collateral_growth,price))
   if STRATEGY=='anchor_first':
    for s in eligible:
     e=ins(s,False)
     if e is not None:candidate(s,e)
   if not candidates:
    for s in sorted(eligible,key=lambda s:RETIRED_ORDER):
     e=ins(s)
     if e is not None:candidate(s,e)
   if candidates:
    if STRATEGY=='all_growth':key=lambda v:(v[2],len(v[1]),-blocks[frames[v[0]]]['rank'],v[0])
    elif STRATEGY=='all_rank':key=lambda v:(-blocks[frames[v[0]]]['rank'],len(v[1]),v[2],v[0])
    elif STRATEGY=='all_collateral':key=lambda v:(v[3],v[4],len(v[1]),-blocks[frames[v[0]]]['rank'],v[0])
    elif STRATEGY=='profile_cost':key=lambda v:(v[5],v[4],len(v[1]),-blocks[frames[v[0]]]['rank'],v[0])
    else:key=lambda v:(len(v[1]),v[2],-blocks[frames[v[0]]]['rank'],v[0])
    s,aa,*_=min(candidates,key=key)
    for a in aa:xor(s,a,g)
    assert not slots[s];retired.remove(s);stats['reclaimed']+=1;stats['clearing_xors']+=len(aa)
    stats['dependency_candidates_considered']+=len(candidates)
    return s
  return new(g)
'''


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--h',type=int,choices=(23,25),required=True)
    ap.add_argument('--strategy',default='rank_desc');ap.add_argument('--weighted',action='store_true');ap.add_argument('--exchange',action='store_true');args=ap.parse_args()
    assert not(args.weighted and args.exchange)
    runner_bytes=Path(__file__).read_bytes();runner_hash=hashlib.sha256(runner_bytes).hexdigest()
    runner_copy=HERE/f'runner-{runner_hash}.py'
    if not runner_copy.exists():runner_copy.write_bytes(runner_bytes)
    source=FROZEN/'scripts/experiments/binary_frame_compiler.py'
    text=source.read_text()
    old="ROOT=Path(__file__).resolve().parents[2]/'references/frame-compiler/pr48'"
    new="ROOT=Path(__file__).resolve().parents[2]/'matrix-synthesis/bridge/pr62/references/frame-compiler/pr48'"
    assert old in text;text=text.replace(old,new)
    if args.strategy=='rank_desc':
        text=text.replace('for s in sorted(retired):',"for s in sorted(retired,key=lambda s:(-blocks[frames[s]]['rank'],s)):")
    elif args.strategy in ('all_growth','all_rank','all_xors','all_collateral','anchor_first','profile_collect') or args.strategy.startswith('profile_cost'):
        start=text.index(' def acquire(g,anchors):');end=text.index(' for step,g in enumerate(order):',start)
        selector='all_growth' if args.strategy=='profile_collect' else ('profile_cost' if args.strategy.startswith('profile_cost') else args.strategy)
        retired_order="(-blocks[frames[s]]['rank'],s)"
        if args.strategy.endswith('_asc'):retired_order="(blocks[frames[s]]['rank'],s)"
        elif args.strategy.endswith('_signal'):retired_order="(slots[s].bit_count(),-blocks[frames[s]]['rank'],s)"
        elif args.strategy.endswith('_signal_desc'):retired_order="(-slots[s].bit_count(),-blocks[frames[s]]['rank'],s)"
        text=text[:start]+ACQUIRE.replace('STRATEGY',repr(selector)).replace('COLLECT_PAIRS',str(args.strategy.startswith('profile_'))).replace('RETIRED_ORDER',retired_order)+text[end:]
        text=text.replace('def compile_(h,', 'LOCAL_PAIRS=set()\n\ndef compile_(h,')
    elif args.strategy!='baseline':raise ValueError('unknown strategy')
    if args.weighted:
        needle=' chosen=set();right={};stats=Counter()'
        assert text.count(needle)==1
        text=text.replace(needle," edges.sort(key=lambda v:(WEIGHTED_EDGE_COST(v),v))\n byblock=[[]for b in blocks]\n for e,(g,u,i)in enumerate(edges):byblock[g].append(e)\n"+needle)
    label=args.strategy+('_weighted' if args.weighted else '')+('_exchange' if args.exchange else '')
    directory=HERE/label/f'h{args.h}';directory.mkdir(parents=True,exist_ok=True)
    compiler_path=HERE/f'compiler_{label}_{hashlib.sha256(text.encode()).hexdigest()[:12]}.py'
    if compiler_path.exists():assert compiler_path.read_text()==text
    else:compiler_path.write_text(text)
    compiler=load('local_compiler_'+args.strategy,compiler_path)
    if args.strategy.startswith('profile_cost') or args.weighted or args.exchange:
        profile_path=HERE/f'pair-profiles-h{args.h}.jsonl'
        values={}
        for line in profile_path.read_text().splitlines():
            row=json.loads(line);assert sum(t*n for t,n in enumerate(row['blocks']))==row['rank']
            values[row['a'],row['b']]=sum(n*t*math.expm1(0.00005103*math.log(575/t))for t,n in enumerate(row['blocks'])if t and n)
        missing=set()
        def profile_cost(a,b,rank):
            if not rank:return 0.0
            if (a,b)not in values:missing.add((a,b));return rank*math.expm1(0.00005103*math.log(575/rank))
            return values[a,b]
        compiler.PROFILE_COST=profile_cost
    graph_path=FROZEN/'research/pair-assembly/pair_graph.py'
    graph=load('frozen_pair_graph',graph_path);compiler.graph=graph.graph
    cache=HERE/f'matching-h{args.h}{("-weighted-"+digest(profile_path)[:12]) if args.weighted else ""}.json'
    native_match=compiler.match
    def cached_match(blocks,uses,enabled):
        if not enabled:return native_match(blocks,uses,enabled)
        expected=[(g,u,i)for g,b in enumerate(blocks)for u,i in b['candidates']]
        if args.weighted or args.exchange:
            owner={x:g for g,b in enumerate(blocks)for x in b['nodes']}
            def cost(v):
                g,u,i=v;producer=owner[blocks[g]['inputs'][i]];target=uses[u][1]
                def price(a,b):
                    ra=0 if a==0 else (args.h if a==1 else blocks[a-2]['rank'])
                    rb=0 if b==0 else (args.h if b==1 else blocks[b-2]['rank'])
                    return profile_cost(a,b,rb-ra)
                return price(g+2,target+2)-price(g+2,1)-price(0,producer+2)-price(producer+2,target+2)
            compiler.WEIGHTED_EDGE_COST=cost
            if args.weighted:expected.sort(key=lambda v:(cost(v),v))
        def improve(edges,chosen,right,stats):
            if not args.exchange:return edges,chosen,right,stats
            prices=[cost(e)for e in edges];priority=sorted(range(len(edges)),key=lambda e:(prices[e],edges[e]))
            startcost=sum(prices[e]for e in chosen)
            def can(e,drop=None):
                g,u,i=edges[e]
                rows=blocks[g]['outbasis']+[1<<edges[f][2]for f in blocks[g]['selected']if f!=drop]
                return compiler.independent(compiler.basis(rows),1<<i)
            for phase in range(3):
                changes=0
                for e in priority:
                    if e in chosen:continue
                    g,u,i=edges[e];f=right.get(u)
                    if f is not None:
                        if prices[e]>=prices[f]-1e-14:continue
                        if not can(e,f if edges[f][0]==g else None):continue
                    else:
                        f=next((z for z in sorted(blocks[g]['selected'],key=lambda z:-prices[z])if prices[e]<prices[z]-1e-14 and can(e,z)),None)
                        if f is None:continue
                    fg,fu,fi=edges[f];chosen.remove(f);blocks[fg]['selected'].remove(f);del right[fu]
                    chosen.add(e);blocks[g]['selected'].add(e);assert u not in right;right[u]=e;changes+=1
                stats['local_moment_exchanges']+=changes
                print('moment exchanges',phase,changes,flush=True)
                if not changes:break
            stats['local_moment_discovery_gain']=startcost-sum(prices[e]for e in chosen)
            assert len(chosen)==len(right)
            for g,b in enumerate(blocks):assert len(compiler.basis(b['outbasis']+[1<<edges[e][2]for e in b['selected']]))==len(b['outbasis'])+len(b['selected'])
            return edges,chosen,right,stats
        if cache.exists():
            data=json.loads(cache.read_text());assert data['graph_sha256']==digest(graph_path)
            assert data['compiler_sha256']==digest(source)
            edges=[tuple(e)for e in data['edges']];chosen=set(data['chosen']);right={}
            assert edges==expected
            for e in chosen:
                g,u,i=edges[e];blocks[g]['selected'].add(e);assert u not in right;right[u]=e
            for g,b in enumerate(blocks):
                assert len(compiler.basis(b['outbasis']+[1<<edges[e][2]for e in b['selected']]))==len(b['outbasis'])+len(b['selected'])
            print('reused exact frozen matching',len(chosen),flush=True)
            return improve(edges,chosen,right,compiler.Counter(data['stats']))
        result=native_match(blocks,uses,enabled);edges,chosen,right,stats=result
        cache.write_text(json.dumps(dict(graph_sha256=digest(graph_path),compiler_sha256=digest(source),edges=edges,chosen=sorted(chosen),stats=dict(stats)))+'\n')
        return improve(edges,chosen,right,stats)
    compiler.match=cached_match
    began=time.perf_counter();result,word=compiler.compile_(args.h,matching=True,reclaim=True,dirty=True)
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
    path=directory/'word.json.gz'
    with path.open('xb')as stream:
        with gzip.GzipFile(fileobj=stream,mode='wb',mtime=0)as archive:archive.write(raw)
    record=dict(strategy=label,axis=args.h,compiled=result,word_sha256=hashlib.sha256(raw).hexdigest(),
        gzip_sha256=digest(path),graph_sha256=digest(graph_path),baseline_compiler_sha256=digest(source),
        experimental_compiler_sha256=digest(compiler_path),elapsed_seconds=time.perf_counter()-began,
        experiment_runner_sha256=runner_hash,experiment_runner=runner_copy.name,
        frozen_source_commit='ad0f25ff7b23cff7f08ad237c2254e6ecf74257e',
        scope='complete compiler dirty-basis controls; independent literal replay/profiles still required',
        no_global_optimality_claim=True,no_external_write=True)
    if args.weighted:record['matching_discovery']='moment-ordered greedy then unweighted augmenting paths; maximum cardinality only, no weighted optimum claim';record['matching_cost_oracle_sha256']=digest(profile_path)
    if args.exchange:record['matching_discovery']='three bounded improving single-edge exchange passes from original exact maximum-cardinality matching; no global weight optimum claim';record['matching_cost_oracle_sha256']=digest(profile_path)
    if args.strategy.startswith('profile_'):
        (directory/'candidate-frames.json').write_text(json.dumps(dict(h=args.h,frames=word['frames'],pairs=sorted(compiler.LOCAL_PAIRS)))+'\n')
        if args.strategy.startswith('profile_cost'):record['missing_local_profile_pairs']=len(missing);record['local_profile_oracle_sha256']=digest(profile_path)
    (directory/'compiled.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k]for k in('strategy','axis','elapsed_seconds')}|dict(roles=result['roles'],
        elementary_xors=result['elementary_xors'],clearing_xors=result['stats'].get('clearing_xors'),
        reclaimed=result['stats'].get('reclaimed'),word_file=str(path)),indent=2),flush=True)


if __name__=='__main__':main()
