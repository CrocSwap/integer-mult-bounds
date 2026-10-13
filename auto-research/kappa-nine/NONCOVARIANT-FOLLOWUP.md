# Dimension-15 follow-up: an open search and a scoped exclusion

This follows the proposed experiment in `next-experiment-spec.json`.
**No new finite network or multiplication exponent is established.** The
unrestricted rational dimension-15 problem remains open. Earlier receipts
and the selected multiplication witness are unchanged.

## Unrestricted formulation and bounded run

For each of the 84 triples T of nine points, use matrices A_T of size
15 by 2 and B_T of size 2 by 15, with

    B_T A_T = I_2,
    B_T A_U = B_U A_T = 0 when |T intersect U| = 1.

Then P_T=A_T B_T is a rank-two idempotent satisfying the requested
annihilation identities. Conversely every requested rational projector
family has such factors: choose a rational basis for each image and use
its coordinate map after projection. The cross conditions are equivalent
to projector annihilation, by multiplication by the corresponding left
and right inverses.

Seven fixed Fano labels can be simultaneously put in seven disjoint
coordinate planes. Only this legitimate global change of basis is imposed.
Neighbors of those labels have zero factor coordinates in the appropriate
planes. No additional local pivot, symmetry, form, positivity or additive
assumption is made.

The resulting system has **2,436 real unknowns and 13,076 nontrivial
quadratic equations**, compared with 4,893 entries in the projector
formulation. A Z3 5.1.0 real-arithmetic run requested a 30-second timeout
and returned UNKNOWN/timeout after approximately 52 seconds of solver
work. This is neither an existence nor an impossibility certificate. A
real model would still need rational reconstruction and exact replay.

`noncovariant-search.json` records that run. The standalone rational checker
verifies every normalization and both directions of every one of the
1,890 unordered edge constraints. The dimension-16 doubled scalar control
passes, including an exact change of basis to the actual Fano gauge and
the resulting support constraints. Corrupted normalization and edge
examples fail. Thus the positive control tests the gauge used by the
search, not just an unrelated ungauged representation.

## A smaller exact test: sharing a scalar coordinate

There is a natural intermediate departure from full permutation symmetry:
distinguish the ninth point, retain S8 covariance on the others, and use
two copies of the standard seven-dimensional S8 representation plus one
trivial line. This has dimension 15; two separate trivial lines would give
the familiar dimension-16 representation.

**The dimension-15 shared-line construction cannot work.** More generally,
rank-two covariant labels on all triples of eight points are impossible in

    V = standard_7^k + trivial^r,    7k+r <= 15.

The projectors themselves may be nonsymmetric. This statement does not
cover other S8 representations, sign-twisted mixtures, or noncovariant
labels.

Fix a triple T. Its S3 x S5 stabilizer decomposes each standard seven-space
into the inside standard space (dimension 2), the outside standard space
(dimension 4), and one invariant line. These are pairwise nonisomorphic
irreducible rational representations, so a commuting projector has blocks

    I_2 tensor E, I_4 tensor F, R,

where E,F,R are idempotents on the respective multiplicity spaces. Its
rank is 2 rank(E)+4 rank(F)+rank(R). Rank two permits exactly two cases.

1. rank(E)=1, F=R=0. For adjacent triples the product of the inside
   standard projections has rank one, and E^2=E is nonzero. Their tensor
   product cannot vanish.
2. E=F=0 and rank(R)=2. Write w_T=1_T-(3/8)1. Its squared norm is 15/8
   and w_T dot w_U=-1/8 at intersection one. The normalized cross map
   between the invariant multiplicity spaces is therefore

       D = diag((-1/15) I_k, I_r).

   Annihilation requires R D R=0. For k<=1, use
   RDR=R+(-16/15)RER, where E has rank k: this would force rank(R)<=k.
   For k=2 the dimension budget gives r<=1. D is invertible on a space
   of dimension at most three, while RDR=0 would place the two-dimensional
   image of DR inside the at-most-one-dimensional kernel of R.

Both cases contradict rank two. The stabilizer commutant dimensions are
also checked independently from integer commutation equations: for k=2,
r=1 the dimension is 17, matching 2k^2+(k+r)^2. A modular rank lower bound
for those equations supplies the upper bound on the rational commutant;
the displayed block decomposition supplies the matching lower bound.

The exclusion is sharp within this family on eight points: with k=2,r=2,
take A=[I_2;I_2], B=[(15/16)I_2,(1/16)I_2], and R=AB. Then BA=I_2 and
RDR=0. The checker verifies this control exactly. This is a geometry
control, not a complete network.

## What this changes

Saving the one dimension by sharing the old scalar coordinate fails even
after relaxing full S9 covariance to this particular S8 action. This is
consistent with the earlier one-sided point-additive obstruction; it is
not evidence against arbitrary rank-two labels.

The unrestricted run is too large for an undirected increase in solver
time to be a compelling next investment. The useful next task is to find
local eliminations or exact kernel patterns in this same unrestricted
factor system, with the dimension-16 control retained. Any fixed kernel
catalogue must be documented as an additional search restriction. A
negative result for that catalogue would not close dimension 15.

Even a successful nine-point geometry would still need extension to the
target ground size, a charged side circuit, mixed-width transfer and a
compatible complex network. The optimistic target budget is not a new
exponent witness.

## Reproduction

    python3 research/kappa-nine/noncovariant_search.py --timeout-ms 30000 --output /tmp/noncovariant-search.json
    python3 research/kappa-nine/shared_scalar_screen.py --output /tmp/shared-scalar-screen.json
    python3 -m unittest discover -s research/kappa-nine -p test_noncovariant.py -v

The search needs Z3; the exact controls and proof checks use the Python
standard library. Four focused tests pass. Solver timing and its precise
timeout point are environment-dependent.
