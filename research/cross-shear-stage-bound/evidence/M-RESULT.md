# M-math — feasibility memos for the [math] items (18, 21, 26 in depth; 23, 20, 49, 50, 53/97, 59, 60; one-liners for 28, 8/46/47/48/51/52/54)

Baseline: #325 package (`/private/tmp/imbwork/w325/research/five-stage-p10b-banks`, p = 10, h = 20, v = 960, m = 100,
κ = 7.69684039383334e-4). Histogram and sensitivities from the certificate agent
(`/tmp/radical/B-certificate-whatif/RESULT.md`): Δκ ≈ +3.8e-7 per unit of five-stage deficit, ≈ −2.9e-10 per
unit of five-stage J (per replica); five-stage J = 2,645,397 of which idle 225,855 (8.5 %), 5×local 2,419,542.
Nothing heavy was run. Three small exhaustive F₂/F₃ searches (seconds to minutes, one core) are in
`/tmp/radical/M/M_search.py`, `M_idle.py`, `M_idle2.py`, `M_portmix.py`, `M_p3k6.py`; their outputs are quoted below.

## 0. The pricing chain in one paragraph (what every item has to go through)

1. The local word's role chains are nested, ascending frame chains; every rank-d step is one recursive child of
   width d (`bitword/references/pr168-v4/research/paired-cube-bit/check_paired_cube_bit.py:303-315`,
   `bitword/bit/base_word.py:61-73`). The five-stage profile is 5×(local climbs incl. the h copied-centre
   transforms at rank h−2) + 2v idle children at ranks (2h−2, h−1, 2h+2, 4) + rank-5a entrance completions
   (`moment.py:91-103`, `code/global_lowering.py:120-135`), the completions being discharged by the banks
   (`math_check.py:57`, `BANK-PROOF.md:70-73`).
2. Price = the strict moment Σ_r (r·n_r/(mW))·(m/r)^a (+ 10⁻¹⁶·32m² fallback) < 1 (`moment.py:55-66`), which is
   the characteristic equation of the recurrence T(n,w) ≤ Σ_r (n_r/W)·T(r⌊n/m⌋, w) + Cn + Cw^{1−a_old}
   (`proof/three-stage-cover-bit.tex:253-264`, `proof/FINITE_BIT_ACCOUNTING.md:84-88`). Because every term
   carries 1/(mW) and Σ r n_r = mW − deficit, the root satisfies a·J + O(a²) = deficit with
   J = Σ r n_r ln(m/r): the stock W enters only through the deficit mW − mass, which is pinned to
   60·(4v − 5h(h−2)) (`math_check.py:60`, `word_pins.py:28-32`).
3. Three ordinary-leaf levels a_{j+1} = (1−c)c + c·a_j from a_old = 384599/10¹⁰ (`math_check.py:79-82`), then
   κ = ⌊(1−η)q/(1+q)⌋ with q = a₃(1−2η) (`math_check.py:85`) and the 47 outer constraints (`outer.py:16-58`).

So the only first-order levers are the deficit (4v − 5ℓ: one free rank unit per data family, minus the copied
centres) and J. Items 18, 21, 26 are deficit/J layout items; 23, 59, 60 are word-legality items; 49, 50, 28,
53/97 touch only the certificate layer, which has no slack.

---

## 1. Idea 18 — k-stage layouts (k = 4, "2+2 completion") — REFUTED for k < 2P+1

