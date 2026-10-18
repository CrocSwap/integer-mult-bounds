# Proofs: extended labels on the selected #1094 word, and the adapter-straddle gap

All line numbers refer to the pinned bytes at base `0b1cccf8`. `verify.py` checks that each quoted line occurs exactly
once at the stated line (stage 0, pinned in `EXPECTED.json`). Lean is cited, not rebuilt.

## 0. Notation

* The selected word is the seven-slot k8 word `SEVEN-SLOT-WORD.json.gz` (content `c2b29430…`). The pinned PR635
  transport turns it into the canonical word `c` (payload `4ddb29fb…`). It has `v = 112` ports, `R = 480` helpers and
  `n = 704` registers `L_0 … L_703`:
  * sources `L_i` (`i < 112`);
  * targets `L_t`, `t = 112 + i`;
  * helpers `L_224 … L_703`.

  The eight private centre registers are `C_0 … C_7`.
* Frames are rows of `c.frames`. Row 0 is the zero frame and row 1 is `FULL` (dimension 9). `T_F` is
  `canonical_frame(9, F)` of `clifford_exact.py`, with `T_0 = I` and `T_FULL = F_9` (the Fourier gate).
* `p_i` is the routing port of source `i`. Its start frame is the line `span{p_i}`
  (transport `hpe_audit_and_transport.py:211`). The target's final frame is the hyperplane `p_i^⊥`, of dimension 8
  (`:216`).
* Helper sets:
  * `E` = entering helpers, `start ≠ 0` (192);
  * `H` = hyperplane-ended helpers, `final ≠ FULL` (78). Of these, 48 are cold (start 0);
  * `W = E ∪ H` = wrapped helpers (240), as in the emitter `hpe_emit_local.py:68`.
* Endpoint monomials (serialized rank-0 records of `CLIFFORD-RECIPES.json`, from `phases_full.py:24–29`):
  * `M_i` = source port `i`, at frame `start_i`;
  * `N_t` = target port `i`, at frame `final_t`.

  **Executed operators.** The entry adapter of source `i` executes `M_i`. The exit adapter of target `t` executes
  `N_t⁻¹`. This is Lemma G's convention (`research/e8-lemma-g-lean/PROOF.md` §4: "the target's is applied inverted") and
  #484's physical model (`lg_phys.py:79–80` applies the source record, `:84–85` applies the target record with
  `inverse=True`). It also matches how `phases_full.py` builds the records: the target record is `T_final ∘ (F C_q⁻¹)⁻¹`,
  and a `new_to_old` conversion executes its inverse.
* Wrappers `R_{E,U}`, `L_{E,U}` are Lemma A / HPE's (`hyperplane-end-lean/PROOF.md` §2). A cold helper has `E = 0`.

## 1. Extended labels for HPE words

A label is a pair (tag, frame). Following Lemma G §4 (`e8-lemma-g-lean/PROOF.md:119`), with HPE's arbitrary terminal
frame:

| tag | carried by | operator `T_(tag, F)` |
|---|---|---|
| `T` | every register in the word's family | `T_F` |
| `(pre, i)` | source `i` before its entry adapter | `M_i⁻¹ T_F` |
| `(post, t)` | target `t` after its exit adapter | `N_t⁻¹ T_F` |
| `(prew, j)` | wrapped helper `j` before `R_{E,U}⁻¹` | `R_{E_j,U_j} T_F` |
| `(done, j)` | wrapped helper `j` after `L_{E,U}⁻¹` | `L_{E_j,U_j}⁻¹ T_F` |

**Reading the emitted JSON as Lean `Event`s** (`LemmaG/Stream.lean:29–34`):
* `climb r a b` is `relabel L_r (T,a) (T,b)`, and `center k a b` is `relabel C_k (T,a) (T,b)`.
* A source entry adapter is `relabel L_i ((pre,i),f) (T,f)`. A target exit adapter is
  `relabel L_t (T,f) ((post,t),f)`. Every other adapter is `relabel (T,f) (T,f)` at `f = 0` (entry) or `FULL` (exit).
