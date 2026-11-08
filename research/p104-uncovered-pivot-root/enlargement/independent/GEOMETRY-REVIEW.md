# Independent review: enlarged-mask capacity and dual prices

Reviewer: @CubeJerry with substantial OpenAI Codex assistance, worker D in the
same coordinated research team. Date 2026-11-08. The previous two-channel hub
package was not changed. No error was found in the stated capacity formula,
pruning argument or complete benchmark invoice under the physical contract.

The source is the L=18, p=8 uncovered-pivot root with one thin query, 18
independent scalar fields and the native profile retained from PR #6833.
The enlargement family has kl=0,...,8 and kr=0,...,9: nearest left fields
are added to every strict-right mask and nearest right fields to every
strict-left mask. These are exactly 90 choices, not arbitrary masks or roots.

REVIEW-SOURCE-PINS.json identifies the reviewed root, native profile, static
DUALS.json and extension verifier. The checker imports none of those
implementations. It independently constructs queries, inverts prefixes by
rational Gauss-Jordan elimination, parses native histogram literals without
executing their file, and uses different capacity and exponential calculations.

## Mathematical review

Let U_i be the query product strictly before full site i. A carrier projector
transported by literal queries is E_i=U_i E U_i^{-1}. For E=v phi, phi v=1,
its neutrality conditions at D=1,S=-1 are alpha_i v=0 and phi beta_i=0, where
alpha_i=y_i^T U_i and beta_i=U_i^{-1}x_i. Untransported x/y data are insufficient.

The masks can be treated as coordinate intersections. Before a strict-left
site the queries are supported in its original minimal mask, so the prefix
commutes with every coordinate superset. Before a strict-right site, the
scalar root endpoint expresses the prefix as minus the inverse of its suffix
times its own query. These factors are supported in the original minimal
mask; the prefix is scalar on the complement and again commutes with every
coordinate superset. The pivot mask is the entire space. Hence U_i^{-1}P_iU_i
=P_i for all these enlargements. The independent implementation checks actual
matrix conjugation on the selected cases. These commutations also support
the arbitrary-D factorization with the changed target masks.

For a nonempty site set J, let C be the common coordinate mask. Restrict
alpha_i and beta_i^T to C to form A and B. Admissible primals and duals lie in
ker(A) and ker(B). With c=dim(C), their bilinear pairing rank is

    c - rank(A) - rank(B) + rank(A B^T).

The radical on ker(A) is ker(A) intersect row(B). Applying A to row(B)
shows its dimension is rank(B)-rank(A B^T); subtract from c-rank(A).
This is an ordinary bilinear statement over characteristic zero, hence
valid over the complex caller field. It is not a Hermitian calculation or
a transfer of rational ranks to arbitrary odd finite characteristics.

A whole rank-one job requires phi v=1, so its J must have positive capacity.
Positive capacity is not claimed sufficient for a physical native job:
active-plane complements, other jobs and actual realization impose additional
constraints. Dropping those conditions is conservative for a paid lower bound.
When J grows, both admissible subspaces shrink in the ambient space, so their
pairing rank cannot increase. Capacity-zero pruning is therefore sound.

The cached implementation keys on the exact common-coordinate set and both
sets of normalized nonzero rows (zero rows may be retained harmlessly).
Row order, multiplicity and nonzero scaling preserve the two row spaces and
the pairing rank. No cache dependency on a changing site context is lost.

Demand at site i is d_i=|M_i|-2 because the native active interface has rank
two. Every actual whole-idle decomposition has nonnegative job counts x_J
with sum_(J contains i) x_J=d_i. A job costs (8|J|)^t. If integer weights obey

    sum_(i in J) lambda_i <= floor(10^18 (8|J|)^t)

for every positive-capacity J, multiplying by x_J and summing proves

    paid idle moment >= sum_i d_i lambda_i / 10^18.

This is weak LP duality directly; no primal optimum is required. Restricting
the searched weights to be nonnegative is harmless. Ignoring capacity
multiplicity and mutual orthogonality enlarges the primal domain and weakens
the paid lower bound.

Specializing D_i=1,S=-1 is necessary for an ordinary data-independent
whole-field carrier, or a carrier regular and nondegenerate at that
specialization. The argument does not cover singular/data-dependent frames,
extra transports or targets restricted to a spectral sector. A full
independent scalar field cannot disappear in the S=-1 specialization under
the declared whole-field contract. These premises remain essential.

## Executed independent checks

Every one of the 262,143 nonempty site subsets was enumerated for each of
four certificates. The code computes explicit rational nullspace bases for
A and B, then the rank of their full pairing matrix. It never uses the
capacity dimension formula or the construction's recursively pruned list.
Exact memoization reuses only identical normalized constraint systems.

| kl | kr | Feasible subsets | Price violations, all capacity zero | Complete upper margin |
|---:|---:|---:|---:|---:|
|0|0|512|41,156|−26.399872663196936965|
|5|5|10,339|7,584|−2.301874175501576844|
|7|8|52,111|214|−0.210890121535325573|
|8|9|107,295|48|−14.108395602800359692|

These 1,048,572 independent subset checks include no enlargement, a
near-critical interior choice, the weakest reported margin and maximum
enlargement. All feasible counts match, all dual inequalities hold, and all
demand objectives match. The caller-accounting reviewer separately confirmed
these violation counts and exact upper bounds with an all90 price review.

The separately written price engine uses a rational atanh logarithm series
with a geometric tail, positive Taylor bounds for exp(+z), and reciprocation.
The construction uses alternating bounds for exp(-z). Both independent bounds
give the same integer floor for 10^18*(8m)^t for m=1,...,18, t=1-.00337180.

The complete margin is reconstructed as

    18(native helper moment - native paid moment)
    +104(main target moment - one thin query - certified idle lower bound).

All 18 independent main targets come from their actual enlarged mask
incidences. Full rank mass, retaining every idle incidence, is exactly 760.
Native helpers/queries, main targets, the thin query and all idle demand are
present. Additional ordinary or precision costs cannot improve a negative
optimistic raw margin.

Controls require the product term in the capacity formula, enforce dual
annihilation, and demonstrate that omitting query conjugation changes the
capacity: enlargement (5,5), subset {4,8,9}, has transported capacity5 and
untransported capacity4. This is a concrete reason to retain actual transport.

Both warning-strict normal and optimized modes passed on CPython3.12.14:

```
python3 -I -W error -B review-a-extension/check_review.py --root-package ../worker-a/research/p104-uncovered-pivot-root
python3 -I -O -W error -B review-a-extension/check_review.py --root-package ../worker-a/research/p104-uncovered-pivot-root
```

Default replay is read-only and compares REVIEW-RESULT.json. `--emit`
explicitly creates a receipt; `--duals` can point to the parent extension's
same byte-pinned DUALS.json so packaging need not duplicate that file.

## Review limits

The capacity and pruning proofs were reviewed generally for this finite
family. This reviewer executed four complete subset censuses, not all90.
The caller-accounting reviewer separately checked all90 prices, margins and
the uniform derivative argument. My executed price result is at the benchmark;
the no-reentry claim uses that separate derivative proof, not a one-point
LP certificate. There is no independent full native Clifford/phase replay,
compiler theorem, new exponent, selected-frontier change or human acceptance.
