# Decoder floors, closures: punctured E8 units (Model C) for 48 ≤ p ≤ 56, all m (no κ claim)

> **Scope, stated first.** A closures-only follow-up of **#2639** (*Decoder floors, closures: punctured E8 units (Model C) to p = 46 (all m) and p ≤ 56 (merged m ≥ 8), windows h = 10–11*, open; this note is based on it and uses its tools, notation and Theorem M8 as stated there). **No κ claim**, no window, no supplier, no word-side cost. #2639 §4 lists "`m ≤ 7` at `48 ≤ p ≤ 56`" as open; this note closes it, so that **every `p` with `48 ≤ p ≤ 56` is closed for every `m`**, in the same setting as #2639: punctured E8 units, Model C (dense `B`, column-space factors). **`p = 47` with `m ≤ 7` is still open and is not claimed**. Any-`B` and masked factors are untouched.
> **Snapshot:** Oct 15 2026, base `origin/main` a571dfa6. Labels as in #2639: **PROVEN** (argument in this README), **CHECKED** (recomputed by `verify.sh`), **RECORDED** (result of the author's working card PUNCT-MID, status quoted; `verify.sh` re-checks a sample, not everything), **OPEN**. kissat 4.0.4 only, never CaDiCaL.
>
> **Credit and prior work.** The model, notation, E7q, Lemma G / H / R, the monotonicity-in-`P` lemma, the merging template and Theorem M8 are those of #2639 (and #2338 behind it); the puncture lineage (#631, #875, #939, #1171 for star label decoders; #1020, #1521, #1180, #1609 at small `p`) concerns other decoder classes and is cited, not re-derived (see #2639 §5). **Overlap:** a search of PR bodies for other closures of these punctures found none; #939 / #1171 treat star label decoders, #2338 / #2639 are this author's own.

## 1. Result

