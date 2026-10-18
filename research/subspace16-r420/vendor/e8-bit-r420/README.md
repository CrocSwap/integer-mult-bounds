# E8 bit word with R = 420: keepers read by targets, then rewritten in phase B

A new E8 bit supplier (h = 8, v = 120, 9 retained totals) with **420 helpers**. The best bit words on the hub so far
have 480 (#503, priced at nine stages by #510) and 489 (#493). Priced by two hub pipelines, unchanged:

| quantity | value |
|---|---|
| **bit c, nine stages** (#510's chain: #463 template, 32 replicas, #442 hosting; 10^-24 grid) | `413456747036699736067/250000000000000000000000` = **0.001653826988146798944268** |
| bit c, eleven stages (#493's chain: #445 geometry, #472 emitter, audit and invoice, #442 hosting) | `82015816228313440961/50000000000000000000000` = 0.00164031632456626881922 |
| #510's R480 word, nine stages (control, reproduced exactly) | 0.001587447106092548137108 |
| #493's R489 word, eleven stages (control, reproduced exactly) | 0.001565442026981656908596 |

The nine-stage c is 4.18% above #510's and 4.01% above the largest cited complex b (#535). Through #493's six-level,
47-inequality outer assembly (the one #510 uses; it also reproduces #535's own κ values, see the controls), both
compositions are complex-bound:

| complex supplier (cited from its receipt, not rebuilt) | complex b | κ | binds |
|---|---|---|---|
| **#535** (icekylinx; open PR) | `1589991533606044174031/10^24` = 0.001589991533606044 | **`793733736881443/500000000000000000` = 0.001587467473762886** | complex |
| #531 (icekylinx; merged, main's headline) | `304013615566499291631/(2·10^23)` = 0.001520068077832496 | `1517760977820331/10^18` = 0.001517760977820331 | complex |

With #535's complex b, #535's own κ is 0.001584931111785787, bound by #510's bit c. This word lifts the bit side above
#535's b, so κ becomes #535's complex cap: **+0.160% over #535**. With #531's b nothing changes, because that
composition was already complex-bound. Each κ above is the same with the nine-stage and with the eleven-stage c, since
the complex side binds in both.

## The word

`data/bitE8mut-r420.json.gz` is rebuilt byte for byte by `code/gen_l3.py` from the frozen plan `data/plan-l3.json`
(`NODEOPT=2000 python -I code/gen_l3.py data/plan-l3.json OUT 0 dead last`, about 2 s). The generator imports #493's
skeleton modules (`e8.py`, `geom.py`, `gen.py`, `wordkit.py`) and D4 partition from `research/e8-bit-carrier-skeleton`
on main. Format: bitE8/1 (#370), with gates allowed to write source registers.

- **Partition.** As in #493: the 120 root lines split into 10 D4 sub-root systems in 5 orthogonally complementary
  pairs, giving 30 orthogonal 4-frames, 180 cells (a cell is a pair of lines in one 4-frame), 60 D4 quads and 180 D6
  frames (one per cell, its orthogonal complement).
- **Three registers per cell.** Each source has one home cell in its 4-frame, and two carriers copy it into its other
  two cells. Every cell holds exactly three registers: its two line branches and one empty register. That is
  120 sources + 240 carriers + 180 empty registers = 540 = 3 × 180, so R = 420.
- **Phase A.** Each cell delivers two sums to its two quads and keeps one line (its keeper). Each quad applies a
  butterfly to its six cell sums. Each D6 node forms o1 = o1 + o2 (o2 is left dead). A D6 that does not host a
  Q-delivery takes a free keeper k of the complementary block as its third register (k = k + o1). The 9 decoder
  totals of #370 are formed at the full frame on dead registers, hosted by the last eligible register (#503's rule).
- **Phase B, d-single reads (120 gates).** Each target t picks a partner x(t) in its 4-frame Φ and reads, at the cell
  C_t = Φ − {t, x(t)}, the keeper of C_t. That keeper is the source register of one line of C_t, and it supplies
  t's single d-line.
- **Phase B, block nodes (477 gates).** The 12 keepers that targets read at the dual cells of a block are exactly
  the 12 sources of that block. After the reads they climb to the block's D4 frame. One invertible F2 transform per
  block turns them into the 12 Q-deliveries for the targets of the complementary block.
- **Phase B, needers (120 gates).** Each Q-delivery register climbs to its target's host D6 and adds that D6's o1
  register, which makes it the target's needer for that D6.
- **Phase B, tops (120 gates).** Each target climbs from its cell straight to t⊥ and reads its three needers there,
  one per D6 of its triple {t, e}⊥.
- **Cleanup.** C is the literal reverse, at the full frame, of all 2,661 gates with a source or helper destination
  (2,064 in phase A and 597 in phase B). D is #370's frame-zero dirt compensation (120 gates).

Frame paths: a source goes line → cell → block D4 → host D6 → t⊥ → full; a target goes 0 → cell → t⊥. The local
paid histogram is {1: 1320, 2: 1440, 4: 60, 5: 120, 8: 9}, with rank mass 5,112.

**Why this is below #493's family bound of 480.** #493's README argued R ≥ 480 for its family with phase-A totals:
the targets' d-line parities need 4 single-line registers per 4-frame, each block's Q-node needs all 4 lines of each
4-frame, and no register can serve both roles. DreamingOfClouds' LP in #493's thread reaches 480 under three stated
hypotheses: three branches per source, two transverse quads per cell, and matching-cell sources feeding the block
frame. This word keeps the first two and drops the third. The block node runs in phase B, after the targets' d-single
reads, so the same source register first gives a target its d-line at its cell and then feeds the block node. R = 420
equals #493's other family bound: at least three registers per cell with three branches per source on this
partition.

## Review point: source registers rewritten in phase B, after targets read them

In #493 every source write is in phase A, and #493's `interface.py` checks, among the hypotheses of #425's lemma,
that phase B writes only targets. This word has 597 phase-B gates that write source registers:

- 477 block-node gates (source ← source, at block D4 frames);
- 120 needer gates (source ← helper, at D6 frames), so helper contents enter source registers until the cleanup.

Each of these 597 gates writes a register that a target has already read in phase B, and 120 target reads at t⊥
read registers rewritten earlier in phase B. No target ever feeds a source or helper.

**Lemma (scalar interface with interleaved z-gates).** Write z = (x, s) for the sources and the arbitrary helper
contents, and y for the targets. Suppose:

- (H1) no gate whose destination is a z register reads a target;
- (H2) every gate of D is at frame 0, writes a target and reads only helpers, and D runs first;
- (H3) A writes only z registers; the scatter adds retained helper registers to targets; B is any interleaving of
  z-gates (z destination, z sources) and target gates (target destination, any sources);
- (H4) C is the list of z-destination gates of A and B in reverse order, each at the full frame, and every z register
  ends at the full frame;
- (H5) the target-to-target part V of the raw word W0 = (A, scatter, B) is the identity.

Then W0 acts as (z, y) ↦ (U z, y + J x + K s); C acts as (z, y) ↦ (U⁻¹ z, y); and with D acting as y ↦ y + N s
the whole word acts as (x, s, y) ↦ (x, s, y + J x + (K + N) s) over F2. It equals (x, s, y + x) exactly when
J = I and N = K. D is legal at frame 0 and C is legal at the full frame.

*Proof.* By induction over the gates of W0, the state has the form z_k = U_k z_0 and y_k = V_k y_0 + M_k z_0. A
z-gate reads only z registers (H1, H3), so it multiplies U_k on the left by an elementary transvection and leaves y
alone. A target gate replaces y_k by P y_k + Q z_k for a transvection P on y and a matrix Q, which gives
V_{k+1} = P V_k and M_{k+1} = P M_k + Q U_k. The scatter is a sequence of such target gates. The form is preserved
whatever the order of z-gates and target gates, so W0 = (U, V, M) with U the product of the z-gates' transvections in
order and M = [J K]. By (H4), C applies the same transvections in reverse order. Over F2 each is an involution (the
destination is never among its own sources), so C = U⁻¹, and C touches no target. D adds N s to y and reads only
helpers. Composing, with V = I by (H5), gives the stated map. For the frames: D runs before any climb, and targets and
helpers start at frame 0, so every register D touches stands at frame 0. After B every z register can climb to the
full frame, because every frame lies inside the full frame. C uses only z registers there, and their final frames are
full, so no descent is needed. Targets reach t⊥ in B and C does not touch them. ∎

**Relation to #425.** #425's lemma (Zhihao Chen, `PROOF.txt` section 3) has one structural hypothesis, "No target may
feed a z register", and states the block form for "the raw A/center/B word" as a whole. Its cleanup executes U⁻¹ "by
reversing and inverting the non-target gates", wherever they occur. Nothing in it requires the z-gates to precede the
target reads, and its lift to exact labels is an induction "through the actual stream", which does not depend on the
order. The interleaving here is therefore covered by #425's statement as written. #493's check (4) is a property of
the R489 word, not a hypothesis of #425's lemma. This package restates the lemma with the interleaving explicit and
checks each hypothesis on the word; reviewers should confirm this reading of #425. On the bit side, the realization
is the role-independent common-label pullback of #472's PROOF.md ("Shared physical labels"), written out in #535's
`PR510-MUTABLE-SOURCE-CARRYOVER.md`: an XOR between two registers at the same label commutes with that label,
whatever the registers are called and whether or not a source still holds its input, and nested climbs compose. That
argument is also order-independent. The mutable-basis realization remains a listed conditional interface, as in
#472, #493 and #510.

What the package checks about it:

- `code/xcheck.py` (independent; reads only the word) checks the labels (an even unimodular lattice of rank 8, every
  frame closed), frame legality, and the exact F2 map on all 660 columns with the helper contents as symbolic inputs.
  It then evaluates (H1)-(H5) one by one and decomposes the conclusion on W0: z' = U z, J = I, K equals D's helper
  sets, and C applied to the W0 outputs restores every source and helper.
- `code/mutants.py`: nine negative controls are rejected, each for the intended reason:
  1. a target feeds a source (F2-neutral pair; rejected by (H1));
  2. a target feeds a helper (F2-neutral pair; rejected by (H1));
  3. a dropped cleanup gate;
  4. a corrupted phase-B source write, with the cleanup changed the same way so every source is still restored;
  5. a phase-B source write moved down to the source's own line frame;
  6. a single target-to-target read (V ≠ I);
  7. a corrupted frame-0 preconditioner;
  8. a phase-B source write moved before the target read of that register (frame nesting forbids it);
  9. a cleanup gate moved off the full frame.

  One positive control, a cancelled pair of target-to-target reads (V = I), is accepted.
- #370's stock checker refuses the word ("x register written"). #493's relaxed copy passes it; it replays all 660
  columns exactly. #493's `interface.py` refuses it at its check (4), as expected.
- The official cohort checkers treat every register alike and accept the word. Three record-level mutants aimed at
  the phase-B source writes are rejected by the five-, nine- and eleven-stage column checkers, with legality
  unchanged: a dropped cleanup ADD, a corrupted phase-B source write with the cleanup adjusted, and an unrestored
  source.
- The same `xcheck.py` accepts #493's R489 and #503's R480 words, where B writes only targets (the lemma's special
  case).

## Checks (`verify.sh`)

```sh
python -m pip install -r research/e8-bit-r420/requirements.txt
bash research/e8-bit-r420/verify.sh /absolute/new/output
```

Python 3.11+ with numpy, sympy and scipy, a C++17 compiler (`CXX`) and Boost headers (`BOOST_INCLUDE`). About 2
minutes on 4 cores (the two controls run in the background).

0. Manifest. Then provenance: 19 files vendored from #510 and 2 receipts from #535, each checked by git blob id.
   Main's files are pinned by sha256: #493's package through its own `MANIFEST.sha256`, and #531's receipt. Every
   cited b is checked against its PR's receipt.
1. The word rebuilt from the frozen plan equals the shipped word.
2. `xcheck.py`, the 9 + 1 mutation controls, and `xcheck.py` on the R489 and R480 words.
3. #370's stock checker refuses; #493's relaxed checker passes (legality, exact F2 on 660 columns, 671 frames with
   positive Gram determinants, primes {2}); #493's `interface.py` refuses at check (4).
4. Official checkers:
   - legality at NCOPY = 9 (29,874 records, 26,916 common-frame ADDs, rank mass 5,112);
   - five-stage formal columns (900 columns, prefix payload 100 bits < 104);
   - nine-stage formal columns (#381's `columns_k`, KPAIRS = 4): 1,380 columns, 18/18 omitted-bridge controls;
   - eleven-stage formal columns (KPAIRS = 5): 1,620 columns, 24/24 omitted-bridge controls;
   - the KPAIRS = 2 regression; #370's 6 record-level mutants; the 3 phase-B record-level mutants;
   - exact Gram determinants and prime witnesses on all 672 frames.
5. Nine-stage price (#510's chain, unchanged): #463's template (4,740 unbanked scalar columns restored, 18 omitted
   bridge shears rejected) and parent audit (17 template mutations rejected). #442's hosting programme rediscovers
   the frozen selection `data/selection9-r420.json`, and all 120,960 helper residuals are hosted whole with 0 banks.
   The hosted audit replays 8,603,712 renamed instructions and rejects 16 mutations. Then #510's nine-stage invoice:
   prefix 189 bits (charged 192), two-level coefficient 416 bits (charged 512), maximum child 42 with
   2 · 42² < 64², row coefficient 18,355. Both moment engines and the outer assembly per supplier follow.
6. Eleven-stage price (#493's chain). `code/adapt11.py` makes the six edits #503 makes for R480 to #493's audit files,
   here for R = 420. #442's programme rediscovers `data/hosting11-r420.json`, and all 36,960 residuals are hosted
   whole with no banks. The independent audit replays 2,628,912 instructions and rejects 22 template mutations. The
   invoice: physical prefix 4,710 bits (charged 4,736), three-level coefficient 14,185 bits (charged 14,208), maximum
   child 56, row coefficient 19,431 < 20,161.
7. Controls, through the same files:
   - #510's R480 word at nine stages reproduces #510's c and κ values, and with #535's b it gives #535's κ
     0.001584931111785787 (bit-bound);
   - #493's R489 word at eleven stages, through #493's files unmodified, reproduces #493's c, κ values and emitted
     program hash. With #531's b it gives #531's κ 0.001517760977820331 (complex-bound). With #535's b it gives the
     κ of #535's own #493 control, 0.001562995248531632 (bit-bound).
8. Every number above against `EXPECTED.json` and the cited receipts.

The eleven-stage invoice is larger than #493's (2,176 and 6,464 charged bits) and than the hub's earlier precedent
(#473: 3,456 and 10,304). These bits enter only the finite cutoffs of the outer assembly, whose 47 strict inequalities
pass. The headline uses the nine-stage price, whose invoice (189 and 416 bits) is close to #510's (193 and 425 bits).

## Retained assumptions

- Every interface that #472's and #510's compositions retain: the all-size bit/Gaussian compiler; the mutable-basis
  and target-label realization (the review point above); whole-call correlated-helper hosting (#442); compressed
  windows and restored work; the common grid and tape, precision, row and analytic contracts.
- Complex savings are cited from their PRs' receipts, not rebuilt. #535 is an open PR, so the primary κ is
  conditional on its review as well.
- The plan is a CP-SAT nomination (`discovery/`). The hosting selections are nominations of #442's integer
  programme. None of them is claimed optimal.
- This is a conditional finite construction, not a Lean proof.

## Files

- `code/gen_l3.py`, `code/nodeopt.py`, `code/planio.py`: the generator that built the word, with package import
  paths. `nodeopt.py` realizes each block node by randomized LU and keeps the realization with the smallest
  cancellation-free norm under the literal cleanup (2,000 tries per block).
- `code/xcheck.py`, `code/mutants.py`, `code/mutrec_b.py`: the independent replay and interface audit, the word-level
  mutation controls, and the record-level phase-B mutants.
- `code/adapt11.py`: R-specific copies of #493's eleven-stage audit files.
- `code/provenance.py`, `code/cited.py`, `code/summary.py`: pins, receipts and the final comparison.
- `data/`: the word, plan, frozen hosting selections, cited b (`complex-b.json`) and #535's receipts.
- `vendor/pr510/`: #510's nine-stage chain as run by its `verify.py`, including the files it vendors from #463, #443,
  #442 and #315, and #503's R480 word as carried by #510's branch (`SOURCE-pr510.json`).
- `discovery/` (not run by `verify.sh`): the CP-SAT plan model and its iteration (needs ortools).
- `DEPENDS.json`: the files of main this package uses, pinned.
