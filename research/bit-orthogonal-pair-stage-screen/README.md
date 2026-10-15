# Orthogonal-pair bit decoders in the frozen PR555 L3 family: a 9- and 11-stage screen

**Status: research note and scoped negative result — an exact finite census, real `gen_p3` builds of the
alternative reader sets, and an exactly priced screen of a decoder lever. No new κ and no new supplier; no
P(111−j) word with punctured duals is built.** The selected record (κ = 0.001672660197076918, complex-bound) and every existing
file are unchanged.

PR1084 (`research/bit-orthogonal-pair-decoders`) found that a decoder term whose reader line `a` and source line
`b` are both punctured and orthogonal costs 6 instead of 7, built a nine-pair system on 102 ports (cst 54, x = 9/17),
and noted two blockers: at nine stages the PR589 inventory R = 439 exceeds the whole-hosting wall `4v = 408`, and
the shipped PR589 puncture admits only one such pair (P110, cst 62). This package asks the next concrete question:

> Inside the construction family that actually produced the selected bit word — PR555's generator on PR543's frozen
> L3 plan — how many cost-6 terms can a legal reader set reach, and what would the resulting units be worth at the
> nine-stage template and at PR555's eleven-stage template, with every hosting wall and idle child priced exactly?

## Result

1. **P102 is unreachable in this family; the maximum is five cost-6 terms (P106, cst 58).**
   A pseudo-target reader line must be `gen_p3`-eligible; the frozen plan has 19 eligible lines, 18 outside the
   lines 0..7 that PR493's frame-zero isometry keeps live. Of the C(18,9) = 48,620 nine-subsets, 17,478 are
   admissible (eligible, outside 0..7, affinely independent in E8/2E8). Over them the number `j` of F2 duals that are
   root lines (each a cost-6 orthogonal pair) is distributed

   | j | 0 | 1 | 2 | 3 | 4 | 5 | 6–9 |
   |---|---:|---:|---:|---:|---:|---:|---:|
   | reader sets | 4,515 | 7,975 | 3,977 | 929 | 77 | 5 | 0 |

   Allowing line 7 (30,411 sets under the decoder rule alone) still gives j ≤ 5. The cap comes from the plan's
   eligible set, not from the decoder: PR1084's witness reaches j = 9 over all 120 lines. The shipped P has j = 1,
   with dual pair (66, 87), exactly PR1084's P110. Two independent implementations agree on 127 fields.
2. **Nine stages: only j ≤ 1 can be whole-hosted at R = 439, and it is worth +0.70%.** The no-bank wall `R ≤ 4v`
   needs v ≥ 110. P110 with PR589's own climbs for the removed line prices at
   `c = 1745584654912925918569/10^24` (+0.701363% over the selected bit c), below both thresholds below.
3. **Eleven stages host every P111…P102 unit whole** (wall `11R ≤ 64v`, so R ≤ 593 at v = 102). PR589 itself loses
   1.2966% there. If every reader set kept the shipped inventory R = 439, the five j = 5 sets would gain +1.939% to
   +1.972% and the 77 j = 4 sets +1.277% to +1.316%. That premise is false.
4. **The real generator charges each alternative reader set 7 to 33 more helpers, which removes every gain.**
   PR555's `choose.py` nominated the shipped P by minimising extra carriers, and that objective conflicts with
   orthogonal pairs. Running the unmodified `gen_p3` construction for each reader set (frozen plan, thirds seed 552,
   bounded receiver search) gives R(P) = 420 + 9 + x(P):

   | reader sets | built | R(P) | extra carriers + junk x |
   |---|---:|---:|---:|
   | shipped P (control) | 1 | 439 | 10 |
   | j = 5 | 5 / 5 | 458–471 | 29–42 |
   | j = 4 | 77 / 77 | 451–472 | 22–43 |
   | j = 3 | 281 / 929 | 448–462 | 19–33 |
   | j = 2 | 2,504 / 3,977 | 446–466 | 17–37 |

   All 83 shipped/j ≥ 4 words pass `gen_p3`'s internal asserts, its decoder-rows check and PR589's `xcheck_p.py`.
   - **Eleven stages, own R(P):** all 82 j ≥ 4 sets remain hostable, but they price between **−2.778% and −0.211%**
     against the selected bit c. None reaches either P104 threshold. The best set,
     P = [10, 15, 53, 56, 72, 96, 103, 106, 111] (j = 4, R = 451), would need 13 fewer helpers to reach PR1084's P104
     line and 18 fewer to reach the re-based one.
   - **Nine stages:** none of the 2,785 built j = 2/3 sets passes the no-bank wall. The lowest R is 446 for j = 2
     (wall 436) and 448 for j = 3 (wall 432). A quick screen with two fixed receiver choices over all 4,906 j = 2/3
     sets never went below R = 447.

   **Within this family the only hostable gain is the shipped P110 at nine stages (+0.70%), below both thresholds.**
   This is a finite, exact result for the frozen plan and a bounded receiver search, not an impossibility theorem for
   orthogonal-pair decoders.

