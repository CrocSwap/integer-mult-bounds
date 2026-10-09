"""Exact finite refinement of icekylinx's conditional PR104 construction.

Copyright 2026 Rohan Arun, Apache-2.0. Prepared with OpenAI Codex assistance.
Does not formally verify the inherited analytic or all-size tape interfaces.
"""
import argparse, hashlib, importlib.util, json, os, shlex, subprocess, sys, tempfile
from pathlib import Path
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import stopped_product_network as parent
from stopped_product.complex import build as parent_build
from structured_bulk_assembly import assembly, js

def read(p): return json.loads(p.read_text())
def pins():
    assert not sys.flags.optimize, 'Assertions must remain enabled'
    for name,digest in read(HERE/'SOURCE.json')['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name

def exact(row):
    original=parent.certificate()
    assert original['kappa']==Q(194869,2500000000)
    bit=parent.profile(read(ROOT/'certificates/stopped-product-bit-axis.json'))
    phase=parent.profile(row)
    bridge=parent.finite_bridge(bit,phase,row,read(ROOT/'certificates/copied-centers-network.json'))
    b=Q(7799647191,10**14)
    cm=parent.moment(phase['m'],phase['W'],phase['child_multiplicities'],b,True)
    a=min(parent.AB,(1-parent.PHASE_STOP)*b-Q(1,10**10))
    k=Q(7798412662809,10**17)
    assembled=assembly(a,b,bridge,k,beta=parent.PHASE_STOP)
    assert len(assembled['strict_constraints'])==47 and len(assembled['margins'])==7
    assert k>original['kappa'] and a<=parent.AB
    # Reject the next grid point for each selected strict endpoint.
    try: parent.moment(phase['m'],phase['W'],phase['child_multiplicities'],b+Q(1,10**14),True)
    except ValueError as e: assert str(e)=='Characteristic moment does not contract'
    else: raise AssertionError('Complex next grid was accepted')
    try: assembly(a,b,bridge,k+Q(1,10**17),beta=parent.PHASE_STOP)
    except AssertionError: pass
    else: raise AssertionError('Kappa next grid was accepted')
    expected=read(HERE/'certificate.json')
    for key,value in dict(kappa=k,complex_saving=b,bit_parameter=a,actual_bit_saving=parent.AB,
                          profile=phase,bridge=bridge,assembly=assembled).items():
        assert js(value)==expected[key],key
    return dict(kappa=str(k),complex_moment_gap=str(cm['strict_gap']),
                constraints=47,margins=7,next_grid_controls=2)

def regenerate(work):
    program=work/'matcher'
    subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',
        str(ROOT/'scripts/endpoint_gauge/match_complex_general.cpp'),'-o',str(program)],check=True)
    spec=importlib.util.spec_from_file_location('selected_rational_producer',HERE/'producer.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    results={}
    for name,builder,expected in (
        ('parent',parent_build,read(ROOT/'certificates/stopped-product-complex-input.json')),
        ('selected',module.build,read(HERE/'producer.json'))):
        prefix=work/name
        construction=builder(24,prefix,24)
        row=json.loads(subprocess.check_output([str(program),str(prefix)+'.bin',str(prefix)+'.labels'],text=True))
        for key in ('h','v','c','q','R','loss','histogram'):
            assert row[key]==expected[key],(name,key)
        assert construction['R']==row['baseline_R']
        assert row['R']==row['c']+row['q']-row['matched']
        results[name]=row
    # Pin the sole mathematical source edit relative to PR104's generator.
    selected=(HERE/'producer.py').read_text().splitlines(keepends=True)[3:]
    old=(ROOT/'scripts/stopped_product/complex.py').read_text()
    assert ''.join(selected)==old.replace('others.sort(key=lambda i:((i^1) in (a,b),i))',
                                          'others.sort(key=lambda i:((i^1) in (a,b),-i))')
    return results

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--arithmetic-only',action='store_true');args=parser.parse_args()
    pins();receipt=exact(read(HERE/'producer.json'))
    if not args.arithmetic_only:
        work=ROOT/'build/reversed-rational-centers';work.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='replay-',dir=work) as tmp:
            rows=regenerate(Path(tmp))
        receipt['parent_and_selected_producers_regenerated']=True
    print(json.dumps(receipt,indent=2));print('PASS conditional reversed rational-center refinement')
if __name__=='__main__': main()
