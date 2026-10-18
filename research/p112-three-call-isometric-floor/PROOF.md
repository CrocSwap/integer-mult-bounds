# Three independently recharted P112 calls still pay 192

This is a scoped written proof, with exact finite premises. It is not a
formal proof of integer multiplication or a lower bound for arbitrary circuits.
It extends the **two-call** isometric-chart result of Sagar Thakrar's pending
[PR2294](https://github.com/CrocSwap/integer-mult-bounds/pull/2294), head
`18d6ac4f864af2b71aa8cf5f4541fcfc4350e2f0`, to **three** independent calls.
The block-triangular averaging argument below is the new step.

Concurrent [PR2338](https://github.com/CrocSwap/integer-mult-bounds/pull/2338),
head `82700676e1d42acf98dc1921cb6ef82551620008`, section 3.4 states a broader
all-batch symmetric-chart result via normal classes and a frame lemma. It was
discovered during the final overlap check, after this core proof and verifier
were completed. This is an independent, narrower proof that does not use
that frame lemma or theorem; no first-closure claim is made. The attained
counting lemma below concerns all pure terms, not only rank-seven terms.

## 1. Exact model and inherited finite premises

Use the model of alephnan's merged PR1714
(`research/p112-batch-centre-floor/PROOF.md`, at the base in SOURCES.json).
Let X be the norm-four 112-by-8 P112 root matrix in frame-adapted Hamming
coordinates. Its eight coordinate directions have been punctured, and
`X^T X = 56 I_8`.

The binary Gram matrix on the full 120 lines is

    B_ij = 1 + (x_i dot x_j)/2 (mod 2).

It has rank nine. Write ell_i for its labels in a nine-dimensional space V
with nondegenerate symmetric bilinear form b, so `b(ell_i,ell_j)=B_ij`.
The chart of this form need not be the standard binary dot product.

We inherit the following finite support classification from Mihir Srivastava
(PR845), Adam Gall (PR1098), and the PR1714 support/pair lemmas:

* For nonzero `a in C^8`, the label span of `supp(Xa)` is V or one of eight
  hyperplanes H_i, and hence has dimension at least eight.
* For any two nonzero `a,c in C^8`, b on their support spans has rank at
  least eight.

The verifier reconstructs the Hamming geometry and checks the finite premises:
among all 511 nonzero binary functionals, 503 complement root matrices have
rank eight and eight have rank seven, each with a distinct coordinate kernel;
all 64 ordered exceptional-support pairs have binary rank eight. A nonzero
minor over Q stays nonzero over C, while the exact coordinate kernel gives
the upper bound. Thus these premises include complex isotropic coefficients.
The deduction from this finite census to the quantified support lemma is
written out in PR1714 section 2; it is an inherited lemma, not a new claim here.

There are three independent calls, indexed by 0,1,2. Call s uses an arbitrary
linear b-isometry phi_s of V, the same chart on its reader and source sides.
These charts can be chosen independently, and are granted **free**.

Allow any finite number m of active root-code terms, with arbitrary complex
coefficient columns `a_j,c_j in C^24`, each split into three 8-blocks. Exactness
means

    sum_j a_j c_j^T = I_24.                                      (1)

Equivalently the live all-pairs endpoint is
`I_3 tensor (X X^T)`, because `I_3 tensor X` has a left inverse. Transpose is
ordinary, not conjugate transpose. Terms with a zero factor are discarded.
Coefficients of overcomplete factors must remain in the block-root code.

Term j pays the F2 rank r_j of b between the two **unions**

    union_s phi_s ell(supp(X a_j^s)),
    union_t phi_t ell(supp(X c_j^t)).

The union forgets call identity and is charged only once. No preparation,
source access, conversion, routing, frame change, restoration or extra helper
cost is added to this favorable algebraic relaxation. A physical interpretation
requires the separate-total copy/delivery interface; this is not a universal
information lower bound for interacting circuits.

## 2. Term prices

Write S_j for the calls with `a_j^s != 0`, and T_j for those with
`c_j^t != 0`. They are nonempty. A term is **pure** if `S_j intersect T_j`
is empty; all other terms are **non-pure**. Let p and n count them.

Every non-pure term contains a within-call support-pair block. The chart on
both sides of that block is the same isometry, so the pair lemma gives
`r_j >= 8`.

Every pure term contains a block pairing two subspaces U,W of V of dimensions
at least eight. Nondegeneracy gives

    rank b|(U x W) = dim U - dim(U intersect W^perp)
                   >= dim U + dim W - 9 >= 7.                  (2)

This uses dimensions, not the common-chart pair lemma. Rank-seven cross
terms really exist (PR2294); reasserting a per-term floor of eight would be
incorrect. Enlarging to the union cannot reduce a submatrix rank.

## 3. A three-block triangular deletion lemma

**Lemma.** Suppose the 24-by-24 identity is a sum of n non-pure and p pure
rank-one terms, classified by the three block supports above. Then

    n >= 24 - (2/3)p.                                         (3)

More precisely, if p_11 pure terms touch one reader and one source call,
and p_12 touch three calls, then
`n >= 24 - p_11/2 - 2 p_12/3`.

*Proof.* Put `Q = sum_non-pure a_j c_j^T`. Every pure term P_j has zero
diagonal blocks, so (1) gives `Q = I_24 - sum_pure P_j`.

For any of the six orders pi of the three calls, let L_pi keep only the
strictly lower **blocks** in that order. The matrix

    U_pi = Q - L_pi(Q) = Q + sum_pure L_pi(P_j)

is block upper triangular with identity diagonal blocks. It is invertible,
with rank 24. Subadditivity of rank and `rank Q <= n` imply

    24 <= n + sum_pure rank L_pi(P_j).                         (4)

For a pure term, the disjoint nonempty sets S,T have either sizes (1,1),
(1,2) or (2,1). In each case one side occupies a single block. Consequently
L_pi(P_j) is zero or is still a single outer product: truncation only removes
whole blocks of the *other* factor. Its rank is one exactly when at least
one source call precedes a reader call.

For sizes (1,1) this happens in three of the six orders. For (1,2), the
single reader is earliest among the three calls in two orders, and the
truncation is nonzero in the other four. For (2,1), the single source is
latest in two orders, again giving four nonzero truncations. These counts
do not depend on coefficients, block widths or the chosen charts.

Average (4) over all six orders. This gives
`24 <= n + p_11/2 + 2 p_12/3 <= n + 2p/3`, proving (3). Equivalently,
some single order has at most `floor(2p/3)` nonzero pure truncations. QED.

The coefficient 2/3 is sharp even for exact coefficient identities. On one
coordinate of each call,

    I_3 = 1 1^T - sum_(s=0..2) e_s (1-e_s)^T.

Here 1 is the three-component all-ones vector: there is one non-pure term
and three pure terms, so `n + 2p/3 = 3`. Add the 21 untouched coordinate
terms to obtain an exact 24-dimensional root-code identity with n=22, p=3.
In every call order exactly two pure truncations are nonzero. The verifier's
`sharp_deletion_coupled` fixture checks this attained counting bound. Its
actual copy bill is 201 in the selected charts; it does not attain (5).

## 4. Sharp copy and recursive-power floors

**Theorem.** Under section 1's model, for every choice of the three isometric
charts and every exact root-code factorization,

    sum_j r_j >= 192 + (5/3)p >= 192.                         (5)

The minimum is 192, and equality excludes pure terms.

*Proof.* Sections 2 and 3 give
`sum r_j >= 8n + 7p >= 8(24 - 2p/3) + 7p = 192 + 5p/3`.
For attainment, use the 24 standard coordinate terms
`a=c=e_s tensor e_k`, for s=0,1,2 and k=0,...,7. Each has rank eight
by the within-call pair lemma and isometry, and their outer products sum to
I_24. If p>0, (5) is strict. QED.

**Power-price corollary.** For every real `0 < q <= 1`,

    sum_j r_j^q >= 24 * 8^q
                    + p * (7^q - (2/3)8^q) >= 24 * 8^q.      (6)

The coefficient of p is positive because
`(7/8)^q >= 7/8 > 2/3`. Attainment is the same 24 coordinate terms.
Dividing by any fixed parent width M to the power q gives the same sharp
comparison for the separate-total child bill `sum_j (r_j/M)^q`.
In particular q=1-a is covered for the supplier regime `0 <= a < 1`.

Thus three-call chart sharing in this relaxation cannot reduce either the
64-per-call centre rank or its separate-total recursive power bill. Adding
nonnegative helper, source-access, frame, routing or restoration charges
cannot improve this comparison. Changing the separate-total contract, the
parent width/volume or other local children needs a new accounting argument.
No changed kappa, supplier or physical construction follows from this note.

## 5. Boundary of the proof

For four calls a pure term can have two reader and two source calls. Lower
block truncation can then have rank two, although the untruncated term has
rank one. Averaging over all 24 orders gives mean rank one for the all-ones
2-by-2 support pattern, exceeding 2/3. The verifier records this as a scope
control. It neither supplies a four-call escape nor rules one out.

Non-isometric own-call charts, different reader/source charts, nonidentity
call coupling, outside-code factors, temporal reuse and interacting copied
totals are also outside this theorem. Finite replay checks the geometry,
ordering counts and explicit examples; the quantified conclusion follows
from the written argument, not a finite search or a proof assistant.
