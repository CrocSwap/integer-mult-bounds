#!/usr/bin/env python3
"""Exact translated partial-swap bit moment and conditional final assembly.

Zhihao Chen (jacklightChen), with OpenAI Codex assistance. Apache-2.0.
The preserved PR18 source, complex source-frame extension, and their written
finite-tape/analytic hypotheses are explicit dependencies, not inferred here.
"""
from collections import Counter
from dataclasses import asdict, replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import partial_swap_network as retained
from certify import Parameters
from compact_control_layer import layer_exponents
from fast_gaussian import fast_constraints,fast_margins
from prepare_layers import serializable

BIT_SAVING=Q(11,10**6)
COMPLEX_SAVING=Q(18,10**6)
KAPPA=Q(5499,10**9)
PR18='f2ab41aebad47861caf6316282c1793e5513845e'
MAIN='6e564879f51ae16f23d392e9e196c605f36d90df'


def bit_counts(data=None):
    data=json.loads(retained.INPUT.read_text()) if data is None else data
    n,original=retained.bit_counts(data)
    rows=Counter(original)
    B=n['B2']
    for width in (575,31625,23,529):
        rows[width]-=B
        assert rows[width]>=0
    for width in (23,32729):rows[width]+=B
    rows=Counter({w:c for w,c in rows.items() if c})
    assert 575+31625+23+529==23+32729==n['m']-23
    assert sum(w*c for w,c in rows.items())==n['s']
    assert n['W']*n['m']-n['s']==2*n['N']-2*n['L']>0
    assert rows[1]==original[1]
    return n,rows


def bit_certificate(saving=BIT_SAVING):
    n,rows=bit_counts()
    result=retained.moment(n['m'],n['W'],rows,saving,True)
    return dict(counts=n,**result,
        replaced_classes=dict(copies=n['B2'],old_widths=[575,31625,23,529],new_widths=[23,32729]),
        scope='Actual stage-two auxiliary endpoint relocation, preserving every other PR18 physical edge and basis profile.')


def parameters():
    tau=1-BIT_SAVING
    return Parameters(tau=tau,sigma=1-COMPLEX_SAVING,
        epsilon=1/(2+BIT_SAVING),c=Q(1),beta=Q(1,1000),delta=Q(1,10**16),
        lam=tau+Q(1,10**20),lamp=tau+Q(2,10**20),C1=Q(19991,10000),kappa=KAPPA)


def assembly(p=None):
    p=parameters() if p is None else p
    ex=layer_exponents(p.tau,p.sigma,p.beta,p.c)
    cs=fast_constraints(p)
    cs['packed_overhead']=p.lam-ex['internal']
    cs['reserved_axes']=p.lamp-ex['preprocessing']
    assert len(cs)==29 and all(v>0 for v in cs.values())
    gs=fast_margins(p)
    assert len(gs)==7 and min(gs.values())>p.kappa>Q(1,2**18)
    return dict(parameters=asdict(p),recurrence=ex,constraints=cs,margins=gs,
        minimum_margin=min(gs.values()),absorption_gap=min(gs.values())-p.kappa,
        gap_above_2_minus18=p.kappa-Q(1,2**18),
        ratio_to_PR18=p.kappa/Q(942293,500000000000))


def validate_retained_sources():
    record=json.loads((ROOT/'certificates/partial-swap-network.json').read_text())
    for name,digest in record['source_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==digest, name
    return dict(commit=PR18,sha256=record['source_sha256'],
        scope='PR18 text source snapshot imported unchanged; predecessor PDF is regenerated from those sources.')


def validate_producer(path):
    result=json.loads(path.read_text())
    assert result['regenerated_from_source']
    d=json.loads(retained.INPUT.read_text())
    for h in (25,23,57):
        actual=result['producers'][str(h)];expected=d['producers'][str(h)]
        assert actual['certificate_equal']
        for key,recorded in [('R','roles'),('c','additions'),('q','outputs'),('matched','matches'),('histogram','histogram'),('loss','loss')]:
            assert actual[key]==expected[recorded], (h,key)
    assert result['complex']['certificate_equal']
    return result


def certificate(producer=None):
    import complex_source
    b=bit_certificate();c=complex_source.run();a=assembly()
    assert c['a_c']==COMPLEX_SAVING and c['moment_upper']<1
    assert c['guard']['C1']==a['parameters']['C1']
    assert c['guard']['rho']==2
    retained_sources=validate_retained_sources()
    controls={}
    for name in ('bit-controls.json',):
        controls[name]=json.loads((HERE/name).read_text())
    if producer:controls['regenerated_producer']=validate_producer(producer)
    else:raise ValueError('A complete once-regenerated producer certificate is required')
    rejected=[]
    for name,check in [('unsupported_bit_saving',lambda:bit_certificate(Q(12,10**6))),
                        ('unsupported_2_minus17',lambda:assembly(replace(parameters(),kappa=Q(1,2**17))))]:
        try:check()
        except (AssertionError,ValueError):rejected.append(name)
        else:raise AssertionError('Negative control failed: '+name)
    paths=sorted(p for p in HERE.glob('*.py'))+sorted((ROOT/'notes').glob('translated-partial-*.tex'))
    return dict(status='CONDITIONAL FINAL MULTIPLICATION SAVING 5499/10^9 > 2^-18; NOT FORMAL VERIFICATION',
        baseline_main=MAIN,retained_pr18=retained_sources,source_frame_PR13='3ef246fa4f69c87ebfed78376418afa9ffcad145',
        nested_PR16='a80f5e676c84b59def9791495df0655efe89a04f',
        bit=b,complex=c,assembly=a,controls=controls,negative_controls=rejected,
        source_sha256={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in paths},
        scope='Written new endpoint, contiguous-corner, complex phase and physical path proofs; exact finite producer and arithmetic. The retained common-basis, scalar/tape and analytic interfaces remain conditional dependencies. No global novelty or linear-time claim.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--producer',type=Path,default=HERE/'producer-certificate.json')
    p.add_argument('--output',type=Path,default=HERE/'certificate.json')
    a=p.parse_args();result=certificate(a.producer)
    a.output.write_text(json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS final conditional kappa='+str(KAPPA)+' > 2^-18')
    print('bit='+str(BIT_SAVING)+'; complex='+str(COMPLEX_SAVING))
    print('29 strict constraints;7 strict margins; gap='+str(result['assembly']['absorption_gap']))
if __name__=='__main__':main()