## Thresholds used (exact, with their premises)

| Threshold | bit c | over selected | Source |
|---|---|---:|---|
| PR1084 recorded P104 complex b | 0.001756471346539970… | +1.329407% | `RESULTS.json` of PR1084, computed against the PR942-era complex profile |
| same +5.511% P104 complex gain applied to the current selected complex b | 0.001767798399743162… | +1.982856% | selected `ASSEMBLY.json` `complex_lower` × PR1084's ratio; a transfer premise, not a construction |
| bit headroom today | — | complex b is 3.46% below bit c | selected `ASSEMBLY.json` |

The bit side does not bind today, so none of these numbers can change κ by itself. They measure how much bit
headroom a decoder change would add if a complex improvement such as P104 landed.

## What is exact and what is a premise

Exact: the census (eligibility, affine independence, F2 duals, decoder identities and rational pairing ranks for
every set with j ≥ 4), the template parameters and walls, the certified slot-model idle optimum and window
max-flow, and every `c` as a certified lower bound on the 10⁻²⁴ grid of the pinned selected-record moment engine.
Positive controls reproduce PR589 at nine stages (`1733427039589844234749/10^24`), PR589 at eleven stages
(`855475950388791987811/(5·10^23)`) and PR555 at eleven stages (`427652201524503168379/(2.5·10^23)`).

Premises (none is verified here):

- **No word is built.** A unit's local profile is a proxy: PR589's per-register climbs with the dead lines' source and
  target climbs removed (`transplant`), with average climbs for lines that change role (`swap`), or the average line
  (`uniform`). An upper envelope over all three is reported.
- **Helper inventory.** R(P) comes from real `gen_p3` builds whose dead duals stay **live**. `gen_p3` does not model
  puncturing a non-reader line, so a true P(111−j) word could need a different count. The price shifts PR589's
  profile by (R − 439) average helper climb patterns (`helper_model='average-helper'`) rather than replaying each
  built word's own profile. The receiver search is a bounded group-wise descent, not a proof of minimal R; on the
  sets it ran it lowered R by only 0–4. A thirds-seed probe (scratch only) moved R by 1–5.
- **The rank-6 COPY.** Lowering a total's COPY child from 7 to 6 is PR1084's favorable price; the asymmetric copy from
  span b^⊥ to span a^⊥, its terminal frame and restoration are the open PR620 realization questions. A different
  climb shape for the affected total can move the result by about 0.03 percentage points either way.
- **Hosting** is PR589's slot model with PR442 windows. Nine-stage rows with j ≥ 2 fail the no-bank wall; their
  banked price is shown for reference only and is not counted as reaching a threshold.
- **Eleven stages** are priced with PR555's eleven-stage template. The selected assembly pins nine stages
  (`L=9, T=32, K=4, M=64`); an eleven-stage bit supplier needs a new assembly receipt, its halving depth 3 and
  larger invoice feed the precision/tape assumption, and the H1–H5 interface has to be rechecked.
- The census fixes the label-reader basis {λ_a}. Other reader bases on the same puncture can carry more cost-6 terms
  at a higher total cost (PR1084 section G); they are not censused.

## Reproduce

From the repository root, Python 3.10+ standard library only:

```sh
python3 -I -B research/bit-orthogonal-pair-stage-screen/census.py --check
python3 -I -B research/bit-orthogonal-pair-stage-screen/independent_census.py
python3 -I -B research/bit-orthogonal-pair-stage-screen/price.py
python3 -I -B research/bit-orthogonal-pair-stage-screen/screen.py --check
```

Expected final lines (about 6 s, 5 s, 10 s and 100 s):

```text
PASS_BIT_P102_ELIGIBLE_CENSUS eligible=19 admissible=17478 jmax=5 jdist=0:4515,1:7975,2:3977,3:929,4:77,5:5 ... checks=33
PASS_BIT_P102_INDEPENDENT_CENSUS: eligible 19 (18 outside 0..7); ... 127 fields agree
PASS_BIT_STAGE_PRICER controls=2 checks=24 rows=24 P110@9 c=1745584654912925918569/1000000000000000000000000 hostable=True nine-stage-unhostable=8
PASS_BIT_ORTHOGONAL_PAIR_STAGE_SCREEN ... | own_R: L11 j>=4 82/82 hostable, >=P104 0/82, >=rebased 0/82, best -0.211302% at R=451 ... checks=57
```