**(i) Where the five is fixed.** `global_lowering.py:27` `ACTIVE = ((0,1),(1,0),(0,1),(3,2),(2,3))` (source,
target bank per stage), `:33` `assert M == 5*H`, `:103-118` (stages 1 and 3 reversed with negated
coefficients, local P replaced by H−P), `:128-131` the six bridge families (same-frame ±1 shears X1±X2, Y1±Y2
after stages 1, 2, 4), `:147-151` the terminal exchange newX = oldY, newY = −oldX, `:184-194` the stage frame
P ⊕ K^{⊕i} (one h-block per stage, K = complement of the canonical port line q*). The proof text:
`UPSTREAM-PR234-PROOF.md:9` ("five phase-major invocations ... X1, Y1, X1, Y2, X2 ... five separated residuals
occupy disjoint windows. One split rank-5a exterior correction completes each ... entrance"),
`proof/INTEGRATED_PROOF.md:23-29, 33-37` (routes ρ_{i,S}, τ_i; "Every same-frame scalar gate telescopes exactly,
all idle transitions are nested actual projectors, and D_I D_Pq = D_(I−Pq) gives the terminal all-data address
endpoint after the scalar exchange"). The deficit formula 4v − 5ℓ (`word_pins.py:31`) is the bookkeeping
consequence: each of the 4v data registers climbs m−1 (X: rank 1 → 5h, Y: 0 → 5h−1, checked by the eight idle
projector pairs `global_lowering.py:204-215`), helpers climb exactly m, copies add 5ℓ of stockless mass.

**What the stages are for.** Simulating `iter_program` scalar-wise (ACTIVE, bridges, exchange) gives the
identity: stage 0 Y1 += X1 → (x1, x1+y1, x2, y2); stage 1 X1 −= Y1 → (−y1, x1+y1, ·, ·); bridge 0 → (x2−y1,
x1+y1, x2, y2−x1−y1); stage 2 → (x2−y1, x1+x2, ·, ·); bridge 1 → (−y1, x1+x2, x2, x2−y1+y2); stage 3 X2 −= Y2
→ (·, ·, y1−y2, ·); stage 4 → (·, ·, y1−y2, x2); bridge 2 → (−y1, x1, −y2, x2); exchange → (x1, y1, x2, y2).
I.e. the five word invocations plus free bridges realise the XOR swap (x,y) ↦ (−y, x) on **both** pairs, which
the terminal exchange then undoes while supplying the pair's two free rank units. Pair 1 gets the classical
three-shear swap (L U L), pair 2 only two shears, the third being borrowed from pair 1 through the bridges.

**(ii) What a k = 4 layout would have to prove.** A 4-stage circuit in which each stage is one local-word
invocation (a ±1 transvection Y_j += ±X_j or X_j += ±Y_j between the two families of one pair, in the stage's
own h-window), with free same-frame bridges and the terminal exchange, that ends in the scalar swap of both
pairs. The model's two legality facts are verifier rules: a source family's frame always contains its port line
(`check_paired_cube_bit.py:229`, `base_word.py:33`) and a target family's frame always lies in the cap
q_T^⊥ (`check_paired_cube_bit.py:363,367`, `base_word.py:92`), so an X-type and a Y-type family of the same
port are never at a common frame and can only be coupled by a word invocation; bridges couple like types only
(`global_lowering.py:128-131`). Bridges act on (X1,X2) and on (Y1,Y2) and generate GL₂(ℤ) on each.

**(iii) Refutation.** Write the 4 families as the X-block (X1,X2) and the Y-block (Y1,Y2). A stage is a rank-v
cross-block factor: L-type [[I,0],[E,I]] or U-type [[I,F],[0,I]] with rank E = rank F = v (one pair, all ports),
bridges are block-diagonal and conjugate E, F to arbitrary rank-v matrices. The required endpoint is
block-antidiagonal [[0,C],[E,0]] (C, E invertible). (a) Run argument, valid over any field and any v: adjacent
same-type stages merge into one factor of rank ≤ 2v; the (1,1) block of a product L U L is I + F·E₂, of
L U L U is I + F₁E₂, of U L U L the (2,2) block is E₁F₂ + I; vanishing forces a rank-2v factor out of a single
rank-v stage, so every ≤ 4-stage pattern fails (LUL and ULU need all three factors invertible = 6 stages).
(b) Exhaustive F₂ check (`M_search.py`, meet-in-the-middle over all cross transvections with free GL₂×GL₂ in
between): no product of 4 or 3 cross transvections is block-antidiagonal over F₂ or F₃; a ℤ-circuit would reduce
to one, so none exists. (c) `M_idle.py 2 4`: with every ordering of pairs/types and free bridges at every
position, k = 4 is unreachable; k = 5 is reachable (PR234). (d) General P pairs (`M_p3k6.py`, meet-in-the-middle
on the annihilation conditions [A₁₁ A₁₂]·[B₁₁;B₂₁] = 0): P = 1: 2 stages ✗, 3 ✓; P = 2: 4 ✗, 5 ✓;
P = 3: 6 ✗ (alternating patterns exhaustively, non-alternating ones by the run-rank argument, since the (1,1)
block minus I is Σ_j F_j(·) and needs #U ≥ P, #L ≥ P), 7 ✓ over F₂. So k_min(P) = 2P+1 for P ≤ 3, which is
exactly B's "consistent model" (deficit 2Pv − (2P+1)ℓ), already priced negative for P ≥ 3 at p = 10.
A pair that is never active cannot get its two free units either (its swap would have to come from like-type
bridges alone, impossible by (b)).

**(iv) Loopholes / what remains open.** Only a *two-sided* local word (an invocation whose scalar endpoint is
not a transvection but e.g. (x, y) ↦ (x, x+y) and (x−y, ·) simultaneously, i.e. rank 2v per stage) could beat
2P+1; nothing in the paired-cube producer supports it (sources are restored: `notes/paired-cube-construction.tex:105-110`),
and it would be a new generator (months, plausibility very low). The exchange cannot be used mid-way (an X family
at a K-type frame violates the source-line rule). **Verdict: refuted** for k = 4 (and for every k < 2P+1);
k ≥ 6 with P ≥ 3 is legal in form but priced negative by B.

---

## 2. Idea 21 — merging the idle boundaries ((2h−2, h−1) → 3h−3) — REFUTED

**(i) Where the split is fixed.** `global_lowering.py:120-126` (boundary 0 after stage 1: X2: P₀ → H₁ and
Y2: 0 → K₁, rank 2h−2 each; boundary 1 after stage 2: X2: P₂ → P₃, Y2: 0₂ → 0₃, rank h−1 each; boundary 2 after
stage 4: pair 1 H₂ → I and K₂ → I−P (2h+2), pair 2 H₄ → I, K₄ → I−P (4)); `:137-143` idle **then** bridges at
each boundary; `:204-215` the exact projector pairs; `proof/INTEGRATED_PROOF.md:35` ("all idle transitions are
nested actual projectors"). The ranks are not free constants: a family parked since position a that must be at
the position-b geometry climbs exactly (b−a)(h−1) (the stage geometry adds one K-block of rank h−1 per stage,
`global_lowering.py:184-194`), and the terminal climbs are (5−p)(h−1)+4 for X / for Y with the I−P endpoint.
So the idle multiset is determined by the *positions at which a parked family must be current*, and a parked
family must be current exactly when it takes part in a bridge or becomes active.

**(ii) What the merge would have to prove.** A 5-stage circuit in which pair 2 has no bridge event before it
becomes active at stage 3 (then X2, Y2 climb once, 3h−3, from their initial frames to the stage-3 geometry).
Equivalently: a scalar circuit with D₁ = D₂ = I (no bridges after stages 0 and 1) — bridges at position 0 are
free of idle cost (X1[t], X2[t] both sit on the port line ⟨χ_t⟩, Y1, Y2 at 0), so they were allowed.

**(iii) Refutation.** `M_idle.py 2 5` with patterns over positions 0..5: ['both','none','none','both','none',
'both'], ['none','none','none','both','both','both'], and all variants with X-only or Y-only bridges at position
3 are **unreachable** over F₂ for every ordering of pairs/types; `M_idle2.py`: restricting positions 1–2 to
X-only or Y-only bridges (one family merged, the other split) is also unreachable, while any pattern with both
an X-bridge and a Y-bridge at positions 1 or 2 is reachable — and every such pattern gives the same idle
multiset {h−1, 2h−2} per pair-2 family. Hence (2h−2, h−1) is optimal for the pair-2 families and (2h+2),(4) are
forced by the end positions. Port-mixing bridges cannot rescue it: at position 0 only Y-bridges can mix ports
(X frames are port-specific lines), and `M_portmix.py` (the exact Schur-complement criterion for "two rank-v
stages with arbitrary bridges", v = 1 exhaustive, v = 2 randomised over F₂ and F₃: 1,728 + 14,400 + 307,200
cases) finds no feasible case; for port-diagonal bridges the v = 1 result lifts to all v because all blocks
are m'⊗I_v. The hand check in B's table ((2h, h, 2h, 3), (2h−1, h, 2h+2, 2) ...) are mass-preserving re-splits
with no corresponding geometry (ranks must be multiples of h−1 plus the fixed terminal pieces).

**(iv) Verdict: refuted** within PR234's structure (+2.1e-5 … +3.0e-5 is not available). Residual: the
*order* of the two pair-2 idles is immaterial; the only idle-side slack would be a different endpoint
convention (both families ending at I), which loses a deficit unit per family (−3.8e-7·v) and is far worse.

---

## 3. Idea 26 — ℓ = h(h−3) instead of h(h−2) — OPEN, needs a new decoder (not a completion-proof change)

**(i) Where ℓ is fixed.** `notes/paired-cube-construction.tex:65-79` ("Coordinate-star copied centers":
S_i = Σ_{S∋i} x_S, its binary source span U_i = {u : u_ī = 0, Σ_{j∉{i,ī}} u_j = 0}, dim U_i = h−2, proof by the
triangle in the outside-edge graph for p ≥ 4; "Each star is assembled from its half-cube channels, at frames
contained in U_i. The copied-center interface therefore charges ℓ = h(h−2), including degenerate U_i").
Verifier: `check_paired_cube_bit.py:241-249` (`centre frame = star span`, `loss` = Σ dims = ℓ), `:318` and
`base_word.py:75` (one copied-centre transform child of rank dim(centre frame)), `code/physical527.py:66` (the
COPY record at the centre frame), `word_pins.py:28` (`ell = h*(h-2)`), `moment.py:94-95,101` (mass identity
h·R + 2v(h−1) + ℓ − gauges, deficit 4v − 5ℓ), `math_check.py:60`. The copy mechanism:
`proof/copied-centers-lemma.tex:37-84` (copy transformed D_U → D_0 at rank r = dim U, original D_U → D_1 at
rank h−r), `proof/INTEGRATED_PROOF.md:27` (copies are lowered afresh in every stage, hence the factor 5).
The "5" cannot be shared across stages (the copy lives in the stage's own block geometry).

**(ii) What the completion proof requires of a centre.** Only three things: (a) its frame contains the span
of its conservative support (value-span rule `base_word.py:33`; `paired-cube-construction.tex:49-51`,
"Signed cancellations do not remove visited address directions"); (b) the frame is G-nondegenerate
(`check_paired_cube_bit.py:375`, Lean `formal/lean/KappaCheck/Frames.lean:93-94` proves anisotropy of
"triples through a common point" for I − J/9); (c) targets read it at their own cap frame, which never
contains U_i (for u ∈ U_i, (3χ_T − 1)·u = 2u_i + 3(u_b+u_c) ≠ 0), so the read must go through a copy
transformed by rank dim U — this is why the copy exists at all. Nothing in PR234/BANK-PROOF depends on the
value h−2 beyond the pinned formula; a centre of rank h−3 would pass the five-stage lowering unchanged
(`global_lowering.py:32` reads `CENTER` from the shape), and the bank identity telescopes (J's finding).

**(iii) What a derivation would have to establish.** A decoder B = G·Fᵀ (B_{T,S} = (|T∩S|−1)/2,
`paired-cube-construction.tex:1-15`) whose centre functionals f_j have Σ_j dim span(supp f_j) ≤ h(h−3), plus
modules that assemble each f_j at frames inside its span. Constraints: B = ½ Σ_i n_i n_iᵀ − ½·11ᵀ has rank h, so
any factorisation needs ≥ h centres; the point stars are the unique rank-(h−2) choice (J-arith verified
numerically; splitting a star always costs more). My partial no-go for "fewer coordinates": a functional in the
row space of B is affine in χ_S (f(S) = λ·χ_S + μ); requiring f = 0 on every port touching a pair {a,ā} and
one more coordinate b forces λ ≡ const and μ = −3c, i.e. f ≡ 0 — so no row-space element has support inside a
"three coordinates avoided" subspace, and the rank-(h−2) stars are the minimum inside the row space. What is
open: factorisations with k > h centres whose individual f_j lie *outside* the row space (only their span must
contain it), with Σ_j rank_j < h(h−2); half-star splits give 2h·(h−3) > h(h−2), and every factorisation tried
by J-arith costs more. Concrete lemma to prove or refute: "for every G, F with G Fᵀ = B, Σ_j dim span{χ_S : F_{Sj} ≠ 0}
≥ h(h−2)". If the lemma is false, the construction is a new generator (modules computing the new centres from
half-cube channels at frames inside their spans; the 35-call target schedule and the caps [h−4,1,1,1] would
change too).

**(iv) Value and effort.** +3.8e-5 uncapped (+2.4e-6 under #315's complex cap, +9.3e-6 under #327's), i.e. ~100
deficit units, by far the largest legal-looking lever. Effort: 1–2 weeks to settle the lemma (it is a finite
rank-minimisation over factorisations of a fixed 960×960 rational matrix; an exact answer for p = 5–7 by
MIP/SAT would already be decisive), then months for a generator if it fails. Plausibility that a cheaper
factorisation exists: low (≈15 %); the row-space argument above and J's split census both point to the stars
being optimal. **Verdict: open, with a concrete lemma; if the lemma falls, needs a new generator.**

---

## 4. Idea 23 — non-nested chains — DEAD (would cost, not save)

Where nesting is used: (a) a frame change Q₁ → Q₂ is one recursive child of width rank Q₂ − rank Q₁ only
because D_{Q₂}D_{Q₁}⁻¹ = D_{Q₂−Q₁} for nested commuting projectors (`proof/three-stage-cover-bit.tex:17-28`,
"Nested commuting-projector identities are polynomial identities"); (b) the telescoping mass identity
(`base_word.py:105-106`, `moment.py:95,101`, `math_check.py:60`) and the completed residual D_(I−σ) of every
helper (`BANK-PROOF.md:8-14`) assume monotone chains; (c) the verifier rules `check_paired_cube_bit.py:310,312`
(`nested role chain`, `ascending role chain`), `:362` (target chains), `base_word.py:70,79`. A non-nested step
U → V is *already expressible* as the nested pair U → U∩V (descent) → V (climb): both are single partial swaps
of the same contract, so no new certificate is needed — but the descent is a paid child, the register's total
paid rank becomes (m − initial) + 2·(descents), the deficit shrinks by the descended rank (−3.8e-7 per unit), and
concavity of r ln(m/r) makes the split climbs costlier still. The only conceivable use (placing a gate at a low
frame not comparable with an operand's current frame) is forbidden by the value-span rule, not by nesting
(see item 60). Δκ ≤ 0. **Verdict: dead** (days to prove formally; nothing to gain).

## 5. Idea 20 — other Gram forms — NEW DECODER FAMILY, months, Δκ unknown

The pricing layer never sees G (B's finding). G enters as: `H0 = (I − J/9)/2` with q_Sᵀ H0 q_S = 1 and
H0(χ_T, χ_S) = (|T∩S| − 1)/2 = B_{T,S} (`proof/three-stage-cover-bit.tex:52-53`,
`paired-cube-construction.tex:1-15`): the 9 is |S|·|T| = 3·3, chosen so that ports with |S∩T| = 1 are
G-orthogonal and the cap of T is q_T^{⊥_G} = ker(3χ_T − 1) (`check_paired_cube_bit.py:222,247`). Legality:
nondegeneracy of every frame (`:375`; det G = (9−h)/9, hence the excluded prime 11 at h = 20, `PROOF.md:163-164`),
`geometry527.py` route checks, `BANK-PROOF.md:29-30` residual rows (h−9)a − Σa. The admissible family is
therefore "I − J/s² for ports of size s" (s = 3 today), or any form for which the chosen port set has the
intersection-1 orthogonality and all used spans are nondegenerate; changing it changes v, ℓ, R and the whole
module design (s = 4 cubes have 16 ports, v = 16·C(p,4), stars of rank ?). It cannot be evaluated without a
generator. Lean only covers I − J/9 (`Frames.lean`). **Verdict: open but needs a new generator**; plausibility
low; effort months; expected Δκ unknown (sign unknown).

## 6. Idea 49 — the concave price r·ln(m/r) — DEAD (no slack; a different price = a different primitive)

r ln(m/r) is not a theorem but the derivative of (r/m)^{1−a} at a = 0: the exact price is the Akra–Bazzi root of
Σ (n_r/W)(r/m)^{1−a} = 1 (`moment.py:55-66`), whose certificate has 1e-18 slack (B: +1.0e-18). The exponent
"child of width r costs T(r·n/m)" comes from `proof/three-stage-cover-bit.tex:86-134` ("the middle operation is
exactly one rf-atom call of the same contract"): a split-rank-r partial swap *is* an interchange of an r/m
fraction of the volume. A cheaper price for rank r would need a child that is not a full interchange of its
residual (a structured primitive, e.g. exploiting that the residual projector is a coordinate block), i.e. a
new §"weighted child" lemma and a new finite bill — months, plausibility very low. **Dead.**

## 7. Idea 50 — entrance-stock price — DEAD (entrances are exactly deficit-neutral by construction)

An entrance of rank a is priced as (h−a)/h of a stock unit (its residual block of width h−a tiles a bank,
`BANK-PROOF.md:77-89, 100-108`; literal stock = 60·4v + 5·banks_per_stage, `math_check.py:56,59`) and climbs
5(h−a) = m·(h−a)/h, so it contributes 0 to mW − mass; the completion child 5a is removed (`math_check.py:57`).
Since κ depends on W only through the deficit (§0.2), there is no "stock price" to recover. Making an entrance
contribute deficit would mean a role of full stock that climbs m − 5a, i.e. a padded bank, which
`BANK-PROOF.md:86-89` explicitly forbids ("its unused coordinates would count as stock without children and break
the telescoping identity"). The kernel donors' ZERO → E climbs (`STAGES-PROOF.md:35-40`) are genuine moves and
are already optimised by the kernel search. Δκ = 0. **Dead.**

## 8. Ideas 53 / 97 — the inherited machine model — DEAD for κ

What is assumed: the upstream paper's main theorem and chunk-swap lemma (`upstream/build/sections/00-introduction.tex:22-31`:
"one deterministic Turing machine A, with a fixed finite alphabet and a fixed finite number of one-dimensional
tapes"; `sections/04-swap.tex:285-300`, Lemma "Arbitrary-width interchange", O(V u^τ)), re-stated in the repo as
`notes/finite-alphabet-transfer.tex:10,35-36,57` and the retained interfaces listed in `PROOF.md:241-247`. The
only model-dependent constants in the κ chain are: the ordinary-leaf saving a_old = 384599/10¹⁰
(`math_check.py:79`; it is the bit saving of the κ = 3.84569e-5 copied-centres network, icekylinx commit
`11817cc`, `notes/copied-centers-assembly.tex:83`, used as the stopped-leaf cost O(V w^{1−a_old}),
`notes/stopped-product-interface.tex:22-29`, `proof/three-stage-cover-bit.tex:156-158`), the fallback envelope
10⁻¹⁶·32m² (`proof/INTEGRATED_PROOF.md:41`), and η, β. Their total influence on κ is < 1e-11 (B's table;
chain start: ±3e-14 even for a_old ∈ [0, 1e-4]). A stronger machine model (k tapes, larger alphabet) changes
only the primitive constant C (`proof/FINITE_BIT_ACCOUNTING.md:10-28`), never the recurrence; a RAM/circuit model
would change the *problem* (the result is specifically about multitape TMs). Lean-ing the bound (53) is months
for Δκ = 0; what is formalised today is the κ = 83e-12-era arithmetic, the I − J/9 label algebra, guard and
layout lemmas (`formal/lean/README.md`), none of the five-stage word. **Dead for κ.**

## 9. Idea 59 — nested temporaries — LEGAL ALREADY, NO VALUE IDENTIFIED

The proof already budgets h simultaneous temporaries: `proof/INTEGRATED_PROOF.md:54` ("Even paying 24
simultaneous temporaries gives physical stock 23,707"), `proof/FINITE_BIT_ACCOUNTING.md:90-97` ("Paying all 24
temporary roles ... The temporary roles never enter the denominator W"), `PROOF.md:222`. Only the lowering
forbids overlap: `global_lowering.py:34` one WORK family, `:247` `assert not copy_open`;
`parity_transform.py:126-128`; `reorder_transform.py:132-134`. Relaxing it is a days-scale verifier change plus
re-deriving the finite stock bound with the actual overlap count. Value: a temporary is stockless mass, so every
extra copy lowers the deficit by its rank unless it replaces a costlier climb; J-arith found no such use (reads
of a temporary are only legal at ZERO). **Verdict: legal (up to h open lifetimes) but worthless as far as anyone
has found; Δκ ≈ 0.**

## 10. Idea 60 — gate frames below operand spans — OPEN BUT NEEDS NEW FRAME SEMANTICS

Enforced by `base_word.py:30-33` (`value span in replacement operation frame`), `check_paired_cube_bit.py:233-236`
(leaf label / operand frame inside node frame), `reorder_transform.py:43-55,123` (`span_violations`: exact
integer source span of every non-target operand ⊆ gate frame). The convention is stated, not proved, in
`notes/paired-cube-construction.tex:49-51` ("Every aggregate's conservative support ... Its physical frame
contains the span of that support ... Signed cancellations do not remove visited address directions") and
`notes/paired-cube-bit.tex:28-31` ("inherited conservative support convention; an even coefficient would merely
give a zero bit read with a retained frame"). The F₂/integer replays (`scalar_check.py`, `virtual_check.py`)
check scalars only and would not detect a frame that omits a direction, so "a corrected integer replay" cannot
certify the relaxation; the frame contract is the arbitrary-subspace Clifford interface
(`notes/general-clifford-frames.tex`), and a value whose stream sits at a frame missing one of its address
directions has no meaning there. What a derivation would need: a lemma that a direction on which a value depends
only through a coefficient that cancels (after parity fusion essentially none remain: J-arith shows the removed
578,560 even gates all sit at rank 0) may be dropped from the frame. Potential value is unquantified (dirty reads
at ranks 16–18 dominate J), plausibility low. **Verdict: open, needs a new frame lemma; not a verifier tweak.**

## 11. One-liners (all ≤ 3e-12, from B's table; mechanism confirmed in the code)

- 28 chain depth / start constant: fixed point of a_{j+1} = (1−s)s + s·a_j is s, loss after 3 levels
  s³(s−a₀) = 3.3e-13 (`math_check.py:79-82`); a₀ ∈ [0,1e-4] moves κ by < 3e-14. Dead.
- 8/46/47 certificate slack: root is exact to 1e-18 (`moment.py:73-89`). Dead. 48 grid rounding: +1e-18. Dead.
- 51 replicas: moment is scale-invariant in T (`math_check.py:59-64`); T only enters the finite bill. Dead.
- 52 fallback envelope: +3e-12 (`moment.py:61-65`). Dead. 54 η, β: +2.3e-15 (`outer.py:16-21`). Dead.
- 49 slack: +1e-18 (above). 50: 0 (above).

---

## Ranked list (expected Δκ × plausibility / effort)

| rank | item | Δκ if it works | plausibility | effort | expected value | verdict |
|---|---|---|---|---|---|---|
| 1 | 26 ℓ = h(h−3) via a new decoder | +3.8e-5 uncapped (+2.4e-6 / +9.3e-6 capped) | 0.15 | 2 weeks (lemma) + months (generator) | ≈ +6e-6 uncapped | open: prove/refute "Σ_j dim span(supp f_j) ≥ h(h−2) for every B = GFᵀ" |
| 2 | 20 other Gram forms (ports of size s, I − J/s²) | unknown, could move v/ℓ by O(1) factors | 0.1 | months | unknown | open, needs a new generator |
| 3 | 60 frames below spans | unquantified (bounded by the rank-16/17 dirty-read mass) | 0.05 | months | small | open, needs a new frame lemma |
| 4 | 18 two-sided local word (only way past k = 2P+1) | +4.5e-4 | 0.02 | months | ≈ +9e-6 | k = 4 refuted; this loophole is a new generator |
| 5 | 59 nested temporaries | ≈ 0 | — | days | 0 | legal already, nothing to gain |
| 6 | 23 non-nested chains | ≤ 0 | — | — | 0 | dead |
| 7 | 21 merged idle | +2.1e-5…+3.0e-5 | 0 | — | 0 | refuted (F₂ exhaustive) |
| 8 | 49, 50, 28, 53/97, 8/46/47/48/51/52/54 | ≤ 3e-12 | — | — | 0 | dead |

Bottom line: within PR234's completion the stage count (2P+1) and the idle split ((2h−2, h−1) per parked
family) are forced, provably over F₂; the deficit 4v − 5ℓ can only move through ℓ, and ℓ can only move through a
decoder that is not the point-star decoder. Every certificate-level item is exact to 1e-18.