* The pre wrapper is `relabel L_j ((prew,j),E_j) (T,E_j)`. The post wrapper is `relabel L_j (T,U_j) ((done,j),U_j)`.
* Scalars map as follows:
  * `add X Y a b` is `add X Y (a/b)`, and `scale X a b` is `scale X (a/b)`;
  * `copy C L_r` at `f` is `copy C L_r (T,f)`;
  * `clear C` at `f` is `clear C F`. The **strict reading** sets `F = (T,f)`. The **permissive reading** takes `F` to be
    the label of the register's next use, which is legal because Lean's `clear` is always admissible.

**Initial and final labels.**

| register | `λ⁰` | `λ¹` |
|---|---|---|
| source `i` | `((pre,i), start_i)` | `(T, FULL)` |
| target `t` | `(T, 0)` | `((post,t), p^⊥)` |
| wrapped helper `j` | `((prew,j), E_j)` | `((done,j), U_j)` |
| other helper | `(T, 0)` | `(T, FULL)` |

Private registers are free.

**H2 in these labels.** Lean's `RecipesExact` (`Stream.lean:111`) asks every relabel `A → B` to execute `T_B T_A⁻¹`:
* **Climbs and centre steps.** This is the child-record content of `CLIFFORD-RECIPES.json`, pinned as `d0768f21…`.
  `lower_child` asserts tableau and zero-state equality when it generates the records. Open PR #1781 re-checks this
  independently on all 512 columns; it is not merged and is not re-run here.
* **Adapters and wrappers.** These are exact by the definition of the table above, provided the **bridge** holds:
  * each source converts once, by `M_i`, and each target once, by `N_t⁻¹`;
  * every other adapter executes the identity at `0` or `FULL`;
  * each wrapped helper has exactly one pre wrapper and one post wrapper, keyed by `(E_j, U_j)`.

## 2. Structural lemma: every emitter output carries the right tags

**Lemma S.** Let `W` be any word that the pinned transport accepts with the pinned routing word `R₀`, and on whose
canonical form the pinned emitter runs to completion. Then, in both emitted programs:

* **(i) Tags.** Every operand of every scalar event carries tag `T`, and every relabel finds the tag it converts from.
  The bridge holds and the programs end with the tags of `λ¹`.
* **(ii) Frames.** Every relabel finds its source frame, and every scalar operand sits at the event's annotated
  frame, with one possible exception: a centre-phase scatter `add` for a cut gate that does not write a target.

So if every cut gate writes a target, each program is `WellLabelled` (`Stream.lean:106`) from `λ⁰` in the extended
labels, under the strict reading, ends at `λ¹`, and satisfies the bridge. This covers every word the selected chain
admits, because the frame-only replay rejects that exception (`hpe_audit_local.py:75`). For the selected word,
`verify.py` checks directly that all 176 cut gates write targets from centres.

*Facts used* (quoted and line-checked by `verify.py`; line numbers are in `hpe_emit_local.py` unless another file is
named):

* **(F1) Ports.** The canonical ports are `R₀`'s ports (transport `:182`). All 112 are nonzero and distinct, which is
  checked on `R₀`, so it holds for every accepted word. Hence:
  * `start_i = span{p_i} ≠ 0` (transport `:211`);
  * `final_t = p_i^⊥` has dimension 8, so `final_t ≠ FULL` (transport `:216`).
* **(F2) Helpers.** Every hyperplane-ended helper has `final ≠ FULL` (transport `:268`). The emitter's wrapped set is
  `{start ≠ 0} ∪ {final ≠ FULL}` (`:64–68`). It is contained in the transport's `start_extra ∪ helper_final`.
* **(F3) Zero-frame precondition.**
  * Every register touched by `precondition + compensation` has start frame 0 (`:59`).
  * None is an entering helper (transport `:160`) or a cold hyperplane-ended helper (transport `:157`). An entering
    hyperplane-ended helper counts as entering.

  By (F1) and (F2), the touched registers are therefore targets and unwrapped helpers, never sources or wrapped helpers.
