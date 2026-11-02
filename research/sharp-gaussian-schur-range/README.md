# Sharp Gaussian Schur-fill range: 0<t<=1/2

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with exact finite corroboration. No new kappa.

For every finite line and every integer bandwidth b>=1, define

```text
G[i,j] = t^((i-j)^2) if |i-j|<=b, and 0 otherwise.
```

The exact positive parameter range with the following strict ordered-minor
criterion, uniformly over all sizes and bandwidths, is **0<t<=1/2**:

```text
det G[R,C] > 0 iff |R_l-C_l|<=b for every matched position l;
det G[R,C] = 0 otherwise.
```

Here R and C are equally long increasing lists. Every principal pivot is
positive. For surviving i<j after eliminating E, a Schur entry is nonzero
exactly when the chain through E intersect (i,j) has every successive gap
at most b. Its sign is (-1)^|E intersect (i,j)|. Schur diagonal entries
are positive, and independent positive row and column scalings preserve
these statements.

[PR5207](https://github.com/CrocSwap/integer-mult-bounds/pull/5207) proves
the sufficient range 0<t<=1/3 and explicitly leaves the largest uniform
range open. The new result settles that question. It replaces the earlier
absolute-value estimate by a finite alternating-tail bound and handles
the repeated root at b=1,t=1/2. For every t>1/2 a width-one principal
determinant is negative at an explicitly specified finite order.
[PROOF.md](PROOF.md) gives the universal proof. The predecessor's path
factorization implication is cited and explained; its census is not replayed.

## Exact evidence

The standalone verifier tests only parameters in the new range,
t=2/5,9/20,1/2. It uses the standard library and exact integers/fractions.

- 503 strictly signed polynomial evaluations through b=12, the one
  exceptional zero at b=1,t=1/2, and 75 alternating-tail checks.
- All 8,307 nonempty ordered minors of six-vertex kernels at b=1,2,3:
  6,525 positive and 1,782 zero.
- All 2,223 nonempty-survivor Schur layouts through n=7 at b=1,2,3.
  Literal rational pivot updates and integer determinant ratios agree on
  all 25,335 entries: 16,503 positive, 4,632 negative and 4,200 zero.
- Six rational parameters above 1/2 have first negative principal orders
  5,4,15,22,49,157, respectively for t=3/5,2/3,51/100,101/200,501/1000,
  5001/10000. Rational and denominator-cleared integer recurrences agree.
  The endpoint identity D_n=(n+1)/2^n is checked through n=512.
- Eight invalid inputs and three altered matrices reject. Two exact Schur
  fixtures detect fill beyond the original band and negative fill parity.

These finite computations corroborate the written proof. They do not
establish its universal quantifiers by extrapolation. Checks use explicit
exceptions and remain active under optimized Python.

## Reproduce

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/sharp-gaussian-schur-range/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/sharp-gaussian-schur-range/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sharp-gaussian-schur-range
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sharp-gaussian-schur-range --check-source-history
```

Substitute another CPython 3.12 interpreter elsewhere. Expected statuses
are `PASS_SHARP_GAUSSIAN_SCHUR_RANGE`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`. Each registered command has a 120-second
limit. The replay writes nothing. Its generated JSON includes the result,
enumerated counts, exact negative determinants, interpreter version and
SHA256 hashes of all six package files. `--receipt /absolute/new/path.json`
also writes that generated receipt to an unoccupied path outside the package.
No receipt is handwritten or committed.

All [source pins](SOURCES.json) are historical provenance at base main
7c49fe32c55de02c2c873655c804b16e4c3fef0a. No predecessor executable or
external scientific input is imported. [TASK.json](TASK.json) records the
changed card scope, open questions and bounded overlap coverage. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360761)
precedes the proof and replay.

## Limitations

The sharpness assertion is uniform over bandwidths. A fixed b>=2 can
have a wider range; this package does not determine it. No concrete
retained caller is shown to satisfy the real linear-path hypotheses.
Periodic kernels, complex or nonpositive phases, conditioning, rounding,
native realization, ownership, routing, stock, tape costs, compiler
admission and exact recovery remain unproved here. The five selected
framework assumptions remain. No supplier admission, selected-frontier
change or complete multiplication theorem is claimed.

Independent human and formal proof-kernel review are unclaimed. Lean,
Docker, predecessor scientific replays and the selected full cold replay
were not run. The verifier has no recursion, dynamic code generation or
third-party dependency. Matrix dimensions are bounded by seven, polynomial
bandwidths by twelve and recurrence orders by 512. Exact Python arithmetic
uses managed allocation; its integer sizes are bounded by these fixed
domains. Package-hash reads are limited to the six declared source files.

## Open next questions

1. Can one concrete retained Gaussian caller use the sharp criterion after
   positive gauges? First pin its actual linear kernel, derive t and its
   truncation, and retain all conditioning and paid caller obligations.
   The missing caller and any additional phases are the blockers.
2. For a fixed b>=2, what is the largest parameter interval with the same
   ordered-minor criterion? First study the finite Gaussian polynomial's
   roots, then prove an all-size factorization or give a failing minor.
   A finite positive table cannot establish the interval.

## Credit

Nick Petalas / PR5207 supplies the question, the earlier sufficient range
and the path-factorization implication. Ryanson Jonathan / PR4407 supplies
the actual-real-entry question and generic support formula; unpaidmoon /
PR4373 supplies the separated carve; James Reed supplies the earlier
bandwidth and Gaussian fixtures; Cinna Davis / PR4100 supplies the retained
Gaussian caller motivation and lineage. Those results are cited premises
and their files and credit are unchanged. Alternating sums, negative-root
factorization, path cancellation and tridiagonal recurrences are classical.
No literature-priority claim is made for these general methods.
