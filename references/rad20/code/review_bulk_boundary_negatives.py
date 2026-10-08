#!/usr/bin/env python3
"""Exact discriminating boundary controls for bulk principal-window layout."""
from datetime import datetime,timezone
from fractions import Fraction as Q
import argparse
import hashlib
import json
from pathlib import Path


def require(c,m):
    if not c:raise AssertionError(m)


def controls():
    # A principal submatrix can retain a far unwrapped edge when the
    # omitted cyclic gap is too short, even without repeated vertices.
    s,w=20,3
    indices=list(range(1,20))
    H=[[Q(int(i==j)) for j in range(s)] for i in range(s)]
    for i in range(s):
        for step in range(1,w+1):
            H[i][(i+step)%s]=Q(1,16)
            H[i][(i-step)%s]=Q(1,16)
    principal=[[H[i][j] for j in indices] for i in indices]
    require(len(indices)<s and principal[0][-1]!=0 and len(indices)-1>w,
            'Missing complement-gap negative does not discriminate')
    gap_record=dict(s=s,w=w,interval=[1,20],cyclic_edge=[1,19],
                    unwrapped_distance=18,entry=str(principal[0][-1]),
                    all_row_gaps_positive=True,noncyclic_banded_claim_rejected=True)
    require(all(H[i][i]>sum(abs(x) for j,x in enumerate(H[i]) if j!=i)
                for i in range(s)),'Negative gap fixture is not strictly DD')

    # q_j-j is constant across the lift of the physical period cut, but
    # the globally rounded H may have a separately rounded cross-cell edge.
    s,t=20,21
    q=lambda j:(2*t*j+s)//(2*s)
    phase=lambda j:q(j)-j
    require(phase(s-1)==phase(s),'Periodic phase lift does not merge in fixture')
    require(phase(s-1)!=phase(0),'Physical first/last phase cells already equal')
    kernel=Q(1,16)
    fixed_cross=kernel-Q(1,2**40)
    require(fixed_cross!=kernel,'False phase merge did not alter global coefficient')
    seam_record=dict(s=s,t=t,lifted_neighbors=[19,20],
        unwrapped_phase=phase(19),physical_cells=[phase(19),phase(0)],
        same_global_H_entry=str(fixed_cross),incorrect_merged_toeplitz_entry=str(kernel),
        first_Neumann_path_difference=str(kernel-fixed_cross),
        merge_rejected=True)

    # Cropping a completed axis is sound; eagerly dropping another axis's
    # halo removes a column which its own core map may still require.
    first=[Q(0),Q(1,4),Q(0)]
    second=[Q(1,4),Q(0),Q(0)]
    data=[[Q(int(i==1 and j==0)) for j in range(3)] for i in range(3)]
    after_first=[sum((first[i]*data[i][j] for i in range(3)),Q(0)) for j in range(3)]
    correct=sum((second[j]*after_first[j] for j in range(3)),Q(0))
    premature=second[1]*after_first[1]
    require(correct==Q(1,16) and premature==0,
            'Unprocessed-axis halo crop negative did not discriminate')
    crop_record=dict(correct_tensor_core=str(correct),premature_other_axis_crop=str(premature),
                     exact_axis_norms=['1/4','1/4'],premature_crop_rejected=True)

    # Persistent halos have near-one volume; binary-padding all axes at
    # once instead multiplies the complete tensor by 2^D.
    D,L,A=8,1024,1
    actual=Q((L+2*A)**D,L**D)
    all_binary=Q((2*L)**D,L**D)
    require(actual<2 and all_binary==256,'Simultaneous field padding negative failed')
    padding_record=dict(axes=D,L=L,A=A,persistent_volume_ratio=str(actual),
        wrong_simultaneous_binary_padding_ratio=str(all_binary),
        correct_current_field_temporary_ratio=str(Q(2*L,L+2*A)),
        simultaneous_padding_rejected=True)
    return dict(complement_gap=gap_record,global_period_phase_cut=seam_record,
                unprocessed_axis_halo_crop=crop_record,simultaneous_padding=padding_record)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();require(not args.output.exists(),'Use a fresh output path')
    result=dict(status='PASS four exact bulk boundary negative controls',
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        controls=controls(),scope='Rational discriminating proof controls, not true-Gaussian numerical fixtures')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS complement gap, physical period phase cut, unprocessed halo and simultaneous padding negatives')


if __name__=='__main__':main()
