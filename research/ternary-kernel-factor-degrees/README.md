# Even local factor degrees for ternary prime-power kernels

This contribution was produced by Nick Petalas. Apache-2.0.

For every a>=1, the exact integral PR621 kernel at radix r=3^a has no
irreducible factor of odd degree over K=Q_3(u), where u is primitive.
In its k-th Newton slope block, every factor degree is divisible by
`2d_k`, with `d_k=3/gcd(3,k-1)`. The first block is an unramified
irreducible quadratic. When a>=2 the second is an irreducible sextic
with ramification index three and residue degree two.

The global cyclotomic field Q(u) also admits no odd-degree factor.
The two local blocks are not asserted to be factors over Q(u).

Claim type: scoped written arithmetic proof with exact finite corroboration.
[PROOF.md](PROOF.md) derives the new leading units and edge quadratics:

```text
odd k:   X^2+2X+2
even k:  2X^2+2X+1
```

Both are irreducible over F3. Every root field consequently has even
residue degree; the cited slope denominator gives the extra factor three.
This strengthens the available local factor information, without changing
the complex circle gap, an inverse implementation, or kappa.

## Evidence and reproduction

Use CPython 3.12 and its standard library from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/ternary-kernel-factor-degrees/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/ternary-kernel-factor-degrees/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ternary-kernel-factor-degrees
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ternary-kernel-factor-degrees --check-source-history
```

Other machines may substitute their CPython 3.12 executable. Direct replay
writes no files and works in a Git-free export of this six-file package.
It emits `PASS_TERNARY_KERNEL_FACTOR_DEGREES` in generated JSON bound by
SHA256 to all six package files. No receipt is handwritten or committed.

The exact finite corroboration covers 45 normalized contact checks across
radices 3,9,27,81,243. A separate dense multiplication in the uniformizer
basis checks all 15 distinct contact coefficients at radices 3,9,27.
Literal unit products through k=9 agree with the parity formula. Both
quadratics, 64 slope denominators, 10,368 admissible ramification/residue
pairs and 15 rejection controls pass. The two coefficient algorithms are
separately implemented here, not independently authored. These checks
corroborate the new arithmetic, not the infinite field-theoretic statements.

## Scope and credit

Credit Hao Yan / FanPUYen, [PR796](https://github.com/CrocSwap/integer-mult-bounds/pull/796)
at `22902155c7875139e43e4fdf15723142d6709bdd`, for the coefficient
polygon, contact positions, valuation normalization and root slopes.
Those are cited premises. No predecessor executable, fixture or receipt
is imported or replayed. Credit Ali Romman / PR621 for the exact kernel,
and the classical cyclotomic, Newton-polygon and local-field theory.
[SOURCES.json](SOURCES.json) pins the retained predecessor text as provenance.
J. S. Milne's standard local-field results have exact locators in the proof.
No literature-wide priority is claimed for the general methods.

This is a self-posed extension of PR796, not an audit. The
`uniform-transfer-audit` card is explicitly changed to this arithmetic
side result in [TASK.json](TASK.json). Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priorities revision 8,
selected PR6030. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371265)
records the scope. Live handoffs, active work, recent account contributions,
local reservations and main/merged formula and object searches were checked.
Sparse notes, arbitrary historical diffs and unpublished work remain limits.

No actual p-adic factors or roots are produced. Higher slope blocks need
not be irreducible; their exact factorization is unclassified here.
Complex conditioning, factor preparation, rounded execution, dirty restoration,
physical hosting, precision/tapes, stock/compiler, full caller and outer
costs remain unproved. All five selected assumptions remain unchanged.
No new supplier, kappa, selected-frontier change or complete multiplication
theorem is claimed. No predecessor scientific replay, selected cold replay,
Lean or Docker build was run. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

- Are the divisors `2d_k` attained by every irreducible factor for k>=3?
  Start with a higher residual calculation for the degree-18 third block.
  First residuals alone do not resolve the wild ramification or lifting.
- Can the local factor structure help an actual paid preparation algorithm?
  Start with a declared local precision, coefficient producer and complete
  conversion/restoration bill. No such consumer or favorable bill is supplied.

The structured questions and blockers are in [TASK.json](TASK.json).
No follow-up is reserved.

## Verifier constraints

All functions are below 60 lines. There is no recursion, dynamic loading,
subprocess, network call or external mathematical input. The direct call
graph is acyclic. Loops have explicit finite domains: a<=5, k<=9 for
unit products, k<=64 for denominator arithmetic, and ramification/residue
indices<=24. Polynomial arrays have at most 243 entries. The dense oracle
has a<=3, with product arrays at most 44 entries. Receipt reads are capped
at one MiB per fixed package file, and valuation scans at 4,097 divisions.
Explicit acceptance guards survive optimized Python. Warning-strict normal
and optimized execution provide the available Python diagnostics.

Power of Ten rule 3 deviation, verify.py: CPython allocates managed integers
and containers during this terminating exact calculation. The fixed domains,
one live coefficient calculation and bounded file reads limit live data.
In the largest cyclic calculation, coefficient l1 norm is at most 2^242;
the cyclotomic reduction and basis substitution add only fixed finite factors.
No fixed-allocation runtime claim is made. A native implementation would
need separate capacity accounting. No shared build configuration is changed.
