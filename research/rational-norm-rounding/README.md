# A quantitative obstruction to reversible inward rational rounding

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof with exact finite corroboration.**
A rational orthogonal map U admits an injective norm-nonincreasing map
F:Z^d -> Z^d with uniformly bounded error from U if and only if U is a signed
permutation. F may be nonlinear and d is any positive finite dimension.

For a nonintegral column U e_j=a/q in lowest denominator form, every integer
output y of norm n, with q not dividing n, obeys

    ||y-n U e_j||^2 = (2n/q)(nq-a dot y) >= 2n/q.

On the complete h-grid unit ball, injectivity and norm nonincrease therefore
force worst-case error at least sqrt(2h(1-h)/q), for h=1/N and integer N>=2.
Thus fixed C h error is impossible at every sufficiently fine dyadic grid.
This is a necessary bound; its asymptotic attainability is open. The full
argument and exact quantifiers are in [PROOF.md](PROOF.md).

This extends ywz65's [PR2589](https://github.com/CrocSwap/integer-mult-bounds/pull/2589)
fixed-phase disk obstruction to rational mixing in arbitrary dimensions.
PR2589's finite-set and restored-helper arguments are cited premises and
retain their credit. Its stronger two-dimensional fixed-phase obstruction
is not improved or replayed. The new step is the radial arithmetic error
quantum and the resulting dimension-independent classification and grid-ball
bound. Classical lattice and finite-set arguments are not claimed as new
mathematics. Credit also PR2527, Mason Hale / PR2313 and Jose Manuel / PR2298
for the retained interface lineage.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/rational-norm-rounding
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/rational-norm-rounding/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/rational-norm-rounding/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/rational-norm-rounding --check-source-history
```

Another CPython 3.12 executable may replace the local interpreter path.
Expected markers are `PASS_RATIONAL_NORM_ROUNDING`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Each direct run prints a generated JSON receipt bound to all six package files.
The default verifier writes no files and runs no predecessor program.

Finite evidence consists of four rational orthogonal fixtures in dimensions
two through four, all their eleven nonintegral columns, 59 complete sphere
streams and 1,254 literal output candidates. The fixtures include a q=5
rotation with and without a spectator, a noncommuting two-plane composition
with q=25 columns, and a rational four-coordinate Hadamard matrix with q=2.
The separate seven-point finite-ball census examines all 5,040 permutations;
exactly eight are norm nonincreasing, and all eight preserve every norm.

There are 704 arithmetic witness selections across eleven columns and 64
dyadic precisions, eight rejected malformed/out-of-scope inputs, an attaining
positive error quantum, 81 signed-permutation inputs and three premise
controls. High-precision output spheres are not enumerated. The reported
C=4 exclusion precisions are the first certified by this particular bound,
not exact interface thresholds or claims against a rounded implementation.

## Scope and implementation limits

An exactly reversible endpoint `(x,H)->(F(x),H)` with the complete entrance
state H fixed independently of x implies injectivity on that fiber. The
result therefore excludes the stated same-grid inward contract even with
arbitrary restored dirty helpers. Gaussian-rational unitaries are covered
by realification when the complete real grid and Euclidean norm are the
actual interface. Retained input/history, outward slack, finer output grids
and restricted reachable domains change the hypotheses.

No actual selected native phase or caller is bound here. Native realization,
rounding error for a permitted relaxed interface, physical storage/tapes,
compiler and outer admission remain open. No new kappa or selected-frontier
change is claimed, and all five selected framework assumptions remain.
Independent human and formal proof-kernel review are unclaimed. Lean, Docker
and the selected supplier cold replay are outside this package.

The executable uses only its fixed four fixtures. Arithmetic helpers bound
dimensions by four, sphere radii by eight, coefficients by 625, and the dyadic
pass by 64 precisions. Each sphere stream has at most 17^3 prefix trials;
the permutation pass has 7! iterations. There is no recursion, network access,
subprocess or mutable global cache. Functions have at most 32 physical lines.
Explicit exceptions remain active under `-O`. Python's managed allocations
are a bounded-runtime deviation from fixed allocation: live sphere-output
lists have at most 2*17^3 entries and at most 128 streams fit these bounds.
Only stream summaries survive each stream. Eight bounded callbacks are
rejection fixtures; scientific arithmetic uses direct calls. A lower-level
implementation would need fixed-memory and compiler analysis of its own.

## Open next questions

- What is the least outward norm slack compatible with a globally bijective
  bounded-error rounder for one rational four-coordinate unitary? Start with
  the q=2 fixture and declare a complete grid interface. This theorem says
  zero slack fails; it neither constructs a bijection nor prices one.
- Does a selected native consumer require this full-ball inward contract,
  or only a restricted reachable domain? Pin its complete entrance fiber,
  norm, grid and retained outputs first. The missing caller binding prevents
  interpreting this obstruction as supplier rejection.

## Coordination

Base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
selected PR6030. The `uniform-transfer-audit` card has changed scope to this
precision/restoration interface theorem, without claiming an actual caller
binding. The selected source-binding example passed. The advance
[CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19373516)
records the live main/merged/open/Discussion and reservation checks.

The concurrent PR4205 butterfly investigation studies linear exactly unitary
dyadic approximants in two complex coordinates. This result fixes rational U,
allows nonlinear maps, and imposes norm nonincrease. General rational-map,
norm-preserving and norm-nonincreasing searches found no matching theorem in
the checked coverage. Sparse notes, arbitrary historical diffs and unpublished
work remain overlap limits. Sources are pinned as provenance in SOURCES.json;
no predecessor scientific file is changed or executed.
