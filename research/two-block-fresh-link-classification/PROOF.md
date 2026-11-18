# All irreducible fresh-factor links on the two fixed blocks

Work over F2 in coordinates C={0,...,5} and F={6,...,5+r}, with r>=1.
Use the normal-form projectors from unpaidmoon's PR #7281. On the first
three coordinates their image/covector pairs are (6,5), (5,6), (7,7),
written as binary bit masks. Shift these three pairs by three coordinates
for the second block. Denote the six pairs by (u_i,v_i).
Their images form a basis of C, and `v_i dot u_j = delta_ij`.
Let H be the span of their off-diagonal patterns. Then dim H=4.
For a matrix M, off(M) sets its diagonal to zero.

The complete pool of a pattern space P is the set of all rank-one
idempotents whose off-diagonal pattern is a **nonzero** member of P.
Diagonal-only projectors are excluded by this definition. Do not restrict
the complete pool to a proposed list of seven generators.

Write a candidate link as `L=x*y^T`, where `y dot x=1`,
`x=u+a`, `y=v+b`, with u,v on C and a,b on F. Assume a and b are
both nonzero, and `p=off(L)` is not in H. Put `P=H+span(p)`.
The last condition excludes diagonal-only fresh projectors; it makes
P five-dimensional. No support bound is imposed inside either block.

**Theorem.** The complete pool acts irreducibly on its joint image
if and only if

```text
u = v = h = e2+e5,                a dot b = 1.
```

In that case the complete pool is exactly the six block projectors and
L. Its joint image is `C + span(a)`, of dimension seven, and P contains
no matrix unit. In particular, disjoint fresh supports cannot work.
For a fixed r-dimensional fresh coordinate space there are exactly
`(2^r-1)*2^(r-1)` such links and distinct pattern spaces. Of these,
`2^(r-1)` are symmetric and `(2^r-2)*2^(r-1)` are nonsymmetric.

The theorem includes arbitrary core supports and nonsymmetric links.
It extends the source's restricted square family and one width-eight
witness. It does not classify arbitrary five-dimensional pattern spaces,
links with a zero fresh factor, or multiple-link extensions.

## The complete pool above H

A nonzero off-diagonal entry in one internal block fixes a nonzero image
coordinate and a nonzero covector coordinate there. Since all cross-block
and fresh entries of H vanish, the corresponding row and column force
both factors to vanish outside that block. Both internal blocks cannot
be nonzero for one rank-one lift.

In a three-coordinate block the nonzero patterns are

```text
E10+E12+E20,       E01+E02+E21,       their sum.
```

The first pattern forces image bits 1 and 2 and covector bits 0 and 2
to be one. Its zero entries force the remaining two bits to be zero.
Thus its lift is (6,5). The transpose gives (5,6). In the third pattern
all six off-diagonal entries are one, so both factors are (1,1,1).
These are the only lifts. Hence the complete pool above nonzero H
consists of the six block projectors at every ambient width. This
rederives the needed special case of the source's fiber calculation.

## Zero core factors are reducible, including extra pool elements

First suppose v=0. The fresh-row/core-column rectangle of every pattern
in P is zero. Every pool lift therefore has either zero fresh image
part or zero core covector part. It either maps into C or kills C.
Thus C is invariant. It lies in the joint image because the six old
images span C. It is proper because the original link has nonzero a.

Next suppose u=0 and v is nonzero. In the nonzero coset p+H the
fresh-row/core-column rectangle is `a*v^T`, a nonzero rank-one matrix.
Over F2 its two nonzero factors are unique. Thus every coset lift has
fresh image a and core covector v. Its core-row/fresh-column rectangle
is zero, so either its core image is zero or its fresh covector is zero.
In the first case its image is exactly a; in the second case it kills a.
Every old projector also kills a. Therefore span(a) is a proper nonzero
invariant subspace of the joint image.

These arguments use every lift of the whole coset. They do not assume
that only the original link was added. Such an assumption is false:
at width seven the link (64,69) has a unit-free pattern space whose
complete pool also contains (70,5). This pool has eight projectors.
The extra projector's covector has no fresh bit, so a pool scan restricted
to the candidate-link domain would miss it. The receipt checks this case.

