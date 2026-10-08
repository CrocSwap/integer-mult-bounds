#!/usr/bin/env python3
"""Rebuild the two changed PR24-derived bit producers and exact label audit.
Zhihao Chen, Codex assistance; underlying code credited in SOURCE.json.
"""
import sys,json,gc,tempfile,subprocess,argparse
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(ROOT/'scripts')]
from producer_bit import graph,export
from partial_swap.positive import run as positive
def run():
    with tempfile.TemporaryDirectory(prefix='two-stage-') as tmp:
        work=Path(tmp);programs={}
        for name,source in [('match_exported_dag',ROOT/'scripts/partial_swap/match_exported_dag.cpp'),
                            ('match_positive_dag',ROOT/'scripts/partial_swap/match_positive_dag.cpp'),
                            ('label_audit',HERE/'label_audit.cpp')]:
            programs[name]=work/name
            subprocess.run(['c++','-O3','-std=c++17','-I',str(ROOT/'scripts/partial_swap'),str(source),'-o',str(programs[name])],check=True)
        for h in [53,55]:
            expected=json.loads((HERE/f'producer-{h}.json').read_text())
            c=graph(h);scalar=c.verify();assert scalar==expected['scalar']
            dag=work/f'h{h}.bin';export(c,dag);c.support_in.cache_clear();del c;gc.collect()
            def call(name,*args):return json.loads(subprocess.check_output([str(programs[name]),*map(str,args)],text=True))
            original=call('match_exported_dag',dag,str(dag)+'.links');assert original==expected['original']
            labels=positive(str(dag));assert labels==expected['labels'];gc.collect()
            matched=call('match_positive_dag',dag,str(dag)+'.positive');assert matched==expected['matched']
            audit=call('label_audit',dag,str(dag)+'.positive')
            assert audit==json.loads((HERE/f'labels-{h}.json').read_text())
            print('PASS complete producer, matching, histogram and exact rational labels h='+str(h),flush=True)
if __name__=='__main__':run()
