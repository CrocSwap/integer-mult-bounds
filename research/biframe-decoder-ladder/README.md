# Delivery lower bounds for #968's frame-pair centers, with an independent re-derivation of its floor (no κ claim)

**Research note: a scoped negative result for one realization class, plus independent verification. No κ
claim, no supplier word, no change to the selected frontier.**

#968 (themilkman216, merged) explains #717's cheap complex decoders (cst 63 on P111, 56 on P104) as
frame-pair decoders. It proves the exact 8-term floor: cst ≥ 72 − p for p ≤ 15 and cst ≥ 56 for p ≤ 24.
It prices P104's favorable budget at **+5.51% b** on the selected T37 profile, and notes that the PR589 bit
cap leaves only about 1.33% of b. It leaves the *construction* of the asymmetric centers open (center
reads, frame legality, restoration).

This package was developed independently. It drew the same sprint seed (47) and reached the same floor
before #968 was posted, but was submitted after #968 merged. The floor is #968's result. What this
package adds is a lower bound on the cost of delivering those centers, plus an independent check.

| | result | status |
|---|---|---|
| 1 | **The cut is not common.** A P104 center gathers in u_b^⊥ and is read by targets whose labels span u_a^⊥. Theorem C's survivor is ⟨u_a⟩, so the cheapest copy tree drops u_b^⊥ → ⟨u_a⟩ at cost 7, not to 0. A reader must therefore stand at a frame containing u_a. Targets read 2/3/4/5/6 mixed centers (12/24/32/24/12 targets), and their cut frames have exactly that dimension. The coordinate decoder reads everything at frame 0. | checked |
| 2 | **Single cut needs ≥ 144 copies.** Each center's 52 readers need 52 distinct cut frames, with 1059 incomparable pairs. A copy that is never dropped again only climbs, so it serves one chain of nested frames. Dilworth gives ≥ 19 chains per center: 152 in all, so ≥ 144 copies beyond the 8 centers. | checked |
| 3 | **Staggered reads need ≥ 47 copies.** If all targets read the centers in one global order, climbing by u_{a_k} before each read, each center's reads form one phase. Over all 40,320 orders the minimum is 55 chains, so ≥ 47 copies. | checked exhaustively |
| 4 | **Against #968's budget**, at #717 P3's helper prices:<br>• Single cut costs ≥ **7.3% / 10.1% / 20.2% b** at w8 / w9 / w9-merged. That exceeds 5.51%, so no single-cut realization with w8–w9 copies can help, and none reaches the bit cap at any listed price.<br>• Staggered delivery costs ≥ 2.4% / 3.3% / 6.6% b. That is inside the budget at no-merge prices and outside it when merged. It reaches the bit cap only if every copy prices like a width-4 helper. | arithmetic checked; budget and prices cited |
| 5 | **Independent re-derivation of #968's floor** with a separately written verifier:<br>• all 11 of #717's D3 hit files (#968 replays 3) are exact bi-frames;<br>• the span thresholds are enumerated over all 255 W(E8) classes of supports directly, with no flat-containment citation;<br>• the D7 orbit, the 896-of-1260 census and the bound are reproduced;<br>• W(E8)-transitivity on the 2025 frames is checked;<br>• **new:** the fully mixed bi-frames are exactly the unimodular root bases whose dual bases are roots (|det| = 1 on all 7168). | checked; lemmas proved |

So the decoder-side gain that #968 prices is not reachable with a barrier cut and shipped-width copies. With
staggered reads a window of at most about 3% b remains (5.51 − 2.40). It needs a 104-port skeleton whose
delivery copies are exact, restored and frame-legal, and which uses at most ~79 copies at w9 or ~39 merged.

```sh
python3 -B research/biframe-decoder-ladder/verify.py            # ~35 s, standard library; compares RESULTS.json
python3 -B research/biframe-decoder-ladder/verify.py --orders   # also re-runs the 40,320-order search (~6 min)
```

Expected last line: `PASS_BIFRAME_DECODER_LADDER: P104 centers need >= 144 delivery copies at a single cut, >= 47 staggered; #968 floor cst >= max(v - 48, 56) re-derived; 11 #717 decoders are exact bi-frames; 10 controls`.

## 1. Model

This is the B14 model of #717 §5 (from #595 C.3 and #446 Theorem C), rebuilt independently in `verify.py`.

- The ports are lines of E8, Gram G (diagonal 2, off-diagonal 0 or ±1).
- The label of a line is u_r = (r mod 2E8, 1) ∈ F₂⁹, with the form ω ⊕ 1. Then u_r·u_s = 1 exactly when ⟨r, s⟩ is even.
- A decoder on a port set P is a list of terms (d_k, t_k) with Σ_k d_k t_kᵀ = 2G on P.
- The cost β of a term with row support R and column support A is the F₂ rank of the label pairing span U(R) × span U(A). cst is the sum of the β.
- F0 = {e_{2a} ± e_{2a+1}} is the coordinate frame, and P112 = P120 − F0.

