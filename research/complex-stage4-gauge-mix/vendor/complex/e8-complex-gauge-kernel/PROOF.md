# Entrance gauges and shared-donor kernel on the E8 complex word: what is claimed, what is new

Everything here is conditional on the interfaces inherited by #442 (all-size compiler, correlated dirty banks, compressed windows,
restored work, tape/common grid, precision, analytic transfer) and, in addition, on **Lemma A** (paid residual wrappers with explicit
spectators) and **Lemma G** (nonzero-frame compensation and the centre scatter), which are the review points. No Lean proof and no
unconditional theorem is claimed. Hosting is #442's whole-residual hosting (no cross-family split) under the additional rule of #458, extended
here to banks: an entering helper is the only owner of its physical family (data or bank) in every invocation.

## 0. Setting
Complex supplier of #433 (R = 560, h = 9, m = 73, nine stages, eight replicas) with #442's idle-axis hosting. Frames are subspaces of
F2^9; T_F = canonical_frame(9, F) (`clifford_exact.py`); a climb A → B applies T_B T_A^-1. A helper normally has start frame {0}, ends at FULL
and its residual has width 9. The frame-zero compensation `target += c·helper` (the response of the arbitrary helper dirt) is what normally
pins every helper to start frame {0}. A helper with start frame E of dimension e has residual width w = 9 − e. The construction of the paid
wrappers and the one-helper rule follow #458 (chafreaky), which did this for the kernel on an eleven-stage complex word; this package
applies them on the nine-stage word and adds entrance gauges.

## 1. Lemma K (shared-donor kernel; port of #417/#435/#434/#439/#440, as frozen in #449 and used by #458)
Let col(x) ∈ Q^120 be the response of the target rows to the dirt of helper x. A class (E, D, P) has donors D with independent columns and
pivots P with col(p) = Σ_d q_{pd} col(d) exactly, E ⊆ the first frame of every member. Each pivot starts at E; before the main word every
donor receives `d += −q_{pd} p` at frame E (inverse after the full-frame cleanup, the inverse of the whole non-target subword). The donor
updates move the pivot's dirt into the donors, so the composite response of the pivot's dirt is col(p) − Σ_d q_{pd} col(d) = 0 and its
frame-zero compensation column vanishes. Exactness is the arbitrary-dirt replay of the explicit program (precondition + compensation + main +
cleanup) on every column, forward and inverse-transpose (`audit_gk.py`); frames are checked by the chain assertion; all coefficients have
power-of-two denominators (asserted by `emit_gk.py`).

## 2. Lemma G (entrance gauge: nonzero-frame compensation and the centre scatter)
Scope: the entrance-gauge part of this package (nonzero-frame compensation and the centre scatter at the target levels), on the headline word gauge80 + kernel42, on the per-tool
words gauge80 and kernel79, with #433's word (the anchor) as the control. Lemma A (wrappers, spectators, one-owner rule, banks; §3) and Lemma K (§1) are not re-proved here; where
Lemma G uses them the interface is stated (2.2, item N). **Lemma G is not an assumption on top of #425 and #471: it reduces to #425's conjugation lemma and to #471/#458's virtual
entrance, plus a schedule lemma (2.4) whose clauses are checked exhaustively by code that imports no package script (2.5, `verify.py` stage).** The inputs are the emitted artefacts of
each variant (`CANONICAL-WORD`, `LOCAL-PROGRAMS`, `CLIFFORD-RECIPES`, `RESIDUAL-ADAPTERS`, and the 72 calls of the hosted template, which reference the program digests of 40 forward and 32 backward calls);
their sha256 values and the program digests are recorded by the check stage (`LEMMA-G-CHECK.json`, `EXPECTED.json`). The local word does not depend on the hosting or on the banks.


### 2.1 Setting

* H = C^(2^9). Every operator below acts on the 2^9 local coordinates; on exterior slices it acts as the identity, which is omitted.
* A **frame** F is a subspace of F2^9, given by a row of the word's frame table. Each frame has a fixed invertible operator T_F on H. In the package, T_F = `canonical_frame(9, F)` (exact Gaussian-dyadic Clifford), T_0 = I and T_FULL = the Fourier gate on all nine axes. **Only the invertibility of T_F is used below.**
* A register is a pair (h, F): physical content h ∈ H and current label F. Its **logical value** is ℓ = T_F^-1 h.
* The events of an emitted local program are listed below. The physical effect is what the hardware does; the label effect is the bookkeeping.

