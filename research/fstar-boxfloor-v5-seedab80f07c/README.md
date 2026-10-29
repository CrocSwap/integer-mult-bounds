# KB5L: the tau >= 1 box floor at v = 5 is PROVEN - and one shareable-class pattern settled

## Scope

Kappa-blocker **KB5L** (authorized explicit open request from the
[handoff thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166);
scope changed from the drawn `complex-new-helper-inventory` card and recorded in
`TASK.json`): the **first open case of the tau >= 1 box floor (`v = 5`)** and the
**shareable-class remainder** - the recorded remainders of
[PR 3012](https://github.com/CrocSwap/integer-mult-bounds/pull/3012) (agent-79).

**Answer (a): the tau >= 1 box floor holds at v = 5 - PROVEN.** For every exact
3-total rational decoder `M = sum_{j<=3} p_j q_j^T` on `v = 5` lines with
`M_tt != 0` and `tau(t) >= 1` on every line, `box(M) >= 3 = floor(2v/3)`.
The mechanism is neither `#keepable >= 3` nor matched pivots alone: it is a
**rank obstruction**. Combinatorially the only way to keep `box` at 2 is a
complete zero-arc digraph inside a 2-bit label-cap family; a complete zero-arc
digraph makes `M` diagonal, and a diagonal `M` on 5 lines has rank 5, which no
3-total decoder has.

**Answer (b): PR 2978's 21-pattern shareable remainder is narrowed.** The
recorded `3 realized / 3 unrealizable-column / 21 not-found-in-cap` split is
replayed exactly (same seed, same stages); a strictly larger bounded search
(exact kernel q-solver at 10,000 P-restarts per pattern plus the big alphabet
at 2,000) realizes none of the 21; and **one of the 21 is PROVEN unrealizable**.
The remaining 20 stay CHECKED, not-found-in-cap. Claims are labelled
PROVEN / CHECKED / DEMOTED.

## CORE: the v = 5 tau >= 1 verdict

| stage | object | result | label |
|---|---|---|---|
| 1 | 5-line type multisets, tau >= 1 | 749,398 enumerated, envelope `box = 2` on exactly 33 | PROVEN (exhaustive) |
| 2 | the 33 families under the anchor screen | 15 unrealizable, 6 shapes survive | PROVEN (written) |
| 3 | blocking zero-arc sets per shape | only the complete digraph blocks every triple | PROVEN (exact, 2^20 per shape) |
| 4 | complete digraph at rank <= 3 | `M` diagonal has rank 5 > 3 | PROVEN (written) |
| 5 | realizable replay | 120 tau-forced decoders, exact box >= 5, witnesses replayed | CHECKED |
| 6 | bounded falsifier hunt | 35 instances, 0 hits | CHECKED (bounded) |

### The reduction (written; engine-anchored definitions)

`box(M)` is the largest kept set over **in-box** labels `a(t) <= a0(t)`,
`b(t) <= b0(t)` with `K_tt = 1` on kept lines and `K_ts = 0` at every zero arc
`(t, s)` with `t` before `s` in the kept order. Three facts reduce the
question to a finite one.

1. **R1 (Lemma SB + definition):** `box` depends only on `(a0, b0, Z)` - the
   anchor masks and the zero-arc set. Labels of non-kept lines never enter a
   constraint.
2. **R2 (monotonicity):** `box` is non-increasing in `Z` (adding zero arcs only
   adds constraints). So `box(Z) >= box(Z_even)` where `Z_even` is the set of
   ALL pairs with `|a0(t) intersect b0(s)|` even.
3. **R3 (Lemma SG, PR 2869, PROVEN; machine-asserted on every realizable
   instance here):** every realizable zero arc is in `Z_even`. The engine's
   `scope_identity` is the exact iff: `dot1(a0[t], b0[s]) = 1` if and only if
   `M_ts != 0` and `v2(M_ts) = gamma`.

Hence a realizable decoder with `box = 2` must have a combinatorial envelope
`(a0, b0, Z_even)` with envelope box 2, and its actual `Z` must block every
triple of kept lines in every order. The three stages enumerate that
possibility space exactly.

### Stage 1 - envelope classification (PROVEN, exhaustive)

`floor_v5.py` job 2 enumerates all `C(41,5) = 749,398` multisets of 5 raw
line types (`(a0, b0)` mask pairs with `tau = |a0 intersect b0| >= 1`; raw
masks preserve the joint bit structure, which per-line canonicalization would
lose). For each multiset the envelope uses `Z = Z_even` and asks for a kept
triple: a memoized singleton-witness test first, the exact kept-set ladder
(pinned to the independent definition-level brute enumeration on 400 random
configs, `PASS_KL_PIN`) as fallback. Result: `PASS_KL_V5 configs=749398
cheap=749347 exact=18 envelope-box2-families=33`.

All 33 families share one shape: **every pair-intersection is even** (so
`Z_even` is the complete digraph) and **one label side is confined to 2 bits**
(a rank-2 cap on in-box `K = A B^T`), e.g. `a0 = [3,3,3,3,3]`, `b0 =
[3,3,3,3,3]` (masks `3 = {0,1}`, `5 = {0,2}`, `6 = {1,2}`, `7 = {0,1,2}`).
This is exactly the Lemma RT + shareable-totals route PR 3012 predicted as the
only possible falsifier shape.

### Stage 2 - anchor-attainment screen (PROVEN, written)

From the engine's `anchor_data` definitions: `a0_j(t) = [v2(p_j(t)) = m_j]`
with `m_j` a minimum over nonzero column entries, `b0_j(t) =
[v2(q_j(t)) = gamma - m_j]`. Two consequences:

- **A1:** if bit `j` is in no `a0(t)` then `p_j` is identically zero (a
  minimum over nonzero entries is attained), so `rank(M) <= 2`.
- **A2:** bit `j` is in some `b0(t)` only if `m_j` is finite and `c_j = gamma`;
  hence a family with bit `j` in some `b0` but in no `a0` is **unrealizable**.

The screen rejects 15 of the 33 (the mirrors with 7s on the `b0` side of a
2-bit `a0`), leaves 5 unshareable-total rank-3 shapes and 3 zero-p-column
rank-2 shapes (`PASS_KL_SHAPES shapes=6 screen-rejected=15`, 6 = the 8
survivors up to total relabeling).

### Stage 3 - blocking zero-arc sets (PROVEN, exact)

For each surviving shape, `family_v5.py` builds exact per-triple blocking
tables (kept-3 infeasibility of the 3-line ladder, all `2^6` arc patterns)
and enumerates all `2^20` arc subsets of the 5 lines. In **every** shape the
only subset that blocks all ten triples is the **complete digraph**
(`blocking=1 minimal=1` per shape). Intuition: with one non-arc `(x, y)` the
order `(x, y, z)` leaves `K_xy` free, and the 2-bit cap can always be met
with `det(K[S,S]) = 0` - the exact tables confirm it in every shape.

### Stage 4 - the rank obstruction (PROVEN, written)

Complete `Z` means `M_ts = 0` for all `t != s`, i.e. `M` is diagonal with
nonzero diagonal, so `rank(M) = 5`. But `M = P Q^T` with 3 totals has
`rank(M) <= 3`. Contradiction: **no exact 3-total rational decoder with
`v = 5`, `tau >= 1` everywhere has `box < 3`**. The rank-2 shapes (A1:
`p_j == 0`) fail a fortiori. This is the same obstruction PR 2978's realized
`v = 3` counterexample family sidesteps only because a `3 x 3` diagonal has
rank 3 <= 3.

**CONCLUSION (PROVEN): `box(M) >= 3 = floor(2v/3)` for every exact 3-total
rational decoder with `v = 5` and `tau(t) >= 1` on every line.** The tau >= 1
box floor is now PROVEN for `v <= 5`; the first open case moves to `v = 6`
(threshold 4).

### Corroboration (CHECKED)

- `PASS_KL_REALIZABLE_V5 instances=120 violations=0 min-box=5`: 120
  realizable tau-forced decoders (`tau_model`: odd role entries force
  `tau >= 1` on every line), identities asserted, exact box by the vendored
  engine, in-box witnesses replayed from the definitions.
- `PASS_KL_HUNT tested=35 hits=0`: bounded falsifier hunt (tau-targeted, PR
  2978-core extensions, nullspace-dense zero patterns), ladder-exact
  criterion. Bounded, not a non-existence result - the PROVEN chain above is
  what settles the question.
- `PASS_KL_PROBE model-ok=142 tau>=1-all=0`: untargeted random entries make
  all-5-lines `tau >= 1` rare (~0.1%); this is why PR 3012's 240-instance
  bounded search is thin evidence at `v = 5` and why the combinatorial
  envelope route is the decisive one.

## Shareable class: the 21-pattern remainder

`shareable_v3.py` recomputes PR 2978 job B from scratch (the vendored receipt
ships empty): `PASS_KJ_V3 configs=3023 box-equals-cert=2996 candidates=27`.
Pass 1 replays PR 2978's `realize_kj.py` pipeline exactly (same seed
20261017, same stages and caps) and reproduces its recorded split:
`{"not-found-in-cap": 21, "realized": 3, "unrealizable-column": 3}`
(`PASS_KL_SHAREABLE`). The 3 realized patterns are PR 2978's diagonal-M
counterexample family (`cert = 3 > 2 = box`, replayed witnesses).

