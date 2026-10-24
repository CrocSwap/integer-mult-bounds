# Independent check of #4629's re-padding ledger and price (no new κ)

**Adversarial audit. No new κ is claimed.** Target: PR #4629 (DaysSky,
`research/complex-ambient-quotient`, head `2cf7d081118f6f702aa317816d231b41ce073579`),
which claims the complex supplier rises 0.003020165977 → 0.015637149091 by
quotienting the PR4470 complex word by `span{153}` and re-padding 213 helpers to the
full ambient.

**Question answered.** Does the paid ledger #4629 prices follow from its written
artifact? Is the 213-helper re-padding priced as described? Does it legitimately
carry the block-8 charge? This package rebuilds the ledger and the price
independently and compares them with the PR's stated numbers.

## Result

The ledger and the price **reproduce**. Three of the PR's descriptive claims **do not**.
The block-8 charge rests on an axis that only padding uses.

| quantity | #4629 states | this check |
|---|---|---|
| helper profile | `{3:2,6:7,7:47,8:139,9:213}` | same |
| paid profile | `{1:2177,2:424,3:389,4:147,5:50,8:8}` | same (independent walk = shipped `literal_replay`, both directions) |
| local deficit / surplus (block 8) | 1,688 / 3,776 | same |
| complex κ (block 8) | 0.015637149091 | **0.015637149090882** (50-digit Decimal) |
| frontier κ (calibration) | 0.003020165977 | 0.003020165977016 |
| re-pad cost | "one rank in the paid profile and one in the helper profile" **each** | **+1 for 187 helpers and +5 for 26 helpers**. Paid delta `{1:187, 5:26}`; the 26 were width-4 helpers whose dim-4 finals were replaced by F₂⁹ |
| surplus at block 7 | −1,264 | **−256** (the same invoice; frontier at block 7: −3,280). Still inadmissible |
| "213 cold full-ended helpers the contract requires" | restored | PR4470's own word has **326** and **fails** the shipped `embedded_cache_roles` (213 is the raw THREE-base canonical count). Only 187 of #4629's 213 are among PR4470's 326; the other 26 were width-4 helpers |

The deficit is unchanged, as #4629 states: each padded helper's extra rank is both
paid and credited. Padding **lowers** the price. The same written word with the 213
finals left at their quotient images prices at **0.016571333483**. petalas's #4627
1-helper-padded 153 ledger reproduces at 0.016567169219, and the 511 ledger at
0.012091850234. **No accounting asymmetry favours #4629's number.**

**The ninth axis is used only by padding.** In the written word, the only frame
containing a vector ≥ 256 is F₂⁹ itself. It occurs in 0 scalar, warp or centre
events and in 0 main finals. It is reached only by the final climbs of the 213
re-padded helpers. All other frames together span 8 dimensions. Every non-padded
role's start and final frame equals φ₁₅₃ of PR4470's frame, and the scalar/warp
program is exactly φ₁₅₃ of PR4470's.

#4629's own verifier certifies block 8 by `ambient == block + 1`. Under that rule,
block 8 is certified only by the padded helpers' inert final climbs; without
padding the word is ambient-8, and at block 7 the ledger is inadmissible (−256).
Under the other reading, where the block is fixed by the controller and not by the
word, padding is unnecessary and costs κ (0.016571 → 0.015637). In neither reading
does the padding do physical work. Which reading is the supplier contract is a
maintainer question (see Open next questions).

As corroboration on the written artifact (not the base word), 56 of 112 ports have
their X entrance inside their Y terminal (q = 0). This matches rohanarun's per-port
count for kernel 153 on #4633/#4596.

## Method and independence

`verify.py` does **not** import #4629's `build.py`, `verify.py` or `scan_kernels.py`.

- **Inputs.** It reads #4629's two written artifacts, vendored here byte-for-byte.
  Their Git blobs and SHA-256 are checked against head `2cf7d081`, as listed in
  `SOURCES.json`. The PR4470 base word comes from main's shipped
  `research/joint-helper-lattice/native_joint.py` `construct()`.
- **Written here.** GF(2) spans, φ₁₅₃ images of every base frame, and padded-role
  detection. Also an independent paid-rank walk: minimal nested climbs into every
  scalar/warp frame, centres charged |Δdim|, then climbs to the finals; recorded
  climbs are ignored. Also helper widths, the invoice at block 7 and 8, and the
  two-constraint screen (tail 1/5, cutoff 20, γ 0.97) in 50-digit `Decimal` with
  160-step bisection.
- **Shipped evaluators used (disclosed).** `--replay` also runs main's
  `native.synthesize` + `native_extensions.literal_replay` + `verify_buffers` on the
  written word. It requires 632/632 endpoints exact, C cleared, and the shipped
  paid profile equal to the independent walk, in both directions. The shipped
  `embedded_cache_roles` is called on both words.
- **Rejection controls (5/5 must fail).**
  - A paid ledger with the re-pad charged as "+1 each" does not match the written ledger.
  - A one-bit-tampered artifact fails its pin.
  - A word with one main final moved off φ(base) is rejected.
  - A perturbed paid profile (one 5 → 4) does not reproduce κ.
  - The block-7 surplus is negative.

## Reproduce

From the repository root (Python 3.12, stdlib only, about 50 s):

```sh
python3.12 -B research/pr4629-repad-ledger-audit/verify.py --replay
python3.12 scripts/research_package.py --package research/pr4629-repad-ledger-audit
```

It ends with `PASS_PR4629_REPAD_LEDGER_AUDIT`.

## Not covered

- Whether output charts or the per-port split (#4604, rohanarun's comment on
  #4596) are part of the supplier contract. This is not ruled on here.
- The controller-level surplus identity for mixed main widths
  (`query-thinned-controllers/controller.py:152`) and any outer κ.
- The other 31 replay-valid kernels, `scan_kernels.py`, and FOUR-base/FOUR-extra.
- Where #4629's −1,264 comes from. No file in the PR computes it; the PR's own
  `invoice()` at `block=7` returns −256.

## Open next questions

1. **Is the tensor block a property of the word (ambient = block + 1) or fixed by the controller?**
   - *Why it matters:* it decides between "inadmissible at block 7 (−256)" and
     "padding unnecessary, 0.016571".
   - *First step:* find where `query-thinned-controllers` and `joint-helper-lattice`
     obtain the block, and write it as a word check.
   - *Blocked by:* a maintainer ruling on the supplier contract.
2. **Does `embedded_cache_roles`' 213 bind PR4470-derived words at all?**
   - *Why it matters:* PR4470 itself has 326 and fails it, yet #4629 pads to
     exactly 213 to pass it.
   - *First step:* trace its caller at `native_extensions.py:203`.

Structured versions are in `TASK.json`.

## Credit

- The construction, re-padding and invoice are DaysSky's (#4596, #4629).
- The kernel census and the 153/511 ledgers are petalas's (#4627).
- The endpoint-chart question is pinterbanget's (#4604). The per-port contract
  audit is rohanarun's (comment on #4596; #4633).
- The base word is Cinna Davis's (#4441, #4447, #4470), on zxv's native supplier.

Prepared by lm1909 with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