`screen.py` runs the census and its independent re-implementation, prices every row, and reads the build receipt
`CARRIERS.json.gz` (sha256 `8344b1a9…`). `--check` regenerates `SCREEN.json` and compares it byte for byte.

Regenerating the build receipt needs numpy, which the registered replay does not install. It took 1,142 s on four
workers with Python 3.14.4 and numpy 2.5.4 (the cp314 PyPI wheel, sha256 `d549420b…a3`):

```sh
PYTHONPATH=<numpy site> python3 -B research/bit-orthogonal-pair-stage-screen/carriers.py --workers 4 --budget 1140
```

The receipt is deterministic (compact sorted JSON, gzip with mtime 0); the coverage of the time-capped j = 2/3 tiers
depends on the budget and machine. Rebuilding the shipped set reproduces PR555's word byte for byte.

Controls include a non-eligible line, an affinely dependent set, a corrupted Gram entry, swapped partners, a line in
0..7, changed input pins and `-O`. The pricing controls are R = 445 > 4v at nine stages, a punctured line used as a
dead line, cost6 > j, a moved idle unit that breaks the rank-mass identity, c + 10⁻²⁴, and R ≠ 439 refused without
the explicit helper model.

## Open next questions

1. **A plan chosen for both objectives.** *Why:* the j ≤ 5 cap and the carrier penalty both come from the frozen
   PR543 plan and PR555's carrier-minimising nomination, while the decoder itself allows j = 9. *First step:* score
   j(P) and x(P) together over re-planned L3 keeper/thirds structures; at eleven stages a j = 5 set needs
   R ≲ 443 to clear PR1084's P104 line. *Blocked by:* a plan generator that targets eligibility of an orthogonal-pair
   system's reader lines, and `gen_p3` support for dead non-reader lines.
2. **The shipped P110 word itself.** *Why:* it is the only hostable gain found (+0.70% at nine stages with R = 439
   and 9 units of slack per replica). *First step:* delete line 87's source and target registers from the PR589 word,
   re-derive frames, and run `xcheck_p.py` and the nine-stage hosting audit. *Blocked by:* the asymmetric rank-6 COPY
   from span 87^⊥ to span 66^⊥ (PR620), its terminal frame and restoration, and the H1–H5 interface. It does not
   change κ unless the complex side first rises above the bit side.
3. **Built-word profiles.** *Why:* the own-R prices use an average-helper climb shift. *First step:* replay each built
   j ≥ 4 word's paid profile (the words are reproducible from `CARRIERS.json.gz`'s receivers) and transplant from it.
   *Blocked by:* nothing; the margin to the nearest threshold is at least 1.5 percentage points, so it is not expected
   to change the conclusion.

## Scope, overlap and credit

- **Base** `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. Sprint track 00–19 (bit supplier), OS
  assignment seed 4. No pinned coordination issue existed, so the claim was recorded locally. The catalogue's bit
  cards concern register models and the H2/K contract, so `TASK.json` declares a changed scope: this targets the bit
  decoder lever left open by PR1084.
- **Overlap.** The live overlap check at 22:30 UTC on 2026-10-14 covered 427 open PRs and 862 discussion records with
  complete pagination. It found no other P102/P110 realization or stage-count pricing. `format-limits-corrected`
  prices x = 54/102 only as a design-free format ceiling at s = 3. PR1023 and `bit589-width7-windows-seed72` price
  helper width, not the decoder.
- **Credit.** navinor (PR1084: orthogonal-pair decoders, P110 and the P104 threshold); eumemic (PR555 generator and the
  L3 punctured word; PR543 R420 L3 plan); DreamingOfClouds (PR545 punctured-star unit, PR589 tuned word and pricing,
  PR595 deficit identity and hosting wall, PR717); PR442 and PR510 hosting and nine-stage chain; PR493 eleven-stage
  chain; Joel Pulikkan / GamingPuzzled (PR620 Theorem C label-decoder model and realization questions); Russell
  Seligmann and Cody Harris (PR757, PR761 P111 floors); themilkman216 (PR968 P104 complex budget).
- Prepared for Sagar Thakrar with substantial AI assistance (Claude Code, Anthropic). Subagents wrote the census,
  pricer and screen; a separate agent re-implemented the census before reading it; another adversarially reviewed
  the pricing; the main session reran every command. Apache-2.0.
