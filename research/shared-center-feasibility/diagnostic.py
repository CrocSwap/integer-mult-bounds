"""Bounded shared-center feasibility, exact arithmetic only.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/geometry-circuit-discovery'))
from screen import binary_basis, rational_rank, weighted_basis, e8, dot, require, encode


def canonical(v):
    return tuple(v) if next(x for x in v if x)>0 else tuple(-x for x in v)


def permute(mask, permutation):
    result=0
    while mask:
        bit=mask & -mask
        result |= 1 << permutation[bit.bit_length()-1]
        mask ^= bit
    return result


def low_rank_catalog(labels):
    """Every nonempty support of rational rank <=2 among the 120 lines.

    Verify all pair-span closures by integer Gram determinants, without a
    root-subsystem classification theorem or presumed transitivity.
    """
    n=len(labels)
    gram=[[dot(x,y) for y in labels] for x in labels]
    require(all(gram[i][i] == 8 for i in range(n)), 'norm-eight stored labels')
    supports={1<<i for i in range(n)}
    closures=set()
    for i,j in combinations(range(n),2):
        a=gram[i][j]
        members=[]
        for k in range(n):
            b,c=gram[i][k],gram[j][k]
            det=512+2*a*b*c-8*(a*a+b*b+c*c)
            require(det>=0, 'Euclidean Gram determinant')
            if det==0:
                members.append(k)
        require(len(members) in (2,3), 'complete rank-two plane closure')
        closures.add(sum(1<<k for k in members))
        for size in range(1,len(members)+1):
            supports.update(sum(1<<k for k in part) for part in combinations(members,size))
    return sorted(supports),dict(sorted(Counter(v.bit_count() for v in closures).items()))


def reflection_orbits(labels, catalog):
    lookup={v:i for i,v in enumerate(labels)}
    permutations=[]
    for q in labels:
        p=[]
        for x in labels:
            c=Q(dot(x,q),4)
            y=canonical(tuple(a-c*b for a,b in zip(x,q)))
            require(y in lookup, 'reflection preserves exact root lines')
            p.append(lookup[y])
        require(sorted(p) == list(range(len(labels))), 'permutation')
        permutations.append(p)
    unseen=set(catalog); orbits=[]
    while unseen:
        representative=min(unseen); seen={representative}; stack=[representative]
        while stack:
            v=stack.pop()
            for p in permutations:
                w=permute(v,p)
                require(w in unseen or w in seen, 'catalog closure and disjoint orbits')
                if w not in seen:
                    seen.add(w);stack.append(w)
        unseen-=seen
        orbits.append(dict(representative=representative,size=len(seen),members=sorted(seen)))
    return permutations,orbits


def positive_control():
    """Redundant centers CAN beat minimum rank, but the cost ledger matters.

    On four mutually orthogonal coordinate labels, C=I+cyclic_shift has
    binary rank three. Its minimum-rank factor costs six; four coordinate
    forms cost four. Both remain above the useful two-axis loss threshold.
    """
    n=4
    labels=[tuple(int(i==j) for j in range(n)) for i in range(n)]
    core=[(1<<i)^(1<<((i+1)%n)) for i in range(n)]
    original=weighted_basis(labels,core)
    expanded=weighted_basis(labels,core+[1])
    require(original['binary_rank']==3 and original['minimum_basis_loss']==6, 'control old factor')
    require(expanded['binary_rank']==4 and expanded['minimum_basis_loss']==4, 'control redundant improvement')
    return dict(n=n,d=n,core_rows=[hex(x) for x in core],old_centers=3,new_centers=4,
        old_loss=6,new_loss=4,old_factor=original,new_factor=expanded,
        new_gross_two_axis_gain=1-Q(2*4,n),
        additional_retained_center_roles=1,
        scope='An exact scalar/support-cost control, not a competitive finite network or new multiplication bound.')


def span(rows):
    values={0}
    for row in rows:
        values |= {x^row for x in list(values)}
    return values


def variable_core(gram, factor):
    """Optimize all fitting C and all factors whose forms lie in this E.

    Unique admissible target rows force F <= rowspace(V) <= E. Here the
    quotient E/F has dimension <=2, so every possible containing subspace
    is enumerated. This is NOT a search over only minimum-rank factors.
    """
    r=factor['binary_rank'];catalog=factor['rowspace_catalog']
    by_selector={v['selector']:v for v in catalog}
    allowed=[]
    for i,row in enumerate(gram):
        forbidden=sum(1<<j for j,x in enumerate(row) if x!=0)
        allowed.append([v['selector'] for v in catalog if int(v['mask'],16)&forbidden == 1<<i])
    require(all(allowed),'old core remains feasible')
    forced=binary_basis(v[0] for v in allowed if len(v)==1)
    complement=[];basis=forced[:]
    for j in range(r):
        v=1<<j
        if len(binary_basis(basis+[v]))>len(basis):
            complement.append(v);basis.append(v)
    q=len(complement)
    require(q<=2,'bounded quotient enumeration')
    quotient_subspaces={frozenset({0})};front=[frozenset({0})]
    while front:
        sub=front.pop()
        for v in range(1,1<<q):
            enlarged=frozenset(set(sub)|{x^v for x in sub})
            if enlarged not in quotient_subspaces:
                quotient_subspaces.add(enlarged);front.append(enlarged)
    checked=[]
    for sub in sorted(quotient_subspaces,key=lambda x:(len(x),sorted(x))):
        lifts=[]
        for word in binary_basis(sub):
            value=0
            for j,v in enumerate(complement):
                if word>>j&1:value ^= v
            lifts.append(value)
        space=span(forced+lifts)
        viable=all(any(v in space for v in row) for row in allowed)
        item=dict(dimension=len(binary_basis(space)),quotient_space=sorted(sub),viable=viable)
        if viable:
            chosen=[]
            for v in sorted((by_selector[x] for x in space if x),key=lambda x:(x['span_dimension'],x['selector'])):
                if len(binary_basis(chosen+[v['selector']]))>len(chosen):
                    chosen.append(v['selector'])
            item['minimum_cost']=sum(by_selector[x]['span_dimension'] for x in chosen)
            item['chosen_forms']=[by_selector[x] for x in chosen]
            item['admissible_core_rows']=[hex(int(by_selector[min(v for v in row if v in space)]['mask'],16)) for row in allowed]
        checked.append(item)
    return dict(forced_rank=len(forced),quotient_dimension=q,
        admissible_row_count_histogram=dict(sorted(Counter(map(len,allowed)).items())),
        checked_subspaces=checked,
        exact_minimum_loss=min(x['minimum_cost'] for x in checked if x['viable']),
        scope='C varies over every fitting binary matrix; all central forms must lie in this one-direction extension of the original rowspace. Any number of centers is allowed; positive-cost dependent centers can be deleted.')


def audit():
    labels,gram,core=e8()
    catalog,closures=low_rank_catalog(labels)
    permutations,orbits=reflection_orbits(labels,catalog)
    baseline=weighted_basis(labels,core)
    old_cost=baseline['minimum_basis_loss']
    cases=[]
    for orbit in orbits:
        v=orbit['representative']
        require(len(binary_basis(core+[v]))==10,'one genuinely new rowspace direction')
        expanded=weighted_basis(labels,core+[v])
        cases.append(dict(representative=hex(v),support=[j for j in range(len(labels)) if v>>j&1],
            support_rank=rational_rank([x for j,x in enumerate(labels) if v>>j&1]),
            orbit_size=orbit['size'],orbit_members=[hex(x) for x in orbit['members']],
            expanded_factor=expanded,
            jointly_variable_core=variable_core(gram,expanded),
            best_cost_covering_original_rowspace=min(old_cost,expanded['minimum_basis_loss']),
            proof='After deleting dependent forms, a covering set within S+<v> spans either S (dimension 9) or the entire extension (dimension 10). These two weighted-basis optima are exact.'))
    return dict(status='BOUNDED SHARED-CENTER FEASIBILITY; NO NEW EXPONENT',
        positive_control=positive_control(),
        e8=dict(n=120,d=8,old_binary_rank=9,old_minimum_basis_loss=old_cost,
            catalog_size=len(catalog),rank_two_closures=closures,
            reflection_generators=permutations,extension_orbits=cases,
            necessary_target_loss_ceiling=43,
            jointly_variable_core_low_rank_screen=dict(maximum_support_density=Q(3,2),
                necessary_loss_lower=Q(2*120)/(1+Q(3,2)),
                scope='Every center has support span of rational dimension at most two; arbitrary binary C with diagonal one and mutually orthogonal labels at its off-diagonal ones. Any number of centers allowed.')),
        expanded_construction_selected=any(c['jointly_variable_core']['exact_minimum_loss']<old_cost for c in cases),
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'diagnostic.py',ROOT/'research/geometry-circuit-discovery/screen.py']})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=audit()
    if args.output:
        args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print('Positive control: central support cost 6 -> 4, but no useful two-axis deficit')
    print('E8 low-rank supports:',result['e8']['catalog_size'])
    for c in result['e8']['extension_orbits']:
        print('orbit',c['orbit_size'],'support rank',c['support_rank'],
            'extension basis cost',c['expanded_factor']['minimum_basis_loss'],
            'best covering old rowspace',c['best_cost_covering_original_rowspace'],
            'variable core minimum',c['jointly_variable_core']['exact_minimum_loss'],
            'histogram',c['expanded_factor']['support_dimension_histogram'])
    print('Jointly variable C, all support ranks <=2: loss >=96')
