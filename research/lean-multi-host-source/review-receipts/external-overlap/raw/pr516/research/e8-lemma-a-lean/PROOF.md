# Lemma A: clean statement and proof

Lemma A of PR #484 (`research/e8-complex-gauge-kernel/PROOF.md` §3) has two parts.

* **Exact part.** For every entrance frame, `S_E = L_E (C_[w] ⊗ I) R_E`, where `L_E` and `R_E` are Gaussian
  monomials. The wrapped product of every entering helper's emitted chain is `C_[w] ⊗ I`. #484 checks this
  numerically.
* **Realization part.** The wrappers surround a whole invocation, and nothing else acts on the helper's stream
  during it. Then the host keeps its assigned residual and identical spectators. #484 assumed this from #458 §3, for
  hosted families and banks, at nine stages.

This package proves the realization part as an abstract theorem in Lean.
* It holds for every chart, every number of stages, and every layout in which the registers of one invocation own
  distinct streams.
* It includes several registers on one family, provided their footprints are disjoint.
* Each hypothesis is checked on the emitted words.

Lean names are in brackets. The objects `Event`, `physRun`, `S`, `WellLabelled` and `RecipesExact` are reused from
the Lemma G package `../e8-lemma-g-lean`.

## 1. Setting: stream units

**Units are physical streams `(F, g)`.** `F` is a family and `g ∈ O(73,2)` is a cover class. This is the model of the
cover construction that #484 inherits:
* the template's `cover` field: "all matrices d in O(73,2)";
* its `loop_order`: "every cover class d; each local invocation completes before the next";
* its `route_semantics`: helper at "physical cover class d*Pi(slot)^(-1)";
* #442's idle-axis hosting (`research/idle-axis-hosting/PROOF.md` §1–2): "on every physical data stream (F, g)", "owned
  by stream (F, d·σ⁻¹)", "eight sequential residuals and a pad tile a bank stream", and the source for distinct streams
  per slot: "Distinct slots of one invocation have distinct σ, so distinct physical classes for every d … They are
  sequential, exactly as the parent's banks are co-owned sequentially by different cover classes";
* #458 §3, only for the convention `g = dσ⁻¹` of the owner cover class.

In this model the pieces fit together as follows.
* **Global state.** A global state is `y : streams → W`, where `W` is the space of functions on a family's address
  cells.
* **Realization.** A local cover sweep runs the invocation once for every class `d`. At class `d`, register `r` is
  realized on the stream `(fam r, d·σ_r⁻¹)` [`streamOwner`]. Here `σ_r` is the register's route: an element of
  `O(73,2)` whose first nine columns are its footprint (its local coordinates on the family). Examples are the slot
  permutation `Π(slot)` of a bank, a host chart, and a data phase `ρ`.
* **Distinct routes, distinct streams.** Two registers of one invocation with different routes own different
  streams, even on one family [`streamOwner_injective`]. Disjoint nonempty footprints give different routes
  [`streamOwner_injective_of_disjoint`].
