# Four thin queries are necessary for the natural four-arm supports

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
The four-arm vectors in the companion construction analysis extend DreamingOfClouds's sign-Gram geometry in
CrocSwap/integer-mult-bounds#6833, head
`ad24ad966b857dbfed50d9121624db84b2eccc92`. The proof is self-contained.
**No new κ.**

## Claim and conventions

Work over Q, on coordinates A,B and disjoint private arms L0,R0,L1,R1,
with lengths a,b,c,d, chronological order as listed, and increasing indices
within each arm. Assume a>=1,b>=2,c>=2,d>=1. Arbitrary additional spectator
coordinates are allowed; native vectors have zero spectator entries.

For a central involution S the native query is T_i=I+(S-1)x_i y_i^T,
with y_i^T x_i=0. The full native factor is
`(I+(D_i-1)P_i)T_i`, with independent stage scalars D_i. Arbitrary thin
factors may occur between full sites, before the first, or after the last.
At S=-1 each thin is invertible and differs from I by rank at most one;
it carries no D_i. All query factors equal I at S=1.

Assume the query-only endpoint is S I and require the all-column endpoint
`S product_i(I+(D_i-1)P_i)`. Matrices act on columns; chronological
T_1,...,T_m multiply as T_m...T_1.

**Theorem.** With the native vectors and coordinate projectors below,
at least four thin factors are necessary, regardless of their vectors
or placement. This rules out the three-thin (4,4,5,5) design with these
supports. It does not rule out five-thin designs with extra spectators,
which can supply additional productive targets and change the invoice.

## Native data

Write H=span(A,B). The arm hub pairs (u,v^T) are

| Arm | u | v^T |
| --- | --- | --- |
| L0 | A | A*-B* |
| R0 | B | A*-B* |
| L1 | B | A*+B* |
| R1 | -A | A*+B* |

A left-arm site with private f coordinates is

    x_i=u+f_i+2 sum_(j<i)f_j,
    y_i^T=v^T-f_i*,
    P_i=projector onto H+span(f_0,...,f_i).

A right-arm site with private h coordinates is

    x_i=u+h_i+2 sum_(j>i)h_j,
    y_i^T=v^T+h_i*,
    P_i=projector onto H+span(h_i,...,h_(g-1)).

Every P_i fixes x_i and y_i^T on its respective side, so it commutes
with T_i. Native pairings give y_i^T x_j=sgn(i-j). Inserted thins need
not preserve that Gram pattern. At S=-1 each native is I-2x_i y_i^T.

## Why stage commutation is necessary

Let C_i be the query prefix through native i and U_i the strict suffix.
At S=-1, U_i C_i=-I. Set all D except D_i to one. The actual coefficient
of D_i-1 is `U_i P_i C_i=-U_i P_i U_i^-1`; the required coefficient is
-P_i. Thus P_i commutes with U_i and C_i. It also commutes with the
inclusive suffix U_i T_i because it commutes with T_i itself.

This is a necessary all-column identity, not merely a preferred extraction
method. If Q(1)=I, an S-independent transported projector Q(S)^-1 P Q(S)
must equal P by evaluation at S=1, so transport cannot repair a fixed P
for free. A fixed simultaneous change of basis preserves the argument.

## Rank perturbation lemma

Inserting k factors I+R_j with rank(R_j)<=1 into any ordered product Q
produces Q' with rank(Q'-Q)<=k. Insert one at a time: replacing AB by
A(I+R)B changes it by ARB, of rank at most one; then use subadditivity.
Consequently, if P Q'(I-P)=0, then

    rank(P Q(I-P)) <= rank(Q'-Q) <= k.

Thus a native-only cross block of rank two needs at least two thins on
that side of the cut. This permits arbitrary inserted vectors.

## Cut 1: last R0 stage

Here P projects onto H+span(h_(b-1)). Delete thins from the prefix to get
Q_0, the L0-then-R0 native product. Rows A,B and columns L0:f_0,
R0:h_(b-2) in P Q_0(I-P) give the minor

    [[2(-1)^(a-1), 0],
     [     *,       2]],

whose determinant is 4(-1)^(a-1), nonzero. Both columns lie outside P.

For the first column, input f_0 gives hub 2A at the first L0 query;
each remaining L0 query flips A. Later private inputs are zero because
left queries alter only current and earlier private coordinates. R0
changes only hub B, leaving A=2(-1)^(a-1). For the second column, input
h_(b-2) is untouched until the penultimate R0 query, which gives hub -2B
and last-private value -4. The last covector reads 2-4=-2 and adds 4B,
leaving hub 2B and zero A.

The actual prefix commutes with P, so at least two thins occur before
this R0 stage completes. Central-gap thins later cannot repair it.

## Cut 2: first L1 stage

Now P projects onto H+span(f_0) in L1. It must commute with the inclusive
suffix. Delete its thins to obtain Q_1, the L1-then-R1 native product.
Rows A,B and columns L1:f_1,R1:h_(d-1) give the minor

    [[    *,      2],
     [2(-1)^c,    0]],

with determinant -4(-1)^c. Both columns are outside P. Input f_1 gives
2B at the second L1 query; later L1 queries flip it to 2(-1)^(c-2)B.
R1 changes only A. Input last-R1 h is untouched until the last query,
which contributes -2(-A)=2A and no B component.

At least two thins therefore occur after the first L1 stage begins.
These two cut-side thin sets are disjoint. Thins in their central gap
belong to neither. At least four thins are necessary in total.

## Scope, evidence and next question

The proof covers every a,d>=1 and b,c>=2 and arbitrarily many spectators.
It counts thin rank-one operations, not net paid cost after target credit.
Different supports or native vectors, dependent stage scalars, other
targets, or higher-rank operations are outside the theorem. A free
S-dependent basis change is not allowed. The independent hub image/dual
merge obstruction is not a premise here.

The verifier checks direct integer products and exact rational ranks,
the minors for length pairs in 1..8, the full (4,4,5,5) embedding with
and without spectators, and all 1,330 unordered three-thin gap placements
for its 18 native sites. Controls expose the critical length, support,
rank-one and scalar-endpoint hypotheses. The all-width lower bound is
the written proof, not a failed finite completion search.

A useful next step is a different support family or an explicitly
completed spectator extension with full stage identities and accounting.
Scientific base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Contributed by @CubeJerry with coordinated OpenAI research assistance.
Independent human and formal proof-kernel acceptance are unclaimed.
