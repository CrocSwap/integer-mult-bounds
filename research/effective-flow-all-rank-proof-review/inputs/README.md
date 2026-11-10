# An effective all-rank bound for the fixed-height direct flow

**Scoped analytic theorem; no new kappa.** This answers the effective-onset
question in [#6329](https://github.com/CrocSwap/integer-mult-bounds/pull/6329)
(`research/direct-flow-exponent-gate`). For its exact historical raw-p7 scalar
recurrence, retain the original height and every source, complement, boundary
exit and terminal leaf. Set

\[
s=\frac{99739}{100000},\qquad
G_0=2\cdot2^{10^{12}}+2,\qquad N_0=121\,5^{G_0}.
\]

Then, for **every integer \(n\ge1\)**,

\[
\boxed{L(n)\le N_0^{261/100000}\,n^{99739/100000}.}
\]

The predecessor already proved the upper exponent 0.99739 and identified the
limiting scalar exponent. Its local-limit argument supplied no effective onset
or majorant constant. This contribution supplies both. The threshold is
deliberately enormous: it proves effectivity, not practical finite-size savings,
and is not claimed to be optimal. Verification uses its exact symbolic expression;
it does not construct that integer or run a flow of that size.

## What closes the gap

[LOCAL_LIMIT.md](LOCAL_LIMIT.md) proves a uniform interval local-limit estimate
with explicit error O(1/log n) for the paid law. Compact Fourier interval
majorants and minorants reduce the problem to a bounded frequency range.
The elementary integer separation of powers of 2 and 3 supplies a quantitative
gap on that range. The new implication has no ineffective irrationality constant
or appeal to qualitative convergence. Atomic endpoints are covered.

[PROOF.md](PROOF.md) transfers this estimate through all mixed target/paid
layers and the full leaf tail. Working directly with source capacity minus
exit cost avoids dividing approximate limiting masses. The independently
checked limiting margin exceeds 40000; the explicit normalized error is below
1600. Conservation at exponent one gives L(n)<=n, which provides the
initial-range constant without enumerating the ranks below N_0.

The classical Beurling--Selberg interval approximation is a cited theorem,
with its precise normalization and an inspected primary-paper statement in
LOCAL_LIMIT.md. The universal conclusion is a written proof, not a finite
experiment or proof-assistant theorem. [REVIEW.md](REVIEW.md) records a separate
adversarial AI review and discloses the reviewer's earlier contribution.

## Reproduce and inspect

From the repository root with standard-library Python 3.12:

```sh
python3 -I -W error -B research/effective-direct-flow/verify.py
python3 -I -O -W error -B research/effective-direct-flow/verify.py
python3 -B scripts/research_package.py --package research/effective-direct-flow
python3 -I -W error -B research/effective-direct-flow/independent_checks.py
```

The two direct verifier commands print `PASS_EFFECTIVE_DIRECT_FLOW`. The
registered replay runs both modes, independent arithmetic controls, and source
transport checks. It authenticates five source files before
using their bytes and writes no generated artifacts. The standalone verifier
does not need Git or third-party libraries.

The new numerical checker imports none of the predecessor's numerical engine.
It uses integer endpoints on a 2^-128 grid, with directed rounding:

- logarithms use 80 positive atanh terms after reduction to [1,2], with
  tail 2z^161/[161(1-z^2)];
- exponentials use 48 Taylor terms after division by 16, a geometric bound
  on all omitted terms, and four squarings;
- exact mean-root endpoint signs, three atom masses, variance, third
  absolute moment, layer ratio and leaf decay are certified;
- 512 positive binomial terms give a **lower** bound for complete complement
  capacity. Omitting the remaining positive tail is valid for this one-sided
  gate. The computed interval for the truncated margin is
  `[47053.890913,47053.895405]`, so the full margin is above 40000;
- small rational comparisons check the symbolic onset and complete error
  budget without evaluating a huge power or a tiny floating exponential.

Ten complete histograms at depths 0 through 3 compare an ordered-word
decomposition with the authenticated original `Flow.merged()` implementation.
Controls reject an extra terminal cap, a missing mixed layer, an insufficient
onset, and invalid arithmetic domains. These finite checks corroborate the
source binding and numerical premises; they do not prove an all-size limit.
The separate exact arithmetic audit checks 3,969 signed interval pairs and
630 signed ceiling cases against independent rational extrema. Optional
`diagnostic.py` uses an independent 90-digit Decimal implementation and direct
pairwise capacity sums; its rounded output is explicitly outside acceptance.
Exact commands, environment and source-corruption checks are recorded in
[VALIDATION.json](VALIDATION.json).

## Sources, overlap and limitations

Canonical base: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
[SOURCES.json](SOURCES.json) binds the literal law, original flow and #6329
proof/README/task by SHA256 and Git blob. The current selected record and its
review are provenance, not inputs to this historical recurrence theorem.
The source law, flow and exact mirror decomposition remain predecessor work.
No frozen source is modified.

The final live overlap refresh (2026-11-04, 07:00--07:02 UTC) covered 663 open
PRs and 6,789 discussion records with complete remote pagination; targeted
all-state PR searches and direct reading
covered the relevant archived predecessors. Sparse local coverage was incomplete.
[#6128](https://github.com/CrocSwap/integer-mult-bounds/pull/6128) already gives
a conditional leaf-tail bound; it does not give this uniform interval estimate
or a complete recurrence onset. The stronger changed-height construction of
#4483 is a different recurrence and is not replaced here. This is a bounded
overlap survey, not a claim of literature-wide novelty.

The selected conditional P104 result remains **kappa = 0.003125804 (#6030)**.
Its construction and review were followed and its source-binding baseline
passed before this historical side question was selected. No selected cold
replay, native supplier, physical caller bill, ownership/erasure proof,
precision/tape proof, compiler-cost admission or exact integer-recovery theorem
is supplied. The five selected framework assumptions remain.

## Open next questions

- Can sharper frequency separation and a less conservative layer budget reduce
  the explicit onset enough for a useful finite-cost comparison? Start with
  certified bounds on the actual characteristic function over a chosen compact
  frequency interval. A rigorous stronger spectral estimate is the blocker.
- Can an all-size physical implementation fund the complete fixed-height
  recurrence? Start by binding its native operations and access, restoration
  and precision costs to the exact source flow. The scalar theorem alone does
  not supply that implementation or bill.

[TASK.json](TASK.json) records the changed scope and these questions. The
[coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19391591)
identifies this continuation of #6329's handoff.

## Credit

Prepared for **@alephnan with substantial OpenAI Codex assistance**, including
parallel mathematical derivation, exact code, writing and adversarial review.
No independent human acceptance or proof-kernel verification is claimed.

Credit zxv (#4436/#4483), Ryanson Jonathan / pinterbanget (#4459/#4467),
DLamdata (#6118), Nick Petalas (#6125/#6128), the full-flow exponent contribution
prepared for @CubeJerry (#6329), Cinna Davis / 1337isnot1337, Jacob Alan Sussman,
and the retained native/precision/analytic lineage. Beurling, Selberg and
Vaaler retain credit for the classical Fourier approximation; Laura Shou's
primary paper provides the inspected statement. New work is Apache-2.0.
