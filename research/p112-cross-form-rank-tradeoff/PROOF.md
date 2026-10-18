# A Schur price for arbitrary two-call P112 cross forms

This is a scoped written proof, with rechecked finite P112 premises. Only the
integer-count implication in section 4 is formalized in Lean. No physical
supplier or multiplication theorem is claimed.

## 1. Model and inherited premises

Use Sagar Thakrar's PR2294 section 4 model, based on alephnan's PR1714:
two independent P112 calls, root-code factors, any finite number of terms,
ordinary transpose over the complex numbers, and separate-total union rank
prices. Let X be the fixed 112-by-8 P112 root matrix. Since X^T X=56 I,
exactness is equivalent to

    sum_j a_j c_j^T = I_16,     a_j,c_j in C^8 direct-sum C^8.

Delete terms with a zero factor. A factor block x has support supp(Xx).
Reader labels and source labels use dual binary coordinates; their within-call
pairing is the ordinary dot product. This is a change of coordinates from the
nondegenerate form b in PR2294, not a changed within-call pairing.

The independently checked finite premises are:

* Each nonzero root-code support spans the full binary space of dimension 9
  or one of eight coordinate-support hyperplanes, on both sides.
* Every ordered pair of nonzero within-call support spans pairs at rank at
  least 8. Coordinate support pairs all have rank exactly 8.

For completeness, the support implication follows from the finite census:
for each of the 511 nonzero binary functionals, collect the roots on which
it evaluates to one. Their rational span has rank 8 in 503 cases, and rank 7
in eight cases with distinct coordinate-line kernels. If a functional kills
the labels of supp(Xx), these collected roots are orthogonal to x. Thus only
one of those eight kernels can occur for nonzero x. Two distinct annihilating
functionals would force x into two distinct coordinate lines, which intersect
only at zero. This proves the span classification over C as well, since
rational matrix rank is unchanged by extension to C. The 64 hyperplane-pair
ranks, plus monotonicity when either span is full, prove the second premise.

Put arbitrary independent binary forms beta01 and beta10 between the two
call summands. They need not be transposes and need not arise from a single
nine-dimensional label table. Within-call pairings are unchanged. Price each
term by the rank over F2 of the union pairing matrix on its actual reader
and source support spans. This is the 18-dimensional direct-sum model of
PR2294, not the single-table rank-nine model of PR2338.

Write r01,r10 for the global ranks of the two forms. Write c01,c10 for
their minimum ranks over the 64 ordered coordinate-support hyperplane pairs.
Monotonicity shows these are lower bounds for all nonzero root-code support
pairs. Restriction loses at most one rank per side, so

    c01 >= max(0,r01-2),   c10 >= max(0,r10-2).

All these ranks are binary ranks, unlike the complex ranks in section 3.

## 2. The double-term price

Call a term *pure 01* if only a^0 and c^1 are nonzero, and *pure 10*
for the reverse direction. All other terms are *non-pure*. A non-pure
term is *double* if all four blocks are nonzero.

Every non-pure term costs at least 8. A double term costs at least

    16 - k,     k = min(8,r01,r10).                            (1)

Proof: in each diagonal within-call block choose a nonsingular 8-by-8
minor; these choices independently select rows and columns in each call.
The resulting 16-by-16 submatrix is [A B; C D], with A and D invertible.
Over F2, block elimination gives

    rank [A B; C D] = 8 + rank(D - C A^-1 B)
                   >= 16 - rank(C A^-1 B)
                   >= 16 - min(rank B,rank C)
                   >= 16 - min(r01,r10).

The retained within-call minor also gives rank at least 8. Combining them
gives (1). No symmetry of B or C is used. This improves PR2294's general
double-term bound max(8,16-rho01-rho10) using the smaller of the two ranks.
The independently exhaustive 2-by-2 analogue checks all 9,216 choices with
invertible diagonal blocks, with equality achieved for each cross-rank pair.
That census is a control for, not a proof of, the arbitrary-size argument.

