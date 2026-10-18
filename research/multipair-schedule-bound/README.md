# Multi-pair schedules cannot beat the nine-stage template (Theorem S; no new κ)

**Research note: a proved scheduling bound and a priced negative result. No κ claim; the selected record is unchanged.**

The B_K schedule has two conventions that no PR has varied:

- rule-table row 13 of [format-limits-corrected](../format-limits-corrected/README.md): one `(X, Y)` bank pair per local-word invocation;
- row 5: the pairwise signed exchange ρ.

The format-limits ceiling theorem explicitly does not cover non-B_K schedules. This package closes that gap for the complex supplier's economics:

- **Theorem S (proved).** Take any schedule of shear-type local words with `s` stages over `K` bank pairs. It needs at least `N ≥ 2K + ⌈2K/(s − 1)⌉` local-word invocations ("pair-calls").
  - Any number of pairs may run in a stage, with either orientation.
  - Bridges may be arbitrary block-diagonal maps.
  - ρ may be any pair-level signed exchange.
  - Calls need not be pair-aligned.
  - It generalises [cross-shear-stage-bound](../cross-shear-stage-bound/README.md), which is the case of one rank-`v` call per stage.
- **Consequence.** Per port, `D/W ≤ 1 − (cst/v)·s/(s − 1)`. Every schedule with `s` stages is dominated port for port by the B-template at the same `s`.
- **Attainment at odd `s`.** Parallel borrowing chains attain the bound, checked by exact replay. Their per-port profile is the B_K profile.
- **Priced on the T74 local words** of PR #1800, the current top open claim:
  - the best attained schedule reproduces its complex exponent `b = 0.001679754956125544521335` exactly and does not beat it;
  - `s = 7` hits the hosting wall;
  - `s = 11`, `13` and `15` lose 1.40%, 3.71% and 6.46% of `b`.