* **One visit per route.** Over the sweep, a fixed stream `(F, g)` is realized through a fixed route `σ` by exactly
  one class, `d = gσ` [`sweep_unique`; #458 §3: "for a fixed family, d → g is a bijection"]. So a stream receives the blocks of different routes sequentially, from
  different invocations. Those blocks are disjoint (§4), so they commute and tile the stream [`pieces_*`, `gather`].

Lemma A is proved in #442's stream model. That the model describes the machine is inherited from #442, like the
compiler.

**An invocation.** It is a local stream `es` on registers `ι`, as in Lemma G. `ι` includes the private centre copies.
A **hosting** `σ` gives each register an owner unit and a linear chart `chart i : W ≃ M`, made of the route and the
batch of remaining coordinates. In this section `σ` is the hosting; elsewhere `σ_r` is a route.

**Physical execution** [`realize`, `realizeRun`]. Each event reads its operands through their charts. It writes the
destination register's unit back.

**Actions and words** [`Supported`, `evalW`, `Interleave`]. An action is *supported on* `S` if:
* it changes only units in `S`;
* its values on `S` depend only on the input on `S`.

A physical schedule is a word of actions, applied left to right.

## 2. Statement

**Lemma A (realization).** Let `σ` host the invocation `es`, and let `j` be an entering helper. Assume the following.

* **(O) One owner per stream.** The owner map is injective on the registers of the invocation. In the stream model,
  (O) follows from **(O′)**: every data wire is alone on its family, and registers that share a family have pairwise
  disjoint, nonempty footprints.
* **(W) Whole invocation, no other actor.** The physical word interleaves the realized events of `es` only with
  actions supported away from the invocation's units.
* **(E) Exact endpoint (Lemma G).** `es` is well labelled with exact recipes. Row `j` of its scalar shadow is `e_j`,
  and column `j` vanishes off the diagonal.
* **(F) Exact factorization.**
  * The labels are **Lemma G's extended labels**: `λ⁰_j = (prew, j)` and `λ¹_j = (done, j)`. The wrappers are relabel
    events in `es`, so `T_{λ¹_j}T_{λ⁰_j}⁻¹ = L_E⁻¹ S_E R_E⁻¹`. Lemma G's `check_extended_labels.py` checks this
    reading, and `verify.py` runs it.
  * The split `M ≅ A ⊗ B` (residual ⊗ spectators and batch) is chosen per helper.
  * The hypothesis is then `T_{λ¹_j}T_{λ⁰_j}⁻¹ = C ⊗ id`. #484's I-helper check gives it.

Then the following hold.

1. **The whole invocation.** The word equals the complete invocation followed by the other actions
   [`whole_invocation`]. Read through the charts, the invocation is the local run [`realize_run`]. Units that host
   no register are untouched [`realize_untouched`].
2. **The helper's unit.** It ends as `chart_j⁻¹ (C ⊗ id) chart_j` applied to its own initial value [`lemmaA_family`;
   on streams with (O′): `lemmaA_streams`]. On a pure tensor this is `a ⊗ b ↦ C a ⊗ b`: **the spectators are
   untouched** [`spectators_fixed`, `helper_block`].
3. **No other reader.** No other unit's final value depends on the helper's unit [`endpoint_indep`]. The complete
   invocation acts on it as a single-unit piece [`lemmaA_piece`] and splits off [`split_off`].
