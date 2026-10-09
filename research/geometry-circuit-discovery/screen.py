"""Exact support-weighted central-factor diagnostics; no new network.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json
from math import comb
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research/mechanism-prep'))
from scorecard import design_envelope, envelope_residual, encode


def require(test, message):
    if not test:
        raise AssertionError(message)


def binary_basis(rows):
    pivots = {}
    for original in rows:
        row = original
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return [pivots[p] for p in sorted(pivots, reverse=True)]


def rational_rank(rows):
    pivots = {}
    for row in rows:
        row = list(map(Q, row))
        for p, base in sorted(pivots.items()):
            c = row[p]
            if c:
                row = [a-c*b for a,b in zip(row,base)]
        p = next((j for j,x in enumerate(row) if x), None)
        if p is not None:
            c = row[p]
            pivots[p] = [x/c for x in row]
    return len(pivots)


def dot(x,y):
    return sum(a*b for a,b in zip(x,y))


def e8():
    # Twice the norm-two roots, modulo antipodes. First nonzero is positive.
    labels = []
    for i,j in combinations(range(8),2):
        for sign in (-1,1):
            x = [0]*8; x[i] = 2; x[j] = 2*sign
            labels.append(tuple(x))
    for tail in product((-1,1),repeat=7):
        x = (1,)+tail
        if sum(a == -1 for a in x)%2 == 0:
            labels.append(x)
    gram = [[Q(dot(x,y),4) for y in labels] for x in labels]
    require(all(x.denominator == 1 for row in gram for x in row), 'integral E8 root products')
    core = [sum((1+int(x)%2)%2 << j for j,x in enumerate(row)) for row in gram]
    return labels, gram, core


def hamming4():
    # Four-letter words of length three, orthogonality at Hamming distance two.
    words = list(product(range(4),repeat=3))
    labels = [(1,)+tuple(int(a == b) for a in w for b in (1,2,3)) for w in words]
    gram = [[2-sum(a != b for a,b in zip(x,y)) for y in words] for x in words]
    core = [sum(int(i == j or x == 0) << j for j,x in enumerate(row)) for i,row in enumerate(gram)]
    return labels, gram, core


def weighted_basis(labels, core):
    """Minimize support-span cost among exactly rank(C) central linear forms.

    For C=UV with r=rank(C) inner coordinates, V is a rowspace basis of C.
    Enumerate this rowspace, then use the weighted vector-matroid greedy theorem.
    Does NOT optimize redundant factors whose rows may lie outside rowspace(C).
    """
    basis = binary_basis(core)
    require(len(basis) <= 12, 'explicit bounded rowspace enumeration')
    candidates = []
    for selector in range(1,1 << len(basis)):
        mask = 0
        for j,b in enumerate(basis):
            if selector >> j & 1:
                mask ^= b
        support = [x for j,x in enumerate(labels) if mask >> j & 1]
        cost = rational_rank(support)
        candidates.append((cost,selector,mask))
    selected = []; pivots = {}
    for cost,selector,mask in sorted(candidates):
        v = selector
        while v:
            j = v.bit_length()-1
            if j in pivots:
                v ^= pivots[j]
            else:
                pivots[j] = v
                selected.append((cost,selector,mask))
                break
    require(len(selected) == len(basis), 'full weighted basis')
    # Construct U exactly and check every row of C is recovered from V.
    coordinates = {0:0}
    for j,(_,_,mask) in enumerate(selected):
        coordinates.update({v^mask:c^(1 << j) for v,c in list(coordinates.items())})
    require(all(row in coordinates for row in core), 'exact UV factorization')
    all_rows = [dict(selector=s,mask=hex(v),support_size=v.bit_count(),span_dimension=c)
                for c,s,v in sorted(candidates, key=lambda x:x[1])]
    histogram = dict(sorted(Counter(c for c,_,_ in candidates).items()))
    return dict(binary_rank=len(basis),rowspace_basis=[hex(x) for x in basis],
        nonzero_rowspace_count=len(candidates),
        support_dimension_histogram=histogram,
        cumulative_rank_by_cost={cost:len(binary_basis(s for c,s,_ in candidates if c<=cost)) for cost in histogram},
        minimum_basis_loss=sum(c for c,_,_ in selected),
        chosen_forms=[dict(cost=c,selector=s,mask=hex(v)) for c,s,v in selected],
        U_rows=[coordinates[row] for row in core],
        rowspace_catalog=all_rows,
        scope='All binary factorizations with inner dimension exactly rank(C); copied center must contain the full input-support span. Redundant factors and other frame schedules are not excluded.')


def hamming_module_rank(k,D):
    """Exact rank of I+A_D for q=4, named k=2D-1, D a power of two.

    N=J_4 decomposes into one two-dimensional nilpotent block and two
    trivial one-dimensional blocks over F2. Expand e_D in the live blocks.
    """
    require(k == 2*D-1 and D>0 and D&(D-1) == 0, 'stated Hamming family')
    # I+A_D = e_D(N_1,...,N_k) by expansion A_i=I+N_i.
    coefficients = [(int(j == 0)+comb(k-j,D-j))%2 for j in range(D+1)]
    require(coefficients == [0]*D+[1], 'elementary-symmetric cancellation')
    summands = []
    for live in range(D,k+1):
        monomials = [sum(1<<i for i in t) for t in combinations(range(live),D)]
        rows = [sum(1<<(s|t) for t in monomials if not s&t) for s in range(1<<live)]
        r = len(binary_basis(rows))
        mult = comb(k,live)*2**(k-live)
        summands.append(dict(live=live,block_rank=r,multiplicity=mult))
    return dict(k=k,D=D,n=4**k,d=3*k+1,binary_rank=sum(s['block_rank']*s['multiplicity'] for s in summands),summands=summands)


def audit_core(name, generator):
    labels,gram,core = generator()
    n = len(labels); d = rational_rank(labels)
    require(rational_rank(gram) == d, 'nondegenerate fitting factor')
    for i in range(n):
        require(core[i] >> i & 1 and gram[i][i] != 0, 'normalized nonzero diagonal')
        for j in range(n):
            if i != j and core[i] >> j & 1:
                require(gram[i][j] == gram[j][i] == 0, 'mutual fitting zeros')
    factor = weighted_basis(labels,core)
    loss = Q(factor['minimum_basis_loss'],n)
    envelope = design_envelope(d,d)
    residual = envelope_residual(envelope,[1,1],[loss,loss])
    ceiling = n*envelope['equal_loss_ratio_ceiling_with_one_role_per_label_interval'][1]
    # ell must be strictly below the true ceiling, which is <= this upper bound.
    maximum_integer_loss = -((-ceiling.numerator)//ceiling.denominator)-1
    return dict(name=name,n=n,d=d,labels=labels,core_rows=[hex(x) for x in core],
        factor=factor,copied_loss_per_label=loss,
        independent_roles_per_label_granted=1,
        gross_gain_fraction_after_central_cost=1-2*loss,
        necessary_maximum_integer_loss_per_equal_axis_at_target=maximum_integer_loss,
        optimistic_joint_budget=envelope,optimistic_residual=residual,
        decision='REJECT minimal-rank center proposal' if residual[1] < 0 else 'UNRESOLVED optimistic screen',
        scope='Grants the current rank-one copied-center ledger, one independent auxiliary per label and perfect batching. This is a rejection screen for the stated proposal, not a compiler or a family-wide impossibility theorem.')


def audit():
    cores = [audit_core('E8 root lines / support-weighted centers',e8),
             audit_core('Four-letter Hamming length-three core',hamming4)]
    large = design_envelope(22,22)
    large_residual = envelope_residual(large,[1,1],[0,0])
    require(large_residual[1] < 0, 'named larger Hamming instance source floor')
    small_module=hamming_module_rank(3,2)
    large_module=hamming_module_rank(7,4)
    require(small_module['binary_rank'] == cores[1]['factor']['binary_rank'], 'independent small Hamming rank')
    return dict(status='BOUNDED GEOMETRY-CIRCUIT DISCOVERY; NO NEW EXPONENT',
        target_bit_saving=Q(1,511),candidates=cores,
        hamming_next_named_instance=dict(alphabet=4,length=7,zero_distance=4,
            n=4**7,d=22,independent_roles_per_label_granted=1,copied_loss_granted=0,
            binary_module_certificate=large_module,
            envelope=large,residual=large_residual,
            scope='Same rank-one independent-producer adapter only. Binary rank is certified by nilpotent module decomposition; no physical producer implementation claimed.'),
        construction_candidate_selected=False,parameter_sweep_performed=False,
        sources_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in [HERE/'screen.py',ROOT/'research/mechanism-prep/scorecard.py',ROOT/'research/kappa-nine/target_budget.py']})


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=audit()
    if args.output:
        args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    for c in result['candidates']:
        print(c['name'], 'n,d,r=',c['n'],c['d'],c['factor']['binary_rank'],
              'weights=',c['factor']['support_dimension_histogram'],
              'loss=',c['copied_loss_per_label'],
              'residual=',tuple(float(x) for x in c['optimistic_residual']))
    print('No complete finite construction or stronger exponent certified.')
