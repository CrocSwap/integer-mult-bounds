#!/usr/bin/env python3
"""Rebuild PR24-derived bit producers at selected dimensions plus the PR29 exact label audit.
Mirrors research/two-stage/producer.py (Zhihao Chen, PR29) but compares complete fresh records
against the selected (47,45) records. Underlying code: icekylinx PR24/18/10.
"""
import sys,json,gc,tempfile,subprocess,os
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];TS=ROOT/'research/two-stage'
sys.path[:0]=[str(TS),str(ROOT/'scripts')]
from producer_bit import graph,export
from partial_swap.positive import run as positive
def run(hs):
    with tempfile.TemporaryDirectory(prefix='two-stage-dimensions-') as tmp:
        work=Path(tmp);programs={}
        for name,source in [('match_exported_dag',ROOT/'scripts/partial_swap/match_exported_dag.cpp'),
                            ('match_positive_dag',ROOT/'scripts/partial_swap/match_positive_dag.cpp'),
                            ('label_audit',TS/'label_audit.cpp')]:
            programs[name]=work/name
            subprocess.run([os.environ.get('CXX','c++'),'-O3','-std=c++17','-I',str(ROOT/'scripts/partial_swap'),str(source),'-o',str(programs[name])],check=True)
        for h in hs:
            c=graph(h);scalar=c.verify()
            dag=work/f'h{h}.bin';export(c,dag);c.support_in.cache_clear();del c;gc.collect()
            def call(name,*args):return json.loads(subprocess.check_output([str(programs[name]),*map(str,args)],text=True))
            original=call('match_exported_dag',dag,str(dag)+'.links')
            labels=positive(str(dag));gc.collect()
            matched=call('match_positive_dag',dag,str(dag)+'.positive')
            audit=call('label_audit',dag,str(dag)+'.positive')
            rec=dict(scalar=scalar,labels=labels,original=original,matched=matched)
            assert rec==json.loads((HERE/f'producer-{h}.json').read_text()), 'Producer mismatch: '+str(h)
            assert audit==json.loads((HERE/f'labels-{h}.json').read_text()), 'Label audit mismatch: '+str(h)
            print('DONE h',h,'R',matched['R'],'loss',matched['loss'],'audit',audit,flush=True)
if __name__=='__main__':run([45,47])
