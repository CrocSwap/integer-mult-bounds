# Three directions under one common six-root cut

## Statement and model

Use the fixed P112 configuration of PR3253. Its 120 E8 root lines have
integer representatives of squared norm eight, with first nonzero coordinate
positive. Remove the eight frame lines `2e_0 +/- 2e_1, ..., 2e_6 +/- 2e_7`
and sort the remaining 112 roots lexicographically. For a live root r_t,
its label ell(t) is its simple-root coordinate vector modulo two, with a
leading affine bit one. Thus ell(t) lies in F2^9. The exact simple system,
root ordering and labels are bound by SOURCES.json.

For a binary seven-space V, let Lambda(V) be its live label trace. For
nonzero h in K^8, where K has characteristic zero, let Off(h) be the live
roots with nonzero ordinary bilinear pairing with h.

**Theorem.** For every fixed V and ONE fixed set P of at most six live
roots, there are at most THREE distinct projective directions [h] with

```text
rank_F2 {ell(t): t in Off(h) outside (Lambda(V) union P)} <= 7.
```

Consequently their K-linear span has dimension at most three. This is
sharp. The independent triple at six cuts already belongs to PR3253;
its attainment is predecessor evidence, not a new witness here.

The new assertion is the universal upper bound at six cuts and its literal
caller application. PR3253's common-five upper bound and common-six lower
bound do not establish this upper bound. The theorem concerns one seven-space,
not the separate seven-plus-four-space alpha74 common-two question.

## Complete finite direction domain

The inherited standard real Weyl-chamber theorem is used explicitly. The
new replay reconstructs the 120 roots, their integral simple coordinates,
simple-system positivity and all 960 simple-reflection root images. The
largest rank-at-most-six parabolic subsystem has 36 full root lines. The
eight maximal parabolic root-line counts are

```text
42, 28, 22, 14, 16, 23, 37, 63.
```

These finite facts and the Weyl-chamber theorem imply the classification
argument below; a finite reflection check alone is not a proof of that theorem.

A qualifying residual span extends to another binary seven-space G, so

```text
D(V,h,G) = Off(h) outside (Lambda(V) union Lambda(G)) subset P.
```

Conversely this containment implies the required rank bound. The new direct
and dual censuses recheck the maximum two-trace union, 68. Hence a qualifying
h has at most 68+6=74 live off-roots, and at least 112-74=38 live zero roots.
Rank at most six cannot contain that many zero roots. Among the maximal
parabolics only the 42- and 63-root types can contain 38 zero roots; the
37-root type still cannot. Their projective Weyl orbits contain 1080 and
120 directions. Thus the SAME 1200-direction superset used in PR3253 remains
complete at six cuts. This explicit 38>37 check is the changed completeness
obligation. The live support histogram is

```text
support size       53   56   70   73   76
directions        112    8  128  896   56
```

The support-76 directions are harmless extra candidates and fail the coverage
budget. No new direction alphabet is inferred by silently raising a cut limit.

For arbitrary characteristic-zero K, fix the zero pattern of h. Its rational
zero-equation matrix has a rational kernel N. Every declared nonzero pairing
is a proper rational hyperplane in N, because h avoids it after scalar
extension to K. Over Q, finitely many proper hyperplanes cannot cover N.
Choose a rational vector with exactly the same zero pattern. The real argument
forces its zero roots to have rank seven. Thus N has dimension one, and its
scalar extension to K is one of the enumerated rational projective lines.
This covers every K-direction without ordering K or using finite-field tests.

## Complete first-flat and completion domains

Every binary seven-space is the kernel of a two-dimensional annihilator.
Its three nonzero functionals are a,b,a^b. Pairs `a<b<a^b` enumerate exactly
43,435 spaces, with 43,181 distinct live traces. The eight frame-preserving
signed permutations retained from PR3253 preserve roots and the full trace
inventory. Exact orbit closure gives 121 trace classes. Both implementations
recheck that quotient; all second spaces G remain in the census.