The explicit P104 decoder used below is in `RESULTS.json`: F0, a frame C of the 896 class, and 8 root pairs
(a_k, b_k), with d ∈ {0, ±1}, t ∈ {0, ±2}. It is exact on all 104² pairs and has cst 56.

## 2. Center geometry: the cut is not common

Term k is d_k = ⟨r, a_k⟩, t_k ∝ ⟨r, b_k⟩ with ⟨a_k, b_k⟩ = ±1 and both lines deleted.

- Center k gathers the sources N(b_k), whose labels span exactly u_{b_k}^⊥.
- Its readers are N(a_k), whose labels span exactly u_{a_k}^⊥.
- u_{a_k} ∈ u_{b_k}^⊥, because ⟨a_k, b_k⟩ is odd.

Theorem C's survivor is therefore u_b^⊥ ∩ (u_a^⊥)^⊥ = ⟨u_a⟩. A copy tree of cost 7 drops u_b^⊥ → ⟨u_a⟩
(d = 8 + 1 − 2 = 7), and every reader meets the center at a frame that contains u_a. In the coordinate
decoder the survivor is u_f^⊥ ∩ ⟨u_f⟩ = 0 (u_f·u_f = 1), and all 112 targets read their 4 centers at frame 0.

With one barrier cut (the shipped center semantics, #717 S4), target t must contain u_{a_k} for every mixed
center it reads. The 104 targets read 2, 3, 4, 5 or 6 centers (12, 24, 32, 24, 12 targets). Their required
cut frames have exactly that dimension, because the u_{a_k} a target reads are independent.

## 3. Delivery lower bounds

**Copy-chain model.** After its single drop to ⟨u_a⟩, center k's content reaches readers through copies.
A copy that is never dropped again (any further drop would add copy rank, by Theorem C) can only climb, so
one copy serves a chain of nested reader frames. Readers at equal frames share a copy. The minimum number
of copies for center k is therefore the minimum chain cover of its readers' frames (Dilworth). The center
itself can serve one chain.

- **Single cut.** For every center: 52 readers, 52 distinct frames, 1059 incomparable pairs, and minimum
  chain cover 19. In all, 152 chains, so **≥ 144 copies** beyond the 8 centers.
- **Staggered reads.** All targets read the centers in one global order, climbing by u_{a_k} just before
  each read. The reads of one center then form one phase, so chain order and read order never conflict.
  - The exhaustive search over all 8! = 40,320 orders gives totals {55: 11,520 orders, 56: 5760,
    57: 17,280, 58: 5760}.
  - The minimum, 55 chains (order 0,1,2,3,4,6,5,7), means **≥ 47 copies**.
  - Per-target orders, and schedules that do not keep one phase per center, are not searched.

These are lower bounds within the copy-chain model. They do not show that copies can be emitted with exact
values and restored. They also do not check frame legality against the side corrections, or hosting.

## 4. Price against #968's budget

#968's README (sha256-pinned) states two numbers:
- P104 raises b by 5.51% on T37;
- reaching the PR589 bit cap leaves about 1.33% of b.

#717 P3 prices a removed helper of width 4 / 5 / 7 / 8 / 9 at 0.026 / 0.031 / 0.038 / 0.051 / 0.070% b
without merge, and w9 merged at 0.140%. Copies restored like the shipped helpers have widths 8–9. All of
these figures are cited, not recomputed.

| delivery | copies ≥ | w8 | w9 | w9 merged | reaches bit cap |
|---|---|---|---|---|---|
| single cut | 144 | 7.34% | 10.08% | 20.16% | never (≥ 3.74% even at w4) |
| staggered, best global order | 47 | 2.40% | 3.29% | 6.58% | only at w4 (1.22%) |

Break-even against 5.51% is 108 copies at w8, 79 at w9 and 39 at w9 merged. The single cut is above all
three. Staggered delivery is below the first two and above the third.

The certified R-free format ceiling (#595, main's `skel.py`) is unit-level and unchanged by this
comparison: s = 9 gives 3.995e-3 for P112/64 and 4.412e-3 for P104/56 (+10.44%).

## 5. Independent re-derivation of #968's floor

The statements in this section are #968's theorem and family. They were re-derived here without reference to
#968, so they serve as corroboration. #968 also proves that the bounds are attained at every p ≤ 24; this
package checks attainment only at p ∈ {0, 8, 9, 16}.

**Lemma 1 (bi-frames).** If P spans Q⁸, an 8-term decoder with D Tᵀ = 2G_P has D = R_P V and T = R_P W with
V Wᵀ = 2I.

*Proof.* rank D Tᵀ = 8 forces col D = col G_P = col R_P. R_P has full column rank, so
R_P (V Wᵀ − 2I) R_Pᵀ = 0 gives V Wᵀ = 2I. ∎

Term k is supported on N(v_k) ∩ P and N(w_k) ∩ P, where N(x) = {r : ⟨r, x⟩ ≠ 0}. All 11 #717 D3 hit
files solve exactly to V Wᵀ = 2I.
- P104: 8 mixed root pairs, each β = 7.
- P111: one mixed root pair (β = 7) and seven terms of cost 8, so cst = 63 = 72 − 9.

**Lemma 2.** The pairing rank of W_R, W_A ⊆ F₂⁹ is ≥ dim W_R + dim W_A − 9.

**Lemma 3.** For roots a ≠ b, both deleted, β ≤ 8 − [⟨a, b⟩ odd]. A pure term (a = b) costs at most 8.

**Thresholds.** Every v ≠ 0 is W-conjugate to Σ_{i∈S} ω_i for a node set S, and labels are W-equivariant.
Over all 255 classes, using all 511 hyperplanes and all 43,435 codimension-2 subspaces of F₂⁹:

| support | lines | span on P120 | deletions for span ≤ 8 (cheapest / next) | for span ≤ 7 |
|---|---|---|---|---|
| root, N(a) (flat E7) | 57 | 9 | 1 (a itself) / 24 | 25 |
| flat D7 | 78 | 9 | 14 / 34 | 42 |
| the other 253 classes | 83–120 | 9 | ≥ 26 | ≥ 51 |

The D7 set is {r : |⟨r, w⟩| = 2}. In the full D7 orbit (1080 directions), any two distinct directions need
≥ 21 deletions together. Both thresholds are attained by explicit sets.

**Theorem (#968).** For 8-term decoders exact on all pairs of P120 − Π:

- cst ≥ 56 when |Π| ≤ 24, because every side spans ≥ 8;
- cst ≥ 72 − |Π| when |Π| ≤ 15.

*Proof of the second bound.*
- **Case A (no D7 side).** A side spans 8 only if it is a root whose line is deleted, and the roots are
  pairwise distinct by biorthogonality. So cst ≥ 8p + 7m + 8q + 9(8 − p − m − q) ≥ 72 − |Π|.
- **Case B (a D7 side w_l ∥ w with O(w) ⊆ Π).** The root sides v_k (k ≠ l) avoid O(w), so at most one of
  them is cheap. Then cst ≥ 6·8 + 2·7 = 62. ∎

Together: cst ≥ max(v − 48, 56) for v ≥ 96. Equality holds at v = 120, 112, 111 and 104.

**Census and a characterization (new).** The 2025 orthogonal frames form one W(E8)-orbit (checked), and
1260 of them are disjoint from F0. Root bi-frames on F0 ∪ C fall into three classes:

| second frames C | root bi-frames | fully mixed | best cst |
|---|---|---|---|
| 896 | 10 | 8 | 56 |
| 336 | 2 | 0 | 64 |
| 28 | 4 | 0 | 64 |

Every fully mixed bi-frame takes 4 a's and 4 b's from F0 and has |det(a)| = 1 (all 7168). Pure frames
have index 16.

In general, a root bi-frame with every ⟨a_k, b_k⟩ = ±1 is exactly a unimodular root basis whose dual basis
consists of roots. To see this, let M = Z{a_k}. Then M* = Z{b_k} ⊆ E8 = E8* ⊆ M*, so M = E8.

## Scope and open obligations

- **Covered:** decoders exact on all pairs, in the #717/#595 label model with #446 Theorem C as a premise.
  The delivery bounds are for one explicit P104 decoder and the copy-chain model, under either a single cut
  or staggered phases.
- **Not covered:**
  - other P104 decoders (896 frame classes × 8 mixed bi-frames; the bounds are computed for one of them);
  - per-target schedules;
  - copies that are dropped again (each such drop adds copy rank);
  - E-graph-only exactness;
  - n ≥ 9 terms;
  - |Π| ≥ 25;
  - the bit side.
- **Open:** an exact, restored, frame-legal staggered delivery layer and a 104-port complex skeleton. The
  helper prices are #717's, measured at #649; they are not re-derived on T37.
- All inherited all-size, realization, hosting, precision/tape and analytic assumptions remain. Finite
  exact checks are not a formal proof of the multiplication theorem. Main's selected κ
  (0.001661960547713947 at submission) is unchanged.

## Files and provenance

- `verify.py`: standard library only. It imports main's `research/format-limits-corrected/scripts/{cert,skel}.py`
  (sha256-pinned) for the ceiling, and reads #968's README (sha256-pinned) for the cited budget. It writes or
  compares `RESULTS.json` and runs 7 negative and 2 sharpness controls:
  - a corrupted hit coefficient;
  - swapped decoder columns;
  - an un-punctured root (its term rises to 8);
  - pure terms (8, not 7);
  - a flipped label bit;
  - tampered vendored bytes;
  - a 336-class frame with no mixed bi-frame;
  - the 25- and 14-deletion thresholds attained;
  - also the coordinate-decoder equalities 64 and 72.
- `inputs/pr717-hits/`: byte copies of #717's 11 D3 hit files at head `67e9e846` (identical at
  `07f4671a`), pinned by git blob id and sha256 in `SOURCES.json`.
- `RESULTS.json`: the receipt. `CLAIM.md`: the local sprint claim. `NOTICE.md`: credits.

Developed on `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Rebased without conflicts onto main
`2921874911956718fcaaaf9396fe8267b3cfa9f0`; the package shares no files with main.
