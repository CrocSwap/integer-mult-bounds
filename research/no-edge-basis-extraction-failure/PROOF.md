# Irreducibility need not survive image-basis extraction

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Result

For every integer `n>=3`, there is a binary off-diagonal pattern space H
with these properties:

- H has dimension `n+1` and contains no matrix unit. Its minimum nonzero
  pattern weight is six.
- Its complete noncoordinate rank-one idempotent pool has exactly `n+1`
  projectors and joint-image dimension n.
- The full pool acts irreducibly on that image.
- There are exactly two proper subcollections with full joint image. Each
  has n independent images and is reducible.

The construction uses width `3n` and permits arbitrary zero padding. It
therefore gives, at every image dimension `n>=3`, a complete no-edge pool
with no irreducible image-basis subcollection. Its excess of one projector
is the least possible for that property: a full-image collection of n
projectors is itself an image-basis collection.

This disproves a general basis-extraction premise that could otherwise be
used to extend the theorem in
[PR #7686](https://github.com/CrocSwap/integer-mult-bounds/pull/7686),
[exact proof](https://github.com/aliromman/integer-mult-bounds/blob/9da06cbe0b888293cbb249cb29eef0f37addaa4f/research/no-edge-image-basis-bound/PROOF.md).
At image dimension seven, the new family has pattern dimension eight.
**It does not answer the extraction question at pattern dimension five.**
A proof that uses that extra restriction remains possible.

## 2. A three-copy embedding preserves exact complete pools

Let A be any linear subspace of `M_n(F2)`. Let E send each coordinate vector
to the sum of three new coordinate vectors in its own block. Thus
`E^T E=I`. Define

```text
R(B) = E B E^T = B tensor J_3,
Phi(B) = off(R(B)),
```

where J_3 is the all-one three-by-three matrix. Over F2, `J_3^2=J_3`, so
R is an injective algebra map. It preserves ranks and idempotence. On the
replicated coordinate space `E(F2^n)`, its action agrees with that of B
under E.

The map Phi is injective. An off-block entry of B appears in all nine
positions of its three-by-three block. A diagonal entry appears in the six
off-diagonal positions of its own block. These supports are disjoint.
For a matrix B with d diagonal ones and o off-diagonal ones,

```text
weight(Phi(B)) = 6d + 9o.
```

Consequently `dim Phi(A)=dim A`, and every nonzero pattern has weight at
least six. In particular, Phi(A) contains no matrix unit.

**Exact pool lemma.** The complete noncoordinate rank-one idempotent pool of
Phi(A) is precisely the image under R of the rank-one idempotents in A,
including coordinate projectors in A.

To prove the reverse inclusion, suppose `x y^T` is a rank-one idempotent
with nonzero pattern `Phi(B)` for `B in A`. Choose a nonzero entry `B_ij`.
If `i!=j`, the corresponding off-block rectangle consists of nine ones.
All image bits in block i and all covector bits in block j are therefore
one. If `i=j`, the six off-diagonal ones in that block force all three image
bits and all three covector bits there to be one.

Use the block of three known image bits. For any ambient column s, choose
a row in that block different from s. The corresponding off-diagonal
entry forces y_s to the B entry for that column's block. Thus y is constant
on each three-coordinate block. The known block of covector ones gives the
same conclusion for x. Write `x=E u`, `y=E v`. Then
`x y^T=R(u v^T)`, and injectivity of Phi gives `B=u v^T`. Since
`y^T x=v^T u`, B is a rank-one idempotent in A. The forward inclusion follows
from rank preservation, idempotence and injectivity of Phi.

This proof also treats extra zero coordinates: the known nonzero blocks force
all factors on the zero rows and columns to vanish. No new noncoordinate
pool member arises from padding. There is no ambient irreducibility claim:
the action under study is on the joint image, which lies in `E(F2^n)`.

## 3. The small matrix space

Index coordinates by `0,...,n-1`, with subscripts taken modulo n. Define

```text
C_i = e_i (e_i+e_(i+1))^T,    0 <= i < n,
Q   = e_0 e_0^T,
A   = span{C_0,...,C_(n-1),Q}.
```

All listed matrices are rank-one idempotents. They are independent. For each
row `i>=1`, its coefficient is determined by its off-diagonal entry in column
`i+1`. The two row-zero vectors `e_0+e_1` and `e_0` are independent. Thus
`dim A=n+1`.

A general matrix in A has row i, for `i>=1`, either zero or
`r_i=e_i+e_(i+1)`. Row zero is one of

```text
0, e_0, e_1, e_0+e_1.
```

The nonzero rows r_i are pairwise distinct when `n>=3`, and none is in the
row-zero list. A rank-one binary matrix has all its nonzero rows equal.
Hence a rank-one matrix in A has just one nonzero row. The possible
idempotents are C_i for `i>=1`, Q and C_0. The remaining row-zero possibility
`e_0 e_1^T` is nilpotent and is not an idempotent. Thus **A contains exactly
the n+1 listed rank-one idempotents**.

Apply the exact pool lemma to `H=Phi(A)`. Its complete pool is exactly
`R(C_0),...,R(C_(n-1)),R(Q)`. Its joint image is `E(F2^n)`, of dimension n,
and its pattern dimension is `n+1`.

The full pattern-weight enumerator is

```text
(1 + z^6 + z^9 + z^15) (1 + z^15)^(n-1).
```

The first factor describes the four row-zero choices. Each other row
contributes either zero or one diagonal and one off-diagonal entry, of
replicated weight fifteen. This also proves that weight six is attained.

## 4. Full irreducibility and failure of each basis

It suffices to work in the small coordinate space. Suppose a nonzero
subspace is invariant under all C_i and Q. If it contains a vector v on
which some C_i is nonzero, it contains e_i. Successive cycle projectors
send this coordinate vector around the cycle, so the subspace contains all
coordinate vectors.

If every C_i kills v, the equations `v_i+v_(i+1)=0` make v the all-one vector
w. But `Qw=e_0`, which again gives every coordinate vector by the cycle.
Thus the full action is irreducible. Replication preserves this action on
the joint image.

Any full-image subcollection must contain C_i for every `i>=1`: it is the
only projector whose image is e_i. It must also contain at least one of C_0
and Q. There are exactly three choices, including the full collection.

If Q is omitted, all C_i kill the nonzero vector w. Its line is a proper
invariant subspace. If C_0 is omitted, the line spanned by e_1 is invariant:
C_1 fixes e_1, every other retained C_i kills it, and Q kills it. Thus both
proper full-image subcollections are reducible. These are exactly the two
image-basis subcollections. No choice of a different image basis from this
pool repairs the defect.

The mechanisms differ: the cycle alone has a common kernel, while the
cycle with C_0 replaced by Q has an invariant line despite full covector
rank. A test that checks only image and covector ranks would miss the latter.

## 5. Exact verification and source boundary

The verifier checks the complete pool for every n from three through twelve.
It enumerates all 16358 nonzero patterns and all 16368 projector subsets
across those ten cases. Exactly three subsets per case have full image;
the two proper subsets have the explicit kernel or invariant-line witness.
Full covector rank and strong incidence certify each full action. Direct
closure of every nonzero vector orbit also checks the full and reduced
actions for n from three through eight.

The embedding lemma is tested on every one of the 67 subspaces of
`M_2(F2)`. The verifier compares the complete lifted pool with all original
rank-one idempotents in each subspace, for 96 pool memberships. It also checks
the algebra law on all 256 ordered matrix pairs. A two-copy control sends
a nonzero idempotent to a nilpotent. A one-copy control loses diagonal
information under off and permits a matrix unit. These checks are finite;
the proof in Section 2 supplies the universal statement.

The four-trial rank-one lift rule and binary matrix primitives are reused
from [PR #7686](https://github.com/CrocSwap/integer-mult-bounds/pull/7686),
[exact verifier](https://github.com/aliromman/integer-mult-bounds/blob/9da06cbe0b888293cbb249cb29eef0f37addaa4f/research/no-edge-image-basis-bound/verify.py).
The new verifier has no runtime dependency on that package. Nick Petalas's
earlier fiber lemma is credited by the sources of PR #7686.

unpaidmoon's cyclic complete-pool example in
[PR #6962](https://github.com/CrocSwap/integer-mult-bounds/pull/6962),
[exact proof](https://github.com/unpaidmoon/integer-mult-bounds/blob/46dbf04cae1140f33bd6a12fa6967a54f8d2c417/research/pattern-dim4-irreducible-image/PROOF.md),
is related prior work. It uses a four-cycle with two next-coordinate reads
and is itself an irreducible basis. The present cycle plus one extra
projector and exact replication address the opposite extraction question.
No earlier cyclic example is claimed as new.

No paid BIT word, native operation, complete invoice or kappa improvement
is supplied. The selected frontier and all five assumptions stay unchanged.
Predecessor scientific replays, the selected cold replay, Lean and Docker
were not run. Independent human and formal-kernel review are unclaimed.

## Open next questions

Does the additional condition of pattern dimension five force an irreducible
seven-dimensional complete pool to contain an irreducible image-basis
subcollection? The present counterexample uses pattern dimension eight at
that image dimension. A proof must use the smaller pattern space; the general
extraction premise is false.
