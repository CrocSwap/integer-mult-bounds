# Exact rank-error asymptote for the full Gaussian inverse

This contribution was produced by Nick Petalas. Apache-2.0.

For the original **untruncated varying-phase full cell** of JoyboyBrian's
[PR5183](https://github.com/CrocSwap/integer-mult-bounds/pull/5183), fix alpha>0
and let theta tend to zero. For every fixed nonnegative integer r,

```text
best rank-at-most-r approximation error / inverse operator norm
    -> 1 / sqrt(2 floor(r/2)+1).
```

This is a scoped written mathematical proof with exact finite corroboration.
The new result determines the complete limiting singular spectrum and the
optimal fixed-rank error, beyond the predecessor's top-norm result.
The two boundary layers duplicate every singular value. Consequently rank
one cannot lower the limiting relative error, and the limiting operator
needs rank four to reach relative error at most one half. These are analytic
rank counts, not physical recursive bills. No new kappa is claimed.

[PROOF.md](PROOF.md) defines the exact finite matrix and proves the result.
It constructs odd/even half-line Hermite bases and derives
`s_k(T_b)=1/(2 sqrt(b(2k+1)))`. Rank-nullity proves optimality even for
approximants mixing the two edges. The source operator-norm limit and the
Lipschitz property of rank approximation errors transfer the result to the
finite Gaussian inverse. The source theorem is a credited premise; no
predecessor scientific replay is included.

## Reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-inverse-rank-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/gaussian-inverse-rank-error/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-inverse-rank-error
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-inverse-rank-error --check-source-history
```

On another host, substitute its Python 3.12 path. The final command requires
a commit containing this package and full source history. The direct commands
print `PASS_GAUSSIAN_INVERSE_RANK_ERROR` inside a generated JSON receipt bound
to the package and source-proof hashes. Optional `--receipt /absolute/path.json`
creates that receipt exclusively outside the checkout. No replay writes
artifacts into the checkout.

The exact verifier compares explicit factorial and recurrence definitions of
Hermite polynomials, evaluates their Gaussian Gram integrals, and solves
weighted antiderivatives by descending coefficients. Coherent polynomial
mixtures test the integral map and normalization. Finite doubled diagonal
truncations check rank indexing, and rank-one matrices mixing the first two
edge modes have explicit kernel witnesses. Rational tolerance checks exercise
the least-rank threshold, including its equality cases. Invalid contracts and
one-edge, parity and dilation controls remain active under optimized Python.
These are finite corroboration, not a substitute for the written proof or
classical Hermite completeness.

Local CPython 3.12.15 on macOS passed both registered commands. Individually
timed direct runs took 0.137 and 0.146 seconds, with identical JSON receipts.
They enumerate 34 polynomial definitions, 33 derivative identities, 512
Gram entries, 16 antiderivatives and normalizations, 81 coherent mixtures,
1,275 coordinate truncations, 324 rational tolerances, 33 mixed-edge
rank-one matrices and 15 rejection/semantic controls. These are check
durations and finite counts, not a runtime speedup claim.

## Scope and limits

The order of limits is fixed r or fixed singular index first, then theta
shrinking at fixed alpha. The exact limiting-operator least rank is
`2 ceil((epsilon^(-2)-1)/2)` for `0<epsilon<=1`. At equality thresholds this
is not an eventual finite-matrix least-rank assertion. No growing-rank or
growing-alpha uniformity is proved.

No coefficient or mode preparation, inverse application, rounded execution,
precision/tape/storage/movement tariff, dirty restoration, stock, native or
compiler admission, integer recovery or complete multiplication theorem is
supplied. The selected PR6030 frontier and all five framework assumptions
remain unchanged. Independent human and formal proof-kernel review are
unclaimed. Lean, Docker and the selected scientific cold replay are outside
this analytic contribution.

## Open next questions

Can the rank-error asymptote hold uniformly for a specified growing rank
r(theta)? This matters when the requested relative error vanishes. Start
with the source operator-norm remainder and compare it to the next predicted
singular value for one rank schedule. A useful uniform remainder and the
complete physical cost of preparing and applying those modes remain missing.
No wider construction search is included.

## Sources and overlap

Credit JoyboyBrian / PR5183 for the two-edge limit and its full coefficient;
Jose Manuel / PR4193, Vlado Vojdanovski / PR1673, Ryanson Jonathan / PR4435,
Nick Petalas / PR5150, Cinna Davis and the retained Gaussian lineage.
Classical Hermite completeness and the weighted derivative identity are
cited to [NIST DLMF 1.18.42](https://dlmf.nist.gov/1.18#E42) and
[18.9.26](https://dlmf.nist.gov/18.9#E26). Hermite singular systems,
minimax approximation and operator-norm perturbation are classical; no
general literature priority is claimed for them. The contribution is their
explicit full-cell inverse rank-error consequence. Predecessor files and
credit are unchanged.

The base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8, selected PR6030. [TASK.json](TASK.json) records the
changed card scope; [SOURCES.json](SOURCES.json) pins the source proof.
The advance [claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363381)
followed live claims, reservations, current-main formula/object searches,
open/merged searches and recent account-work checks. Sparse historical
notes, arbitrary historical diffs and unpublished work remain limits.

Related open work includes PR3910 on forward row-norm transfer, PR371 on
final-grid rounding, PR6413 on finite encoded setup, PR6459 on constant-shift
finite-cap inverse bounds, and PR6404/6405 on truncated Gaussian Schur
boundaries. Their objects or quantities differ from this full-cell inverse
singular spectrum; no shared computed number is compared. PR5986 concerns
polynomial locality under norm hypotheses rather than rank compression.

## Implementation bounds

Build the Lever led to a standalone exact verifier; Prove It Works led to
separate polynomial constructors, literal antiderivatives and Gram integrals.
Power of Ten inspection is confined to verify.py. There is no recursion,
network, subprocess, dynamic code loading or predecessor executable import.
Polynomial degrees are at most 33, Gram blocks have sixteen modes per parity,
the mixing enumeration has 81 four-coefficient vectors, and every truncation
subset lies in an eight-mode space. Rank-one controls enumerate 81 integer
matrices. Tolerances have denominators at most 32. Functions fit sixty lines.
Explicit exceptions preserve checks under optimization.

Power of Ten rule 3 has a managed-runtime deviation for Python integers,
Fractions, tuples and lists. Fixed finite domains bound all live collections;
there is no steady service. Rule 9 retains standard-library iterator and
argument-parser dispatch with fixed visible targets. Package hashing admits
at most sixteen regular files of at most 1 MiB each and one source proof of
at most 1 MiB. The receipt file is scoped and closed on every exit. A fixed
memory native checker would be required to remove those runtime deviations.
Warning-strict normal and optimized execution and in-memory AST/compilation
checks supply local diagnostics; no shared configuration changes are made.
