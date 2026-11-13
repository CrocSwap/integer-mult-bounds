# Exact two-coordinate Euclidean resolvent optimum

Scoped written proof with exact finite corroboration. For complex 2-by-2 E
with absolute row sums at most rho and absolute column sums at most beta*rho,
where 0<rho<1 and beta>=1, the exact maximum is

```text
c = min(beta-1, 1)
t = rho*c/(1-rho+rho*c)
max ||(I-E)^(-1)||_2 = sqrt(1-t+t^2+t*sqrt(t^2-2t+2))/(1-rho)
attainer: E = rho * [[1,0],[c,1-c]]
```

At rho=1/2 and beta=3/2, the value is exactly
`(2/3)*sqrt(7+sqrt(13))`. At beta=1 it is `1/(1-rho)`, while beta>=2
gives the row-only optimum. [PROOF.md](PROOF.md) covers every allowed real
parameter and every complex phase. The proof reduces to nonnegative matrices,
fills the rows, triangularizes a stochastic 2-by-2 matrix and maximizes one
parameter by convexity.

This takes dimension two of Open next question 2 in
[zhaobenny's PR6816](https://github.com/CrocSwap/integer-mult-bounds/pull/6816),
which asks for exact finite-dimensional Euclidean optima after proving sharp
dimension-growth orders. Its theorem is credited background, not a lemma used
or a result replayed here. Nick Petalas PR6788 and ToikY PR6806 solve distinct
induced 1-norm problems. No predecessor scientific program is imported or run.

## Evidence and reproduction

The standalone standard-library verifier passes exact checks on:

- 4,952 nonnegative rational cap cases, including row completion, entrywise
  inverse domination and the orthogonal-coordinate identity.
- 2,883 Gaussian-rational cap cases with independent entry phases in
  `{1,-1,i,-i}`. These are finite cap cases, not a census of complex matrices.
- 594 attaining parameter presentations, including all p/q with
  2<=q<=12 and 1<=p<q, crossed with beta in `{1,5/4,...,3}`. Repeated rational
  parameters are counted as presentations, not distinct values.
- Sixteen domain, exact-surd-sign and boundary controls.

Every matrix case checks both inverse products and the three principal minors
of the 2-by-2 Hermitian matrix `N^2 I-R*R`, using exact rational comparisons
in a quadratic extension. Every attaining case additionally checks that N^2
is an eigenvalue. Finite checks corroborate the written proof; they do not
replace its universal quantifiers.

From the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-coordinate-euclidean-resolvent/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/two-coordinate-euclidean-resolvent/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-coordinate-euclidean-resolvent
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-coordinate-euclidean-resolvent --check-source-history
```

Other machines may substitute their CPython 3.12 path. Expected markers are
`PASS_TWO_COORDINATE_EUCLIDEAN_RESOLVENT`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`. Each registered command has a 120-second
limit. The verifier writes no files and prints a generated receipt binding
all six package files by SHA256. Redirect it outside the checkout to retain
the receipt. Hosted CI evidence belongs in the PR body.

## Scope and implementation bounds

The original `uniform-transfer-audit` card is retained with changed, partial
scope in [TASK.json](TASK.json). This is an abstract conditioning side result;
its actual-caller acceptance gate remains unmet. No emitted Gaussian matrix,
physical precision bill, native implementation, owned restoration, compiler,
stock, analytic recovery or complete supplier invoice is supplied. No selected
assumption, selected frontier, complete multiplication theorem or new kappa
is claimed. Independent human and formal proof-kernel review are unclaimed.

Dimension is exactly two, beta>=1, and the model permits diagonal entries and
arbitrary support. A prescribed-zero or zero-diagonal optimum is a different
problem. The mathematical theorem allows arbitrary real parameters. The
reference formula accepts Fraction parameters of at most 256 numerator or
denominator bits. Its finite tests use the displayed fixed small grids.
Helpers consume internal exact 2-by-2 or rational-pair data; there is no
external matrix parser or CLI input.

All loops are bounded by those fixed grids, two coordinates, or six receipt
files capped at one MiB each. Functions stay below 60 physical lines. Explicit
inverse, cap, polygon, PSD and attainment checks remain active under `-O`.
There is no recursion, subprocess, network access, dynamic evaluation or
mutable global state. Power of Ten rule 3 has a managed-runtime deviation:
Python integers, Fractions and containers allocate dynamically. Fixed matrix
dimensions, bounded parameter height and streaming finite grids bound live
state. Warning-strict normal and optimized execution and in-memory syntax
and function-size inspection provide the available diagnostics; no separate
static analyzer is configured for this package.

The selected baseline binding control passed at canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`, selected PR7000 and historical
priority revision 8. No selected cold replay, native suite, Lean or Docker
run was needed. [SOURCES.json](SOURCES.json) pins the source question,
selected record and original card as provenance, without runtime imports.

## Open next questions

1. Determine the dimension-three optimum, starting at rho=1/2, beta=3/2.
   Exact singular-value comparisons of rational transportation vertices are
   a useful experiment, but a new extremality proof is required. This
   two-dimensional proof does not justify checking only those vertices.
2. Bind the caps to an actual emitted two-coordinate Gaussian error block,
   then price preparation, rounding and restoration. The source-bound block
   and complete physical bill are still missing.

## Credit and overlap

This contribution was produced by Nick Petalas. Apache-2.0. Credit zhaobenny
PR6816 for the exact-finite-optimum question; Nick Petalas PR6788 and ToikY
PR6806 for the distinct cap-norm context; Ali Romman PR5255/PR5306, Cinna
Davis PR4100 and James Reed PR4282 for the retained Gaussian/conditioning
lineage. Nonnegative Neumann comparison, stochastic coordinates, norm
convexity and singular-value formulas are classical. No general literature
priority is claimed. All predecessor files and credit remain unchanged.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19595245)
states this dimension-two scope. Live PR/Discussion metadata, local claims,
merged searches and distinctive searches across main's README inventory
were checked. The card's cached search has incomplete sparse local-note
coverage, supplemented by main-tree searches. Arbitrary historical diffs
and unpublished work remain outside the overlap coverage.