For each representative V and all 1200 directions h, the primary C++ scan
checks all 43,435 second spaces G, skipping only directions whose support
exceeds that representative's maximum two-trace union plus six. It emits
EXACTLY the records with |D(V,h,G)|<=6. Python checks every emitted mask,
index, uniqueness and predicate. RESULT.json retains all 230 completion
records, versus PR3253's 148 records at five cuts. There are at most eighteen
records in any first-flat class.

The separate implementation reconstructs roots from lattice conditions,
labels by rational elimination, and all annihilators in reduced row-echelon
form. For a residual root set outside V it first finds functionals whose
violations have size at most six. Every successful annihilator pair uses two
such functionals. It then checks every pair's violation union and recovers
exactly the same 230 records. This uses attributed predecessor reconstruction
libraries and a new six-cut dual scan, not an independent human/model audit.

## One common cut, and the sharp upper bound

For each first-flat class, generate unions of the recorded completion cuts,
retaining only unions of size at most six. At most 41 union states occur in
a class. For each union, count distinct direction indices with at least one
completion cut contained in it. The maximum is THREE.

This finite check proves the arbitrary-common-P statement. If four distinct
directions qualified for some P, choose a completion G for each. The union
of their four recorded cuts would be a generated state contained in P,
qualifying all four directions, contradicting the exact count. Extra roots
in P do not need to be generated or enumerated.

The separate checker instead checks every four-record choice with distinct
directions, 14,640 choices in total. Every union has more than six roots.
It also finds a compatible triple. This argument does not use the primary
union-state routine. SUMMARY.json and REFERENCE.json retain both receipts.

For sharpness, the unchanged PR3253 witness uses annihilator `(60,65)` for V,
common cut `{24,34,35,100,101,110}`, and directions

```text
(0,2,0,-2,0,0,0,0)
(0,2,0, 2,0,0,0,0)
(2,0,-2,0,0,0,0,0).
```

Their Gram matrix is 8 I_3, determinant 512. All three residual ranks are
seven. Both new commands recheck this literal predecessor witness.

## Literal historical caller 2^3,7^7

Assume the inherited P112 root-evaluation code C in K^112 has minimum
nonzero support 53. Assume its binary-rank support capacities two and
thirty-six at ranks two and seven. These are mathematical premises, retained
from PR3289, not new capacity or distance proofs.

Suppose ten independent pieces q_0,...,q_9 have rank bounds
`2,2,2,7,7,7,7,7,7,7`, and their span T meets C in dimension at least six.
The quotient T/(T intersect C) has dimension at most four. Choose
X={q_0,q_1,q_2,q_3}, with q_3 as the rank-seven anchor. Its union support
has size at most 2+2+2+36=42<53. A nonzero combination of X is nonzero by
piece independence and cannot be a codeword below the code distance.
Thus the four quotient images are independent, form a quotient basis,
and force dim(T intersect C)=6.

For each i=4,...,9, write its unique quotient relation as

```text
c_i = q_i - lambda_i q_3 - a_i in C,
a_i in span(q_0,q_1,q_2).
```

These six codewords are independent by their distinct q_i coefficients.
Root evaluation is injective, so their directions h_i are independent.
Let V extend the anchor's binary support span to dimension seven. Let P be
ONE actual support union of q_0,q_1,q_2, of size at most six. Outside
Lambda(V) union P, c_i agrees with q_i, so its residual binary rank is at
most seven. The new theorem permits at most three projective directions,
in contradiction to the six independent h_i. The literal caller is excluded,
conditional on the stated code/capacity premises.

This is a named caller result, not a recomputed total public survivor count.
No actual support-union minimum or coefficient realization is claimed.

## Limits and stopping decision

The standard real Weyl-chamber theorem and the caller's distance/capacities
are explicit inherited mathematical premises. Exact rational field transfer
and the quotient argument are written proofs, not proof-kernel checks.
The finite direction, flat, completion and common-cut domains are replayed.
Historical unrelated capacity/caller suites, Lean, Docker, selected cold
replay, human review and full multiplication verification are unrun.

This closes one specified implication and caller gap. Stop this session here;
no larger cut census or dependent construction round is authorized by the
finding. Full C5, physical access, restoration, paid consumers, all-size
supplier admission, selected science and kappa remain outside scope.
