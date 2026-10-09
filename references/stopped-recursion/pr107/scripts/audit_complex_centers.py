#!/usr/bin/env python3
"""Exact dyadic central compression with the full complex side circuit."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

from certify import require, verify_sources
from prepare_layers import serializable
from experiments.complex_centers import factor, verify_factor, counts
from experiments.disjoint_tensor import DisjointTensor, scalar_program
from complex_compression import saving_bounds, matching, LeaveOneCircuit
from general_network_guard import guard

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    h=26;c=DisjointTensor(h);side=c.verify();frames=c.verify_frames()
    f=factor(h);checked=verify_factor(f);code=scalar_program(c)
    n=counts(h,side['roles']);lo,hi=saving_bounds(n)
    require(lo>Q(36,10**9),'Claimed complex saving unsupported')
    M=sum(len(ins)+len(outs)-2 for ins,outs in code['gates'])
    C=len(code['sources']);J=len(code['outputs'])
    G=checked['gather_steps'];H=checked['scatter_steps']
    steps=3*n['v']**2*(4*M+2*C+4*J+2*G+2*H)
    E=64*(n['W']+n['m']+1)**3
    slack=E-(4*steps+8*n['s']+8*n['W']+8*n['m'])
    require(slack>0,'Node charge insufficient')
    g=guard(n['m'],n['s'],E,Q(1,100),Q(1,1000),Q(5))
    labels,pi=matching(h)
    require(len(labels)==len(set(pi))==n['v'],'Nonbijective shared matching')
    require(all(any(i not in S and i not in labels[j] for i in range(h))
                for S,j in zip(labels,pi)),'Missing shared residual unit')
    sources=('scripts/audit_complex_centers.py','scripts/experiments/complex_centers.py',
             'scripts/experiments/disjoint_tensor.py','scripts/complex_compression.py',
             'scripts/exclusion_circuit.py','scripts/binary_phase_frames.py',
             'scripts/general_network_guard.py','notes/dyadic-central-factor.tex',
             'notes/disjoint-tensor-compression.tex','notes/complex-compression.tex',
             'docs/research/dyadic-central-factor.md')
    return dict(status='COMPLEX INTERFACE HEADROOM; RETAINED KAPPA 2^-31',
                upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),
                certified_complex_saving=Q(36,10**9),saving_bounds=(lo,hi),counts=n,
                central_factor=checked,side_circuit=side,side_phase_frames=frames,
                intersection_two=LeaveOneCircuit(h-2).verify(),
                central_frames=dict(gates_keep_all_incidences=True,
                    downward_dimensions_per_invocation=h*h,
                    proof='notes/dyadic-central-factor.tex'),
                shared_matching_sha256=sha256(json.dumps(pi).encode()).hexdigest(),
                scalar_charge=dict(M=M,C=C,J=J,G=G,H=H,steps=steps,E=E,slack=slack,guard=g),
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/dyadic-central-factor.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS: h central roles; complex saving > 3.6e-8; retained kappa 2^-31.')