## 3. Complex coefficient counts

Let n be the number of non-pure terms, d the number of double terms,
and p01,p10 the pure counts. Each identity diagonal block has rank 8 over
C, so at least eight terms must have both factors nonzero in that call.
Counting across calls gives

    n+d >= 16.                                               (2)

Let R01 and R10 be the sums of the pure coefficient outer products in
the two directions. Define t01=rank_C R01, t10=rank_C R10 and
mu=min(t01,t10). Then t01<=p01 and t10<=p10. The non-pure terms sum to

    [I_8  -R01; -R10  I_8].

The complex Schur complement implies this matrix has rank at least
16-mu. A sum of n rank-one matrices has rank at most n. Therefore

    n+mu >= 16.                                              (3)

This is PR2294's count argument, retained with credit. It concerns the
aggregate pure coefficient matrices, not binary form ranks.

## 4. The strengthened sufficient condition

**Theorem.** If c01+c10 >= k=min(8,r01,r10), every exact factorization
in section 1 has COPY cost at least 128. The minimum is exactly 128.

The total charge is at least

    8n + (8-k)d + c01*p01 + c10*p10
      >= 8n + (8-k)d + (c01+c10)mu
      >= 8n + (8-k)d + k*mu.                                 (4)

If n>=16, (4) is at least 128. Otherwise let delta=16-n. Equations
(2) and (3) give d>=delta and mu>=delta. Since 0<=k<=8,

    8n+(8-k)d+k*mu >= 8n+(8-k)delta+k*delta = 128.

The usual eight coordinate terms per call give I_16 and cost 16*8=128,
independently of the cross forms, proving sharpness.

`P112CrossForm.floor_of_counts` in `CountFloor.lean` formalizes exactly
the natural-number implication from 0<=k<=8, (2), (3), and (4) to the
floor. `rank_four_floor` specializes it to k=4. `floor_of_term_prices`
also proves the passage from separately charged pure directions in (4),
assuming their counts each dominate mu and their price sum dominates k.
The binary matrix bound,
complex rank argument, support census interpretation, and initial
per-term bill in (4) are **not** formalized in that file. Its counterexamples demonstrate
that omitting the incidence count, Schur count, pure surcharge or rank-eight
within-call charge invalidates the corresponding weakened claim.

## 5. Rank-only corollary and boundary

A sufficient condition depending only on global ranks is

    max(0,r01-2)+max(0,r10-2) >= min(8,r01,r10).                (5)

In particular (5) holds whenever max(r01,r10)>=4 or either rank is zero.
For the first assertion, assume r01>=r10. If r10<=2, r01-2>=2>=r10;
if r10>=2, r01+r10-4>=r10. Both bounds dominate min(8,r01,r10).

Among the 100 ordered rank pairs in {0,...,9}^2, condition (5) certifies
93. The seven not decided by this rank-only test are exactly

    (1,1), (1,2), (2,1), (2,2), (2,3), (3,2), (3,3).

PR2294's global rank-sum-at-least-12 corollary covers 28 pairs; its
zero-form result and form-specific condition provide additional coverage.
Our comparison is with that specific rank-only corollary, not a claim
that every one of the other 65 pairs was previously unresolved.

The rank-(4,4) forms in RESULT.json have c01+c10<8 but satisfy (5),
so PR2294 Proposition B's old form-specific test does not decide them
while the new theorem does. The 100 concrete form pairs checked by the
verifier are examples, not an enumeration of all binary forms. Each has
five exact decoder fixtures, including a non-coordinate mixed factorization.

The seven residual rank pairs are not counterexamples or proven openings:
their actual c01,c10 can still satisfy section 4. No sub-128 decoder was
found or claimed. The criterion is sufficient, with no converse asserted.
No physical chart conversion, common-label embedding, supplier hosting,
precision, recursive interface, rank-power moment or kappa consequence is
established. The contribution is a COPY-rank-sum floor in the stated model.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New work is Apache-2.0; predecessor text retains its original credit.
