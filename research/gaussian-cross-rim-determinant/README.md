# Exact Gaussian cross-rim determinant and channel rank

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with exact finite corroboration.
For a bandwidth-b truncated Gaussian, eliminate an m-coordinate contiguous
interior A between two b-coordinate rims, where m>=b>=1. The complete
cross-rim Schur block C satisfies

```text
det C = (-1)^(bm) t^(b^2(m+b)) / det A.
```

Here t is any nonzero element of any field and A must be invertible.
Thus C has rank exactly b. No exact linear factorization C=UV through
fewer than b scalar channels exists. Nonzero diagonal row/column gauges
preserve the rank. The theorem gives an exact necessary budget for this
boundary; it is not a recursive-call or runtime lower bound.

The new statement is the determinant formula and its parameter-independent
noncancellation once A is invertible. In the older sufficient real range
0<t<=1/3, full-rank conclusions also follow from Nick Petalas's
[PR5207](https://github.com/CrocSwap/integer-mult-bounds/pull/5207)
ordered-minor theorem. That earlier result and its proof are not replayed
or claimed again. The formula covers parameters and fields outside that
real range. It follows by a classical triangular-minor/block-determinant
argument, not by a new general determinant identity.

For b=2, m=3, t=1/2, the exact fixture has det A=135/256 and
det C=1/552960. It therefore needs two exact scalar channels.
For real 0<t<=1/3, elementary strict diagonal dominance supplies the
invertible-interior premise at every size. [PROOF.md](PROOF.md) gives the
all-size proof, a more general outer-band product identity, gauges and
the precise factorization scope.

## Evidence and reproduction

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-cross-rim-determinant/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/gaussian-cross-rim-determinant/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-cross-rim-determinant
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-cross-rim-determinant --check-source-history
```

Substitute another CPython 3.12 path if needed. The direct marker is
`PASS_GAUSSIAN_CROSS_RIM_DETERMINANT`. The last command requires committed
publication bytes. The verifier writes nothing and prints a generated
receipt bound to SHA256 hashes of all six package files. No handwritten
receipt or stored numerical certificate is supplied.

The finite rational checks enumerate:

- 144 Gaussian cases, b=1,...,4, m=b,...,b+5, with each of the six
  parameters -1/2, 1/4, 1/3, 1/2, 2/3 and 2.
- 20 asymmetric banded hosts with nonzero outer band and an invertible
  strictly diagonally dominant interior.
- 12 signed, nonuniform row/column gauge cases, checking every entry of
  the cross-rim covariance identity.
- Eight invalid-input rejections and three semantic counterexamples:
  a missing outer-band factor permits rank loss, a wrong parity changes
  a determinant, and omitted rim factors give a wrong exponent.

Rational Gauss-Jordan elimination builds each Schur block. Fraction-free
Bareiss elimination checks its determinant, the interior determinant and
an independently selected full-host minor. These are different exact
calculations in one verifier, not independent scientific review. The
universal and field-valued claims rest on the written proof. No finite
field census, predecessor replay, selected cold replay, Lean or Docker
is run. Explicit exceptions retain all checks under optimized execution.

Local CPython 3.12.15 on macOS passes both direct modes and the registered
replay. The two registered command forms each take less than 0.12 seconds
locally, against a 120-second command limit. This is a replay duration,
not a speedup claim. Hosted CI remains pending at publication.

## Scope and relation to the bottleneck

This changes the `uniform-transfer-audit` card to a new structural side
result at the retained Gaussian boundary, rather than an audit of another
contributor or a discharge of an assumption. The selected binding
orientation passes. It does not replay the selected supplier.

The separated-carve bandwidth bound 2b-1 remains unpaidmoon's PR4373 and
James Reed's earlier work. Ryanson Jonathan's PR4407 addresses structural
fill; PR5207 supplies a restricted real-entry sign theorem. Neither
bandwidth nor individual nonzero entries alone should be read as a lower
rank compression certificate. The new determinant settles exact block
rank and leaves approximate compression open.

No new kappa, selected-frontier change, full multiplication theorem,
physical caller, native implementation, rounded recovery or useful
singular-value bound follows. The caller already allows O(b) boundary
width, so this obstruction does not worsen its stated asymptotic cost.
Low displacement rank is a different structure and is not excluded.
All five selected framework assumptions remain. Independent human and
formal proof-kernel review are unclaimed.

## Open next questions

Can a concrete retained boundary solve use approximate cross-rim
compression with a favorable complete bill? Start by pinning its kernel,
truncation, diagonal gauges and allowed final error. A singular-value tail
bound, representation/movement costs and rounded error propagation are
required; exact full rank alone does not decide this. The structured
question is in [TASK.json](TASK.json). Research stops at the exact formula.

## Provenance and credit

Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. [SOURCES.json](SOURCES.json) binds the catalogue, selected
record and predecessor statements as historical provenance. No predecessor
executable is imported. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360797).

Credit Cinna Davis PR4100 for the Gaussian caller; unpaidmoon PR4373,
James Reed PR4285/4298/4299 and Ryanson Jonathan PR4407 for the retained
carve and fill questions; and Nick Petalas PR5207 for real-entry signs.
The block determinant, rank-factorization and diagonal-dominance arguments
are classical. The new contribution is the exact boundary determinant
and its explicitly scoped channel consequence. No literature-priority
claim is made, and all predecessor credit lines remain unchanged.

Live open PRs, recent account work, handoff claims, local reservations,
main-tree README searches and merged searches were checked before the
claim. The cached overlap helper was also run. Sparse local notes,
unpublished work and arbitrary historical diffs remain coverage limits.
A concurrent claim studies PR5207's largest real positivity range; that
is a different question from this exact determinant with a nonsingular
interior. No result of that work is assumed or checked.

## Verifier constraints

Power of Ten inspection covers the single new Python file. It uses no
recursion, subprocesses, writes, dynamic code or predecessor imports.
Functions stay below 60 lines. All matrix loops have dimensions at most
24; actual fixtures have size at most 17, and all other loops range over
the fixed domains above. Hash reads are limited to six files of at most
256 KiB each. Matrix input is internal, with explicit dimension, bandwidth
and nonsingularity checks. No public arbitrary-size service is supplied.

Rule 3 has a managed-runtime deviation: exact Python integers, fractions
and lists allocate dynamically. The fixed input literals and finite matrix
sizes bound the live algorithmic collections; interpreter allocation is
not instrumented. A fixed-storage native rewrite would be required before
use in an allocation-prohibited environment. Rule 10 uses warning-strict
normal and optimized execution and AST/function-size inspection; no static
type checker is configured for this isolated standard-library verifier.
