# Sharp inverse norms under simultaneous row and column caps

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with exact finite corroboration.
For any complex n by n matrix E whose absolute row sums are at most 0<rho<1
and whose absolute column sums are at most m rho, integer m>=2, the exact
largest induced inverse 1-norm is

    max_E ||(I-E)^-1||_1
      = [sum_(i=1)^n rho^ceil(log_m i)] / (1-rho).

The exponent for i=1 is zero. The bound covers arbitrary complex phases and
diffuse rows. A nonnegative routing matrix with E_(i,ceil(i/m))=rho attains
it. At n=m^h and rho=1/m the exact value is h+m/(m-1). Thus row cap 1/2
and column cap 1 give a sharp value 5 at n=8 and 8 at n=64. The row-only
maxima are 9 and 65, respectively.

[PROOF.md](PROOF.md) proves the all-dimension result by bounding every sorted
inverse-column partial sum and solving the resulting induction. This takes
the abstract column-budget portion of Ali Romman's
[PR5255](https://github.com/CrocSwap/integer-mult-bounds/pull/5255) open
conditioning question. That predecessor's theorem is cited, not replayed.
The extra column cap changes the admitted class. It is not asserted for an
actual emitted Gaussian matrix, and no supplier or new kappa is claimed.

## Exact finite evidence

The standalone verifier enumerates every nonnegative matrix through order
three with entries in {0,rho/2,rho}, row sums at most rho, and column sums
at most m rho, for m in {2,3} and rho in {1/3,1/2,2/3}. The 6,144 admitted
matrix evaluations check 54,072 sorted partial sums. Independent rational
Gauss-Jordan inversion finds the exact proposed maximum in all 18 domains.
A further 648 signed matrix evaluations exercise cancellation. Counts refer
to evaluations across the stated parameter tuples, rather than deduplicated
matrices across tuples.

The attaining construction is checked at all n=1..64, m=2..8 and five
rational row caps. Its 2,240 matrices check 72,800 column entries and 72,800
transport equalities; 420 also have independently computed dense inverses.
Sixteen critical closed forms, twelve rejected inputs, and five contract or
example controls include an illegal row-only star and the redundant-cap
boundary. The written proof establishes the unbounded complex theorem;
these finite checks corroborate it.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/column-capped-resolvent/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/column-capped-resolvent
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/column-capped-resolvent --check-source-history
```

Other hosts may substitute their CPython 3.12 executable. The direct marker
is `PASS_COLUMN_CAPPED_RESOLVENT`; the launcher also reports
`PASS_REGISTERED_RESEARCH_PACKAGE`. Both warning-strict normal and optimized
commands are registered. Explicit exceptions retain every acceptance check
under optimization. The verifier writes no files. Its stdout receipt binds
all six package files by SHA256. It also runs from a Git-free export of those
files with no external input. All source pins are provenance, not runtime
dependencies. No receipt is handwritten.

## Scope, credit and overlap

Ali Romman supplies the graph-support row-only envelope and the column-budget
question in #5255, plus the unequal-row extension #5306. Cinna Davis #4100
supplies the Gaussian conditioning context, and James Reed #4282 supplies
periodic sections. Nick Petalas #5859 handles forbidden diagonals under row
caps. ToikY #4209 proves Schur closure when both caps equal the same number
below one. The present column cap may equal or exceed one and gives an exact
finite-dimensional optimum. Neumann comparison, transport inequalities and
partial-sum induction are classical; no general literature-priority claim
is made. Frozen predecessor files and their credit are unchanged.

Canonical base is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision
8. The selected-baseline binding command passed. TASK.json records a changed
scope from the decoder card to this conditioning side result. The advance
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19440639)
records the target. Live open/account PRs, recent handoffs, active Discussions,
local reservations, merged-topic searches and main README searches were
checked. The overlap helper's sparse local inventory was incomplete; main
was searched separately through Git. Unpublished work remains outside that
coverage.

No actual Gaussian admission, physical preparation, rounding, stock, native
implementation, ownership or restoration, tape, compiler, analytic recovery
or complete supplier invoice is supplied. Noninteger column-to-row ratios,
unequal row caps and prescribed support graphs remain open. The selected
frontier and its five assumptions are unchanged. Predecessor scientific
suites, selected cold replay, Lean and Docker were not run. Independent
human and formal proof-kernel review are unclaimed.

## Open next questions

- Determine the exact envelope for a noninteger column-to-row ratio beta>1.
  Begin with a three-vertex rational-cap transport problem allowing split
  rows. Rounding beta upward can lose precision; the integer parent routing
  here does not saturate fractional capacities.
- Bind useful row and asymmetric column caps to one emitted Gaussian matrix.
  Export its exact rounded coefficients and charge their preparation before
  applying this theorem. That source-bound matrix and its physical bill are
  the missing obligations.

## Verifier constraints

All scientific domains are fixed, with matrix order at most 64 and dense
inversion at most 12. Every function is below 60 lines. Loops have explicit
finite bounds, and every inverse is checked by exact multiplication. There
is no recursion, subprocess, network access or dynamic code generation.
The managed Python runtime allocates Fractions and containers during checking,
a Power of Ten rule 3 deviation bounded by those fixed dimensions, fixed
rational fixtures and the one-MiB-per-file receipt inventory. Rejection
controls call only the local envelope and admission functions, a bounded
rule 9 deviation. Warning-strict normal and optimized runs and AST inspection
provide the available diagnostics; a separate static linter is unavailable.
