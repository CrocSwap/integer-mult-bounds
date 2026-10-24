# Exact polynomial degree-cost distribution

For the two-role alphabet I+u y^T over F_q[t], with y over F_q and free
GL2(F_q) maps anywhere, the paid cost of a uniform invertible target of
exact entry degree D>=1 satisfies

    cost(M)-1 ~ Binomial(D-1, (q-1)/q).

Writing g_q=(q^2-1)(q^2-q), the exact number with cost r is

    g_q (q+1) (q-1)^r q^(D-1) binom(D-1,r-1),  1<=r<=D.

The mean is 1+(D-1)(q-1)/q and the variance is (D-1)(q-1)/q^2.
There are g_q(q^2-1)q^(2D-2) targets of exact degree D, and
g_q q^(2D) of degree at most D. Degree-zero targets are the g_q free maps.

This is a scoped algebraic counting proof with finite corroboration.
[PROOF.md](PROOF.md) extends #4763's binary constant-free cost reduction
to general fields and counts its unique expressions. The contribution is
the all-q joint degree-cost count and binomial law. The classical matrix
presentation and degree method retain Nagao's credit. No new group
presentation, native supplier, multiplication theorem or kappa is claimed.

## Evidence and reproduction

The standard-library verifier independently enumerates determinant-unit
matrices by grouping polynomial products with equal nonconstant tails.
It compares that complete set with literal reduced-factor products and
free endpoints, rejecting duplicate expressions and checking every joint
degree-cost count. The bounded censuses are:

- F2, entry degree at most four: 1,536 targets.
- F3, entry degree at most two: 3,888 targets.
- F4, entry degree at most two: 46,080 targets, using F2[z]/(z^2+z+1).
- F5, entry degree at most one: 12,000 targets.

The 63,504 targets require 135,570 product-tail comparisons. These are
enumerated counts, not a count of every rejected polynomial matrix.
All 924 invertible degree-one paid parameter tuples across the four fields
pass constant splitting; all free conjugations pass with their required
nonzero scalar. Eight control groups cover merging, cancellation, constants,
nonunit determinants, singular endpoints, conjugation scaling, the binary
degree-four compatibility vector and an incorrect field weight. Exact
normalization, mean and variance checks cover 480 integer pairs 2<=q<=16,
1<=D<=32. Non-prime-power q in that last check tests a numerical identity,
not a nonexistent finite field.

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/polynomial-cost-distribution/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/polynomial-cost-distribution/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/polynomial-cost-distribution
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/polynomial-cost-distribution --check-source-history
```

Another CPython 3.12 path can replace the local interpreter. Expected marker:

```text
PASS_POLYNOMIAL_COST_DISTRIBUTION targets=63504 fields=4 probability_cases=480 controls=8 no_new_kappa
```

The first output line is a generated receipt containing the census and
SHA256 hashes of all six package files. The verifier also checks the
predecessor proof against its hash in SOURCES.json. The receipt is emitted
to stdout. No handwritten receipt or generated evidence file is committed.

The card's initial 945-pairing positive control passed. Source-bound selected
metadata orientation passed after materializing its sparse omitted inputs.
Those orientation checks provide no new scientific result or selected
operator replay. The selected conditional kappa remains 0.00302015.

## Verification limits and code bounds

The all-field, all-degree claim is a written proof. Finite enumeration
corroborates it in the stated domains. The alphabet has two data roles,
base-field right vectors and free base-field maps. Singular endpoints,
multivariate coefficients and restored auxiliary roles are outside the
classification. Uniform targets of exact degree are the sampling measure;
uniform words or degree-bounded targets have different distributions.
Preparation, conversion, routing, precision, restoration, stock and a
complete physical consumer remain unpriced. No selected replay, Lean or
Docker build was run, and independent human and formal proof-kernel review
are unclaimed.

Every verifier loop has a finite bound from the fixed four configurations.
There are at most 64 input polynomials, 4,096 product pairs and 16,777,216
pair comparisons per census before grouping. Every generated sequence has
total degree at most four. Free groups have at most 480 matrices. Probability
checks have 480 cases and at most 32 entries per case. No function reaches
60 physical lines, there is no recursion, and checks remain active under
optimization. The script reads the six package files and one declared proof
input, writes only stdout, and propagates failures.

Power of Ten rule 3 deviation: Python allocates objects during the finite
census. Fixed input configurations bound collection growth; the largest
observed direct target set has 46,080 entries, and direct sets are discarded
after each field. A fixed-storage implementation is unnecessary for the
research contract and would change the verifier substantially. Revisit it
before allowing arbitrary degree or field-size inputs. Rule 10 limitation:
warning-strict ordinary and optimized execution and in-memory compilation
are available; optional external Python analyzers were unavailable locally.
The registered replay repeats the warning-strict checks in CI.

## Open next questions

- Determine the exact cost distribution under a degree-bounded target
  measure. The current exact-degree counts give a finite weighted mixture;
  a useful first step is a closed form for its moments. The sampling
  measure must be stated before comparing typical costs.
- Identify a literal native coefficient producer and consumer before
  using the abstract factor law for a supplier. Start with the price of
  polynomial left-coefficient preparation. Native conversion, routing,
  precision and restoration costs remain blockers.

## Credit

This contribution was produced by Nick Petalas. Nick Petalas #4763 supplies
the binary cost theorem and degree-four census; #4276/#4243 supplies its
preceding alphabet criteria and free-map normal form. Hirosi Nagao's
1959 *On GL(2,K[x])*, Theorem 2 and its degree proof, supplies the classical
structural context ([original paper](https://www.i-repository.net/contents/osakacu/sugaku/DB-M-010-02-04.pdf)).
The local-product and semilocal boundary retains ToikY #4334 and Nick
Petalas #4601/#4749 credit. Wentao Li #4099 following #2513 supplies the
right-vector alphabet lineage. Those predecessors are cited, not audited.
Apache-2.0.
