# A solver-free lower bound for P111 generalized label decoders

This is a scoped lower bound on a sum of rational pairing ranks. It is not a
new multiplication exponent, and it does not assert that every abstract term
can be implemented at its lower-bound price. The physical interpretation uses
the per-total drop-pricing premise of DreamingOfClouds' #446, Theorem C.

## 1. Fixed model and exact geometric premises

Let `L` be the 120 E8 root-line representatives in the extended-Hamming
numbering used by #370 and the punctured-star packages. Each has squared norm
4, and `G = LL^t/2` has diagonal 2 and off-diagonal entries in `{−1,0,1}`.
Put `B0 = (J + G) mod 2`.

Delete one of these nine-element sets:

- #545: `{39,52,57,71,76,78,103,109,114}`;
- #555: `{10,15,51,53,56,66,72,89,111}`.

Write `P` for the ordered deletion list and `V` for the 111 live indices.
Let `B = B0[P,P]`, `M = B^(-1)` and `R = B0[V,P]`, all over F2.
The verifier establishes the following exact finite premises separately for
each set:

1. `B` is symmetric and invertible, with every diagonal entry equal to one.
2. `R` has column rank nine and `B0[V,V] = R M R^t`.
3. For every nonzero `x in F2^9`, put
   `S(x) = {v in V : R[v,:] x = 1}` and
   `W(x) = span_Q {L[v] : v in S(x)}`.
   Precisely the nine vectors `x=e_i` have deficient span; for them
   `W(e_i) = L[P_i]^perp` has dimension seven. Every other `W(x)` is Q^8.

A generalized **label** decoder here is any finite list of nonzero binary
vectors `(x_i,y_i)` satisfying

`sum_i x_i y_i^t = M` over F2.

Equivalently its source/reader rectangles reproduce the fixed binary decoder
`B0[V,V]`. Both sides of every rectangle are evaluations of linear
functionals of the fixed nine-dimensional label space. Arbitrary port-subset
rectangles outside this class, a changed decoder matrix, vector-valued labels,
and changes to the correction network are not covered.

The priced objective is

`C = sum_i beta(x_i,y_i)`,
`beta(x,y) = rank_Q G[S(x),S(y)]`.

Premise 3 and nondegeneracy of the Euclidean form give:

- cost 8 if neither vector is a coordinate unit;
- cost 7 if exactly one vector is a coordinate unit;
- cost 6 for `x=e_a,y=e_b` when `L[P_a] . L[P_b] = 0`;
- cost 7 for the remaining unit/unit pairs.

For the hyperplane/hyperplane case, the pairing kernel on `a^perp` is
`a^perp intersect span(b)`. It has dimension one exactly when `a.b=0`.
All other cases follow immediately. Every cost-6 term therefore has distinct
coordinate indices and `B[a,b]=1`. Conversely, distinct unit indices with
`B[a,b]=1` have cost 6. The verifier checks the finite premises using integer
elimination and cross-checks all 100 pairs of span classes by Fraction
elimination. Thus the classification covers all 511^2 ordered nonzero pairs.

## 2. Nine totals cost at least 63

Let `X` and `Y` have the `x_i` and `y_i` as columns. If there are nine terms,
`XY^t=M` is invertible, so both matrices are invertible and

`Y^t B X = I_9`.

Let `a` be the number of unit columns of `X`, `b` the number of unit columns
of `Y`, and `c` the number of terms with `x_i=y_i=e_j` for some coordinate
`j`. Unit coordinates do not repeat inside either invertible matrix.
Furthermore, if `x_i=y_j=e_t`, then `(Y^t B X)[j,i]=B[t,t]=1`, forcing
`i=j`. Hence the union of unit coordinates has size `a+b-c`, and

`a+b-c <= 9`.

If both sides of a term are distinct units, its diagonal entry in
`Y^t B X` is one, so it is a cost-6 term. A term with just one unit, or the
same unit on both sides, costs seven. The exact total is consequently

`C = 8*9 - (a+b-c) >= 63`.

This argument permits arbitrary bases and asymmetric source/reader choices;
it is not restricted to stars or symmetric factorizations.

## 3. Ten totals cost at least 64

For ten terms, `X,Y` are 9-by-10 of rank nine. Define

`K = Y^t B X`.

The identity `XY^t=M` gives `K^2=K` and `rank(K)=9`. Its complement has rank
one, so over F2

`K = I_10 + alpha beta^t`