| # | statement | status |
|---|---|---|
| M7-a | `P = 53`, all `q_γ := |S ∩ γ^⊥| ≥ 6`: the Lemma-G-failure CNF is UNSAT for **all 8** rank-7 flat types | **RECORDED** (every leaf kissat + drat-trim VERIFIED in the card, or a counting leaf); sample re-solved here (**CHECKED**) |
| M7-b | `P = 56`, all `q_γ ≥ 17` (and `q_α ≥ 16` at the normal `α` for the E7 type): UNSAT for **all 8** types | same |
| R | reduction of `m ≤ 7`, `48 ≤ p ≤ 56`, to M7-a / M7-b | **PROVEN** from #2639's tools (§2); arithmetic **CHECKED** (`c1`). Imported from #2639 (open), labels as there: E7q PROVEN from CHECKED data; Lemma H PROVEN; Lemma R PROVEN from card-verified data |
| C | **`48 ≤ p ≤ 56` closed for every `m`** (`m ≥ 8`: #2639 Theorem M8 with its Case-B census, 11 leaves; `m ≤ 7`: R + M7) | **PROVEN** from #2639's imported results (Theorem M8: PROVEN from RECORDED data; Case-B census: RECORDED there) and from M7-a / M7-b (RECORDED, leaves sampled CHECKED, tree coverage CHECKED by `c3`) |

Nothing is claimed for `p = 47, m ≤ 7`, for `p ≥ 57`, or outside Model C.

## 2. Reduction (PROVEN, from #2639 §2.1, §2.4, §2.5)
Let `48 ≤ p ≤ 56`, a decoder with `m ≤ 7` merged terms, `need(p) = ⌈(54/102)(120 − p)⌉ = 39, 38, 38, 37, 36, 36, 35, 35, 34` (`c1`).
* `48 ≤ p ≤ 53`. If some root has `q_γ ≤ Q(p) = 5, 5, 5, 6, 6, 6`, E7q (cost `≥ 49 − 2q ≥ need(p)`) closes it for every `m`. Otherwise every `q_γ ≥ 6`. `m ≤ 7` needs `rank N ≤ 7`, so Lemma G fails: some rank-7 flat `F*` (one of 8 `W`-types, WLOG its representative) has every live outside line bad and every orthogonal 8-frame hit by `S` — the CNF of `sat/middrv.py` for (type, `P = p`). For the E7 type Lemma H gives `q_α ≤ p − 50 ≤ 3` (closed by E7q) or `q_α ≥ 16`.
* `54 ≤ p ≤ 56`. If some `q_γ ≤ 16`: Lemma R gives `m ≥ 7`; `m = 7` costs `≥ 35 ≥ need(p)` (35, 35, 34), `m ≥ 8` is M8. Otherwise all `q_γ ≥ 17` (Lemma H's branch is then automatic, `q_α ≥ 17`) and the same Lemma-G-failure CNF applies. At `p = 56` the two sets with `h(K) < 9` (`S = N(α) ∖ {α}` and `S = D8`) are closed for all `m` in #2639 §0 / PUNCTTHEORY §2.3 and are not part of this reduction.
* **Monotonicity in `P`** (#2639 §2.1): `P` enters only through `|S| ≤ P` and the option filter `|e| ≤ P` (options inclusion-minimal); the lower bounds `q_γ ≥ k` involve `S` only. So UNSAT at (`P = 53, k = 6`) covers every `48 ≤ p ≤ 53`, UNSAT at (`P = 56, k = 17`) every `54 ≤ p ≤ 56`.
UNSAT of both families ⇒ Lemma G holds, `rank N = 8`, `m ≥ 8`, and M8 closes the case. ∎

## 3. The two SAT families (RECORDED; sampled CHECKED)
Variables `S_t` (120 lines). Clauses: `|S| ≤ P` (sequential counter); every orthogonal 8-frame (2,025) contains an `S` line; `q_γ ≥ k` for all 120 roots (own sequential counter; `q_α ≥ 16` for the E7 type); for every live outside line `s` some option `e ⊆ S`, where the options of `s` are the inclusion-minimal sets `s^⊥ ∖ F′` over rank-7 flats `F′ ∋ s` with `|e| ≤ P` (equivalently the complements of the 8,821 rank-6 sections of the E7 `s^⊥`, sizes 27–53; `sat/opts.py`).

**Orbit tree** (`sat/middrv.py`): the `W_J`-orbits `O_1, O_2, …` of outside lines (`W_J` = stabiliser of `F*`), largest first. Every model has a first `i` with `O_i ⊄ S`; WLOG `s_i = min O_i` is live and its option `e` is an orbit representative under `Stab_{W_J}(s_i)`. Leaf `(i, e)`: units `T = O_1 ∪ … ∪ O_{i−1} ∪ e ⊆ S`, `s_i ∉ S`. `|T| > P` is refuted by counting. Each other leaf is written **directly** as a CNF (`T`, `¬S_{s_i}`, the clauses above, options with `|T ∪ e′| ≤ P` only — sound since `T ∪ e′ ⊆ S`), solved by kissat `--no-binary`, and checked by drat-trim against exactly that CNF (≤ 540 s). Leaves that did not finish in 20 minutes are split symmetrically (largest orbit of the stabiliser of the leaf: branch "orbit ⊆ S", or a new live line with options up to its stabiliser; depth ≤ 4). Every heavy run was capped at 20 min wall and resumed from the state file.

**Results** (`data/states/T{t}_P{P}_k{k}.json`, per-leaf tables `data/tables/*.tsv`, run summaries `data/summaries/`): all 8 types UNSAT-VERIFIED for both families, no SAT, no TIMEOUT / UNVERIFIED entry. Counted by `c1`:

| type `t` | `P=56, k=17`: verified entries / counting / split nodes | `P=53, k=6`: verified / counting / split |
|---|---|---|
| 0 | 125 / 0 / 2 | 44 / 0 / 0 |
| 1 | 305 / 83 / 3 | 112 / 0 / 0 |
| 2 | 561 / 187 / 5 | 397 / 187 / 3 |
| 3 | 1373 / 544 / 8 | 1119 / 558 / 8 |
| 4 | 1027 / 375 / 6 | 858 / 376 / 6 |
| 5 | 575 / 183 / 5 | 397 / 183 / 3 |
| 6 | 238 / 56 / 4 | 81 / 0 / 0 |
| 7 | 60 / 7 / 2 | 19 / 0 / 0 |
("verified entries" include split parents, which are verified through all their children.) Wall time of the runs: about 2.5 CPU-h per family, Oct 15.

**Soundness checks.** `c2` (CHECKED): the counter agrees with brute force on 1,800 assignments; the leaf CNF with all 120 `S`-variables fixed agrees with a direct numpy test (`|S| ≤ P`, `q_γ ≥ k`, frames hit, every live outside line bad by a rank test) on 440 sets for (type 7, `P = 56, k = 17`) and 440 sets for (type 7, `P = 50, k = 0`, no `α` bound; 40 of them SAT, from the non-spanning family `N′(α) ∖ C`, so the check is not vacuous). An independent Sonnet audit of the driver found no soundness bug (card statement, not shipped); one hygiene fix (a cached leaf is reused only if `T` and the live set match) is in `sat/middrv.py`.

## 4. What `verify.sh` does, and does not do
`verify.sh` (≈ 15 min on one core, `nice 10`, sequential): step 0 manifest + pins; `c1` the tallies above, leaf-table row counts and the arithmetic of §2; `sat/opts.py` rebuilds the option sets of 4 of the 8 types (types 7, 0, 6, 1) from scratch (E8 lines, the 440,880 rank-7 flats, W-orbits); `c2`; then for each of those 4 types and each family `scripts/replay.py` (a) checks **all** counting leaves (`|T| > P`), (b) regenerates a spread sample of 60 leaf CNFs from `(T, live)` and compares the **md5 recorded when the original run solved them** — the md5 of a CNF depends on the exact option set and its order, so agreement validates the rebuilt options end to end — and the sha256 pinned in `evidence/sample_cnf_sha256.tsv`, (c) re-solves a spread sample of 15 leaves (kissat UNSAT + drat-trim VERIFIED), (d) drat-trims the **shipped DRAT proofs** (`evidence/proofs/*.drat.xz`, 3 small leaves per (type, family) for types 7 and 0; sha256 of proof and of CNF in `evidence/proofs/index.tsv`) against the regenerated CNFs. `c3_cover.py` (CHECKED) re-walks each orbit tree with `middrv.py`'s own `solve` logic (orbits, Schreier generators, option representatives, symmetric re-splits of the recorded split nodes) and an oracle `leaf()` answering from the state file: it requires that every leaf the walk reaches is recorded UNSAT-VERIFIED with identical `(T, live)` or is a counting leaf, that no restricted (chunk) leaf occurs, and that every recorded entry is visited; types 7, 0, 6, 1 by default, all 8 under `FULL=1`. `FULL=1` does (b) and (c) for **every** leaf of all 8 types and both families (hours; every kissat call is capped at 20 min).

**Not re-run by default / RECORDED:** the leaves outside the sample and the other 4 types' option sets; the tree coverage of the other 4 types (`c3` under `FULL=1`); the Case-B census behind M8 (in #2639: `evidence/punct/censusB4.py`, `data/logs/cB4_*`). The other leaf DRAT proofs (≈ 10⁴ files, tens of GB) are not shipped (the driver deleted them after drat-trim): for those leaves the verdict is **RECORDED**, pinned by the md5 of each leaf CNF in the tables; `replay.py` regenerates any CNF and proof on demand (`FULL=1` for all). `evidence/PUNCT-MID_THEORY_snapshot.md` is the card text as read (its status line for `P = 53` still says "running"; the finished result is in `data/summaries/` and `data/states/`).

## 5. Still open
`p = 47` with `m ≤ 7` (not claimed); `p ≥ 57`; any-`B` and masked factors for punctures; everything listed in #2639 §4 other than `m ≤ 7` at `48 ≤ p ≤ 56`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