## Nonzero core factors force one new pool element

Now assume u and v are both nonzero. Every pattern in p+H has the
unchanged cross rectangles `a*v^T` and `u*b^T`. Both are nonzero.
Their unique rank-one factorizations over F2 fix a, v, u and b.
Therefore L is the only lift above the coset, and the complete pool is
exactly the six old projectors plus L. The seven images are independent
because a is nonzero. Put V=C+span(a).

Define `alpha_i = v_i dot x` and `beta_i = y dot u_i`.
If beta_i=0, the line span(u_i) is invariant: the old projectors act on
it diagonally and L kills it. If alpha_i=0, the subspace spanned by x
and the other five old images is invariant. Its dimension is six; the
omitted old projector kills x and the other five old images, and L maps
into span(x). Thus irreducibility requires all twelve incidences to be one.

Since the old image and covector bases are dual, these twelve equations
force u to be the sum of the six old images and v to be the sum of the
six old covectors. Both sums equal h=e2+e5. Since `h dot h=0`,
idempotence then requires `a dot b=1`.

Conversely suppose these conditions hold. A nonzero invariant subspace
hit by any pool covector contains that projector's image. Any old image
is sent to x by L, and x is sent to every old image by the six old
projectors. Such a subspace is all of V. If every pool covector vanishes
on a vector in V, the old covectors first force its core part to zero.
The remaining vector is a multiple of a, and `y dot a=1` forces that
multiple to be zero. There is no nonzero vector in this common kernel.
This proves irreducibility.

## Pattern space and exact counts

In a positive case any fresh coordinate where a is one gives a row of
p with ones at both core hubs. These two entries survive addition of
any element of H. Hence no pattern in p+H is a matrix unit. Every
nonzero pattern in H has weight at least three, so P is unit-free.
The same row proves p is outside H. Thus dim P=5 and dim V=7.

For each of the `2^r-1` nonzero choices of a, the nonzero linear
functional `b -> a dot b` has `2^(r-1)` solutions to value one.
None is zero. These give all positive links. Symmetry is equivalent
to a=b, and `a dot a=1` means odd Hamming weight; there are
`2^(r-1)` such vectors. Subtract to obtain the nonsymmetric count.

Two different positive links cannot define the same pattern space:
if they did, both would be lifts over the same nonzero coset of H,
contrary to the unique-lift result. These are counts in the fixed
coordinate model, not counts modulo coordinate permutations.

In the basis of the six old images followed by a, every positive pool
has the same action: the old projectors are the first six coordinate
projectors, while the new projector has image and covector both equal
to the seven-entry all-ones vector. Thus nonsymmetric coordinate
supports do not produce a new action on the joint image in this class.
This is the source incidence pattern, now a consequence of the full
fresh-factor classification.

## Exact verification and limits

The verifier enumerates all 8128 rank-one idempotents at width seven
and all 32640 at width eight, including those outside the candidate-link
domain. A quotient index modulo H and a separate lookup over each of
its sixteen literal coset patterns give the same complete pools.
The candidate domain has 2079 and 18526 links, respectively. Every
negative candidate has an explicit proper invariant-subspace certificate,
checked against its complete pool. Every positive candidate has all 127
nonzero vector orbits checked. There are one and six positives, giving
889 census orbit checks. At width eight exactly four are nonsymmetric.
A separate source positive control and a valid disjoint-fresh reducible
link are checked. Five invalid-certificate or idempotence controls pass.
The finite checks support the all-width proof; they do not replace it.

No paid BIT word, native operator, physical supplier, complete invoice,
selected assumption discharge or new kappa is supplied. This is a
structural side result on the stated fixed blocks. A different block
geometry, a zero fresh factor or several links changes the contract.
Independent human and formal-kernel review are unclaimed.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Credit Nick Petalas for PR #7648's witness and question and PR #5921's
fiber context; unpaidmoon for PR #7281's square family, PR #7237's
seven-projector model and PR #6921's normal-form triple. No predecessor
code was copied. New work is Apache-2.0.
