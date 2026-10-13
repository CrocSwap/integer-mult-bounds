#!/usr/bin/env python3
"""Opt-in exact orbit reduction for the historical sparse-fusion screen.

Apache-2.0. Prepared for ToikY with substantial OpenAI Codex assistance.
The adapted screen retains Douglas Colkitt's original checks and receipt.
"""
import argparse
from hashlib import sha1, sha256
import importlib.util
import json
from math import comb
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def load_original(root=ROOT):
    """Admit pinned scientific inputs before importing the original checker."""
    root = Path(root)
    pins = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for relative, digest in pins['files'].items():
        data = (root / relative).read_bytes()
        blob = b'blob '+str(len(data)).encode()+b'\0'+data
        if (sha256(data).hexdigest() != digest or
                sha1(blob).hexdigest() != pins['git_blob_ids'][relative]):
            raise ValueError('Source pin mismatch: ' + relative)
    sys.path.insert(0, str(root / 'scripts'))
    spec = importlib.util.spec_from_file_location(
        'sparse_fusion_original', root / 'scripts/audit_sparse_fusion.py')
    original = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    return original


def orbit_representatives(h):
    """All triple orbits under permutations fixing the first three axes."""
    if h < 22:
        raise ValueError('Use the admissible complex family')
    return tuple((low | (((1 << (3-low.bit_count()))-1) << 3),
                  comb(h-3, 3-low.bit_count())) for low in range(8))


def accelerated_screen(original, h=25):
    """Adapt only the original triple enumeration and its weighted rank sum."""
    Q, require, binary_rank = original.Q, original.require, original.binary_rank
    require(h>=22,'Use the admissible complex family')
    triples=orbit_representatives(h)
    v=comb(h,3);centers=h+1
    baseline=v*(h-1)+2*centers*h
    minimum_changed=None
    frames=[]
    for bits in range(64):
        Qcols=[1<<i for i in range(h)]
        Qcols[:3]=[0,0,0]
        at=0
        for i in range(3):
            for j in range(i,3):
                if bits>>at&1:
                    Qcols[j]^=1<<i
                    if i!=j:Qcols[i]^=1<<j
                at+=1
        k=binary_rank(Qcols)
        r=binary_rank([col^(1<<i) for i,col in enumerate(Qcols)])
        unary=sum(weight*(binary_rank([col^(t if t>>i&1 else 0)
                                       for i,col in enumerate(Qcols)])+r)
                  for t,weight in triples)
        frames.append((Qcols,k,r,unary))
        if r==0:continue
        actual=unary+2*centers*k
        proved_increase=v*(k+r-h)+2*(Q(v,h)-centers)*(h-k)
        require(actual-baseline>=proved_increase>0,'Central-frame lower bound failed')
        minimum_changed=actual if minimum_changed is None else min(actual,minimum_changed)
    joint_baseline=2*v*(h-1)+3*centers*h
    joint_min_changed=None
    for A,kA,rA,unaryA in frames:
        for IC,kIC,rIC,unaryIC in frames:
            AC=[x^y^(1<<i) for i,(x,y) in enumerate(zip(A,IC))]
            actual=unaryA+unaryIC+centers*(kA+binary_rank(AC)+kIC)
            x,y=h-kA,h-kIC
            u,w=kA+rA-h,kIC+rIC-h
            lower=(v-centers)*(u+w)+2*(Q(v,h)-centers)*(x+y)
            require(actual-joint_baseline>=lower>=0,'Joint central-frame bound failed')
            if rA or rIC:
                require(lower>0,'Nonoriginal middle frames escaped strict bound')
                joint_min_changed=actual if joint_min_changed is None else min(joint_min_changed,actual)
            else:require(actual==joint_baseline,'Original central frame score changed')
    return dict(h=h,triples=v,center_roles=centers,baseline_incident_rank=baseline,
                sampled_changed_frames=63,minimum_sampled_changed_rank=minimum_changed,
                rank_density=Q(v,h),density_minus_center_count=Q(v,h)-centers,
                joint_frame_pairs=4096,joint_baseline=joint_baseline,
                joint_minimum_changed_rank=joint_min_changed,
                theorem='The original four central frames jointly minimize the directional rank lower bound when side frames and the active h-factor are fixed.',
                scope='All four central frames may vary, but side frames, topology and the tensor factor are retained. Does not exclude changing those ingredients or the tape primitive.')


def receipt(original, mode, kind='certificate', h=25):
    if mode not in ('reference', 'accelerated') or kind not in ('screen', 'certificate'):
        raise ValueError('Invalid replay mode or kind')
    if kind == 'screen':
        screen = original.central_gate_screen if mode == 'reference' else lambda h: accelerated_screen(original, h)
        return original.serializable(screen(h))
    if h != 25:
        raise ValueError('The complete historical certificate uses h=25')
    if mode == 'reference':
        return original.serializable(original.certificate())
    reference_screen = original.central_gate_screen
    try:
        original.central_gate_screen = lambda h=25: accelerated_screen(original, h)
        return original.serializable(original.certificate())
    finally:
        original.central_gate_screen = reference_screen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('reference', 'accelerated'), default='accelerated')
    parser.add_argument('--kind', choices=('screen', 'certificate'), default='certificate')
    parser.add_argument('--h', type=int, default=25)
    args = parser.parse_args()
    print(json.dumps(receipt(load_original(), args.mode, args.kind, args.h), sort_keys=True))


if __name__ == '__main__':
    main()
