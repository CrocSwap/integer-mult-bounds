# Lemma G: clean statement and proof

Lemma G is the entrance-gauge lemma of PR #484 (`research/e8-complex-gauge-kernel/PROOF.md` §2): target-side compensation at nonzero
frames, labelled targets, and the centre scatter along a chain. This file splits it into

* **(i) an abstract lemma**, proved once for all: Theorems 1–4 below, formalised in Lean (`LemmaG/*.lean`, names in brackets), and
* **(ii) instance hypotheses H1–H6** on the emitted streams, checked exhaustively by Python: #484's stage `code/lemmaG/` and
  this package's `code/check_extended_labels.py`.

§5 lists what changed relative to #484's §2.

## 1. Setting

* `K` is a semiring and `M` is a `K`-module. For the word, `K = Q` and `M = C^(2^9)`, which is a `Q`-module.
* `Λ` is a set of labels. `T : Λ → (M ≃ₗ[K] M)` gives each label a linear automorphism. Nothing else about `T` is used.
* `ι` is a finite set of registers. A state is `h : ι → M` and a labelling is `λ : ι → Λ`.
* The events and their effects:

| event | physical effect | label effect | admissible at `λ` iff |
| --- | --- | --- | --- |
| `relabel r A B` | `h_r ← rec(A,B) h_r` | `λ_r := B` | `λ_r = A` |
| `add t s q` | `h_t ← h_t + q·h_s` | none | `λ_t = λ_s` |
| `scale t q` | `h_t ← q·h_t` | none | always |
| `copy c r F` | `h_c ← h_r` | `λ_c := F` | `λ_r = F` |
| `clear c F` | `h_c ← 0` | `λ_c := F` | always |

* `rec(A,B)` is the operator the hardware executes, i.e. the serialized recipe.
* A stream `es` is **well labelled** from `λ⁰` if every event is admissible at the labels current when it runs (`WellLabelled`).
* Its **recipes are exact** if every `relabel r A B` in `es` executes `T_B T_A⁻¹` (`RecipesExact`).
* `λ¹ = labRun es λ⁰` is the final labelling.
* The **scalar shadow** `scal_es` is `es` with every relabel deleted, run on any `K`-module (`scalRun`).
* Its matrix is `S_rs := (scal_es e_s)_r` over `K` (`S`). Here `e_s` is the basis column.
* `D(λ)h := (T_{λ_r} h_r)_r` (`D`, `Dinv`).

## 2. Exactness

**Theorem 1 (common-frame conjugation)** [`Stream.conj`, `Stream.conj'`, `Stream.conj_matrix`]. Let `es` be well labelled from `λ⁰`, with exact recipes.
* Operator form: `physRun es = D(λ¹) ∘ scal_es ∘ D(λ⁰)⁻¹`.
* Matrix form: for every input `h` and every register `r`,

  `h_r(final) = T_{λ¹_r} ( Σ_s S_rs · T_{λ⁰_s}⁻¹ h_s ).`

*Proof.* The operator form is the invariant `h = D(λ)ℓ`. Here ℓ runs the scalar shadow and λ runs the labels. We check one event at a time (`Stream.step`):
* A relabel with `λ_r = A` maps `T_A ℓ_r` to `T_B T_A⁻¹ T_A ℓ_r = T_B ℓ_r`, and the label becomes `B`.
* An add with `λ_t = λ_s = F` gives `T_F ℓ_t + q·T_F ℓ_s = T_F(ℓ_t + q·ℓ_s)`.
* A scale commutes with `T_F`.
* A copy with `λ_r = F` gives `T_F ℓ_r` under the new label `F`.
* A clear gives `0 = T_F 0`.

Induct over the stream, then start from `ℓ = D(λ⁰)⁻¹h`.

For the matrix form: every event commutes with any `K`-linear map applied register-wise (`scal_map`), and the shadow is additive (`scalRun_add`). Write `h = Σ_s e_s ⊗ h_s`. Then the shadow acts on any module through `S` (`scalRun_eq_sum`). ∎

**The row form of `S`** [`Stream.S_rowform`]. `S_rs` is the coefficient of `e_s` in register `r` after one symbolic replay in which register `i` holds `e_i`. #484's `lg_lib.scalar_replay` computes exactly this:
* each register is a dict of coefficients;
* private copies start empty.

On inputs whose private registers are empty, the columns of the private registers do not contribute, because `T⁻¹0 = 0`.

