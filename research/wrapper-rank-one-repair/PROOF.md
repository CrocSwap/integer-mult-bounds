# Exact rank-one repair of the weighted ordinary wrapper

This scoped written proof was produced by Nick Petalas.

Let V be a positive finite-dimensional vector space over any field F. Fix
P in GL(V). A second map Q in GL(V) may be chosen freely. Keep the six
chronological instructions of Jerry Chen / CubeJerry's PR2950:

```text
D -= H
F_P(H,D) = (P D, P^-1 H)
D += H
F_Q(H,D) = (Q D, Q^-1 H)
D = -D
D += H
```

The required endpoint is J(H,D)=(D,H). In addition, allow any finite
workspace U with arbitrary initial contents. Every original instruction fixes
U. The required full endpoint is J direct-sum I_U.

An added correction is an invertible linear map S on V direct-sum V
direct-sum U with rank(S-I)=1. Every added correction costs one. Corrections
may mix the banks and workspace, need not commute, and may be inserted at any
cut between the six original instructions, including the two end cuts. There
are no other free operations. In particular, arbitrary basis changes are not
free instructions. Choosing a different Q is permitted without an added
correction charge, as in PR2950's second-callee comparison.

## Theorem

The minimum number of added corrections, over every Q, every finite U and
every placement of the corrections, is

```text
r = rank(P^2-I).
```

An attaining word chooses Q=P and U=0. All its corrections are cross-bank
shears inserted immediately after the ordinary middle D += H. Thus the
optimum is unchanged if the correction alphabet is narrowed to these
cross-bank shears. The unit here is one arbitrary rank-one linear correction,
not a native call, scalar ADD or physical tape operation.

## Lower bound with arbitrary dirty workspace and arbitrary cuts

Write W_(P,Q) for the unchanged six-instruction endpoint. PR2950 proves

```text
rank(W_(P,Q)-J) >= rank(P^2-I),
```

with equality at Q=P. This is a cited predecessor result, not a new claim.
For a self-contained identification of the inherited quantity, its first
error coordinate restricted to D=0 is Q(P^-1-P)H. Its rank is r because
Q(P^-1-P)=-Q P^-1(P^2-I), with invertible outside factors. Projection and
restriction cannot increase rank.

Consider a proposed word with k corrections. Remove one correction S while
leaving every other instruction fixed. If the products before and after that
cut are R and L, the endpoint changes by L(S-I)R, of rank at most one. Remove
the k corrections in any order and telescope their endpoint differences.
Rank subadditivity gives

```text
rank(corrected endpoint - (W_(P,Q) direct-sum I_U)) <= k.
```

If the corrected endpoint is J direct-sum I_U, the left side equals
rank(W_(P,Q)-J), since a zero workspace block does not change rank. Therefore
k>=r. The argument retains every dirty workspace input and its required
identity output. It does not project away or initialize that workspace.

## Attaining construction

Set C=P^-2-I. Multiplication by the invertible P^-2 gives

```text
C = -P^-2(P^2-I),    rank(C)=r.
```

Take a rank factorization C=sum_(i=1)^r u_i phi_i, where u_i is a nonzero
column of V and phi_i is a nonzero linear functional on V. Such a
factorization exists over every field by choosing a basis of the image.
Insert the following r corrections after the middle addition:

```text
S_i(H,D) = (H, D+u_i phi_i(H)).
```

Each S_i is invertible, with inverse obtained by subtraction. Each S_i-I has
rank one. These particular corrections commute, so the effective middle
instruction is D += (I+C)H = P^-2 H.

Writing the input as (h,d), the successive pairs are

```text
(h, d-h)
(P(d-h), P^-1 h)
(P(d-h), P^-1 h+P^-2 P(d-h)) = (P(d-h), P^-1 d)
(d, d-h)
(d, h-d)
(d, h).
```

The second callee is F_P. This proves exact interchange, including
characteristic two, with precisely r added corrections and no workspace.
If r=0, the empty correction list is allowed. The lower bound proves
optimality even against the larger alphabet and arbitrary dirty workspace.

## Scope and credit

The new step converts the inherited error-rank obstruction into an exact
repair tariff for a changed instruction alphabet. PR2950 already proves the
fixed-word obstruction and its optimal second-map value. Its censuses are
not replayed. Nick Petalas's PR4850 minimizes output-coordinate rescalings;
PR5228 classifies optimal second callees while the word remains fixed. Neither
is the inserted-correction model here. The recent PR6406 counts regular J3
second callees and its follow-up questions are not pursued.

Credit Jerry Chen / CubeJerry for PR2950, Nick Petalas for PR2808 and PR2786,
David Arias for PR2753, Jose Manuel / jmbarrancoml for PR2697 and PR2899,
and the retained caller lineage. Rank subadditivity, telescoping products and
matrix rank factorization are classical. No general literature priority is
claimed for those ingredients.

The theorem is algebraic. A rank-one correction may require expensive
functional evaluation, broadcast, coefficient preparation, movement, frames
or restoration in an actual caller. None is priced here. The result is not a
physical supplier, new kappa or complete multiplication theorem. Independent
human and formal proof-kernel review are unclaimed. Apache-2.0.
