# Structural bit-word research candidate

This source variant changes the PR325 pair-module coordinate labeling, cube orientation, and reuse assignment. It is a candidate predecessor for fresh downstream optimization. Its complete standalone finite construction has bit root `771005354683887/10^18` and κ `385205681529931/(5*10^17)`. The inherited complex supplier remains unchanged and the bit binds. These values are below the separate downstream successor; downstream gains must be rediscovered and cannot be added to this result.

The strict verification entry point is `python -B verify.py --output /new/proof`. The two-pass producer is `python -B bitword/producer/regenerate_structural.py . --work /new/build`. The original one-pass `regenerate.py` belongs to the inherited PR325 source and does not reproduce this variant. No Lean run is claimed. All all-size and analytic interfaces remain conditional.

`STRUCTURAL-PROVENANCE.json` records the source pins and exploratory selection. The source tree contains no Python caches; strict verification reads this source and pins every file. Prepared with OpenAI Codex assistance, retaining all upstream attribution and notices.

The documentation below and in the other inherited Markdown files describes the original PR325 package. Its old numerical claims are historical context, not the numbers of this variant.

---

κ = 7.69684039383334e-4

# A re-searched p = 10 bit word in the five-stage completed banks

A conditional finite construction with **κ = 384842019691667/(5·10¹⁷) ≈ 7.69684039383334 × 10⁻⁴**.

This package is PR #315's p = 10 package (`research/five-stage-p10-banks/`, κ = 7.64230861320245e-4) with a new
bit word. #315 ported #285's gen5 five-stage package to cube size **p = 10**: h = 20 coordinates, v = 960 sources,
five-stage width m = 5h = 100 and 100-coordinate stage-private completed banks. Everything after the bit word is
#315's, with the new word's values re-pinned in `word-pins.json`. That covers the five-stage layout, the banks, the
source527 verification chain, the centre-sharing complex supplier and the assembly. #315's package is unchanged.

The bit word comes from eumemic's PR168 generator with #276's gen4 changes, as in #315. Four things changed:

1. **Pair module** (`pm_p10.json`). It was re-annealed from #315's module on the exact one-instance compile cost
   with five-stage weights, plus a penalty λ·debt (λ = 150 to 300). The debt counts module additions that do not
   donate to a carrier arc. The module still has 36 inputs, the centre root and 273 additions. Its carrier arcs
   go from 178 to 181, so its debt goes from 95 to 92.
2. **Local design** (`local_design_p10.json`). #315 reused a design found on the p = 12 word. This one was
   re-searched at p = 10 by 1-move steepest ascent from #315's design, scored on the five-stage virtual price of
   the full word. It reached a local optimum after two moves, which changed 2 of the 12 plane recipes. With shared
   subtrees a cube now takes 24 local additions instead of 27. It has 8 local carrier arcs instead of 11, so the
   per-cube debt stays 16.
3. **Balanced cube orientation** (`cube_orient_p10.json`, new). The generator used sorted cubes: position 0 of
   {a < b < c} is a. Coordinate 0 was therefore position 0 in C(9,2) = 36 cubes, and coordinate 9 in none.
   Position 0 carries face0, the 4-target root that the reuse-recipient gauges are tied to. Under that imbalance a
   maximum reuse matching covered only 892 of the 960 recipient candidates. The new file lists each cube as a
   cyclic rotation of its sorted triple. Position 0 is the element after the largest cyclic gap (mod 10). In the
   one rotation orbit with gaps 4, 4, 2, position 0 is the element between the two gaps of 4. The rule is
   rotation-equivariant, so every coordinate is position 0 (and 1, and 2) in exactly 12 cubes. Orientation alone
   did not change the virtual word's R or its five-stage virtual price in the research runs. What it changes is
   which donors fit which recipients. The generator reads the file when it is present; otherwise it uses sorted
   cubes.
4. **Tiered reuse matching** (`make_physical.py`). Hopcroft–Karp returns some maximum matching regardless of
   donor value, and with the balanced orientation it prefers low-dimension donors. The first-order five-stage
   value of a reuse pair grows with the donor's end-frame dimension e. The producer therefore admits donors in
   tiers of decreasing e. After each tier it runs Kuhn augmenting paths from the current matching until none is
   left among the donors admitted so far. An augmenting path never unmatches a matched donor, so this is the
   greedy algorithm on the transversal matroid of donors. For every threshold t, as many donors with e ≥ t are
   matched as any matching allows. The last tier is the whole graph, run until no augmenting path remains, so the
   result is a maximum matching (Berge). Here it matches all 960 recipients, against #315's 890 pairs; with
   60·width already divisible by m, no pair is dropped.

The physical layer still follows PR200's rules; only the choice among maximum matchings changed. The compensated
reuse recipients are the rank h − 3 = 17 gauges. All 960 are matched, so the 1,200 independent entrances all have
rank 16.