4. **Pending blocks.** Pieces on disjoint blocks of one pending child commute [`pieces_commute`]. They multiply to
   `C ⊗ D` [`pieces_product`]; for `k` blocks, iterate. Together with the paid remainder they give back the child,
   which is `⊗_b C_b` over its pending axes (#458: "the original idle operator is recovered").

**(O) cannot be dropped within the model** [`one_owner_needed`]. If two registers share a unit, the one-event stream
`scale i 0` changes what register `j` sees, while the local run leaves `j` alone.

**(W) cannot be dropped.** An action that reads the helper's unit between `R_E⁻¹` and `L_E⁻¹` sees `R_E⁻¹h`, not `h`.

**Variant A′ (asynchronous borrowing)** [`lemmaA_async`, `async_window`, `defer`, `gather`]. Suppose every action
between the invocation and the pending child's deadline commutes with the piece of item 3. This holds in either case:
* the action does not touch the piece's unit [`commute_of_not_mem`];
* the action is another piece of the same child on a disjoint block [`pieces_commute`].

Then the schedule equals the one in which the rest of the invocation runs in place and the piece runs just before the
deadline. Gathering the child's pieces gives back the child [`gather`]. The variant's hypotheses are #505's scheduling
conditions. Under them, the owner's history is the original one:
* **window:** each block is used strictly inside its pending child's open window, after the owner's previous data or
  bridge touch and before the child's deadline;
* **blocks:** the blocks of one child are pairwise disjoint;
* **whole invocations:** each invocation is indivisible, with distinct owners.

## 3. Proofs

* **`realize_run`.** Induct over the stream. Realizing an event writes the destination's unit and nothing else.
  Under (O), every other register sits on another unit, so its view is unchanged. The destination's view is its new
  local value.
* **`family_endpoint`, `lemmaA_family`.** A unit's value is `chart⁻¹(view)`, and the view is the local run. Lemma G's
  `row_unit` gives `T_{λ¹}T_{λ⁰}⁻¹` applied to the initial view, and (F) rewrites it.
* **`lemmaA_streams`.** Apply `lemmaA_family` to the hosting `r ↦ (fam r, d·σ_r⁻¹)`.
* **`streamOwner_injective`.** `d·σ⁻¹ = d·σ'⁻¹` forces `σ = σ'` in a group.
* **`streamOwner_injective_of_disjoint`.** Equal routes on one family would give a footprint disjoint from itself, yet
  nonempty.
* **`sweep_unique`.** `d = gσ` is the unique solution of `d·σ⁻¹ = g`.
* **`endpoint_indep`.** Changing the helper's unit changes the view only at `j`. By `conj_matrix`, output `r` is
  `T(Σ_s S_rs T⁻¹h_s)`, and `S_rj = 0`.
* **`commute_of_disjoint`, `shuffle_eval`, `whole_invocation`, `split_off`, `defer`, `async_window`.** Check unit by
  unit, and induct over interleavings and words.
* **`pieces_commute`, `pieces_product`.** Mathlib's `rTensor_comp_lTensor` and `lTensor_comp_rTensor`.

The scheduling and stream results hold over any semiring; `streamOwner_injective` holds over any group. The tensor
results (`lemmaA_family`, `lemmaA_streams`, `lemmaA_piece`, `lemmaA_async`, `helper_block`, `spectators_fixed`,
`pieces_*`) need a commutative semiring.

## 4. Instance hypotheses

| | hypothesis | check | result |
| --- | --- | --- | --- |
| (F) | `L_E⁻¹ S_E R_E⁻¹ = C_[w] ⊗ I` in Lemma G's extended labels | #484 `adapters_gk.py` (`LEMMA-A.json`); #484 I-helper (all 512 columns); Lemma G `check_extended_labels.py` (run by `verify.py`) | headline: 16 frames and 122/122 helpers; gauge80: 80/80; kernel79: 79/79; 0 tag violations |
| (E) | well labelled, exact recipes, unit helper rows, zero helper columns | Lemma G package H1–H3 (#484 G0/G2/G3, I-tr, scalar replay) | 0 violations |
| (O′) | data wires alone; registers sharing a family have disjoint footprints; centre copies in distinct private slots | **new** `code/check_owners.py` (3 mutants rejected) | 0 violations on all four words |
| (W) | calls run to completion; every hosted block strictly inside its pending child's open window | completion: `check_owners.py` tests the template's declared `loop_order` (a declaration, not a structural replay; for #505's asynchronous order the structural check is #505's own audit, replayed here but not re-implemented); windows: **new** `code/check_windows.py` (independent, 2 mutants rejected); #484 `audit_hosted_gk.py` | 0 violations on all four words |
| blocks | the hosted blocks of one pending child are pairwise disjoint; the remainder is the rest | `check_windows.py`; #484 `audit_hosted_gk.py` (remainder ranks) | 0 violations |
| charts | route = permutation of an orthonormal basis, residual first, then spectators | #484 `audit_hosted_gk.py` | PASS |

Data wires and centre copies have a nonempty footprint by construction: their route's first nine columns. So the
Lean hypothesis `hne` holds for them, although `check_owners.py` tests nonemptiness only on shared families.

**Coverage on #484's words** (`check_owners.py`, from the emitted hosted templates):

| word | calls with one register per family | calls sharing a family with disjoint footprints | hosted blocks in their windows |
| --- | --- | --- | --- |
| headline gauge80 + kernel42 | 72/72 | 0 | 39,792 |
| gauge80 | 40/72 | 32 (1,280 registers, #433 pure-bank slots) | 38,112 |
| kernel79 | 56/72 | 16 (1,308 registers, #433 pure-bank slots) | 37,720 |
| anchor | 0/72 | 72 (36,480 registers, #442 hosted slots) | 34,560 |

Every call of every word satisfies (O′). Lemma A therefore covers all calls of all four words, including the
slot-sharing calls of gauge80 and kernel79.

The anchor is not pinned to `EXPECTED.json` and has no wrappers. Its (O′) and windows rest on this package's two
checkers alone. #484's anchor hosting audit is non-strict and is not read.

## 5. Scope

* **#458 and #484.** #458 §3 states the one-helper rule as required, and rejects same-call packing into disjoint slots.
  This package follows #442 §2 instead: distinct routes give distinct physical classes, and streams are co-owned
  sequentially across cover classes. That needs atomic invocations (`loop_order`).
  * The single-owner calls are #458's case: headline 72/72, gauge80 40, kernel79 56, and #505 72/72.
  * The sharing calls rest on #442's model.
* **#433 pure banks and #442 hosted slots.** These are instances through (O′): the slots are disjoint footprints.
* **#471 and #500 (footprint rule).** Several helpers of one invocation on one family, with pairwise disjoint
  nine-coordinate footprints, is exactly (O′). Given their footprint disjointness and windows, these layouts are
  instances. Their words are not checked here. `check_owners.py` and `check_windows.py` read hosted templates in the same
  format and layout: 960 families per replica, 120 ports, and 16 centres for `--async`.
* **#505 (asynchronous whole owners).**
  * Each invocation is whole. Per #505, "all 800 families per invocation are distinct", so (O) holds literally.
  * The cross-replica borrowing is Variant A′.
  * **Replayed here.** #505's own `verify.py` (offline, Python 3.14) passes every stage, including its independent
    asynchronous audit.
    * Two discrepancies remain. Its final comparison of the emitted template's sha256 with #505's `EXPECTED.json`
      fails, although the audit's sigma-stream digest, owner, profile and κ records equal #505's shipped evidence.
      Separately, #505's tree lacks a `.gitattributes` that its MANIFEST lists; that entry was dropped from a scratch
      copy.
    * On the emitted template, `check_owners.py` finds one register per family in 72/72 calls.
    * `check_windows.py` finds all 40,320 hosted blocks strictly inside their owner child's open window, with blocks
      pairwise disjoint and family-group windows disjoint.

    So Variant A′'s owner and window hypotheses hold on the template emitted by replaying #505 (4ee769c) here. That
    template does not hash-match #505's `EXPECTED.json` (template_sha256 aa741871… vs 276b69e3…). The sigma-stream
    digest, owner, profile and κ records equal #505's shipped evidence.
  * Not re-checked here: per-replica order (#505's audit checks it), the prefix bound and its invoice. (E) and (F) are
    not re-checked on #505's word.
* **#512.** It reports 800 distinct physical owners per invocation, and it builds on #505's asynchronous machinery
  and #507's factory. On its own report its invocations meet (O). Its borrowing is Variant A′ under the same
  scheduling conditions. #512's word is not checked here.

## 6. Changes relative to #484 §3

1. **The realization part is proved, not assumed.** It holds for every chart, given one owner per stream.
2. **The unit model is stated.** A unit is a stream `(F, g)`, as in #442 §2. #458 §3 states the one-helper rule as
   required and rejects same-call packing into disjoint slots. This package follows #442 §2 instead: one owner per
   stream, which disjoint footprints imply, with streams co-owned sequentially across cover classes. That needs atomic
   invocations.
3. **"Nothing else acts" is exactly** that the interleaved actions avoid the invocation's units (`whole_invocation`),
   together with the window condition for borrowed blocks.
4. **The spectator claim follows from two facts:** Lemma G's block structure and the exact factorization in the
   extended labels.
5. **(O′), the windows and the block disjointness are now checked independently** on all four words.
   `check_owners.py` and `check_windows.py` can also run on asynchronous templates.
