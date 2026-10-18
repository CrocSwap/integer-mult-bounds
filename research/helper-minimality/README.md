# Helper minimality (no κ claim): the shipped helper layers of the #656 / #799 words are minimal for their op multiset

This package states and checks lower bounds on the helper layers of the shipped frontier words: the 11 eight-line S1 blocks,
the S3/S4 packet copies, the 12 bridges and the entering/holder copies, the 8 cut centres, and the pre-read targets. It continues
`research/format-limits-2` (#717) and the merged #595 (rows F3-F5 of #717 record the same facts as value and exact-replay statements; the
rows here are the frame-side bounds with their scope). **It makes no κ claim and ships no word.** Each result comes with its scope and
hypotheses. Each is marked:

- **CHECKED**: `verify.sh` recomputes it from the files listed below (exact arithmetic; solver results are solver statuses, no certificate file is shipped);
- **ARGUED**: a proof or file:line argument in this README; the quoted lines and every quantity the argument uses are themselves checked where stated;
- **RECORDED**: the result of an earlier run that `verify.sh` does not repeat. The card note is shipped under `evidence/`; the row says what is not reproduced.

A row marked CHECKED for only part of its statement says which part.

```sh
python3 -m pip install -r research/helper-minimality/requirements.txt
bash research/helper-minimality/verify.sh /fresh/output/dir            # from a checkout or `git archive` of the whole repository
HM_FULL=1 bash research/helper-minimality/verify.sh /fresh/output/dir   # also regenerates the 36,501-pair pre-read table (about 5 min)
```

Python ≥ 3.11; `requirements.txt` pins numpy and ortools (CP-SAT); set `PYTHON` to choose the interpreter. Step 0 checks the package
against `MANIFEST.sha256` (every file) and every vendored input against its pin in `SOURCES.json` (git blob ids of PR files, sha256 and
content hashes published by the PRs for the rebuilt words), and stops with exit 1 on any mismatch. Then four check groups run at once and
print one `PASS`/`FAIL` line per assertion. Nothing outside the package directory is read; scratch files go to the output directory.
Default: see "Tested" below.

## Words and verifier

- **#656 word**: the gauge44 layered word (`inputs/words/656-CANONICAL-WORD.json.gz`, `656-layers-FULL-WORD.json.gz`), 492 helpers, pinned by the hashes #656 publishes.
- **#799 word**: the X4 word (`799-X4-CANONICAL-WORD.json.gz`, `799-X4-FULL-WORD.json.gz`), 504 helpers, 5687 add ops, pinned by the hashes #799 publishes
  (the PR ships the construction, not the X4 word; the words are rebuilt from it and compared with its pins).