* **(F4) Phase layout.** Scalars are emitted only in these phases:
  * `zero_frame_precondition`, at frame 0 (`:56–60`);
  * `A`, `centers`, `B`, `cleanup_tail` (`:80–110`). In `A`, `B` and `cleanup_tail`, both registers of a gate are
    first climbed to the gate's frame (`:85–86`);
  * `full_frame_cleanup`, at `FULL` (`:116–120`).

  The other phases contain no scalars:
  * `entry_adapters` emits exactly one entry event per register: a pre wrapper if `r ∈ W`, otherwise an adapter at
    `start_r` (`:69–71`);
  * `final` emits only climbs to `final_r` (`:112`);
  * `exit_adapters` emits exactly one exit adapter at `final_r` per register outside `H` (`:113–115`);
  * post wrappers follow the cleanup (`:121`).

  Data adapters are emitted only in `entry_adapters` and `exit_adapters`. Each sits at its register's current frame:
  `start_r` before any climb, or `final_r` after the final climbs.
* **(F5) FULL cleanup.** Every register touched in `full_frame_cleanup` has `final = FULL` (`:119`).
  * None is a target, because target finals are the hyperplanes `p^⊥` (F1).
  * None is hyperplane-ended (F2).

  So each is a source or a FULL-ended helper, and its exit adapter, if any, is an identity at `FULL`.
* **(F6) Centres.** The emitter asserts at the start of the phase that every target sits at its level `lv(t)` (`:91`),
  and that each centre register sits at its centre frame `cf` (`:93`).
  * The private copy `C_k` is cleared and copied at `cf` (forward), or cleared at the lowest level (backward).
  * It is relabelled one step at a time along the chain `path` (`:95–110`).
  * Each scatter `add` runs at `path[a] = lv(e[1])` (`:102`, `:108`).
* **(F7) Climbs.** The emitter tracks the current frame `cur`. It emits a climb only from `cur[r]`, and only as a
  nested ascent (`:72–77`).

*Proof.* Track each register's label as (tag, frame).

**Tags.** By (F4), tags change only at adapters and wrappers.
1. Before `entry_adapters`, sources carry `(pre,i)`, wrapped helpers carry `(prew,j)`, and every other register
   carries `T`.
2. In `entry_adapters`, every register receives exactly one entry event, and it finds the tag it expects.
   * Sources and wrapped helpers are untouched before this phase, by (F3).
   * Targets and unwrapped helpers keep `T` through an identity adapter at frame 0. Their start frame is 0: for
     targets by transport `:211`, and for unwrapped helpers because they are not entering.
3. From phase `A` through phase `final` there are no adapter or wrapper events, so **every `L` register has tag `T`**.
   Private copies are copied from, or added to, `T`-tagged registers and relabelled only by centre steps, so they are
   also `T`.
4. In `exit_adapters`:
   * targets go `T → (post,t)`;
   * sources and FULL-ended helpers keep `T` through identity adapters at `FULL`;
   * hyperplane-ended helpers have no exit event.
5. Post wrappers come after the cleanup. They take wrapped helpers from `T` to `(done, j)`.

Now take any scalar event:
* **`zero_frame_precondition`.** Its registers are targets or unwrapped helpers (F3), still tagged `T` (step 1).
* **`A`, `centers`, `B`, `cleanup_tail`.** Everything is tagged `T` (step 3).
* **`full_frame_cleanup`.** Its registers are sources or FULL-ended helpers (F5), tagged `T` (step 4). Entering
  FULL-ended helpers are still `T`, because their post wrapper comes later (`:121`).
* **`entry_adapters`, `exit_adapters`, `done`.** There are no scalars (F4).

This proves (i).

**Frames.** The emitter's `cur` is the frame component of every `L` label (F7). We check each phase:
* **Precondition.** No climb precedes it. Its registers start at 0, and its gates are at 0 (F3, F4).
* **Entry adapters and pre wrappers.** They sit at `start_r`, with no climb before them.
* **`A`, `B`, `cleanup_tail`.** Each gate's two registers are climbed to its frame immediately before the gate (F4).
* **Centres.** By (F6), every operand sits at the gate's frame, provided the scatter target `e[1]` is a target. Then
  its frame is `lv(e[1])`.
