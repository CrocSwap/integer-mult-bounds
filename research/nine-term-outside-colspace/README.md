# Decoder floors, case (b): nine terms outside col M (P112 ≥ 64, #968 P104 ≥ 56; no κ claim)

**Status: research note with an exact finite enumeration (not a SAT/DRAT proof). No κ claim, no supplier word.** Only
`research/nine-term-outside-colspace/` is added. It closes one named residue of #2338's open item "factors outside `col M`, `m ≥ 9`"
(the sub-case that #1224 calls the one-sided nine-term decoder) and nothing else.

## Claims box (scope is part of the claim)

Setting (the model of #2338 / #2277 / #1224): a unit of lines `V` (`P112` = E8 minus the frame `F0`, 112 lines; `P104` = E8 minus `F0 ∪ F1`, 104 lines, #968's unit),
a **dense** pairing table `B` (the rank-9 label table; by Theorem R of #2338 every fitting `B` of F2-rank ≤ 9 is this one), and an **exact masked decoder**
`N = Σ_{j ≤ m} p_j q_jᵀ`: `N` has the P112 / P104 zero pattern (zero on orthogonal pairs, nonzero diagonal, free elsewhere), `p_j, q_j` arbitrary vectors over a field of characteristic 0,
cost `Σ_j rank_F2 B[R_j, A_j]` (`R_j`, `A_j` the row and column supports).

| # | Statement | Scope | Status |
|---|---|---|---|
| C1 | **P112: cost ≥ 64** | `m = 9`; `N` has rank 8 (a **rank-8 realisation** of the pattern); **exactly one** of the two factors has a column outside `col M` (= "case (b)", `s + t = 1`); dense `B`, hence every fitting `B` of rank ≤ 9 | PROVEN from CHECKED (exact class-level enumeration) |
| C2 | **P104: cost ≥ 56** | same scope on P104 | PROVEN from CHECKED (same method, 701 configurations) |

Realisation-free: the argument uses only the propagation lemma (Lemma 1.1 of #2338's card, valid in *every* rank-8 realisation of the pattern) and the reductions below; no Gram-level
step, so the rigidity results (#1212, #1815) are **not** needed.

**Scope note.** `P104` throughout is #968's unit (`F1 = H4`) only. The result relies on #2338 (Theorem P, Theorem R, and "≤ 8 paid terms ⇒ ≥ 64 / ≥ 56"), our own open PR.

**Not covered (stated up front):**
* **Case (c): a square decoder of a RANK-9 realisation.** This contains **every nine-term masked co-star decoder** (philippeVV, Discussion 1267: #2338 shows every such decoder is case (c)).
  This package does **not** touch the co-star programme; D1267's `k = 7, 8, 9` families remain exactly as open as before. It also does not cover the "A2 family" of rank-9
  iff-pattern realisations (the author's working analysis, unpublished).
* `m ≥ 10` (any realisation); two-sided decoders with `ρ = 9` or `m ≥ 10`.
* Any `B` of rank ≥ 10; other punctured units; Theorem R and Theorem P for P104 beyond what #2338 states.
* Not a DRAT / SAT result. The enumeration is exact Python on finite data (E8 geometry, 511 label classes), re-runnable, but not proof-logged.

## 1. Where this sits

* #2338 (open): Theorem P (P112 ≥ 64 for every rank-8 realisation with factors in `col M`), `≤ 8` paid terms with factors anywhere ⇒ ≥ 64, and the `m = 9` trichotomy
  (a) `ρ = 8`, factors in `col M`: Theorem P; (b) `ρ = 8`, one outside factor; (c) `ρ = 9`. (b), (c) and `m ≥ 10` were listed OPEN. **This package closes (b) at `m = 9`.**
* #1224 (merged): one-sided nine-term decoders are overcomplete representations (normal form, Lemma D merge, ratio classes). #1180 (merged): the example with `s + t = 1` costs 65 and is a split of a
  proportional pair (#2338 / #2639). #1633 (merged): the excess budget `s + t ≤ m − 8`. #1213 (merged): one coordinate component. #2277 / #2639 (open, ours): the floors this extends.
* #1212, #1815: rigidity of the rank-8 realisation; **not used here**.

## 2. Inputs, cited and not re-derived (labelled INPUT)

* **INPUT-1 (Lemma 1.1, support propagation: the lemma behind #2338's Theorem P; working card IDEAL3 §1.1).** For a label class `O` (more generally any line set `X`), `lb(X) := 8 − min_E |S_E(X)|` after iterating
  `S_E ← (E∖X) ∩ ⋂_F ⋃_{g ∈ F∖X} N̄(g)` over the 8-frames is a lower bound for `rank p₀(X)` in **every** rank-8 realisation. P112 has 1260 frames, P104 759.
  *Proof (3 lines).* For a frame `E` write a killing functional `h* = Σ_{e∈E} c_e q₀(e)`; `h*(p₀(e)) = c_e M_ee` and `M_ee ≠ 0`, so `c_e = 0` on `E ∩ X`; for another frame `F`, `h* ∈ span q₀(F∖X)` and
  `q₀(g) = Σ_e (M_eg/M_ee) q₀(e)` has `E`-support in `N̄(g) ∩ E`, which gives the stated update; iterating is sound.
  *Recomputed here:* `checks/inputs_check.py` (frames, classes, the 8 / 16 uncertified "survivor" classes, each of 56 / 52 lines, being exactly the live lines orthogonal to one removed root).
* **Exact rank formula (PROVEN; IDEAL Thm 3 / BIGTHEORY Thm A of the working cards; proof inlined).** Dense `B[t,s] = Ω(u(t),u(s))` with `u(t) ∈ F₂⁹` the label of line `t` and `Ω` nondegenerate on `F₂⁹`
  (`h = 9` and 511 classes, checked by `inputs_check.py`). For supports `R, A` with label spans `U_R, U_A`, `B[R,A]` has the rank of `Ω` restricted to `U_R × U_A`, i.e. `rank B[R,A] = dim U_R − dim(U_R ∩ U_A^{⊥Ω})`.
  Identify `F₂⁹` with its dual via `Ω`; the avoided classes of a support are `Z_R = U_R^⊥` (so `U_R = Z_j^⊥`, `d_j = 9 − dim U_R`), and if `δ_A = dim Z_A = 1`, `Z_A = ⟨z_A⟩` and `U_A^{⊥Ω} = ⟨z_A⟩`.
  Hence for `δ_A(j) ≤ 1`: `r_j = 9 − d_j − τ_j`, `τ_j = [δ_A(j) = 1 and z_A(j) ∈ U_R]`, i.e. `Ω(z_A(j), Z_j) = 0`; and `τ_j = 0` if `δ_A = 0`. Spot check on random blocks: `checks/rank_formula_check.py`
  (2,974 P112 + 2,973 P104 random blocks, 0 mismatches; also `ctlb.py` below).
* **INPUT-3 (survivor facts; recomputed by `inputs_check.py`).** Survivor pairs have `rank_F2 B[V∖O_z, V∖O_z′] = 8` (P112) / ∈ {7, 8} (P104); every survivor class has an orthogonal 7-clique and no 8-frame;
  no plane of the label space contains three survivors.
* **INPUT-4 (Theorem R of #2338):** every fitting `B` of F2-rank ≤ 9 on E8, P112, P104 is the dense one (this is what gives "rank ≤ 9 `B`" from "dense `B`").
* **Reductions (PROVEN, short; #2338 card STRAYS-MASK §1).**
  *Free terms absorbed:* under dense `B` a term with `B[R_j,A_j] = 0` has all its entries on pairs with `B = 0` (off-diagonal, non-orthogonal), so deleting it leaves a decoder with the same values on the diagonal and on orthogonal pairs and the same cost; WLOG every term is paid (`r_j ≥ 1`),
  which gives `σ_j ≤ 7` (P112) and `σ′_j ≤ 6` (P104): the caps `min(7,·)` in `cnt7/cnt8/cnt9` and `min(6,·)` in `cnt9b`, and the skip of `τ₀ = 1` for `d₀ = 8` in `cnt7.py:31` (there `d₀ − 1 + τ₀ = 8` exceeds the cap, so `τ₀ = 1` adds nothing).
  *Lemma D (merge, #1224):* if `q_i = c·q_k` then `p_i q_iᵀ + p_k q_kᵀ = (c p_i + p_k) q_kᵀ`, with row support in `R_i ∪ R_k`, column support `A_k = A_i`, and `rank B[R_i ∪ R_k, A_k] ≤ rank B[R_i,A_k] + rank B[R_k,A_k]`; so the cost does not rise (same for rows). WLOG no two normals on a side are proportional; this gives "distinct terms with `τ = 1` use distinct survivors" below.
  `m ≤ 8` is the square case (Theorem P of #2338); for `m = 9`, Sylvester gives `ρ ∈ {8, 9}` and `s + t ≤ 9 − ρ`.

## 3. The argument

**3.1 Normal form (PROVEN, #1224 Thm A / Cor C re-derived).** Case (b), `t = 0`: `Q = Q₀Ȳ` with `Ȳ ∈ K^{8×9}` of rank 8, `z` spans `ker Ȳ`, and `P = P₀X̄ + κ zᵀ`, `X̄Ȳᵀ = I₈`, `κ ∈ K^V` a free "lift".
`S = supp z` are the *masked* terms (`|S| ≥ 3`); the others are *inside* (`p_j = P₀x̄_j`). Each line is dead (`P[t,j] = 0`) for at most one ratio class of masked terms.

**3.2 Lemma 2.1: the lift is free (PROVEN; = Theorem OS row-independence, #2338 card MASK3).** For any `κ′`, `P′ = P₀X̄ + κ′zᵀ` gives `P′Qᵀ = P₀X̄ȲᵀQ₀ᵀ + κ′(Ȳz)ᵀQ₀ᵀ = N`.
Setting `κ′(t) = −p₀(t)·a_j` (`a_j := x̄_j / z_j`) at a line live for every masked term only shrinks supports, so the cost does not rise. WLOG every line is row-dead for at least one masked term;
if the result has rank `P′ = 8` it is case (a) (Theorem P), if a term vanishes it is an `≤ 8`-term decoder, hence square, and #2338 Theorem P gives ≥ 64 (P112) resp. ≥ 56 (P104).

**3.3 Accounting (PROVEN from the rank formula, INPUT-1, 3).** `σ_j := 8 − r_j = d_j − 1 + τ_j` (P112); cost ≤ 63 ⟺ `Σσ_j ≥ 9`. Inside terms and terms whose row-dead classes are survivors have `σ ≤ 0`.
`δ_A(j) ≤ 1`, and `δ_A = 1` only at a survivor: columns are inside (`t = 0`), so a deficient column class has `q₀`-rank ≤ 7; by Lemma 1.1 applied to `Nᵀ` (symmetric pattern) it is a survivor, survivors contain no plane (INPUT-3), and the 7-clique inside a survivor gives rank exactly 7, hence a column functional unique up to scale.
`τ_j = 1` needs `δ_A(j) = 1` at a survivor and distinct terms use distinct survivors (two such terms would have proportional column normals and merge, Lemma D). For every set `J` of terms the
common row-dead set `M_J` has `rank p₀(M_J) ≤ 9 − |J|`: in case (b) `rank P = 9` (else case (a)) and `P = [P₀ | κ]·X̂` with `X̂ = [X̄; zᵀ]` invertible, so `P[t,j] = w(t)·X̂_j` for `w(t) = (p₀(t), κ(t))`; for `t ∈ M_J` the vector `w(t)` is annihilated by the `|J|` independent columns `X̂_j`, `j ∈ J`, so it lies in a subspace of dimension `9 − |J|` and `rank p₀(M_J) ≤ rank w(M_J) ≤ 9 − |J|`. This holds for any `J`, so no condition `J ∩ S ≠ ∅` is needed. Moreover and by INPUT-1 `rank p₀(X) ≥ lb(X)`; `M_J ⊇ ⋂_{j ∈ J} C(Z_j)`, `C(Z) = ⋃_{c ∈ Z∖0} O_c`.
A term is *big* if `d ≥ 2`, *small* if `d = 1` at a non-survivor class with `τ = 1` (`σ = 1`), *extra* otherwise (`σ ∈ {−1, 0}`). Any 2-dim label subspace contains a non-survivor class, so big terms are masked.
P104 (INPUT-3, STRAYS-MASK §4.6): `σ′ = 7 − r = d − 2 + τ`, cost ≤ 55 ⟺ `Σσ′ ≥ 8`; terms with `d ≤ 1` have `σ′ ≤ 0`, so at least two bigs are needed.

**3.4 P112 census (CHECKED, exact enumeration over the 511 label classes).**

| Case | Result | Script(s) | Status |
|---|---|---|---|
| no big term | `Σσ ≤ 8 < 9` | (counting, §3.3) | PROVEN |
| ≥ 2 big terms | 71 Aut-orbit reps of 2-dim label subspaces `R` against all 43,180 planes `W`: `lb(C(R) ∩ C(W)) = 8` except 41 (rep, plane) pairs (10 orbits); every multi-big configuration (cliques of compatible planes, all superspace extensions keeping the J-conditions, all τ-patterns), then small sets, extras and the support filter: 41 configurations → **0** | `cnt.py`, `cnt9.py` | CHECKED (not independently re-implemented) |
| one big, `d₀ = 2` | max `k` of small terms over plane reps ≤ 7; residue 8 configurations → support filter **0** | `cnt4.py 2`, `cnt7.py`, `cnt8.py` | CHECKED (not independently re-implemented) |
| one big, `d₀ = 3` | 3-dim reps: max `k` ≤ 6; residue 1 → **0** | same | CHECKED (not independently re-implemented) |
| one big, `d₀ = 4` | `cnt6.py`: 2,786 four-dim extensions, 417 admit `k ≥ 5`; residue 17 → **0** | `cnt6.py 4`, `cnt7`, `cnt8` | CHECKED (not independently re-implemented) |
| one big, `d₀ = 5` | 2,035 subspaces admit `k ≥ 4`; residue **0** (plain count: no survivor `s₀` with the τ₀-rank condition, so `τ₀ = 0`, and max valid `k` is 4 < 5) | `cnt6.py 5`, `cnt7` | CHECKED **and CHECKED-INDEPENDENTLY** (`evidence/helper/`) |
| one big, `d₀ = 6` | 3,498 subspaces; residue **0** (same reason; max valid `k` 3 < 4) | `cnt6.py 6`, `cnt7` | CHECKED **and CHECKED-INDEPENDENTLY** |
| one big, `d₀ = 7, 8` | `Z₀` is the annihilator of the labels of term 0's live lines (1–2 lines), enumerated exactly (6 resp. 1 orbit cases); residue **0** | `cnt10.py`, `cnt7` | CHECKED (not independently re-implemented) |

Support filter (`cnt8.py`): for each residue, every survivor assignment, every choice of extra classes / τ-extras, live sets taken maximal; (D) every line live on both sides for some term;
(C) every orthogonal 7-/8-clique `C` has ≥ `|C|` terms live on `C` on both sides. All tests are necessary conditions (sound). Hence **P112 case (b) costs ≥ 64.**

**3.5 P104 (CHECKED).** `aut104.py` builds the stabiliser of `F1` inside the reflection-pair group fixing `F0` (191 Schreier generators on the live lines, each checked to be an isometry fixing `F0`, `F1`; 39 class orbits, 732 plane orbits);
`cnt104b.py` (frame-containment prefilter + propagation): 413 compatible (rep, plane) pairs, no plane has 3 survivors; `cnt9b.py`: every multi-big configuration whose bigs reach `Σ min(6, d − 2 + τ) ≥ 8`,
then the support filter with all other terms fully live (a relaxation): **701 configurations, 0 survive.** Hence **P104 case (b) costs ≥ 56.** (CHECKED; not independently re-implemented.)

**3.6 Controls.** `ctl8.py`: the removed-frame coordinate decoder plus an empty ninth term passes the support filter, dropping a term fails (C), the clique condition (the filter is not vacuous).
`ctlb.py`: six random genuine case-(b) decoders (Gram realisation, random invertible `X̂`, random lift killing a random masked term per line): exact (`PQᵀ` = Gram), `r_j ≥ 9 − d_j − δ_A`, `δ_A ≤ 1` only at survivors,
and `lb(M_J) ≤ rank p₀(M_J) ≤ 9 − |J|` on random `J`: 294 checks, 0 violations (rank-formula and INPUT-3 consequences exercised on real decoders).

**3.7 Audit history (honest).** A separate reviewer run (Claude Sonnet, read-only plus re-run of `cnt7` / `cnt8` for `d₀ = 2, 3`) found no logical gap and **one incompleteness**: the extras search forbade repeated classes.
It was fixed in `cnt7/8/9` (repeats allowed) and **everything was re-run**; the final numbers above are the post-fix ones (residues unchanged). `R == W` in `cnt9` is skipped soundly (a plane holds a non-survivor, so `lb(C(R)) = 8`).
The `τ` test `rank == 8 − D` on the maximal live block is exact because `r = 9 − d − τ` depends only on label spans.
**Independent re-implementation** (`evidence/helper/`, own `lb` propagation, own matching / J-condition DFS, own orbit reduction, same geometric inputs): agrees **exactly** for `d₀ = 5` (3-dim reps 104 → dim 4: 5,723 → 2,468 → dim 5: 34,741 → 2,035)
and `d₀ = 6` (170 → 9,397 → 7,016 → 72,159 → 21,982 → 71,191 candidates → 3,498), residue 0 in both. **NOT independently re-implemented:** `d₀ = 2, 3, 4, 7, 8`, the ≥ 2-big census, and all of P104.

## 4. What `verify.sh` does, and what it does not

The full pipeline is long (P112 `cnt.py` census 44 min, P104 `cnt104b.py` 32 min, `cnt7` for `d₀ = 5` ~17 min, `d₀ = 6` ~28 min (timings from the recorded logs, machine under load), plus `cnt6` and `cnt9`; several single-core hours in total), so it is **not** re-run by default.

| mode | what runs | time (single core) |
|---|---|---|
| default (`bash verify.sh [OUTDIR]`) | step 0 manifest; `inputs_check.py` (INPUT-1/3 on both units); `rank_formula_check.py` (exact-rank formula spot check); regeneration of the geometric data (orbits, cliques, pair census via `pairs_fast.py`, `aut104.py`); `ctl8.py`, `ctlb.py`; **exact replays** of `cnt4` (`d₀ = 2, 3`), `cnt7`/`cnt8` for `d₀ = 2, 3, 7, 8` (+ `cnt10`), compared line-for-line with the recorded logs; **subset replays** of the census (`cnt.py` orbits 8, 13; `cnt104b.py` selected orbits), compared with the recorded logs; `cnt9` and `cnt9b` replayed from the recorded compact output of the census (`data/lb22_le7_*.json`, entries with `lb ≤ 7`) | ~10-15 min on one core (the PR body states the measured transcript) |
| `FULL=1 bash verify.sh` | additionally the whole chain from scratch (`cnt.py`, `cnt104b.py`, `cnt4 3`, `cnt6 4/5/6`, `cnt7/8` for `d₀ = 4, 5, 6`) | hours; **not run for the transcript** |

**Recorded, not re-run by default (RECORDED):** the full census logs (`evidence/logs/cnt_P112.log.txt`, `cnt_P104.log.txt`), `d₀ = 4, 5, 6` (`cnt6/7/8_P112_{4,5,6}.log.txt`), the `cnt9` / `cnt9b` logs; they are shipped with sha256 in `MANIFEST.sha256`.
The compact census output `data/lb22_le7_*.json` is a recording of the working-card pickles (entries with `lb ≤ 7`); its trustworthiness rests on the census logs and the subset replays, not on a full re-run.
`evidence/helper/` (independent re-implementation, logs, sources) is shipped as exported (only the absolute working-card paths stripped from `ind.py`, `ind2.py`, `probe.py`); its scripts need the working-card pickles and are **not** run by `verify.sh`.
Requirements: Python ≥ 3.11 (3.14 used), `numpy`, `networkx`; `requirements.txt`. No SAT solver, no kissat, no drat-trim.

## 5. Files

* `checks/` — the scripts (geometry modules `lib.py, lib2.py, common2.py, frames.py, cert2.py, setup9.py` are copies of the author's #2338 / #2277 library files; counting scripts `cnt*.py`, `m9lib.py`, `aut104.py`, `ctl8.py`, `ctlb.py` copied from the working card MASK9 with only absolute paths removed,
  `frames_data.py` + `data/p104_frames.json` replacing a pickle, `ONLY_ORBITS` env hook in `cnt.py` / `cnt104b.py`; new: `inputs_check.py`, `rank_formula_check.py`, `pairs_fast.py`, `mk_cnt_pkl.py`, `cmp_logs.py`).
* `evidence/logs/` — recorded run logs of the working card (Oct 15, 2026); `evidence/helper/` — independent re-implementation. `SOURCES.json` — hashes of the working-card texts quoted.

## 6. Open (listed, none claimed)

1. **Case (c)**: square decoders of rank-9 realisations, including all nine-term masked co-star decoders (D1267) and the A2 family. This package does not bear on them (co-star = case (c) by #2338).
2. `m ≥ 10`, one-sided (the sparse-representation residue of Theorem OS) and two-sided.
3. Independent re-implementation of `d₀ = 2, 3, 4, 7, 8`, the ≥ 2-big census and P104.
4. Any `B` of rank ≥ 10; the other P104 units.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
