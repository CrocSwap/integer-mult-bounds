# Three more controlled blocks: conditional kappa = 2.0156e-7

This research continuation keeps the exact dimension-30 producer of
[PR #12](https://github.com/CrocSwap/integer-mult-bounds/pull/12) and strengthens
the controlled-basis argument inherited from icekylinx's
[PR #10](https://github.com/CrocSwap/integer-mult-bounds/pull/10).
It supports the **unreviewed conditional witness**

    kappa = 5039/25000000000 = 2.0156e-7,

approximately **59.35% above PR #12's 1.2649e-7**. This compares asymptotic
exponent savings, not measured runtimes. The general arguments and inherited
multiplication interfaces remain mathematical proof obligations.

## Pre-submission comparison

During the local audit, eumemic submitted [PR #13](https://github.com/CrocSwap/integer-mult-bounds/pull/13).
At commit `3ef246fa4f69c87ebfed78376418afa9ffcad145`, its PR description and
exact certificate both state `kappa=7699/10^10=7.699e-7`. That is about
3.82 times this local candidate, so this note does **not** claim an improved
bound over PR #13. Both remain conditional, unreviewed arguments. PR #13's
proof has not been independently validated here.

Its auxiliary source-frame construction replaces the edges used by our new
auxiliary entrance block. Combining the results requires rebuilding that
rank accounting; adding all gains would double count incompatible changes.
The stage-two data entrance and stage-three data corner remain possible
compatible directions, subject to a fresh simultaneous-basis and cost proof.
This continuation is held locally pending that comparison and review.

## What changes geometrically

The same controlled basis exposes additional contiguous blocks inside corners
that the previous compiler treated as singleton pivots. There are two new
factorization arguments, applied to three edge classes:

| Edge class at h=30 | Old singleton pivots per edge | New singleton pivots | New block size |
|---|---:|---:|---:|
| Stage-two auxiliary entrance | 870 | 30 | 840 |
| Stage-three data entrance corner | 929 | 87 | 842 |
| Stage-two data entrance | 841 | 59 | 782 |

The first and third edges have the form `Pi_t tensor Pi_U`. Their first/last
900-coordinate corner is a projector on the multiplicity space, up to
invertible diagonal row and column factors. Apply the large-projector Schur
argument *inside this corner*. That creates an ordered contiguous block,
while all other pivots still fit the permitted lower-triangular compiler.

The second corner is an invertible diagonal matrix plus a rank-at-most-29
update. A further corner elimination exposes an 842-coordinate identity block.
The proof gives an explicit rational witness for the required nonzero minors,
then combines those minors with all earlier conditions using the finite
nonzero-polynomial argument. The old 25,142-coordinate middle block survives.

See [proof.tex](proof.tex) for the full argument, including the residual
subspaces, multiplicities, pivot ordering, simultaneous-basis conditions, and
stronger arbitrary-width interchange lemma. The actual producer, scalar
schedule, matching, rank sum and width are unchanged. The complex network
and dependency-path precision guard also remain unchanged.

## Exact result and validation

The bit saving becomes `40315/10^11 = 4.0315e-7`. The recursive block lengths
are 26,880, 25,200, 25,142, 900, 842, 840, and 782, with multiplicities in
[certificate.json](certificate.json). The new singleton count is exactly
`65,379,670,780,393,117,512`; the rank-mass identity is unchanged.

The certified bit moment is below one by more than `1.4e-12`.
Use the preceding dimension-28 complex saving `7/10^7`, choose
`epsilon=99999979/200000000`, and retain `c=1`, `beta=1/1000`,
`delta=1/10^10`, `zeta=1/10000`, and `C1=11999/10000`.
Set `lambda=tau+1/10^16`, `lambda'=tau+2/10^16`.
All 29 constraints and seven margins are strict; the final absorption gap is

    14957569250021/10^24 > 1.4957e-11.

The checks cover:

- Exact idempotency and permitted lower/lower pivot profiles for simultaneous
  controlled matrices over F_1009 at h=3,4,5. Both new factorization arguments
  are exercised; the stage-two data block is positive at h=4,5 and is left
  unbatched at h=3. The integer-lift parameters and pivot positions are saved.
- Independent exact rational reconstruction at h=3,4 for all five projector
  profiles, including the two retained profiles. Integer unimodular bases
  supply exact inverses; both lower-triangular factors are tracked and their
  product with each projector is checked against the claimed partial
  permutation over Q. Modular screening only selects nonzero minors; no
  modular equality substitutes for a rational identity. These witnesses
  are included in `certificate.json` and rerun by `make controlled-corners`.
- Source-hash verification of the unchanged PR #12 producer certificate,
  which contains the full h30 producer, star, dirty-scratch and matching checks.
- Exact logarithm, rank-mass, recursion-moment, and assembly arithmetic.
- Negative controls: removing *any* of the three new batches rejects this
  saving; an oversized exponent and zero absorption gap are also rejected.

The small matrix controls are finite examples, not a substitute for the
general rational existence proof. A full h30 controlled basis of dimension
27,000 is not materialized. The written proof supplies its existence.

The independent [manuscript patch](../../patches/controlled-corners.patch)
retains prior proofs, appends the stronger bit and layer interfaces, redirects
the downstream consumers, and updates the complete assembly and integer
rounding test. Bundled upstream is unchanged. The complete materialized manuscript also
compiles with Tectonic after guarding three inherited pdfLaTeX-only metadata
commands in the disposable build copy. Compilation is a source-integrity
check, not a mathematical proof check.

```sh
make controlled-corners
make verify
python3 research/controlled-corners/make_patch.py --materialize build/controlled-corners/manuscript
```

For review, focus on the stage-two residual tensor forms, the additional
nonzero-minor witnesses, and the physical pivot ordering after corner
elimination. Checking the numerical margins alone does not establish them.

## Attribution

The new corner analysis builds on icekylinx's controlled-basis and batching
work in PR #10, Zhihao Chen's ternary geometry and producer in PR #7, and the
dimension/matching/star work in PRs #9, #11, and #12. Earlier contributors and
the original OpenAI manuscript remain credited in NOTICE and the inherited
documents. The new analysis, controls, and integration were prepared with
substantial OpenAI Codex assistance at Rohan Arun's request. No worldwide
priority, formal verification, or OpenAI endorsement is claimed.
