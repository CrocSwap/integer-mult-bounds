# Independent audit of the two-negative plane case

Audit date: 2026-10-11.

The audited files have these SHA-256 hashes:

```text
3e5569f04561ba3c71b3bbc554ce4ce8c063aa3c1f3cdb83370342d3ee45c529  TWO-NEGATIVE-PROOF.md
0283b675f73e874c846909130998a97609e037163e0088a6f563d745425a2919  THEOREM.md
```

## Result

No proof gap was found in the two-negative case or in its use in the
theorem on exactly three complete roles. The direct proof excludes five
queries with two negative ADDRESS determinants. This theorem requires at
least six queries. Six coordinate reflection queries attain the endpoint.

## Checks

The audit checked each reduction in TWO-NEGATIVE-PROOF.md. It also read
PROOF.md, POSITIVE-FIVE-PROOF.md, the determinant lemma in
../native-research/PROOF.md, search.py, and independent-audit/check.py.

The whole-word determinant relation is needed in the no-target-pair
case. Together with the triple relation, it gives det(A)det(B)=1 and
det(C)=1. The two normal forms then have zero or four negative queries.
They cannot have two.

A two-query target has opposite reflections R and zR. The sign quotient
forces their DATA projectors to be equal. The determinant magnitude
quotient, full span, and coloop conditions then force all three positive
ADDRESS maps to be nonidentity unipotents.

The target extrema force the positive triple to have ordered product z.
A full five-query target would make its middle positive block conjugate
to its negative. Each possible block has trace 2 or -2. This excludes
the full target.

A four-query target forces R U R=V^-1 for two distinct positive maps.
This relation also gives R V R=U^-1. A second positive pair would share
one map with the first and force two positive maps to be equal. Thus
there is at most one four-query target.

The only possible targets are the negative pair S, its positive
complement T, and one four-subset F. If F omits positive index c, three
distinct target minima require c=1. Three distinct target maxima require
c=5. The contradiction is valid. No finite search or ADDRESS conjugacy
classification is needed for this conclusion.

The finite verification section also covers both orders of the selected
positive pair. Conjugation by K=[0 1; -1 0] exchanges A and B, sends C
to z B^-1 A^-1, and exchanges J and -J. The literal search maps are a
common rational conjugate of that set. The source loops cover all 120
map orders and all 28^3 positive DATA projector choices before the
stated necessary span and coloop filters.

This audit did not run either finite checker again. The checkers are
verification evidence for a direct proof, not dependencies of the proof.

## Scope and caveats

The model is Mat_3(F2[G]) with exact formal group-algebra equality. Each
query uses a nonzero binary rank-one idempotent DATA projector and a
nonidentity rational invertible plane ADDRESS map g with rank(g-I2)=1.
The endpoint is z I3, where z=-I2, on three complete arbitrary-input
DATA roles. The all-size native contract is an assumption of the theorem.
This audit does not re-establish that contract from the upstream compiler.

Idempotence is necessary for the determinant-product reductions used
here. A rank-one square-zero DATA matrix does not satisfy this hypothesis.
The theorem must not be extended to that model without a new argument.

This audit does not prove a helper extension, an integer-multiplication
lower bound, a general eight-query three-coordinate lower bound, or a
kappa gain. It makes no global novelty claim. No upstream file was
changed. AI assistance was used in the proof review.

The final helper extension in THEOREM.md is outside this audit. That
extension has its own audit in independent-audit/HELPER-AUDIT.md.
