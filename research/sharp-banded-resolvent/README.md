# Exact inverse norms from a directed support graph

This is a scoped mathematical proof with exact finite checks. It gives the
sharp inverse 1-norm allowed by the row-gap and support hypotheses in
Cinna Davis's PR #4100 conditioning note. The complete kappa calculation
and the selected frontier do not change.

## The result

Let G be a finite directed graph on n vertices. Allow every diagonal entry.
An edge i to j permits the entry E[i,j]. Let 0 < rho < 1 and
`sum_j |E[i,j]| <= rho` for each row. Write d(i,j) for directed distance,
with `rho^infinity = 0`, and put delta = 1-rho. Then

```text
max_E ||(I-E)^-1||_1 = max_j sum_i rho^d(i,j) / delta.
```

This is a maximum over all complex matrices with that support and row
budget. Nonnegative real matrices attain it. Diagonal permission is a
hypothesis of attainment, not a condition needed for the upper bound.

### Proof

The Neumann series converges because `||E||_infinity <= rho < 1`.
A length-k path cannot connect i to j when k < d(i,j). Also
`|(E^k)[i,j]| <= ||E^k||_infinity <= rho^k`. Thus the absolute value of
entry (i,j) of the inverse is at most `rho^d(i,j)/delta`. Sum each column
and take the largest sum.

Fix a maximizing root j. Give the root a diagonal entry rho. From each
other vertex that can reach j, choose one edge that reduces its distance
to j by one and put rho in that entry. Put zero in all other entries.
A row that cannot reach j is zero. This matrix has the required support
and row budget. Its k-th power has entry (i,j) equal to zero for k < d(i,j)
and rho^k for k >= d(i,j). The root column of its inverse therefore
attains every entry bound at once. This proves equality.

### Banded lines and the conditioning consequence

For the line with vertices `-mb,...,mb`, permit `|i-j| <= b`, where b,m
are positive integers. Distance to zero is `ceil(|i|/b)`. The root-routing
matrix above has column sum

```text
[1 + 2b sum_(k=1)^m rho^k] / delta.
```

The difference from the bound in INVERSE-CONDITIONING.md is exactly
`2b rho^(m+1)/delta^2`. Consequently the dimension-independent ceiling
`1/delta + 2b rho/delta^2` is the exact supremum over finite dimensions.
Its constants cannot decrease using only these hypotheses. This does not
state that a Gaussian matrix attains the ceiling.

The squared Euclidean norm of the same column is
`[1 + 2b sum_(k=1)^m rho^(2k)]/delta^2`. The operator 2-norm is at least
that column norm. As m tends to infinity its square tends to
`[1 + 2b rho^2/(1-rho^2)]/delta^2`. For fixed b and delta tending to zero,
this is asymptotic to `b/delta^3`. The existing upper bound is asymptotic
to `2b/delta^3`. Thus the power delta^(-3/2) in the operator 2-norm cannot
improve uniformly in dimension. An exact operator 2-norm constant is not
claimed.

## Evidence and reproduction

Use Python 3.12 or newer; the standard library is sufficient.

```sh
python3 -I -B research/sharp-banded-resolvent/verify.py
python3 -I -O -B research/sharp-banded-resolvent/verify.py
python3 -B scripts/research_package.py --package research/sharp-banded-resolvent
```

Expected marker: `PASS_SHARP_BANDED_RESOLVENT`. The checker uses rational
Gauss-Jordan inverses, independently of the path formula. It exhausts every
directed off-diagonal support through three vertices, two row budgets and
every root: 402 attaining columns. It also checks 120 signed rational
matrices and 24 banded instances. Six controls reject invalid budgets or
diagonal permission and refute row-only inverse norm shortcuts. Checks
remain active under Python -O. The universal theorem rests on the proof
above; finite checks corroborate it.

## Scope, sources and credit

Cinna Davis supplies the original bound and Gaussian caller in
[PR #4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100).
James Reed supplies the periodic-section extension in
[PR #4282](https://github.com/CrocSwap/integer-mult-bounds/pull/4282).
Their source files are pinned in SOURCES.json at main
`ff3cc58e370d0f678e529246f8c73e8094e18fcf`. Neumann series, graph distance,
and induced matrix norms are classical; no literature-priority claim is made.
This package adds the exact support-dependent optimum and an attaining
family. It does not rerun either predecessor's scientific suite.

The Gaussian row gap, rounded coefficients, physical tape cost, complete
supplier, outer recovery and unconditional multiplication theorem remain
outside scope. No Lean, Docker or selected-frontier cold replay was run.
Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
No independent human review or proof-kernel verification is claimed.

## Open next questions

Can the actual Gaussian caller supply a column budget or a reversible
weighted measure that excludes this directed concentration? First bind such
a condition to its rounded matrix. That source-specific condition is the
blocker; the present row-only class cannot justify a smaller uniform order.