* **Final climbs, exit adapters and post wrappers.** After the final climbs every register is at `final_r`. Exit
  adapters sit there. No later event changes a frame, so post wrappers also find `final_r = U_j`.
* **Cleanup.** Its registers are FULL-final (F5), so they sit at `FULL`, where its gates run.

Private clears are consistent with the strict reading:
* forward: clear at `cf`, then copy at `cf`;
* backward: clear at `path[-1]`, whose first use is an `add` at `path[-1]`. That level is a served level, or `cf` when
  `path = [cf]`.

This proves (ii).

**Conclusion.** Together, (i) and (ii) give G0 in the extended labels at every scalar event. G0 is stronger than Lean's
`Admissible`, where `add` needs `λ_t = λ_s` (`Stream.lean:70`). Every relabel finds its source label. Hence the program
is `WellLabelled` and ends at `λ¹`.

The bridge is steps 2 and 4 plus the post wrappers. The serialized adapters are exactly:
* the 112 source records at `start_i`;
* the 112 target records at `final_t` (`phases_full.py:25–29`). ∎

**Corollary.** No program produced by the pinned emitter, from any word, has a scalar event in `entry_adapters` or
`exit_adapters`, or a data adapter outside those phases or away from its register's current frame (F4). None of the
three mutants of §5 is an emitter output:
* X and Y put scalars in an adapter phase;
* Z puts 113 exit adapters in phase `B`, and 112 of them away from their register's frame.

Lemma S is a paper proof over the pinned Python. It is quantified over all accepted words, but it is not formalised
(see the open questions). `verify.py` checks its instance on the selected word directly (§3), under both readings.

## 3. Instance: the selected word

Everything in this section is regenerated from committed bytes; `verify.py` runs stages 2–3:
* canonical payload `4ddb29fb…`, programs `071ecdac…` (forward) and `f36c5831…` (backward), and `CLIFFORD-RECIPES`
  `d0768f21…`;
* `SLOT-PINS-k8` (#1018) and the #1094 `PLAN.json` provider registry name the same four hashes.

| | forward | backward |
|---|---:|---:|
| events | 24,767 | 24,767 |
| extended-label violations, strict / permissive | 0 / 0 | 0 / 0 |
| scalar events (precondition 7,400; A 3,451; centres 200; B 1,846; tail 116; cleanup 6,680) | 19,693 | 19,693 |
| climbs / centre steps | 3,486 / 8 | 3,486 / 8 |
| entry adapters / exit adapters / pre wrappers / post wrappers | 464 / 626 / 240 / 240 | 464 / 626 / 240 / 240 |
| source writes (`add`/`scale` whose target is a source) | **1,497** | **3,924** |

**Source writes by phase.**
* Forward (1,497): A 730, B 60, tail 2, cleanup 705.
* Backward (3,924): A 865, B 218, centres 5, tail 26, cleanup 2,810.

**Other instance facts.**
* 5 of the 8 centres are sources. In the backward centre phase each of them is written once, by `L_r += −C_k`.
* The precondition touches 352 registers: 112 targets and 240 unwrapped helpers.
* The cleanup touches 514: 112 sources and 402 FULL-ended helpers.
* No private register is read before its first clear.
* An independent exact scalar replay gives the data shear (**H3**), in both orientations:
  * forward: source rows `e_i`, target rows `e_t + e_i`;
  * backward: source rows `e_i − e_t`, target rows `e_t`;
  * helper rows are unit rows, and private rows and columns are zero.

**Controls.** Both readings reject 28 edits of the forward program and 27 of the backward program; each count is pinned:
* the five edits of the published checker's `mutants()`;
* an HPE wrapper without its terminal field, and a tail gate moved into the FULL cleanup;
* edits aimed at single clauses of the checker, listed in README (a) and in `control_edits`. Each targets one condition:
  an adapter's or wrapper's frame or label, an unknown kind, the phase order, a wrapper key, or a bridge count. The
  forward program has one more: its centre copy taken from a register at a wrong frame.

Only the strict reading rejects one further edit, a scale annotated at a wrong frame. Lean's `Admissible` asks nothing
of `scale`.

**Clause coverage.** The checker's conditions split into 32 clauses (one disjunct each; the list is `WEAKENINGS` in
`verify.py`). `verify.py` weakens each alone, in memory, and re-runs the checker on all 62 pinned inputs: the two
programs, the 57 controls and the three mutants of §5. 31 weakenings change a pinned value. The survivor is "a source
entry adapter is keyed at `start_i`". It is implied by the clause "it finds `((pre,i), f)`". A `(pre,i)` label starts at
frame `start_i` and is only ever passed on unchanged: by a copy, or, under the permissive reading, by an add into a free
private register. Every event that sets a frame also sets a tag other than `(pre,i)`. These are controls of the checker,
not a proof of it. Lemma S is the proof.

