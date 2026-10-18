# Fixed positive C5 restriction charging has a small certificate ceiling

## Model and result

Use the 56 complete binary planes from PR2782's retained physical matching.
Each plane has two associated scalar coordinates. Each scalar coordinate
carries that entire two-dimensional plane, rather than only its label line.
There are 112 scalar coordinates in total.

A strict scalar fit over a characteristic-zero field is a finite sum
`K = sum_t u_t v_t^T`, with ordinary transpose, diagonal one and zero at
distinct coordinates whose complete planes are not orthogonal. Other
off-diagonal entries are free. For scalar supports A and B, let

`r(A,B) = rank_F2(<E(A), E(B)>)`,

where E(A) is the sum of all complete planes touched by A. This is a binary
pairing rank. It is not the characteristic-zero scalar rank of K.

Let C range over the 23 induced C5s in the orthogonality graph of these planes.
Each C has ten scalar coordinates. Write
`r_C(A,B) = r(A intersect C, B intersect C)` for the restricted tariff.
Grant every local theorem `sum_t r_C(A_t,B_t) >= 20`. The local theorems are
predecessor results, not reproved or needed as assumptions for the ceiling
calculation below.

A **direct restriction certificate** chooses fixed real weights lambda_C >= 0
and proves the universal termwise domination

`sum_C lambda_C r_C(A,B) <= r(A,B)` for every scalar support pair A,B.

Summing over a fit would then yield the raw linear lower bound
`sum_t r(A_t,B_t) >= 20 sum_C lambda_C`.

**Theorem.** Every certificate of this precisely defined form has
`20 sum_C lambda_C <= 180/7 < 26`. The same necessary ceiling applies if
domination is demanded only for terms that can occur in some exact strict fit.
No claim is made that the ceiling is attainable. Final rounding to an integer
cost could yield at most 26. In particular, these certificates cannot establish
a global cost 64 or cost 224 floor by aggregation alone.

## One admissible term gives the obstruction

Take u=v=1 on all 112 scalar coordinates, so the term is J=11^T. It touches
every complete plane. Its actual global binary pairing rank is 9. Its
restrictions to the 23 C5s have ranks

`7 on four cycles; 8 on six cycles; 9 on thirteen cycles`.

RESULT.json records each physical cycle and its exact rank. Packed binary
elimination and a separate dense implementation recover this entire vector.
The two implementations independently enumerate the 23 chordless cycles.
In particular, every local rank is at least 7.

Apply universal domination to this term. Nonnegativity gives

`7 sum_C lambda_C <= sum_C lambda_C r_C(full,full) <= 9`.

Multiplication by 20/7 proves the theorem. More generally, one test term with
global cost R and positive local costs r_C imposes the necessary ceiling
`R max_C(b_C/r_C)` on any weighted certificate using granted local bounds b_C.
This is an upper bound on a proof method's possible lower-bound objective.
It is neither an upper bound nor a lower bound on the true decoder optimum.

The unweighted sum already fails termwise on J: it charges 193 locally against
9 globally. Merely using fewer of the 23 cycles or repeating their inequalities
does not escape the theorem. Such choices are nonnegative weight vectors too.

## The full-support term occurs in exact fits

For n=112, an explicit rational asymmetric decomposition is

`I_n = J - sum_{i != j} e_i e_j^T`.

It consists of 12,433 nonzero rank-one scalar terms, including J. Every matrix
entry is checked, so it fits even all off-diagonal entries, including the ones
the strict mask leaves free. No decoder-cost improvement is asserted.

There is also a signed Gram extension, checked separately:

`I_n = J - sum_{i<j}(e_i+e_j)(e_i+e_j)^T + (n-1) sum_i e_i e_i^T`.

The off-diagonal entries cancel once. Each diagonal equals
`1 - (n-1) + (n-1) = 1`. Thus restricting attention to individual terms
extendible to exact strict fits cannot discard the test term. These formulas
do not make universal termwise domination necessary for every conceivable
decoder-level charging argument. Coefficient cancellations may support a
different global argument that fails on individual terms.

## Limits and research decision

This closes only the direct fixed-nonnegative-weight restriction implication
suggested by the local C5 handoff. It grants all local 20 floors, so it remains
a valid ceiling even if the current provisional proofs are strengthened or
replaced by other proofs of those same inequalities.

It does not exclude signed combinations, stronger local inequalities carrying
coefficient information, decoder-level cancellation identities, extra global
constraints, other physical matchings or a different tariff. Nor does it
produce any cheap strict fit. A global proof must use information beyond this
fixed positive aggregation. No native execution, physical routing, dirty-state
restoration, precision, consumer, supplier or kappa claim follows.

The bounded family decision is to stop this particular aggregation route.
The next justified test is one explicit global, coefficient-sensitive
inequality that remains valid on an entire completed strict fit even when it
fails on J alone. The complete consumer and physical bill remain unknown.

## Sources and credit

Canonical geometry is retained from Tekalign/PR2782 and Cinna Davis/PR1825,
with Adam Gall/PR1889's strict mask and the E8/P112 lineage. The immediate
global-charging handoff is Krzysztof Wojt/PR3281 at
`a3a7306c15c7da541e4b586fdb642e2855fc2956`, alongside Nick Petalas/PR3279 at
`67c1360a7a6e81bcac515c698d56656454340b10`. Those local proofs, thakrarsagar's
PR3256/3232 and PR3268 are credited rather than imported as executable or
Git-object dependencies. Arham Tahir/PR2879, Sagar Thakrar/PR2484, ctoth,
Philippe Van Velzen and the retained supplier/geometry sources retain credit.
Apache-2.0.
