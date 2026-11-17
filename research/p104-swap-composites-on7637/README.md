# CONDITIONAL κ = 0.0037136318149: 20 swap-then-delete composites and an exact-zero-join fix on #7637 (premises: the same as #7637's)

**κ = 0.00371363181495617566871962832203768736…, ×1.00366339 over
[#7637](https://github.com/CrocSwap/integer-mult-bounds/pull/7637)** (κ 0.0037000770037809918…, the current frontier). The base word is
#7637's word, vendored unmodified as data (decompressed sha256 `8ab3d9db…83aa`). The official `evaluate_recursive_power` bracket
(256 bits) is [0.00371363181495, 0.00371363181496]. The claim 0.0037136318149 is a 13-decimal value below the exact crossing.

> **Premises: conditional on exactly #7637's.** Those are #7620's five framework assumptions (`native_all_columns`, `owned_erasure`,
> `compiler`, `precision_tape`, `analytic_recovery`) with its CLEAR reading, over #7637's 233 lifetimes plus one (below), and the
> changed entrance `initial[457] = 281`, which this word inherits unchanged. The common-U lifetime tariff affects bill totals only,
> not κ. If #7620's premises are refused, this word is void with #7637 and its lineage.

## The edits

Base: #7637's word (`data/base-7637-word.json.gz`, 78,596 events). New word: `data/word.json.gz`, 219,147 events. Every edit is listed in
base-word coordinates in [data/edits.json](data/edits.json): 20 composites C1–C20 on 40 helpers, one zero-join fix Z1 (468 interior
deletions, 397 insertions in all), then the re-derived hubs.

