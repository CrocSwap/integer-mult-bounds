#!/usr/bin/env python3
"""Compose PR69 balanced coarse sums with pinned PR71/73 anchored split graph.

Only one exact source fragment changes. Preserves upstream notices and source
files; the new module exists only in memory. Authoritative inherited sources are
verified before use. Prepared with Codex; no finite/profile claim without replay.
"""
import argparse, gzip, hashlib, json, subprocess, sys, types, time
from pathlib import Path
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
PIN='253ecc88faeed55a950c76026d1fe67a7f690123'
COARSE_PIN='91aa1f17e6e3fc063241686a41a34ddd0dc24c50'
BEFORE='''            coarse = {(i, j): self.total([e(a, b) for a in groups[i] for b in groups[j]])
                      for i, j in combinations(range(ng), 2)}'''
AFTER='''            def coarse_sum(i, j):
                columns = [self.total([e(a,b) for a in groups[i]]) for b in groups[j]]
                return self.total(columns)
            coarse = {(i,j):coarse_sum(i,j) for i,j in combinations(range(ng),2)}'''

def setup(root):
    head=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    assert head==PIN,(head,PIN)
    assert not subprocess.check_output(['git','-C',str(root),'status','--porcelain','--untracked-files=no'],text=True).strip(), 'Tracked source modifications'
    sys.path.insert(0,str(root/'scripts/experiments'))
    import split_pair_graph as producer
    from split_pair_compose import check_sources
    check_sources()
    old=producer._graph
    source=Path(old.__file__).read_text()
    assert source.count(BEFORE)==1,'Exact PR69 coarse-source anchor changed'
    modified=source.replace(BEFORE,AFTER)
    module=types.ModuleType('balanced_split_private_graph')
    module.__file__=old.__file__
    exec(compile(modified,old.__file__+'+pr69-balanced', 'exec'), module.__dict__)
    producer._graph=module
    return producer,dict(base_pin=PIN,coarse_transformation_pin=COARSE_PIN,
        original_graph_sha256=hashlib.sha256(source.encode()).hexdigest(),
        transformed_graph_sha256=hashlib.sha256(modified.encode()).hexdigest(),
        experiment_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        exact_replacements=1,configuration='PR71 anchored [1,1,2], unchanged region ordering and live/retired engine',
        transformation=dict(before=BEFORE,after=AFTER))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream',type=Path,required=True)
    p.add_argument('--h',type=int,choices=(23,25),required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--compile',action='store_true')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    start=time.monotonic();producer,source=setup(a.upstream.resolve())
    g=producer.graph(a.h);graph=g.verify()
    result=dict(source=source,h=a.h,graph=graph)
    print(json.dumps(dict(stage='graph',seconds=time.monotonic()-start,**graph)),flush=True)
    if a.compile:
        from split_pair_compiler import compile_axis
        compiled,word=compile_axis(a.h)
        assert compiled['scalar']==graph
        raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
        path=a.output/f'balanced-split-word-{a.h}.json.gz'
        path.write_bytes(gzip.compress(raw,mtime=0))
        result.update(compiled=compiled,word_sha256=hashlib.sha256(raw).hexdigest(),
                      gzip_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        print(json.dumps(dict(stage='compiled',seconds=time.monotonic()-start,**compiled)),flush=True)
    (a.output/f'balanced-split-{a.h}.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
