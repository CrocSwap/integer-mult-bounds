#!/usr/bin/env python3
"""Rebuild both original-envelope scalar DAGs and exact fixed-I+J profiles.

Producer/basis provenance: icekylinx PR24/32, Zhihao Chen PR29, all retained
predecessors. Dimension adaptation/composition with GPT-6 Astra assistance.
No PDFs. All large intermediates stay in temporary storage.
"""
import gc,json,os,shlex,subprocess,sys,tempfile
from pathlib import Path
from hashlib import sha256

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'research/two-stage'),str(ROOT/'scripts')]
from producer_bit import graph,export
from partial_swap.positive import read

def original_labels(path):
    h,v,n,q,args,core,cover,roots,kind,active=read(str(path));full=(1<<h)-1
    additions=0;dependencies=0;sources=0
    for x in range(1,n):
        if not active[x]:continue
        assert not core[x]&~cover[x]
        if not args[2*x]:
            assert core[x]==cover[x] and core[x].bit_count()==3;sources+=1
            continue
        assert core[x].bit_count() in (1,2);additions+=1
        for y in args[2*x:2*x+2]:
            assert active[y] and y<x
            assert not core[x]&~core[y] and not cover[y]&~cover[x]
            dependencies+=1
    for x,total in zip(roots,kind):
        assert core[x].bit_count()==1
        if total:assert cover[x]==full
        else:assert (full^cover[x]).bit_count()==2
    assert sources==v and dependencies==2*additions
    return dict(h=h,exact_original_envelopes=additions,exact_dependency_inclusions=dependencies,
                output_frames=q,source_lines=v,reverse_complements_by_exact_duality=True)

def run():
    assert not sys.flags.optimize,'Assertions must remain enabled'
    pinned=json.loads((ROOT/'research/two-stage/SOURCE.json').read_text())
    for name,digest in pinned['source_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    receipt={}
    with tempfile.TemporaryDirectory(prefix='fixed-I-plus-J-') as tmp:
        work=Path(tmp);exe=work/'profiles'
        subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',
                        '-I',str(ROOT/'scripts/partial_swap'),str(HERE/'rankone_profiles.cpp'),'-o',str(exe)],check=True)
        for h in (45,47):
            c=graph(h);scalar=c.verify();dag=work/f'h{h}.bin';export(c,dag)
            c.support_in.cache_clear();del c;gc.collect()
            labels=original_labels(dag)
            raw=subprocess.check_output([str(exe),str(dag),str(dag)+'.links'],text=True)
            original=json.loads(raw);expected=json.loads((ROOT/f'research/two-stage-dimensions/producer-{h}.json').read_text())
            assert scalar==expected['scalar'] and original==expected['original']
            actual=json.loads(Path(str(dag)+'.round3_rankone_certified_profiles.json').read_text())
            assert actual==json.loads((HERE/f'profiles-{h}.json').read_text())
            receipt[h]=dict(scalar=scalar,labels=labels,original=original,profile=actual)
            print('PASS full fixed-basis replay h',h,flush=True)
    return receipt

if __name__=='__main__':
    run()