Pass 2 pushes the cap on the 21 with an **exact kernel q-solver**: for fixed
`P` (anchor recipe, `p_j(t)` odd iff `j in a0(t)`) the row `q(s)` must lie in
the integer kernel of its zero-arc predecessor rows, avoid finitely many
hyperplanes (`p(t).q(s) != 0` off `Z`), and match the parity box; a solution
exists iff `p(t)` is outside `span{p(u) : (u, s) in Z}` for every non-arc
`t`. 10,000 deterministic P-restarts per pattern, plus the vendored big
alphabet at 2,000. **No new realization: all 21 remain not-found-in-cap**
(`push-final` equals `replay`), now under a strictly larger and structurally
different search.

**One pattern is PROVEN unrealizable** (settled): candidate 7,
`a0 = [3,3,3]`, `b0 = [3,3,3]`, `Z` complete. A1 gives `p_2 == 0`, so
`rank(M) <= 2`, but complete `Z` forces `M` diagonal with `rank(M) = 3`.
Unrealizable over Q, no search cap involved.

**Correction to PR 3012's framing:** only **20** of the 21 lie in the
shareable class (`r_box = 3`; every total appears in some `b0`, which forces
`c_j = gamma`). The settled pattern forces `r_box = 2` (bit 2 appears in no
`b0`), so it was never a shareable-class candidate. What remains for
shareable-class completeness at `v = 3` is: the 20 recorded patterns, plus the
caveat below.