Each composite is two steps at one chart c:
1. **A SWAP-NULL relabel** of two helpers h1, h2 that are both born at {0} and both end at V. Exchanging their row trajectories after c is
   undone exactly by the hubs (the {0} prefix and the V mix), so on its own it changes no final row and no price. This is the swap law of
   our Lean package [#7634](https://github.com/CrocSwap/integer-mult-bounds/pull/7634) (`SwapNull`).
2. **Deletion of the recombined stay** at c. After the relabel, one of the two stays at c is no longer needed.

**Why the deletion is legal (the blank hand-off).** In every composite the receiver b is {0}-born and still *blank* when it reaches c. A
co-resident register a either hands its content to b there (`b += a`) and then only collects on its way to V, or has already spent its
content and idles to V. Deleting b's stop without the relabel fails, because b's stop carries that content flow. After the relabel, a
carries its own content along b's old tail, and b, still blank, takes a's collector tail straight from {0}: the copy `b += a` becomes a
rename, and b's stop at c disappears. The composites are our M4 mechanism from [#7630](https://github.com/CrocSwap/integer-mult-bounds/pull/7630)
and [#7636](https://github.com/CrocSwap/integer-mult-bounds/pull/7636), screened and stacked jointly on #7637's word.

| id | helpers h1, h2 | swap chart | stay deleted of | deletions / insertions | routes after |
|---|---|---|---|---|---|
| C1 | 408, 376 | 842 | 376 | 11 / 8 | 376: 3→127; 408: 3→37→463→473→762→842→967→227→127 |
| C2 | 396, 564 | 457 | 564 | 8 / 5 | 396: 3→90→448→457→895→127; 564: 3→127 |
| C3 | 398, 565 | 458 | 565 | 10 / 7 | 398: 3→60→446→458→896→127; 565: 3→127 |
| C4 | 1132, 338 | 819 | 338 | 10 / 9 | 1132: 3→62→425→432→819→940→137→127; 338: 3→76→394→127 |
| C5 | 274, 475 | 311 | 475 | 22 / 18 | 274: 3→93→311→320→839→966→127; 475: 3→815→938→192→127 |
| C6 | 276, 477 | 313 | 477 | 26 / 22 | 276: 3→52→313→322→847→976→127; 477: 3→554→946→194→127 |
| C7 | 278, 476 | 315 | 476 | 29 / 25 | 278: 3→29→315→321→526→975→158→127; 476: 3→822→945→210→127 |
| C8 | 290, 487 | 331 | 487 | 24 / 20 | 290: 3→50→331→338→525→974→127; 487: 3→817→940→192→127 |
| C9 | 292, 489 | 332 | 489 | 32 / 28 | 292: 3→95→332→340→841→968→218→127; 489: 3→555→948→194→127 |
| C10 | 294, 488 | 333 | 488 | 30 / 26 | 294: 3→51→333→339→840→967→206→127; 488: 3→823→947→210→127 |
| C11 | 295, 486 | 334 | 486 | 30 / 26 | 295: 3→51→334→337→846→973→158→127; 486: 3→816→939→212→127 |
| C12 | 332, 516 | 372 | 516 | 32 / 28 | 332: 3→102→372→381→893→1015→142→127; 516: 3→871→993→188→127 |
| C13 | 342, 524 | 389 | 524 | 23 / 19 | 342: 3→1→389→395→875→127; 524: 3→557→945→200→127 |
| C14 | 348, 528 | 390 | 528 | 28 / 24 | 348: 3→26→390→399→891→127; 528: 3→837→959→145→127 |
| C15 | 354, 535 | 405 | 535 | 26 / 22 | 354: 3→68→405→414→874→1000→127; 535: 3→821→938→184→127 |
| C16 | 366, 541 | 408 | 541 | 24 / 20 | 366: 3→27→408→420→890→1014→127; 541: 3→833→952→143→127 |
| C17 | 358, 536 | 409 | 536 | 23 / 20 | 358: 3→69→409→415→867→127; 536: 3→556→947→214→127 |
| C18 | 359, 534 | 410 | 534 | 28 / 24 | 359: 3→69→410→413→873→999→127; 534: 3→820→937→137→127 |
| C19 | 364, 540 | 410 | 540 | 24 / 20 | 364: 3→56→410→419→889→1013→127; 540: 3→832→951→162→127 |
| C20 | 392, 562 | 445 | 562 | 28 / 24 | 392: 3→89→445→455→1077→1007→127; 562: 3→848→975→147→127 |

**Joint hub re-settle.** Every ADD/SCALE at the {0} chart and at V is solved jointly and exactly, so all 1,569 final rows and end charts
equal #7637's. The word has hub events only of that kind (ADD/SCALE).

**Exact-zero joins.** #7637 has two owned fields that become exactly zero and are later refilled within one lifetime (fields 1568 and
1504; #7637's own conditions list this as a residual). The re-derived hubs have no join on 1568, and Z1 inserts a `CLEAR 1504; INIT 1504`
pair at chart 734 at the zero point of 1504, splitting that lifetime in two: 233 → 234 lifetimes, peak 50, the same 52 labels of 68, no owned
MOVE change. The new word has none; `check.py` detects them with its own exact replay and the Z1 control shows they return without it. Ten
ADDs in the word read an exact-zero owned source; this is harmless on the exact route.

## Price

Native paid delta per call {2:−16, 3:−5, 4:−16, 6:+14, 9:+3}; helper targets unchanged. Over 17 calls: paid
{2:−272, 3:−85, 4:−272, 6:+238, 9:+51}. Paid positions 109,023 → 108,683; rank surplus S = 1,424 unchanged.
Ordinary bill (17 calls, the repository `independent.py` formula with its call count set to 17): 789,821,188 for #7637 → 878,834,276 for
this word, below 10^9. Coefficients stay 5-smooth. The replayed grid moves from #7637's (2-adic exponent 25, odd lcm 1,125, 40 numerator
bits) to (21, 10,125, 30). Odd 3/5-smooth literal divisions go from 6,160 to 26,482; they enter only the ordinary bill and the verifier
line, not κ.
Official tools (`price.py`):
- `compare_recursive_invoices` against #7637 gives `uniformly_better`.
- `evaluate_recursive_power` (256 bits) gives `new_cost_lower` at C = 0.0037136318149 and `new_cost_higher` at C = 0.0037136318150.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-swap-composites-on7637
```
`VERIFY.json` registers nine commands:
- `core`: words, interior edit list, exact replay and legality of both words, rows, end charts and owned data, zero joins, routes,
  coefficients, invoice and κ.
- `certificates`: all 234 CLEAR certificates, with 2 rejecting controls.
- `controls`: 14 rejecting controls, 2 accepting, and the Z1 control.
- `columns1` to `columns4`: the column tests, in four parts.
- `price.py`.

**Census.** #7637 publishes no chart-pair census. The census here is every old- and new-route pair of the 40 changed helpers plus the 13
new MOVE pairs (223 pairs in all); `check.py` runs 512 forward and 512 adjoint Gaussian columns, signed Pauli action, absolute phase,
exact ascent rank and a wrong-phase rejection on each. It does not retest pairs this word leaves untouched.

Independently of the package, the word passed our exact pricer, an independent exact Fraction replay (all 1,569 rows equal #7637's, no
chart, ascent or ownership violation), a replay modulo 2^89−1 and 2^107−1, the repository's `independent.py` native audit (bad_inputs 0)
and caller identity, and `full_verify` of the 17-call route.

## Conditional premises and what is not rerun

The claim carries exactly #7637's premises (above), over 234 lifetimes with individually certified contents, and the signed #7113 caller
and BIT premise of the base. This package does not rerun #7620's full native/signed 17-stage application, catalogue, outer predicates or
precision/tape counts, nor #7637's own odd-grid and precision accounting: the replayed grid changes (above) and its effect on those
counts is not rechecked here. No upstream maintainer has reviewed the package.

## Credit

The base word is SYLforge's [#7637](https://github.com/CrocSwap/integer-mult-bounds/pull/7637), the H5B frame-restored construction,
vendored as data with its notices. Its credited lineage: Ali Romman's #7605, Clear1nsight's #7631/#7633/#7626, Rohan Arun's #7113 signed
caller, and the construction inside it from SYLforge's #7616/#7620 and our #7630. The relabel law and composites are ours:
[#7630](https://github.com/CrocSwap/integer-mult-bounds/pull/7630), [#7636](https://github.com/CrocSwap/integer-mult-bounds/pull/7636),
[#7634](https://github.com/CrocSwap/integer-mult-bounds/pull/7634). See [NOTICE](NOTICE).
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

- **More composites.** Only pure deletions after a single relabel were screened; further single hits conflicted in the joint stack.
  Making non-blank receivers blank first (with a κ-null gauge) is untested.
- **The premises.** A ruling on #7620's inherited assumptions and its CLEAR reading, and on the inherited entrance `initial[457] = 281`,
  decides #7620, #7637 and this word together.
- **Grid.** The replayed odd lcm grows from 1,125 to 10,125; whether #7620's precision/tape accounting absorbs it is not rechecked here.