**Complex supplier of this variant, and the bit binds.** The complex program is #315's centre-sharing complex
word, unchanged. It was built with PR #304's recipe on three query modules and a patched graph builder (local
research, not published; see `inputs/complex/centre-mw/NOTICE`). Its coarse saving is b = 7.72714351296671e-4,
certified with the 10⁻¹⁶ bad-class fallback like the bit side; the inherited no-fallback convention gives
7.72714354722691e-4. The bit's certified coarse saving, 7.70276910e-4, is 0.32% below the complex leaf cap
(1 − β)·b. The bit therefore binds, and the assembly path is #285's: the bit is fed at its certified root. (With
PR #304's complex supplier, 7.6358781017907e-4, the bit root would exceed the cap. `math_check.py` also handles
that complex-bound case, but this package does not exercise it.)

The complex program itself is checked in every run by Jacob Sussman's reference checker `gx.check1` with the
exact scalar identity, and by his `gxcore` mirror of the two Lean checks. No Lean check of the program is pinned
here.

**Lean (run locally; not pinned here).** With Jacob Sussman's wht-power-saving-lean at f010392c (Lean v4.34.1,
Mathlib d13f23b) and his unchanged generator `tools/gx/regen_check.py`, the exact gcert pinned here (sha256
bb0499ab342aee3594904fc1cd72b9ff496cdb315d0840f4cdd5ba64ef794d34) was compiled to Lean and kernel-checked:
`OAI.PowerSaving.WHT.wht_main_block_B2Gcc27x`, the Walsh–Hadamard corollary at exponent 1 − 7727140/10¹⁰.
`tools/Compare.lean` passed against a challenge file that differs from Sussman's ChallengeB2Gp193x only in the
exponent and names; the axioms are propext, Classical.choice and Quot.sound. The official comparator and a clean
build from nothing were not run. This covers only the complex program's Walsh–Hadamard saving, not the bit word,
the bootstrap, the κ assembly or the retained integer-multiplication interfaces. Because the bit binds, κ is
unchanged if b is replaced by the Lean exponent.

| one invocation | gen5 (#285), p = 12, m = 120 | #315, p = 10, m = 100 | this package, p = 10, m = 100 |
| --- | ---: | ---: | ---: |
| virtual auxiliary roles | 17,292 | 9,120 | **9,060** |
| compensated reuse pairs | 1,406 | 890 | **960** |
| independent dirty registers R | 15,886 | 8,230 | **8,100** |
| formal F₂ columns 2v + R | 19,406 | 10,150 | 10,020 |
| independent entrances (ranks) | 2,554 (17, 18, 20, 21) | 1,270 (16, 17) | 1,200 (16) |
| banks per stage | 164,934 | 86,526 | 85,680 |
| literal stock, 60 replicas | 1,247,070 | 663,030 | 658,800 |
| normalized stock / deficit | 249,414 / 52,800 | 132,606 / 24,480 | 131,760 / 24,480 |
| bit coarse saving (certified root) | 7.43337804075788e-4 | 7.64815357146385e-4 | **7.70276909563042e-4** |
| complex coarse saving | 7.47454944651775e-4 (PR193, no fallback) | 7.72714351296671e-4 (centre-sharing, with fallback) | 7.72714351296671e-4 (unchanged) |
| binding side | bit | bit | **bit** |
| κ | 7.42785663120535e-4 | 7.64230861320245e-4 | **7.69684039383334e-4** |

Run with Python 3.12 or newer (tested on 3.12 and 3.14), sympy 1.14.0 and assertions enabled:

```sh
python3 -m pip install -r requirements.txt
python3 -B verify.py --output /tmp/p10b-five-stage-verification
```

The output directory must be new and outside this immutable package. Verification takes about three to five
minutes, uses no network and runs no producer. It performs these checks:

- the PR168-v4 checker on the virtual word, with its five mutation controls;
- PR200's physical-word proof as PR200 ran it: frames, handoffs, the physical row and all-column replays, with
  4 adverse controls;
- the retained source527 scalar program on all 10,020 formal F₂ columns, both integer decoder signs and 11
  corruptions;
- the physical event emitter, parity fusion and five-stage global lowering;
- exact h = 20/m = 100 geometry, including two distinct actual entrance bases of rank 16, the only entrance rank
  of this word;
- exact determinants for 12,760 bases;
- 120 bank charts and all 2,430,000 bank assignments;
- the centre-sharing complex program: `gx.check1` with the exact scalar identity and the `gxcore` mirror, with a
  flipped-sign control;
- the complex supplier (labels, scalars, splice and finite guard), and both rational moment engines on the bit
  and complex profiles, each with the fallback;
- the assembly (bit-bound here) with all 47 outer inequalities, and the finite bill.

`bitword/producer/regenerate.py` rebuilds the five pinned bit-word files from the generator and the two
physical-layer producers, and checks them byte for byte. This is provenance only, not part of the proof.
`discovery/REPIN.md` describes how to re-pin the package mechanically for new module, design or orientation data.

The result is conditional on the retained all-size compiler, common weighted chart, restored rows, selectors,
tape routing, prime supply, precision/recovery, complex symbolic correctness and analytic reduction. The included
finite checks do not replace those hypotheses. See:

- `PROOF.md` for the verification chain and what changed from p = 12 and from #315;
- `BANK-PROOF.md` for the banks;
- `bitword/README.md` for the bit word;
- `NOTICE.md` for attribution.