## 4. Scoped theorem: per-call common-label / mutable-source realization (complex supplier)

**Theorem R.** Let `es` be the selected word's forward or backward program. Let `M` be `ℂ^{2^9}`, or `ℂ^{2^9} ⊗ V`
with every operator acting on the first factor. More generally, let `M` be any `ℚ`-module on which the same operators
`T_F`, `M_i`, `N_t`, `R_{E,U}`, `L_{E,U}` act as `ℚ`-linear automorphisms and the same recipes `rec` satisfy H2. Then
for **every** `h ∈ M^{registers}`, with arbitrary dirty contents in sources, targets, helpers and private registers:

`physRun rec es h = D(λ¹) · S · D(λ⁰)⁻¹ h`, register by register (Lean `Stream.conj_matrix`, `Stream.lean:294`).

Here `S` is the data shear of §3.

*Proof.* `conj_matrix` holds for any semiring `K`, any `K`-module `M` and any label family. Its hypotheses are
`RecipesExact` (H2, §1) and `WellLabelled` (H1, Lemma S and §3). `S` is the exact scalar shadow (H3, §3). ∎

**Rows in the forward orientation.**
* Source `i`: `T_FULL T_{p_i}⁻¹ M_i h_i`.
* Target `t = 112+i`: `N_t⁻¹ T_{p_i^⊥} (h_t + T_{p_i}⁻¹ M_i h_i)`.
* Wrapped helper `j`: `L_{E,U}⁻¹ T_U T_E⁻¹ R_{E,U}⁻¹ h_j`.
* Other helpers: `T_FULL h_j`.
* Private registers: `0`.

The backward rows are analogous.

**What this means.**
* *Common label:* every scalar gate acts on operands with equal labels.
* *Mutable source:* sources are written 1,497 / 3,924 times, yet each source ends exactly at its shadow row's value. In
  the forward orientation that is its own converted input `T_FULL T_{p_i}⁻¹ M_i h_i`. In the backward orientation it is
  `T_FULL (T_{p_i}⁻¹ M_i h_i − h_t)`.

The private columns of `S` are zero, so dirty private inputs never matter.

**What stays inherited** (not proved here). Four parts of the retained common-label / mutable-source interface are
untouched:
1. **All-size / compiler.** H2 is a statement about 9-qubit recipes `L (C_[r] ⊗ I) R` acting on `ℂ^{2^9}`. The
   selected construction executes a rank-`r` climb by recursive children at every size. That execution is the retained
   all-size/compiler interface.
2. **Whole-call hosting and footprints.** These are Lemma A's (O′) disjoint footprints and (W) whole invocations
   (`research/e8-lemma-a-lean`): how calls share physical registers under the T16 owner map.
3. **Composition of data phases across calls.** Theorem R is per call.
4. **The bit supplier's realization.** Theorem R is about the complex supplier's local programs only. The bit
   supplier's common-label / mutable-basis realization is the role-independent carryover argument of #535's
   `PR510-MUTABLE-SOURCE-CARRYOVER.md` (`:13–14`). The bit packages keep it as a listed conditional interface
   (`research/e8-bit-r420/README.md:113–118`; `research/e8-bit-p111-tuned/tune/README.md:84`). This package checks no
   bit word.

Two further retained obligations are used, not proved:
* **Precision and tape.** Theorem R is exact arithmetic over the module; the finite-precision and tape contracts stay
  inherited.