**Methodological caveat (CHECKED observation, not a proof).** PR 2978 job B's
canonicalization applies total relabeling **per line** (`canon_total` on each
line's `(a0, b0)` separately) and then computes pair parities from the chosen
representatives. Total relabeling is a global operation on the shared bit
indices, so two joint structures with the same multiset of per-line canonical
types can have different cross-line parities (e.g. three tied singletons on
three distinct bits versus on one bit) and therefore different `Z` spaces. The
recorded `3023`-pattern census may thus under-count the joint `(a0, b0, Z)`
space, and "the 21" (or 20) may not be the complete gap-candidate set at
`v = 3`. The v = 5 enumeration in this package is unaffected: it enumerates
raw joint type multisets, which preserve cross-line structure. A joint-sound
v = 3 census is the natural follow-up check.

## What is proved, what is checked, what is demoted

- **PROVEN:** the tau >= 1 box floor at `v = 5` (`box >= 3`), by the
  four-stage chain above (exhaustive envelope classification + written
  anchor screen + exact blocking-Z enumeration + rank obstruction). The
  envelope classification (33 families), the anchor-attainment screen (15
  rejected), and the blocking-Z result (complete digraph only) are each
  finite and machine-replayed. The v = 3 pattern `(3^3, 3^3, complete)` is
  unrealizable.
- **CHECKED (machine, deterministic):** ladder pinned to definition-level
  brute enumeration on 400 configs; 120 realizable tau-forced decoders with
  replayed in-box witnesses; the 35-instance bounded hunt (0 hits); the
  exact PR 2978 classification replay (3/3/21) and the cap push (20 patterns
  survive 10,000 exact-kernel restarts + big alphabet).
- **DEMOTED / OPEN:** v = 6 (threshold 4) is the new first open case of the
  tau >= 1 floor; the 20 remaining shareable-class patterns are
  not-found-in-cap, not proven unrealizable (one more is now proven, so 20 of
  the original 21 remain); the matched-pivot floor stays demoted.

## What this does and does not say about F-star

F-star (`cert(M) >= floor(2v/3)`) is **not** proved and **not** refuted.
Nothing here lowers `cert` on any instance; the box rung of the
`cert >= max(named, box)` lower bound is now PROVEN to carry the threshold on
the entire tau >= 1 domain for `v <= 5`, and the named/matched-pivot rung
carries the `tau = 0` region (PR 3012's falsifiers all have `cert = v`). The
shareable-class question is about `box = cert` completeness, not about the
threshold; even a realized gap pattern would not falsify F-star (its `cert`
would still need to drop below `floor(2v/3)`, which no falsifier test in the
lineage has produced).

## Reproduce

Standard library only, Python 3.10+ (registered replay: 3.12):

```sh
python3 -B research/fstar-boxfloor-v5-seedab80f07c/verify.py
python3 -B research/fstar-boxfloor-v5-seedab80f07c/predecessor/pr3012/anchor_replay.py
python3 scripts/research_package.py --package research/fstar-boxfloor-v5-seedab80f07c --check-only
```

Observed: `PASS_KL_PINS vendored-pr3012=57`; `PASS_KL_PIN configs=400
brute-equals-ladder=400`; `PASS_KL_V5 configs=749398 cheap=749347 exact=18
envelope-box2-families=33`; `PASS_KL_REALIZABLE_V5 instances=120
violations=0 min-box=5`; `PASS_KL_ALL v5-configs=749398 envelope-families=33
realizable=120`; `PASS_KL_PROBE model-ok=142 tau>=1-all=0`;
`PASS_KL_SHAPES shapes=6 screen-rejected=15`; `PASS_KL_HUNT tested=35
hits=0`; `PASS_KL_FAMILY_ALL shapes=6 hunt-tested=35 hunt-hits=0`;
`PASS_KJ_V3 configs=3023 box-equals-cert=2996 candidates=27 certmax-cache=64`;
`PASS_KL_SHAREABLE candidates=27 replay={"not-found-in-cap": 21,
"realized": 3, "unrealizable-column": 3} push-final={"not-found-in-cap": 21,
"realized": 3, "unrealizable-column": 3} counterexamples=3`; `PASS_KL_VERIFY
v5-configs=749398 families=33 shapes=6 realizable=120 hunt=35 shareable=27
pins=57 digest=<printed>`. The vendored PR 3012 anchor replay prints
`PASS_KM_ANCHORS markers=12 digest=0b5b55f84375b37c vendored-verify=exit0`,
re-running the vendored PR 2978 `verify.py` unchanged (including
`PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19 mp=9/16 chain=22
reach=0/12,8/19` and `PASS_KJ_COUNTEREXAMPLE v=3 tau=2/2/2 cert=3 box=2
r_box=2 independent=3/2`) and the PR 3012 markers `PASS_KM_VERIFY
falsifiers=4 lb2=16761 mixed=240 v3-configs=3023 pivot=240
digest=fb29a75bde520732`. `research_package.py --check-only` prints
`PASS_PACKAGE_METADATA_AND_PINS` (not a mathematical acceptance check).

## Exact heads and pins

- Base: `d8e0f83f00191df62174b641e9fff055c357f641` (frozen assignment pin =
  canonical `origin/main` at worktree creation, 2026-10-16); branch
  `research/agent-80-kb5l-boxfloor-f0`.
- [PR 3012](https://github.com/CrocSwap/integer-mult-bounds/pull/3012) head
  `63c6525120c20543c4a7acae1a1e1ea36e099b81`, package
  `research/fstar-boxfloor-minimal-seed758ae8fe` vendored byte-exact under
  `predecessor/pr3012/` (57 files, `pr-tree-extract`), SHA-256 pins in
  `predecessor/PINS.json`, re-asserted at every replay. Its nested vendored
  chain ([PR 2978](https://github.com/CrocSwap/integer-mult-bounds/pull/2978)
  head `12eb7b832de9239a314a7cddf6c6033d618cd8f2`, [PR
  2963](https://github.com/CrocSwap/integer-mult-bounds/pull/2963) head
  `ee755e682b3b30d493e764d3be50003b13b69b4a`, [PR
  2936](https://github.com/CrocSwap/integer-mult-bounds/pull/2936) head
  `f0ef06f13e4de3e50c211c880bdc6891c09620a1`, [PR
  2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914) head
  `3f7781efccdf10fa61a1e0a6f11c191579b21280`) carries its own pin sets (14 +
  29 files), re-asserted by the vendored replays.

## Open next questions

1. **The tau >= 1 box floor at `v = 6`** (threshold 4): run the same envelope
   classification (6-line multisets) and blocking-Z enumeration with
   constraint propagation. Smallest falsifying instance first.
2. **The 20 remaining shareable-class patterns**: the kernel feasibility
   condition settles the `Z` side exactly; the anchor side needs a
   valuation-level realizability characterization. Any realization refutes
   box-completeness on the shareable class at `v = 3`.
3. **F-star at general `v`**: the box rung now covers the whole tau >= 1
   domain for `v <= 5`; the `tau = 0` region lives in the named rung. A joint
   lower bound in the shareable-class vocabulary is the natural next lemma.

## Credit

F-star, `cert(M)`, L8 labellings and the proven chain `cost >= cert(M)`:
`research/root-unit-decoder-lemmas`, [PR
1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds (Claude Opus 5.5 (Anthropic) via Claude Code assistance).
Fixtures `tied_min`/`cex_min_1` with recorded limits 11/18: DreamingOfClouds,
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111).
Lemmas SF/MP/RK/AN, Lemma MX, zero-digraph machinery, Lemmas SC/SG (the scope
identity used as R3 here), chi(Z) machinery, Lemma CT, the sub-anchor box and
Lemmas SB/LB (used as R1), Lemma BPP with the tau >= 1 necessity pin, the
twelve `tied_min` `v = 11` sub-decoders, Lemma V2, Lemma RT + shareable
totals with the minimal `box = cert` counterexample and the v = 3
combinatorial census with `realize_kj` (the 27 patterns replayed here), and
Lemma K / Lemma LB2 / Lemma TB with the four tau = 0 falsifiers and the
recorded v = 5 obstruction shape: Aaron Wang (navinor), [PR
2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717) /
[2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) /
[2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774) /
[2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869) /
[2890](https://github.com/CrocSwap/integer-mult-bounds/pull/2890) /
[2901](https://github.com/CrocSwap/integer-mult-bounds/pull/2901) /
[2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914) /
[2936](https://github.com/CrocSwap/integer-mult-bounds/pull/2936) /
[2963](https://github.com/CrocSwap/integer-mult-bounds/pull/2963) /
[2978](https://github.com/CrocSwap/integer-mult-bounds/pull/2978) /
[3012](https://github.com/CrocSwap/integer-mult-bounds/pull/3012). All
authors verified at current ground truth with `gh pr view --json author,title`
on 2026-10-16. New here: the exhaustive v = 5 envelope classification (33
families), the anchor-attainment screen (A1/A2), the exact blocking-Z
enumeration (complete-digraph-only), the rank obstruction closing the
tau >= 1 floor at `v = 5`, the exact kernel realization solver, and one
shareable-class pattern proved unrealizable.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance;
no model named; no independent human review claimed). No kappa, supplier, word
or moment claim.
