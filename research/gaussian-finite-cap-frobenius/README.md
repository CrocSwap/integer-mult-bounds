# A smaller finite-cap Gaussian inverse bound

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped written proof with exact finite corroboration. No new kappa.**
For every N>=2, gamma>0 and |s|<=1/2, the normalized Gaussian section

    T_N(s)[i,j] = q^((j-i)^2-2s(j-i)),  q=exp(-gamma),

has the improved bound

    ||T_N(s)^(-1)||_2 <= sqrt(D_N(q^4)) / P_(N-1)^3 < N/P_(N-1)^3,
    P_(N-1) = product_(r=1)^(N-1) (1-q^(2r)),
    D_N(x) = N(N+1)/2 + ((N-1)x-Nx^2+x^(N+1))/(1-x)^2.

The old bound and inverse-entry estimate are credited to Jose Manuel /
[PR4193](https://github.com/CrocSwap/integer-mult-bounds/pull/4193).
This answers its first Open next question in part. The new step sums the
squares of the complete entry-decay estimate before applying the Frobenius
norm. [PROOF.md](PROOF.md) proves the all-size corollary, endpoint envelope,
closed form and strictness. There is equality between the two bounds at N=1.

At N=2 and q=1/2 the old bound is 128/27 and the new bound is 112/27,
exactly one eighth smaller. For fixed q, their ratio tends to 1/sqrt(2) as
N grows. This is a limit of upper bounds. No asymptotic formula or optimal
constant for the actual inverse norm is claimed.

## Reproduce

From the worktree root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-finite-cap-frobenius/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/gaussian-finite-cap-frobenius/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-finite-cap-frobenius
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-finite-cap-frobenius --check-source-history --check-modes
```

Another CPython 3.12 path may be substituted. The direct verifier prints
`PASS_GAUSSIAN_FINITE_CAP_FROBENIUS` in a generated JSON receipt bound to all
six package-file hashes. It writes nothing and runs without Git, network or
predecessor executables. No handwritten receipt is supplied.

The finite checks compare the closed form to independent weighted and
entrywise sums, test the closed-half-shift envelope, and construct literal
rational inverses by Gauss-Jordan elimination. Every inverse is checked on
both sides before its full squared Frobenius norm is compared with the new
bound. Invalid parameters, an omitted lower triangle, a wrong inverse sign,
a singular matrix and the size-one equality are explicit controls. All
checks remain active under optimization. The written proof supplies the
universal quantifiers; finite checks are corroboration. The local complete
replay passes 896 geometric cases, 889 strict improvements, 180 literal
inverses with 2,376 entries and 180 shift-envelope cases. Fourteen invalid
inputs reject and nine named semantic control groups pass.

## Scope, sources and credit

This is an analytic side result under the cited PR4193 entry theorem. It is
not an audit of that result. No predecessor scientific suite is imported or
replayed. The complete source proof and README are pinned as historical
provenance in [SOURCES.json](SOURCES.json). Frozen sources are unchanged.

The original `uniform-transfer-audit` card is marked changed in
[TASK.json](TASK.json). Entry orientation used the current selected-binding
positive control. No selected framework assumption is discharged. Scientific
base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8, selected PR6030. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362912)
records this target. Live claims, local reservations, recent account work,
main formula/object searches and merged/open PR bodies were checked. Sparse
notes, arbitrary historical diffs and unpublished work remain coverage limits.

Credit Jose Manuel / jmbarrancoml PR4193 for the explicit question, entry
bound and finite-cap framework; Vlado Vojdanovski / PR1673 for the retained
q-LDU identities; Jeremy Kothe and the PR1758 contributors for the shifted
Gaussian lineage; and Cinna Davis for the later broad Gaussian caller.
Frobenius domination, convexity and finite geometric sums are classical.
The explicit improved bound and its proof are the additional contribution.

JoyboyBrian / PR5103 and PR5183 prove varying-phase full-cell bounds and a
boundary-layer operator limit. They do not supply the constant-shift finite
Frobenius improvement here. Recent Schur-fill results study eliminated
boundary matrices rather than this input inverse-norm estimate. No common
numerical norm or contradictory value is inferred.

Optimal inverse constants, a growing-parameter caller substitution,
coefficient preparation, rounded-prefix errors, diagonal gauges, native
operators, physical movement/stock, restoration, compiler and complete
supplier costs remain separate. No selected cold replay, native suite, Lean
or Docker build is run. Independent human and formal proof-kernel review
are unclaimed. The selected frontier is unchanged.

## Open next questions

- Find a matching finite-size lower bound or the sharp fixed-q half-shift
  inverse-norm asymptotic. Start with a trial vector for the positive
  checkerboard inverse and retain every boundary row. Sharpness remains
  the missing step.
- Bind one actual rounded constant-shift caller to the new allowance.
  Substitute it into that caller's perturbation inequality, retaining its
  diagonal gauges and complete coefficient, precision and physical costs.
  Those caller obligations are not supplied here.

Structured first steps and blockers are in TASK.json. The first verified
improvement is shipped without pursuing these follow-ons.

## Verifier constraints

The executable accepts no command-line workload. Numeric helper sizes are
capped at 128, rational encodings at 20 bits and literal inverse matrices at
6 by 6. Loops are bounded by those caps, four kernel roots, five sizes and
nine shifts. Functions have fewer than 60 physical lines. State is local
apart from immutable constants; file handles are scoped; errors propagate.
There is no recursion, indirect dispatch, subprocess or dynamic evaluation.

Power of Ten rule 3 deviation: CPython dynamically allocates managed integers,
Fractions and containers in this finite command. Matrices are at most 6 by 12
including augmentation, only one inverse case is live, and file reads are
capped at 256 KiB per each of six files. Exact arithmetic sizes are bounded
by the fixed rational grids and loop caps. Revisit fixed storage before
embedding this in a runtime with allocation constraints. Normal/optimized
warning-strict runs and source compilation are the available diagnostics;
no repository-wide analyzer configuration is changed.
