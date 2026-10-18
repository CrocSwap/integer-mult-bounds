# Lemma G extended labels on the selected #1094 programs (seed 65)

**No new κ. The selected record is unchanged.** This is an audit package, with two parts:
* a scoped positive result for the restoration interface that the selected record retains as *common-label /
  mutable-source realization*, for the **complex supplier only**: the local programs of the selected seven-slot word;
* an exact admission gap next to it.

* Card: `uniform-transfer-audit`.
* Scope: **refined** (see [TASK.json](TASK.json)).
* Base: `0b1cccf8`.
* Proofs: [PROOF.md](PROOF.md).
* Numbers: [EXPECTED.json](EXPECTED.json), all produced by [verify.py](verify.py).

## (a) Main result: H1 holds for the selected programs, so Lemma G applies per call

Lemma G's Theorem 1 is proved in Lean as `LemmaG.Stream.conj_matrix` (`research/e8-lemma-g-lean/LemmaG/Stream.lean:294`,
`PROOF.md:37`). It needs two hypotheses:
* **H1:** the emitted stream is `WellLabelled` in the extended labels (tag × frame, Lemma G `README.md:50`);
* **H2:** every relabel's recipe is exact.

Under them, `physRun(es)(h) = D(λ¹) S D(λ⁰)⁻¹ h` for every dirty input, on any module where the recipes are exact.

**This package proves H1 for the selected seven-slot word's emitted forward and backward local programs.** Every
input is regenerated from committed bytes:

* **Word.** `research/k8-frame-antichain/inputs/SEVEN-SLOT-WORD.json.gz` (content `c2b29430…`).
* **Transport.** The in-repo PR635 tools (`research/complex-sw4-frame8/vendor/pr635/…/code/`):
  `hpe_audit_and_transport.py`, run with `--routing` set to the phase-baseline `CANONICAL-WORD`.
* **Emitter.** `hpe_emit_local.py`.
* **Frame-only replay.** `hpe_audit_local.py`.
* **Recipes.** The in-repo `phases_full.py` with its `clifford_exact.py`.

