"""Cyclic interval strips on both axes of PR104's stopped product-ring construction.

Bit axis (h23 retained-total producer) and complex axis (h24 all-disjoint rational
centers, with PR108 dual-suffix pair stars) both replace prefix/suffix leave-one-out
sums by cyclic interval strips. Everything else - matchers, positive labels, exact
support/frame/rational-scatter assertions, profiles, bridge and assembly - is PR104/PR107.
Copyright 2026 Rohan Arun, Apache-2.0. Prepared with Anthropic Claude assistance.
"""
import argparse, hashlib, importlib.util, json, os, shlex, subprocess, sys, tempfile
from pathlib import Path
from fractions import Fraction as Q
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import stopped_product_network as parent
from structured_bulk_assembly import assembly, js

COARSE=Q(898920417,10**13)          # certified stopped coarse saving of the new bit row
B=Q(8579641984,10**14)              # strict complex saving of the new complex row
KAPPA=Q(8578151200855,10**17)
PRIOR={'PR107':Q(7798412662809,10**17),'PR108':Q(7988289348441,10**17),'PR109':Q(39980858679,500000000000000)}

def read(p): return json.loads(Path(p).read_text())
def pins():
    assert not sys.flags.optimize,'Assertions must remain enabled'
    for name,digest in read(HERE/'SOURCE.json')['files'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
def rejects(f):
    try: f()
    except Exception: return True
    return False

def exact(bit_row,row,write=False,compare=True):
    old=(parent.COARSE,parent.AB)
    try:
        parent.COARSE=COARSE;parent.AB=(1-parent.ATOM)*COARSE+parent.ATOM*parent.OLD
        bit=parent.profile(bit_row);coarse=parent.coarse_moment(bit)
        parent.COARSE=COARSE+Q(1,10**13);parent.AB=(1-parent.ATOM)*parent.COARSE+parent.ATOM*parent.OLD
        assert rejects(lambda:parent.coarse_moment(bit)),'Next coarse grid accepted'
        parent.COARSE=COARSE;parent.AB=(1-parent.ATOM)*COARSE+parent.ATOM*parent.OLD
        phase=parent.profile(row)
        cm=parent.moment(phase['m'],phase['W'],phase['child_multiplicities'],B,True)
        assert rejects(lambda:parent.moment(phase['m'],phase['W'],phase['child_multiplicities'],B+Q(1,10**14),True)),'Next complex grid accepted'
        bridge=parent.finite_bridge(bit,phase,row,read(ROOT/'certificates/copied-centers-network.json'))
        a=min(parent.AB,(1-parent.PHASE_STOP)*B-Q(1,10**10))
        assembled=assembly(a,B,bridge,KAPPA,beta=parent.PHASE_STOP)
        assert len(assembled['strict_constraints'])==47 and len(assembled['margins'])==7
        assert rejects(lambda:assembly(a,B,bridge,KAPPA+Q(1,10**17),beta=parent.PHASE_STOP)),'Next kappa grid accepted'
        for name,k in PRIOR.items(): assert KAPPA>k,name
        computed=dict(kappa=KAPPA,coarse_bit_saving=COARSE,effective_bit_saving=parent.AB,complex_saving=B,bit_parameter=a,
                      bit_profile=bit,coarse_moment=coarse,complex_profile=phase,bridge=bridge,assembly=assembled)
        if write:(HERE/'certificate.json').write_text(json.dumps(js(computed),indent=2)+'\n')
        if compare:
            expected=read(HERE/'certificate.json')
            for key,value in computed.items(): assert js(value)==expected[key],key
        return dict(kappa=str(KAPPA),complex_saving=str(B),coarse_bit_saving=str(COARSE),constraints=47,margins=7,next_grid_controls=3,
                    gains={k:float((KAPPA/v-1)*100) for k,v in PRIOR.items()})
    finally: parent.COARSE,parent.AB=old

def regenerate(work):
    spec=importlib.util.spec_from_file_location('csb_bit',HERE/'producer_bit.py');bitmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(bitmod)
    bit=bitmod.build_row(work/'bit')
    stored=read(HERE/'bit-row.json')
    for k in ('h','v','c','q','baseline_R','matching','R','loss','histogram','label_source'): assert bit[k]==stored[k],('bit',k)
    program=work/'matcher'
    subprocess.run([*shlex.split(os.environ.get('CXX','c++')),'-O3','-std=c++17',str(ROOT/'scripts/endpoint_gauge/match_complex_general.cpp'),'-o',str(program)],check=True)
    spec=importlib.util.spec_from_file_location('csb_complex',HERE/'producer.py');cx=importlib.util.module_from_spec(spec);spec.loader.exec_module(cx)
    con=cx.build(24,work/'complex',24)
    row=json.loads(subprocess.check_output([str(program),str(work/'complex')+'.bin',str(work/'complex')+'.labels'],text=True))
    stored=read(HERE/'producer.json')
    for k in ('h','v','c','q','R','matched','loss','histogram'): assert row[k]==stored[k],('complex',k)
    assert con['R']==row['baseline_R'] and row['R']==row['c']+row['q']-row['matched']
    return bit,row

def main():
    p=argparse.ArgumentParser();p.add_argument('--arithmetic-only',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args()
    if not a.write:pins()
    if a.write or not a.arithmetic_only:
        with tempfile.TemporaryDirectory(prefix='cyclic-strips-') as tmp:
            bit,row=regenerate(Path(tmp))
    receipt=exact(read(HERE/'bit-row.json'),read(HERE/'producer.json'),write=a.write)
    receipt['bit_and_complex_producers_regenerated']=not a.arithmetic_only or a.write
    print(json.dumps(receipt,indent=2));print('PASS conditional cyclic strips on both axes')
if __name__=='__main__':main()
