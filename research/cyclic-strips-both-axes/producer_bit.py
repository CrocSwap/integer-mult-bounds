"""Regenerate the h23 retained-total bit row with cyclic strips (PR104/#36 selected bit pipeline).

Same pipeline as scripts/partial_swap_producer.py: graph -> scalar/frame verify -> export ->
unchanged match_exported_dag -> positive labels recomputed for this graph -> unchanged
match_positive_dag. Only PairedExclusionCircuit.block's leave-one-out layout is replaced, privately.
Rohan Arun with Anthropic Claude assistance, Apache-2.0.
"""
import gc, importlib.util, json, shlex, os, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import partial_swap.paired as base_paired
from partial_swap.graph import graph, export
from partial_swap.positive import run as positive_labels

def build_row(work,cxx=None):
    assert not sys.flags.optimize,'Assertions must remain enabled'
    spec=importlib.util.spec_from_file_location('bit_paired',HERE/'bit_paired.py');layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout)
    assert (layout.LAYOUT,layout.ORDER,layout.CARRY)==('cyclic','id','last')
    cls=base_paired.PairedExclusionCircuit;old_block=cls.block
    cls.block=layout.PairedExclusionCircuit.block;cls.loo=layout.PairedExclusionCircuit.loo
    try:
        work=Path(work);work.mkdir(parents=True,exist_ok=True)
        progs={}
        for name in ('match_exported_dag','match_positive_dag'):
            progs[name]=work/name
            subprocess.run([*shlex.split(cxx or os.environ.get('CXX','c++')),'-O3','-std=c++17',str(ROOT/'scripts/partial_swap'/(name+'.cpp')),'-o',str(progs[name])],check=True)
        h=23;circuit=graph(h);scalar=circuit.verify();frames=circuit.verify_frames()
        dag=work/f'triple_base2_{h}.bin';export(circuit,dag);del circuit;gc.collect()
        original=json.loads(subprocess.check_output([str(progs['match_exported_dag']),str(dag),str(dag)+'.links'],text=True))
        positive_labels(str(dag))
        matched=json.loads(subprocess.check_output([str(progs['match_positive_dag']),str(dag),str(dag)+'.positive'],text=True))
    finally:
        cls.block=old_block;del cls.loo
    assert matched['loss']==h*(h-1) and matched['rank_sum']==h*matched['R']+2*h*(h-1)
    assert original['matched']==matched['matched'],'Positive labels must not enlarge the envelope matching'
    assert matched['R']==matched['c']+matched['q']-matched['matched']
    return dict(h=h,v=matched['v'],c=matched['c'],q=matched['q'],baseline_R=matched['baseline_R'],matching=matched['matched'],
                R=matched['R'],loss=matched['loss'],histogram=matched['histogram'],label_source='positive',
                description='Retained-total aligned triple producer with cyclic interval strips (carry last), base-two recursion, original maximum carrier matching, positive labels.')
if __name__=='__main__':
    import tempfile
    with tempfile.TemporaryDirectory() as d: print(json.dumps(build_row(d)))
