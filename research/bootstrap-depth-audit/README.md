# Five bootstrap levels cannot certify PR387's grid point

**Status: scoped mathematical audit / negative result; no new κ.**

PR [#387](https://github.com/CrocSwap/integer-mult-bounds/pull/387) shows that
five bootstrap levels miss its published κ at its chosen slack values.
This audit strengthens that statement: **five levels miss the same κ even
if each level chooses its saving independently and every choice is allowed
to approach the certified coarse-root upper endpoint**. The initial ordinary
supplier and the recurrence accounting must remain fixed.

This is supporting evidence, not a counterexample or a correction to #387.
It does not say that the underlying algorithms cannot admit a sharper analysis.
The reviewed frontier at this audit's base remains #626/#543 with conditional
κ = 0.001635527380375392; #387 is an older, unreviewed PR in the central ledger.

## Exact result

The starting saving is `a0 = 384599/10^10`. The inherited coarse-root interval is

```
l = 999632926176283805553 / 10^24
u = 999632926176283805554 / 10^24.
```

For the retained recurrence `a_j = s_j(1-s_j+a_(j-1))`, permit independent
`0 < s_j < u`, relaxing all other supplier restrictions. Its optimistic
outer-margin ceiling after j levels is

```
A_j = u - u^j(u-a0),       C_j = A_j/(1+A_j).
```

At the published `κ = 0.000998634658090835`:

| Quantity | Exact enclosure, in units of 10^-18 |
| --- | --- |
| κ minus the optimistic five-level ceiling | between 0.546434 and 0.546435 |
| Published six-level compact margin minus κ | between 0.406 and 0.407 |

Thus no depth from zero through five certifies κ using this accounting.
The published six-level compact margin clears it. This audit recomputes that
margin and the recurrence gaps, but does not replay all 47 assembly constraints.

There is also a useful boundary on the conclusion. With five levels, even the
optimistic coarse endpoint requires an initial saving **greater than**
`0.0005869935357213085...` to reach this grid point. The pinned initial saving is
only `0.0000384599`. A control using `a0 = 0.0006 < u` escapes the five-level
exclusion, so this is not a ceiling for arbitrary starting suppliers.

[PROOF.md](PROOF.md) gives the uniform argument for independently chosen
per-level savings. [EXPECTED.json](EXPECTED.json) records exact rational
ceilings, the positive integer exclusion cross-product, the threshold and
all control outcomes.

## Reproduce

From the repository root, with Python 3.9+ and no external packages:

```sh
python3 -I -B -O research/bootstrap-depth-audit/verify.py --check research/bootstrap-depth-audit/EXPECTED.json
```

Expected output:

```
PASS_SCOPED_BOOTSTRAP_DEPTH_AUDIT; depths 0..5 excluded; six-round margin admitted; 9 controls rejected
```

The verifier imports no predecessor implementation. It compares a rational
recurrence with an unreduced integer closed form, checks the pinned witness's
chain and compact margin, and checks every retained source's SHA256 and Git
blob ID. Rejections include deleting the quadratic cost term, an off-by-one
depth, a stronger starting supplier, a lowered target, the next target grid,
zero assembly slack, non-strict grid rounding and a changed source byte.
Checks remain active under optimized Python. `--output /fresh/path.json`
generates the full deterministic receipt without overwriting an existing file.

`python3 -I -B -O research/bootstrap-depth-audit/test_audit.py` runs seven
additional tests, including 1,536 varying-savings schedules evaluated directly
from the three cost exponents, 2,400 strict-grid boundary cases and subprocess
rejections of altered source and receipt files. The finite schedules check
implementation behavior; they do not prove the continuous envelope theorem.

## Dependencies and limits

- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Audited #387 head: `d9fb9410b1ae6f6ada376a1e7fd12bc176e476ea`.
- [SOURCE.json](SOURCE.json) pins the retained proof, root receipt, witness,
  parameter file, implementation excerpts, PR185 proof and notices. Files
  under `sources/` are immutable audit inputs, not a runnable copy of #387.
- The coarse-root interval is **inherited** from #387's two-engine moment
  receipt. This audit checks its source binding and sign consistency; it does
  not recompute either moment engine or the underlying paid profile.
- The completed ordinary leaf, dirty restoration, spectators, row borrowing,
  finite cutoffs, fixed tapes, compiler and analytic interfaces are inherited.
  No supplier, paid primitive, frame or selected certificate changes.
- The uniform ceiling follows from the written algebra. Finite replay supports
  the arithmetic and failure detection; it is not a formal theorem proof,
  an impossibility result for other recurrences or a new multiplication bound.

The assignment seed is **73**, drawn with operating-system randomness. Three
candidate audits, the local claim and stopping rule are in [CLAIM.json](CLAIM.json).
No pinned sprint issue existed; issue #650 requests a discussion channel and
was not used as a reservation thread. The initial 567-open-PR snapshot through
#748 showed no matching depth audit. Pending #657 studies the much broader
square-root assembly wall; #668/#736 concern cyclic-inverse arithmetic; #684
audits a different Gaussian domain. None is a dependency of this result.
The refresh also read [ahrazzle's PR387 review](https://github.com/CrocSwap/integer-mult-bounds/pull/387#pullrequestreview-5482278356):
its reported independent three-round replay and closed-form assembly
comparisons are prior evidence. This audit
adds the uniform five-round exclusion with independently variable savings and
the starting-supplier threshold, rather than repeating those replays.

See [VALIDATION.md](VALIDATION.md) for executed checks and their limits.

## Attribution

Rohan Arun supplied #185's completed-leaf bootstrap and #387's fixed-depth
extension, exact witness and coarse-root refinement. #387 builds on Chafik
Boukhalfa's #384 supplier package and its credited contributors. The retained
outer formula is eumemic's #315 engine, following icekylinx's #144 constraints,
Zhihao Chen's #23 and the RaD/hipotures balanced-prefix work. Original source
notices and the Apache-2.0 license are preserved under `sources/pr387/`.
Credit ahrazzle's earlier independent PR387 assembly replay and structural
comparison; this package does not certify that review's full-suite claims.

This scoped audit is by Isaac Grannis (@BagMan9), with substantial OpenAI Codex
assistance in the mathematics, implementation, checking and writing. No separate
human or delegated-agent review is claimed. New material is Apache-2.0; no
literature-priority claim is made.
