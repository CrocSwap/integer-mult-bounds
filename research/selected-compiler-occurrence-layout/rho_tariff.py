#!/usr/bin/env python3
"""Source-bound fixed-rho tariff corroboration. @CubeJerry/Codex; Apache-2.0."""
import argparse
import hashlib
from fractions import Fraction
import json
from pathlib import Path
import re


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate(root):
    manifest = json.loads(Path(__file__).with_name('RHO-SOURCES.json').read_text())
    data = {}
    for row in manifest['files']:
        raw = (root/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source mismatch: '+row['path'])
        data[row['path']] = raw.decode()
    fragments = {
      'upstream/build/sections/05-layers.tex': [r'one common offset $0\le\rho<K$', r'on the $D$ selected bits', r'\Gamma(K)\Gamma(\rho+1)\Gamma(w)'],
      'upstream/build/sections/06-transforms.tex': [r'b=(\ell-1)\bmod K', r'offset $(h-b)\bmod K$', r'$O(Tpd^{\lambda\prime})$ per round'],
      'research/p104-6030-deferred-layer/PROOF.md': ['mu_tau   < 2^-94010', 'K=128G', 's=max(N,h^eta)'],
      'notes/compact-control-movement.tex': [r'j_i=\rho+iK'],
      'notes/compact-control-layout.tex': [r'F(e)\le(s/W)F(e/m)+O(G^\tau e^\tau+1)', r'no factor $K^\tau$'],
    }
    norm = lambda s: re.sub(r'\s+', '', s.replace("\\lambda'", r'\lambda\prime'))
    for path, fs in fragments.items():
        for fragment in fs:
            need(norm(fragment) in norm(data[path]), 'missing interface: '+path+' / '+fragment)
    selected = json.loads(data['certificates/selected-result.json'])
    need(selected['kappa'] == '781451/250000000', 'selected source changed')
    return {'sources': len(data), 'fragments': sum(map(len, fragments.values())), 'base': manifest['base_commit']}


def schedules():
    cases = total = 0
    for ell in range(2, 71):
        for k in range(1, ell):
            q, b = divmod(ell-1, k)
            pairs = [divmod(h-b, k) for h in range(ell-2, b-1, -1)]
            need(len(pairs) == q*k and len(set(pairs)) == q*k, 'main round count')
            need(set(pairs) == {(j, rho) for j in range(q) for rho in range(k)}, 'chunk/plane coverage')
            for leading in (0, 1):
                need(len(pairs)+b+leading == ell-1+leading, 'outer total')
                need(b+leading <= k, 'prefix count')
            cases += 1; total += len(pairs)
    q, b = divmod(6-1, 2)
    need(q*2 == 4 and q*2*2 == 8, 'extra inner sweep control')
    return {'pairs': cases, 'main_rounds': total, 'ell6_K2_actual': 4, 'ell6_K2_extra_sweep': 8}


def coordinates():
    cases = 0
    for n in (2, 3, 5):
        p = tuple((a+1) % n for a in range(n))
        swaps = [(0, a) for a in range(1, n)]
        for f in (1, 2, 3):
            for k in (1, 2, 4):
                for rho in range(k):
                    initial = [1 << i for i in range(3+n*f*k+2)]
                    actual, expected = initial.copy(), initial.copy()
                    for a, b in swaps:
                        for j in range(f):
                            x, y = 3+(a*f+j)*k+rho, 3+(b*f+j)*k+rho
                            actual[y] ^= actual[x]; actual[x] ^= actual[y]; actual[y] ^= actual[x]
                    for a in range(n):
                        for j in range(f):
                            expected[3+(p[a]*f+j)*k+rho] = initial[3+(a*f+j)*k+rho]
                    need(actual == expected, 'selected-bit permutation/spectator failure')
                    need(actual != initial, 'omitted-return control')
                    for a, b in reversed(swaps):
                        for j in range(f):
                            x, y = 3+(a*f+j)*k+rho, 3+(b*f+j)*k+rho
                            actual[y] ^= actual[x]; actual[x] ^= actual[y]; actual[y] ^= actual[x]
                    need(actual == initial, 'literal inverse')
                    cases += 1
    selected = list(range(8)); selected[0], selected[4] = selected[4], selected[0]
    need(selected != list(range(4, 8))+list(range(4)), 'full-chunk control')
    return cases


def endpoint_control():
    def h(v, axis):
        out, bit = v.copy(), 1 << axis
        for low in range(len(v)):
            if not low & bit:
                out[low], out[low|bit] = v[low]+v[low|bit], v[low]-v[low|bit]
        return out
    one = h([1, 0, 0, 0], 0)
    every = h(one, 1)
    need(one == [1, 1, 0, 0] and every == [1, 1, 1, 1], 'extra-plane endpoint control')
    return {'one_rho': one, 'extra_inner_plane': every}


def bill():
    n, pairs, role_swaps = 16, 3, 2
    events = {'coordinate_additions': 6*(n-1)*pairs, 'monomial_additions': 7,
              'aligned_role_swap_scans': 4*role_swaps, 'scalar_phase_scans': 11,
              'owned_scans': 8, 'park_return_scans': 9, 'descriptor_after_cutoff': 1}
    need(sum(events.values()) > events['coordinate_additions'], 'permutation-only bill control')
    need(6*(32-1)*pairs != events['coordinate_additions'], 'growing-template control')
    for x in range(-3, 4):
        for y in range(-3, 4):
            a, b = x, y
            a += b; b -= a; a += b; b = -b
            need((a, b) == (y, x), 'aligned four-scan role swap')
    return {'fixture_only': True, 'events': events, 'total': sum(events.values())}


def selected_guards():
    cases=0
    for p in (2,3,4,7,8,15,16,31,63,127,256,1000,4096,65537):
        ell=(p-1).bit_length(); g=4*ell+6; k=128*g
        need(k>=g+4*ell+10, 'logarithmic-K sufficient guard')
        delta=p*(Fraction(2,2**g)+Fraction(8,2**(k-g)))
        need(delta<=Fraction(5,128*p**3), 'compact bad-fraction bound')
        cases+=1
    p=16;g=22
    need(p*(Fraction(2,2**g)+8)>Fraction(5,128*p**3), 'underfunded-K control')
    c,q,x=9,3,2304
    need(c*x**q<=2**(x//8-1), 'polylog absorption fixture')
    need(c*80**q>2**(80//8-1), 'constant-only threshold control')
    return {'K_guard_cases':cases,'absorption_x':x,'underfunded_K':'rejected','constant_only_threshold':'rejected'}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--repo', type=Path, default=Path.cwd())
    args = ap.parse_args()
    print(json.dumps({'status': 'PASS_FIXED_RHO_TARIFF', 'sources': authenticate(args.repo.resolve()),
                     'schedules': schedules(), 'coordinate_cases': coordinates(),
                     'endpoint_control': endpoint_control(), 'complete_bill_fixture': bill(), 'selected_guards': selected_guards(),
                     'limits': 'source-bound accounting; physical primitives/backing retained'}, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
