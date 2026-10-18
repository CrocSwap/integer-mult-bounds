# Format limits (no κ claim): a certified ceiling, a spec census, structural lemmas and helper bounds

This package states results about the limits of the current construction format (B_K compressed windows, star
copies, whole-residual hosting) and checks the ones that can be checked. **It makes no κ claim and ships no word.**
Each result comes with its scope and assumptions. Each is marked:

- **checked**: `verify.sh` recomputes it from the files listed below (exact or certified arithmetic unless stated);
- **argued**: a proof or proof sketch in this README;
- **recorded**: an input taken from a run or a PR that `verify.sh` does not repeat (the file and its source are named).

```sh
python3 -m pip install -r research/format-limits/requirements.txt
bash research/format-limits/verify.sh /fresh/output/dir     # from a checkout or `git archive` of the whole repository
```

Python ≥ 3.11 with numpy, scipy, sympy, python-sat and ortools (`requirements.txt` pins a tested set). Step 0
checks the package against `MANIFEST.sha256`, the vendored inputs against the git blob ids of their PR commits
(`SOURCES.json`) and the files of main it reads (`DEPENDS.json`). Steps A–E print one `PASS`/`FAIL` line per claim.
About 2 minutes on 12 cores (six checks at a time).

**Tested environments** (fresh `git archive`, every claim PASS):

| Python | numpy | scipy | sympy | python-sat | ortools | how installed |
|---|---|---|---|---|---|---|
| 3.11.17 | 2.4.6 | 1.17.1 | 1.14.0 | 1.9.dev15 | 9.15.6755 | fresh venv from `requirements.txt` |
| 3.14.7 | 2.4.6 | 1.17.1 | 1.14.0 | 1.9.dev15 | 9.15.6755 | fresh venv from `requirements.txt` |
| 3.14.7 | 2.5.4 | 1.18.1 | 1.14.0 | 1.9.dev15 | 9.15.6755 | fresh venv, latest releases |
| 3.14.7 | 2.3.5 | 1.17.0 | 1.14.0 | 1.9.dev15 | 9.15.6755 | development venv |

Values that come from floating-point solvers (the hosting LP, the coupled-cover MILP) are compared with explicit
tolerances; the certified roots are rational intervals.

## Results at a glance

