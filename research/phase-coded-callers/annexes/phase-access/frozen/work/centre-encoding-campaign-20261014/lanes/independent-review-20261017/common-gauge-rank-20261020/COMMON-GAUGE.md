# The least rank of a common cover gauge

Let a family of pure-line ratios be C_a C_b^-1 on n binary cover axes.
The least Bruhat rank of one common cover Clifford W that makes every
ratio monomial is exactly

```text
dim span{a+b : (a,b) is an edge in the family}.
```

This is a separate derivation of the common-gauge minimum already
proved in `coherent-port/coupled-m1-terminal-20261018/AFFINE-GAUGE.md`,
SHA256
`c287019ae240fbe8ad80f0170f8d90a9964ec6db3050e5a1ea9314a6c270e0ec`.
That packet also gives an exact constructive gauge for affine labels.
The contribution here is a Lagrangian proof, an explicit statement for
arbitrary ratio graphs, and a binding to the new four-owner reduction.

The result permits arbitrary Clifford phases in W. Thus a more complex
phase choice cannot lower this rank. It concerns one common cover
conjugation. It does not restrict a joint circuit that mixes fields,
uses different interleaved charts, or modifies earlier productive calls.

For the four-owner terminal from the actual 64-port permutation, the
four lines are orthonormal and the edges form a cycle. Their difference
span has dimension three. A common gauge of rank one or two cannot
make the four cover ratios monomial.

## Proof of the lower bound

Use binary Pauli coordinates (x,z). Write X for the subspace z=0 and
Z for the subspace x=0. A pure C_a has symplectic action

```text
(x,z) -> (x+a(a dot z),z).
```

Its inverse has the same binary action. Therefore the ratio for an
edge (a,b) acts by

```text
(x,z) -> (x+Tz,z),       T=aa^T+bb^T.
```

Suppose W makes every ratio monomial, and put L=W^-1 Z. A Clifford
is monomial exactly when it preserves computational Z in binary
phase space. Thus L is invariant under each displayed shear.

Let U={x:(x,0) is in L}, and let Z0 be the projection of L to its
z coordinates. Isotropy of L gives Z0 contained in U-perpendicular.
Both have dimension n-dim(U), so they are equal.

For any z in Z0, choose (x,z) in L. Invariance gives (Tz,0) in L,
so Tz is in U. Since z is perpendicular to U,

```text
0 = z^T T z
  = (a dot z)^2+(b dot z)^2
  = (a+b) dot z.
```

The last equality uses the field F2. Hence a+b is in Z0-perpendicular,
which is U. Let D be the span of all edge differences. Then D is
contained in U.

The spaces L intersect X and L intersect Z are disjoint subspaces of
L. Consequently

```text
dim(L intersect Z) <= n-dim(U) <= n-dim(D).
```

The Bruhat rank of W is n-dim(W^-1 Z intersect Z). It is therefore
at least dim(D). This proof does not assume that the lines are
orthogonal or that the edge graph is connected.

## Construction at that rank

Take U=D and the split Lagrangian

```text
L = X_U direct_sum Z_(U-perpendicular).
```

For z perpendicular to U, every edge satisfies a dot z=b dot z.
Thus Tz=(a dot z)(a+b) is in U, and L is invariant under every ratio.

Choose a binary address basis G whose first d columns span U. A
partial Walsh transform on those d coordinates, conjugated by the
address permutation G, has inverse image L and Bruhat rank d. It
therefore makes every ratio monomial.

This Walsh can use the actual Gaussian-dyadic primitive. On one
coordinate, with S=diag(1,i), the product S C_e S is
exp(i*pi/4) times the real Walsh transform. Tensor d such products
and conjugate by G. The scalar phase is common to W and cancels in
W R W^-1. The implemented matrix itself has Gaussian-dyadic entries.
All resulting monomials retain their exact Gaussian-unit phases.

This proves equality, not only a lower bound or a finite search result.

## Actual orbit and exact checks

The checker pins
`bridge-access-20261017/permutation-cycle-20261020/CYCLE64-PROGRAMS.json`
at SHA256
`e9dadd6bc2aa58065b0079126944dd198238fb91ad55cb992d4ddf574e3989e2`.
For all 32 actual port pairs it verifies the four-line Gram matrix and
the difference rank three. It inherits the producer's reduction from
the routed terminal to these lines. It does not independently replay
the routed owner maps or their full phase equations.

As an independent exact construction check, it builds the common Walsh
for all nonempty subsets of at most four distinct nonzero directions
in dimensions one through four. It verifies the claimed binary rank
and that every conjugated cycle ratio preserves computational Z.
These cases support the general proof; they do not replace it.

For the canonical orthonormal quadruple it also uses a separate
Gaussian-integer state interpreter. It checks every column of all
four monomials, including their exact phases. The common gauge uses
three native rank-one calls. The checker does not import a compiler
or a producer module.

Run from the workspace root:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/common-gauge-rank-20261020/check_gauge_rank.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/independent-review-20261017/common-gauge-rank-20261020/check_gauge_rank.py
```

Expected output starts with `PASS_EXACT_COMMON_GAUGE_RANK`. The
receipts must be byte-identical.

## Meaning for the decoder

A scheme that applies the same W separately to all four owner fields,
executes the conjugated monomial cycle, and applies W^-1 separately
uses at least 24 native rank units in those eight gauge calls. That
literal scheme is worse than the eight-rank direct decoder. This is
not a lower bound of 24 on a decoder: cancellations, shared fields,
different intermediate charts, and a changed earlier computation
violate the stated scheme.

In particular, this theorem does not rule out a six-rank joint orbit
implementation. It states what a successful construction must change
if it starts from the common-gauge idea.

The bridge-access lane supplied the exact four-owner target. The
coherent-port lane supplied the earlier common-gauge construction and
minimum theorem. This lane derived the parallel Lagrangian proof and
the checks above. OpenAI Codex assisted the work. Independent proof
review is requested. No PR
or publication is authorized. Before any PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
