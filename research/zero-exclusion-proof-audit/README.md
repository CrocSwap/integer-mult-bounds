# Audit of PR1560's zero-exclusion theorem and its use in PR1616 / PR1650

**Corroborated; no gap found. No new bound, κ or rigidity claim.**

[PR1560](https://github.com/CrocSwap/integer-mult-bounds/pull/1560) (Andrey Mas / @an664, with GPT-6 Pro), head
`eb9f6f15`, proves in `proof.md` that three frame-incidence conditions (D), (G), (W) at a pivot frame F force
`a_ik b_ik = 4` on every live support (Theorem 1), and with nonempty blocks the gauge form `K = D(2G_L)D^{-1}`
(Corollary 2). It claims no independent human review. [PR1616](https://github.com/CrocSwap/integer-mult-bounds/pull/1616)
(`7b3e4624`) and [PR1650](https://github.com/CrocSwap/integer-mult-bounds/pull/1650) (`d960f8a2`) apply the
theorem at hundreds of different pivots to get rigidity on every P107, P106 and P105 unit, and cite it without
re-deriving it. This package audits that step. Pins are in [SOURCES.json](SOURCES.json).

## 1. Written audit of proof.md §2–§4 and §6

Every step was rederived over an arbitrary field E of characteristic zero. Nothing below needs order, symmetry or
nonzero entries.

| Step | Claim | Audit |
|---|---|---|
| §2 | `K = K[:,F]K[F,:]/4`; `Π_i` idempotent, trace 1, `Π_f = E_ff`, support in `T_i × T_i` | Holds: rank K = 8 = rank `K[F,F]`; `a_i·b_i = 16`; support from the zero entries on orthogonal pairs. |
| (4), (5) | `Σ_{i∈S} Π_i = I` for every live frame; `Σ_{i∈C} Π_i = E_T` | Holds: `A_S B_S^T = 16I` gives `A_S^T B_S = 16I`; (5) by completing C to the live frame `C ∪ (F∖T)` (fact E4 below). |
| (6) | `Σ_{i∈S} G_ik G_il = 4δ_kl` | Holds for every frame S and pivot F (E1). |
| §4.1 | `(Π_i)_kl = t_kl G_ik G_il` on `I_kl` | Holds: off-diagonal entry of (4) is zero, pivots contribute zero, edge rule `p_i + p_j = 0 = h_i + h_j` with `h = ±1`. |
| §4.2 | `(Π_i)_kk = 1/4 + Σ c_kl G_ik G_il` on `I_k` | Holds: the difference from `Π^0` vanishes on pivots (both are `E_ff`) and off `I_k`; (D) is a rank statement over Q, so it holds over E; the c_kl are unique because the seven h_kl are independent. |
| §4.3 | Hadamard rows; common quadratic `x² − x + q`; class sum 1; dichotomy; `w_j = ±1/2` contradiction | Holds. (10) uses only (7) on rows with support T, all in `I_kl`. The dichotomy is E7. The sign-product step is E4 + E6: the product of the three signs `s_{i0,l}s_{j,l}` is the product over T of `ε_{i0}ε_j`, which is −1 exactly for opposite classes. |
| §4.4 | every ordered `(k,l)` gets `c_kl = 0` | Holds: a witnessed block containing `{k,l}` gives both orientations, since either point can be the distinguished coordinate. |
| §6 | `t_kl t_lk = 1/16`, `t_kl t_lm = t_km/4`, `u_kl = g_k/g_l`, gauge form | Holds. 2×2 minors of the rank-one `Π_i`; each triple of pivots lies in exactly one block (E3), which is nonempty by hypothesis. |

**One expository omission, filled here.** §6 says "the pivot entries have the required form" without the
calculation. With `a_ik = δ_i ε_ik g_k`, `b_ik = 4ε_ik/(δ_i g_k)`, `a_f = b_f = 4e_f`, `d_i = δ_i/2`,
`d_f = 1/g_f`: `K_if = a_if = δ_i ε_if g_f = 2G_if d_i/d_f` and `K_fi = b_if = 4ε_if/(δ_i g_f) = 2G_fi d_f/d_i`;
pivot–pivot entries are `4δ_ff' = 2G_ff'`. So the corollary holds as stated.

## 2. Finite facts the proof uses implicitly, at every pivot

PR1560's checker establishes its premises only for its own pivot. The proof also uses E8 facts about lines
relative to F that it never states as hypotheses. [verify.py](verify.py) was written from the prose only (it does
not read PR1560's, PR1616's or PR1650's code) and checks them exactly at **all 2025 frames** as pivot:

- **E1** `2v_i = Σ_{k∈F} G_ik v_k` for every line (gives (6) and `Σ_k G_ik G_jk = 2G_ij`);
- **E2** pivot rows are `2δ`; every nonpivot row has `G_ik ∈ {0, ±1}` and `|T_i| = 4`;
- **E3** exactly 14 supports, 8 lines each, forming a Steiner system S(3,4,8) on F;
- **E4** the sign product splits each block 4 + 4; classes are mutually orthogonal, opposite classes have
  `G = ±1`, and each class plus `F ∖ T` is a frame (needed for (5));
- **E5** the class rows `(1, s_i)` are Hadamard for every distinguished k;
- **E6** for every block, class, k, exceptional row `i0` and opposite-class line j (3,628,800 configurations), the
  sign product is −1 and the predicted `w_j` is ±1/2, never a root of `x² − x`;
- **E7** four values in `{x, 1−x}` with sum 1 are all 1/4 or a permutation of `(1,0,0,0)`;
- **E8** the identity `Σ_k ε_ik ε_jk = 2G_ij` used for nonpivot pairs in §6.

All hold at every pivot. Controls: a non-frame pivot fails; removing one class-completion frame is caught by E4.
An illustration (an identity, not a rejection control) shows that a same-class "witness" gives `w = 1`, so
opposite parity is what forces the contradiction.

## 3. Binding to PR1616 / PR1650

Reading both `criterion` functions against §3: the pivot must be a frame inside `L = P112 ∖ X`; ScripS is all
live frames; supports must have size 4; all 14 blocks must be nonempty (tested before (W), so the code demands the
Corollary 2 premise for Theorem 1 too, which is stronger, not weaker); (W) asks for one class with 4 live lines
and a live line of the other; (G) builds the graph on `I_kl` with an edge exactly when a live frame meets `I_kl`
in two points and requires one component; (D) requires the seven `h_kl` independent (rank 7 modulo a prime) and
the deduplicated incidence rows to reach rank `|I_k| − 7` modulo the prime, a lower bound over Q whose matching
upper bound is the seven kernel vectors. Their kernel membership is identity (6), which both verifiers check
for all 2025 frames as `Σ_{i∈S} v_i v_i^T = 8I`. Classes by sign-parity are the orthogonality classes (E4). I
found no mismatch.

[binding_crosscheck.py](binding_crosscheck.py) compares PR1650's `criterion` with a second implementation from
§3's prose that uses different exact methods: classes by orthogonality, Q-rank of the integer Gram matrix `MᵀM` by
Bareiss elimination, and BFS. PR1650 stops at its first failing test (support, blocks, (W), (G), (D)); the cross-check
requires the same first failure, or a pass when all four hold. Results (Python 3.12, 2026-10-14 02:00 EDT,
PR1650 at `d960f8a2`), all **agree**:

| Run | Cases | Pass | (W) | (G) | blocks | (D) |
|---|---:|---:|---:|---:|---:|---:|
| `--samples 1000`: fixtures, 1000 random 5–10-line deletions with a random live pivot, every live frame of five random 7–10-line deletions | 4354 | 4019 | 334 | 0 | 0 | 1 |
| `--samples 1500 --thin`: fixtures, random 11–40-line deletions | 1503 | 246 | 1252 | 2 | 2 | 1 |

The fixtures are PR1560's positive fixture (passes), its `X_bad` control (fails (W)), and session 13's
full-family (G)-without-(D) pivot from #1502 (fails (D) in both). Because PR1650 stops at its first failure, this
compares (G) and (D) verdicts only where every earlier test passed. That is thin for (G) and (D): two cases and one distinct case (the same fixture in both runs).


Part 3 is a same-account check: PR1616/PR1650 were earlier Claude sessions on this account. Parts 1 and 2 do not
depend on that code.

## Not covered

- PR1212 §8 (the copy floor from gauge rigidity) and §10 (stabiliser transport of units). The floors 59/58/57
  claimed by PR1616/PR1650 also need those.
- The finite premises at PR1616/PR1650's units, beyond the cross-check sample (their own verifiers replay them).
- Whether (G) implies (D) (session 13's claim in #1502).
- Proof-assistant formalization.

## Reproduce

```sh
python3.12 -I -B research/zero-exclusion-proof-audit/verify.py          # about 50 s; 3.10+
python3 scripts/research_package.py --package research/zero-exclusion-proof-audit --check-only
python3.12 scripts/research_package.py --package research/zero-exclusion-proof-audit
# Cross-check (needs PR1650's verify.py at d960f8a2, not on main):
git show d960f8a2:research/complex-rank8-rigidity-p105/verify.py > /tmp/pr1650_verify.py
python3.12 -I -B research/zero-exclusion-proof-audit/binding_crosscheck.py /tmp/pr1650_verify.py --samples 1000  # needs 3.10+ (int.bit_count)
```

## Open next questions

1. **PR1212 §8 binding.** Does the floor lemma consume exactly Corollary 2's conclusion on `L = P112 ∖ X`,
   with PR1212 §10's transport? It matters because PR1616/PR1650's floors need it. First step: state §8's
   hypothesis next to Corollary 2's conclusion. Not started here.
2. **Formalization.** The §4.3 local step (Hadamard class, common quadratic, dichotomy) is small enough for Lean
   over a characteristic-zero field, with E1–E8 as finite lemmas. Blocked by the lack of a Lean E8 model with
   these line IDs.

## Credit

Theorem, proof and fixture: Andrey Mas (@an664) with GPT-6 Pro (PR1560). Applications audited: PR1616 and PR1650
(Josie Elliston with Claude). Predecessors credited by PR1560: Brett Halligan / @burntout76 / Ninefold (PR1212),
@DreamingOfClouds (PR717), @themilkman216 (PR968). This audit: Josie Elliston with Claude Opus 5.5 (Anthropic) via
Claude Code; substantial AI assistance. Apache-2.0.
