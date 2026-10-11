# E8 bit word with source carriers: R = 489 on a D4 quad skeleton

A new E8 bit supplier (h = 8, v = 120, 9 retained totals) with **489 helpers**; the hub's best bit word had 715 (#463).
Its source registers also carry partial sums, which is PR #425's mutable-basis interface applied on the bit side
(the review point below). Priced by the hub's eleven-stage whole-residual hosted bit pipeline (#445 geometry,
#472 emitter, audit and finite invoice, #442 hosting, #315 engines):

| quantity | value |
|---|---|
| bit c, eleven stages, eight pooled replicas, every residual whole and hosted (10^-24 grid) | `391360506745414227149/250000000000000000000000` = 0.001565442026981656908596 |
| same pipeline on #472's R715 word (control, reproduced exactly) | 0.001293771240692396056124 |
| five-stage saving from #370's checker (no envelope) | 0.00127887365561970469 |

The bit side no longer binds: c is 20.6% above the best whole-residual bit supplier (#483, 0.0012982901) and 18.0%
above the largest whole-residual complex b. Through the six-level, 47-inequality outer assembly (#434/#315, as in
#472), every composition is complex-bound:

| complex supplier (cited from its receipt, not rebuilt) | complex b | κ |
|---|---|---|
| **#484** (DreamingOfClouds; draft, conditional on its Lemmas A and G) | `663394767670133/5·10^17` = 0.001326789535 | **`662515748707749/500000000000000000` = 0.001325031497415498** |
| #471 (Dugongue), the complex supplier of #473, #478 and #483 | `1305231506267591/10^18` | `260706019542937/200000000000000000` = 0.001303530097714685 |
| #458 (chafreaky), the complex supplier of #472 | `1297203880559577927527/10^24` | `323880830669511/250000000000000000` = 0.001295523322678044 |

The best whole-residual κ on the hub when this was prepared is #483's 0.001296606691405309, bit-bound with
#471's complex b. With #484's supplier this word gives +2.19% over it; with #471's supplier, +0.53%. Each κ above
is the complex cap of its supplier: any bit word with c above b gives the same value. The #484 value inherits that
draft's two lemmas as review points.

Information only, not a claim: #448's cross-copy complex supplier (b = `718766148669433/5·10^17` = 0.001437532)
would give κ = `358867191156973/250000000000000000` = 0.001435468764627892, complex-bound. That number rests on
#448's cross-family residual split, which #451 disputes (research/cross-family-residual-obstruction; the author's
rebuttal is on #451's thread).

## The word

`data/bit/bitE8mut-r489.json.gz` is rebuilt byte-for-byte by `code/skeleton/gen.py` from the frozen plan
`data/skeleton/plan-skB.json` and the D4 partition `data/skeleton/d4part-pairs.json`. Format: bitE8/1 (#370), with
gates allowed to write source registers.

- **Partition.** The 120 root lines split into 10 D4 sub-root systems (12 lines each), in 5 orthogonally
  complementary pairs. Each block has 3 orthogonal 4-frames: 30 four-frames and 180 cells (a cell is a pair of lines
  in one 4-frame; it spans 2 dimensions and contains exactly those 2 lines).
- **Sources.** A fixed matching splits each 4-frame into two matching cells and four cross cells. A source stays in
  its matching cell and two carriers copy it at its line into its two cross cells: three branches per source. Three
  is the minimum: s⊥ (an E7) is a spherical 4-design, so two hyperplane sections do not cover it (the carrier bound of
  #463).
- **Cells and quads.** Each cell delivers its sum to its two quads and keeps single lines: a cross cell uses its
  two branches and one empty register, a matching cell its two sources and two empty registers. A quad is a
  4-dimensional D4 frame made of 6 cells from 6 blocks (3 complementary block pairs); there are 60. A butterfly on
  the 6 delivered cell sums gives 6 outputs S + u_H, one per D6 the quad feeds (S is the quad's sum; u_H is the
  owner D6's d-cell, its Q-cell or both).
- **Tops.** Target t is reached through the three D6 frames {t, e}⊥ (e the other lines of its 4-frame). At the D6
  shared with its matching partner it reads two quad outputs and a Q-delivery; at t⊥ it reads one register from each
  of its two other D6 frames.
- **Q-nodes (the source writes).** For each block, its 12 sources (all sitting in matching cells) undergo one
  invertible F2 transform at the block's D4 frame. It produces the 6 Q-deliveries read by the complementary block's
  targets and 6 leftovers. These are the only gates that write sources: 577 gates, all at block D4 frames, each
  reading one other source; 117 of the 120 source registers are written.
- **Totals and cleanup.** The 9 decoder totals of #370 are collected at the full frame on 9 fresh registers from
  registers that are no longer needed. The cleanup C is the literal reverse of every source and helper gate of A and
  B at the full frame, so every source and helper is restored; D is #370's frame-zero dirt compensation.
- **Count.** 120 sources, 240 carriers, 240 cell registers, 9 totals: R = 489. Local paid histogram
  {1:1200, 2:1440, 4:180, 6:120, 8:18}, rank mass 5664 = 8R + 72 + 240·7.

## Review point: source registers as gate destinations

PR #370's independent checker contains one assertion this word does not meet: "x registers are never destinations".
PR #425's scalar-interface lemma (Zhihao Chen) shows the assertion is a sufficient condition, not a necessary one:
if no target feeds a source or helper register, the raw word is z' = U z, y' = V y + J x + K s; a frame-zero
preconditioner (here D) and U⁻¹ at the common full frame after the last climb (here C) give exactly
(x, s, y) → (x, s, y + x). #425 uses this with sources carrying packets below the full frame on the complex side;
#433 (icekylinx) already wrote source rows on the bit side, at the full frame only (559 XORs in its R758 word).
This word writes sources below the full frame (block D4 frames), as #425's packets do.

What the package checks about it:

- `code/bit/independent/relax.py` generates the relaxed checker from #370's pinned file by removing exactly that
  assertion (it counts such gates instead). Every other check is unchanged, including the exact F2 replay on all
  729 columns, which requires every source to end holding exactly its own column. The stock file is run as well and
  must refuse the word with "x register written".
- `interface.py` checks the lemma's hypotheses directly: no target feeds a source or helper; D writes only targets
  from helpers at frame zero; C acts only at the full frame and is the literal reverse of the source and helper gates
  of A and B; B writes only targets.
- Mutants aimed at the interface are rejected: dropping a source cleanup gate, corrupting a packet that targets
  read while keeping every source restored, leaving a source unrestored, moving a source write below the source's
  frame, dropping a source write (relaxed checker); the same three record-level mutants against both official
  column checkers; two F2-neutral edits in which a target feeds a source or a helper (accepted by the F2 checker,
  rejected by `interface.py`).
- The official cohort checkers (`legality_h`, `columns_h`, `columns_k`) treat every register alike and accept the
  word unchanged. In the hub's bit address realization (#472's PROOF.md, "Shared physical labels") the pullback of
  D_F on F2-valued streams does not depend on whether a register is called a source, helper or target, so the
  common-frame argument covers source registers as it covers helpers. The mutable-basis realization stays a listed
  conditional interface, as in #472, #473 and #478.

## Checks (`verify.sh`)

0. Manifest; 50 vendored files byte-identical to their PRs (git blob ids, `SOURCE-pr*.json`); the adapted hub
   files equal #472's files plus the listed edits (`code/eleven/adapt.py --check`); cited complex b values equal
   their PRs' own receipts (`code/cited.py`).
1. The word rebuilt from the frozen plan equals the shipped word.
2. #370's checker: the stock file refuses; the relaxed copy passes (legality, exact F2 on 729 columns, 671 frames
   with positive Gram determinants, primes {2}, five-stage price); `interface.py`; 11 word-level mutants and 2
   hypothesis controls.
3. Official checkers: legality (NCOPY = 9; 33,990 ADDs, rank mass 5,664), five-stage formal columns (969 columns,
   prefix payload 100 bits < 104), eleven-stage formal columns (#381's `columns_k`, KPAIRS = 5: 1,689 columns,
   2,880 bridge additions, 24/24 omitted-bridge controls), the KPAIRS = 2 regression, #370's 6 record-level
   mutants and 3 mutable-source record mutants.
4. Exact Gram determinants and prime witnesses on all 672 frames.
5. Eleven-stage whole-residual hosting: #386 nine-stage geometry (parent of the audit), #445 eleven-stage geometry,
   #472's emitter and independent audit with R = 489 (all 43,032 helper residuals hosted whole on idle data
   families of the eight pooled replicas, 6,579 unbanked scalar columns restored, 24 omitted bridge shears
   rejected, 22 template mutations rejected, 3,252,216 renamed instructions), then #472's bit invoice and both
   moment engines, and the outer assembly per cited supplier (#484, #471, #458; #448 for information).
6. Controls through the unmodified hub files: #472's R715 word reproduces c = 0.001293771240692396056124 and,
   with #458's b, κ = 0.001292099559442278 (#472's published values); #445's R740 word through #445's emitter
   reproduces c = 0.001264963576077378514188, and #451's R740 rank149 word through #451's emitter (byte-identical to
   #445's) reproduces c = 0.001267536342017397153864.
7. Every number above against `EXPECTED.json`.

```sh
python -m pip install -r research/e8-bit-carrier-skeleton/requirements.txt
bash research/e8-bit-carrier-skeleton/verify.sh /absolute/new/output
```

Python 3.11+, numpy, sympy, a C++17 compiler (`CXX`) and Boost headers (`BOOST_INCLUDE`). About 2 minutes.

## Finite invoice

The physical prefix (#472's chronological cancellation-free bound over physical families) is 2,119 bits, charged
at 2,176; the three-level coefficient is 6,411 bits, charged at 6,464. Both are larger than #472's (804/2,496)
because the Q-node butterflies and the totals have long XOR chains; they stay below the hub's precedent (#473
charges 3,456 and 10,304) and only enter the finite cutoffs. Maximum child 56, three-level halving, row
coefficient 19,431 < 20,161 (#445's orthogonal-cover bound).

## Bounds for this family (analysis, not run by verify.sh)

R ≥ 120 for any design (top arrivals; carriers). For tops through consistent D6 triples, at least 14 registers per
4-frame at dimension 6, so R ≥ 300. With three branches per source on this partition, at least 3 registers per cell
(540 at dimension 2), so R ≥ 420. With the totals in phase A, a brute force over all d-parity patterns needs 4
single-line registers per 4-frame for the targets' parities, and each block's Q-node needs all 4 lines of each of
its 4-frames; no register can do both, and 3-register cells leave only 6 single-line registers per 4-frame. That
gives 20 registers per 4-frame, 600 in all, so R ≥ 480. R = 480 is reached with the totals on leftover registers,
but its prefix payload is 129 bits > 104; nine fresh total registers give R = 489 at 100 bits.

## Scope

Conditional on every interface #472's eleven-stage composition retains: the all-size bit/Gaussian compiler,
mutable-basis and target-label realization, whole-call correlated-helper hosting (#442), compressed windows,
restored work, common grid and tape, precision, row and analytic contracts. Complex savings are cited from their
PRs' receipts, not rebuilt; the primary κ also rests on #484's Lemmas A and G. The hosting selection is a frozen nomination of #442's integer programme
(`discovery/host_select.py`) and the plan a CP-SAT nomination (`discovery/plan.py`); neither is claimed optimal.
No unconditional multiplication theorem, Lean proof or κ = 1 result is claimed.

## Credits

Zhihao Chen (#425: the mutable-basis interface lemma; #386: nine-stage geometry); DreamingOfClouds (#463: the
carrier bound; #315: moment engines; #484: the primary complex supplier); DaysSky (#442: idle-axis hosting; #381: `columns_k`); chafreaky (#445, #451,
#472: eleven-stage geometry, row bound, pooled whole hosting, emitter, audit and invoice; #443's bank routes;
#458's complex supplier); Dylan Crow (#370: bitE8/1 format, independent checker, generalised official checkers);
icekylinx (#433: source rows written on the bit side); Dugongue (#471: complex supplier; #483: current
whole-residual frontier); higherbeing (#448, information only); eumemic (#436: R740 and the provenance tooling); Jacob Sussman (the E8 unit). Details in
`NOTICE.md`.

Prepared by eumemic with substantial Anthropic Claude assistance. Apache-2.0 (`LICENSE`).
