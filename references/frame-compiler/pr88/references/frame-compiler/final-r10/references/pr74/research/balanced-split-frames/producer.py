#!/usr/bin/env python3
"""Balanced coarse sums + anchored split/live frames + core ordering and coordinates.

Composition for Thomas DiFiore with OpenAI Codex assistance. Apache-2.0.
PR69 coarse sums: eumemic. PR71 split/live composition: Chafik Boukhalfa.
Graph: Avi Eisenberg PR62; split operation: Rohan Garg PR59; reclamation:
Rohan Arun PR65/67, Dominik Scholz PR63/68, eumemic PR57. Original notices
and exact sources are retained under references/frame-compiler/pr69 and pr71.
"""
import sys
if sys.flags.optimize: raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
from pathlib import Path
from hashlib import sha256
import argparse,ast,gzip,importlib.util,json,types
from concurrent.futures import ProcessPoolExecutor
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DEP=ROOT/'references/frame-compiler/pr71'
sys.path.insert(0,str(DEP/'scripts/experiments'))
import split_pair_graph as provider
import split_pair_compiler as ancestor
from binary_frame_replay import replay


def check_sources():
    for folder in (DEP,ROOT/'references/frame-compiler/pr69'):
        manifest=json.loads((folder/'SOURCE.json').read_text())
        for name,digest in manifest['files'].items():
            assert sha256((folder/name).read_bytes()).hexdigest()==digest,name
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    required={str((HERE/name).relative_to(ROOT)) for name in ('producer.py','check.py','graph_audit.py','independent_check.py','selection.json')}
    assert required <= set(manifest['files']), 'Incomplete selected source closure'
    for name,digest in manifest['files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name


def reorder(c):
    groups={}
    for x in sorted(c.active):
        if c.args[x]: groups.setdefault((c.core[x],c.union[x]),[]).append(x)
    def key(item):
        (core,cover),nodes=item
        return cover.bit_count()-core.bit_count(),-core,cover,min(nodes)
    ids=list(range(len(c.inputs)+1))+[x for _,nodes in sorted(groups.items(),key=key) for x in nodes]
    mapping={x:i for i,x in enumerate(ids)}
    args,core,cover,provenance=c.args,c.core,c.union,c.provenance
    c.args=[tuple(mapping[y] for y in args[x]) if args[x] else None for x in ids]
    c.core=[core[x] for x in ids];c.union=[cover[x] for x in ids]
    c.provenance=[provenance[x] for x in ids]
    c.active={mapping[x] for x in c.active};c.outputs={k:mapping[v] for k,v in c.outputs.items()}
    c.support_in.cache_clear()
    c.verify()
    return c


def graph(h,ordered=True):
    source=Path(provider._graph.__file__).read_text()
    original=ROOT/'references/frame-compiler/pr69/scripts/experiments/balanced_coarse_compiler.py'
    replacements={}
    for node in ast.parse(original.read_text()).body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in ('BEFORE','AFTER'):
                    replacements[target.id]=ast.literal_eval(node.value)
    assert source.count(replacements['BEFORE'])==1
    module=types.ModuleType('balanced_split_private_graph');module.__file__=provider._graph.__file__
    exec(compile(source.replace(replacements['BEFORE'],replacements['AFTER']),module.__file__+':balanced-coarse','exec'),module.__dict__)
    previous=provider._graph
    try:
        provider._graph=module
        c=provider.graph(h)
    finally:
        provider._graph=previous
    return reorder(c) if ordered else c


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


def compile_axis(h):
    check_sources()
    config=json.loads((HERE/'selection.json').read_text())['axes'][str(h)]
    previous_graph,previous_order=provider.graph,provider.ordered_build
    # graph() calls the original provider; keep that callable private while
    # the inherited driver resolves the selected composed graph dynamically.
    original_graph=previous_graph
    def selected_graph(dimension):
        provider.graph=original_graph
        try:return graph(dimension)
        finally:provider.graph=selected_graph
    try:
        provider.graph=selected_graph
        provider.ordered_build=lambda original,dimension:original
        compiled,word=ancestor.compile_axis(h)
    finally:
        provider.graph,provider.ordered_build=previous_graph,previous_order
    compiled['graph_configuration']=config
    word=relabel(word,config['coordinate_permutation'])
    raw=(json.dumps(word,separators=(',',':'))+'\n').encode()
    path=HERE/f'word-{h}.json.gz'
    with path.open('wb') as stream:
        with gzip.GzipFile(filename='',fileobj=stream,mode='wb',mtime=0) as archive:archive.write(raw)
    receipt=replay(path)
    assert sha256(raw).hexdigest()==config['expected_word_sha256']
    axis=dict(configuration=config,compiled=compiled,replay=receipt,
              word_sha256=sha256(raw).hexdigest(),gzip_sha256=sha256(path.read_bytes()).hexdigest())
    (HERE/f'axis-{h}.json').write_text(json.dumps(axis,indent=2)+'\n')
    print(f'PASS fresh balanced/split/core word h={h}, roles={receipt["roles"]}',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--h',type=int,choices=(23,25));args=parser.parse_args()
    if args.h:compile_axis(args.h)
    else:
        with ProcessPoolExecutor(max_workers=2) as pool:list(pool.map(compile_axis,(23,25)))
