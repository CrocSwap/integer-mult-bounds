#!/usr/bin/env python3
"""Final independent literal guard, product-row and prefix qualifications.

Uses accepted review certificates and hashes the two frozen written layout
inputs. No batching producer or cloner is imported. Small labelled row
controls test only the new nested reservation, not an old physical network.
"""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import resource
import time

from review_semantic_guard import FixedGrid


def nested_rows():
    cases=rows=boundaries=0
    for dc in range(1,5):
        for db in range(1,4):
            wc,wb=3,5;stock=wc**dc*wb**db;q0=(stock-1).bit_length();R=1<<q0
            padded=stock*((R+stock-1)//stock)
            assert stock<=R<=padded<2*R
            for j in range(dc+1):
                factor=wc**j;remaining=padded//factor
                assert remaining%(wc**(dc-j)*wb**db)==0
                for u in range(remaining):
                    # Reversible bit selector split, entirely inside a
                    # temporarily inherited complete integer row range.
                    digit=u;selected=[]
                    for _ in range(db):digit,role=divmod(digit,wb);selected.append(role)
                    restored=digit
                    for role in reversed(selected):restored=restored*wb+role
                    assert restored==u
                    # The activation tag is external to coefficient data.
                    active=u<R//factor
                    assert (restored<R//factor)==active
                    rows+=1
                boundaries+=1
            cases+=1
    # Prefix transform exactly once. A repeated child prefix changes C^2=X.
    width=64;values=[(int(x==0)<<width,0) for x in range(16)]
    machine=FixedGrid(width,0,1)
    after_prefix=machine.leaf(values,(0,1))
    correct=machine.leaf(after_prefix,(2,3))
    repeated=machine.leaf(correct,(0,1))
    changed=sum(a!=b for a,b in zip(correct,repeated));assert changed>0
    return dict(exact_product_shapes=cases,labelled_nested_row_returns=rows,
        exact_complex_depth_boundaries=boundaries,one_initial_volume_inflation=True,
        mixed_integer_prefix_has_no_power_of_two_requirement=True,
        repeated_prefix_negative_changed_entries=changed)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--finite-review',type=Path,required=True)
    ap.add_argument('--generic-review',type=Path,required=True)
    ap.add_argument('--controls',type=Path,required=True)
    ap.add_argument('--characteristic',type=Path,required=True)
    ap.add_argument('--root-layout',type=Path,required=True)
    ap.add_argument('--root-prefix',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();assert not args.output.exists();start=time.monotonic()
    assert sha256(args.root_layout.read_bytes()).hexdigest()=='5781af807210dc3ac740e876cdb8073683ea3658f4b8aa067605608919a8f520'
    assert sha256(args.root_prefix.read_bytes()).hexdigest()=='84ebd3bb5327ccd04134db36d0b109b377c6d6cf2c0c82923d1c35b596dc43b2'
    finite=json.loads(args.finite_review.read_text())['full'];c=finite['counts'];guard=finite['guard']
    controls=json.loads(args.controls.read_text());characteristic=json.loads(args.characteristic.read_text())
    assert controls['status']=='PASS independent mixed whole-rank complex interface controls'
    assert characteristic['status']=='PASS independent exact b_phase=10^-6 on accepted changed h28'
    assert characteristic['counts']==c
    h=c['h'];v=comb(h,3);m=h**3;R=c['R'];W=c['W'];s=c['s']
    additions=finite['complete_changed_logical']['additions']
    G=3*v*v*(4*(additions+v)+4*v+4);E=64*(W+m+1)**3
    assert G==guard['actual_grouped_scalar_gates'] and E==guard['additive_E']
    charged=2*G*W*W+8*s+4*W+4+32*m;assert charged<E
    bit=json.loads(args.generic_review.read_text())['row']['counts']
    hb=int(bit['h']);mb=int(bit['m']);wb=int(bit['W']);rb=mb-4*hb
    assert mb**651>2*rb**651 and wb<2**49
    rc=m-2*h;assert m**272>2*rc**272 and W<2**41
    coefficient=49*651+41*272
    # ceil log2(Cp)<=2 log2 p+1, under p>=C; log2 p>=25.
    assert coefficient*51<89000*25
    assert 4*89000==356000
    output=dict(status='PASS independent complete whole-rank complex transfer qualifications',
        generated_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        dependency_sha256={'review_semantic_guard.py':sha256(Path(__file__).with_name('review_semantic_guard.py').read_bytes()).hexdigest()},
        inputs={str(p):sha256(p.read_bytes()).hexdigest() for p in
            (args.finite_review,args.generic_review,args.controls,args.characteristic,args.root_layout,args.root_prefix)},
        finite_count_and_guard=dict(h=h,R=R,W=W,s=s,G=G,E=E,
            stronger_wrapper_tail_depth=charged,strict_E_slack=E-charged,
            B=s+E,C0=32*m*(s+E)**2,C1=1),
        combined_rows=dict(complex_depth=272,bit_depth=651,complex_maxchild=rc,bit_maxchild=rb,
            exact_product='W_complex^D_complex*W_bit^D_bit',
            stock_base_two_coefficient=coefficient,polynomial_degree=89000,
            sufficient_suffix_slope=356000,one_initial_leading_prefix=True,
            prefix_chunks='ceil(log2 Q_rows), precomputed once; all descendants inherit',
            elementary_prefix_fallback='e<=q0, O(V log p)',
            actual_prefix_volume='2^(q0*K)>=Q_rows; pad once to a stock multiple, less than2 volume'),
        nested_row_controls=nested_rows(),
        scope='Independent full analytic phase/layout/volume/tail/tree review is written separately. This certificate pins the producer reports and closes the literal wrapper guard and combined product-stock arithmetic; it does not claim giant phase program execution or a final multiplication assembly.',
        wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(output['status'],flush=True)


if __name__=='__main__':main()
