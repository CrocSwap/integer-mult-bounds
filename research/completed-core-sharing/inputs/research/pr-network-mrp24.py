"""Explicit maximal resolvable quadruple packing on 24 points.

Implements Zhang--Ge, J. Combin. Des.18(2010),209--223,
DOI10.1002/jcd.20234, Lemmas2.2,2.4, using an elementary RH(6^4).
Only the exact partition and Gram identities are asserted here.
"""
import hashlib
import itertools as it
import json
from collections import Counter
from pathlib import Path

P=Path(__file__).resolve().parent
triples=list(it.combinations(range(24),3))
index={T:i for i,T in enumerate(triples)}
classes=[]

def point(g,a):
    return 6*g+a%6

def add(blocks):
    blocks=[sorted(Q) for Q in blocks]
    assert len(blocks)==6 and sorted(it.chain.from_iterable(blocks))==list(range(24))
    assert all(len(set(Q))==4 for Q in blocks)
    classes.append(blocks)

# Four-group transversal design: fourth coordinate a+b+c (mod6).
# A class fixes b-a and c+a. Every coordinate is a permutation of Z6.
for u in range(6):
    for v in range(6):
        add([[point(0,a),point(1,a+u),point(2,-a+v),point(3,a+u+v)]
             for a in range(6)])

# Circle-method one-factorization of K6: infinity5 and Z5.
factors=[[(5,j)]+[((j+i)%5,(j-i)%5) for i in (1,2)] for j in range(5)]
assert Counter(tuple(sorted(e)) for F in factors for e in F)==Counter(it.combinations(range(6),2))
def pair(g,i,k):
    return [point(g,a) for a in factors[i][k%3]]

# Add all two-plus-two blocks between groups, except the reserved group
# matching {(0,1),(2,3)}, to obtain the RG(12^2) of Lemma2.4.
for matching in [[(0,2),(1,3)],[(0,3),(1,2)]]:
    for i in range(5):
        for shift in range(3):
            add([pair(g,i,k)+pair(h,i,k+shift) for g,h in matching for k in range(3)])
assert len(classes)==66

# Lemma2.2 on each reserved 12-point group, synchronized across the two.
for i in range(5):
    for shift in range(3):
        if i==0 and shift==0:
            continue
        add([pair(g,i,k)+pair(h,i,k+shift) for g,h in [(0,1),(2,3)] for k in range(3)])
for s in range(3):
    add([Q for g,h in [(0,1),(2,3)] for Q in
         [pair(g,0,s)+pair(g,0,s+1),pair(h,0,s)+pair(h,0,s+1),
          pair(g,0,s+2)+pair(h,0,s+2)]])
assert len(classes)==83

groups=[[index[T] for Q in C for T in it.combinations(Q,3)] for C in classes]
used=Counter(it.chain.from_iterable(groups))
assert len(used)==1992 and set(used.values())=={1}

# In each six-point group the leave is exactly the eight triples choosing
# one endpoint of each pair in factors[0]. Pair a triple with its disjoint
# complement; synchronize the four pairs over the four six-point groups.
for bits in range(4):
    G=[]
    for g in range(4):
        T=tuple(sorted(point(g,factors[0][k][(bits>>k)&1]) for k in range(3)))
        U=tuple(sorted(point(g,factors[0][k][1-((bits>>k)&1)]) for k in range(3)))
        G.extend([index[T],index[U]])
    groups.append(G)

assert Counter(map(len,groups))==Counter({24:83,8:4})
assert Counter(it.chain.from_iterable(groups))==Counter(range(2024))
gram_checks=0
for G in groups:
    masks=[sum(1<<p for p in triples[t]) for t in G]
    for i,a in enumerate(masks):
        for j,b in enumerate(masks):
            assert (a&b).bit_count()%2==int(i==j)
            gram_checks+=1

out=dict(status='PASS: exact coverage, parallel classes and binary GramI',h=24,
    triple_indexing='zero-based lexicographic combinations(range(24),3)',
    source=dict(authors='Xiande Zhang and Gennian Ge',year=2010,
                doi='10.1002/jcd.20234',lemmas=['2.2','2.4'],
                url='https://staff.ustc.edu.cn/~drzhangx/papers/mrpacking.pdf',
                pdf_sha256='b6758567fd48844b708fd2164f75e0957d5880c4e037adb27826a4f545a27998'),
    groups=[sorted(G) for G in groups],group_size_counts={24:83,8:4},
    quadruple_parallel_classes=classes,K6_one_factors=factors,
    covered_triples=2024,gram_entries_checked=gram_checks,
    scope='Finite partition only; physical phases and recurrence require separate validation.')
dest=P/'pr-network-mrp24.json'
dest.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(status=out['status'],groups=len(groups),sizes=out['group_size_counts'],
                     gram_entries_checked=gram_checks,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),indent=2))

# An equal-cost variant pairs cube triples along one edge rather than a
# long diagonal. Each partial group then has a displayed signed odd basis
# for its complement, avoiding a wholly alternating complement.
signed_groups=groups[:83]
complements=[]
for bits in range(4):
    G=[];basis=[]
    for g in range(4):
        a,b=pair(g,0,0)
        c=point(g,factors[0][1][bits&1]);d=point(g,factors[0][2][bits>>1])
        G.extend(index[tuple(sorted(T))] for T in [(a,c,d),(b,c,d)])
        basis.extend([[a,b,c],[a,b,d],
                      [point(g,factors[0][1][1-(bits&1)])],
                      [point(g,factors[0][2][1-(bits>>1)])]])
    signed_groups.append(sorted(G));complements.append(basis)
    all_vectors=[sum(1<<p for p in triples[t]) for t in G]+[sum(1<<p for p in B) for B in basis]
    assert len(all_vectors)==24
    assert all((a&b).bit_count()%2==int(i==j)
               for i,a in enumerate(all_vectors) for j,b in enumerate(all_vectors))
assert Counter(it.chain.from_iterable(signed_groups))==Counter(range(2024))
signed=dict(out,groups=signed_groups,partial_complement_basis_supports=complements,
            variant='Cube-edge pairs; each rank16 complement has8 norm3 and8 norm1 orthogonal vectors.')
dest=P/'pr-network-mrp24-signed.json'
dest.write_text(json.dumps(signed,indent=2)+'\n')
print(json.dumps(dict(variant=signed['variant'],sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),indent=2))
