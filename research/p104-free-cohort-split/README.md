# Three-role neutral cohort: conditional κ .003638315828316

This exact successor of [#7112](https://github.com/CrocSwap/integer-mult-bounds/pull/7112) improves its conditional claim by **.000000898708375**, to **.003638315828316**. It also exceeds the concurrent caller improvement [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113), .00363797977, by **.000000336058316**. Three coordinated contact-free MOVE retimings expose one additional independent helper split, rank 9 → rank 3 + rank 6. Each retimed role preserves its complete paid histogram; all 690 new scalar instructions are charged. The source and caller are pinned to #7112, head `e59520bb11b0df5ac33f062f55397d78a491e7af`.

## Construction and changed premise

Earlier retiming searches admitted at most two moved roles. This construction needs three roles together at chart 734, dimension 3, before zero-based source event 37929:

| Role | Original MOVE event | Path | Placement relative to split |
|---|---:|---|---|
| 1463 | 38145 | 3 → 734 | before |
| 1243 | 37722 | 734 → 738 | after |
| 509 | 39073 | 3 → 734 | before |

All three original and replacement paths cost exactly one rank 3 MOVE. `construct.prepare` checks the entire contact-free interval, every removed event, absence of scalar reads/writes and INIT/CLEAR, nested frames, ownership flags, and exact nonzero paid-rank Counter equality for each role. It moves each role into the common cut chart and restores its required outgoing chart before its next contact. Distinct roles have no shared scalar operation in these intervals, so the relocations commute. The verifier rejects omission of each of the three retimings individually. A synthetic rank 1+8 → rank 3+6 retiming is rejected even though both paths have the same rank sum: paid histograms must agree.

At the aligned cut, with helper pivot 509,

```
a = e1463 - 2 e509,
b = -e1463/3 - 2 e1243/3 - 2 e509/3 + 2 e806/3.
```

The complete exact boundary vectors c and d are in `WITNESS.json`. They use only independent helpers whose initial/final charts are (3,127), dimensions (0,9). For the entire prefix P and suffix S, including all public and owned coefficients, `split.check_cut` proves aP=c, Sb=d and ab=cd=1. Every cut operand is at 734. No input helper is assumed zero or identified with another helper.

The credited independent-helper construction chooses G with row 509=c and Gd=e509, and J with row 509=a and Jb=e509. It emits G⁻¹, the prepared prefix, J, the renamed J⁻¹ and suffix, then the renamed G. Pivot 509 now ends at 734; fresh independent helper 1484 starts at 734 and ends at 127. G isolates the retained arbitrary input at the cut. Substituting the new arbitrary input changes the suffix along b, hence the final boundary along d, which G isolates to the renamed output. All other outputs agree. Owned labels shift by one and retain all logical lifetimes. The existing smooth-swap basis rule from #7112 is retained; here both pivot entries are already nonzero.

G has 340 instructions and J has 5. Including inverses adds **686 ADDs and 4 SCALEs**, with no net change in MOVE count. The emitted word has 72,833 events, 1,485 public fields and 1,085 independent helpers. Owned labels 51, lifetimes 54, peak 43, rises 23 and ascent mass 56 remain unchanged. Canonical word SHA256 is `ae30929ff3b5f6b49a5edac78e2164acfbf809113d0b9f03249ef940dd7b2491`.

## Complete invoice and bounds

Per LOCAL, ΔP={} and ΔT={3:+1,6:+1,9:−1}. Across 18 LOCALs, the concave margin improves by **18(3^p+6^p−9^p)>0** for every 0<p<1. The complete invoice has 117,148 paid and 23,482 productive requests, surplus 1,520 and no empty-root credit. Its fixed-invoice crossing is enclosed independently by

```
(0.00363831582831655596050722548632002,
 0.00363831582831655596050722548632003).
```

The claim is `909578957079/250000000000000`; the source invoice rejects it. More digits of this crossing would not be a new construction. The unchanged BIT pin is .00376669, leaving .000128374171684 between it and the claim; this is parameter headroom, not a realizable further improvement. Compiler gap 10⁻¹⁷, logarithm power 2233, H=16480300000000000000000, all 54 strict and 4 functional outer gates pass.

The full ordinary bound is **849,950,512 <10^9**, margin 150,049,488, including every added scalar operation, input conversion, helper boundary, inherited second LAMBDA charge, signed-route charge 1,168,000 and recomputed B-scalar surcharge 784,256. These are the retained source cost units; a literal physical-machine upper-cost application requires its own bridge.

The fresh exact prefix/pre-product denominator-LCM derivation gives odd scale 1125 and fractional height 24. A separate fixed-grid integer engine checks every division and endpoint. Scale 375 and fractional height 23 reject. Maximum scaled mass is 1630273820634225/16384. Signed caller precision is recomputed: context height 450, mass exponent 671, c=1342, and 19,530 distinct stage/helper inputs. The native alphabet remains the original 2,3,5-smooth scalar alphabet and magnitude bound.

## Evidence and reproduction

```
python3 -I -B research/p104-free-cohort-split/verify.py
python3.12 -B scripts/research_package.py --package research/p104-free-cohort-split
```

Expected final line: `PASS_P104_FREE_COHORT_SPLIT 909578957079/250000000000000`.

The standard-library standalone verifier needs no network or Git. It authenticates all 19 exact predecessor files by SHA256 and Git blob, follows the frozen nested manifests, reconstructs #7108 through #7112, and compares the entire source word and invoice. It then regenerates this candidate, verifies whole-cut identities, complete arbitrary-input forward and adjoint maps, the exact signed caller, both rational price engines, all ordinary and precision charges, BIT source binding and outer gates. The three relevant chart maps (3,734),(734,127),(3,127) are checked on all 512 Gaussian columns including absolute phase; these pairs already exist in the source catalogue. Full width 512 native physical and signed caller route replays also pass. Rejection controls cover each missing retiming, contacts, missing old moves, duplicate roles, changed paid histogram, incorrect prefix/suffix/chart/fresh frame, missing corrections, lower grids and global phase.

Every receipt field is compared against `RESULT.json`. `--out UNUSED_PATH` generates a receipt; `--skip-physical` is diagnostic only. Optimized Python is rejected because pinned engines contain assertions. `VALIDATION.md`, `REPLAY.txt` and `ENVIRONMENT.json` record actual runs, separately from inherited checks. This is source-aware reuse of attributed engines, not independent human or formal-kernel review.

`discover.py`, `SEARCH.txt` and `DISCOVERY.json` preserve the bounded nomination search: 10,537 neutral windows, 23,070 exact prefix systems, 3,789 saved states, one nonzero pairing and accepted nomination. The verifier does not trust search scores. This is not an optimality proof or a complete search over scalar basis choices. Earlier local negative rounds are described in the canonical Discussion and remain local-only; they are not repackaged as evidence here.

## Remaining obligations and credit

Canonical main `e54523517d0f03e58352e647c403a5af3e525a57` selects #7000, κ=.00363005817. Its pinned [application review](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md), including the BIT ambient 134 repair, does not automatically admit this changed native supplier and signed caller. The five framework assumptions remain `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. Complete changed-source occurrence/storage/root and physical upper-cost application, independent review and maintainer acceptance remain obligations. Owned CLEAR may erase nonzero correlated contents under its inherited assumption. Finite checks and source-unit bounds do not constitute a complete multiplication theorem. No selected record or frozen input is changed.

Prepared for dillona with substantial OpenAI Codex assistance; no subagents. Apache-2.0. Credit **Ali Romman** for independent-helper/basis methods; **Jerry Chen / CubeJerry** for paid retiming, counted inventories, shared-wire composition, caller/BIT and precision engines; **DreamingOfClouds** for the native chain; **ToikY** for #7003/#7004 and #7108/#7109/#7110 signed caller and native sources; #7105/#7107/#7112 for the preceding source-bound edits and smooth basis routine; and all retained notices. **Rohan Arun's #7113** independently improves the caller and is acknowledged as concurrent work, not imported here. The new contribution is the three-role neutral cohort, exact rank 3+6 witness and complete source-bound checks.

## Open next questions

- Compose this exact native split with #7113's 17-stage signed caller. Pin both heads, regenerate the complete invoice, physical binding, ordinary costs, precision and application; do not add decimal gains. Composition is unverified here.
- Transfer the selected application proof to this changed supplier, including actual occurrence allocation, owned storage, root widths and physical upper-cost constants. The five framework assumptions remain.

`TASK.json` records relevance, first steps and blockers. The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521) records scope and checkpoints.