- **AL** = `inputs/pr799/independent/audit_local.py` (git blob in #799), the verifier whose frame rules the rows use.

## Model and hypotheses (shared by all rows)

- Registers carry a GF(2)-subspace frame. Every A/B/tail op declares its own frame `e[-1]` (AL:31, :138); `climb(q, e[-1])` requires `contained(cur[q], U)` for **both** operands (AL:122, "frame not monotone"), so frames only grow and an op frame is a common frame (join) of both operands. Nothing about values is checked at an ADD.
- `cur[]` is assigned only at AL:117, :120 (start) and :125 (climb); the centre loop (:130-136) changes only the local billing set. End caps: `climb(q, end[q])` (AL:115, :142); target registers end in `perp(port)`, the rest at the full space. The ports are 112 odd-weight vectors of F₂⁹.
- The minimal legal declaration of an op is the join (span-sum); declaring more only adds climbs. All bounds below are bounds on this **frame** lattice.
- **FOM (fixed op multiset)**: the set of ADD/scale ops is unchanged; only order and register assignment may change. Unless a row says otherwise, theorems are for FOM.
- **Interface**: S1 rows are stated **given the shipped end-of-A frames as bounds** (the 24 own registers of each block: their shipped bounds and end-of-A rows) and the value targets (value-forced). The case where the later readers' true caps replace the shipped frames is **open** (as in #717); see open problem 3.
- **Lawler frames `g` (L2, L3, B1, N1)**: `g` is the partner's frame in the **shipped order**: the target-side replay over every add, value-zero frame-courier adds included. It is a lower bound for an arbitrary reordering only where the frame is value-forced (distinct-source independence, the B172 caveat). Shipped check: recomputing `g` while skipping the value-zero adds (1921 on #656, 2317 on #799; source row empty) still gives 268/268 FAIL on both words (`cards/B171/lawler799.py`, `S2.skipzero-*`). The hypothesis is still a hypothesis; the rerun shows the result does not depend on the courier adds.
- **H-CUT** (cut row only): every cut op is `add target<-q` with `q` a centre, and no centre is a target. AL does not enforce it (AL:132 reads only dest/src of cut ops; AL:88 covers A and B). It is enforced by the generator (`construct_gauge_xcentre.py:344, :360`), by `len(centers)==8` (`audit_allcold.py:75`, `emit_allcold.py:41`), and by the emitter, which keeps only centre-sourced cut terms (`hpe_emit_local.py:94`); the spec schedule fixes the scatter and gather as gates on targets/sources and the centre (`03-motifs.tex:78-83`). Row K3.
- **Cancellation**: the S1 and Lawler counts are support/frame bounds, not cancellation-free-delivery statements (contrast Boyar–Find 2013). A frame is the running join of everything a register ever received; cancellation changes values, not frames, and a correcting ADD is one more visit whose frame also joins. So, for the S1 bound (given the shipped end-of-A frames) and the Lawler bounds (under the `g` hypothesis above), cancelling programs with the same op multiset are covered. This is not claimed for the other rows. Adding undo/redo ADDs changes the multiset and is outside (open problem 2). Row N1, `evidence/B185-NOTES.md`.

## Results at a glance

22 rows by primary status: 13 CHECKED, 4 ARGUED, 5 RECORDED (rows partly CHECKED say so).

| id | result | status |
|---|---|---|
| H1 | **S1 Hall lemma.** In each of the 11 S1 blocks with 8 lines, 15 registers (16 shipped) are infeasible: the number of whole-bound registers (8) is at least the number of plane stoppers (8, distinct planes), a perfect matching is forced, so every whole-bound register is indispensable, the "never read" ones included. Given the shipped end-of-A frames as bounds (true-cap case open). | counts CHECKED (candidate partners = wide registers, asserted in all 11 blocks); lemma ARGUED |
| H2 | Independent solver check on block (4,5,6,7): dropping register 433 makes the level model (F₃ relaxation of values, no lemma, any horizon) INFEASIBLE (sound for dyadic coefficients and the 4-level lemma, see H2-H4). | CHECKED (CP-SAT status) |
| H3 | The 38 "twin couriers" are whole-bound registers of H1 (38/38; drawn from base+1, +3, +5, +10 in the 11 blocks, a set that holds 44). They are long-lived A working registers (19-25 source reads each), not copies: 0 of 38 equals its partner P (value-forced, B176). This closes the twin-fusion route only, not the true-cap case of H1. | CHECKED |
| H4 | Borrowed-target plane jump: of the 88 stoppers, 0 have a holder of the l₂ piece and 0 have a point-holder escape. | CHECKED |
| H5 | Re-balancing the 12 demand planes of block (4,5,6,7): c_B = 2.0 per plane both ways, full move net 0, partial move −2 per plane (count level, not an op-count price). | RECORDED |
| H6 | **Blocks (0,1,2,3), (0,1,4,5), (0,1,6,7): the Hall bound is slack** (21 stoppers on 21 distinct planes match 21/21 using line registers alone; scratch alone matches 15/21). So scratch minimality there is **unproven, not refuted**. | CHECKED (negative scope) |
| L1 | The order-free Lawler oracle (`lawler`) agrees with exhaustive search over all orders on 3000 seeded random instances (80 feasible), returns a feasible order when it returns one, and separates a mergeable from a conflicting synthetic pair. | CHECKED |
| L2 | **S3/S4 on #656:** no copy pair can be merged by any reordering: 268/268 FAIL (S3 156, S4 112), each chain alone passes (caps not over-tight). | CHECKED; reading ARGUED |
| L3 | **S3/S4 on #799:** the same on the X4 word: 268/268 FAIL (5687 add ops, 156 + 112). | CHECKED; reading ARGUED |
| L4 | Every copy already has a two-visit conflict (one visit from each chain): 156 + 112 pair conflicts on each word. | CHECKED |
| L5 | Value classification of the 156 S3 copies on #656: 124 value-feasible with one packet, 32 both-mutated; all 112 S4 both-mutated, so 144 need extra undo/redo ADDs. | RECORDED (B82/B172) |
| B1 | **Bridges and holders on #799:** the 12 bridge registers 716..727: 12/12 FAIL (each chain alone passes); S3 holder/entering copies in 450..457 and 484..569: 94/94 FAIL; none removable at FOM; the 12 bridges have pairwise distinct 8-supports. | CHECKED |
| B2 | Merging a bridge into any other register is value-impossible without undo/redo ADDs (non-proportional 8-supports, overlapping lifetimes B1178..B1916); holder reuse is legal only for the 8 slots 450..457 (card B169; #869 is the eight block-0 hybrid deliveries). | RECORDED |
| K1 | **Cut ≥ 8 centres.** If W passes AL on the 112-port geometry and satisfies H-CUT, the number of centre registers read by the cut is ≥ μ ≥ ω = 8 (μ = minimum rank of a real 112×112 X with X[t,u] = δ_tu on the odd pairs, ω = the largest set of ports with pairwise odd inner product). | ARGUED (every quantity CHECKED, row K2) |
| K2 | On both shipped words: H-CUT holds, F = I, the cut-deleted map F₀ vanishes on odd positions (nnz(F₀) = 5824), rank(F−F₀) = 8 = |K| = ω, the clique {0,3,45,46,69,70,104,107} gives F−F₀ = I₈; AL accepts both words. | CHECKED |
| K3 | H-CUT is not enforced by AL, and this is not an issue for the executed program: a centre-free net-zero cut pair is accepted by AL (CHECKED) and flagged by the H-CUT check (CHECKED); the generator, `len(centers)==8` asserts, emitter line and spec lines quoted above are present at the quoted lines (CHECKED); that the emitter silently drops such terms and the full local chain accepts the toy with an identical emitted event count (24,411) is RECORDED. | ARGUED; anchors, toy CHECKED |
| R1 | **Pre-read layer:** the minimum number of touched pre-read targets on #799 within the move family is 66 (CP-SAT OPTIMAL, bound 66) against the threshold 62; no target can be cleared. | CHECKED on the stored pair table |
| R2 | The move family has 271 moves (84 h2r, 92 r2h, 95 deferrals); 0 of 271 singles and 0 of 36,501 pairs are legal (every |V| ≥ 2); all 271 singles and 150 seeded pairs are recomputed with the exact oracle; with `HM_FULL=1` the whole table is regenerated and compared; 38 of the 46 whole-copy-pair bundles are legal (their net ≤ 0 is RECORDED, B155). | CHECKED |
| R3 | Repair-pair triples (76 pairs × every third move, 20,368): 0 legal, min |V| = 2; target-sharing k ≤ 3 moves and k ≤ 4 pairs: 0 (B155). Ignoring legality the ILP ceiling of the family is 21 touched; the exact build of that move set touches 38 targets and has 104 violations. | RECORDED |
| M1 | **Verifier-model agreement:** the oracle frames equal the AL frames on all 5726 A/B ops of the #656 chain word (register bijection and GF(2) coordinate map), and AL accepts the word. | CHECKED |
| M2 | 272 twin-substitution edits (68 pure helpers × 4 policies) run through AL: all rejected; the number of "frame not monotone" failures equals the oracle `fin_raise` count in 272/272, 0 edits with 0 violations. The shipped table is checked structurally; the equality with the oracle count needs the card oracle, which is not shipped. | RECORDED (table CHECKED) |
| N1 | The S1 and Lawler counts are frame bounds, so they hold for cancelling programs of the same op multiset (see Cancellation above). | ARGUED |

Relation to #717 (rows F3-F5): there, the S1 scratch, the twin reads and the meet-frame reads are recorded as exact value and replay statements for
the shipped order. Rows H1-H4, L2-L4 and B1 are the order-free frame counterparts with the hypotheses stated. They do not replace F3-F5.

## 1. S1 blocks

### H1. Hall/matching lemma (ARGUED; counts CHECKED)
**Statement.** In each of the 11 S1 blocks with 8 lines, k = 15 registers (16 shipped) is infeasible. #whole-bound registers ≥ #plane stoppers = 8; a perfect matching is forced, so every whole-bound register is indispensable.
**Scope.** #656, 11 of the 14 S1 blocks (blocks (0,2,4,6) … (4,5,6,7)), 8 lines, **given the shipped end-of-A frames as bounds** (own 24 registers: shipped bounds + end-of-A rows), any horizon, FOM. The true-cap case (later readers' true caps replace the shipped frames) is open, as in #717.
**Proof sketch.** The 8 line vectors are the points of AG(3,2); every frame is a flat of size 1, 2, 4 or 8. A plane-bound register z whose target row has support all 4 points of its plane Π must, at the meeting where its frame jumps from at most 2 points to Π, meet a partner whose bound contains Π (the join is ≤ both bounds); only whole-bound registers qualify. After serving Π₁ the partner's frame is ≥ Π₁, so it cannot serve Π₂ ≠ Π₁ (the join would be the whole space, above bound(z₂)). The 8 stoppers have distinct planes, so #whole ≥ 8.
**Check.** `cards/B167/blockscan.py` prints, per block, 8 scratch-16, 8 wide, 8 plane stoppers, distinct planes, matching 8, and `cand-eq-wide True`: the candidate partners of every stopper equal the wide registers (11 lines asserted for each).
### H2-H4
H2: soundness conditions. The F₃ relaxation of the value layer is sound for **dyadic** coefficients; non-dyadic coefficients are outside the stated soundness; "any horizon" rests on the **4-level WLOG lemma** of B167, which is ARGUED in the card only and not re-proved here. `cards/B167/extract.py` builds the block (4,5,6,7) instance from the word and `level.py --drop 433` runs the level model (stable reordering by hull size, F₃ relaxation of the value layer, so UNSAT means infeasible for any horizon); the status INFEASIBLE is asserted (about 50 s). No blind discovery of the 16-register program was achieved by the solver (UNKNOWN in 100 s), so the run is a refutation check, not a replay of the shipped program.
H3: `cards/B176/val.py`; the 38 are whole-bound registers of H1 (38/38; not the same set as the never-read registers), so H3 shows none equals its partner P (the twin-fusion route is closed) but does not close the true-cap case. #717 F3's "16 equal twins" is word-wide (8 pairs in 8 blocks, card B92b), a different set from these 38; there is no contradiction. H4: `cards/B179/gate.py` (A-replay equals the end rows) and `gate2.py`. Scope as H1; H4 needs a second Π-frame l₂ holder to escape and finds none.
### H5-H6
H5 RECORDED (`evidence/B175-NOTES.md`; its script overwrites a card pickle and is not shipped). H6: `cards/B171/scan01b.py` (stoppers, 21 distinct planes, matching 21 with line registers, 15 of 21 with scratch only, 5 of 7 per block).
**Stated limits.** An interface change (fewer plane-stopper rows, other hyperplanes, a plane register with support ≤ 2) is **not** excluded, and neither is the true-cap case (later readers' true caps instead of the shipped end-of-A frames). B177 (the (0,1,*) blocks) has no verdict at the time of writing.

## 2. S3/S4 copies: order-free minimality

**Statement (L2, L3).** No S3 or S4 copy pair can be merged into one register by any reordering: 268/268 FAIL on each word.
**Scope.** FOM; frames `g` in the **shipped order** (see the Lawler hypothesis above: a lower bound for arbitrary reorderings only where value-forced; the skip-zero rerun is also 268/268 FAIL): the partner's frame before an op (target-side replay from the start frames over every add, centre joins ignored: weaker, so sound for FAIL); caps = perp of the ports of the targets reached from the partner, with the two copies a, b treated as sinks; the precedence-free relaxation (no value precedence is imposed). Copies are identified without tags as the first op filling an empty helper row from a non-empty one, restricted to the ledger S3/S4 ids. #870 is not local and was not run. Non-S3/S4 helper pairs: only the B1 classes.
**Proof sketch.** Lawler 1973 (Management Science 19(5):544-546, 1|prec|f_max, least cost last; citation per the card, not re-fetched). A merged register's frame after a prefix is the join of the frames of the visits so far (a nondecreasing set function); an order is feasible iff the join of every prefix lies in the cap of its last visit. Lawler's backward rule decides this order-free: take any visit whose cap holds the join of all remaining visits as the last one; if none exists, no order exists. L1 checks the rule against exhaustive search.
**Checks.** `cards/B171/lawler799.py` (any word; `passing copies 0`), `pair799.py` (156 + 112 two-visit conflicts), `checks/lawler_check.py`. The same script reruns with value-zero adds skipped in the `g` replay (1921 / 2317 skipped): 268/268 FAIL on both words.
**Reuse.** `lawler(visits, base, prec)` is an order-free legality oracle for any "one register serves X and Y" claim.

## 3. Bridges and holders on #799 (B1, B2)
**Statement.** The 12 bridge registers 716..727 (register ids): 12/12 FAIL; S3 holder/entering copies in 450..457 and 484..569: 94/94 FAIL; removable: 0. **Scope.** #799, FOM, value-forced lower-bound frames, caps = reached-target ports. The frames are the shipped-order frames of the Lawler hypothesis above. The phase-1 frame-courier role of the bridges is ignored (it only adds conflicts, so FAIL stays sound). `cards/B182/b182.py`.

## 4. The cut needs at least 8 centres (K1-K3)
**Statement (K1).** Let W pass AL on the 112-port geometry and satisfy H-CUT; K = the centre registers read by the cut. Then |K| ≥ μ ≥ ω = 8. The shipped words have |K| = 8 = rank(F−F₀), so `len(centers)==8` is forced for this cut. **Scope.** #656 and #799 (identical numbers); AL has a single cut section at one instant (AL:82, :126-137). Without H-CUT the argument gives rank(F−F₀) ≤ the number of frame-free ops.
**Lemmas.** L0 endpoint identity (AL:106-112). L1 frames are monotone everywhere. L2 path lemma: a time-respecting path u → … → v+t gives cur_end(v+t) ∋ p_u, and the end cap perp(p_t) forces (t,u) even. L3 F₀ (cut deleted) is 0 on the odd positions. L4 the cut block is I+N, N = Σ_{q∈K} n_q e_qᵀ, N² = 0, so rank(F−F₀) ≤ |K|. L5 F−F₀ = F = I on the odd positions, so |K| ≥ rank ≥ μ ≥ ω. Side lemma: a centre frame contains p_u for u in the support of its A-row.
**Checks.** `cards/B174/check.py` on each word prints H-CUT, F = I, F₀ odd nnz 0, rank(F−F₀) = 8 ≤ |K| = 8, ω = 8, the clique submatrix I, the centre-frame lemma; `clique.py`; AL on both words. **Caveats.** μ ≥ ω only; μ = 8 uses the shipped words. The card's premise "the odd part of M has rank 8" is false as stated (rank(M∘Odd) = 112); the right object is the minimum-rank completion. Decoder terms (B14/B27) and all pricing are separate; this is a count.
**K3.** See the hypothesis H-CUT above; `checks/make_toy.py` builds the toy, `checks/anchors.py` checks the quoted lines. Full text: `evidence/B178-VERIFIER-GAP.md`.

## 5. Pre-read layer (R1-R3)
**Move family.** 271 moves: 84 h2r (read r not h, delete the matching pre-read), 92 r2h (read h, insert a pre-read), 95 pre-read deferrals, plus 46 whole-copy-pair bundles (38 legal, all net ≤ 0). Exact-oracle legality, retained frames (`cards/B147/oracle799.py`, whose no-op evaluation is legal with κ = 0.001661634653669567, the κ #799 publishes).
**Proof status.** The minimum 66 is exact for the model "legal singles and legal bundles, each leaked final cap needs a pairwise repairer in the chosen set" and is proven only at the pairwise level (singles, all pairs) plus the recorded triple probes, **not** for arbitrary k-sets. Not tested: joint copy-gate retiming, re-gauge, the end-frame convention.

## 6. Model fidelity (M1, M2)
**Scope.** The #656 chain word (the same AL file as #645/#656). `cards/B128/retest.py base` prints `frame map bad 0 5726` and the AL verdict; `checks/b128_table.py` checks the shipped 272-row table.

## Open problems and gaps (stated plainly)

1. **S1 blocks (0,1,2,3), (0,1,4,5), (0,1,6,7):** the Hall bound is slack (H6); 48 scratch registers, including the centres 224, 240, 256, have no minimality proof. B177 is running; no verdict yet.
2. **Multiset-changing merges** (undo/redo ADDs, B169-style holder merges) are outside every Lawler result; the S3/S4 and bridge theorems are FOM only.
3. **S1 true-cap case and interface change.** S1 minimality is proved given the shipped end-of-A frames as bounds. The case where later readers' true caps replace those frames is open (as in #717), and so are fewer plane-stopper rows and other hyperplanes.
   - *Update (post-submission, unverified here; card B188):* on the 11 eight-line blocks of #656, all 7 pair directions for the S1 stage basis cost exactly 2 registers per demanded plane (2 × 12 = 24 per block, the shipped cost). Directions with fewer stoppers need more pair registers, because a pair register serves only one plane. So a change of stage basis alone cannot lower the S1 count. What remains open is fewer demanded planes (an op-multiset change) or a frame descent.
4. The cut ops and centre frames are not examined beyond K1-K3; non-S3/S4 helper pairs have no generic sweep; #870 is not local.
5. **H-CUT** is not enforced by AL; several-epoch cuts in another verifier are outside the theorem.
6. **Decoder n ≥ 9** (mixed β ≤ 7 terms, #717 D1) is a separate question; the decoder terms are not covered.
7. **Pre-read** is proven only up to singles, all pairs and the recorded triple probes, not for arbitrary k-sets.
8. The Lawler layers and the S1 lemma have no independent second-reader audit; the Lawler citation was not re-fetched.

## Tested

Fresh `git archive` of the commit, every assertion PASS, exit 0: **53 PASS lines (2 in step 0), about 52 s wall** on 12 cores (the S1 solver run, about 50 s, is the longest single step; the four groups run at once). With `HM_FULL=1` there is one more PASS line (the regenerated pre-read table equals the stored one; about 13 min at background priority on a loaded machine, one run by the authors: that run's regeneration line and the other 50 lines passed, but its S1 solver step hit the then 150 s limit under load, so the limit is now 900 s; the default run above, from the final commit, passes all 53). The solver step takes about 50 s on an idle machine; `UNKNOWN` (limit reached) fails the assertion.

| Python | numpy | ortools | how installed |
|---|---|---|---|
| 3.14.7 | 2.5.4 | 9.15.6755 | development venv (the pins of `requirements.txt`) |

## Files

- `verify.sh`, `scripts/provenance.py` (step 0; `--write-manifest` regenerates the manifest), `SOURCES.json`, `MANIFEST.sha256`, `requirements.txt`, `LICENSE`, `NOTICE.md`.
- `inputs/`: vendored files by PR (`pr799/`, `pr635/`, `main/`), rebuilt words (`words/`), the helper ledger and the pre-read pair table (`derived/`).
- `cards/`: the swarm's card scripts under their card ids (B167 S1 lemma and solver; B171 Lawler on any word; B176, B179 extensions; B182 bridges; B174 cut; B159 pre-read; B128 fidelity; B98b/B98c/B99/SYN-18 shared loaders; B147/B155 pre-read oracle). The only edits against the originals are the local path prefixes (replaced by `HM_ROOT`), `pair799.py` taking an optional word argument, `extract.py` writing its instance into its own card directory and the pre-read table read as JSON instead of a pickle.
- `checks/`: `expect.py` (assertion helper), `lawler_check.py`, `make_toy.py`, `anchors.py`, `pairs_sample.py`, `b128_table.py`.
- `evidence/`: card notes (local paths removed) and the 272-row table.

## Credits

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0. See `NOTICE.md` for the PRs whose words, code and results are used and for the overlap check.
