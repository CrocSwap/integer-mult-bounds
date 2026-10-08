#!/usr/bin/env python3
"""Exact near-balanced bit construction with the retained semantic assembly.

Dominik Scholz, with substantial OpenAI GPT-6 Astra/Codex assistance.
Apache-2.0. PR24 basis/producer, PR25 A5 block, PR21 complex interface,
PR23 semantic assembly and attributed RaD transfers are dependencies.
"""
from collections import Counter
from difflib import unified_diff
from fractions import Fraction as Q
from hashlib import sha256
from math import comb, prod
from pathlib import Path
import json

import endpoint_semantic_composition as composition
import near_balanced_controls as controls
from certify import require
from partial_swap_network import moment

ROOT = Path(__file__).resolve().parents[1]
BIT_SAVING = Q(52007, 4000000000)
KAPPA = Q(13001411, 10**12)
HEADROOM = Q(1, 10**8)


def bit_profile():
 rows=json.loads((ROOT/'certificates/near-balanced-axes.json').read_text())
 a,b,k=(r['h'] for r in rows);H=a*b;m=H*k;N=prod(r['v'] for r in rows)
 for x in rows:
  h=x['h'];assert x['v']==comb(h,3) and x['q']==3*x['v']+h
  assert x['baseline_R']==x['c']+x['q'] and x['R']==x['baseline_R']-x['matched']
  assert x['loss']==h*(h-1)
  assert len(x['histogram'])==h+1 and all(n>=0 for n in x['histogram'])
  assert sum(r*n for r,n in enumerate(x['histogram']))==x['rank_sum']==h*x['R']+2*x['loss']
  assert x['scalar']['all_additions_disjoint'] and x['scalar']['all_partial_outputs_exact'] and x['scalar']['every_node_has_common_point']
 B1,B2,B3=(N//x['v']*x['R'] for x in rows);assert B3>=B1
 W=2*N+B2+B3;L=sum(N//x['v']*x['loss'] for x in rows);s=W*m-2*N+2*L
 z=Counter()
 def add(n,*widths):
  for t in widths:
   if n and t:z[t]+=n
 add(B1,a,1,1,a-2,1,m-2*(a+k))
 add(B3-B1,k,m-2*k);add(B2,b,m-2*b)
 add(2*N*(2*k-1),1);add(2*N,k-2,H-2*k+2,m-2*H-2*k+2)
 add(2*N*((a+b-1)-(b-2)),1);add(2*N,b-2,H-2*(a+b-1))
 for h,x in zip((a,b,k),rows):
  add(2*N,1,h-2)
  for r,n in enumerate(x['histogram']):
   c=N//x['v']*n
   if 2*r>h:add(c,2*r-h);add(c*(h-r),1)
   else:add(c*r,1)
 assert all(0<t<m and count>0 for t,count in z.items())
 assert sum(t*n for t,n in z.items())==s
 return dict(dimensions=[a,b,k],m=m,N=N,B1=B1,B2=B2,B3=B3,W=W,L=L,rank_sum=s,deficit=2*(N-L)),z


def certificate():
    prior, _ = composition.validate_dependencies()
    counts, rows = bit_profile()
    require(counts['dimensions'] == [33, 31, 34], 'Selected dimensions changed')
    bit = dict(counts=counts, **moment(counts['m'], counts['W'], rows, BIT_SAVING, True))
    require(bit['strict_gap'] > Q(1, 10**13), 'Bit moment gap')
    bridge_bit = dict(counts=dict(counts, child_multiplicities=rows))
    bridge = composition.finite_bridge(prior, bridge_bit)
    def assemble(**kwargs):
        return composition.assembly(bridge, a=BIT_SAVING, h=HEADROOM, **kwargs)
    assembly = assemble(kappa=KAPPA)
    require(assembly['absorption_gap'] > Q(5, 10**13), 'Final absorption gap')
    require(KAPPA > composition.KAPPA, 'No improvement over the prior composition')
    negatives = []
    def reject(name, check):
        try:
            check()
        except (AssertionError, ValueError):
            negatives.append(name)
        else:
            raise AssertionError('Negative control accepted: '+name)
    reject('next_bit_1e-11_grid', lambda: moment(counts['m'], counts['W'], rows,
                                               BIT_SAVING+Q(1, 10**11), True))
    no_second = rows.copy()
    no_second[31] -= counts['B1']
    no_second[1] += 31*counts['B1']
    reject('omit_A1_second_block', lambda: moment(counts['m'], counts['W'],
                                                 no_second, BIT_SAVING, True))
    no_a5 = rows.copy()
    no_a5[29] -= 2*counts['N']
    no_a5[1] += 58*counts['N']
    reject('omit_A5_block', lambda: moment(counts['m'], counts['W'],
                                          no_a5, BIT_SAVING, True))
    reject('old_guard', lambda: assemble(kappa=KAPPA, old_guard=True))
    reject('old_exposures', lambda: assemble(kappa=KAPPA, old_exposures=True))
    reject('unsupported_2_minus16', lambda: assemble(kappa=Q(1, 2**16)))
    paths = [Path(__file__), ROOT/'scripts/near_balanced_controls.py',
             ROOT/'scripts/near_balanced_producer.py',
             ROOT/'certificates/near-balanced-axes.json',
             ROOT/'notes/near-balanced-bit.tex',
             ROOT/'docs/research/near-balanced-bit.md',
             ROOT/'scripts/endpoint_semantic_composition.py',
             ROOT/'scripts/endpoint_gauge/bit.py']
    return dict(
        status='CONDITIONAL NEAR-BALANCED BIT CONSTRUCTION; NOT FORMAL VERIFICATION',
        kappa=KAPPA, bit=bit, basis=controls.basis(),
        a1_controls=[controls.a1(33, seed) for seed in (4, 7)],
        a5_control=controls.a5(), finite_bridge=bridge, assembly=assembly,
        eventual_bounds=composition.bulk.cutoffs(bridge, assembly),
        negative_controls=negatives,
        predecessor_certificate_sha256=composition.PINS,
        source_sha256={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                       for p in paths},
        provenance=dict(PR23='661ebabc1076c9f525d7ce4967c876b203fa9827',
                        PR24='ed90fd940279c336ebc45968631bdebfb087b505',
                        PR25_A5='61f81dc9c864d921adbc2ddeeeec3e672e688335',
                        prior_PR27='c297233e788a23e9833ad1ee07fc8517accd0f42'),
        scope='New bit dimensions and common-basis ordered blocks; unchanged PR21 '
              'complex circuit and PR23 semantic/bulk analytic interfaces. Generic '
              'basis and all-size compiler/tape arguments remain written proofs.')


def proof_patch():
    name = 'notes/semantic-bulk-17-note.tex'
    original = (ROOT/name).read_text()
    marker = r'\begin{thebibliography}{9}'
    require(original.count(marker) == 1, 'Pinned proof insertion point')
    updated = original.replace(marker, '\\input{notes/near-balanced-bit.tex}\n\n'+marker)
    return ''.join(unified_diff(original.splitlines(keepends=True),
                                updated.splitlines(keepends=True),
                                fromfile='a/'+name, tofile='b/'+name))


def main():
    result = certificate()
    (ROOT/'certificates/near-balanced-network.json').write_text(
        json.dumps(composition.canonical(result), indent=2, sort_keys=True)+'\n')
    (ROOT/'patches/near-balanced-bit.patch').write_text(proof_patch())
    print('PASS conditional kappa='+str(KAPPA)+'; bit saving='+str(BIT_SAVING))
    print('47 strict constraints, 7 margins, 6 rejected negative controls')
    print('Product row degree:', result['finite_bridge']['rows']['degree'])


if __name__ == '__main__':
    main()