| id | result | status |
|---|---|---|
| A | **Format ceiling, rev. 2.** Under the accounting axioms of §A.1, every supplier in the format has saving a ≤ X(s, h/k, x) (root of the slot-domination bound). On the realised units, X* = 6.0005·10⁻³ (bit, 111 lines, decoder constant 63) and 5.1863·10⁻³ (complex, 112 ports, copy cost 64), both at s = 5, so **κ ≤ 5.1595·10⁻³** (complex binds). | theorem argued; every number checked (`a1`–`a5`) |
| A.4 | The axioms hold on the frontier words #555 (bit) and #568 (complex): published values reproduced from their profiles, deficit identity with equality, B_K idle windows literal, slot domination at nine values of q. | checked (`a3`); (Bat)/(Hst) for #568 argued from its README |
| A.5 | At s = 9 the frontier sits 2.66× (bit) / 2.50× (complex) under the ceiling; 87% / 93% of the log-gap is helper cost, 19% / 25% data-run fragmentation, and hosting recovers 7% / 18%. | checked (`a4`); #568 uses a recorded idle remainder |
| A.6 | The rev. 1 scope x = 3/5 (κ ≤ 4.5151·10⁻³) is superseded: the punctured units have x = 63/111 and 64/112. | checked (`a1`) |
| B | 25 format rules classified as spec / proved / convention, with file:line evidence in the upstream paper and the hub's checkers, and the corrections the census found. | anchors checked (`b`); classification argued |
| C.1 | Frame sandwich: a register's frame lies between the span of what it carries and the orthogonal of what it will serve; the three complex frame walls are its faces; leaving it is exact and costs d(f, g). | argued; toy checked (`c1`) |
| C.2 | Lemma N: the per-target rank-1 port factor is a gauge of the endpoint frames, always paid; any detour off the geodesic interval costs exactly 2. | proof argued; toys checked (`c2`) |
| C.3 | Lemma R: complement sinks w_t^⊥ (w·u = 1) are legal at zero rank and port cost, and forced to w_t = u_t on every target of the four complex words checked (#531; #569 width-7 and four-cold; #571 combined). | checked (`c3_gate0`, `c3_taint`) |
| C.4 | Lemma Q: a degenerate-label unit is dominated by its quotient (copy cost and window), so degenerate spans give no new (w, x) points. | proof argued; toys and families checked (`c4`) |
| C.5 | Lemma λ: a phase-frame butterfly needs λ = ±i (and 2 invertible) in its payload ring; b < c is the price of √−1, and the outer already uses shift twiddles. | argued; instances checked (`c5`), anchors (`b`) |
| C.6 | At the E8 decoder pattern with window ≤ 9 the label pairing B = W·Uᵀ is unique (= B0); every W ≠ U is a gauge. Window 8 is impossible. | checked (`c6`, SAT without proof logs) |
| C.7 | A rank-r descent costs 2r data mass in every call (−5.63% c on #555, −5.65% b on #568 per rank-1 descent); within that price class a schedule with a paid descent is dominated. | toy and prices checked (`c7`); dominance argued |
| C.8 | Splitting one helper residual across two hosting streams meets a trace obstruction under every invertible storage change; uncharged, it is worth at most +0.67% b on the current complex frontier. | argued |
| D | Design-free helper floors in the drop-free monotone-chain model: bit ≥ 212 (sink-only targets) / 138 (strict) vs 439 shipped; complex ≥ 107 / 0 vs 496. Coupling the levels adds 0. The "224 carriers" complex floor is a design choice, and carriers are register-neutral in the calibrated ledger. | checked (`d1`–`d3`), given the argued crossing lemma |
| E | Complex helper price by class and width on #569 (0.039–0.140% b per helper at k = 1; the hosting offset depends on width only), and the moment-cost census by class on #555 and #569. | k = 1 prices, control and census checked (`e1`, `e2`); k > 1 rows recorded |
| F | Cost structure: a change paid in every local word must buy about 2.8% of the supplier value per rank unit; open problems: per-word enablers, a non-star decoder, the schedule/ρ freedom, new skeletons. | conclusion from checked prices |

Earlier statements this package relies on: Theorems A–C of #446 (DreamingOfClouds, open; content-frame invariant,
stage-window additivity, pairing-rank copy floor). They are cited as premises and are not re-proved here. #446 states
Theorem B for rank-1 labels (every number in this package is at k = 1), and its Theorem C value 72 for the bit E8
unit is computed there and not replayed here.

## A. Format ceiling, rev. 2

### A.1 Scope S2 (accounting axioms)

A word is a B_K compressed-window block for one supplier (bit or complex), replicated T times, with s = 2K + 1
stages, v ports of label rank k and stage window h, copy rank cst per stage, and any helper network (any R, widths,
local programs), any banking or hosting rule and any halving depth. Writing z_r for the number of paid children of rank
r and g_q(r) = r((m/r)^q − 1):

- **(P) pressure identity.** The supplier saving a is the root q of Σ_r z_r g_q(r) = D. (The hub pricers add a
  nonnegative fallback term, which only lowers their root.)
- **(Dfc) deficit.** D = T[(s − 1)vk − s·cst], with cst ≥ cst_min(U), the star floor of the unit U (the pairing-rank
  floor of #446 Theorem C holds for any copy tree; the star form β_j ≥ k·w_in is the scope assumption).
- **(Win) window.** Every data register climbs a ≥ h − k per stage and m = k + s·a (#446 Theorem B gives
  m ≥ k + s(h − k); #386's compressed windows attain it). X is non-increasing in a, so a = h − k is the extreme case.
- **(Sch) B_K schedule.** Stage j activates one bank pair (2 data registers per port per replica); pair 0 is active at
  stages 0, 1, 2 and pair p ≥ 1 at 2p + 1, 2p + 2. Idle frame changes per copy (2v copies): pair 0 has [(2K − 2)a];
  pair p ∈ 1..K − 1 has [2pa, a, (2K − 2p − 2)a] (a bridge read splits the pre-stretch).
- **(Bat) batching.** A paid child executes part of one frame change Δ and has rank ≤ rank Δ (Δ is a register's
  frame change, or, as in #448, one idle change across the copies of one idle child). Local children have rank ≤ a
  (data registers) and ≤ h (helpers, copies).
- **(Hst) hosting is accounting.** A hosted helper child is a local child (rank ≤ h) that executes coordinates of an
  idle frame change; the rest of that change is paid in children of rank ≤ its rank; an unhosted helper lives on a bank
  wire.

### A.2 Theorem and proof sketch

Per port (v and T cancel), the **forced slots** are: the active climbs (mass 2sa, cap a), the copy drops (mass s·x,
x = cst/v, cap h) and each idle frame change of rank r of the schedule (mass 2r, cap max(r, h)). Let
F_s(q) = Σ_slots mass · ((m/cap)^q − 1) and D_s = (s − 1)k − s·x.

**Theorem.** For every word in S2 on a unit U, a ≤ X(s, h/k, x_U) := the root q of F_s(q) = D_s, with
x_U = cst_min(U)/v(U). Since e^y − 1 ≥ y, also X ≤ D_s/Cost_s with Cost_s = Σ_slots mass · ln(m/cap).

*Proof sketch.* (1) Monotonicity: each g_q(r) increases in q for r < m, so a(z, D) ≤ a(z', D') whenever f_z ≥ f_z'
pointwise and D ≤ D'. (2) Slot domination: by (P) the paid mass executes every coordinate of every forced slot; by
(Win), (Sch), (Bat) and (Hst) every child touching a slot has rank ≤ its cap; φ_q(r) = (m/r)^q − 1 decreases in r, so
splitting each child's mass over the slots it touches gives f_N(q) ≥ F_s(q; cst_N); children touching no slot
contribute ≥ 0. (3) Helpers never shift D or m (call this Lemma H): Theorem B bounds m with target frames only; a bank wire is restored
scratch, so its saving is ≤ 0; a data register saves ≤ k whoever executes its coordinates; copies cost ≥ cst_min for
any tree. X is non-increasing in a (d/da of each slot term is ≥ 0 by Bernoulli's inequality). The cap max(r, h) on
idle slots absorbs the one place where hosting lowers paid cost (a width-h helper child on a single-stage idle slot);
it costs 1% against the literal R = 0 profile. (4) F_s increases and D_s decreases in cst, so cst_N may be replaced by
cst_min. Apply (1).

**General k (argued; no number here uses it).** Scaling every rank by k (a = k(w − 1), h = kw, m = k(1 + s(w − 1)),
every slot mass and D multiplied by k at fixed x/k) leaves each ratio m/cap unchanged, so X depends only on
(s, w = h/k, x/k). Every number in this package is at k = 1.

**κ.** The outer assembly seeds s0 = min(c, (1 − β)b) − 10⁻²⁴ and bootstraps x ↦ (1 − s0)s0 + s0·x from below; the map
is increasing with fixed point s0, so κ ≤ X/(1 + X) with X = min(X_bit*, X_cx*), each side at its own best s.

### A.3 Numbers (certified; `a1_ceiling_roots.py`, `a2_ceiling_sup.py`)

| unit | x | s = 3 | **s = 5** | s = 7 | s = 9 | s = 11 | s = 13 |
|---|---|---|---|---|---|---|---|
| bit, 111 live lines, decoder constant 63 (#545, #555), h = 8 | 0.5676 | 5.9474e-3 | **6.0005e-3** | 5.2095e-3 | 4.6072e-3 | 4.1490e-3 | 3.7879e-3 |
| complex, 112 ports, copy cost 64 (#523 → #569), h = 9 | 0.5714 | 5.0474e-3 | **5.1863e-3** | 4.5130e-3 | 3.9946e-3 | 3.5989e-3 | 3.2865e-3 |

Roots are rational-interval brackets of width < 10⁻¹⁵; the upper end is the certified value.

- **κ ≤ 5.1594938·10⁻³ < 5.1595·10⁻³**; the complex side binds. The bit-only corollary is c/(1 + c) ≤ 5.9647·10⁻³.
- **The supremum over s is at s = 5** on both units. For odd s = 7..401, the certified D_s/Cost_s stays below X(5);
  the largest values are 5.2311·10⁻³ (bit) and 4.5292·10⁻³ (complex), both at s = 7. For s ≥ 403 a tail bound applies:
  Cost_s/v ≥ 2Σ_{p<K} 2pa·ln(m/(2pa)) ≥ 4a·Σ_{p<K} p ln(K/p) (using m > 2Ka), and
  Σ_{p=1}^{K−1} p ln(K/p) ≥ K²/4 − K/e − K/2. Then X ≤ D_s/Cost_s < (1 − x)s/(4a(K²/4 − K/e − K/2)), which is
  decreasing in K and equals 6.27·10⁻⁴ (bit) / 5.44·10⁻⁴ (complex) at s = 403.
  - *Proof of the inequality (erratum to rev. 1, which invoked "trapezoid error for a concave function", the wrong
    direction).* f(p) = p ln(K/p) is concave, so by Hermite–Hadamard f(p) ≥ ∫_{p−1/2}^{p+1/2} f. Summing gives
    Σ_{p=1}^{K−1} f(p) ≥ ∫_{1/2}^{K−1/2} f = K²/4 − ∫_0^{1/2} f − ∫_{K−1/2}^K f. Both removed pieces are small:
    the first is (1/8)(ln K + ln 2 + 1/2), and the second is ≤ (K/2)·ln(K/(K − 1/2)) ≤ K/(4K − 2) ≤ 1/3. Their sum is
    ≤ K/e + K/2 for every K ≥ 2. The script also checks the inequality numerically for K = 2..5000.
- **Frontier against the ceiling at s = 9.** X(9)/c = 2.658 for #555 (c = 1.733053·10⁻³), and X(9)/b = 2.499 for
  #568 (b = 1.598685·10⁻³).
- **Copy charge.** One copy-rank unit per stage (bit cst 63 → 62) raises X by +3.90% (s = 5), +2.82% (s = 9) and
  +2.65% (s = 11).

### A.4 The axioms on the frontier words (`a3_axioms.py`, checked)

| check | words | result |
|---|---|---|
| (P): certified root of the published global profile at the word's (m, D) vs its published value | #510 R480 s9, #543 R420 s9/s11, #545 p111 s11, #555 p111 s9/s11, #568 | root ≥ published; relative difference 1.2–1.7·10⁻⁹ on the bit pipelines (consistent with their nonnegative 10⁻¹⁶ fallback term), 5·10⁻¹⁸ on #568 |
| (Dfc): m·W − rank mass = T[(s − 1)v − s·cst] with integral W | same seven profiles | equality (e.g. #555: 64·28416 − 1,808,352 = 10,272; #568: 73·7168 − 520,704 = 2,560) |
| (Win): m = k + s(h − k); largest child = literal idle remainder (2K − 2)a | same | m = 64/78/73; largest child 42/56/48 on #543, #545, #555, #568 (#510's largest child is 8) |
| (Sch): active + copies + idle slot mass = rank mass | #555, #568 | 447,552 + 18,144 + 1,342,656 = 1,808,352; 129,024 + 4,608 + 387,072 = 520,704 |
| (Sch): idle windows per replica = idle_slots(K = 4, a = 8) on both banks | #568 PLAN, 8 replicas | {8: 6, 16: 4, 32: 4, 48: 4} on every replica |
| (Hst): helpers hosted whole, no banks | #555 | bank assignments 0; hosted residuals 126,432 = 439·288 |
| Lemma 2 on a grid: min of f_N(q)/F_s(q; cst_N) over nine values of q in [10⁻⁵, 1] | all seven | 2.29–2.66 (≥ 1) |

**(Bat) at child level.** #555's helper runs have rank ≤ 5 ≤ h (checked by the replay in `a4_gap.py`). #568's helper
children have rank ≤ 6 ≤ h (its implied helper histogram in `a4_gap.py`). #568's README (commit 71c99ac,
research/complex-multicold/README.md:22) reports one whole owner for all 36,288 helpers, no auxiliary banks and 27,679
cross-replica roles; a cross-replica role hosts helper children of one idle change at rank ≤ h, so it falls inside
(Bat)/(Hst) (argued). No structural axiom is violated by #555 or #568.

### A.5 Gap decomposition at s = 9 (`a4_gap.py`, checked)

| step | #555 bit | #568 complex |
|---|---|---|
| A: theorem skeleton (R-free; idle slots at cap max(r, h)) | 4.6072e-3 | 3.9946e-3 |
| B: literal R = 0 (each idle slot one child of its own rank) | 4.5661e-3 | 3.9631e-3 |
| C: B with the real data-register runs and copy children | 3.7868e-3 | 3.1544e-3 |
| D: C plus every helper run paid unhosted (the only step with more rank mass) | 1.6183e-3 | 1.3517e-3 |
| E: the real word (helpers hosted whole, idle remainders paid) | 1.7331e-3 | 1.5987e-3 |

Shares of ln(A/E) (0.978 / 0.916):

| component | #555 | #568 |
|---|---|---|
| helpers | 87% | 93% |
| data fragmentation | 19% | 25% |
| literal vs cap | 1% | 1% |
| hosting | −7% | −18% |

Steps A, B, C and E have the same rank mass, m·W − D (1,808,352 and 520,704).

Inputs:

- **#555.** Data, helper and copy runs are replayed from the published word. The replay matches #555's local
  histogram, and the helper mass is 8R. The idle remainder is the published profile minus 288 × the local profile;
  75.3% of the skeleton idle mass is hosted.
- **#568.** The data-register runs per call come from #569's four-cold provider word (the same x/y ladders). The paid
  idle remainder {1: 93, 2: 93, 3: 2118, 7: 1, 48: 1713} is **recorded** from our replay of #568's hosting
  (`data/ceiling/gap568-inputs.json`). Its 4,018 children match the "4,018 positive idle remainders" of #568's README
  (checked), and the implied helper histogram is nonnegative (checked).

The headroom under S2 is therefore almost entirely helper cost. Even with zero helper cost and real data
fragmentation, the words would sit 2.19× (bit) / 1.97× (complex) above today.

### A.6 The superseded numeric scope of (Dfc)

Rev. 1 of this ceiling fixed cst_min = 72 and x = 3/5 (the full 120-line E8 unit) on both sides. That gave X_bit* =
5.1598·10⁻³, X_cx* = 4.5356·10⁻³ and κ ≤ 4.5151·10⁻³ (checked, `A1.rev1-superseded`).

The punctured units that the frontier now uses have smaller x:

- bit: #545/#555 keep 111 live lines with decoder constant 63;
- complex: the #523 lineage has 112 ports with copy cost 64.

So x = 63/111 = 0.5676 and 64/112 = 0.5714. With x_U taken from the realised units the ceiling is §A.3's
κ ≤ 5.1595·10⁻³. The structural axioms are unchanged.

Status of cst_min per unit:

| unit | cst_min | status |
|---|---|---|
| bit 120/72 | 72 | proved given #446 Theorem C: the F2 decoder of the E8 pattern needs 9 totals (its F2 minrank is 9; c = 8 is UNSAT, checked in `c6`), and each star total costs β = 8, the Gram rank of an 8-line in-cap clique (premise, not replayed) |
| bit 111/63 | 63 | the star floor among punctures of p ≤ 25 lines: Δcst ≤ min(p, 9), from an exact matroid-greedy search over the 9-dimensional code that this package does not reproduce (**argued**, not checked here). For 26 ≤ p ≤ 52 only the total D gain s·Δcst − (s − 1)p ≤ 9 is bounded, which does not pin x. |
| complex 112/64 | 64 | 8 × 8, the star floor at w_in = 8, attained (**argued**) |

A unit with smaller x would move X by about +2.8% per copy-rank unit at s = 9 (§A.3). For scale, two units with
smaller x that no word realises are checked as well (`A1.outside-scope`): bit x = 54/102 gives X* = 8.2457·10⁻³ and
complex x = 56/104 gives X* = 6.8000·10⁻³, both at s = 3. They lie outside the realised-unit scope of the theorem.

### A.7 What each scope rule is worth (`a5_scope_multipliers.py`, checked)

Multiplier of the ceiling if one rule is dropped. Each cell is best-s multiplier / s = 9 multiplier.

| rule dropped | bit 111/63 | complex 112/64 |
|---|---|---|
| star scope (copy charge x → 0) | ×6.77 / ×2.79 | ×6.91 / ×2.83 |
| B_K idle frame changes free | ×1.67 / ×2.14 | ×1.68 / ×2.15 |
| all idle changes of a copy in one child | ×1.19 / ×1.55 | ×1.20 / ×1.55 |
| bridges off the idle stretches (no split) | ×1.15 / ×1.18 | ×1.15 / ×1.18 |
| data local climbs batched to h (cross-register) | ×1.12 / ×1.03 | ×1.08 / ×1.02 |
| idle free and local batching together | ×1.79 / ×2.28 | ×1.79 / ×2.27 |
| family window one smaller at the same x | ×1.16 / ×1.16 | ×1.14 / ×1.14 |

Hosting cannot raise the ceiling (step (3) of the proof in §A.2). Full relaxation of (Bat), with arbitrary batching up to rank m,
would give no bound, because rank-m children cost 0.

**Not covered:**

- non-B_K schedules (a different number of active pairs per stage changes (Sch) and (Dfc));
- non-star decoders (totals with β_j < k·w_in), and units with smaller x than the realised ones (see A.6);
- labels outside the cross-field unit;
- any change to (P), such as children of rank larger than their frame change, or a new outer assembly.

## B. Spec versus convention census

`b_census_anchors.py` checks every file:line anchor of the rule table (B.2), 73 in all, and the four corrections
marked "checked" in B.3. Line numbers are as of the base commit 7dfa22b. Each anchor's quoted text must lie within two
lines of the cited line, except in docs/research/ (the hub's ledgers and reviews, which main rewrites often), where it
is matched by text anywhere in the file. The line ranges cited in the prose of B.1 and B.3 were read by hand at
7dfa22b and are not machine-checked. Paths are relative to the repository root, and `U/` is
`upstream/build/sections/`. The classification is argued:

- **S**: mandated by the upstream paper or interfaces;
- **P**: proved necessary given the cited S/C rules;
- **C**: a convention of the paper's instance or of the hub's checkers and templates, changeable if the replacement is
  proved.

### B.1 What upstream imposes

- **Bit contract** (the only bit-side interface), U/04-swap.tex:105-123. A finite circuit of W wires whose pointwise
  bit gates induce a *permutation* ρ. There is one rational m×m matrix per terminal and per gate, common to every wire
  at that gate. The cost is s = Σ rank_Q(M_head − M_tail), with M_out(ρ(w)) − M_in(w) = I_m on every role and s < Wm.
  The recurrence is F_k ≤ (s/W)F_{k−1} + O(1) (:197-211). No subspaces, nesting, banks, pairs or nondegeneracy appear.
- **Complex interface**:
  - frames C_U = H^m diag(i^{q_U}) H^m, with q_U(x) = wt(P_U x) mod 4 for nondegenerate binary U (U/03-motifs.tex:528-561);
  - an edge is a product of one kernel (aI + bX_v)^{±1} per vector of an orthonormal basis of the residual of
    comparable labels (:568-583);
  - endpoint C^{⊗m} on every role after free per-role corrections (:579-582, :641-668; U/05-layers.tex:127-154);
  - the implementation P_M conjugation needs only invertible M (U/05-layers.tex:86-103).
- **Common-frame identity** for any invertible D_v: U/03-motifs.tex:154-186.
- **The paper's instance**:
  - nondegenerate nested labels (U/03-motifs.tex:199-208, 351-364);
  - terminal labels X_a: U_a → F, Y_a: 0 → U_a^⊥ (:235-243);
  - the signed exchange of X_a and Y_a (:89-100);
  - arbitrary, restored scratch (:34-46).
- **Outer.** Two suppliers are composed through 08-assembly.tex (:16-48, κ at :849-866, :995-1000). The transforms
  are Nussbaumer synthetic transforms whose roots are signed shifts (U/00-introduction.tex:44-56, U/06-transforms.tex).
- **The maintainer's interface list**, docs/research/community-pr531-review.md:116-125:
  - all-size compilation;
  - common-label and mutable-basis realization;
  - normalized residual wrappers as uniformly priced operations;
  - whole-call correlated-helper hosting;
  - compressed windows and restored rows;
  - grids, tape, precision;
  - the analytic transfer.

  The same review of #531's integration says the fixed-word ceiling and family-optimality discussions it carries
  were "not independently certified" (:130-134).

### B.2 Rule table

Multipliers are from §A.7 (best s / s = 9, bit unit unless stated).

| # | rule | class | anchors (file:line) | evidence and history | ceiling multiplier if relaxed |
|---|---|---|---|---|---|
| 1 | Common frame at every gate | S | U/03-motifs.tex:157; U/04-swap.tex:111; legality_h.cpp:11; audit_local.py:64; LemmaG/Stream.lean:106 | never changed; an ADD across frames needs an adapter edge priced d(f, g) | 1.00 |
| 2 | Frames are nondegenerate subspaces | spec: any invertible D_v (S); nondegenerate subspaces: the paper's instance (C) | U/03-motifs.tex:154, :203; U/04-swap.tex:110; gram_frames.py:46; notes/general-clifford-frames.tex:21 | #130's general frame lemma covers arbitrary (also degenerate) binary subspaces, d = dim U + dim V − 2 dim(U ∩ V); main has its TeX note and Python checks, its Lean proof is in an external repository (a conditional interface); degenerate labels are dominated by their quotient (C.4) | none by itself (only through x) |
| 3 | Nesting: climbs along a register's life; drops only as copies or centre steps | C (priced, not forbidden) | U/03-motifs.tex:352 (the paper has decreasing edges); U/05-layers.tex:83; legality_h.cpp:11; audit_local.py:45, :128; LemmaG/Stream.lean:111 | #425's full → 0 centre copies; a non-nested step is exact and costs d(f, g) (C.1, C.7) | 1.00 (two nested edges) |
| 4 | Exact restoration of helpers and dirty registers | S (same endpoint operator on every role; scratch arbitrary); "ρ fixes scratch" is C | U/03-motifs.tex:46, :98, :581; U/05-layers.tex:150; columns_k.cpp:57; audit_local.py:101 | no PR permutes scratch | 1.00 |
| 5 | ρ = signed exchange of X_a and Y_a, pairwise | C (any permutation ρ is legal) | U/04-swap.tex:107; U/03-motifs.tex:99, :628; bit_global.py:55; columns_k.cpp:56 | never varied | not quantified |
| 6 | Terminal labels X_a: U_a → F, Y_a: 0 → U_a^⊥; targets inside u_t^⊥ | C (the paper's choice; the ⊥ relations then follow from #446 Thm A) | U/03-motifs.tex:235, :240; U/05-layers.tex:128, :146 | complement sinks are legal at zero cost but forced on every current decoder (C.3) | 1.00 on current decoders |
| 7 | Rank-1 labels (k = 1) | C | U/03-motifs.tex:233 | X depends only on (s, h/k, x/k) (§A.2) | through (w, x) |
| 8 | Star copies (cst = Σβ_j, β_j ≥ k·w_in) | scope assumption of the ceiling; the pairing-rank floor itself is proved for any copy tree (#446 Thm C) | legality_h.cpp:1; columns_k.cpp:39 | every PR's totals are star | ×6.77 / ×2.79 (complex ×6.91 / ×2.83); +2.8% per copy-rank unit at s = 9 |
| 9 | E8 cross-field unit (h = 8 bit, 9 complex) | C (family) | U/03-motifs.tex:221, :225 ("the scalar domain need not equal the label field") | — | window one smaller: ×1.16 (complex ×1.14) |
| 10 | Window m = k + s(h − k) | P (#446 Thm B) | — | attained by #386 | 1.00 in model |
| 11 | Deficit D = T[(s − 1)vk − s·cst] | P given rows 8 and 12; spec form D = mW − s | U/04-swap.tex:122; U/03-motifs.tex:360 | equality on seven profiles (§A.4) | through rows 8, 12 |
| 12 | B_K schedule (one dependency chain, alternating locals, bridges, idle children) | P given row 13 | bit_global.py:49; columns_k.cpp:46; Work__Bridge__Net.lean:56 | no other schedule on record | idle free ×1.67 / ×2.14; one idle child ×1.19 / ×1.55; no split ×1.15 / ×1.18 |
| 13 | One (X, Y) bank pair per invocation (LOCAL = 2V + R) | C | bit_global.py:12; columns_k.cpp:31; Work__Bridge__Net.lean:55 (one I : Inv for all stages) | no local on two pairs on record | feeds row 12 |
| 14 | (Bat): a paid child executes one frame change | axiom of the ceiling: one register across a local/bridge is the equal-frame rule; cross-register batching is open | docs/research/pr-ledger.md:403, :405 (#448 and #451 unreviewed) | #451's trace obstruction to #448's split residuals (C.8) | local batching ×1.12 / ×1.03; with idle free ×1.79 / ×2.28 |
| 15 | Whole-residual hosting | accepted conditional interface | community-pr531-review.md:122; idle-axis-hosting/PROOF.md:43 | #442 accepted; split residuals disputed (C.8) | 1.00 (Lemma H, §A.2) |
| 16 | One owner per stream (#458) | P inside #442's stream model | LemmaA/Realize.lean:95 (`one_owner_needed`) | relaxed to disjoint footprints | 1.00 |
| 17 | Source registers never destinations | C (#370's checker assertion) | e8-bit-carrier-skeleton/README.md:67-68 | sufficient, not necessary (#425); relaxed by #433, #493 | already taken |
| 18 | Payload bounds (2^104 bit, 2^192 complex prefix, 2^80 prime witnesses) | C, never binding | columns_h.cpp:25; columns_k.cpp:34; finite_check.py:98; audit_local.py:103; gram_frames.py:17 | — | 1.00 |
| 19 | F2 payload coefficients | C | columns_h.cpp:27 | — | 1.00 |
| 20 | Replication T | C | bit_global.py:11; finite_check.py:86 | #505 asynchronous replicas | 1.00 (T cancels) |
| 21 | 47-inequality outer assembly | structure S, constants C | outer.py:27; U/08-assembly.tex:37; assembly-domain-audit.md:21 | the 1/32 domain cap is conservative and not binding | 1.00 |
| 22 | κ is the composition of the two suppliers | S | U/08-assembly.tex:37; outer.py:29, :30 | — | — |
| 23 | Two suppliers: complex butterfly layer, bit address shear | S | U/00-introduction.tex:48, :56, :118; U/06-transforms.tex:12 | shift twiddles are already in the outer (C.5) | — |
| 24 | Pressure identity (a rank-r child priced as a fraction of a call) | inherited conditional ("normalized residual wrappers as uniformly priced operations") on the paper's rank-1 recurrence | U/04-swap.tex:197; community-pr531-review.md:122 | — | defines the ceiling |
| 25 | Bridges X → X and Y → Y only | P (X wires contain q, Y wires do not) | columns_k.cpp:43 | — | — |

Abbreviations:

- `legality_h.cpp`, `columns_h.cpp`, `columns_k.cpp` and `gram_frames.py` are in
  research/e8-bit-carrier-skeleton/code/bit/checkers/;
- `audit_local.py` is research/direct-delivery504-global/code/audit_local.py;
- `bit_global.py` is research/e8-early-reset-kernel/bit_global.py;
- `Work__Bridge__Net.lean` is in research/five-stage-gen4-banks/inputs/complex/sources/;
- `finite_check.py` is research/five-stage-gen4-banks/finite_check.py;
- `outer.py` is research/e8-bit-carrier-skeleton/code/pricing/outer.py;
- `LemmaG/`, `LemmaA/` are under research/e8-lemma-g-lean/ and research/e8-lemma-a-lean/;
- `community-pr531-review.md` and `assembly-domain-audit.md` are under docs/research/.

### B.3 Corrections, as the census found them

1. **The bit interface is the shear contract alone** (U/04-swap.tex:105-123). Subspace labels, nesting, Gram
   orthogonality, bank pairs and the pair exchange are construction-layer choices of the paper's instance
   (:199-243, 351-364), not interface requirements.
2. **Nesting is priced, not forbidden.**
   - The paper itself has decreasing edges (U/03-motifs.tex:352-353).
   - The paper counts kernels on decreasing edges (U/05-layers.tex:83).
   - #130's frame lemma prices non-comparable labels by d(f, g).
   - The checkers enforce nesting as a pricing rule.
3. **The bit legality checker** keeps its MOVE (nested and exactly priced), ADD (common frame) and COPY-lifecycle rules
   on legality_h.cpp:11; line 10 holds the containment helper and the owner/helper selection (checked).
4. **The invariant `Inv`/`GInv`** used by the complex five-stage bridge is imported (`import Work.Bridge.Inv`) and
   defined nowhere in main (checked). "One X bank and one Y bank per invariant" therefore rests on its use in
   `Bridge2` and in bit_global.py / columns_k.cpp, not on a definition in the repository.
5. **#370's assertion "x registers are never destinations"** is a sufficient, not a necessary, condition (#425's
   scalar-interface lemma; #493's README) (checked).
6. **The outer already uses shift twiddles** (Nussbaumer synthetic transforms; U/00-introduction.tex:44-50); the
   complex supplier is the H_0 butterfly layer (:114-121). A ring change does not remove it (C.5).
7. **Complement sinks** (sink = any complement of the source label, w·u = 1) are not covered by the earlier phase-frame
   null result: the sink stays a plain label with a new projection. They are legal (C.3, gate 0), and Lemma R closes
   them on every current decoder.
8. **The only untested spec freedom with a ceiling term ≥ ×1.15** is the schedule/ρ family (rows 5, 12, 13). The
   large multipliers (×6.8 copy charge, ×1.16 window) are scope and family terms, not rules.

Caveats of the census itself:

- "Sink = any complement of the source label" (row 6) was the census's own reading of U/05-layers.tex:145-148; it is now
  settled by C.3.
- "A plain swap of two scratch roles cannot gain" (row 4: shared gate frames give ≥ 2m on the swapped pair) is the
  census's own argument and is not re-derived here.
- #448 and #451 are unreviewed in the hub's ledger, so the "conceded" status of split-residual hosting rests on the
  contributors' own record.

## C. Structural lemmas

### C.1 Frame sandwich and the complex frame walls (argued; toy `c1_sandwich_toy.py` checked)

**Lemma (sandwich).** Let R be a register at time t, and consider paths that carry no priced drop. Then

  span{frame(r, t′) : r's content reached R drop-free by t}  ⊆  frame(R, t)  ⊆  (span{L_q : target q that R's content reaches drop-free after t})^⊥.

*Proof sketch.* The lower side is #446 Theorem A, applied with any register as origin. For the upper side, a target q
ends at L_q^⊥ because its terminal label absorbs the port gate (T_{u^⊥} = F·C_u^{−1} up to monomials). Chains are
monotone, and a copy taken at t sits at its parent's frame (common frame at the copy gate), so it inherits the
parent's future. Exactness uses neither side: both are accounting.

**Consequences** on the complex unit (labels in F_2^9, 112 ports):

- **(W1)** The common station of a term whose readers span u_a^⊥ is the point ⟨u_a⟩. A cut shared by all readers of a
  term is therefore one point per term.
- **(W2)** A copy serving a face of four targets of rank-3 span has frame dimension ≤ 6. A group of eight copies whose
  faces span rank 4 has a common frame of dimension ≤ 5.
- **(W3)** Run backwards on the cleanup, the lower side gives end(X) ≥ the join of the frames of every register that
  X's restoration reads.

**Leaving the sandwich is legal and priced.** The toy (n = 4) puts three readers whose labels span u_a^⊥ at a station
⟨w⟩ outside every u_i^⊥ and then takes a non-nested step to u_i^⊥:

- both networks are exact on 64/64 basis columns;
- every child's Clifford rank equals d(A, B) = dim A + dim B − 2 dim(A ∩ B), including the non-nested rank-4 steps;
- the charge is 18 = 13 + 3·2 − 1 against the standard network's 13.

Relaxing "targets avoid u_t" costs +2 data mass per relaxed target per call (C.7 prices this).

### C.2 Lemma N: the port factor is a gauge, always paid (`c2_port_gauge.py`)

**Setting.** C_v = ((1 + i)I + (1 − i)X_v)/2, so C_v² = X_v. The full transform is F = Π_{w ∈ orthonormal basis} C_w,
and T_{q^⊥} = F·C_q^{−1} (#514's repeated-axis identities). In the hub's controller a source family runs
⟨q⟩ → … → F and a target family runs 0 → … → q^⊥. Each data family saves exactly one unit (m − 1 instead of m), which
is the C_q gauge: (s − 1)vkT = 8·112·8 = 7168 on the complex side, of which copies take 4608 and D = 2560 remains.

**Lemma N.** For a parent child Z = C^{⊗A},

- rank(C_q^{±1}Z) = rank Z − 1 if q ∈ span(A) with odd support;
- rank(C_q^{±1}Z) = rank Z + 1 if q ∉ span(A) and q ⊥ A.

**Theorem N (proof).** With d(f, g) = dim f + dim g − 2 dim(f ∩ g), any path f0 → G → f1 costs at least d(f0, f1),
with excess

- **target** (0 → q^⊥): d(0, G) + d(G, q^⊥) − d(0, q^⊥) = 2(dim G − dim(G ∩ q^⊥)) ∈ {0, 2}, which is 0 iff G ⊆ q^⊥;
- **source** (⟨q⟩ → L): 2(1 − dim(⟨q⟩ ∩ G)) ∈ {0, 2}, which is 0 iff q ∈ G.

(dim G − dim(G ∩ q^⊥) ≤ 1 because q^⊥ is a hyperplane.)

The route T_{fY}·T_{fX}^{−1} equals F modulo monomials *only if* dim fX + dim fY = n and fX ∩ fY = 0. The source's
saving and the target's saving are therefore tied: un-labelling one side alone leaves a rank-1 mismatch on the pair.

**Consequence.** "y avoids u_t" is the geodesic condition of the endpoint frames, not an artifact of where the
factor is paid. Moving the rank-1 factor to the parent costs at least d(0, L) − d(0, q^⊥) = 1 per family. Leaving
the interval costs exactly 2.

**Checks (exact Clifford).**

- The F2 rank of B = Σqqᵀ equals the tableau child rank on 240 random C-products (n = 4..7).
- Detour excess is 0 on the geodesic set and exactly 2 otherwise:

  | n | geodesic | off-geodesic |
  |---|---|---|
  | 3 | 20 | 44 |
  | 4 | 128 | 408 |
  | 5 | 1072 | 4912 |
  | 6 | 3740 | 24510 |

  The source and target families give the same counts.
- The rigid pairs at n = 3, 4 are a subset of the complementary pairs. The converse fails: complementary pairs need
  not be rigid.
- The gauge descent rank − 1 holds in 9/9 controls.

**Not reproduced here.** A run on the 112 retained ports of the #523 controller found rank(C_q Z) = rank Z + 1 on
2016/2016 idle children and 2016/2016 stage climbs (no parent object absorbs the gauge). It needs the controller's
generated data-phase files, which this package does not ship, so it is reported, not checked.

### C.3 Lemma R: complement sinks are legal but pinned

**Legal (gate 0, `c3_complement_gate0.py`, checked).** For an odd w with w·u = 1, the route T_{w^⊥}·T_{⟨u⟩}^{−1} has
Clifford rank n:

- for every complement w at n = 3..6, and on 40 seeded samples at n = 9;
- it equals C^{⊗n} after monomial wrappers of the same class as the standard sink, on the tableau and on every basis
  column (n ≤ 6);
- non-complements (w·u = 0) give rank n − 2.

The port price is unchanged: Y: 0 → w^⊥ and X: ⟨u⟩ → F both cost n − 1. The geodesic interval is G ⊆ w^⊥, with
excess exactly 2 outside it. A corrector that the standard sink forbids is exact and correctly priced. So the sink
stays a plain label with a new projection, and the port gate stays a gauge (C_w instead of C_u).

**Lemma R.** If the sources whose content reaches target t drop-free span u_t^⊥, the only admissible complement sink
of t is w_t = u_t.

*Proof.* By #446 Theorem A the sink V_t = w_t^⊥ contains u_t^⊥, and V_t is a hyperplane.

**Pinned (`c3_complement_taint.py`, checked).** The checks run on four complex words: main's #531 word, the width-7
and four-cold provider words of #569, and the combined-eight-local word of #571. The closure starts every helper at frame 0, the most permissive choice,
so the result holds for every frame assignment of the same scalar word; the words' own entrance frames are not
needed (on the three vendored words the closure with them gives the same result).

- The most permissive lower closure (helpers enter at 0; every centre may drop to 0 at the cut) has dimension 8 on
  112/112 targets, so w_t = u_t is forced on 112/112.
- The pure drop-free source taint of every target is exactly its Gram-orthogonal neighbourhood: 52 sources, span
  u_t^⊥. Phase A contributes nothing to any target.
- Any w ≠ u_t breaks at least 20 of t's 52 lossless corrections (112/112 targets).

A positive control removes the 4 correction gates of one target. The closure then reports dimension 7 and 2
admissible sinks, so the instrument sees freedom when it exists.

On these four words the obstruction is the decoder's lossless pattern, not the endpoint rule. A decoder whose pairing is not symmetric
would be needed, and C.6 shows the E8 pattern admits none at window ≤ 9.

### C.4 Lemma Q: a degenerate unit is dominated by its quotient (`c4_quotient.py`)

**Setting.** The ports span W (dim d), with radical rad = W ∩ W^⊥ (dim ρ) and Gram rank r = d − ρ. Write
π: W → W/rad.

**Lemma Q.**

- A copy of total j read at a common cut g (g lies in every target sink, so WLOG g ⊆ rad) costs
  d(f_j, g) ≥ dim π(f_j).
- Summed over j, this is the quotient unit's reads-at-0 cost, which is ≥ Σ_j rank G[S_j, R_j] (#446 Theorem C at
  Gram level).
- Every stage window contains W and is nondegenerate, so h ≥ r + 2ρ.

Since X is non-increasing in a and in cst (§A.2), X_deg(s) ≤ X(s, r/k, x_quot) ≤ X(s, r/k, x_ThmC) for every s.
Star scope is Gram-level (an in-cap clique inside S_j has a nonsingular diagonal Gram block in every realisation), so
degenerate spans are not outside the ceiling's scope and add no (w, x) points.

**Checks (exact ranks).**

- **The paired-cube p = 3 toy:** d 4, ρ 2; copy cost 18 (reads at 0), 16 (optimum over all flags of rad), 12
  (quotient = Theorem C bound); window 6 vs quotient 2.
- **Paired cubes p = 3..12:** only the complex p = 3 cube is degenerate.
- **E8 + an extra vector (bit):** 81 → 72 = quotient 72, window 10 vs 8.
- **E8 + weight-2 isotropic decorations (complex), ρ = 1, 2, 3:** 80 / 88 / 96 → 72 = quotient, windows 11 / 13 / 15
  vs 9.
- **Random radicals:** 0 violations of "cut cost ≥ quotient cost" on 737 seeded instances.
- **Certified X:** each realisation sits below its quotient.

  | unit | quotient | realisation(s) |
  |---|---|---|
  | bit | 5.1598e-3 | 4.0462e-3 |
  | complex (ρ = 1 / 2 / 3) | 4.5356e-3 | 3.6522e-3 / 3.0570e-3 / 2.6286e-3 |

**Out of scope.** Repeated-label (vector-linear) decoders are a Gram-level class that Lemma Q does not close.

### C.5 Lemma λ: a phase-frame butterfly needs √−1 (argued; instances checked by `c5_lambda.py`)

**Lemma λ.** Let K be a directional kernel defined by its direction alone. If P_N(K ⊗ I)P_N^{−1} = K ⊗ I for the
e₁-fixing N, then K = aI + bX. If moreover H_0 = [[1, 1], [1, −1]] satisfies u·H_0 = D₁(aI + bX)D₂ with D₁, D₂
invertible diagonal and u a unit, then (b/a)² = −1, i.e. the Walsh eigenvalue ratio λ = (a − b)/(a + b) = ±i.

*Proof.* The first part is a 2 × 2 symbolic computation (T5). For the second, write D₁ = diag(d, d′) and
D₂ = diag(e, e′). Entrywise, d·a·e = u, d·b·e′ = u, d′·b·e = u and d′·a·e′ = −u. Multiplying the first and last
equations gives dd′ee′·a² = −u², and multiplying the middle two gives dd′ee′·b² = u². Hence a² = −b², so a and b are
units and (b/a)² = −1. With b = ±i·a, λ = (1 ∓ i)/(1 ± i) = ∓i. Writing λ needs a + b = a(1 ± i) invertible, and
(1 + i)(1 − i) = 2, so the ring must also make 2 invertible (H_0 itself has determinant −2). ∎

**Consequences.**

- A payload ring in which −1 is not a square (Z[1/2]; Z/M with a prime factor ≡ 3 mod 4) or in which 2 is not
  invertible (F2; even M) carries no phase-frame butterfly supplier.
- In a ring with √−1, such as the Fermat ring Z/(2^N + 1) where i = 2^{N/2} is a shift, the ring hosts the identical
  C-network with the same paid Fourier-rank histogram and the same b.
- The odd-weight residuals that the phase calculus needs (U/03-motifs.tex:600) force an odd-form unit. For E8 this
  means F2 rank 9 and h = 9, which is the structural part of b < c.
- Bit networks have signed-permutation endpoints per role for any payload alphabet. Each two-point butterfly level at
  most doubles row support, so a length-8 transform needs ≥ 3 butterfly levels, with the same Fourier-rank mass as the
  complex DFT₈.
- The outer already uses shift twiddles (B.3, item 6).

**Checks (exact, sympy / modular).**

- **T1–T3:** the product of three H_0 factors and three monomial twiddles equals the bit-reversed DFT₈. Over Z/17 it is
  the length-8 NTT with root 2. Row support 8 needs 3 levels.
- **T4:** brute force over Z/M for the 16 odd moduli M ∈ {3, 5, 7, 9, 11, 13, 15, 17, 21, 25, 29, 33, 37, 41, 45, 65}:
  solutions exist iff −1 is a square mod M, and λ² = −1 in every solution.
- **T5:** the commutation forces K = aI + bX.
- **T6:** C² = X and H_0 = b·S·C·S in Z/17 with i = 4.
- **T7:** there is no real solution.
- **T8:** weight-2-mod-4 residuals act as translations.

### C.6 Asymmetric pairing uniqueness at the E8 pattern (`c6_asym.py`)

**Setting.** A unit is (N over Q, B = W·Uᵀ over F2):

- window = rank B (the pairing version of Lemma Q);
- a correction N_TS is lossless iff B_TS = 0 (#446 Theorem A, directed);
- β_j = rank B[R_j, A_j] (Theorem C);
- exactness is N∘B = diag.

The gauge (U, W) ↦ (UP, WP^{−T}) fixes B, so "W ≠ U" means nothing by itself. A symmetric unit-diagonal F2 matrix of
rank r is congruent to I_r.

**Result (SAT).** At the E8-linear decoder pattern (B_TS = 0 where G_TS ≠ 0, B_TT = 1), gauge-fixed on 8
pairwise non-orthogonal lines (where the pattern forces B[K, K] = I, so U_K = W_K = [I_8 | 0]):

- P112 at c = 9: "B ≠ Bᵀ" and "B ≠ B0 = (J + G) mod 2" are UNSAT with U and W both free; with U fixed to the E8
  labels and W free, "B ≠ Bᵀ" is UNSAT too (the "B ≠ B0" question was not run with U fixed);
- P120 at c = 9: the same two questions are UNSAT;
- c = 8: UNSAT, symmetric and non-symmetric (P120), and non-symmetric on P112;
- calibration: c = 9 without the extra constraint is SAT, with B = B0.

So at window ≤ 9 the pairing is unique and every W ≠ U is a gauge. The UNSAT answers come from CaDiCaL (through
python-sat) without proof logs; the SAT calibration runs show that each encoding is satisfiable where it should be.

**Off the E8 pattern.** An exact asymmetric P112 unit exists at copy cost 65 (+1) and window 9: N′∘B = diag on all
112 × 112 entries. Two of its targets take sinks w ≠ u and need 28 corrections instead of 52. In this verified unit one extra copy-rank
unit (65 instead of 64) frees exactly two sinks; no lower bound on the price of a freed sink is claimed. A directed
3-cycle toy (B non-symmetric, rank 2,
exact on 343 inputs) shows that the asymmetric class is larger in general.

### C.7 Per-call descent pricing (`c7_descent_toy.py`, `c7_descent_price.py`)

**Statement.** A descent of rank r followed by its re-climb costs exactly 2r rank units in the local word. It
therefore costs 2r units of data mass in every call, which is 2r copy-rank units by the deficit identity. There is no
fixed cost to share between uses.

**Checks.**

- **Exact toy (n = 5).** One reader reads three cheap terms at point stations ⟨u_a⟩, ⟨u_b⟩, ⟨u_c⟩, and each term's
  readers span u_j^⊥.
  - Four networks (standard, clones, direct descents, descents through 0) are exact on 224/224 basis columns.
  - Every child, including the rank-2 non-comparable ones, has Clifford rank d(A, B).
  - Each rank-1 descent costs +2, whether direct or through 0, and a reader at k point stations pays 2(k − 1).
- **Prices on the published profiles** (certified root, hosting held fixed): one rank-1 descent per local word costs
  **−5.630% c on #555** (288 stage-replicas) and **−5.646% b on #568** (72 calls); two cost −11.26% / −11.29%.

**Dominance within the price class (argued).** In the known designs (the complex factory, face and M-copy ledger and
the bit pair-term and star units; this list is a census of those designs, not a theorem), each use of a descent buys at
most one of the following:

- one target removed from one last-read antichain (≤ |T_t| ≤ 7 private copies);
- two monotone arms for a copy register;
- two fixed pair-split conflicts;
- one supplied retired row.

That is at most about 7 helpers' work. One rank-1 descent costs −5.65% b on #568, about 40 width-9 complex helpers
at 0.14% b each (§E.1). So within the class where every non-comparable step is one child of rank d(f, g)
paid in every call, a schedule with ≥ 1 paid descent is dominated by the best schedule without one.

This is price-class dominance, not an impossibility. It does not cover a descent paid once per word.

### C.8 Split residuals across hosting streams (argued)

Split a helper residual of width w = a + b over two streams. #451 (chafreaky) shows that the identity
trace(D_{a+b} + I) − trace(D_a + D_b) = q^{2m−a−b}(q^a − 1)(q^b − 1) ≠ 0 is invariant under every invertible linear
change of storage; there is a complex analogue. So no relabelling makes an uncharged split exact. An exact split
needs one of:

- a cross-term repair (≥ min(a, b) doubly paid coordinates);
- one helper per piece;
- a new hub primitive that prices split routing.

The "one further route factor per helper selector" of #448 (higherbeing) is the last kind.

Even uncharged, the gain is small on the current complex frontier. #569 hosts all residual supply and pays the idle
remainder {3: 1200, 7: 48, 48: 1808} (90,720 coordinates; checked in `e2`). #588 uses the same hosting regime, but
its remainder differs and is not reproduced here. φ(r) = r((m/r)^q − 1) is concave, so with free
splitting the best case puts the whole remainder in rank-48 children: 1890·φ(48) = 60.98 against 78.06 today, a
saving of 17.08 D-units. That is **at most +0.67% b**, and it ignores windows and timing.

Status: argued (concavity bound on #569's reproduced hosting profile; the profile itself is checked in `e2`).

## D. Design-free helper bounds (`d1_cover_numbers.py`, `d2_coupled_count.py`, `d3_carrier_ledger.py`)

**Model.** Registers are monotone frame chains:

- helpers 0 → F;
- sources ⟨u_s⟩ → F;
- targets 0 → u_t^⊥.

Gates act at a common frame. The only drops are the decoder copies: 9 totals at p^⊥ (bit), 8 rank-8 centres
(complex). The demand is the drop-free source → terminal map.

**Crossing lemma (argued; #446 Thm A plus the sandwich).** Fix a level d. Every drop-free path s → q crosses level d
exactly once, inside one register's climb a → b, so N = Σ_e α_e β_eᵀ over the level-d crossing events, with
supp β_e ⊆ S(a_e) and supp α_e ⊆ Q(b_e^⊥). Each register crosses each level at most once. Only the extreme levels
bind: at the middle levels the rectangle areas are below the free data crossings.

**Cover numbers (exact).**

| side | per-source cover | per-terminal cover | evidence |
|---|---|---|---|
| complex P112 (F2^9) | 2 | 2 | two proper hyperplane sections cover every source's 52 readers (112/112; max section 32; 26 with port-spanned frames only, still 2 sections) |
| bit #555 (Q^8, E7 = the 63 lines ⊥ a source) | 3 | 3 | exhaustive census of the 8821 hyperplane flats of E7: two cover at most 52 of 63 (≥ 11 left), three D6 flats (30 lines each) cover all; on the terminal side at least 6 live sources stay uncovered by any two flats (all 120 terminals) |

**Floors.**

| side | sink-only targets | strict (y → y mixing allowed) | shipped |
|---|---|---|---|
| bit | 2·111 − ⌊111/11⌋ = **212** | max(3·111 − 222, 3·120 − 222) = **138** | 439 |
| complex | 112 − ⌊112/20⌋ = **107** (108 with port-spanned frames) | 2·112 − 224 = **0** | 496 (+ 8 centres) |

**Coupling adds 0 (checked).** The coupled cover model (hop areas through all levels, exact unit rectangle caps
32/32/32/36/32/32/32 for complex d = 2..8, exhaustive for d = 2..5 and by the symmetry d ↔ 10 − d above; end
patterns; bit flat sizes 1, 3, 6, 12, 20, 36, 63 per rank, enumerated in E7, with maximality in E8 from the
root-subsystem chain A1 ⊂ A2 ⊂ A3 ⊂ D4 ⊂ D5 ⊂ E6 ⊂ E7) has integer count optima 212 / 138 / 107 / 0 (HiGHS, zero gap),
identical to the single-cut bounds. The shipped words are feasible in it. With the shipped data ladders held fixed the
floors rise to 222 (bit) and 146 / 123 (complex).

**Corrections.**

- **The census of E7's hyperplane flats.** An earlier sampled census found 2258 flats; the exhaustive census has 8821
  (5040 / 2016 / 1008 / 666 / 63 / 28 of sizes 10 / 13 / 16 / 21 / 30 / 36). The sampled set is reproduced (seed 1) and
  undercounts the small types; the cover number 3 is unchanged.
- **The "224 carriers = 2 per source" complex floor is a design choice.** #531 gives every source exactly 3 level-2
  crossings (X_s + 2 helpers) into port-spanned 2-dim frames whose section is 20 (3 × 20 = 60 ≥ 52), while two
  sections already cover every source. The 224 is a property of the section type, not of the format.
- **Carriers are register-neutral in the calibrated ledger (checked).** The register ledger rebuilt from #531's real
  tile objects (168 block-local planes, 168 keys, mate matching 2) reproduces 224 scratch + 168 face copies + 112 M
  copies = 504, with B = N2 + K + R − 112 + waste. The carrier stage and the face stage together cost 2·N2 − 112 +
  waste for any edge cover. The cover axis therefore only enters through wasted single-variant butterflies:
  - rebuilding the same planes from cross-tetrad edges costs +168 (12 per block, exact);
  - tetrad edges give waste 0 (CP-SAT over all three splits).

**What the floors certify.** At most 48% (bit, sink-only, 212/439) / 22% (complex, 107/496 helpers without the 8
centres) of the shipped helper count is design-free necessary. No single-cut or coupled cover argument closes the helper gap that §A.5 identifies as the whole headroom.

## E. Complex helper prices and the moment-cost census (`e1_run_census.py`, `e2_helper_prices.py`)

### E.1 Price per helper by class and width on #569

The b gain per deleted helper is measured as follows:

- the helper is removed in all 72 calls;
- its width returns to the idle remainders;
- hosting is re-solved (the LP relaxation of the whole-owner model; integer CP-SAT spot checks at k = 1, not
  reproduced here, agreed with it to < 0.002% b).

The control reproduces #569's hosting (remainder {3: 1200, 7: 48, 48: 1808}, b = 1.602631811·10⁻³).

| cell (count) | width | % b per helper, k = 1 (checked) | k = 8 / 14 / whole cell (recorded) |
|---|---|---|---|
| factory scratch (216) | 9 | 0.140 | 0.142 / 0.143 / 0.179 |
| face copy (64) | 9 | 0.134 | 0.140 / 0.141 / 0.151 |
| face-copy entrant (72) | 8 | 0.105 | 0.102 / 0.101 / 0.081 |
| face-copy provider (32) | 7 | 0.075 | 0.069 / 0.062 / 0.050 |
| M-copy entrant (56) | 8 | 0.111 | 0.111 / 0.109 / 0.098 |
| rank-4 pivot (48) | 5 | 0.039 | 0.039 / 0.036 / 0.032 |
| rank-5 pivot (8) | 4 | 0.042 | 0.041 / – / – |

**Width law.** Price = local fee saved − hosting offset, where the offset is the increase of the hosting LP objective.
The offset depends on width only: cells of equal width have identical LP objective increases (checked). Its share of
the local fee at k = 1 (checked) is:

| width | 9 | 8 | 7 | 5 | 4 |
|---|---|---|---|---|---|
| offset share, k = 1 | 6.3–6.6% | 17.0–17.9% | 31.5% | 57.4% | 45.4% |

The share is not monotone in width (w4 sits between w7 and w5). At larger k the w7 share rises to 55% and the w5 share
to 65% (recorded in `data/prices/helper-price-table.json`). One conversion constant links all cells: fee saved minus offset is 25.64–25.66 moment units per 1% b.

A count-based "0.11% per helper" is therefore about right for the width-8 entrants (0.105–0.111), overprices the
width-7 providers by about 1.5× (0.075) and the rank-4/5 pivots by 2.6–2.8× (0.039–0.042), and underprices the
width-9 scratch and face copies by about 25% (0.134–0.140). Summed k = 1 marginals give:

| class | share of the marginal helper cost | % b |
|---|---|---|
| factory scratch | 53% | 30.2 |
| face copies | 32% | 18.5 |
| M copies | 15% | 8.4 |

Full table, including the mixed-class runs: `data/prices/helper-price-table.json` (k > 1 rows recorded).

### E.2 Moment-cost census by class (checked)

The F-share of a class is its share of Σφ = D at the word's own root. The all-single-run ceiling is the supplier value
if each register of the class climbed in one child, with hosting proportional.

**#555** (R = 439; 288 stage-replicas):

| class | n | runs | mean run | stops/register | F-share | all-single-run ceiling |
|---|---|---|---|---|---|---|
| line-born carriers (0,1,2,…) | 205 | 1120 | 1.46 | 4.46 | 29.5% | +14.75% c |
| cell-born (0,2,…) | 153 | 686 | 1.78 | 3.48 | 21.2% | +9.60% |
| line → quad/D6 keepers and totals | 80 | 349 | 1.83 | 3.36 | 10.7% | +4.35% |
| quad-born | 1 | 4 | 2.00 | 3.00 | 0.1% | +0.05% |
| data x / data y | 111 / 111 | 539 / 213 | 1.44 / 3.65 | – | 14.1% / 10.4% | – |

Copies take 0.7% and the idle remainder 13.4%.

**#569** (R = 504; width-7 provider word for all 72 calls):

| class | n | runs | mean run | stops/register | F-share | all-single-run ceiling |
|---|---|---|---|---|---|---|
| factory scratch | 216 | 1304 | 1.49 | 5.04 | 32.5% | +16.4% b |
| face copies | 168 | 696 | 1.98 | 3.14 | 21.9% | +9.1% |
| M copies | 112 | 504 | 1.43 | 3.50 | 12.4% | +4.9% |

Data take 28.3%, centres 1.8% and the idle remainder 3.0%. The published global profile is reproduced exactly from
63 width-7 calls, 9 four-cold calls and the remainder.

## F. What the results imply

**Cost structure (result).** Under S2 the ceiling is set by the copy charge and the B_K idle structure (A.7); on the
real words the headroom is helper cost, 87–93% of the log-gap (A.5). A change inside the local word is paid in every
call: the local word runs 288 times (stage-replicas) in #555's bit pipeline and 72 times in #568's complex pipeline,
and by the deficit identity each rank unit added per local word lowers D by one per call. On the published profiles one
rank unit per local word costs 2.82% of c (#555) and 2.82% of b (#568): half the checked price of a rank-1 descent
(C.7), and the same size as one copy-rank unit per stage (+2.8% of X at s = 9, A.3). What such a change unlocks (a
shared station, a freed sink, a removed copy, a supplied row) is a gain fixed per word.

**Break-even.** A change that costs Δ rank units in every local word pays only if its per-word gain exceeds about
2.8·Δ % of the supplier value. On the complex side that is about 20·Δ width-9 helpers (0.14% b each, E.1). The
per-call prices of C.1, C.2, C.6 and C.7 are all of this form: +2 per relaxed target per call, at least 1 per
un-gauged family per call, one copy-rank unit for the two sinks freed in the verified asymmetric unit, and 2r per
rank-r descent per call.

**Open problems.**

1. **Per-word enablers.** A mechanism charged once per word or per outer level instead of per call, such as a descent,
   gauge change or station hoisted out of the local word. At 1/72 of its per-call price a rank-1 descent would cost
   about 0.08% b, roughly half a width-9 helper. The current interface has no such primitive (B.2 rows 1, 3, 24).
2. **A non-star decoder.** The copy charge is the largest scope term (×6.8 at the best s, ×2.8 at s = 9; A.7). On the
   E8 pattern the pairing is unique at window ≤ 9 (C.6), and on the four complex words checked the lossless pattern
   pins every sink (C.3). Lowering x therefore needs a different unit or decoder; for scale, x = 54/102 (bit) and
   56/104 (complex) would give X* = 8.25·10⁻³ and 6.80·10⁻³ (A.6).
3. **The schedule/ρ freedom.** Any permutation ρ is spec-legal, and one bank pair per invocation is a convention (B.2
   rows 5, 12, 13). The B_K idle terms are worth ×1.15 to ×2.15 (A.7).
4. **New skeletons.** The design-free floors certify at most 48% (bit, 212/439) and 22% (complex, 107/496) of today's
   helper counts (D). The other 52% and 78% of the helpers are not shown necessary by any argument here.

## Files

- `scripts/`: one check per claim group, plus shared code.
  - Shared: `report.py` (PASS/FAIL, paths), `cert.py` (rational-interval ln/expm1, certified roots), `skel.py`
    (skeleton slots, variants), `e8units.py` and `minrank_sat.py` (E8 geometry, SAT encodings), `d_geometry.py`,
    `e_hosting.py` (the hosting LP and the moment root).
  - Driver and step 0: `run_all.py`, `provenance.py`.
- `data/vendor/`: inputs copied from open PRs (`SOURCES.json` gives PR, author, commit, path, git blob id).
- `data/ceiling/`, `data/census/`, `data/toys/`, `data/prices/`: small inputs (#568's recorded idle remainder, the
  census anchors, the p = 3 paired-cube instance, #569's call dispatch with its source blob id, the deleted-helper
  specs and the recorded price table).
- `DEPENDS.json`: files of main read by the checks, by sha256.
- `MANIFEST.sha256`: every file of the package.

## Credits

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0. See `NOTICE.md` for the
PRs whose words, pipelines and results are used.
