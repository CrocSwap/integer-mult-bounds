"""Prepared for Thiago with OpenAI GPT-6 Astra and Codex assistance. Apache-2.0.

Independent exact audit of the pinned P112 characteristic-two certificate.

Only the Python standard library is used.  This module imports no producer,
search code, or other verifier.  The source supplies integer roots and binary
upper-bound labels; the four displayed clique lists are certificate data.

Proof for every positive block size d over ANY characteristic-two field:
normalize the diagonal blocks to I_d and factor M_ij=U_i V_j with rank r.
P_i=V_i U_i are rank-d idempotents and mutually annihilate on required-zero
cliques. For an eight-clique C, E_C=I-sum_C P_i has rank r-8d. The four
cliques have odd incidence precisely at a four-clique T. Consequently
sum_C E_C=sum_T P_i has rank 4d, so 4d<=4(r-8d), or r>=9d. Known binary
labels tensored with I_d give the matching upper bound. The checker verifies
the finite inputs and rank-inequality coefficients, not a formalization of
the universal rank lemmas. No symmetry, new circuit or exponent is claimed.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path

PIN='327d2a868043e846381aa58a33053c24425e8cad522ff401b10ec8af1d649a3f'
HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[1]/'research/direct-delivery504-global/inputs/hamming/PROTOTYPE.json'
BLOCKS=[
    [2,16,57,70,78,84,100,102], [10,16,57,70,78,84,108,110],
    [2,10,16,32,34,57,70,84], [16,32,57,68,70,84,100,108],
]
ODD=[34,68,102,110]
UNIVERSAL=[16,57,70,84]
PETERSEN_PAIRS={2:(0,2),10:(1,2),32:(2,3),34:(2,4),68:(3,4),
                78:(0,1),100:(0,3),102:(0,4),108:(1,3),110:(1,4)}


def require(condition,message):
    if not condition:
        raise ValueError(message)


def pinned(raw):
    require(hashlib.sha256(raw).hexdigest()==PIN,'source SHA-256 mismatch')
    return json.loads(raw)


def graph(roots):
    require(len(roots)==112,'P112 vertex count')
    require(all(len(r)==8 and all(type(x) is int for x in r) and sum(x*x for x in r)==4
                for r in roots),'eight integer coordinates and squared norm four')
    edges=set()
    for i,j in combinations(range(112),2):
        dot=sum(roots[i][k]*roots[j][k] for k in range(8))
        require(dot in (-2,0,2),'distinct root lines with normalized Gram in {-1,0,1}')
        if dot:
            edges.add((i,j))
    return edges


def lower(edges,blocks,odd=ODD):
    require(len(blocks)==4 and len(blocks)%2==0,'four clique equations cancel their identities in characteristic two')
    for block in blocks:
        require(len(block)==8 and len(set(block))==8,'eight distinct clique vertices')
        require(all(tuple(sorted((i,j))) in edges for i,j in combinations(block,2)),
                'clique requires zeros on BOTH directed off-diagonal matrix entries')
    counts=Counter(v for block in blocks for v in block)
    require(sorted(v for v,c in counts.items() if c%2)==odd,'odd incidence is precisely the displayed four vertices')
    require(len(odd)==4 and len(set(odd))==4,'four distinct residual vertices')
    require(all(tuple(sorted((i,j))) in edges for i,j in combinations(odd,2)),
            'residual projectors mutually annihilate in BOTH directions')
    # rank(sum_T P_i)=|T|*d <= sum_C rank(E_C)=t*(r-8*d).
    # This verifies the finite coefficients; the rank lemmas are in README.
    require(Fraction(8*len(blocks)+len(odd),len(blocks))==9,
            'exact normalized block-rank bound is nine')
    return counts


def binary_basis(rows):
    pivots={};indices=[]
    for index,row in enumerate(rows):
        x=row
        while x:
            p=x.bit_length()-1
            if p in pivots:
                x^=pivots[p]
            else:
                pivots[p]=x;indices.append(index);break
    return indices


def known_graph(edges,vertices,pairs=PETERSEN_PAIRS):
    require(set(vertices)==set(UNIVERSAL)|set(pairs),'the displayed graph partition is exact')
    require(sorted(tuple(sorted(p)) for p in pairs.values())==list(combinations(range(5),2)),
            'the ten vertices represent all two-subsets of a five-set')
    for i,j in combinations(vertices,2):
        required=(i in UNIVERSAL or j in UNIVERSAL or bool(set(pairs[i])&set(pairs[j])))
        require(((i,j) in edges)==required,'exact K4 join triangular-graph structure')
    return dict(required_zero_graph='K4 joined with the triangular graph T(5)',
                usual_fitting_graph='four isolated vertices disjoint union Petersen',
                universal_vertices=UNIVERSAL,vertex_to_two_subset=pairs)


def upper(roots,labels,edges):
    require(len(labels)==112 and all(type(x) is int and 0<x<512 for x in labels),'nine binary coordinates')
    require(all(x.bit_count()%2==1 for x in labels),'nonzero diagonal in the binary Gram matrix')
    require(all((labels[i]&labels[j]).bit_count()%2==0 for i,j in edges),'all required directed zeros')
    require(all((labels[i]&labels[j]).bit_count()%2 ==
                (1+sum(a*b for a,b in zip(roots[i],roots[j]))//2)%2
                for i in range(112) for j in range(112)),
            'the complete normalized integer-Gram identity holds, including nonedges')
    basis=binary_basis(labels)
    require(len(basis)==9,'the known labels span nine dimensions')
    require(len(binary_basis([sum(((labels[i]&labels[j]).bit_count()%2)<<j
                                 for j in range(112)) for i in range(112)]))==9,
            'the explicit fitting matrix itself has rank nine')
    return basis


def reject(name,fn):
    try:
        fn()
    except ValueError as exc:
        return dict(control=name,outcome='REJECTED',reason=str(exc))
    raise ValueError('corruption was accepted: '+name)


def main():
    raw=SOURCE.read_bytes();source=pinned(raw)
    require(source['root_lines'][:8]==[[2*int(i==j) for j in range(8)] for i in range(8)],
            'source offset eight removes exactly the coordinate root lines')
    roots=source['root_lines'][8:];labels=source['binary_ports'][8:]
    edges=graph(roots);counts=lower(edges,BLOCKS);basis=upper(roots,labels,edges)
    vertices=sorted(counts)
    structure=known_graph(edges,vertices)
    restricted_basis=[vertices[i] for i in binary_basis([labels[i] for i in vertices])]
    require(len(vertices)==14 and len(restricted_basis)==9,'the induced 14-vertex graph already has rank nine')
    controls=[reject('source byte changed',lambda:pinned(raw+b' '))]
    bad=deepcopy(BLOCKS);bad[0][0]=3
    controls.append(reject('clique vertex changed',lambda:lower(edges,bad)))
    controls.append(reject('one clique omitted',lambda:lower(edges,BLOCKS[:-1])))
    inverted=set(combinations(range(112),2))-edges
    controls.append(reject('edge convention reversed',lambda:lower(inverted,BLOCKS)))
    controls.append(reject('odd-incidence set changed',lambda:lower(edges,BLOCKS,[2,68,102,110])))
    without_residual_edge=edges-{(34,68)}
    controls.append(reject('required edge inside residual clique removed',lambda:lower(without_residual_edge,BLOCKS)))
    bad_pairs=deepcopy(PETERSEN_PAIRS);bad_pairs[2],bad_pairs[10]=bad_pairs[10],bad_pairs[2]
    controls.append(reject('Petersen embedding changed',lambda:known_graph(edges,vertices,bad_pairs)))
    bad_labels=labels[:];bad_labels[0]^=1
    controls.append(reject('upper diagonal corrupted',lambda:upper(roots,bad_labels,edges)))
    bad_labels=labels[:];bad_labels[0]^=3
    controls.append(reject('upper label changed with odd norm preserved',lambda:upper(roots,bad_labels,edges)))
    controls.append(reject('upper labels truncated to eight coordinates',
                           lambda:upper(roots,[x&255 for x in labels],edges)))
    result=dict(status='PASS_INDEPENDENT_CHAR2_ALL_BLOCK_SIZES_FITTING_RANK_9D',
                source_sha256=PIN,source_vertex_offset=8,vertices=112,
                required_zero_unordered_edges=len(edges),symmetric_matrix_assumed=False,
                diagonal_normalization='left multiply by blockdiag(M_ii^-1); preserves rank and every required zero',
                factor_orientation='M_ij=U_i*V_j; P_i=V_i*U_i; U_C*V_C=I_8d implies V_C*U_C is a rank-8d idempotent',
                certificate_vertices=vertices,cliques=BLOCKS,
                classical_graph_identification=structure,
                incidence_counts=dict(sorted(counts.items())),residual_vertices=ODD,
                induced_required_zero_edges=sum(i in counts and j in counts for i,j in edges),
                block_rank_inequality='4*d <= 4*(r-8*d), hence r >= 9*d',
                exact_minimum_block_rank='9*d for every positive integer d',
                exact_fractional_minimum=9,upper_dimension=9,
                block_upper_construction='the verified binary fitting matrix tensor I_d',
                upper_basis_vertex_indices=basis,induced_upper_basis_vertex_indices=restricted_basis,
                field_scope='Every field of characteristic two, finite or infinite; no symmetry assumption.',
                corruption_controls=controls,
                scope='Exact finite certificate and elementary field-independent proof; no novelty, native circuit, or exponent claim.')
    out=HERE/'VERIFIED.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