for nonzero `alpha,beta` (with `beta^t alpha=1`).

Let `S` index the `k` cost-6 terms. Their diagonal entries `K[i,i]` equal
one, hence `alpha_i beta_i=0` for every `i in S`. In particular the
restrictions of `alpha` and `beta` to S have disjoint supports. The principal
submatrix

`K[S,S] = I_k + alpha_S beta_S^t`

is invertible: its square is the identity, since `beta_S^t alpha_S=0`.
Thus the corresponding unit columns of `X` are distinct, as are those of
`Y`. Let A and D be their two k-element sets of coordinate indices.

There are at least `2k-9` coordinates in `A intersect D`. Any such
coordinate has a unique representation `x_i=y_j=e_t`, with `i,j in S`.
Here `i != j` because a cost-6 term cannot have the same unit on both sides.
Since `B[t,t]=1`,

`1 = K[j,i] = alpha_j beta_i`.

Distinct common coordinates use distinct i and distinct j. Their number is
at most each of `|supp(alpha_S)|` and `|supp(beta_S)|`, whose sum is at most k.
Therefore

`2k-9 <= |A intersect D| <= floor(k/2)`,

which forces `k <= 6`. All other terms cost at least seven, giving

`C >= 6k + 7(10-k) = 70-k >= 64`.

No enumeration of SAT models or selection of a term-type pattern is used.
The bound 64 is only a lower bound for ten totals; attainability at 64 is
not asserted.

## 4. Arbitrarily many totals and attainment

Fewer than nine rank-one terms cannot sum to the rank-nine matrix M.
Eleven or more nonzero terms cost at least `6*11=66`. Terms with a zero
factor can be deleted without changing the decoder and need not be counted.
Sections 2–3 therefore cover every possible improvement over 63, even when
the number of totals is not bounded in advance and repeated terms are allowed.

For each of the two fixtures, the row decomposition

`M = sum_{i=0}^8 e_i (row_i(M))`

has nine cost-7 terms. Its literal vectors are supplied in the two baseline
JSON files and checked against all 111-by-111 live decoder entries. Hence
the exact optimum of this abstract copied-rank objective is **63** for both
fixtures.

## 5. What this adds and what remains open

GamingPuzzled's #620 already reports that cost <=62 is infeasible for a
nine-line puncture identified there as #545, using CaDiCaL without proof logs.
That reported optimum is predecessor work, not a novelty claim here.
There is a source-binding discrepancy: the archived `hamming_e8()` sorts the
Hamming words, while the actual supplier files use a different order of the
same signed root set. The report's literal indices select supplier-index set
`{9,31,37,52,66,76,78,111,119}`, rather than the actual #545 deletion set above.
`ORDERING.json` records the complete exact permutation. The reported 44
cost-6 ordered pairs belong to that archived-order example; the actual #545
example has 36 (the actual #555 example has 44).

The contribution is a short algebraic proof independent of that solver,
exact portable verification bound to the actual supplier files (the archived
exploration uses floating rank in `geo.py`), and explicit coverage of #555's
different puncture. The ordering discrepancy does not refute the reported
optimum; the present proof establishes 63 for both actual published inputs.
#631 proves a broader puncture threshold for star decoders; the present class instead
permits asymmetric factorizations and extra totals for two fixed punctures.
#669 concerns paired-hypercube stars, a different geometry.

The final overlap review also read #717's section 5. Its complex P111
examples have eight rational terms priced by binary label-pairing rank;
the present bit model has binary label terms priced by rational pairing
rank. #717 explicitly credits the bit-side value 63 to #620 and does not
repeat that calculation. #703 proves a quaternionic copy-cost floor;
#708 reduces R420 operand-preparation XORs while retaining its nine copies;
#715 studies a non-root-port extension. None of those results is used as a
premise here. This review is not a global priority or novelty claim.

The proof does not certify the general drop-pricing interface, simultaneous
frame scheduling, source access, helper preparation/restoration, common-cut
or mutable-basis assumptions, the suppliers, the assembly, or the full
multiplication theorem. It does not show uniqueness of every possible E8
decoder matrix. It closes only the stated label-functional factorization
mechanism for reducing this copy-rank objective. There is no new kappa claim
or claim to improve the selected frontier.

The all-length conclusion comes from the written linear-algebra proof.
Finite code checks support its premises and test its finite-dimensional
identities; they are not a formal proof-assistant verification.
