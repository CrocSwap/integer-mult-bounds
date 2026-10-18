# Decoder floors: every label window h ≥ 12 is closed in the root-code scope (clique bound + DRAT-verified h = 12–14; no κ claim)

> **Scope, stated first.** A closures-only follow-up of #2639 (*Decoder floors, closures*: windows `h = 10, 11`, ready) and of #2338 (open; the parent). It contains **no κ claim**, no window, no supplier and no word-side cost. It closes the row "windows `h ≥ 12`" of #2639 §4 *within the root-code scope of #2639 §3* and under the inherited pricing model (both stated in §0). Each statement carries one of **PROVEN** (proof in this README), **CHECKED** (recomputed by `verify.sh` here), **RECORDED** (inherited from a working card or an earlier PR and not re-derived here) or **CONDITIONAL** (a PROVEN/CHECKED argument whose last step uses a RECORDED input, named). #2639 is not needed to run `verify.sh`.
>
> **Credit and prior work, stated first.** Model, notation, Lemmas S and M, the second gauge, the SAT encoder (`sat/hk3.py`, shared with #2639, §5) and the pricing model are #2639's / #2338's (author's own); the rank-8 rigidity used in §7 is **#1212** (burntout76); the pricing code imported in `lib/pricing.py` is Douglas R. Colkitt's (`research/format-limits-corrected`, `research/complex-local-word-ceiling`). See `NOTICE.md`.
>
> **Snapshot:** Oct 16 2026, base `origin/main` d311a18c6. The working cards (`WIN12`, `WIN12X`, `H11`) are live files; `SOURCES.json` pins the sha256 of the card texts read.

## 0. Model, scope, labels

Notation as #2639 §0/§3. `P112 = E8 − F0` (112 root lines); `B ∈ F2^{112×112}` is a **fitting** pairing: `B_tt = 1` and `B_ts = 0` for `t ≠ s` **non-orthogonal** (odd true inner product); `B_ts` is free on orthogonal pairs. A *root-code* decoder (#2639 §3: Gram realisation `M = D₁ G D₂`, factors `p_j = D₁ R x_j`, `q_j = D₂ R y_j` in `col M`) with `m` nonzero terms has **cost** `Σ_j rank_{F2} B[R(x_j), A(y_j)]`, `R(x) = {t : r_t · x ≠ 0}` (the lines *not* orthogonal to `x`), `A(y)` likewise, and a *label window of width `h`* is a fitting `B` of `F2`-rank `≤ h`. Since `rank M = 8`, `m ≥ 8`. A *section* `H(x) = P112 ∖ R(x)` for a maximal-flat normal `x` is a **maximal section**; there are 440,880 of them, in 47 orbits under `Aut` (order 172,032).

**The pricing model (RECORDED, inherited).** A decoder of total cost `c` at width `h` *pays* iff `X(112,c,h) ≥ X(112,64,9)` and `roof(112,c,h) ≥ roof(112,64,9)` (the dense unit: cost 64, `h = 9`); `be(h)` is the largest paying cost. The model (a format-limit skeleton `X` plus a reverse-engineered roof profile; `STRAYS/PRICE-P112-H10`) is **reproduced here, not derived or audited**; `c5` recomputes its numbers with the sibling-directory code pinned in `SOURCES.json`. A window is **closed** when every decoder costs at least `be(h) + 1`. Every "closed" below is therefore **CONDITIONAL** on this model and on the cost model above; the per-term rank bounds do not use it.

## 1. Master table

| # | statement | status | where |
|---|---|---|---|
| W1 | Lemma C: `rank B[R,A] ≥ ω(R ∩ A)` (clique of the non-orthogonality graph) for every fitting `B`, any `h`, any gauge, any factorisation | **PROVEN** | §2 |
| W2 | census: `min ω(R ∩ A) = 5` over all `47 × 440,880 = 20,721,360` pairs; `ω ≥ 7` except 144 pairs (3 with `ω = 5`, 141 with `ω = 6`) in 6 orbits | **CHECKED** (2 independent C++ implementations, networkx, pynauty) | §3 |
| W3 | break-even `be(h)` = 55 51 46 42 38 33 29 25 for `h = 11..18` | **RECORDED** (inherited model); arithmetic **CHECKED** | §4 |
| W4 | `h ≥ 15`: every term `≥ 5`, cost `≥ 40 > be(h)`; `X(112,40,h)/base` strictly decreasing for `h = 15..200` | **CONDITIONAL** (W1, W2 + model) | §4, §6 |
| W5 | `h = 12, 13, 14`: 61 orbit queries UNSAT, all DRAT VERIFIED; terms `≥ 7 / 6 / 6`, cost `≥ 56 > 51`, `48 > 46`, `48 > 42` | **CHECKED** (rank bounds); closure **CONDITIONAL** | §5, §6 |
| W6 | the 696 queries `T(12, l+k = 7)` that #2639 lists as not run: 696/696 UNSAT, DRAT VERIFIED | **CHECKED** | §5 |
| W7 | **Theorem W:** every label window `h ≥ 12` is closed in the root-code scope, for any number of terms `m ≥ 8` | **CONDITIONAL** (W1–W5 + model) | §6 |
| W8 | the scope covers every rank-8 realisation of the P112 pattern (not only the Gram one), by #1212 Theorem 1 | **RECORDED** (#1212, merged); precise statement and its limit | §7 |

## 2. Lemma C (PROVEN)

**Conventions** (read off `sat/hk3.py`, the definition used by every query): a fitting `B` has `B_tt = 1`, and `B_ts = B_st = 0` whenever `t ≠ s` are non-orthogonal (the relation is symmetric; `hk3.py` imposes both orders). Rows of a term block are indexed by `R = R(x)`, columns by `A = A(y)`; `hk3.py` builds `B[R,A] = U[R] V[A]ᵀ`.

**Lemma C.** If `S ⊆ R ∩ A` is a set of pairwise non-orthogonal lines, then `rank B[R,A] ≥ |S|`, for every fitting `B` (any `h`, any factorisation `B = UVᵀ`, any gauge, any field).

*Proof.* Rows `S ⊆ R` and columns `S ⊆ A` give an `|S| × |S|` submatrix of `B[R,A]`. Its `(t,s)` entry is `B_ts`: `1` for `t = s`, and `0` for `t ≠ s` because `t, s` are non-orthogonal. It is the identity, so the rank of `B[R,A]` is at least `|S|`. Both inclusions are needed (rows from `R`, columns from `A`); the census uses `R ∩ A`, which gives both. ∎

**Reduction (inherited, PROVEN in #2639 §3 / STRAYS-H10).** `ω(R ∩ A)` is monotone in `R` and `A`, and by Lemma M every `x ≠ 0` has a maximal-flat normal `x′` with `R(x′) ⊆ R(x)`; hence `rank B[R(x),A(y)] ≥ rank B[R(x′),A(y′)] ≥ ω(R(x′) ∩ A(y′)) ≥ min over maximal sections`. `Aut` (order 172,032) preserves the section family (`c3.a`) and acts on pairs of sections, so it suffices to take `R` over the 47 orbit representatives and `A` over all 440,880 sections.

`c1` exercises the lemma on every exceptional pair (§3): it recomputes `ω` by a third, pure-Python exact clique search, checks that a maximum clique lies in `R ∩ A` with identity pattern, and that 40 random fitting matrices per pair have `rank_{F2} B[R,A] ≥ ω`.

## 3. The census (CHECKED)

For each of the 47 representatives `r` (as `R = P112 ∖ H_r`) and each of the 440,880 sections `A`, `ω(R ∩ A)` in the non-orthogonality graph of P112 (52-regular, 112 vertices).

* `census/cen.cpp` (decision DFS for a 7-clique, exact `ω` only below 7) and `census/mc.cpp` (exact maximum clique, greedy-colouring branch and bound) are two separately written programs; both read data rebuilt by `lib/common.py` from `lib/e8.py` and the shipped normals (`data/normals_x840.npy.xz`; asserts: 440,880 distinct sections, every 88th normal has a rank-7 root section, the 47 representatives of `data/hyp_reps.json` are exactly sections, non-orthogonal degree 52 everywhere).
* **Result:** `20,721,216` pairs have `ω ≥ 7`; **144** have `ω ≤ 6`: 3 with `ω = 5` (representative 43, `|H| = 59`), 141 with `ω = 6` (representative 43: 66, representative 45: 12, representative 46 = `f^⊥`: 63). **`min ω = 5`.** `cen.cpp` runs in full inside `verify.sh` in seconds; `mc.cpp` (the recorded full run took about 25 min) runs on representatives 43–46 plus a stride sample by default and on all pairs under `FULL=1`. `data/exceptional_pairs.json` is the 144-pair list; `c2` requires the fresh `cen.cpp` list to equal it and the recorded `evidence/cen_full.out.txt`, and the fresh `mc.cpp` histograms to equal `evidence/mc.out.txt`.
* `c4`: networkx `find_cliques` gives the recorded `ω` on all 144 pairs and `ω ≥ 7` on 940 random non-exceptional pairs (20 per representative; 400 under `FULL`).
* `c3` (pynauty): `|Aut| = 172,032`, all 13 generators map the section family to itself; the 144 pairs form **exactly 6 orbits** under `Aut` and transposition (sizes 3, 7, 8, 18, 48, 60; one with `ω = 5`, five with `ω = 6`), and these are exactly the six pairs of `data/pairsX.json` that §5 queries (pair 4 is the `ω = 5` orbit). Under `FULL=1`, `c3.c` also shows that the 47 representatives have 47 distinct certificates and that all 440,880 sections have the certificate of a representative.

## 4. Break-even and the arithmetic (RECORDED model; arithmetic CHECKED)

`c5` (full scan from `c = 64` downwards, both conditions) reproduces `be(h)` for `h = 11..18`:

| h | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 |
|---|---|---|---|---|---|---|---|---|
| `be(h)` (RECORDED, inherited model) | 55 | 51 | 46 | 42 | 38 | 33 | 29 | 25 |
| per-term floor | 7 (#2639) | 7 | 6 | 6 | 5 | 5 | 5 | 5 |
| 8 terms ≥ | 56 | 56 | 48 | 48 | 40 | 40 | 40 | 40 |

and shows `X(112,40,h)/base < 1`, **strictly decreasing for every integer `h = 15..200`** (maximum `0.968` at `h = 15`, `0.123` at `h = 112`): computed to the end of the meaningful range (a fitting `B` has at most 112 columns), not extrapolated. `c5.d` shows `X(112,c,h)` strictly decreasing in `c` on `40..112` (a skeleton with `D ≤ 0` counts as not paying) on a grid of widths (all `h = 15..112` under `FULL=1`), so cost `≥ 40` never reaches the dense baseline for `h ≥ 15`. The model's `be(12) = 51` has a very thin `X` margin (0.04%) but no closure uses it (the floor there is 56).

## 5. SAT queries for `h = 12, 13, 14` and the 696 (CHECKED, DRAT VERIFIED)

**Query semantics (Lemma S, PROVEN in #2639 §3).** `T(h, l, k, H₁, H₂)` is SAT for some `l + k = h − c` iff some fitting `B` of rank `≤ h` has `rank B[R,A] ≤ c`. So UNSAT for all splits `l + k = h − c` means every fitting `B` of rank `≤ h` has `rank B[R,A] ≥ c + 1` on that pair. Pairs are taken up to simultaneous `Aut` and transposition (`Bᵀ` is fitting).

* **61 orbit queries** (`sat/jobs61.txt`): `h = 12`, `l + k = 6` on the six exceptional orbits × 7 splits (42) ⇒ rank `≥ 7`; `h = 13`, `l + k = 8` on the `ω = 5` orbit × 9 splits ⇒ rank `≥ 6`; `h = 14`, `l + k = 9` on the `ω = 5` orbit × 10 splits ⇒ rank `≥ 6`. **61/61 UNSAT, every proof DRAT VERIFIED** (kissat 4.0.4 `--no-binary`, drat-trim `-t 1200`).
* **696 queries `T(12, l + k = 7)`** on the 172 `f^⊥` pair orbits (`sat/jobs696.txt`; item (i) of the card H11 and the queries #2639 leaves as not run): **696/696 UNSAT, DRAT VERIFIED**; they give rank `≥ 6` at `h = 12` on those pairs. The job list of the card H11 has splits `l ≤ 3` for 170 of the 172 pairs and the full range `l = 0..7` for two; the card's own derivation of "rank `≥ 6` on every `f^⊥` pair" from this list also uses `G(12,4)` UNSAT on the 46 representatives other than `f^⊥` (H11, RECORDED, not re-run here). They are a **side result**: the statement "every pair has rank `≥ 6` at `h = 12`" follows from the census (`ω ≥ 7` off the six orbits) plus the 42 `h = 12` queries (rank `≥ 7` on the six orbits), independently of this list, and Theorem W does not use them.
* **Encoder.** `sat/hk3.py` is the encoder of #2639 (`evidence/h10/hk3.py`, sha256 `71aa9da7659e58acd74a642e65d74c762d3a23f97b28e7084eb54a81e53effa0`) with exactly two marked edits (the `sys.path` line now points to `lib/`; the pair files are JSON instead of pickle). Flags `RREF=1 ORTH=1` and `GAUGE = RA` (6 + 9 + 10 queries and 16 of the 696) or `GAUGE = A` (680 of the 696) are the symmetry reductions whose soundness is the card's PROVEN paragraph (#2639 §3.2; `RA` only chooses the gauge clique, and any non-orthogonal 8-clique is a valid gauge). On the two edits: the CNF produced for `T(12,2,4)`, pair 4, is byte-identical to the one from the unedited file.
* **Evidence handling.** `evidence/drat_61.log.txt` and `evidence/drat_696.log.txt` are this package's re-run (Oct 16): per query the CNF sha256, the kissat time and the drat-trim verdict; the CNFs and proofs are regenerated and deleted (the largest proof is about 1.6 GB, so DRAT files are not shipped). `evidence/oct15_*.log` are the working cards' first runs (no CNF hashes; the 696 log contains one query twice, pair 89 `l1 k6`: one chain logged `NOOUT` because the other chain removed its proof file; re-run alone and VERIFIED, `oct15_drat_rerun.log.txt`). `verify.sh` step 7 regenerates 14 queries and checks their CNF hash against the shipped record, then kissat and drat-trim; under `FULL=1` all 757. `c6` counts the logs.
* **What the SAT evidence is not.** One solver and one checker, and one encoding, shared with #2639; the encoding is validated by SAT controls (`evidence/oct15_controls_sat.log.txt`: `T(12, l+k = 3)` on pair 4, SAT 4/4) and by #2639's controls, not by a second encoding. The per-term rank bounds from `ω` (Lemma C) do not depend on it.

## 6. Theorem W (CONDITIONAL)

**Theorem W.** In the root-code scope, for any number of terms `m ≥ 8`, any fitting `B` of `F2`-rank `≤ h`: every nonzero term has rank `≥ 7` (`h = 12`), `≥ 6` (`h = 13, 14`), `≥ 5` (every `h`, by Lemma C and the census). Hence the cost is `≥ 56 > 51`, `48 > 46`, `48 > 42` for `h = 12, 13, 14`, and `≥ 40 > be(h)` for `15 ≤ h ≤ 18` (`be = 38, 33, 29, 25`); for `h ≥ 15` generally cost `≥ 40` does not pay because `X(112,c,h)/base < 1` for `c ≥ 40` (§4). **Every label window `h ≥ 12` is closed.**

*Proof.* Per-term floors: a term's block is `B[R(x),A(y)]`; by the reduction of §2 it is bounded below by the same quantity on a pair of maximal sections, i.e. by a pair in the census. Non-exceptional pairs have `ω ≥ 7`, so rank `≥ 7`. Exceptional pairs: `h = 12`: the 42 UNSAT queries on the six orbits give rank `≥ 7`; `h = 13`: the five `ω = 6` orbits have rank `≥ 6` by Lemma C and the `ω = 5` orbit has rank `≥ 6` by the 9 UNSAT queries; `h = 14`: the same with the 10 queries. Any `h`: `ω ≥ 5`. The cost is the sum over `m ≥ 8` terms; the arithmetic against `be(h)` and `X(112,c,h)` is §4. ∎

Labels: the per-term rank bounds are **PROVEN** (Lemma C + reduction) from **CHECKED** data (census, DRAT); the closure is **CONDITIONAL** on the **RECORDED** pricing model (§0) and on the root-code cost model.

## 7. Scope: rank-8 realisations (#1212)

#2639 §3 states its window theorems for the *root code* (Gram realisation). The card `H11` §3 (not #2639) records the non-Gram rank-8 realisations as open: only local rigidity of the Gram point was proved there. **#1212, Theorem 1** (merged; `research/complex-rank8-decoder-rigidity/PROOF.md` §7): on P112 every real matrix `K` of rank `≤ 8` with `K_ii = 4` and `K_ij = 0` on orthogonal pairs has rank exactly 8 and equals `D (2G) D⁻¹` for a diagonal `D` with nonzero diagonal; in particular no odd entry vanishes (it holds verbatim over `C`). Applied to `K = diag(4/M_tt) · M`, this is exactly the statement needed: **every realisation `M` of rank `≤ 8` of the P112 pattern (`M_tt ≠ 0`, `M_ts = 0` on orthogonal pairs, other entries free) has rank exactly 8 and is a diagonal rescaling `D₁ G D₂` of the Gram matrix, with exactly the Gram zero pattern**, so its supports are the Gram supports and §2–§6 apply to it. `verify.sh` step 8 checks that the text of Theorem 1 is present in the repository tree; it does not re-prove it.

**What this does not say.** Theorem 1 concerns realisations of rank `≤ 8`; realisations of rank `≥ 9` are not covered (#2639 §4 lists them as not claimed). It concerns the matrix `M` (the sum of the terms), not the individual factors. The scope of #2639 §3 also takes the term factors `p_j, q_j` of a decoder with `m > 8` terms to lie in `col M` (root-code factors); factors outside `col M` (the single-call floor, #2639 §4) are **not** covered here and remain open.

## 8. Not claimed

No κ, no supplier, no word-side cost; no statement about realisations of rank `≥ 9`; no statement about decoders whose factors lie outside `col M`; no change to the pricing model; no claim for punctured units or for `h ≤ 11` (see #2639). The pricing model is inherited; if it changes, only §4 and the final comparison of Theorem W change, not the per-term rank bounds.

## 9. Reproduction

`bash research/label-windows-h12-plus/verify.sh /fresh/output/dir` (run inside the repository tree: it needs the sibling directories `research/format-limits-corrected`, `research/complex-local-word-ceiling` (pricing model, pinned) and, for step 8, `research/complex-rank8-decoder-rigidity`; Python ≥ 3.11 with numpy; pynauty, networkx, a C++ compiler, kissat 4.0.4 and drat-trim are used when present, `SKIP` otherwise, never `PASS`). Step 0 `MANIFEST.sha256` + `SOURCES.json`; `c1` Lemma on the 144 exceptional pairs; `c2` the census (two programs); `c3` orbits (pynauty); `c4` networkx; `c5` pricing arithmetic; `c6` log accounting; step 7 SAT sample (CNF hash + kissat + drat-trim on 14 queries); `c8` the cited #1212 text. `FULL=1 bash verify.sh ...` runs `mc.cpp` on all pairs, the 440,880-section orbit cover, all `h = 15..112` cost grids, and re-solves all 757 SAT queries in two nice-10 chains with per-query timeouts (about 1.5 hours with two chains; summed per-query time of the re-run was 74 min, hardest query kissat 270 s). At most two processes run at a time and nothing waits in an unbounded loop.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
