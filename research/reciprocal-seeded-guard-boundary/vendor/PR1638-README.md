# Three reciprocal guard bits from directed rounding

**Scoped precision refinement; no new kappa.** The retained Section09 reciprocal
routine uses five fractional guard bits after its six-bit warm-up. Keeping its
downward rounding signs proves that **three suffice for every real normalized
input `1<=c<2` and every integer target precision `p>=1`**. The returned dyadic
`x` satisfies `|1-cx|<2^-(p+1)` and `|x-1/c|<2^-(p+1)`.

The [written proof](PROOF.md) preserves the seed `5/8`, exact products, changing
input prefixes and capped doubling schedule. It supplies the precise implication
and its induction, not an extrapolation from finite tests. Zero, one and two
guards fail to propagate the existing invariant from arbitrary admitted states.
Those witnesses are not the actual warm-up outputs: optimality for the **seeded**
routine remains open.

This is an explicitly labelled side result under `uniform-transfer-audit`.
Section09 proves a downstream exact-arithmetic corollary and is not a dependency
of the multiplication theorem. The selected conditional frontier, frozen sources,
root outer schedule, recursive call count and supplier profiles are unchanged.
Two fewer fractional product bits are a sufficient precision refinement, not a
measured speedup or a new multiplication exponent.

## Evidence and independent checking

| Check | Exact completed domain |
| --- | --- |
| Rational / integer full-trace agreement | 16,320 common prefix cells, both guard allowances, `p=1..8` |
| Paired outer stage traces | 64,064 per allowance; every prefix, product and output compared |
| Separate integer census | 81,920 cells, `p=1..10`, candidate and baseline grids |
| Separate intermediate endpoint checks | 774,784 across 387,392 stage cells |
| General invariant fixtures | 4,995 rational boundary/interior states in the tests |
| Nondyadic cell-interior fixtures | 120 candidate/baseline executions through `p=12` |

[CERTIFICATE.json](CERTIFICATE.json) contains exact rational margins, full-trace
digests, symbolic residual/slack identities and mathematical failure witnesses.
[INDEPENDENT.json](INDEPENDENT.json) records the separately written integer
checker, its full coverage, endpoint maxima and transcript digest. Both retain
incoming iterate precision exactly when the first three-guard stage has five
bits but its incoming warm-up has six.

Every tested cell fixes all input prefixes, so its stored iterates are constant.
The residual is affine in the true input. Endpoint checks therefore cover every
real input inside each finite cell, including nondyadic values. The all-precision
claim rests on the written quantified argument, not the finite domain.

The two implementations were written separately by Codex agents; neither imports
the predecessor's executable. This is implementation separation and mathematical
cross-checking, not independent human or proof-kernel review.

## Reproduce

From the repository root, Python3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/reciprocal-directed-guards
```

Expect `PASS_RECIPROCAL_DIRECTED_GUARDS`,
`PASS_RECIPROCAL_DIRECTED_GUARDS_INDEPENDENT`, eight passing test groups and
`PASS_REGISTERED_RESEARCH_PACKAGE research/reciprocal-directed-guards outcome=completed`.

Direct checks work under isolated optimized Python. Normal replay writes nothing.
Explicit regeneration uses `verify.py --write-receipt NEW_PATH` or
`independent.py --write NEW_PATH`; occupied paths are refused. The tests reject
source and receipt corruption, missing warm-up, stale input prefixes, a wrong
residual sign and invalid domains, and replay read-only inputs from a path with
spaces. [VERIFY.json](VERIFY.json) registers only this bounded package.
Local environment, actual commands and omitted checks are in
[VALIDATION.json](VALIDATION.json).

## Sources, scope and credit

Base main: `0a201997097b8a89b638f3a2afcb35db4184c8b2`. Exact consumed Section09
Git blob and SHA256 are in [SOURCES.json](SOURCES.json). The selected record and
priority-three catalog are historical provenance; no pending PR executable is
needed to replay. The candidate is an isolated numerical port and theorem,
not a replacement wired into the manuscript or selected compiler.

Credit **Hanson Sun (@bbMisk), [PR1528](https://github.com/CrocSwap/integer-mult-bounds/pull/1528),
head `f43caa53c5cc9717a8a04fe5a1538e31adeef313`**, for the earlier bounded Newton
audit and explicit all-precision question. We add the directed-rounding guard
refinement; we do not claim its full root/recovery domain. Credit OpenAI's retained
manuscript, its cited classical Brent reductions, and Douglas Colkitt's repository
and audit guidance. Source-specific notices remain in `upstream/LICENSE` and
`NOTICE`. No algebraic/literature priority claim is made.

The task/nonce, claim, overlap coverage and limits are in [TASK.json](TASK.json).
Discussion coverage is explicitly incomplete; a text search is not a novelty
certificate. The source's parking target already has a separate result in PR1379
and was not duplicated. Prepared for **@ToikY** with substantial **OpenAI Codex
assistance** in mathematics, implementation, verification and writing. Apache-2.0.

## Open next questions

Can the actual seeded routine use two guards under a stronger reachable-state
invariant? A first step is to derive a true-input interval invariant for the
warm-up and propagate it through capped stages. Further finite no-failure cells
alone cannot settle this; our generic-state witnesses do not settle it either.

Can the rounding identity and induction be kernel checked and bound to the
complete root caller? Formalize floor-grid residuals and capped recursion first,
then replay nested root and final-recovery contracts after substitution. The
root outer schedule, physical tape execution, head-return/cost analysis and
selected supplier/compiler/analytic obligations remain outside this package.
Structured questions and blockers are also recorded in [TASK.json](TASK.json).
