#!/usr/bin/env python3
"""Exact tensor-DAG complex side certificate, preserving the retained bound."""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from math import comb
import json

from certify import require, verify_sources
from prepare_layers import serializable
from experiments.disjoint_tensor import DisjointTensor, complex_counts, scalar_program, plan
from complex_compression import saving_bounds, matching, LeaveOneCircuit
from general_network_guard import guard

ROOT=Path(__file__).resolve().parents[1]


def certificate():
    controls=[]
    for h in (8,10):
        c=DisjointTensor(h)
        controls.append(dict(circuit=c.verify(),phase_frames=c.verify_frames(exact_bases=True)))
    c=DisjointTensor(26);v=len(c.inputs);expanded=c.verify();frames=c.verify_frames()
    n=complex_counts(26,expanded['roles']);code=scalar_program(c)
    lo,hi=saving_bounds(n);require(lo>Q(3,10**8),'Claimed complex saving unsupported')
    M=sum(len(ins)+len(outs)-2 for ins,outs in code['gates'])
    C=len(code['sources']);J=len(code['outputs'])
    require(M==2*c.additions+comb(26,2)*2*LeaveOneCircuit(24).additions,'Wrong mixer count')
    steps=3*v*v*(4*M+2*C+4*J+18*v)
    E=64*(n['W']+n['m']+1)**3
    slack=E-(4*steps+8*n['s']+8*n['W']+8*n['m'])
    require(slack>0,'Guard node charge insufficient')
    retained_guard=guard(n['m'],n['s'],E,Q(1,100),Q(1,1000),Q(5))
    labels,pi=matching(26)
    require(all(any(i not in S and i not in labels[j] for i in range(26))
                for S,j in zip(labels,pi)),'Missing shared-join residual unit')
    scan=[]
    for h in range(22,37,2):
        d=DisjointTensor(h);counts=complex_counts(h,d.additions+len(d.outputs))
        scan.append(dict(h=h,additions=d.additions,counts=counts,
                         saving_bounds=saving_bounds(counts),
                         full_coefficient_and_physical_frame_recheck=h==26))
    sources=('scripts/audit_disjoint_tensor.py','scripts/experiments/disjoint_tensor.py',
             'scripts/exclusion_circuit.py','scripts/binary_phase_frames.py',
             'scripts/complex_compression.py','notes/disjoint-tensor-compression.tex',
             'docs/research/disjoint-tensor-compression.md')
    return dict(status='IMPROVED FINITE COMPLEX NETWORK; NO NEW MULTIPLICATION KAPPA',
                upstream_commit=verify_sources(),retained_kappa=Q(1,2**31),
                exact_small_controls=controls,expanded_disjoint_circuit=expanded,
                phase_frames=frames,counts=n,saving_bounds=(lo,hi),certified_complex_saving=Q(3,10**8),
                intersection_two_control=LeaveOneCircuit(24).verify(),
                scalar_node_charge=dict(mixer_additions=M,copies=C,injections=J,
                    steps=steps,E=E,slack=slack,guard=retained_guard),
                matching=dict(labels=len(labels),bijective=True,orthogonal=True,
                    residual_unit_exists=True,sha256=sha256(json.dumps(pi).encode()).hexdigest()),
                finite_construction_scan=scan,
                scope='Finite construction and written phase transfer; conditional on retained upstream interfaces. The multiplication bit network remains unchanged.',
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in sources})


if __name__=='__main__':
    result=certificate()
    (ROOT/'certificates/disjoint-tensor-compression.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS: complex saving > 3e-8; full h=26 map and phase ledger; retained kappa 2^-31.')
