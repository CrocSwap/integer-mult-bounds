#!/usr/bin/env python3
"""Maintainer cross-check of PR62's stacked finite profile and PR61's refinement.

Reconstructs the complete child list from the two replayed axis profiles.
Uses the maintainer's independent rational log/exp enclosures. Finite physical
realization and the inherited all-size theorem remain separate obligations.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from audit_community_candidate import moment, log_bounds, require

ROOT = Path(__file__).resolve().parents[1]


def run():
    native = json.loads((ROOT/'research/pair-assembly/frame/frame-certificate.json').read_text())
    package = ROOT/'research/matrix-exponent-synthesis'
    refined = json.loads((package/'candidate/arithmetic.json').read_text())
    pinned = package/'candidate/pinned62-certificate.json'
    require(sha256(pinned.read_bytes()).hexdigest() == refined['source_certificate_sha256'], 'PR62 pin')
    require(refined['source_profile'] == native['bit'] == json.loads(pinned.read_text())['bit'], 'unchanged finite profile')
    N, m = 4073300, 575
    W, loss = 2*N, 0
    rows = Counter({1: 19*N, 21: 2*N, 17: 2*N, 481: 2*N})
    for h in (23, 25):
        f = json.loads((ROOT/f'research/pair-assembly/frame/frame-profiles-{h}.json').read_text())
        rep = N//f['v']
        require(f['v']*rep == N and f['loss'] == h*(h-1), 'axis dimensions')
        require(f['blocks'][h] == 0 and sum(t*n for t,n in enumerate(f['blocks'])) == h*f['R']+f['loss'], 'paid copied centers')
        bank = rep*f['R']; W += bank; loss += rep*f['loss']
        rows.update({t: n*rep for t,n in enumerate(f['blocks']) if t and n})
        rows.update({h: bank, m-2*h: bank, 1: 2*N, h-2: 2*N})
    require((W, loss, m*W-sum(t*n for t,n in rows.items())) == (137151806,2226400,1846900), 'complete rank ledger')
    require(dict(rows) == {int(t):n for t,n in native['bit']['child_multiplicities'].items()}, 'complete child list')
    results = {}
    for name, certificate in [('pr62',native),('pr61_on_pr62',refined)]:
        a, kappa = Q(certificate['bit_saving']), Q(certificate['kappa'])
        lo, hi = moment(m,W,rows.items(),a)
        require(hi < 1, name+' independent moment')
        p = {k: Q(v) for k,v in certificate['assembly']['parameters'].items()}
        h,beta,b = p['h'],p['beta'],p['a_complex']
        q = a*(1-2*h); eps = (1-h)/(1+q); c = q+h/4
        G = eps*q; r = (G+1-eps)/2; delta = h/8
        require(0 < q < a < (1-beta)*b < b < 1, 'stopping order')
        require(c > q and 1-eps*(1+c)>0 and eps+r<1 and eps>(1-r)/2 and eps>a, 'geometric and analytic conditions')
        require((p['epsilon'],p['c'],p['q'],p['alpha_squared_power'],p['delta']) == (eps,c,q,r,delta), 'parameter binding')
        margins = [1-eps,a,G,a,min(1-eps-delta,r-delta),1-eps-delta,eps]
        require(margins == [Q(certificate['assembly']['margins']['g'+str(i)]) for i in range(1,8)], 'seven margins')
        require(min(margins) == G > kappa > Q(1,2**15) and kappa < Q(1,2**14), 'headline')
        require(len(certificate['assembly']['constraints']) == 47 and all(Q(x)>0 for x in certificate['assembly']['constraints'].values()), 'strict slacks')
        results[name] = dict(kappa=str(kappa),moment_gap_lower=str(1-hi),absorption_gap=str(G-kappa))
    # Recompute all 47 rows and eventual bounds using the previously reviewed
    # balanced interface, pinned independently by PR61's certificate.
    path = ROOT/refined['assembly_code_path']
    require(sha256(path.read_bytes()).hexdigest() == refined['assembly_code_sha256'], 'assembly source pin')
    spec = importlib.util.spec_from_file_location('reviewed_balanced_assembly',path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    assembled = module.assembly(refined['finite_bridge'],Q(refined['bit_saving']),Q(refined['kappa']),h=Q(refined['h_backoff']),a_complex=Q(717,10**7))
    def js(x):
        if isinstance(x,Q): return str(x)
        if isinstance(x,dict): return {str(k):js(v) for k,v in x.items()}
        if isinstance(x,(tuple,list)): return [js(v) for v in x]
        return x
    require(js(assembled) == refined['assembly'], '47 derived constraints')
    require(js(module.cutoffs(refined['finite_bridge'],assembled)) == refined['eventual_bounds'], 'eventual bounds')
    # Bind the kernel's explicit rational rows to the physical certificate.
    exported = json.loads((package/'candidate/weighted-lean-input.json').read_text())
    require({r['width']:r['multiplicity'] for r in exported['rows']} == dict(rows), 'Lean profile binding')
    require(exported['named_slacks'] == refined['assembly']['constraints'], 'Lean slack binding')
    require(exported['kappa'] == refined['kappa'] and exported['bit_saving'] == refined['bit_saving'], 'Lean saving binding')
    for row in exported['rows']:
        require(Q(row['log_upper']) >= log_bounds(Q(m,row['width']))[1], 'independent logarithm bound')
    with tempfile.TemporaryDirectory(prefix='frontier-lean-binding-') as directory:
        generated = Path(directory)/'RefinedFrontierCertificate.lean'
        subprocess.run([sys.executable,str(package/'candidate/generate_frontier_case.py'),str(package/'candidate/weighted-lean-input.json'),'--output',str(generated),'--label','PR62 inherited construction; parameter arithmetic refinement','--source-pin',refined['source_commit']],check=True,capture_output=True,text=True)
        require(generated.read_text() == (package/'RefinedFrontierCertificate.lean').read_text(), 'kernel source generation')
    return dict(status='PASS',counts=dict(m=m,W=W,N=N,L=loss,deficit=1846900,maxchild=max(rows)),candidates=results,lean_profile_bound=True,scope='Independent moments and direct assembly identities; exact retained 47-row interface and source-bound finite Lean arithmetic. General transfer and physical realization are reviewed separately.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--check',type=Path)
    args = parser.parse_args(); result = run()
    if args.check: require(result == json.loads(args.check.read_text()), 'receipt mismatch')
    if args.output: args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS independent PR62/61 moments, complete child ledger, assembly and Lean source binding')
