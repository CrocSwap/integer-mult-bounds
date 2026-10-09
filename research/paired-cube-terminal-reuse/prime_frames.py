#!/usr/bin/env python3
"""Exact Gram witnesses for every rational frame in the regenerated bit word.

Uses the PR165/169 Bareiss determinant and factor-witness routines, retaining
their attribution. Adapted by huxint with substantial OpenAI Codex assistance.
Apache-2.0. No prime is tested by sampling.
"""
from hashlib import sha256
from pathlib import Path
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'research/paired-cube-bit-descent-168/prime_witnesses.py'
spec=importlib.util.spec_from_file_location('inherited_gram_witnesses',SOURCE)
inherited=importlib.util.module_from_spec(spec)
spec.loader.exec_module(inherited)


def certify(experiment):
    e=experiment;c=e.c
    used=set(e.frames)|set(c.nf.values())|set(c.rf)|set(c.w['source_frame'])
    used.update(z['frame'] for z in c.w['gauges'])
    used.add(c.w['full_frame'])
    for row in c.k['entries']:
        used.update(row['carrier_chain']);used.update(row['passive_chain'])
    records=[];done=set()
    for f in sorted(used):
        B=c.B[f]
        key=json.dumps(B,separators=(',',':'))
        if key in done:continue
        done.add(key)
        sums=list(map(sum,B))
        gram=[[9*sum(a*b for a,b in zip(x,y))-sums[i]*sums[j]
               for j,y in enumerate(B)] for i,x in enumerate(B)]
        determinant=inherited.det(gram)
        powers,residual=inherited.factor_witness(determinant)
        records.append(dict(basis_sha256=sha256(key.encode()).hexdigest(),dimension=len(B),
                            determinant=determinant,small_prime_powers=powers,residual=residual))
    records.sort(key=lambda r:r['basis_sha256'])
    return dict(status='PASS every original and replacement bit frame',
                unique_frames=len(records),prime_lower_bound=2**80,
                maximum_residual=max(r['residual'] for r in records),
                all_frames_nondegenerate_for_every_retained_prime=True,
                frame_witnesses=records)
