#!/usr/bin/env python3
"""Exact two-stage finite profile, common-basis witness and PR23 assembly.
Zhihao Chen (jacklightChen), OpenAI Codex assistance. Apache-2.0.
"""
import sys,json,importlib.util
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(ROOT/'scripts')]
from two_stage_unequal import profile,prescriptions
from check_unequal_corners import control
from partial_swap_network import moment
from assembly import assembly
from prepare_layers import serializable
AB=Q(15537,10**9);KAPPA=Q(15536,10**9)

def halving(m,r):
    k=1
    while m**k<=2*r**k:k+=1
    return k

def run():
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    for name,digest in manifest['source_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    # PR23's complex circuit and all analytic dependencies remain source-pinned.
    spec=importlib.util.spec_from_file_location('semantic_predecessor',ROOT/'research/semantic-bulk/verify.py')
    predecessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(predecessor)
    predecessor.pinned_inputs()
    old=json.loads((ROOT/'research/semantic-bulk/certificate.json').read_text())
    for name,digest in old['input_sha256'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    axes=[]
    for h in [55,53]:
        record=json.loads((HERE/f'producer-{h}.json').read_text());a=record['matched']
        assert record['scalar']['all_additions_disjoint'] and record['scalar']['all_partial_outputs_exact']
        assert record['scalar']['every_node_has_common_point']
        assert a['q']==3*a['v']+h and a['R']==a['c']+a['q']-a['matched']
        assert a['loss']==h*(h-1) and sum(r*n for r,n in enumerate(a['histogram']))==h*a['R']+2*a['loss']
        labels=json.loads((HERE/f'labels-{h}.json').read_text())
        assert labels['exact_envelopes']==a['c'] and labels['exact_dependency_inclusions']==2*a['c']
        assert labels['output_frames']==a['q']
        axes.append(a)
    p=profile(*axes);assert p['deficit']==330823350
    exact=moment(p['m'],p['W'],p['rows'],AB,True)
    assert exact['strict_gap']>Q(27,10**11)
    basis=control(53,1);prescriptions(55,53)
    f=old['finite_bridge']
    # Fractions in the inherited bridge were serialized as strings.
    f['semantic']['strict_literal_gap']=Q(f['semantic']['strict_literal_gap'])
    f['semantic']['C0']=int(f['semantic']['C0'])
    mb,Wb,Mb=p['m'],p['W'],max(p['rows']);db=halving(mb,Mb);wb=Wb.bit_length()
    f['bit']=dict(m=mb,W=Wb,maxchild=Mb,halving_degree=db,wire_bits=wb)
    coefficient=db*wb+f['complex']['halving_degree']*f['complex']['wire_bits']
    degree=1000*((coefficient*51+24999)//25000)
    f['rows']=dict(coefficient=coefficient,degree=degree,suffix_slope=4*degree,
                   degree_gap=degree-Q(coefficient*51,25),contract='PR23 product Wc^Dc Wb^Db; parked correction uses existing role stream, no new row index')
    assembled=assembly(f)
    assert assembled['absorption_gap']>Q(5,10**10)
    rejected=[]
    for name,kwargs in [('old_guard',dict(old_guard=True)),('old_exposures',dict(old_exposures=True)),
                       ('unsupported_2_minus15',dict(kappa=Q(1,2**15)))]:
        try:assembly(f,**kwargs)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(name)
    # Same framework with singleton local calls cannot certify the headline.
    no_local=profile(*axes,local=False)
    try:moment(no_local['m'],no_local['W'],no_local['rows'],AB,True)
    except ValueError:rejected.append('unbatched_local_profile')
    else:raise AssertionError('Unbatched local profile unexpectedly certified')
    return dict(status='CONDITIONAL kappa=15536/10^9 >2^-16; written finite/basis/analytic/tape dependencies; not formal verification',
                bit=dict(**p,**exact),basis=basis,finite_bridge=f,assembly=assembled,negative_controls=rejected,
                producer_replay='producer.py regenerates each changed finite graph once; labels checked exactly in both orientations by duality',
                references=dict(PR23='661ebabc1076c9f525d7ce4967c876b203fa9827',PR24='ed90fd940279c336ebc45968631bdebfb087b505'))

if __name__=='__main__':
    r=run();(HERE/'certificate.json').write_text(json.dumps(serializable(r),indent=2,sort_keys=True)+'\n')
    print('PASS final kappa=15536/10^9 >2^-16;',len(r['assembly']['constraints']),'constraints;7 margins')
    print('bit moment gap',float(r['bit']['strict_gap']),'final gap',float(r['assembly']['absorption_gap']))
    print('product stock',r['finite_bridge']['rows']['degree'])