- **The only unexplored room is even `s = 8`.** Even if Theorem S were attained there, it is worth at most +0.26% (window-aligned idle children) or +0.70% (packing-ceiling relaxation). See the [s = 8 open question](#open-next-questions).

This answers the "is the one-pair-per-invocation convention costing anything?" side of the [coverage-law-change](../../docs/research/agent-task-catalog.json) card. The card's main question, two unpaid coordinates per family, is not addressed; the [TASK.json](TASK.json) scope change says so.

## 1. What the spec requires, and two pairs in one call

- **The contract.** `upstream/build/sections/04-swap.tex:105-123` gives:
  - `W` wires and pointwise gates inducing a permutation ρ;
  - one frame per gate, common to its wires;
  - cost `Σ_e rank(M_head − M_tail)` with `M_out(ρ(w)) − M_in(w) = I_m`.

  The recursion (`:197-211`) charges one recursive call per unit of edge rank. "Invocation", "bank pair", "stage" and "local word" are construction-layer notions. The paper's instance is the three-stage exchange per pair (`03-motifs.tex:89-100`, ρ at `:628`).
- **Two pairs in one stage are legal.** Two local words on disjoint pairs touch disjoint wires, and every gate keeps its common frame.
  - Concurrent calls share the stage's 8-dimensional window, as the replicas already do. So `m = 1 + 8s`. This is the reading most favourable to the lever.
  - A stage may also mix orientations. After bridges it is `[[I, H], [E, I]]` with `HE = EH = 0`.
- **Each pair keeps its own centre path and helper network.**
  - A local word's eight rank-8 centre copies (`cst = 64`) carry the eight decoder totals of its own 112 sources.
  - Two pairs active together hold independent coordinates. Their 16 totals are independent functionals, and each copy pays at least its pairing rank (star floor, format-limits row 8).
  - Fusing two pairs on the same labels gives a degenerate-label unit. format-limits Lemma Q (C.4) dominates it by its quotient.
  - So every pair-call pays the full per-call profile.
- **Difference from centre-sharing PRs** (#1708, #1748, #1791, #1829, #1838). Those reuse one call's centre values in a *later* call on related data. Pairs in the *same* stage share no data, so a multi-pair invocation opens no new sharing route.

## 2. Theorem S

**Model.** This is the pair-level model of cross-shear-stage-bound, tensored with `I_v`.
- The state is `M_t ∈ GL_2K(F)` over any field.
- Bridges are arbitrary invertible block-diagonal maps.
- Stage `t` is `[[I, H_t],[E_t, I]]`, with cost `c_t = rank E_t + rank H_t` pair-calls.
- The goal is `M_s` block antidiagonal. Any pair-level signed ρ has this goal.

**Theorem S.** `N := Σ_t c_t ≥ 2K + ⌈2K/(s − 1)⌉` for every `s ≥ 2`.

*Proof.*

**Setup.**
- Let `P_t, Q_t` be the row spaces of the top and bottom block rows of `M_t`. Bridges preserve them.
- Let `X = F^K ⊕ 0` and `Y = 0 ⊕ F^K`. The start is `(P, Q) = (X, Y)`; the goal is `(Y, X)`.
- A stage maps `P_{t−1}` to `P_t = {p + ψ_t p}`, where `ψ_t: P_{t−1} → Q_{t−1}` has `rank ψ_t = rank H_t =: h_t`.
- It maps `Q_{t−1}` to `Q_t = {q + φ_t q}`, where `rank φ_t = e_t`.
- Put `a = dim P∩Y`, `β = dim P∩X`, `σ^P = K − a − β ≥ 0`.
- Put `d = dim Q∩X`, `γ = dim Q∩Y`, `σ^Q = K − d − γ ≥ 0`.

**(i)** `P_t ∩ Q_{t−1} = 0`: if `p + ψp ∈ Q_{t−1}` then `p ∈ P_{t−1} ∩ Q_{t−1} = 0`. So `P_t∩Y` and `Q_{t−1}∩Y` are independent in `Y`, giving

  `a_t ≤ K − γ_{t−1} = d_{t−1} + σ^Q_{t−1}`.

Symmetrically, `d_t ≤ a_{t−1} + σ^P_{t−1}`.

**(ii)** `ker ψ_t ⊆ P_t ∩ P_{t−1}`, so `dim(P_t∩P_{t−1}) ≥ K − h_t`. This gives `a_t ≤ a_{t−1} + h_t` and `β_t ≥ β_{t−1} − h_t`. Hence

  `σ^P_t ≤ σ^P_{t−1} + w^P_t`,

with waste `w^P_t := h_t − (a_t − a_{t−1}) ≥ 0`. The same holds for `Q`.

**(iii)** Telescoping `a` and `d` from `0` to `K` gives `N = 2K + W`, where `W = Σ_t (w^P_t + w^Q_t)`.

**(iv)** By (i), `a_t + d_t ≤ a_{t−1} + d_{t−1} + σ_{t−1}`, where `σ = σ^P + σ^Q`. We have `σ_0 = 0` and `σ_u ≤ W`. Summing over `t = 1..s` gives `2K ≤ (s − 1)W`. ∎

The proof does not use `HE = EH = 0`. Replacing `K` by `Kv` gives the port-level statement. With one rank-`v` call per stage (`N = s`), it recovers `s ≥ 2K + 1`.

**Corollary.** Per replica, `W = 2Kv` ports, `m = 1 + 8s` and `D = W − cst·N`. So per port:
- `D/W ≤ 1 − (cst/v)·s/(s − 1)`;
- the active climb mass is at least `16s/(s−1)`;
- the helper demand is at least `(s/(s−1))` times the per-call helper width per port;
- idle capacity is correspondingly at most its B_K value.

These are the B_K values at `s = 2K + 1`, so (Dfc) becomes an inequality for every schedule. Each extra call at fixed `m` lowers `D` and replaces idle children by local children. So the packing ceiling decreases in `N/W`, and pricing at the bound dominates every schedule with `s` stages.

## 3. Attainment and searches

- **`chains_replay.py` (exact rationals).** It runs `t` borrowing chains `B_k` side by side, in either orientation, with `s = 2k + 1` and `K = tk`.
  - This gives `N = 2K + 2K/(s−1)`, exactly the bound.
  - Seven schedules replay to the exact signed exchange, on random data and on every unit vector. They include `B_4 ‖ B_4` with every stage mixed (rank 2v), unequal `B_4 ‖ B_3`, and three parallel full-rank 3-shears.
  - `B_4` alone reproduces format-limits (Sch): idle windows `{8: 6, 16: 4, 32: 4, 48: 4}` per port.
- **`sched_search.py` (exhaustive over GF(2), states up to bridges).**
  - The pruning uses `Φ = 2K − a − d`, which falls by at most a stage's cost (proof step (ii)), so it is admissible.
  - For `K = 2`, with mixed or alternating stages, the minimum `N` over schedules with at most `s` stages is `6, 6, 5, 5` for `s = 3..6`. That is exactly the bound.
- **`K = 3, s = 4` (the smallest even case).** Equality `N = 8` would need `σ_1 = σ_2 = σ_3 = 2`. That forces stage 1 to cost exactly 2 and every later stage to be waste-free.
  - Restricted to at most one word of each orientation per stage (`--maxrank 1`), no such schedule exists (`search/K3_s4_N8_equality.json`). `diag_equality.py` locates where the pattern dies (`search/K3_s4_equality_diagnostic.txt`).
  - Without that restriction, the exhaustive equality search over all 2,051 stage shapes (`search/K3_s4_N8_equality_full.json`) also finds **no schedule**. So the bound is not attained at (K = 3, s = 4), and chains (`N = 9`) are optimal there.
  - The same tool finds the chain value `N = 8` at `s = 5` (`search/K3_s5_N8_rank2_wastefree.json`).
- **`lemma_check.py`.** It independently checks inequalities (i), (ii) and the waste bound on 10,697 random stages over GF(2), GF(3) and GF(5), with K up to 4. Two false strengthenings must fail and do: (ii) with `h − 1`, and (i) without its σ term.

## 4. Prices on the T74 words

`inputs/T74-WORDS.json` holds an extract of PR #1800's provider registry (`research/capped-fusion-t74-k554/new/PLAN.json` at `46d865ab`; blob and SHA256 pinned inside):
- the two local words' per-call paid profiles;
- their helper-width histograms;
- the 417/249 call split.

The verifier recomposes the published global profile from it exactly and reproduces the T74 complex endpoint with the retained moment engine. Each family is then priced with the same engine and with [ceiling.py](../complex-local-word-ceiling/ceiling.py).

| id | schedule | s | K | N | m | D/replica | b (exact lower) | vs T74 |
|---|---|---|---|---|---|---|---|---|
| F00 | B_3 (any parallel B_3 chains) | 7 | 3 | 7 | 57 | hosting wall (helpers 26 156 > idle 25 088) | none | wall |
| F01 | B_4 = T74 (any parallel B_4 chains) | 9 | 4 | 9 | 73 | 320 | 0.001679754956125544521335 | 0 |
| F05 | B_4 ‖ B_4, every stage mixed (rank 2v) | 9 | 8 | 18 | 73 | 640 | 0.001679754956125544521335 | 0 |
| F06 | B_4 ‖ B_3 | 9 | 7 | 16 | 73 | 544 | 0.001610042388228235763691 | −4.15% |
| F02 | B_5 | 11 | 5 | 11 | 89 | 416 | 0.001656172228607112292838 | −1.40% |
| F03 | B_6 | 13 | 6 | 13 | 105 | 512 | 0.001617382665125020322085 | −3.71% |
| F04 | B_7 | 15 | 7 | 15 | 121 | 608 | 0.001571246396968943417717 | −6.46% |
| F07 | s = 8 by chains | 8 | 3 | 7 | 65 | 224 | 0.00159028683109454299811 | −5.33% |
| F08 | s = 8 **at the bound** (hypothetical), idle ≤ 40 | 8 | 7 | 16 | 65 | 544 | 0.00168419220807572539741 | +0.26% |
| F09 | same, idle at the guard R = 45 | 8 | 7 | 16 | 65 | 544 | 0.001691512754596525670768 | +0.70% |
| F10 | s = 10 at the bound (hypothetical) | 10 | 9 | 20 | 81 | 736 | 0.001676096670260698677048 | −0.22% |
| F11 | s = 6 at the bound (hypothetical) | 6 | 5 | 12 | 49 | hosting wall | none | wall |
| F12 | excluded: N one below the bound | 9 | 8 | 17 | 73 | 704 | 0.001950681375323732307036 | +16.1% (impossible) |
| F13 | excluded: two pairs, one centre path | 9 | 8 | 18 | 73 | 1216 | outside engine window | impossible (§1) |

Full identities, idle windows and packing ceilings are in `FAMILIES.json`, `profiles/` and `grader/`.

**What decides these numbers:**
- **The per-pair-call charge.** Each pair-call pays a centre path, about 3,736 of hosted helper width, and 1,792 active climbs.
- **Chain-seed waste.** Theorem S charges at least `2K/(s−1)` extra calls.
- **The hosting wall at `s ≤ 7`.**
- **Window growth at `s ≥ 10`.**

F12 shows what the bound rules out: a waste-free parallel schedule would be worth +16%.

## 5. Scope and limits

**Covered:** every schedule of shear-type local words on the T74 per-call profile under the coverage law `(m − 1)W + cst·N`. That includes:
- any number of pairs per stage;
- mixed orientations;
- unequal chains;
- calls that are not pair-aligned;
- arbitrary block-diagonal bridges;
- any signed pair-level ρ.

**Not covered:**
- even-`s` attainment beyond (K = 3, s = 4), where it fails;
- ρ through a third bank class, which changes the coverage law (the "two unpaid coordinates" lever);
- a local word that is not a shear;
- a frame-checker replay of mixed-orientation stages (their legality is argued in §1).

**Assumptions:**
- the stage window is shared by concurrent calls;
- idle mass is packed at the stated rank cap;
- in the hypothetical families, Theorem S is attained.

The T74 profiles are PR #1800's. Its construction is not re-verified here.

## Reproduce

From the repository root (standard library only):

```sh
python3 -B research/multipair-schedule-bound/verify.py      # PASS_MULTIPAIR_SCHEDULE_BOUND, about 30 s
python3 scripts/research_package.py --package research/multipair-schedule-bound
```

Longer searches whose committed outputs are not rerun by `verify.py`:

```sh
python3 -B research/multipair-schedule-bound/sched_search.py 3 8 4 --maxrank 1 --wastefree-after-1   # ~6 min
python3 -B research/multipair-schedule-bound/sched_search.py 3 8 4 --wastefree-after-1               # unrestricted, ~1 h
python3 -B research/multipair-schedule-bound/sched_search.py 3 8 5 --maxrank 2 --wastefree-after-1   # ~23 min
python3 -B research/multipair-schedule-bound/diag_equality.py 3 4
```

## Open next questions

- **Is Theorem S attained at even `s`?** Only `s = 8` could pay, by at most +0.26% to +0.70%, and only with exact attainment: one extra pair-call per 35 pairs costs about 3.4%.
  - The first open instance is `K = 4, s = 4` (bound 11, chains 12). It needs orbit reduction under GL(X)×GL(Y) or a compiled search.
  - A proof that even `s` is never better than `s − 1` would close the lever.
- **ρ through three bank classes.** Can a cycle `X → Y → Z` leave more than one unpaid coordinate per family? This is the levers.py "two unpaid coordinates" budget (×3.77), not a scheduling question.

## Credit

- Theorem S generalises the stage-count proof in [cross-shear-stage-bound](../cross-shear-stage-bound/README.md) and the archived borrowing-chain campaign it audits.
- The rule table, (Sch)/(Dfc) and Lemma Q are from [format-limits-corrected](../format-limits-corrected/README.md).
- The packing ceiling is [complex-local-word-ceiling](../complex-local-word-ceiling/README.md).
- The T74 words and profile are from PR #1800 (jeremykothe2) and its lineage, credited in that PR: PR1625 (mdumitrean), PR1661 (midhatn), PR1319/PR1297 (rohanarun), and others.

Prepared by themilkman216 with substantial Claude (Anthropic) assistance. The investigation was run as parallel fresh-context research branches. Apache-2.0.