* **Lemma A's (N) for the wrapper pairs.** Evaluating the wrapped helper rows `L_{E,U}⁻¹ T_U T_E⁻¹ R_{E,U}⁻¹` to
  `C_[w] ⊗ I` is Lemma A / HPE (#516, #593, #599), with instance bindings in open #1611 and #1697.

Further limits:
* The Lean build of `research/e8-lemma-g-lean` is **not** re-run. `verify.py` checks only the statement text.
* #1781 is open, and H2 is otherwise the producer's own generation-time assertion.

## 5. The admission gap: no tag check in the selected chain, and the frame-only replay does not substitute for one

**Where H1 is checked.** H1 has a frame half and a tag half.
* Lemma G assigns the tag half to `check_extended_labels.py` (`e8-lemma-g-lean/README.md:50`). That checker cannot run
  on HPE words (§6).
* The HPE package maps only G0 in `cleanup_tail` (`hw`, tail shape, `hmv`) to `audit_local.py`
  (`hyperplane-end-lean/PROOF.md:104`). In `cleanup_tail` every operand has tag `T` (Lemma S, step 3).

So the selected chain runs no tag check. The only stage found in it that reads the emitted events is the PR635
frame-only replay `hpe_audit_local.py`; `emit_allcold.py` and `audit_allcold.py` bind the programs and this replay's
receipt by hash. What it checks:
* Its scalar check (`:75`) asserts the frame (`cur[r]==f`) and the wrapper order. The wrapper order is the
  `prew`/`done` part of the tag discipline.
* Its adapter check (`:50–52`) compares the adapter's frame field with `start[r]` or `final[r]`. It checks neither the
  phase nor `cur[r] == f`.
* At the start of `A` (`:37`) and of the cleanup (`:39`) it compares the ordered lists of adapters seen so far, not
  where they occurred.

It records no per-register state for data adapters, and allows scalar events inside the adapter phases.

**Proposition P (falsified): the frame-only replay substitutes for the tag check.** "If a pair of programs for the
selected canonical word is accepted by the pinned `hpe_audit_local.py`, then it is `WellLabelled` in the extended
labels, so its physical run is `D(λ¹) S D(λ⁰)⁻¹`."

**Counterexamples.** All three are edits of the forward program only. X and Y each insert 5 scalar events, all at the
adapter's frame:

`[C0 += L; L −= C0]  adapter  [L += C0; C0 −= L; clear C0]`

* **X (exit straddle):** `L = L_112` (target of port 0) around its exit adapter at frame 778 (event 17331).
* **Y (entry straddle):** `L = L_0` (source 0) around its entry adapter at frame 9 (event 7402).
* **Z (exit block moved):** no event is added. The 113 exit adapters of registers 0..112 (events 17219..17331, in
  order) move to just before event 15487, `['scalar',['add',['L',112],['L',48],-1,2],778]` in phase `B`. 112 of them
  are the identity exit adapters of the sources, at `FULL`; the last is target 112's at frame 778.

| | X | Y | Z |
|---|---|---|---|
| pinned `hpe_audit_local.py` | exit 0, `PASS_…`, 25 controls | exit 0, `PASS_…`, 25 controls | exit 0, `PASS_…`, 25 controls |
| exact scalar shadow | equal to honest | equal to honest | equal to honest |
| label checker, permissive | 2 violations (events 17334, 17335) | 2 (7405, 7406) | 113 (15487–15598, 15600) |
| label checker, strict | 4 (17331, 17332, 17334, 17335) | 2 (7402, 7403) | 113 (the same events) |
| patched Lemma G checker (capped at 50 / uncapped) | 4 / 4 | 4 / 4 | 50 / 113 |
| `adapter_rule` (recommended below) | 2 | 2 | 114 |

Z's 113 violations are the 112 moved source exit adapters, which find their registers below `(T, FULL)`, and the add
(now event 15600), which finds `L_112` at `((post,112), 778)`.

**Segment algebra of X and Y** (checked symbolically by `verify.py`). Let `X` be the adapter operator, `a` the content
of `L` and `c` the content of `C0` just before the segment.
* Honest: `L = X a`, `C0 = c`.
* Mutant: `L = a + c − X c`, `C0 = 0`.

**Exact consequence of X.**
* The last event on `C0` before the insertion is a clear (event 12576), so `c = 0`.
* No event after the exit adapter touches `L_112`.
* Every other register evolves identically.

So the mutant leaves target 112 at `a`, while the honest program ends at `A_t a`, where `A_t = N_t⁻¹` is the executed
exit operator. The two differ iff `A_t a ≠ a`.

`N_t` fixes no basis vector (0 of 512), so the outputs differ at every basis vector. At `a = e_0`:
* `N_t e_0 = i³ e_11` (the serialized record's action);
* the executed exit gives `A_t e_0 = N_t⁻¹ e_0 = i³ e_1 ≠ e_0`.

`a = e_0` is attained. By Theorem R applied to the honest prefix, with the target's shadow row `e_112 + e_0` just
before the exit adapter (checked):

`a = T_778 (h_112 + T_9⁻¹ M_0 h_0)`.

So the input `h_0 = 0`, `h_112 = T_778⁻¹ e_0` gives `a = e_0`. On it the honest output is `i³ e_1` and the mutant's is
`e_0`.

**Exact consequence of Y.**
* No event before source 0's entry adapter touches `L_0` or `C0`, so at the insertion `L_0 = h_0` and `C0 = c_0`, the
  initial private content.
* After the segment, `L_0 = h_0 + (I − M_0) c_0` and `C0 = 0`. The honest values are `M_0 h_0` and `c_0`.
* The honest program's next event on `C0` is a clear (event 12551).

So the mutant run on `h` equals the honest run on `h'`, where `h'_0 = M_0⁻¹ (h_0 + (I − M_0) c_0)` and `h'` agrees with
`h` elsewhere. By Theorem R (forward source row `e_0`), source 0 ends at

`T_FULL T_9⁻¹ (h_0 + (I − M_0) c_0)`,

which is `T_FULL T_9⁻¹ h_0` when private registers start empty, as in all pinned replays. The correct value is
`T_FULL T_9⁻¹ M_0 h_0`.

With `c_0 = 0` the two differ iff `M_0 h_0 ≠ h_0`. Witness: `M_0 e_1 = i·e_10`. Source adapters fix 256 of 512 basis
vectors with phase 0; for example `M_0 e_0 = e_0`, so the witness must avoid `e_0`. Target 112 also inherits the
error, through its row `e_112 + e_0`.

**Exact consequence of Z** (each step checked by `verify.py`).
* The 112 moved source exit adapters are identity relabels `(T,FULL) → (T,FULL)`. Under H2 they execute `I`, and
  #484's physical model skips them (`lg_phys.py:86`). Moving them changes no content.
* Write `g` for the add `L_112 += −½ L_48` (honest event 15487). The honest program touches `L_112` at `g` and next at
  its exit adapter (event 17331), and at no event in between. `A_t = N_t⁻¹` acts on `L_112` alone and does not read
  `L_48`.
* So only the order of `g` and `A_t` differs, and only `L_112` changes. Let `a` and `b` be the contents of `L_112` and
  `L_48` just before `g`. Then (swap algebra, checked symbolically):
  * honest: `L_112 = A_t (a − b/2) = A_t a − ½ A_t b`;
  * mutant: `L_112 = A_t a − b/2`;
  * honest − mutant `= (I − A_t) b/2`.

**Witness for Z.** Just before `g`, the honest shadow rows have coefficient 1 on column 48 in `L_48`'s row and ½ in
`L_112`'s row (checked). Both registers carry `(T, 778)` there. `start_48` is frame 155, so `T(λ⁰_48) = M_48⁻¹ T_155`.
By Theorem R applied to the honest prefix, on the input with `h_48 = M_48⁻¹ T_155 T_778⁻¹ e_0` and all other inputs 0:
* `b = T_778 (1 · T_155⁻¹ M_48 h_48) = e_0`, and `a = e_0 / 2`.
* The honest target 112 ends at `A_t (a − b/2) = 0`.
* The mutant's ends at `A_t a − b/2 = (A_t e_0 − e_0)/2 = (i³ e_1 − e_0)/2`, using `A_t e_0 = N_t⁻¹ e_0 = i³ e_1` (§5,
  X).

Every other register ends as in the honest run.

**All 224 endpoint adapters are non-identity monomials.** This uses an independent evaluator of the rank-0 record
semantics: `D(Q,α)`, then `P(G)`, then `X(b)`, then `i^phase`, as in `clifford_exact.monomial`.
* For both port-0 records, all 512 columns are cross-checked against the pinned `clifford_exact` circuit semantics.
* Source records fix exactly 256 basis vectors each, and target records fix none.

**Downstream.**
* By the Corollary of §2, the pinned emitter cannot produce X, Y or Z from any word.
* The selected programs are emitter outputs, bound by hash, and satisfy H1 (§3). So **κ and the selected word are
  unaffected**.

The finding is a coverage gap in admission. The admission check, read as a specification, would accept a future
emitter or a substituted program that breaks restoration while keeping every frame and scalar identity.

**Recommendation.** Run an HPE-aware extended-label check (this package's `label_check` or the patched Lemma G
checker) next to the frame-only replay. Forbidding scalar events in `entry_adapters` and `exit_adapters` does **not**
close the gap: Z has none there. A cheaper rule must at least:
* place every data adapter and every wrapper in its own phase, at `cur[r] == f`. The replay checks `cur` at a wrapper
  only for HPE post wrappers (`:46`), and at a data adapter never;
* track per-register adapter state, as the replay does for wrappers: no scalar or climb on a source before its entry
  adapter, and none on a target after its exit adapter.

`verify.py` implements this rule as `adapter_rule`. It finds 0 offending events in both selected programs, and 2, 2 and
114 in X, Y and Z. It is a sketch: it is not proved to imply H1, which the extended-label check decides directly.

## 6. The published Lemma G checker, three ways

The checker is `research/e8-lemma-g-lean/code/check_extended_labels.py` (blob `bc1d9c32…`). Before this package it was
run only by #509's `verify.py` (on the four historical #484 words) and #516's Lemma A `verify.py`. The HPE Lean packages
#593 and #599 extended the labels in Lean and shipped only `check_hpe_pairs.py`, so it had never run on an HPE word.

Its top-level `from lg_lib import load` is used only by `main()`, so `verify.py` serves it with a stub and calls
`check()` and `mutants()` directly.

1. **As published.** `ValueError: too many values to unpack (expected 4…)` at the first 5-field HPE wrapper, event
   7675 `['residual_adapter','pre',273,0,124]` (cold helper 273, `U` = frame 124), in both orientations. The message
   suffix depends on the Python version.
2. **5th field stripped.** There are 96 violations per orientation: 48 `pre wrapper … tag T` and 48
   `register … ends with tag ('done', r)`. They are exactly the 48 cold hyperplane-ended helpers, each counted twice,
   because the published checker treats only `start ≠ 0` helpers as wrapped.
   * The checker caps its returned list at 50 (`bad = lambda m: … if len(viol) < 50`), so it returns 50 entries.
   * 96 is the count with that one line uncapped, applied in memory.
3. **Patched copy** (`patched/check_extended_labels_hpe.py`). The original is pinned in the header and in
   SOURCES.json. Three marked lines differ:
   * cold-HPE helpers are wrapped;
   * the 5th field `U` is accepted;
   * `U` must equal the helper's final frame.

   `verify.py` rebuilds the file from the pinned original and compares bytes. Results:
   * **0 violations** in both orientations;
   * its own five mutants are still rejected, with 12, 1, 1, 43 and 1 violations, identically in both orientations;
   * it rejects all three mutants of §5: X and Y with 4 violations each, Z with 113 (it returns 50, its cap).

## 7. Not claimed

The following are not claimed:
* no new κ or construction;
* no Lean build;
* no proof of the all-size compiler, whole-call hosting, precision and tape, Lemma A's (N) for the wrapper pairs, or
  cross-call composition;
* nothing about the bit supplier: its common-label / mutable-basis realization (#535) stays a retained interface;
* no claim that `adapter_rule` implies H1;
* no claim that #1781's independent H2 check has been reviewed or merged.

Lemma S is a paper proof over pinned Python, not a formal one.
