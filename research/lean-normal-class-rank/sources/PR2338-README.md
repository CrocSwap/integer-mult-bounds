# Decoder floors are tight in the frontier format: one F2^9 label table, factors in col M of a rank-8 realisation (P112 64, E8 72, P104 (#968's unit) 56; two-call batches 128) — no κ claim

> **Scope, stated first.** This package says one thing: *for decoders of the E8-family units that are hosted the way the frontier hosts them* — one global label
> table in `F2^9` (so the admissible pairing `B` of the whole unit has `F2`-rank `≤ 9`), with the factors of every term in the column space of a minimal-rank realisation
> (`col P ⊆ col M`, `col Q ⊆ row M`, rank `M = T = 8`; the square decoder of a *rank-9* realisation is **not** covered, OPEN §5.2 (c)), any number of terms, any number of independently batched calls — **the copy cost of the decoder cannot be lowered
> below P112 64, E8 72, P104 56 (P104 means #968's unit, `F1 = H4`; E7 49 on its own rank-7 table), and two independent P112 calls cost at least 128**, all attained. It contains **no κ claim**, no window,
> no supplier, no word-side (helper, transport, packing) cost. Everything outside that format is listed in §5 as **OPEN**, with what each escape would have to achieve.
> Nothing here removes the need to price an escape; it only says where the escapes are. **Credit, stated first:** the P111 row of Theorem R (rigidity of the rank-9 fitting matrix of a P111 pattern) is prior work of #620 (GamingPuzzled; SAT) and #1097 (bitplane, merged; LRAT-checked in the general model), and #1815 (jmbarrancoml, merged) proves a one-sided P112 fitting rigidity; what is new here is Theorem R on E8, P112, P104 (#968's unit and class representatives), E7, E6, plus P111 on #589's 111 lines in the symmetric and general model with DRAT (§3.1, §3.7). Other P104 units are **not claimed** (§6, §5.6).
>
> **Labels.** **PROVEN** (proof in this README, or a cited proof of a merged / open PR of the swarm); **CHECKED** (recomputed by `verify.sh`: exact integer / `Fraction` / bit
> arithmetic, or SAT whose UNSAT verdict carries a DRAT proof that `drat-trim` verifies; kissat 4.0.4 only, never CaDiCaL); **RECORDED** (a result of the author's working
> cards that this package does **not** re-run, stated with its exact scope and where the evidence is; nothing in §2 marked PROVEN or CHECKED depends on a RECORDED item
> unless that is said); **OPEN**.

## 0. Reading this package

```sh
bash research/decoder-floors-frontier-format/verify.sh /fresh/output/dir        # Python >= 3.11, standard library only
DRAT_TRIM=/path/to/drat-trim KISSAT=/path/to/kissat bash research/decoder-floors-frontier-format/verify.sh /fresh/output/dir
```

Step 0 checks every file against `MANIFEST.sha256` and every pin of `SOURCES.json` (hard stop on a mismatch). Then seven check scripts print one `PASS` / `FAIL` line per
assertion (`SKIP` for anything that needs `kissat` or `drat-trim` when it is absent: those lines are not PASS). `verify.sh` exits nonzero on any FAIL. One core;
6-7 minutes of CPU with both tools (358 s and 417 s user in two runs on a loaded machine; the 30 rigidity instances are re-solved and the UNSAT proofs re-checked), about 20 s without them (4 SKIP lines).
`HIT_FULL=1` additionally re-solves three slow clique-hitting instances (kissat only, no proof; §3.6).

| script | what it recomputes |
|---|---|
| `checks/c1_rigidity.py` | Theorem R: regenerates 30 CNFs (hash, #vars, #clauses), recorded verdicts, 4 shipped DRAT proofs, and (with kissat) re-solves all 30; 16 UNSAT proofs re-checked with drat-trim, 14 SAT models decoded |
| `checks/c2_support_propagation.py` | Lemma 1.1 census (all `2^h − 1` label classes) on D4, D6, E7, E8, P112, P104; survivors, pair ranks, exactness of the per-term rank |
| `checks/c3_batch_premises.py` | labels of P112 in `F2^9`, normals `w_i`, `b(w_i,w_j) = 1`, `ρ(N(f_i),N(f_j)) = 8`, frame lemma, an `O(9)` chart with all 64 cross pairs of rank 7 |
| `checks/c4_masked_costar.py` | #1180's nine-term identity (cost 65), co-star dead sets, survivor 7-cliques |
| `checks/c5_attaining_decoders.py` | the decoders that attain the floors (E8 72, E7 49, D6 30, D4 12, P112 64, P104 56), exact `Fraction` arithmetic |
| `checks/c6_block_minrank_punctures.py` | EDGE E1a (every admissible `B`: the block `N(f)` of P112 has minrank 8; 8 DRAT proofs) and the C4.1 clique-hitting bounds on punctures |
| `checks/c7_p111_unit.py` | the P111 bit unit of #589's word: 111 lines of an E8 line system, `rank_F2 B_d = 9`, an 8-frame |

Layout: `lib/` (E8-family units, Bron–Kerbosch, exact `F2` / `Q` linear algebra, CNF helpers; `roots.py`, `satgen.py`, `frames.py`, `report.py` are the author's own files from
#2277's package, `units.py`, `supprop.py`, `solve.py` are new), `sat/` (generators `rigid.py`, `misc.py`, `hitting.py`; registries; recorded results
`results.jsonl`, `results_misc.jsonl`; shipped DRAT proofs `proofs/*.drat.xz`; author tools `mkresults.py`, `mkmisc.py`), `data/` (frames, the 111 P111 lines, one chart).

## 1. Setting

A **unit** is a set of `v` pairwise non-proportional lines `r_t ∈ Q^8` of the E8 root system (`E8`: 120 lines, `P112 = E8 − F0`, `P104 := E8 − F0 − F1` with `F1 = H4`, the second frame of #968's unit (the swarm has other P104 units, e.g. #1399's 896 admissible ones; those are not covered here, §6 and §5.6; the 1,260 frames `F1` disjoint from `F0` fall into invariant classes by the number of live 8-frames of the unit, `759 / 767 / 801`, and `H4` lies in the 759 class), `E7`, `E6`, the bit unit `P111` of #589). A **realisation** `M` has `M_tt ≠ 0` and `M_ts = 0` for orthogonal `t ≠ s`. A **decoder** is `M = Σ_j p_j q_jᵀ`
with an **admissible (fitting) pairing** `B ∈ F2^{v×v}`: `B_tt = 1`, `B_ts = 0` for non-orthogonal `t ≠ s`, free on orthogonal pairs. Cost `= Σ_j rank_F2 B[R_j, A_j]`, `R_j = supp p_j`,
`A_j = supp q_j` (the copy-pairing rank sum that the invoice charges; every bound below therefore also holds for any costlier physical charge). The **dense** pairing is
`B_d = 1` on every orthogonal pair (and the diagonal); `rank_F2 B_d = h = 9` for E8, P112, P104, P111, `7` for E7, E6.
**Model hypothesis (the frontier format).** The registers of the word carry labels in one `F2^h`; the pairing used by every term is a block of one matrix `B = U Vᵀ`
(or `P Pᵀ`, the physical symmetric form) with `U, V ∈ F2^{v×h}`, i.e. `rank B ≤ h`. That the frontier word hosts its decoders on a single table of dimension `h = 9` is an
engineering fact of the word; the code that fixes it is in this repository: `research/complex-571-cold14-k492/code/construct_k_triangle.py:20` (`P=D['binary_ports'] … h=9`), `:183–187` (the centre frames are `hyper(P[frame[i]])`, so the physical pairing is `J + Gram(even parts)`, symmetric of rank `≤ 9`) and `:364` (`'ports':P[8:]`); the working card `EDGE/HOSTING.md` (not shipped) records the same reading, with the term-cost model of #717 (cost = dimension of the label span). It is **not** proved here, it is the hypothesis whose negation is §5 item 1.
**Label classes** (as in #2277 §1): `C = col B_d` (dim `h`); a class is the support of a nonzero `w ∈ C`; `Def(R) = {w ∈ C : supp w ∩ R = ∅}`, `δ(R) = dim Def(R)`.
**Frames.** A `T`-frame is `T` pairwise orthogonal lines (`T = 8` for E8, P112, P104, P111; 7 for E7). Every realisation has rank `≥ T` (a frame gives an invertible diagonal minor).

## 2. Master table: escape class → status → certificate

"Class X" = one label table with `h = 9` (`h = 7` for E7), factors in `col M / row M` of a rank-`T` realisation.

| # | escape class | what is shown | status | certificate |
|---|---|---|---|---|
| 1 | non-dense admissible `B` of rank `≤ 9` (E8, P112, P104 = #968's unit and three class representatives, P111) or `≤ 7` (E7, E6) | every fitting `B` of that rank **equals the dense `B`**, general `UVᵀ` and symmetric `PPᵀ` | **CHECKED** (16 DRAT-verified UNSAT + 10 SAT controls + 4 non-dense witnesses) | `c1`, §3.1 (Theorem R); the P111 case is #620 / #1097's, re-derived on #589's lines |
| 2 | factors in the E8 root code, any `m`, dense `B` | P112 ≥ 64, E8 ≥ 72, P104 (#968's) ≥ 56, E7 ≥ 49 | **PROVEN** (cited, not re-run: #2228 Thm 4; #1180) + attained (**CHECKED**, `c5`) | #2228, #1180; with row 1 this is every `B` at `h = 9` |
| 3 | any rank-8 realisation, factors in `col M`, any `m` | **P112 ≥ 64**; P104 (#968's unit) ≥ 56; E8 ≥ 72, E7 ≥ 49 | **PROVEN** from **CHECKED** (Lemma 1.1 census) | §3.2 (Theorem P), `c2`; E8/E7/P104 also #2277 Cor. 5.3 |
| 4 | ≤ 8 paid terms, factors anywhere | square ⇒ row 3 | **PROVEN** | §3.3 |
| 5 | #1180's outside-code nine-term example | costs exactly 65; its shape is ≥ 64 for **every** `B` | **CHECKED** + **PROVEN** | `c4`, `c6`, §3.3 |
| 6 | co-star nine-term masked decoders (Disc. 1267) | all 120 dead sets span in every rank-8 realisation ⇒ each is a square decoder of a rank-9 realisation (pins them to §5 item 2(c)) | **CHECKED** (`c4`) + **PROVEN** consequence | §3.3 |
| 7 | batches: `k` independent P112 calls on one `F2^9` table, any chart, factors in `col M_c`, any `m` | `k = 2`: ≥ 128 + 3t; `k ≥ 3` (symmetric charts): ≥ 64k + 3t; attained | **PROVEN** from **CHECKED** premises | §3.4 (Thm B, Bk), `c3`; k = 2 / O(9) / Gram also swarm #2294 |
| 8 | any `B` on a single coordinate block | `rank_F2 B[N(f), N(f)] ≥ 8` for every admissible `B`, all 8 `f` | **CHECKED** (8 DRAT) | `c6`, §3.5 (EDGE E1a) |
| 9 | punctures of the coordinate term under any table | clique hitting: `f(2) ≥ 14`, `f(6) ≥ 46`, `f(7) ≥ 52`, `f(8) = 56`; `s/f(s) ≤ 1/7` on the computed values | **CHECKED** (s = 2, 6: DRAT; 7, 8 exact); s = 3, 4, 5 **RECORDED** (kissat UNSAT re-run with `HIT_FULL=1`, no DRAT here) | `c6`, §3.5 |
| 10 | P111 bit unit | rigid at `h = 9` (sym + general; **prior work of #620 / #1097**, re-derived on #589's lines); set-decoders with ≤ 12 totals cost ≥ 63, and with 13 totals ≥ 63 | rigidity **CHECKED** (2 DRAT); ≥ 63 for ≤ 12 and for 13 totals **RECORDED** | `c1`, `c7`, §3.7 |
| 11 | E8 square root-code decoders for **every** `B` (no `h` cap) | ≥ 72 (4022 pair classes) | **RECORDED** (4022 DRAT verified in the working card; not re-run) | §3.8 |
| 12 | `FL(4)`: every D4 decoder, every `B`, every `m` | ≥ 12 | **RECORDED** (support-level enumeration, 144 classes) | §3.8 |
| 13 | E7 square maximal-normal root-code decoders, every `B` | ≥ 49 (no ≥ 5 root–root partners) | **RECORDED** (exact enumeration + independent audit in the working card) | §3.8 |
| 14 | P104 delivery (#968's decoder) under any `F2^9` table | no helper-free nested delivery (24 DRAT) | **RECORDED** | §3.8 |
| 15 | PUNCT2 near-miss unions `p = 25..44`, any physical table, any `m` | no decoder beats P102's 54/102 (Model C) | **RECORDED** | §3.8 |
| 16 | **label tables of rank `h ≥ 10`** | non-dense fitting tables exist (row 1, witnesses); a 112-port unit needs cost ≤ 59 at `h = 10` to tie P112-`h = 9` (≤ 55 at `h = 11`) | **OPEN** | §5.1 |
| 17 | **factors outside `col M`, `m ≥ 9`** | `m = 9`: `ρ ∈ {8, 9}`; (b) `ρ = 8` one outside factor, (c) `ρ = 9` square rank-9, (d) `m ≥ 10` | **OPEN** | §5.2 |
| 18 | **bit window of 14 totals** (13 totals: RECORDED closed, row 10) | 14-total run in progress in the working card, not final | **OPEN** | §5.3 |
| 19 | **puncture windows `p ≥ 45`** | — | **OPEN** | §5.4 |
| 20 | **batches `m ≥ 17` outside `col M`**, GL charts with `k ≥ 3`, mixed units, correlated demands, `h ≥ 10` joint tables | — | **OPEN** | §5.5 |
| 21 | **P104 units other than #968's** (Theorem R for all 1,260 frames `F1`; the Lemma 1.1 census for them) and **rank-9 square decoders** | — | **OPEN** | §5.6, §5.2 (c) |

Rows 11–15 are *beyond* what the headline needs: at `h = 9` row 1 already forces `B = B_d`, so the headline uses `B_d` only. Their role is to show that the dense-pairing
statements are not hiding a cheap non-dense escape *inside* the `h = 9` class; row 1 does that, and rows 11–13 give the independent every-`B` statements for the
(square, root-code) sub-class.

## 3. Results

### 3.1 Theorem R: the minimal-rank label table is unique (CHECKED, DRAT)

**Theorem R.** Let `U ∈ {E8, P112, P104, P111}` (P104 as defined in §1, plus the class representatives below) and let `B ∈ F2^{v×v}` fit `U` with `rank_F2 B ≤ 9`. Then `B = B_d`. The same holds for `E7, E6` with `rank B ≤ 7`. (**Credit:** for P111 this is #620's and #1097's result; see the paragraph after the table.)
It holds in the general model `B = U Vᵀ` and in the symmetric model `B = P Pᵀ` (the physical one: `B_d = J + C` with `C` the alternating Gram of the even-weight label parts,
which is `PPᵀ` for odd-weight labels `P_t = 1 + e_t`). For P104 the statement is checked for `H4`'s `F1` (the frame of #968; its unit has 759 live 8-frames, so it lies in the 759 class) and one representative of each of the three invariant
classes (`759 / 767 / 801` live 8-frames) of frames disjoint from `F0`: **three classes, four instances** (`H4` is in the 759 class). **These classes are not proven to be single orbits**, and the backfill over all 1,260 frames was not finished,
so P104 is claimed only for #968's unit (`F1 = H4`); Theorem P's census was run on `H4` only, and Theorem R / Theorem P for every other P104 unit is **not claimed** (§6, OPEN §5.6).

*Encoding (`sat/rigid.py`).* `B = U Vᵀ` with `U, V ∈ F2^{v×h}`; constraints `⟨U_t, V_t⟩ = 1`, `⟨U_t, V_s⟩ = 0` for every non-orthogonal ordered pair `t ≠ s`; mode `alt` adds the clause
"some orthogonal ordered pair (unordered in the symmetric model) has `B_ts = 0`"; mode `ctl` omits it. Products and parities are Tseitin variables with constant folding.
*Gauge (PROVEN).* Let `S` be a pairwise non-orthogonal `k`-clique (`k = 8` for E8, P112, P104, P111; 7 for E7; 5 for E6; pinned in `results.jsonl`, `c1.gauge` checks the clique).
Then `B[S,S] = I_k`, so `U[S]` has rank `k`; `GL(h)` acts by `U ↦ U g`, `V ↦ V g^{-T}`, preserves `B` and is transitive on rank-`k` `k`-tuples, so `U[S] = (e_1..e_k)` w.l.o.g. In the
symmetric model with `k = 8`, `h = 9`: `P[S]` is orthonormal, `W = span P[S]` is nondegenerate, `W^⊥ = ⟨w⟩` with `w·w = 1` (`det I_9 = det I_8 · w·w`), so an isometry in `O(9)` maps
`P[S]` to `(e_1..e_8)`; this needs `k ≥ h − 1`, which `registry()` asserts for every symmetric UNSAT instance. (For SAT instances the gauge is only a restriction, so a SAT verdict stands.)
Rank `≤ h` is equivalent to a factorisation with `h` columns, so UNSAT of `alt` says every fitting `B` of rank `≤ h` is dense. (The general model contains the symmetric one as a sub-model, so general-model UNSAT already implies the symmetric statement and, for E7 and E6 where only the general model is run, covers the physical table; the symmetric runs are redundant but consistent.)

| group (`results.jsonl`) | instances | verdict | check |
|---|---|---|---|
| `alt`, minimal rank | P112, E8, P104 (H4, 759, 767, 801), P111, each sym + gen (14 instances); E7, E6 gen at `h = 7` (2) | **UNSAT**, every proof verified by drat-trim (binary DRAT, kissat 4.0.4) | `c1.status`, `c1.resolve`; four proofs shipped (`proofs/`, sym P112 / E8 / P104-H4 / P111) |
| `ctl`, no extra clause | P112, E8, P104-H4, P111 (sym + gen), E7, E6 | **SAT**; every decoded model is a fitting matrix with 0 non-dense orthogonal entries (model is `B_d`) | `c1.ctl` |
| negative controls | `SUB20`, `SUB40` (the gauge clique plus the first 20 / 40 other lines of P112, `h = 9`, gen); P112 at `h = 10` (sym 59 of 3304, gen 89 of 6608 orthogonal pairs with `B_ts = 0`) | **SAT**: a non-dense fitting `B` exists | `c1.neg` |

(The encoding is the one of the author's working card `STRAYS/rigid2.py`; the clique choice here is deterministic and pinned, so the CNFs differ from the card's files, with the
same verdicts. The `h = 10` row shows the instance family does detect non-rigidity; the `SUB` rows show the same at `h = 9` on sub-units.)

**Prior work on P111 and one-sided P112 rigidity (credit; this changes the novelty of Theorem R).** #620 (GamingPuzzled, open) found by SAT, without proof logs, that the rank-9 fitting matrix of its archived P111 pattern is unique; #1097 (bitplane, merged 2026-10-13) proof-checked this with LRAT: "fitting rank ≤ 9, unequal to `B0`" is UNSAT in the general (asymmetric) model with an 8-port gauge. That is the P111 row of Theorem R, and it is **theirs**. *Which set?* #1097's object is the archived sorted Hamming-root order of #620 with indices `39, 52, 57, 71, 76, 78, 103, 109, 114` deleted (`encoding.py:9`); #589's 111 lines (`data/p111_lines.json`) are a different 111-subset of the same 120 Hamming-coordinate lines: 104 lines in common (up to sign), 7 on each side only (a one-off comparison against #1097's retained `e8units.hamming_e8`, not part of `verify.sh`; whether the two sets are `W(E8)`-equivalent was not checked). So Theorem R here **re-derives** the P111 statement on #589's puncture, in both the general and the symmetric model, with DRAT, and does not rely on #1097. #1815 (jmbarrancoml, merged 2026-10-14) is the one-sided predecessor for P112: with the two column spaces fixed, unit diagonals and the required zeros force `N = RRᵀ` and `B = UUᵀ`; Theorem R removes the column-space hypothesis on `B` (every fitting `B` of rank `≤ 9` is dense). What is new here is Theorem R on E8, P112, P104 (#968's unit and representatives), E7 and E6.

**Corollary R1 (PROVEN from Theorem R and the theorems of §3.2 / rows 2).** In the frontier format (one `F2^9` table, `F2^7` for E7), every term pairs through the dense `B_d`. Hence
every statement made below for the dense pairing holds for every hosted decoder, and *the overcomplete "any `B`" slack* (orthogonal-normal blocks of fitting minrank 5–6;
orthogonal E8 root–root terms of rank 6) *does not exist at `h = 9`*: it needs a non-dense `B`, hence `h ≥ 10`.
**Corollary R2 (two-call tables, PROVEN).** If a two-call batch uses one `F2^9` and each call's block fits P112, the labels are `(P, PΦ)` with `Φ ∈ O(9, F2)` (general model:
`(U, V), (UΦ, VΦ^{-T})`, `Φ ∈ GL(9)`). *Proof.* By Theorem R both blocks equal `B_d`, of rank 9. `P_1P_1ᵀ = P_2P_2ᵀ` has rank 9, so `P_1, P_2` have the same column space and `P_2 = P_1Φ`;
then `P_1(ΦΦᵀ − I)P_1ᵀ = 0` with `P_1` of full column rank gives `ΦΦᵀ = I`. ∎

### 3.2 Theorem P: P112 ≥ 64 in every rank-8 realisation (PROVEN from CHECKED)

Setting (#2277 §5). `K` is any field (the swarm uses `Q` / `C`; Lemma 1.1 and Theorem P are field-independent). Let `M` be a realisation of rank exactly `T = 8` (the minimum), `M = P₀ N Q₀ᵀ`, `P₀, Q₀ ∈ K^{v×8}` bases of `col M`, `col Mᵀ`, `N ∈ GL_8`; `π(t)` is row `t` of `P₀`.
Consider decoders with `p_j = P₀x_j`, `q_j = Q₀y_j` (every square decoder `m = 8` is of this form; for `m > 8` this is the hypothesis `col P ⊆ col M`). Then `N = Σ_j x_j y_jᵀ`, so at least 8 terms
are nonzero.

**Lemma 3.1 (support-only bound; #2277 Lemma 5.1, restated).** For `R, A ⊆ [v]`, `rank_F2 B_d[R, A]` depends only on the subspaces `Def(R), Def(A) ⊆ C`, and `≥ h − δ(R) − δ(A)`.
*Proof.* Take `B_d = X Yᵀ`, `X = Y ∈ F2^{v×h}` of full column rank (`B_d` symmetric), `col X = C`. `ker X_R ≅ Def(R)` via `w = Xz`, so `rank X_R = h − δ(R)`, and the row space of `X_R` is
the annihilator of `ker X_R`, i.e. determined by `Def(R)`; likewise for `A`. Sylvester gives the bound. ∎
**Lemma 3.2 (Theorem 4′; #2277 §5, restated).** `cost ≥ Σ_{j : x_j, y_j ≠ 0} (h − δ(R(x_j)) − δ(A(y_j)))`, with `R(x) = {t : π(t)·x ≠ 0}`. If `w ∈ Def(R(x))` then `π(supp w) ⊆ x^⊥`: the class
`supp w` is *deficient* (its `π`-image lies in a hyperplane). *Proof.* Lemma 3.1 and the count of nonzero terms. ∎

**Lemma 1.1 (support propagation; working card `IDEAL3` §1.1, PROVEN here).** Let `E` be an 8-frame and write a functional `h*` that kills `π(O)` as `h* = Σ_{e ∈ E} c_e σ(e)`, where `σ(e) = N κ(e)ᵀ`, `κ(e)` = row `e` of `Q₀`
(`π(e)·σ(e′) = M_{ee′}`: for a frame `E` the `σ(e)` are the dual basis of `{π(e)}` up to the nonzero scalars `M_ee`, and `σ(e)` depends on the line only). (i) `c_e = 0` for `e ∈ E ∩ O`: `h*(π(e)) = c_e M_ee`. (ii) For every 8-frame `F`: `supp_E(c) ⊆ (E ∖ O) ∩ ⋃_{g ∈ F∖O} N̄(g)`,
`N̄(x) = {x} ∪ {lines non-orthogonal to x}`. *Proof.* (i) is the displayed identity. For (ii), applying (i) to `F` gives `h* ∈ span σ(F∖O)`; expanding `σ(g)` in the dual basis of `E`,
`σ(g) = Σ_e (M_eg/M_ee) σ(e)`, whose `E`-support lies in `{e : M_eg ≠ 0} ⊆ N̄(g) ∩ E` (`M_eg = 0` for orthogonal `e ≠ g`). ∎
*Corollary.* If iterating (ii) over all frames ends with some `S_E = ∅`, the class `O` is non-deficient in **every** rank-8 realisation.

**Census (CHECKED, `c2`).** For every one of the `2^h − 1` classes: D4 (3 frames), D6 (15), E7 (135), E8 (2025): **all** certified. P112 (1260 frames): **exactly 8 classes uncertified** (the
8 sets of 56 live lines orthogonal to one removed root; each has `rank_Q = 7`, i.e. is Gram-deficient, so the certificate is sharp); P104 (`H4`'s unit, 759 frames; the census was run on this unit only): 16 uncertified (sets of 52), also
exactly the Gram-deficient ones. In both units the uncertified classes contain **no 2-dimensional subspace** (`a ⊕ b` is never one). For each uncertified `O`, the classes with support inside `O` are
`{O}` alone (`c2.def`), so `Def(V∖O) = ⟨w_O⟩` and the single-deficiency rank is `rank B_d[V∖O, V] = 8`; over all ordered pairs of P112 survivors `rank B_d[V∖O, V∖O′] = 8` (64 of 64), and
for P104 the values are `8` (192) and `7` (64).

**Theorem P (PROVEN from the CHECKED census).** For P112, every rank-8 realisation `M`, every decoder with `col P ⊆ col M`, `col Q ⊆ row M` (all square decoders, any `m` otherwise), dense `B`:
**cost ≥ 64**, attained by the removed-frame coordinate decoder (`c5`). For P104 = #968's unit (`F1 = H4`; the census of Lemma 1.1 is run on this unit only): **cost ≥ 56**, attained (`c5`).
*Proof.* A nonzero `w ∈ Def(R(x_j))` is a deficient class (Lemma 3.2), hence one of the 8 (16) survivors (Corollary of Lemma 1.1; the census). Survivors contain no 2-dimensional subspace, so
`δ(R(x_j)), δ(A(y_j)) ≤ 1`, and by Lemma 3.1 and the census the term's rank is `9` (no deficiency), `8` (one) or, for both deficient, the pair rank: `8` in P112, `≥ 7` in P104. So every nonzero
term costs `≥ 8` (P112), `≥ 7` (P104); at least 8 terms are nonzero. ∎
For E8 (72) and E7 (49) no class is deficient (census), so every term costs `h`; with at least `T` terms the floors are `8·9 = 72`, `7·7 = 49`. (#2277 Cor. 5.3 gives all of E8 72, E7 49, D6 30, D4 12, P104 56
via the weaker clause-(c) certificate; its P112 value was 56, and "P112 ≥ 64 for every realisation" was listed there as open — Theorem P closes it.) **Sharpness (CHECKED, `c5`):**
frame decoders with `M = Gram` cost 72 (E8), 49 (E7), 30 (D6), 12 (D4); the removed-frame decoder of P112 costs 64; the eight frame-pair terms of #968 cost 56 on P104.

### 3.3 Few terms, outside `col M`, #1180 and the co-star (PROVEN / CHECKED)

*(working card `STRAYS-MASK` §1–§3; dense `B`, which at `h = 9` is every `B` by Theorem R)*
**1.1 Free-term absorption.** A term with `B[R_j, A_j] = 0` contributes `0` to the cost and nothing on the diagonal or on orthogonal pairs, so the paid part `N = Σ_{paid} p_j q_jᵀ` is again a realisation
of the same pattern with the same cost; w.l.o.g. every term is paid.
**1.2 Merge lemma (#1224 Lemma D, both sides).** If `q_i = c q_k` then `p_i q_iᵀ + p_k q_kᵀ = (c p_i + p_k) q_kᵀ`; the new row support lies in `R_i ∪ R_k`, and
`rank B[R_i ∪ R_k, A_k] ≤ rank B[R_i, A_k] + rank B[R_k, A_k]` (`A_i = A_k`). The merge does not raise the cost for **any** `B`. W.l.o.g. no two row normals and no two column normals are proportional.
**1.3 `m ≤ 8`.** `rank N ≥ α_⊥ = 8`, so `m ≥ 8`; `m = 8 = rank N` is the square case with factors in `col N / row N` (every factor lies in the column space of a rank-8 matrix with 8 terms), so Theorem P
gives `≥ 64` (P112), `≥ 56` (P104, #968's unit), **whatever the factors, the realisation or the masking**. This covers every component of #1213, not only the connected one.
**1.4 `m = 9` trichotomy.** `a = rank P = ρ + s`, `b = rank Q = ρ + t`; Sylvester: `ρ ≥ a + b − 9`, so `s + t ≤ 9 − ρ` with `ρ = rank N ∈ {8, 9}`. (a) `ρ = 8`, `s = t = 0`: Theorem P; (b) `ρ = 8`, `s + t = 1`: §5.2 (b) (#1180 / #1224's residual class); (c) `ρ = 9`: square in a rank-9 realisation (OPEN, §5.2 (c)).
**#1180's example (CHECKED, `c4`).** Its nine-term identity `D Tᵀ = 8·Gram` holds on all `112 × 112` entries (`ex1180`-form: `t_1 = R_0 + z`, outside terms `(t_1, R_0)` and `(−z, R_0)`) and its term ranks under `B_d`
are `[8]×8 + [1]`, **total 65**. Its two outside-`col M` terms share the column vector `R_0`: by the merge lemma (any `B`) the example costs at least the removed-frame decoder, whose terms are the blocks `B[N(f), N(f)]`,
each of fitting minrank 8 for every `B` (`c6`, §3.5), so **after merging the two outside terms it is the removed-frame decoder, which costs ≥ 64 for every admissible `B` by E1a**: the "outside `col M`" in #1180's example is only a split of a proportional pair.
**Co-star (CHECKED, `c4`; PROVEN consequence over any field of characteristic 0, the scope of the working card `STRAYS-MASK` Theorem 3.2).** *Definitions.* The **dead set** of a term `p qᵀ` on the row side is `{t : p_t = 0}` (the lines the term does not touch), on the column side `{t : q_t = 0}`; a set of lines is **spanning** if its images `π(t)` span `K^8` in every rank-8 realisation. For each of the 120 root lines `α`, the dead set `V ∖ S_α` (`S_α` = live lines orthogonal to `α`, plus `α` if live; `|S_α| = 60` for the 112 live `α`, 56 for the 8 removed) is certified spanning in every
rank-8 realisation (Lemma 1.1). *Lemma (inside dead sets; STRAYS-MASK Lemma 3.1).* If a term of a rank-8 realisation has its column factor in `row M` (`q = Q₀ȳ`, `ȳ ≠ 0`, an "inside" side), its dead set `{t : κ(t)·ȳ = 0}` has images in the hyperplane `ȳ^⊥`, so it is not spanning and cannot contain `V ∖ S_α` (rows by transposition: the pattern is symmetric). *Consequence.* Let a nine-term masked co-star decoder (philippeVV, Discussion 1267; every term's supports inside co-stars, arbitrary coefficients, zeros, any `k`) have `ρ` = the rank of the full nine-term sum. If a term is free, or two row or two column normals are proportional, the paid or merged part has `≤ 8` terms, hence is square, and Theorem P gives `≥ 64` outright. Otherwise `ρ = 8` would give `s + t ≤ 1` (§1.4), so one side, say `t = 0`, is inside for all nine terms, contradicting the Lemma; `ρ ≥ 10 > m` is impossible. So `ρ = 9` and the decoder is a square
biorthogonal decoder of a **rank-9** realisation: cases (a), (b) of §1.4 are empty for co-stars. This pins the open `k = 7/8/9` families to §5.2 (c); it does not close them. Every survivor class contains an
orthogonal 7-clique and no 8-clique (`c4.survclique`), so its killing functional is unique up to scale in every rank-8 realisation.

### 3.4 Batching: independent calls on one `F2^9` table (PROVEN from CHECKED)

*(working card `STRAYS-BATCH`; the model is #1714's: `k` independent P112 calls, `C = I_k`, cross-call blocks of the requested matrix are 0.)* The requested matrix is `M_1 ⊕ … ⊕ M_k`, `M_c = P_cQ_cᵀ` a rank-8
realisation (Gram: `P_c = Q_c = X`). A decoder is `Σ_j d_j t_jᵀ = M` with `d_j = (P_ca_j^{(c)})_c`, `t_j = (Q_cc_j^{(c)})_c`; exactness is `A Cᵀ = I_{8k}`. One label table on all `112k` lines; each call's block fits P112,
so by Theorem R it is dense and by Corollary R2 call `c` carries labels `PΦ_c`. The charge of term `j` is `rank_F2` of the pairing between the span of the output labels of its union support `S_j` and the span of the input
labels of `T_j` (the cheapest charge, #1714; every costlier charge is covered). **Premises (CHECKED, `c3`; they are Lemma 1.1's sharpness in label language):**
(P1) in any rank-8 realisation the support of `P_c x`, `x ≠ 0`, has label span `V` (dim 9) or one of 8 hyperplanes `H_i = w_i^⊥` (it avoids the deficient class `O_i`, the live lines orthogonal to `f_i`); the survivors contain no 2-dimensional
subspace, so no support avoids two classes and every span has dim ≥ 8. (P2) `b(w_i, w_j) = 1` for all 64 ordered pairs, and `ρ(N(f_i), N(f_j)) = 8` for all 64 pairs, `i = j` included.
**Theorem B (`k = 2`, PROVEN).** For every chart `Φ` (`O(9)` symmetric or `GL(9)` general) every decoder satisfies `Σ_j cost_j ≥ 128 + 3t`, `t = #{j : cost_j = 7}`; the minimum is 128 (two coordinate decoders), only at `t = 0`.
*Step 1.* Union spans have dim ≥ 8 (P1), so cost `≥ 8 + 8 − 9 = 7`; at cost 7 both spans are hyperplanes. *Step 2 (rank-7 terms are pure cross-call).* If `a_j` has a nonzero part in call `c`, that part's span (dim ≥ 8) lies in the output span `H`
of dim 8, hence equals it, so `H` is a call-`c` output hyperplane; likewise `H′` is the input hyperplane of every call where `c_j` is nonzero. If one call had both parts nonzero, `(H, H′)` would be an output / input hyperplane pair of
that call, which pairs at rank 8 by (P2). So `calls(a_j) ∩ calls(c_j) = ∅`. *Step 3 (rank count).* With `N = Σ_{cost 7} a_jc_jᵀ = [[0, N₁₂],[N₂₁, 0]]`, `t₁₂ + t₂₁ = t`, `rank N₁₂ ≤ t₁₂`, `rank N₂₁ ≤ t₂₁`; the other active terms
cost ≥ 8 and sum to `I₁₆ − N`, so there are at least `rank(I − N) = 8 + rank(I₈ − N₂₁N₁₂) = 16 − d` of them, `d = dim ker(I₈ − N₂₁N₁₂) ≤ min(t₁₂, t₂₁) ≤ t/2`. So `Σ cost ≥ 7t + 8(16 − d) ≥ 128 + 7t − 8min(t₁₂,t₂₁) ≥ 128 + 3t`. ∎
**The counting floor 120 is not the truth** (`c3.chart.rank7`): there is a chart `Φ ∈ O(9, F2)` (shipped in `data/chart_rank7.json`) for which all 64 cross pairs (call-1 support `N(f_i)`, call-2 support `N(f_k)`) pair at rank 7, while within a call the same pairings have rank 8.
Per-term counting alone gives 120; the extra 8 units come from the rank argument.
**Theorem Bk (`k ≥ 3`, symmetric model, PROVEN).** Charts `Φ_c ∈ O(9, F2)`, any rank-8 realisations, any `m`: `Σ cost ≥ 64k + 3t`. *Proof.* Steps 1–2 verbatim. Every hyperplane is `n^⊥` for a unique normal; slot `(c,i)` has normal `Φ_cw_i`, and
`b(n, n) = 1` by (P2). Partition the `8k` slots into classes by normal (at most one slot per call). A rank-7 term has `b(n, n′) = 0`, so `n ≠ n′`; `a_j` is supported in the class of `n`, `c_j` in the class of `n′`. For `x ∈ Z^P_{c,i}`, `y ∈ Z^Q_{c,i′}` (`Z^P_{c,i}` := the coefficient vectors `x` whose call-`c` output support `supp P_c x` avoids `O_i`, i.e. lies in the hyperplane slot `(c,i)` with normal `Φ_c w_i`; `Z^Q_{c,i′}` := the same on the input side, `supp Q_c y` avoiding `O_{i′}`),
`i ≠ i′`: `yᵀx = Σ_{e ∈ E}(y·q_c(e))(p_c(e)·x)/M_ee` over any 8-frame `E` of live lines; a summand needs `e ∈ N(f_i) ∩ N(f_{i′})`, and `c3.framelemma` finds for every `i < i′` a frame with `E ∩ N(f_i) ∩ N(f_{i′}) = ∅`, so `yᵀx = 0`. Hence
`K = CᵀA` over the rank-7 terms has `K_ij ≠ 0` only if `class(c_i) = class(a_j)`, `K_ii = 0`. *Lemma K:* `corank(I_{8k} − ACᵀ) = corank(I_t − K) ≤ t/2` (order the classes; the larger of `{j : α(j) < β(j)}`, `{j : α(j) > β(j)}` has size `≥ t/2`, along `K`-arcs inside it the class strictly
moves, so `K[S,S]` is nilpotent up to a permutation and `I − K[S,S]` is invertible). So `Σ cost ≥ 7t + 8(8k − t/2) = 64k + 3t`. ∎ (Every batch with exactly `8k` terms needs no factor hypothesis, #1714 §5.)
**Credit.** #2294 (thakrarsagar) proves the `k = 2`, `O(9)`, Gram-root-code core first (its Theorem A: `≥ 128 + 6μ + 7(r_01 + r_10 − 2μ)`, `μ = min(r_01, r_10)`) and independently finds that some isometric charts make all 64 exceptional pairs rank 7; the derivation above was done
before #2294 was read and is the same inequality. Beyond #2294: `GL(9)` charts of the general factor model, any rank-8 realisation (the Theorem P setting), and `k ≥ 3` in the symmetric model.

### 3.5 One coordinate block under any `B`; punctures (CHECKED)

**EDGE E1a (`c6`, 8 DRAT).** For each removed root `f` (all 8), `N(f)` is the 56-line support of the coordinate term. *Every* admissible `B` has `rank_F2 B[N(f), N(f)] ≥ 8`: the instance "`rank ≤ 7`" (gauge: the largest non-orthogonal
clique in `N(f)`, 7 lines) is UNSAT with a drat-trim-verified proof (8 proofs of about 70 kB each; one shipped), and "`rank ≤ 8`" is SAT (the dense block). So no choice of `B` lowers a coordinate term of the removed-frame decoder, and with
`m ≥ 8` the removed-frame decoder costs `≥ 64` for every `B`. (Together with the merge lemma this is the "shape ≥ 64 for every `B`" of §3.3.) `ω_non(N(f)) = 7` and `α_⊥(N(f)) = 4` are recomputed in `c6`.
**Punctures (NEWWORD C4.1).** A puncture `D ⊆ N(f)` (lines deleted from the support) that brings `rank B[R∖D, R∖D]` to `≤ 8 − s` for some admissible `B` must hit every `(9 − s)`-clique of pairwise non-orthogonal lines (a clique `C` has `B[C,C] = I`
for every admissible `B`). `f(s)` := the least size of such a hitting set. Proven bounds: `f(2) ≥ 14` (the 576 7-cliques cannot be hit by 13 lines; DRAT), `f(6) ≥ 46` (the largest triangle-free kept set has 10 lines: 11 is UNSAT, DRAT; the working card
had 15 and `≥ 42`), `f(7) ≥ 52` (`α_⊥(N(f)) = 4`, exact), `f(8) = 56`. Recorded (kissat UNSAT, working-card DRAT; `HIT_FULL=1` re-solves them here without a proof): `f(3) ≥ 23`, `f(4) ≥ 32`, `f(5) ≥ 38` (the card's `s = 1` value, `z ≥ 8`, is EDGE's separate
`killgauge` SAT result and is not reproduced here). The ratios `s/f(s)` are `.1429, .130, .125, .132, .130, .135, .143` (`s = 2..8`; `c6.f` prints the proven ones): **no computed `s ∈ {2..8}` exceeds 1/7** (`s = 3–5` RECORDED, `s = 1` not computed here). The puncture-saving statement
("punctured coordinate decoders tie P112 at best under any global label table") is therefore the clique-hitting bound plus the card's price model (break-even `s/f(s) > .1441`, margin under 1%, inside the price model's error): the **bound** is CHECKED, the
**pricing consequence** is RECORDED and is not claimed as a theorem.

### 3.6 Slow instances

`HIT_FULL=1` re-solves `hit_k6_z22`, `hit_k5_z31`, `hit_k4_z37` (the `s = 3, 4, 5` bounds) with kissat only; recorded (kissat 4.0.4, UNSAT, no proof; wall time under machine load): `hit_k6_z22` 102 s, `hit_k5_z31` 227 s, `hit_k4_z37` 9 s, i.e. `f(3) ≥ 23`, `f(4) ≥ 32`, `f(5) ≥ 38`; their results are in `sat/results_misc.jsonl` (flagged `slow`) and re-derived by `HIT_FULL=1`. No DRAT is checked for these here (the proofs are 100–200 MB).

### 3.7 The bit side: P111 (rigidity CHECKED, prior work of #620 / #1097; "≥ 63" RECORDED)

**P111 is rigid at `h = 9` (CHECKED, `c1`, `c7`; prior work: #620 by SAT, #1097 LRAT-checked in the general model, see §3.1).** On #589's set, which is not #1097's (§3.1), the statement is re-derived here in two models. The 111 live lines of #589's word (`data/p111_lines.json`; the source file's sha256 is pinned in `SOURCES.json` and equals the entry of `research/e8-bit-p111-tuned/MANIFEST.sha256` on `main`) are a sub-configuration of an E8 line system
(`c7`); `alt` is UNSAT in the symmetric and the general model (drat-trim verified; the symmetric proof is shipped), the controls are SAT with the dense `B`. So at `h = 9` the bit side is also a dense-`B` question.
**RECORDED (not reproduced here): P111 set-decoders with at most 12 retained totals cost ≥ 63.** The working card `STRAYS-BIT` proves it premise-free from the full census of the E8 line matroid's flats (ranks 1–6: `120 / 4,900 / 85,680 / 661,542 / 2,091,600 / 2,221,780`, maximal line counts `1, 3, 6, 12, 20, 36`;
the rank-6 flats with ≥ 24 lines are exactly the 4,900 sets `a^⊥ ∩ b^⊥`), `G ≥ 12` (no live code word is covered by rank-≤ 6 sets of total rank ≤ 11, exhaustive) and an induction `D(Λ) ≥ r_k + D(Λ ∩ a_k^⊥)`. That enumeration needs 378 s with numpy and was **not ported to the standard library**; this package
does not verify it and no other statement here uses it. It extends #757 / #761 (63 optimal on the shipped P111 for 9, 10 and 11+ label terms) and agrees with #620 (63 for P111; exact SAT, cost ≤ 62 UNSAT, 8 totals UNSAT; also #1097's rank-9 uniqueness above).
**RECORDED (another agent's working card, `STRAYS-BIT` closure 2; not re-run and not reviewed here): P111 word-priced bit decoders with 13 totals cost ≥ 63.** In the word's pricing (the set-decoder model: retained totals are arbitrary live-line sets, each priced by the rank of its span) the card reports exact rational Farkas certificates for all 132 code classes of excess 4 (re-checked there with `Fraction`s only), on top of `G(3) ≥ 15` and `G(4) ≥ 14` (exhaustive: no ≤ 4-set low cover of total rank ≤ 13, no 3-set low cover of total rank ≤ 14), and `P110` (P111 minus line 38) `≥ 63` for `n ≤ 12` totals, which is P110's whole hosting window (`R = 439 ≤ 4·110`). The card also reports rigidity at `h = 9` on P110 (controls SAT). The card's status for **14 totals** is *in progress*: of the 51,973 excess-5 classes, 51,233 have Farkas certificates and 735 are integer-only (kissat UNSAT, drat-trim verified for the 55 classes with `κ = 6, 7`; `κ = 8, 9` pending, no final count). So: **13 totals RECORDED closed; 14 totals in progress, OPEN** (§5.3). Not covered by the card: decoders outside the set-decoder model (a retained total charged below its source span's rank, i.e. a projected or asymmetric copy) and `≥ 15` totals (excluded by hosting, `R ≤ 4v`).

### 3.8 Recorded results of the working cards (not re-run)

* **E8□ (IDEAL3 §4.6).** Every square E8 root-code decoder costs `≥ 72` for **every** `B` (4,022 non-orthogonal pair classes, each with fitting minrank `≥ 9`); the card's `census/e8drat.out` ends "DONE 4022 classes; not verified: 0". The proof logs (139 MB) are not shipped. Not needed at `h = 9`.
* **FL(4) (IDEAL3 §2).** The Frame Lemma for `n ≤ 4` (PROVEN modulo a 144-class support-level enumeration) gives `D4 ≥ 12` for every decoder, every realisation, every `m`, every `B`. Lemmas 4.1 (maximal-pair reduction) and 4.2 (`k`-term averaging) of IDEAL3 §4 are the shared-`B` reductions used by E8□ and the E7 statement below.
* **E7 (STRAYS S4).** Square maximal-normal root-code decoders cost `≥ 49` for every `B`: no decoder has ≥ 5 root–root partners (256 bad partners, 16 compatible 5-sets, 0 six-sets, 0 completions; Sonnet enumeration, independently re-audited). The 49 *on E7's own rank-7 table*, the case in the headline, needs only Theorem R at `h = 7` (CHECKED) and #2277 Cor. 5.3.
* **P104 delivery (NEWWORD C4.2).** For #968's P104 frame-pair decoder (cost 56, rank-7 terms) no global admissible label table in `F2^9`, with any per-term gather orientation, allows helper-free nested delivery (24 DRAT-verified instances; pairs `(0,1), (0,4), (1,4)`, same orientation, both directions; the graph of class-1 pairs is triangle-free and 3-regular on the 8 terms, so among any three mutually adjacent terms two share an orientation). Extends EDGE-B's Delivery Lemma from the dense table to every table. Escape: `h > 9` (a P104 at `h = 10` already loses to P112 at `h = 9` on the format ceiling: `3.931e-3 < 3.995e-3`).
* **PUNCT2, `p = 25..44` (NEWWORD c5).** Model C (dense pairing, column-space factors): at the 1,323 near-miss unions the bilinear forms vanishing on orthogonal live pairs have nullity 1 (`N ∝ Gram`), so every 8-term decoder is biorthogonal; for `m ≥ 9` merging and PUNCT2's deficiency census (`d ≤ 2`) give cost `≥ 5m ≥ 45 > 40.24` (`p = 44`) and `≥ 7m − 12 ≥ 51 > 44.47` (`p = 36`); rigidity at the two representatives is DRAT-verified and the 1,323 unions form two `W(E8)` orbits. So no decoder in the class beats P102's 54/102; the "+13–15%" near-miss points were relaxation artefacts. Depends on PUNCT2's census inputs, which are not shipped.
* **E7 frame decoders (NEWWORD c3).** No E7 root-line decoder with `m = 8` and every cross `⟨y_i, x_j⟩ = ±1`; best type mixes cost `≥ 39` on `≤ 50` ports (`x ≥ .78`), none beats P56's `x = .75` even with per-term-optimal `B` and free delivery (scope: crosses in `{0, ±1}`, root-line normals).
* **EDGE (coordinate block, minrank 8 every `B`):** CHECKED in §3.5. EDGE-B's Delivery Lemma (dense table) is the one C4.2 extends; not re-run.

## 4. How to cite this

"For every decoder hosted on one `F2^9` label table (Theorem R: the pairing is the dense one), with factors in the column space of a rank-8 realisation and any number of terms (Theorem P; #2228 Thm 4 for the root code), the copy costs of the E8-family units are exactly
P112 64, E8 72, P104 56 (#968's unit, `F1 = H4`; E7 49 on rank-7 tables), and `k` independent P112 calls cost `≥ 64k` (`= 128` for `k = 2`; symmetric / physical table for `k ≥ 3`, `GL` charts with `k ≥ 3` are open, §5.5) (Theorem B, Bk; #2294). Remaining escapes: tables of rank `≥ 10`, rank-9 square decoders and overcomplete factors outside `col M` with `≥ 9` terms, the bit window of 14 totals (13 is RECORDED closed), puncture windows `p ≥ 45`, batches of `≥ 17` terms outside `col M`, other P104 units."

## 5. OPEN (each leaves class X; priced where a price exists; none constructed)

<a id="open-1"></a>
### 5.1 Label tables of rank `h ≥ 10`

Non-dense fitting tables exist at rank 10 (`c1.neg`: `P112_sym_h10_alt`, `P112_gen_h10_alt` are SAT). *Price* (working card `STRAYS/PRICE-P112-H10.md`, a Sonnet helper's pricing, not a theorem; it reproduces the P104 rows of NEWWORD `c4/PRICE-H10.md`): a 112-port unit at
`h = 10` must reach **cost ≤ 59 (−5 units)** to tie P112-at-`h = 9`, before any helper growth; at `h = 11`, `≤ 55`. **Status: undecided.** Per-term floors under a global rank-10 cap were probed on the first orthogonal-normal class (free-`B` minrank 6) and timed out at 20 minutes for cap 7 at both `h = 10` and `h = 12`. Per-term `≥ 8` at rank `≤ 10` would close `h = 10` (since `m ≥ 8`).
For E8 overcomplete under any `B`: non-orthogonal terms `≥ 9`, other orthogonal terms `≥ 8`, orthogonal root–root terms are 6; counting alone allows `m ∈ {9, 10, 11}` below 72; the `m = 9` root-normal family is jointly `≥ 65` (EDGE). Another agent works this (working card `STRAYS-H10`).
<!-- UPDATE IF CLOSED: §5.1 / master row 16 — state the h = 10 (and h = 11) per-term floor or the decoder found, its status label, the check script and DRAT proofs, and update §4 and the title. -->

<a id="open-2"></a>
### 5.2 Factors outside `col M`, `m ≥ 9`

Proven (§3.3): `m ≤ 8` ⇒ `≥ 64` / 56 for any factors and any realisation; `m = 9`: `ρ = rank(paid part) ∈ {8, 9}`, `s + t ≤ 9 − ρ`. **Open:** (b) `ρ = 8` with one factor outside `col M` (#1180's residual class; necessary conditions proven, 42k of 45k class pairs uncertified at support level);
(c) `ρ = 9`, square in a rank-9 realisation (needs a rank-9 analogue of Lemma 1.1, `Σδ ≥ 18` to reach ≤ 63; contains every philippeVV co-star `k = 7/8/9` family, §3.3); (d) `m ≥ 10` (budget `s + t ≤ m − ρ`, #1633; the average term rank would have to drop below 6.4). All under dense `B`, which at `h = 9` is every `B`. (working card `STRAYS-MASK`; `STRAYS-MASK2` continues.)
<!-- UPDATE IF CLOSED: §5.2 / master row 17 — which of (b), (c), (d) closed, the theorem, status labels and checks. -->

<a id="open-3"></a>
### 5.3 Bit window of 14 totals (13 totals: RECORDED closed)

P111 set-decoders with `14` retained totals: the `≤ 12` and `13`-total bounds are RECORDED (§3.7); the 14-total finite per-code check is still running in the working card (`STRAYS-BIT`, no final count), so it stays OPEN. `≥ 15` totals are excluded by hosting in the current word (`R ≤ 4v`).
<!-- UPDATE IF CLOSED: §5.3 / master row 18 — the 14-total bound, its status label and check. -->

<a id="open-4"></a>
### 5.4 Puncture windows `p ≥ 45`

PUNCT2's exclusion covers `p = 25..44` (RECORDED, §3.8). For `45 ≤ p ≤ 112`: is `cost ≥ (54/102)(120 − p)` in Model C (dense or rank-≤ 9 `B`), column-space factors, any `m`? The census of `d ≥ 3` kernels and non-root flats beyond 44 has not been run; the `T²` law (#2125, argued) predicts no gain for `v ≲ 64`. (working card `PUNCT3`.)
<!-- UPDATE IF CLOSED: §5.4 / master row 19 — the p-range now covered, the theorem, status labels and checks. -->

<a id="open-5"></a>
### 5.5 Batches outside class X

`m ≥ 17` terms with factors outside `col M` (every 16-term batch needs no factor hypothesis, #1714 §5); `GL(9)` charts with `k ≥ 3` (mathematical only: the physical table is symmetric; the obstruction is a possible loop in the component quotient of the output / input hyperplane graph, so
Lemma K's ordering argument may fail; the bound needs only `corank(I_t − K) ≤ 7t/8`); `h ≥ 10` joint tables (pure cross terms may cost `< 7`; #2294 Props B–D cover cross blocks that factor through the call labels as bilinear forms); correlated demands (`C ≠ I`, #1714 §4); mixed-unit batches; a second call on a different unit.
<!-- UPDATE IF CLOSED: §5.5 / master row 20 — which batch case closed, theorem, status labels and checks. -->

<a id="open-6"></a>
### 5.6 Other P104 units; rank-9 square decoders

Theorem R and the Lemma 1.1 census (Theorem P) are run for P104 = #968's unit (`F1 = H4`) only, with Theorem R also at one representative of each of the classes `759 / 767 / 801`. **Not claimed:** Theorem R for all 1,260 frames `F1`, the census and Theorem P for any other P104 unit (the swarm has many, e.g. #1399's 896 admissible ones). The rank-9 square case is §5.2 (c).
<!-- UPDATE IF CLOSED: §5.6 / master row 21 — which P104 units are now covered, the check scripts and DRAT proofs. -->

**Out of scope by construction:** non-E8 units (BIGTHEORY: no-go only for `h ≤ 13`; #2222-type large-`h` units are compensation-bound), and all word-side overheads (helpers, transport, packing). 1337isnot1337's rank-16 child-merging screen (Discussion 1166, `< 0.21%` even at zero overhead) is a word-side route, not a decoder saving.

## 6. What was not reproduced

See §3.5 (steps `s = 3, 4, 5` of the puncture table; `s = 1` not computed), §3.7 (the 12- and 13-total bit bounds) and §3.8: every RECORDED item is a result of the working cards that this package neither re-runs nor depends on for rows 1–10 of §2, with the single exception noted in §3.5 (the pricing
consequence of the puncture table). Differences between the working cards and this package, none of them a failed reproduction: the SAT instances are regenerated with a deterministic gauge clique (the card's files differ, the verdicts agree); `f(6)` is `≥ 46` here (card: `≥ 42` from a looser 15-set instance); the `h = 10` witnesses differ from the card's
(non-dense in 59 / 89 orthogonal entries rather than 171 / 381); the card's "rank(B − B_dense) = 8" for the `h = 10` witness is not claimed. Not claimed: Theorem R for all 1260 frames of P104 (class representatives only), and Theorem P or any P104 statement for units other than #968's (`F1 = H4`); the rank-9 square case (§5.2 (c)); novelty of the P111 row of Theorem R (#620 / #1097).

## 7. Credits and related PRs

Our PRs: #1590 (model, merged), #2111, #2125, #2162 (Lemma CR2 / Theorem B2; navinor's independent audit #2293 passes our CR2/B2 on 58 instances), #2228 (root-code floors Thm 4, dense polar law), #2244, #2277 (Theorem 4′, frame-intersection certificate, Cor. 5.3). Swarm: #968 (frame-pair P104 decoder), #1180 (outside-code nine-term example), #1212 / #1213 / #1236 (rank-8 rigidity, components, root-star supports), #1744 (global fitting rank ≥ 9 on P112), #757 / #761 (P111 63), #620 (GamingPuzzled; P111 rank-9 uniqueness and 63, found by SAT) and #1097 (bitplane, merged; LRAT proof of that uniqueness in the general model, on the archived Hamming order, not on #589's set), #1815 (jmbarrancoml, merged; one-sided P112 fitting rigidity), #1331 (Arham-Tahir64, merged; the coordinate COPY 64 is not improved by one free rectangle; related to E1a and the punctures), #1249 (bbMisk, merged; independent verification of #1236's 64), #717 (ours; term cost = dimension of the label span, frontier-word censuses and decoder floors; the hosting model rests on it), #2176 / #2206 (forced minors, exact pairing costs),
#2232 / #2240 / #2247 / #2137 (E6 screens, 1337isnot1337), #2272 (dense-polar small-`T` screen), #2267 (rectangular Lean form of the shadow lemma), #2294 (k = 2 batching, thakrarsagar), #1714 (batch model), #1224 (joaqcoo; the merge lemma and one-sided overcomplete structure), #1633 (bbMisk; excess-rank budgets), Discussion 1267 (philippeVV; co-star families).
Tools: kissat 4.0.4, drat-trim (Marijn Heule, Nathan Wetzler). See `NOTICE.md`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
