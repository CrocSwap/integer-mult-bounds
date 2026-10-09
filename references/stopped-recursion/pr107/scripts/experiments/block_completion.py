#!/usr/bin/env python3
"""Bounded floating-point exploration; NEVER a feasibility certificate.

Run with: uv run --with numpy==2.5.3 python scripts/experiments/block_completion.py
Writes only to build/. Exact rational verification would be required to promote
any converged output. Both definite and split diagonal blocks are explored.
"""
from itertools import combinations
from pathlib import Path
import json
import numpy as np


def run(h, rank, signature, seed, steps=200, noise_scale=0.1):
    ts=list(combinations(range(h),3));v=len(ts);k=2;n=k*v
    incidence=np.zeros((v,h))
    for i,t in enumerate(ts):incidence[i,list(t)]=1
    intersections=incidence@incidence.T
    fixed=np.kron(intersections==1,np.ones((k,k),dtype=bool))
    desired=np.zeros((n,n));diag=np.diag([1.,float(signature)])
    for i in range(v):
        fixed[2*i:2*i+2,2*i:2*i+2]=True
        desired[2*i:2*i+2,2*i:2*i+2]=diag
    rng=np.random.default_rng(seed)
    noise=rng.normal(size=(n,n));noise=(noise+noise.T)/2
    X=np.kron((intersections-1)/2,diag)+noise_scale*noise
    best=float('inf');best_X=None
    for _ in range(steps):
        X[fixed]=desired[fixed]
        vals,vecs=np.linalg.eigh(X)
        keep=np.argsort(np.abs(vals))[-rank:]
        X=(vecs[:,keep]*vals[keep])@vecs[:,keep].T
        error=float(np.max(np.abs((X-desired)[fixed])))
        if error<best:best=error;best_X=X.copy()
        if error<1e-10:break
    if best<1e-10 and noise_scale:
        Path('build').mkdir(exist_ok=True)
        np.save(f'build/block-candidate-{h}-{rank}-{signature}-{seed}.npy',best_X)
    return dict(h=h,rank=rank,diagonal_signature=signature,seed=seed,
                iterations=_+1,best_max_constraint_error=best,
                status='NUMERICAL CANDIDATE ONLY' if best<1e-10 else 'NO CONVERGENCE; NOT A NONEXISTENCE CLAIM')


if __name__=='__main__':
    controls=[run(8,16,signature,0,steps=1,noise_scale=0) for signature in (1,-1)]
    assert all(c['best_max_constraint_error']<1e-10 for c in controls)
    results=[]
    for h,rank in ((8,14),(10,16),(12,20)):
        for signature in (1,-1):
            for seed in (109,110):
                row=run(h,rank,signature,seed)
                results.append(row)
                print(json.dumps(row),flush=True)
    Path('build/block-completion.json').write_text(json.dumps({
        'scope':'Bounded floating-point search; failure is not a rank lower bound',
        'numpy_version':np.__version__,'known_feasible_controls':controls,
        'cases':results},indent=2)+'\n')