The four outputs equal the selected pins, and both `SLOT-PINS-k8` (#1018) and the #1094 `PLAN.json` provider registry
name the same hashes:

| output | hash |
|---|---|
| canonical payload | `4ddb29fb…` |
| forward program | `071ecdac…` |
| backward program | `f36c5831…` |
| `CLIFFORD-RECIPES` | `d0768f21…` |

An independent, HPE-aware extended-label checker (`label_check`, standard library) finds **0 violations in both
orientations**. It does so under both the literal (strict) and the most permissive Lean reading of private clears. It
also checks:
* the adapter/wrapper bridge;
* the end labels;
* an independent exact scalar shadow (H3).

| | forward | backward |
|---|---:|---:|
| events | 24,767 | 24,767 |
| violations (strict / permissive) | 0 / 0 | 0 / 0 |
| source writes | 1,497 | 3,924 |
| wrapped helpers (192 entering + 48 cold hyperplane-ended) | 240 | 240 |

Five of the eight centres are sources.

**Controls of the checker.** These are failure controls, not a proof of the checker; Lemma S below is the argument.
* **Both readings must reject** 28 edited forward programs and 27 edited backward programs:
  * the five edits of Lemma G's own `mutants()` and two HPE-specific edits;
  * edits aimed at single clauses:
    * a target exit adapter at a non-final frame, or before its last climb;
    * identity entry adapters (an unwrapped helper's at a nonzero frame, one added for a wrapped helper, a target's
      after its first climb);
    * identity exit adapters (one added for an HPE helper, a source's keyed at a non-FULL frame);
    * a post wrapper before its helper's final climb;
    * a source entry adapter keyed away from `start_i`;
    * a centre step from a wrong frame;
    * a phase marker dropped, two swapped;
    * an unknown event kind, scalar kind, adapter direction and wrapper side;
    * wrapper keys and counts (an entering helper's wrapper keyed at 0, a wrapper added for an unwrapped helper, a
      duplicated pre wrapper, a dropped post wrapper);
    * forward only, the centre copy taken from a register at a wrong frame.
* **Only the strict reading must reject** one edit, a scale annotated at a wrong frame. Lean's `Admissible` asks nothing
  of `scale`, so the permissive reading accepts it by design.
* **Both readings must reject** the three mutants of (b).

All counts are pinned in `EXPECTED.json`. As a coverage check, `verify.py` also weakens each of the checker's 32 clauses
alone, in memory, and re-runs it on all 62 pinned inputs. **31 of the 32 weakenings change a pinned value.** The one
that does not is "a source entry adapter is keyed at `start_i`". It is implied by the next clause, "it finds the label
`((pre,i), f)`", because a `(pre,i)` label only ever exists at frame `start_i`.

**All-words structural lemma** (PROOF.md §2, Lemma S). The tag part holds for every word that the pinned transport
(with the pinned routing) and the pinned emitter accept:
* the emitter places scalars only in non-adapter phases, and data adapters only in their own phases;
* the zero-frame precondition touches only registers that start at frame 0 and are not wrapped;
* the FULL cleanup touches only FULL-final registers. Those are never targets, because target finals are the
  hyperplanes `p^⊥`, and their exit adapters are identities.

Hence every scalar event sees tag `T` on all its operands. The emitter also places every operand at the annotated
frame, provided every cut gate writes a target. The frame-only replay enforces that condition, and the selected word's
176 cut gates satisfy it. So H1 holds for every word the selected chain admits.

**Scoped theorem** (PROOF.md §4). Combine:
* Lean `conj_matrix`;
* H1 (above);
* H2 (the `phases_full` recipe pin `d0768f21`, asserted when the recipes are generated and independently re-verified
  by open PR #1781);
* the exact scalar shadow.

Together they give **per-call common-label / mutable-source realization of the complex supplier's local programs, on
ℂ^{2^9} and ℂ^{2^9} ⊗ V (more generally, on any ℚ-module where the same operators and recipes satisfy H2), for
arbitrary dirty inputs**: register by register, each orientation's physical run equals `D(λ¹) S D(λ⁰)⁻¹ h`.

**Still inherited** (named, not discharged). Four parts of the retained common-label / mutable-source interface are
untouched here:
1. all-size execution of climb recipes by recursive children (the compiler);
2. whole-call hosting and footprints (Lemma A (O′) and (W));
3. composition of data phases across calls;
4. the **bit supplier's** common-label / mutable-basis realization. It is the role-independent carryover argument of
   #535's `PR510-MUTABLE-SOURCE-CARRYOVER.md` and stays a listed conditional interface
   (`research/e8-bit-r420/README.md:113–118`, `research/e8-bit-p111-tuned/tune/README.md:84`). This package checks no
   bit word.

Two further retained obligations are used and not proved here (PROOF.md §7):
* the precision and tape contracts;
* Lemma A's (N) for the wrapper pairs, which evaluates each wrapped helper's row to `C_[w] ⊗ I`.

**The Lean build is not re-run.** `verify.py` checks the theorem's statement text only.

## (b) Admission gap: the selected chain runs no tag check, and its frame-only replay does not substitute for one

Lemma G assigns the tag half of H1 to `check_extended_labels.py` (`research/e8-lemma-g-lean/README.md:50`). That
checker cannot run on HPE words; see (c). The HPE package maps only G0 in `cleanup_tail` (`hw`, tail shape, `hmv`) to
`audit_local.py` (`research/hyperplane-end-lean/PROOF.md:104`), and there every operand has tag `T`. So **no stage of
the selected chain checks tags.**

Its emitted-program check is the PR635 frame-only replay `hpe_audit_local.py`:
* its scalar check (line 75, `assert cur[r]==f …`) enforces frames and the wrapper order;
* its adapter check (lines 50–52) compares an adapter's frame field with `start[r]` or `final[r]`; it checks neither
  the phase nor `cur[r] == f`;
* lines 37 and 39 compare the ordered lists of entry and exit adapters seen by the start of `A` and of the cleanup,
  not where in those prefixes the adapters occur.

It keeps no per-register data-adapter state. Three **scalar-neutral** mutants of the forward program show that it does
not substitute for a tag check:

* **X, exit straddle.** It inserts `[C0 += L; L −= C0] adapter [L += C0; C0 −= L; clear C0]` around target 112's exit
  adapter, at frame 778.
* **Y, entry straddle.** It inserts the same segment around source 0's entry adapter, at frame 9.
* **Z, exit block moved.** It moves the 113 exit adapters of registers 0..112 (events 17219..17331, in order) to just
  before event 15487, `L_112 += −½ L_48` at frame 778 in phase `B`. Z adds no event and puts no scalar in an adapter
  phase.

The pinned `hpe_audit_local.py` **accepts all three**: exit 0, `PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY`,
25 controls rejected. Their exact scalar shadows equal the honest data shear. **Both label checkers reject all three.**

| checker | X | Y | Z |
|---|---:|---:|---:|
| this package's `label_check`, permissive | 2 | 2 | 113 |
| this package's `label_check`, strict | 4 | 2 | 113 |
| patched Lemma G checker (capped at 50 / uncapped) | 4 / 4 | 4 / 4 | 50 / 113 |
| recommended adapter rule (below) | 2 | 2 | 114 |

Z's 113 label violations are the 112 source exit adapters, which find their registers below `(T, FULL)`, and the add
on `L_112` after its exit adapter.

**Exact physical consequences** (PROOF.md §5):

* **X.** Target 112 ends at `a` instead of `A_t a`, where `a` is its content before the exit adapter.
  * `A_t = N_t⁻¹` is the executed exit operator. `N_t` is the serialized target record, applied inverted as in Lemma G
    §4 and `lg_phys.py:84–85`.
  * `N_t` fixes no basis vector, so the output is wrong at every basis vector.
  * At `a = e_0`: the record maps `N_t e_0 = i³ e_11`, and the executed exit gives `A_t e_0 = i³ e_1`. The input
    `h_0 = 0`, `h_112 = T_778⁻¹ e_0` attains `a = e_0`.
* **Y.** Source 0 restores to `T_FULL T_p⁻¹ h_0` instead of `T_FULL T_p⁻¹ M_0 h_0`, when private registers start
  empty. In general it is `T_FULL T_p⁻¹ (h_0 + (I − M_0) c_0)`.
  * This is wrong at `h_0 = e_1`, because `M_0 e_1 = i·e_10`.
  * Target 112 inherits the error.
* **Z.** The 112 moved source exit adapters are identities (`lg_phys.py:86`), so only target 112 changes. Its exit
  adapter `A_t` now runs before `L_112 += −½ L_48` instead of after it, and no other event touches `L_112` in between.
  Honest minus mutant is `(I − A_t) b/2` on `L_112`, where `b` is the content of `L_48` at that add.
  * Witness: `h_48 = M_48⁻¹ T_155 T_778⁻¹ e_0` (frame 155 is `start_48`), all other inputs 0. Then `b = e_0`.
  * The honest target 112 ends at `0`; the mutant's ends at `(i³ e_1 − e_0)/2`.

An independent evaluator shows that all 224 endpoint adapters are non-identity monomials. It is cross-checked against
the pinned `clifford_exact` on the port-0 records.

**The pinned emitter cannot produce these mutants from any word.** It emits no scalar in the adapter phases, and it
emits data adapters only in those phases, at the register's current frame. So κ and the selected word are unaffected:
this is a coverage gap in admission.

**Recommendation.** Harden the selected local replay by running an HPE-aware extended-label check next to it, such as
this package's `label_check` or the patched Lemma G checker. Forbidding scalar events in `entry_adapters` and
`exit_adapters` is **not** enough, because Z has none there. A cheaper rule must at least:
* place every data adapter and every wrapper in its own phase, at `cur[r] == f`. The replay checks `cur` at a wrapper
  only for HPE post wrappers (line 46), and at a data adapter never;
* track per-register adapter state, as the replay already does for wrappers: no scalar or climb on a source before its
  entry adapter, and none on a target after its exit adapter.

`verify.py` implements this rule as `adapter_rule`. It accepts both selected programs and rejects X, Y and Z. It is a
sketch, not proved sufficient for H1; the extended-label check is the complete fix.

## (c) The published Lemma G checker on the selected programs

The checker is `research/e8-lemma-g-lean/code/check_extended_labels.py`. Before this package only two packages ran it:
* #509, on the four historical #484 words;
* #516, from the Lemma A `verify.py`.

The HPE Lean packages (#593, #599) extended the labels in Lean and shipped only `check_hpe_pairs.py`. So the checker
had never run on an HPE word.

1. **As published.** It fails to parse the 5-field HPE wrapper events:
   `ValueError: too many values to unpack (expected 4…)` at event 7675, a cold helper 273 pre wrapper.
2. **5th field stripped.** There are **96 violations per orientation**: the 48 cold hyperplane-ended helpers × 2
   (pre-wrapper tag and end tag). The checker returns at most 50, because of its list cap; 96 is the uncapped count.
3. **Minimally extended.** The patched copy is `patched/check_extended_labels_hpe.py`. It has three marked lines, and
   the original's blob `bc1d9c32…` and SHA-256 `9e072754…` are pinned. Results:
   * **0 violations** in both orientations;
   * its own five mutants are still rejected, with 12, 1, 1, 43 and 1 violations;
   * it rejects all three mutants of (b).

## Reproduce

From the repository root (about 85 s; `phases_full.py` runs concurrently and dominates):

```sh
python3 scripts/research_package.py --package research/selected1094-extended-labels-seed65 --check-only
python3.12 scripts/research_package.py --package research/selected1094-extended-labels-seed65
```

The registered run executes `verify.py` twice: plain, and under `-O`. Every package check raises `ValueError`, and the
pinned producer scripts run in `-I -B` subprocesses from byte copies whose SHA-256 was checked first. The final line is
`PASS_SELECTED1094_EXTENDED_LABELS_AND_ADMISSION_GAP`. Pass `--keep DIR` to inspect the regenerated files.

## Files

| file | content |
|---|---|
| `README.md`, `PROOF.md` | result, Lemma S, Theorem R, the consequences of the three mutants |
| `verify.py` | the verifier (standard library) |
| `EXPECTED.json` | every pinned number |
| `patched/check_extended_labels_hpe.py` | labelled patched copy of the published Lemma G checker |
| `TASK.json`, `SOURCES.json`, `VERIFY.json` | card, scope, pins, registered commands |

## Overlap

* **#1781** (open, Sagar Thakrar). Same selected word. It checks **H2** (every child record and endpoint adapter of
  `CLIFFORD-RECIPES` exact, global phase included). This package checks **H1** and uses #1781 only as independent
  support for H2. The two are complementary.
* **#1282** (merged, Gareth Davidson / bitplane) applies a Lemma G prefix-norm corollary to the same selected programs.
  **#1309** (open, bitplane) formalises that corollary on `LemmaG.Stream`. Both take H1 (`WellLabelled`) and H2
  (`RecipesExact`) as premises.
  * This package discharges the H1 instance they assume, for the selected programs.
  * It also discharges part of the extended-label binding handoff of Discussion #1291 / #1309: the concrete extended
    labels.
  * The row certificate stays theirs, and the recipes stay theirs and #1781's.
* **#509, #516** (Lemma G / Lemma A Lean packages) ran `check_extended_labels.py` only on historical words. **#593,
  #599** (HPE Lean packages) did not run it. This package runs it on the selected word, in its pinned form and a minimal
  HPE extension.
* **#1611** (open, bbMisk) and **#1697** (open, Aaron Wang / navinor) bind wrapper pairs and cold hyperplane operators
  (Lemma A / HPE (N)). Theorem R uses them only through the inherited helper-block evaluation.
* **#729** (open, sk1-j) found a frame-history gap in a standalone interface check. This package finds a tag
  (data-adapter) gap in the selected local replay. Same spirit, different component.
* **#1049** (Sagar Thakrar) and **#1583** (open, Arham-Tahir64) audit leaver cells and helper endpoint rigidity. There
  is no overlap in the checked proposition.

## Open next questions

Structured in [TASK.json](TASK.json) `open_questions`:

1. **Wire an HPE-aware extended-label check into the selected local replay**, with X, Y and Z as negative controls.
   Forbidding scalars in the adapter phases is not enough (Z). A cheaper rule must place every data adapter and wrapper
   in its phase at `cur[r] == f` and track per-register adapter state, like `adapter_rule`; it would still need a
   proof that it implies H1. This closes the admission gap of (b).
2. **Extend to the cross-call data-phase composition.** Theorem R is per call. State the two-call composition in Lemma
   G's event model and identify the junction conditions.
3. **Re-run the Lean build** of `research/e8-lemma-g-lean` (and `hyperplane-end-lean`) on the pinned toolchain. This
   package checks statement text only.
4. **Formalise Lemma S** against an extended Lean emitter model (entry/exit adapter phases and wrappers), so that the
   reading of the pinned Python is no longer a trust step.

## Credit

* **Lemma G / Lemma A Lean packages:** DreamingOfClouds (#509, #516, and #484's Lemma G stage and `lg_phys.py`). They
  build on #425 (Zhihao Chen / jacklightChen), #458 (chafreaky) and #471 (Dugongue).
* **HPE Lean packages:** jeremykothe2 (#593) and DreamingOfClouds (#599).
* **PR635 tools:** jeremykothe2 (#635). As each file's header records, the code adapts #433 (icekylinx), building on
  #425 (Zhihao Chen / jacklightChen) and the #514 replay (Dugongue).
  * It includes jeremykothe2's HPE changes (#591, #592, #601) and DreamingOfClouds' GK (#484) and COLD-HPE (#604)
    changes.
  * `phases_full.py` was adapted by icekylinx and vendored through #558 (eumemic). `clifford_exact.py` comes from #531
    (icekylinx).
* **Slot / leaver / T16 lineage:**
  * rohanarun: #987 slot search; #1094 rare-pattern T16 exchanges, the selected record;
  * jeremykothe2: #1005 mutable-leaver k8 word, #1018 seven slots and `SLOT-PINS-k8`, #1087 T16 owner packing;
  * #1022 T16 controller: jeremykothe2's application of Hao Yan's (FanPUYen) #858 sixteen-replica owner controller.
* **Bit-supplier interface (cited, untouched):** icekylinx's #535 carryover note `PR510-MUTABLE-SOURCE-CARRYOVER.md`.
* **Prefix-norm corollary (overlap):** Gareth Davidson / bitplane (#1282, #1309).
* **Committed bytes:** Ali Romman (`research/k8-frame-antichain`) committed the seven-slot word bytes used here.

Prepared by **Sagar Thakrar with substantial Anthropic Claude assistance**. New material is Apache-2.0. The patched
checker copy keeps its original Apache-2.0 attribution, and its changes are marked.