| event | physical effect | label |
| --- | --- | --- |
| `climb r A→B` | h_r ← T_B T_A^-1 h_r (the serialized child recipe) | A → B |
| `center k A→B` | the same on the private copy C_k | A → B |
| `add t ← s, q` at F | h_t ← h_t + q h_s | none |
| `scale t, q` | h_t ← q h_t | none |
| `copy C ← r` at F | h_C ← h_r | C := F |
| `clear C` at F | h_C ← 0 | C := F |
| adapters, wrappers | fixed endpoint operators (outside Lemma G) | none |

---

### 2.2 What is inherited (admitted by #425, #433, #458, #471)

**C. Common-frame conjugation lemma (#425, "Why the scalar argument lifts to exact complex labels").**
*Hypothesis:* in a stream of the events above, every `add` and `copy` has both operands at one current label, which equals the annotated frame (clause G0).
*Conclusion:* let λ⁰ and λ¹ be the initial and final labels, and let S be the rational matrix of the scalar events with the frames stripped. Then for **every** physical input,

  h_r(final) = Σ_s S_rs · T_{λ¹_r} · T_{λ⁰_s}^-1 · h_s.

*Proof (four lines, included so that this file is self-contained).* The invariant is that h_r = T_{λ_r} ℓ_r at all times, where ℓ evolves under the scalar events alone. Start with ℓ_s := T_{λ⁰_s}^-1 h_s.
* A climb A → B: T_B T_A^-1 (T_A ℓ) = T_B ℓ, with the new label B.
* An add at a common F: T_F ℓ_t + q T_F ℓ_s = T_F(ℓ_t + q ℓ_s).
* A scale commutes with T_F. A copy at F gives T_F ℓ_r. A clear gives 0 = T_F·0.

Only linearity and invertibility are used. ∎

**C′. #425's scalar interface.**
* Block form z′ = Uz, y′ = Vy + Jx + Ks. No target feeds a source or helper. Targets may be read, as in the 56 target butterflies at frame 0.
* The frame-zero preconditioner runs on label-0 registers. The cleanup U^-1 runs at the common FULL label.
* The second orientation is the inverse transpose: the dual of every scalar, in the same event order and with the **same frame chronology**.
* Private centre copies are taken, moved between nested frames by explicit paid children, scattered, and erased. #433 adds split centres: c_k has rank 8 or 1, and the copy goes c_k → 0.

**N. Virtual entrance and full-invocation normalisation (#471 §1, #458 §1).**
* A helper may start at label E. Its logical input is T_E^-1 h, and no physical T_E is executed.
* Nonzero-frame helper←helper additions at the head of the word are admitted: the kernel donor updates at E, inverted at FULL in the cleanup.
* With the scalar identity, the cross blocks vanish, so the data endpoint is unaffected and the helper block is Φ_E = T_FULL T_E^-1. #471 states this as a property of the **complete invocation**, not of any one addition.
* Paid wrappers R_E^-1 (before) and L_E^-1 (after) turn Φ_E = L_E (C_[w] ⊗ I) R_E into C_[w] ⊗ I. Spectators are borrowed in the same owner array. That is Lemma A, which is not part of Lemma G.

**Neither #458 nor #471 uses the gauge.** #458's README says "No … entrance-gauge construction from PR449 is used". #471's PR text says "Its separate gauge-80 change is not used". The steps below are therefore new.

### 2.3 What is new relative to #458 and #471

* **N1. Labelled targets before the centre phase.** A target climbs 0 → E_(1) ⊊ … ⊊ L_t during a compensation segment and is read and written there. It sits at L_t through the centre phase and climbs from L_t into part B. In #425, #433, #458 and #471, targets are at label 0 until the scatter.
* **N2. Target-side nonzero-frame compensation.** The dirt column of an entering helper j is cancelled by gates `y_t += c_tj · x_j` at its entrance label E_j, instead of in the frame-zero preconditioner. In #471 the nonzero-frame adds are helper←helper, and a pivot's column vanishes by linear dependence.
* **N3. Centre scatter along a chain.** The copy descends c_k → λ_1 → … → λ_m = 0, scattering at every level. The backward orientation gathers while ascending. In #425 and #433 the copy makes one step, c_k → 0.

All three are made of the event types already admitted in C, C′ and N. **No new operator-level fact is needed.** What is new is a *schedule lemma*: the emitted stream satisfies G0 and the accounting clauses. That lemma is proved below and checked exhaustively in 2.5.

### 2.4 Lemma G: statement and proof

Notation:
* W is #433's word. G is the set of gauge helpers, with entrances E_j; the kernel helpers (Lemma K) are disjoint from G.
* supp(j) is the set of targets in the support of j's dirt-response column.
* F_1(j) is the frame of the first gate on j in W. B_1(t) is the frame of the first gate on target t in part B of W.

**Hypotheses on the selection:**
* **(a)** E_j ⊆ F_1(j). Since W's frames along a register are nested, E_j then lies inside every later frame of j.
* **(b)** For each target t, ℰ_t = {E_j : j ∈ G, t ∈ supp(j)} is a chain under inclusion. Write L_t := max ℰ_t, or 0 if ℰ_t is empty.
* **(c)** For each centre k, Λ_k = {L_t : t served by k} is a chain, max Λ_k ⊆ c_k, and 0 ∈ Λ_k.
* **(d)** L_t ⊆ B_1(t). The package's nested-climb assertions (`emit_gk`, `gk_word.profile`) enforce it, and it holds for all 50 levelled targets of the headline word.

**Facts about W (checked):**
* **(W)** In part A of W no gate touches a target. With the gauge, the compensation gates are the only part-A gates on targets: 420 gates, 0 others.
* No entering helper is touched by the frame-zero preconditioner. In the headline word the preconditioner touches 112 targets and 438 helpers, none of them entering.
* At the cut, every centre register is at its centre label c_k, and no centre register is an entering helper.

**Emission order:**
1. preconditioner
2. entry adapters and R^-1 wrappers
3. compensation segment: the gauge gates sorted by (dim E_j, j), each preceded by the climbs that bring its target to E_j
4. kernel updates
5. A
6. centre phase: copy at c_k; descend through Λ_k by decreasing dimension; scatter at each level; clear
7. B
8. final climbs
9. exit adapters
10. full-frame cleanup
11. L^-1 wrappers

**Conclusions:**
* **(G-i) Schedule.** In both orientations the emitted stream satisfies:
  * G0: common labels at every add and copy.
  * G1: virtual entrances, with the wrappers outermost on each entering helper.
  * G4: start labels as in W, except λ⁰_j = E_j; final labels as in W.
  * ACC (accounting):
    * every transition of a non-private register is an ascending nested climb charged |B| − |A|;
    * every centre step is a strict nested descent (an ascent in the backward orientation) inside c_k;
    * the centre steps sum to dim c_k;
    * no child runs while a copy is live;
    * the local rank mass per call equals mass(W) − Σ_j dim E_j.
* **(G-ii)** By C, h_r(final) = Σ_s S_rs T_{λ¹_r} T_{λ⁰_s}^-1 h_s for all inputs.
* **(G-iii)** The exact replay gives the scalar identity S: (x,s,y) ↦ (x,s,y+x) forward and (x−y,s,y) backward, all 800 columns, copies cleared. Therefore:
  * the data block is **W's** data block (the source and target labels are unchanged at both ends);
  * the cross blocks are 0;
  * the block of entering helper j is Φ_{E_j} = T_FULL T_{E_j}^-1, which is exactly the input of #471's normalisation and Lemma A.

**Proof of (G-i).**

*Claim 1 (entering helpers).*
* j starts at E_j, and by (W) the preconditioner does not touch it.
* In the compensation segment, a gauge helper j occurs only as the source of its own gates, which are emitted at E_j, its label. A kernel pivot occurs only in donor updates at its class entrance, which is its start label (inherited, Lemma K / #471).
* The next event on j is the climb E_j → F_1(j), which is nested by (a) (by Lemma K's class condition for kernel helpers). The remaining climbs are W's, so they are nested and end at FULL.
* A nested chain telescopes, so j's climb mass is 9 − dim E_j.

*Claim 2 (targets in the compensation segment).*
* Let j_1, …, j_p be t's gauge gates in emission order, so dim E_{j_1} ≤ … ≤ dim E_{j_p}.
* In a chain, dim E ≤ dim E′ implies E ⊆ E′, and equal dimension implies equality. By (b), therefore, 0 ⊆ E_{j_1} ⊆ … ⊆ E_{j_p} = L_t.
* The emitter climbs t only when the next gate's frame differs. So t's climbs are 0 → E_(1) ⊊ … ⊊ L_t, all ascending and nested.
* At each gate, t's label is E_j, which is j's label by Claim 1. So G0 holds at all 420 compensation gates.

*Claim 3.* By (W) no other gate in the compensation segment, the kernel updates or A touches a target. So every target is at L_t when the centre phase starts.

*Claim 4 (centre phase).*
* Forward:
  * The copy is taken at c_k, the centre register's label, so the copy satisfies G0.
  * Order Λ_k as λ_1 ⊋ … ⊋ λ_m. The order is strict because the λ_i are distinct elements of a chain, and λ_1 ⊆ c_k by (c).
  * The steps c_k → λ_1 (omitted when they are equal) → … → λ_m are strict nested descents.
  * At level λ_i the copy has label λ_i and scatters only into targets with L_t = λ_i, whose label is L_t by Claim 3. So G0 holds.
  * By (c), λ_m = 0, so the step ranks telescope to dim c_k: the same mass as W's single c_k → 0 child.
  * No climb is emitted inside the centre phase, so the lifetime clause holds.
* Backward:
  * The copy is cleared at λ_m and gathers at λ_m.
  * It then ascends λ_m → … → λ_1 → c_k, gathering at each level.
  * Finally r += −C at c_k, followed by a clear. The label equalities are the same as in the forward orientation.

*Claim 5 (targets in B).* t's first climb in B is L_t → B_1(t), nested by (d). The remaining climbs are W's and end at perp(P_t). The mass telescopes to 8, the same as in W.

*Claim 6 (remaining events).*
* The preconditioner is at 0 on label-0 registers.
* The cleanup is the inverse of the non-target gates of the segment, the kernel updates, A and B. This includes the kernel updates, inverted at FULL, and excludes the gauge gates, whose destination is a target. Every source and helper is at FULL there.
* The backward orientation dualises each scalar but keeps its operand pair, so every label equality carries over.

*Mass.* Sources contribute 8·120, targets 8·120, helpers Σ_j (9 − e_j) and centres Σ_k dim c_k. So mass = mass(W) − Σ_j e_j. ∎

**Which clauses are needed for what.** The necessity controls in 2.6 confirm this split.
* **Exactness (semantic):**
  * G0 at the compensation gates (Claims 1 and 2), at the kernel updates (inherited) and at every scatter (Claims 3 and 4);
  * G1, the virtual entrance with the wrappers outermost;
  * the exact scalar identity S.
* **Paid profile, mass and lifetimes (accounting):**
  * the nested monotone chains, which follow from (a), (b) and (d);
  * the nested strict centre chain inside c_k with bottom 0, which follows from (c);
  * the copy lifetimes.

  The operator identity survives a violation of any of these, but the charged children, the mass identity and therefore the moment (b) would be wrong.

### 2.5 Independent exhaustive checks (`code/lemmaG/`, run by `verify.py`; no package script imported)

Code in `code/lemmaG/` (driver `check.py`, one run per variant, stage of `verify.py`):
* `gd.py`: an exact Gaussian-dyadic applier for the Clifford primitives. It uses int64 with a 2^60 guard on every primitive; no run tripped it, so every equality is exact over Z[i][1/2]. It is cross-checked against the vendored state-vector routine on 19 operators.
* `lg_lib.py`: the label checker and exact rational scalar replay.
* `lg_phys.py`: the physical simulator.
* `lg_instances.py`, `lg_e2e.py`, `lg_mutants.py`: the drivers.

The vendored `canonical_frame` and `cgate` are used only as **definitions** of T_F and C_q. Every executed transition, data adapter and wrapper is decoded from its serialized recipe.

**Label, scalar and accounting checker** (`run_labels.py`). Both orientations, every event.

| variant | label violations | scalar replay (800 columns) | compensation gates | kernel updates | entering helpers / entrance rank | local mass | calls → verified program |
| --- | --- | --- | --- | --- | --- | --- | --- |
| anchor | 0 | exact | 0 | 0 | 0 / 0 | 7032 | 72/72 |
| kernel79 | 0 | exact | 0 | 229 | 79 / 79 | 6953 = 7032 − 79 | 72/72 |
| gauge80 | 0 | exact | 420 | 0 | 80 / 106 | 6926 = 7032 − 106 | 72/72 |
| gauge80 + kernel42 | 0 | exact | 420 | 111 | 122 / 148 | 6884 = 7032 − 148 | 72/72 |

In every variant the paid profile recount equals the word's `local_profile`, and every centre chain ends at 0 with lowering mass dim c_k (8×8 + 8×1 = 72).

**Per-instance operator identities** (`lg_instances.py`). Each is exact and checked on **all 512 basis columns of every input**.

| identity | headline instances | result |
| --- | --- | --- |
| I-tr: every used transition, recipe = T_b T_a^-1 | 2945 transitions (climbs and centre steps) | 0 failures |
| I-comp: the compensation segment acts as h_t ↦ T_{L_t}(h_t + Σ_j c_tj T_{E_j}^-1 h_j), h_j ↦ h_j | 420 gates; 130 input registers (50 targets, 80 gauge helpers) | 0 failures |
| I-centre: forward h_t += q_t T_{L_t} T_{c_k}^-1 h_r; backward h_r −= Σ q_t T_{c_k} T_{L_t}^-1 h_t | 16 centres × 2 orientations (every served target in the backward orientation) | 0 failures |
| I-helper: L_E^-1 · (recipes along the helper's emitted chain E → … → FULL) · R_E^-1 = C_[w] ⊗ I | 122 helpers (w = 8: 104; 7: 14; 5: 4) | 0 failures |

The headline's centre chains are (dimensions along the path):
* 1→0 eight times;
* 8→0 once;
* 8→1→0 once;
* 8→2→1→0 twice;
* 8→4→2→1→0 four times.

The target levels have dimension 1, 2 and 4. The same identities hold, with 0 failures, on gauge80 (I-tr 2933, I-comp 420 gates and 130 inputs, I-centre, I-helper 80) and on kernel79 (I-tr 2932, I-centre, I-helper 79; it has no compensation segment).

**End-to-end identity of the complete emitted program** (`lg_e2e.py`). Both orientations, all events: preconditioner, data adapters, wrappers, every climb and centre step by its recipe, cleanup. The result is compared with the intended transform computed **from definitions**. Here F is the nine-axis Fourier gate, C_q is the port gate, x_i = C_{q_i}^-1 h_i, and the target paired with source i is v + i.

* **Forward:**
  * source i ↦ F x_i
  * target v + i ↦ F C_{q_i}^-1 (h_{v+i} + x_i)
  * non-entering helper ↦ F h (= C_[9])
  * entering helper ↦ C_[w] ⊗ I · h
* **Backward:**
  * source i ↦ F (x_i − h_{v+i})
  * target ↦ F C_{q_i}^-1 h_{v+i}
  * helpers as in the forward orientation

Columns checked:

| variant | basis columns | dense columns | result |
| --- | --- | --- | --- |
| gauge80 + kernel42 | 806 | 8 | PASS, exact |
| gauge80 | 722 | 8 | PASS, exact |
| kernel79 | 670 | 8 | PASS, exact |
| anchor | 512 | 8 | PASS, exact |

* The headline's 806 basis columns are:
  * 256 random (register, coordinate) columns;
  * 244 columns at the entering helpers, two per helper;
  * 50 columns at the levelled targets;
  * 16 at the centre registers;
  * 240 at the ports.
* In a dense column every one of the 800 registers holds random Gaussian integers at once.
* The anchor passing the same formula shows that the data-adapter interpretation is the admitted #433 one.

The end-to-end result depends neither on the wording of Lemma G nor on Lemma C: it is a direct exact computation of the emitted program.

### 2.6 Necessity controls (`code/lemmaG/lg_mutants.py`)

Each mutant edits the emitted headline stream so that one clause is violated. "Physics" is the exact end-to-end check on targeted and random columns; a transition that has no recipe is executed as T_b T_a^-1.

| mutant | clause violated | checker | physics |
| --- | --- | --- | --- |
| M1 compensation with the target still at label 0 | G0 at a nonzero-frame compensation | G0 | FAIL both |
| M2 physical T_E on the helper (start declared 0) | G1 virtual entrance | G1, ACC | FAIL both |
| M3 target visits its levels out of nesting order (E2 → E1) | G2 (via (b)) | G2, ACC | PASS → accounting |
| M3b helper detours E_j → X ⊉ E_j → F | G2 (via (a)) | G2, ACC | PASS → accounting |
| M4 scatter after the copy descended below the target's level | scatter at the level (G0 in the centre) | G0 | FAIL |
| M5 last centre step skipped | chain reaches every level, bottom 0 | G0, ACC | FAIL |
| M6 copy taken at the wrong label | copy at c_k | G3 | FAIL |
| M7 another child runs while a copy is live | copy lifetime | G3 | PASS → accounting |
| M8 centre chain leaves c_k (c_k → X → L1) | nested chain inside c_k (via (c)) | G3, ACC | PASS → accounting |
| M9 compensation coefficient doubled | scalar identity S | S | FAIL both |
| M10 compensation after the helper's first climb | G0 (the compensation reads the entrance value) | G0 | FAIL both |
| M11 kernel update with the donor at label 0 | G0 at a nonzero-frame kernel update (inherited) | G0, ACC | FAIL both |
| M12 R_E^-1 after the helper's first gate | G1, wrapper outermost | G1 | FAIL both |
| M13 L_E^-1 dropped | G1, wrapper outermost | G1 | FAIL both |

The checker rejects all 14 mutants. The physics column confirms the classification: the semantic clauses are needed for exactness, and the accounting clauses for the charged profile.

### 2.7 What Lemma G rests on
* #425's common-frame conjugation lemma C (proved in 2.2; it holds for any invertible label family), #425's scalar interface, and #471's / #458's virtual entrance and complete-invocation normalisation, with Lemma A (§3) closing the helper block.
* The new content is the schedule lemma (G-i), proved in 2.4 from (a)-(d) and the base-word facts (W). The common-label property is a CHECKED property of the emitted stream, not an assumption: the stage checks every event's labels,
  the exact scalar identity on all 800 columns, the paid profile and mass identity, every transition recipe, the compensation segment, every centre phase and every entering helper's normalised chain on all 512 basis columns of each input, the 72 calls' program digests, and the complete program end to end.
* (b), (c) and nestedness are accounting conditions (charged profile, mass, D), not exactness conditions (2.4, 2.6).
* Lemma C and the virtual-entrance convention remain the admissions of #425 and #471/#458; Lemma G adds none. Lemma A (spectators, the one-owner rule, banks) and the global composition lie outside Lemma G; the check stage reads only the call digests of the hosted template.


## 3. Lemma A (paid residual wrappers with explicit spectators) — review point
Let E ⊆ F2^9, e = dim E, w = 9 − e. A helper that starts at E and ends at FULL has the physical residual S_E = T_FULL T_E^-1 (apply T_E^-1
first). Its initial label is an interpretation of its arbitrary physical input h: the logical scalar value is T_E^-1 h. No T_E entrance transform is
executed, and none is charged as rank zero; the emitter has no entry adapter for entering helpers.
(i) **Exact (checked, `adapters_gk.py`):** S_E = L_E (C_[w] ⊗ I) R_E with R_E applied first, L_E, R_E Gaussian monomials (address permutation,
quadratic phase, translation, scalar power of i), for every entrance frame of the word, global phase included. The serialized monomials are
DECODED with the primitive constructors (not `lower_child`) and L_E^-1 S_E R_E^-1 has exactly the tableau and zero-state vector of C_[w] ⊗ I, i.e.
it is the Fourier factor on w coordinates and the identity on the other e. Wrong phase, translation, quadratic form, swapped sides and wrong width are rejected.
(ii) **Paid wrappers (emitted, replayed):** R_E^-1 is applied before every gate that touches the helper and L_E^-1 after the full-frame cleanup of the
whole local invocation (`residual_adapter` events; `replay_gk` demands exactly one of each per entering helper, with the right frame and phase). They are
charged: 144 elementary factors at each end of every entering helper in every invocation (a monomial on 9 bits has at most 81 + 45 + 9 = 135) in
`integrate_gk.py`. The wrapped residual is C_[w] ⊗ I on the nine local coordinates.
(iii) **Spectators and the one-helper rule (assumed, adopted from #458 §3):** the wrappers mix the w residual axes with e spectator axes of the host family
and surround the whole invocation, so the spectators must not be touched by anything else during the call. Hosting is therefore whole-residual with
at most one helper per physical data family per invocation, and an entering helper is also the only owner of its bank family (below); generated and audited (`onehost_gk.py`, `hosted_gk.py --one-helper-per-family`,
`audit_hosted_gk.py --one-helper-per-family`: all hosted families of a call are pairwise distinct and distinct from the active data families; the children of one
(pair, side) share their families and have pairwise disjoint windows, which is checked). The host chart is explicit and audited: for the host's port q the
parent's idle basis is B_q = U_q ⊕ I; the residual occupies the pending vectors b_off … b_(off+w−1); the spectators are the first e basis indices of B_q not
occupied by it, in increasing order; the route [4, child, offset, w, spectators] records them. The route is a permutation of an orthonormal basis (it is in
O(73,2)); the non-orthogonal address maps occur only inside the paid monomials. Under these conditions the complete effect of a call on the host is
P_g (C over the assigned pending vectors) P_g^-1 with identity on every spectator, and factors of different calls act on disjoint pending coordinates.
**Banked entering residuals (the same rule).** Entering residuals that are not hosted are tiled into banks of their own: bank j of a stage holds the j-th
entering helper of each of the eight replicas, packed from cell 0 (`gk_common.tile`), so a bank family has at most ONE entering owner per invocation (the generators place replicas by construction rather than asserting it; the eight replicas share each bank's spectator cell across invocations, never within one) and no
width-9 residual shares it. The bank chart is the analogue of the host chart: the bank is the standard basis of its 73 cells; the residual occupies cells
off … off+w−1; the e = 9 − w spectators are the first e cells beyond every residual cell of the bank (its pad), in increasing order; route
[2, off, w, spectators]. The pad is paid as before (rank 73 − Σ widths, i.e. 9 for eight width-8 residuals); the spectators are borrowed inside it and not
deducted, so D = 2496 is unchanged. Width-9 residuals keep #433's pure banks, [2, slot] with eight disjoint 9-cell slots, and carry no wrapper. A layout with eight
entering helpers of one invocation per bank family, each in a disjoint 9-cell footprint (eight residual cells and a spectator in the pad), has the same bank count, pad
and b; it is NOT used and the audit rejects it (control below), because the argument adopted here is #458's one-owner rule, not disjoint supports.
**Where the rule is asserted.** On every register class of an invocation, in the generators (`hosted_gk.one_helper_rule`, `integrate_gk.py`) and independently in
`audit_hosted_gk.py` (strict) and `replay_gk.py` (parent template): active data wires and hosted helpers (data families: one owner each, any width); banked helpers
(an entering helper is the sole owner of its bank family, spectators = the bank chart, the 9-cell footprints of a family are disjoint; width-9 helpers share a pure bank);
the private namespace (centres, reserved tableau, coefficient: never an owner; the hosted template's `private_namespace` record is re-based on the hosted stock, the
inherited record pointed beyond it, and is audited); copies (every owner of a replica's invocation lies on that replica's data families or on a bank; the children of
one (pair, side) share their families and have pairwise disjoint windows). Wrappers are emitted and replayed for helper registers only (data, target and centre
registers are rejected), and an entrance (`start_extra`) is accepted for helper registers only.
**What is not met:** the entrance frames consist of even-weight vectors of F2^9 (the dot product is alternating on E; 15 of the 16 frames of the headline
word are totally isotropic). The bit-style criterion of #440 (`validate_isometries`) is therefore **not** satisfied, and cannot be: no orthogonal map of O(9,2)
sends such an E to coordinate axes (restricted to entrances that satisfy it the gain is 0, `provenance/iso1.py`). That is why the wrappers are two-sided
paid monomials and not an orthogonal conjugation.

## 4. Hosting, stock and invoices
Hosting is #442's integer programme with residual widths 9 − dim(E) and distinct stages in the pattern of every copy of an idle child
(`onehost_gk.py`); a hosted residual occupies w pending coordinates of one family; no piece lies on two families (`audit_hosted_gk.py`). Unhosted
residuals are tiled into banks (width-9 residuals by first fit, eight per bank with #433's [2, slot] routes; entering residuals in banks of their own, one per replica
per bank, route [2, offset, width, spectators]) and each bank pays a pad of rank 73 − Σ widths (split into commuting children of rank ≤ 51). The live stock is
64·120 + 9·banks; the finite invoices are #442's with the hosted stock
plus the wrapper factors above (`integrate_gk.py`, `assemble_gk.py`).

## 5. Regression anchor and controls
With the empty selection the generalised scripts reproduce #433's CANONICAL-WORD, LOCAL-PROGRAMS, LOCAL-CHECKS, parent GLOBAL-TEMPLATE and
INDEPENDENT-REPLAY and #442's hosted template and HOSTED.json byte for byte (`verify.py` asserts it); the anchor keeps #442's hosting rule.
Mutation controls, all rejected: (a) through the certifying scripts (`controls_pipeline.py`, each runs `audit_gk` then `emit_gk` on a mutated word):
kernel donor update omitted / sign flipped; gauge gate omitted / coefficient doubled; entrance outside the frame of its gates; an entrance given to a helper
that keeps a frame-zero compensation; target level forgotten; centre levels not a chain (word built without the builder's checks); (b) in `replay_gk`:
the four local and three global controls of #433, missing / misplaced / wrong-frame wrappers, a centre step that is not nested, a skipped centre
descent step; (c) in `adapters_gk`: wrong phase, translation, quadratic form, swapped sides, wrong width; (d) in `audit_hosted_gk`: the eight controls of #442's
audit with a wrong-width control, two helpers on one physical family (accepted by #442's rule, rejected here), a spectator that is a residual coordinate,
shifted / dropped spectators, a missing spectator record, the rule flag removed, and, for the other register classes, two entering helpers on one bank family (the
nine-cell-footprint layout above: accepted by the #442 rule, rejected here), a bank spectator that is a residual cell / shifted / miscounted / dropped, a banked
entering helper or a second owner on an active data family, a bank owner in the centres or the reserved tableau of the private namespace, a private-namespace record left at the
parent's ranges or overlapping the live stock, a hosted or active owner on another replica's family, overlapping windows in one family group;
(d') in `controls_hosting.py`, through the generators (`hosted_gk.one_helper_rule`, `hosted_gk.py`, `integrate_gk.py`): one mutated owner array per register class (two entering
helpers on one bank family, a spectator inside the residual, an active wire on a bank, two hosted helpers on one data family, a helper on an active data family, an owner in the centres,
the reserved tableau or the coefficient registers), and the whole hosting and parent-template generators run with the eight-entering-helpers-per-bank tiling, which they must refuse;
in `replay_gk.py` the same rule is tested on mutated owner arrays of the parent template, plus wrappers naming a data, target or centre register; (d'') the independent Lemma G stage of `verify.py` (`code/lemmaG/`): the label / scalar / accounting checker, the exhaustive instance identities, the end-to-end identity and the 14 necessity mutants of 2.6 (all rejected);
(e) on the selection (`gk_word.build`): entrance outside a first frame,
non-nested entrances, pivot outside the donor span, entrance outside a donor's first frame. The strict outer assembly rejects the next grid point and zero/unit η, β.