**Corollary 2 (the word's rows)** [`Stream.row_unit`, `Stream.row_pair`].
* If row `r` of `S` is `e_r`, then `h_r(final) = T_{λ¹_r} T_{λ⁰_r}⁻¹ h_r`.
* If row `r` is `e_r + a·e_{s₀}`, then `h_r(final) = T_{λ¹_r}(T_{λ⁰_r}⁻¹ h_r + a·T_{λ⁰_{s₀}}⁻¹ h_{s₀})`.

## 3. Schedule and accounting

Frames form a partial order with a **strictly monotone rank** (`rk A < rk B` whenever `A < B`). The subspaces of F₂⁹, with inclusion and dimension, are an instance [`frameRank_strictMono`].

**Lemma 3.0** [`le_of_rk_le`, `eq_of_rk_eq`]. If `A`, `B` are comparable and `rk A ≤ rk B`, then `A ≤ B`; equal rank gives `A = B`.
* *Proof.* If `B < A`, then `rk B < rk A`. ∎

**Emitter.** A schedule is a list of gates `(mover, partner, frame F, q, direction)`. Before each gate, the emitter relabels the mover from its current label to `F` unless it is already there. It then emits `mover += q·partner` or `partner += q·mover` (`emit`).
* Step 3 of #484's emission (compensation segment): mover = target `t`, partner = gauge helper `j`, `F = E_j`.
* The kernel updates (Lemma K): mover = donor, partner = pivot, `F` = class entrance.
* Step 6 (centre phase): mover = private copy `C_k`, partner = served target `t`, `F = L_t`.

**Theorem 3 (schedule)** [`emit_spec`, `emit_wellLabelled`, `comp_segment`, `comp_segment_frames`, `centre_forward`, `centre_backward`, `moveLab_top`, `moveLab_mem`].
1. *Exactness part.* Assume no partner is ever a mover, and each partner sits at its gate's frame. Then the emitted segment is well labelled. No order condition is needed.
2. *Compensation segment.* Assume also:
   * every target starts at `0`, or more generally below each of its frames;
   * the gates are emitted in order of non-decreasing rank;
   * **(b)** the frames of each target form a chain.

   Then every relabel is a strict nested ascent `A < B`. Target `t` ends at `L_t = max ℰ_t`: above every frame of its gates, and equal to one of them. Registers that are not targets keep their labels.
3. *Centre phase, forward orientation.* Copy `C_k ← r` at `c_k`, gates in order of non-increasing rank, clear. Assume:
   * the centre register `r` is at `c_k`;
   * `C_k` is not a served target;
   * each served target is at `L_t`;
   * **(c)** the levels form a chain inside `c_k`.

   Then the phase is well labelled and every centre step is a strict nested descent.
4. *Centre phase, backward orientation.* Clear at the bottom, gather in order of non-decreasing rank, and end with the gate `r += −C_k` at `c_k`. The phase is well labelled and every step is a strict nested ascent.

*Proof.* Induct over the gates (`emit_spec`, which is parametrised by a relation `R`) with three invariants:
* the partners are still at their frames, since they never move;
* each mover is `R`-below every frame still ahead of it;
* the mover sits at the gate's frame when the gate is emitted.

At a gate:
* both operands are at `F`, so the gate is admissible;
* the emitted relabel starts at the current label, so it is admissible;
* the relabel is a proper `R`-step: it is emitted only when the current label differs from `F`.

Taking `R` = "always true" gives part 1. For parts 2–4, Lemma 3.0 turns "chain + sorted by rank" into "sorted by `≤`" (or by `≥`), and the invariant follows from that. The end label is the last frame (`moveLab_mem`). By transitivity it lies above all the others (`moveLab_top`). ∎

**Theorem 4 (accounting)** [`paid_telescopes`]. Let `es` be well labelled. Suppose every relabel of register `m` is rank-ascending, and nothing copies into or clears `m`. Then the paid rank of `m`, `Σ |rk B − rk A|` over its relabels, equals `rk λ¹_m − rk λ⁰_m`. The descending case is the same with the order reversed. ∎

**Frame of the other events** [`Stream.labRun_untouched`, `Stream.wellLabelled_append`, `Stream.labRun_append`].
* A sub-stream that never relabels register `i` leaves `λ_i` unchanged.
* Well-labelledness of a concatenation splits at the junction.

**Bit side** [`Dbit_one_mul`, `Dbit_conj`]. For `D_P = [[1−P, P], [P, 1−P]]` over any commutative ring:
* `D_1 D_P = D_{1−P}`;
* `diag(g,g)ᵀ D_P diag(g,g) = D_{gᵀPg}` whenever `gᵀg = 1`.

These are the two identities of the bit-side entrance transfer (`D_I D_E = D_{E⊥}`, a pure conjugation of the coordinate frame), proved for every `P`. The complex word does not use them.

## 4. Lemma G for the word

**Extended labels.** A label is a pair (tag, frame `F`).
* Tag `T` is the word's family: `T_(T,F) = canonical_frame(F)`.
* The other tags are register-specific:
  * `(pre, i)`: source `i` before its entry adapter;
  * `(prew, j)`: entering helper `j` before `R_E⁻¹`;
  * `(post, t)`: target `t` after its exit adapter;
  * `(done, j)`: entering helper `j` after `L_E⁻¹`.
* Their operators are defined so that each conversion event executes `T_B T_A⁻¹`:
  * `T_(pre,i),p = M_i⁻¹ T_p`;
  * `T_(prew,j),E = R_E T_E`;
  * `T_(post,t),F = N_t⁻¹ T_F`;
  * `T_(done,j),FULL = L_E⁻¹ T_FULL`.

  Here `M_i` and `N_t` are the serialized source and target endpoint monomials; the target's is applied inverted. The identity adapters, on all other registers, keep tag `T`.
* Under this reading, every climb, centre step, data adapter and wrapper is a `relabel`. Theorem 1 then applies to the **complete** emitted stream, both orientations, with no event left outside.

**Instance hypotheses (checked; the checks read the emitted artefacts of each variant).**

| | hypothesis | where it is checked | result (headline word, both orientations) |
| --- | --- | --- | --- |
| H1 | well labelled in the extended labels | frames: #484 `lg_lib.check_labels` (G0 at every add and copy, G2 climb source, G3 centre-step source and copy label); tags: `code/check_extended_labels.py` | 0 violations on all four words; 3 adapter mutants rejected on every word, plus 2 wrapper mutants on the three wrapper words |
| H2 | exact recipes | climbs and centre steps: #484 `lg_instances` I-tr, every used transition on all 512 basis columns (not run on the anchor); a recipe is a circuit of linear primitives, so it is `C`-linear and 512 columns determine it on every vector. Adapters and wrappers: exact by the definition of the extended family, given the bridge that `code/check_extended_labels.py` enforces, as `lg_phys.run` executes it: each source has exactly one entry adapter, `(pre,i) → T`, executing `M_i`; each target has exactly one exit adapter, `T → (post,t)`, executing `N_t⁻¹`; every other adapter has no serialized operator, i.e. is the identity, at frame 0 (entry) or FULL (exit); each entering helper has exactly one pre and one post wrapper, keyed by its start frame (#484 G1 also checks this) | 2945 transitions, 0 failures |
| H3 | `S` = `(x,s,y) ↦ (x,s,y+x)` forward, `(x−y,s,y)` backward | #484 `lg_lib.scalar_replay`, exact rational replay, all 800 columns; private copies cleared | exact |
| H4 | endpoint labels | #484 G4: sources at their port lines, targets at 0, helpers at 0 or `E_j`; final labels as in W | 0 violations |
| H5 | accounting | #484 G2 (ascending nested climbs), G3 (strict nested centre steps), ACC (per-register telescoping, centre mass `dim c_k`, paid profile = `local_profile`) | 0 violations |
| H6 | #433's data-adapter identities: `T_{p_i}⁻¹ M_i = C_{q_i}⁻¹`, `T_FULL T_{p_i}⁻¹ M_i = F C_{q_i}⁻¹`, `N_t⁻¹ T_{final_t} = F C_{q_i}⁻¹` | `code/check_adapters.py`, every port, all 512 basis columns, exact | 0 failures on all four words |

**Lemma G.** Assume H1–H4 hold for the emitted word V of a variant. Then for **every** input with empty private registers, each orientation of V computes `D(λ¹) S D(λ⁰)⁻¹` (Theorem 1). By Corollary 2 and H3:
* *Sources and targets.* Each row is `e_r` or `e_r ± e_{pair(r)}`, and the labels at both ends are W's (H4, with the same adapters). The data block is therefore **W's data block**. With H6 it is the intended #433 transform: source `i ↦ F x_i` and target `v+i ↦ F C_{q_i}⁻¹(h_{v+i} + x_i)` forward, with `x_i = C_{q_i}⁻¹ h_i`, and the backward rows likewise.
* *Cross blocks.* No helper column enters a data row, and no data column enters a helper row. So the cross blocks are 0.
* *Helpers.* The block of entering helper `j` is

  `T_(done,j) T_(prew,j)⁻¹ = L_E⁻¹ · T_FULL T_E⁻¹ · R_E⁻¹ = L_E⁻¹ Φ_E R_E⁻¹`,

  which is the virtual entrance of #471/#458 with its wrappers. Lemma A (#484 I-helper) evaluates it to `C_[w] ⊗ I`.

Hence, given H1–H6 and Lemma A, the complete emitted program equals #484's end-to-end formula on every input with empty private registers. #484's `lg_e2e.py` sampled 814 columns of that identity.

Assume H5 as well. By Theorem 4, each non-private register pays `rk λ¹ − rk λ⁰`, and each centre copy pays `dim c_k`. The only start labels that differ from W are `λ⁰_j = E_j`, and the final labels agree. So the local mass is `mass(W) − Σ_j dim E_j`.

**A priori route to H1 and H5 (Theorem 3).** The direct checks above suffice. Theorem 3 also *derives* the frame part of H1, and H5, from the selection hypotheses of #484 §2.4, independently of the checker:
* *Exactness.* Theorem 3.1 needs only that helpers are not targets and that each partner sits at its frame:
  * entering helpers at `E_j`: the virtual entrance; the preconditioner does not touch them;
  * targets at `L_t` when the centre phase starts: A does not relabel targets (`labRun_untouched`);
  * the centre register at `c_k` at the cut.
* *Accounting.*
  * **(a)** `E_j ⊆ F_1(j)` makes helper `j`'s first climb nested.
  * **(b)** and the rank order make the compensation climbs strict nested ascents (Theorem 3.2).
  * **(c)** makes the centre steps strict nested descents (Theorem 3.3/3.4). With `0 ∈ Λ_k`, their ranks sum to `dim c_k`.
  * **(d)** `L_t ⊆ B_1(t)` makes the junction climb nested. Theorem 4 then gives the target the same paid rank as in W.

## 5. Changes relative to #484 PROOF.md §2

1. **Relabel source.** Lemma C's hypothesis named only G0 for adds and copies. The proof also needs every climb or centre step `A → B` to find its register at `A`. This is now part of admissibility. #484's checker already enforced it (G2, G3).
2. **Adapters and wrappers: an implicit commutation step.** #484 §2.1 left adapters and wrappers outside Lemma C as endpoint operators. Register-wise this is right. In every word and orientation, each non-identity adapter and each wrapper is the first or last event on its register. The adapters that sit mid-stream (headline forward: 550 entry, 672 exit) are all identities. But Lemma C as stated covers a stream without adapter events. Using it needs the unwritten step "an operator that is first (last) on its register commutes past every event on other registers", which #484 checked only indirectly (phase order, G0, G4). The clean proof reads adapters and wrappers as relabel events of an extended label set, so Theorem 1 covers the whole stream. The condition this needs is checked directly by the new `code/check_extended_labels.py`, including the bridge in the H2 row. All four words pass. Three mutants are rejected on every word: a dropped source entry adapter, a duplicated source entry adapter, and a target exit adapter moved before the target's last add. Two more are rejected on the three wrapper words: a dropped `R_E⁻¹`, and an `L_E⁻¹` moved before the helper's last add.
3. **From the rational replay to the action on `H`.** "S, the rational matrix of the scalar events" is now a proved step: `scalRun_eq_sum` and `S_rowform`. That step also explains why the replay's empty private copies are harmless.
4. **Minimal label condition.** Exactness needs `λ_t = λ_s` at an add, `λ_r = F` at a copy, and nothing at a scale. The checker's G0 (operands at the annotated frame, scale at its operand's label) is stronger.
5. **(a)–(d) are not needed for exactness at all** (Theorem 3.1). #484 says (b), (c) and nestedness are accounting conditions. The clean proof also places (a) and (d) there, and confirms that the emitter's well-labelledness uses only "partners do not move, partners at their frames". This matches the mutant classification of #484 §2.6 (M3, M3b, M7, M8: physics PASS).
6. **Implicit side conditions made explicit:**
   * gauge helpers are not targets;
   * the private copy is not a served target;
   * Claim 2's "dim E ≤ dim E′ ⇒ E ⊆ E′ in a chain" needs a strictly monotone rank (Lemma 3.0).
7. **The kernel updates** are an instance of the same emitter, with the donor as mover. Their exactness therefore needs only the class entrance condition of Lemma K.
8. **The "every input" claim names its inherited facts.** It rests on #433's data-adapter identities, now checked exhaustively (H6, `code/check_adapters.py`), and on Lemma A (#484 I-helper, exhaustive). It holds for inputs with empty private registers.
