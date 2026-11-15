# P104 follow-up: κ(k) caller law, cut/pocket lemmas, radix-3 and spec-challenge results, CLEAR-content freedom (no κ)

This package follows up #7606 (`research/p104-odd-unit-per-grading`), #7607 (`research/p104-toolkit-v3`) and #7608
(`research/p104-dual-scan-drop-902`). It collects the results our lanes logged after #7606 shipped. Nothing that is
already in those three PRs is repeated here. Where we build on them, we cite them.

It makes **no κ claim** and ships no word. The base word is ToikY's #7546 (κ 0.003648411294790). At the time of
writing, the frontier is aliromman's #7605 (κ 0.0036504442446), and our #7608 (κ 0.00365074956598) is conditional on
one CLEAR-content premise. §1 below discharges that premise.

Tags:

- **[P]** proved in [PROOF.md](PROOF.md).
- **[C]** exact computation, re-run by a checker in this package.
- **[C-lane]** exact computation by our lane code. The number is reported, but CI does not re-run it.
- **[C-param]** priced by our invoice tool PRICEKIT (`pricekit.py`, shipped in #7607). Its control reproduces #7546's
  κ and S = 1424.
- **[N]** numerical.
- **[S]** judgement.

Nothing tagged [N] or [S] is claimed as a result. A network-compiler effort (recompiling the helper layer from
requirements) is still in progress, and **nothing from it is claimed here**. Lanes that have not finished are listed
as in progress, with no claim.

## Summary

| # | result | tag |
|---|---|---|
| 1 | Under `owned_erasure`, the content of a lossless owned CLEAR is free, and every CLEAR of an endpoint-exact word is lossless. This discharges #7608's premise and answers the clear-form-gap package's Q1 with YES, with exact certificates | [P, C] |
| 2 | The compiler hypothesis r_max < k_min is not a gap. It applies after strictification, and the gate passes for #7546, #7605 and #7608 | [C] |
| 3 | t = −1 toys: the F₂³ toy is decided by two independent proofs, and every F₂⁴ climb-(n−1) survivor is refuted by the new Pocket Lemma | [P, C / C-lane] |
| 4 | On P104, 8 owned hubs realise the cut floor M = 72, so the conjecture "M ≥ n at t = −1" is false in the frame model. Hubs still do not pay: the V-funnel lemma forces a public y → X layer of rank ≥ 96 | [P, C-lane, C-param] |
| 5 | Callers: the Crossing and Floor Lemmas. B (#7113) is optimal among nested two-arm layouts. A junk role is a disguised ρ = 3 root. ρ ≥ 3 gains nothing. β = 4g + 2. Nesting is proved at the outermost and innermost stages only | [P, C, C-param] |
| 6 | Decoders: the residual identity gives C ≥ n for odd-denominator networks and C ≥ 16 at half level. The h = 10 decoder costs 57. Neither 1/3 nor fooling sets nor lifted labels go below 56 | [P, C, C-lane] |
| 7 | Shape and framework: κ is bounded in k, h and v. Self-application gives Δκ = 0 exactly, and one outer level is optimal. Slot knobs are a single compile number | [P, C-param] |
| 8 | Radix 3: A12 (binary radix) is the only over-conservative clause found. Endpoint wrappers exist in odd radix, but Lemma Z keeps the per-port +1. The radix-3 decoder target is H, so 3-integral decoders cost ≥ v = 112, and no radix-3 route crosses | [P, C, C-param] |
| 9 | Negatives: no resonance in any knob, no non-linear op, single-step anchors illegal, no usable symmetry, no new cut floor, and the dual scan rediscovers #7603–#7605 | [P, C-lane, C-param] |

## How to verify

```
python3 -I -B research/p104-follow-up-findings/clearform.py  # §1 CLEAR certificates                 PASS_CLEARFORM
python3 -I -B research/p104-follow-up-findings/sepgate.py    # §2 strictification gate              PASS_SEPARATION_GATE
python3 -I -B research/p104-follow-up-findings/toy4.py       # §3 F2^3 decision, controls           PASS_TOY4_DECISION
python3 -I -B research/p104-follow-up-findings/labels.py     # §4, §6 E8/P104 label facts           PASS_LABEL_FACTS
python3 -I -B research/p104-follow-up-findings/oddradix.py   # §7, §8 forms, wrappers, Lemma Z      PASS_ODD_RADIX
python3 scripts/research_package.py --package research/p104-follow-up-findings
```

- All checkers use the standard library only and finish in minutes.
- Each has positive and negative controls, listed in [VERIFY.json](VERIFY.json).

---

## 1. Owned CLEAR content is free (CLEARFORM)

| statement | tag |
|---|---|
| **Rank lemma ⇒ lossless.** Every event except CLEAR keeps the live rank, and a CLEAR lowers it by at most 1. An invertible endpoint forces rank n throughout, so **every CLEAR of an endpoint-exact word is lossless**. "Lossless" is implied by correctness; it is not an extra premise | [P] PROOF 1.1 |
| **Content theorem.** The retained contract behind `owned_erasure` has six clauses (E1–E6 in PROOF 1.2, each quoted with file:line). None names, limits or prices the erased value. So two endpoint-exact words with identical owned INIT/MOVE/CLEAR events either both satisfy the contract or both fail it, and pay identical erasure cost. The κ invoice and the strictification gate take no CLEAR input | [P] PROOF 1.2 |
| **#7608, CLEAR #44** (owned 1557, chart 595). The new row {451: −1, 1495: 1} is an exact Q-combination of 21 live rows (other live rank 1501 = n_pub). #7605's row is the same combination plus −3/2·(x902 + x985). The other 73 CLEARs are identical in the two words, and both endpoints have rank 1501 | [C] |
| **Swarm Q1** (`research/p104-6372-clear-form-gap`, README Q1). CLEARs 17755 (role 780) and 17756 (role 779) of the pinned candidate are lossless, each with an exact 97-term certificate (other live rank 770 = n_pub). Q1 resolves YES, subject only to the chronology clause E3, which is a field-identity check | [C, P] |

Scope:

- Owned fields only. Zeroing a public register without a live owned holder is a genuine loss.
- The result fails in a reversible-uncompute model, which the retained contract (E5) says it is not.
- [S] The contract is spread over retained notes. A maintainer could adopt a stricter "frozen content" reading, but no
  quoted clause supports it. The selected BIT admission itself has 237 of 237 nonzero erasures.

Consequence for #7608: its premise reduces to `owned_erasure` as written, with nothing extra [P + C]. The ruling stays
with the maintainers.

## 2. The separation hypothesis is not a gap (SEPAUDIT)

- **The flag.** Our PROFILECHK lane flagged that FINITE-PRECOMPILATION.md:51-52 requires r_max < k_min, while the
  #7113-caller invoices have r_max = 64 and k_min = 1.
- **The scope.** The condition applies to the **strictified** unit fed to the compiler. The selected #7000 record
  states that its raw invoice fails the condition and then strictifies it (c = 11, b = 12, u = 1/7, v = 1920;
  `interval_gate.py`) [P, quoted in PROOF 2].
- **[C] `sepgate.py`.**
  - The #7000 control reproduces FULL-RESULT.json's γ and δ.
  - #7546 gives γ 0.940836, δ 0.908148; #7605 gives 0.940920, 0.908149; #7608 gives 0.940932, 0.908149. All are below
    31/32.
  - Each kappa root matches its published κ.
  - Negative control: paid mass of rank ≥ 16 scaled by 1.10 fails the gate.
- **[C-lane]** #7601 gives γ 0.940861, δ 0.908148.
- **Verdict.** No contributor result is affected.

## 3. t = −1 closures: toys

The model is the WEBS toy: U-only targets, any helpers, owned ascents. The web-general Cut Lemma (WEBS, an
outside-session lane of Mason's) shipped in #7606 §I.3, and #7606 listed the F₂³ question as open.

| result | tag |
|---|---|
| **F₂³ decided.** Labels 1, 2, 4, 7. There are 8,261 owned multisets of climb 3 and 460 up-sets. 13 sets pass every cut, and all 13 are infeasible for any number of helpers. Owned climb ≥ 4 = n is needed. The 4-feeder control is realised exactly. Labels 1, 2, 7 at climb 2: the only cut-feasible set is also refuted. The Charge Corollary is not vacuous: it blocks 240 of the 2,074 cut-feasible climb-4 sets and leaves the 4-feeder set alone. The duality map permutes the 13 climb-3 sets | [P, C `toy4.py`] |
| **Proof S2** (outside-session, Mason's): the Pin Lemma, the time-cut basis and the Down-set No-Loss Lemma (DNL) give the **Charge Corollary**. The DNL hypotheses are necessary: violating them, the finals still span on 1,448 random programs | [P] PROOF 3.1–3.4; [C-lane] |
| **Proof S1** (ours): the **Forwarding**, **Union** (multi-commodity cut) and **Duality** (O feasible ⇔ O^⊥ = {(b^⊥, a^⊥)} feasible, X ↔ Y) Lemmas. A brute-force certificate covers all 460 up-sets | [P] PROOF 3.6–3.8; [C-lane `cert3.py`] |
| On F₂⁴, cuts + Charge + dual Charge + Union decide every 3-port set and the 4-port types (0,2,2,2) and (1,2,2,3). The survivors are path type (8 per set) and two-disjoint-pairs type (32 per set) | [C-lane, CP-SAT up-set ILPs] |
| **Pocket Lemma** (TOY5, any helpers, descents allowed): o(G) + #(owned moves into the pocket N) ≥ \|R\| | [P] PROOF 3.9 |
| The Pocket Lemma refutes **every** F₂⁴ survivor (44 at 4 ports, 128 at n = 5) and every cut-feasible climb-(n−1) set tested (3,801 sets, including 3,044 at n = 5). The two proofs are complementary: Pocket kills the S2 survivors, 256 of 256 on {1, 2, 7, 11}. Controls: one feeder per port survives, and 1,381 of 2,074 F₂³ climb-4 sets survive, so the test is not vacuous | [C-lane, CP-SAT] |
| On P104 these lemmas do **not** give M ≥ 104. Every P104 port has 200 of its 255 planes free of non-partner labels, and on pure {0} → V hubs the Pocket Lemma collapses to the cut lemma (α = 8, M ≥ 72) | [C-lane; P] |
| An unfed port cannot piggyback on non-partners' private ascents ⟨q_s + q_d⟩ → ⟨q_s, q_d⟩ (geometry-free) | [P] PROOF 3.13 |

## 4. Hubs realise the cut floor but do not pay (HUBCLASS)

| result | tag |
|---|---|
| Index-coding hub construction: k direct hubs {0} → V plus one helper per partner cell give X_t = x_t − y_t, Y_t = y_t exactly, with no helper bound needed | [P] PROOF 3.10 |
| P104, 8 hubs, A = G/2: **exact, M = 72 < n = 104** (41,265 events, 4,992 partner-cell helpers). So the conjecture "M ≥ n at t = −1" (#7606, tagged [S] there) is **false in the frame model**. The cut floor 72 is tight, and the minimum hub count is exactly 8 | [C-lane exact replay] |
| G104 is the optimal fit: integer, rank 8, diagonal 2, 0 on all 5,720 odd cells, ±1 on all 4,992 partner cells; α = 8. P104 has an exact cover by 13 disjoint orthogonal frames | [C `labels.py`] |
| F₂⁴: two hubs are exact (M = 8 = n) on TOY5's sets and on all 8 odd labels, and one hub fails the cuts. Hub total climb is ≥ n on every F₂⁴ label set | [C-lane; P] PROOF 3.12 |
| **V-funnel lemma.** With k hubs as the only owned moves, the public y-content into V has rank ≥ n − k = 96, so a public y → X layer of rank ≥ 96 is forced. Hubs share only additive y → X delivery; on the park side the Clone lemma still needs owned rank ≥ 96 | [P] PROOF 3.11 |
| Price, with S = 1248: 1.0856× at the flag-free LP floor (U = 1,235, not a build), 0.8234× at U = 7,127 and 0.7175× at the best built U = 10,730. The hub crossing needs U ≤ 2,817 D0/call | [C-param] |

## 5. Caller theory

### 5.1 Two-arm callers

**Lemmas.** These come from CALLEROPEN (an outside-session lane of Mason's).

| result | tag |
|---|---|
| **Crossing Lemma.** Idle lines lose 4 dimensions at every witnessed boundary. B's caps (0, 2, …, 14, …, 2, 0) are attained exactly at all 15 non-centre boundaries, at q₀ = 1 and q₀ = i. This kills the outer-boundary bonus (1.1272 / 1.1109) | [P] PROOF 4.1; [C-lane `cap_check.py`, shipped in #7607] |
| **Floor Lemma**, under nesting: \|Z_k\| ≥ 2(k+1) + 2. It is attained by B at every non-centre call | [P] PROOF 4.2 |
| **B is optimal among nested two-arm, two-hub layouts** at ρ = 2, at 1.0950 / 1.0031 / 0.9773 (twins deleted / shadows / shadows + 2 relays). The majorisation step is at sketch level | [P] PROOF 4.3; [C-param] |
| A shared D across calls, or a D-dependent free op, is illegal, and SL holds anyway | [P] PROOF 4.4 |
| Multi-centre layouts force ρ ≥ 2c and lose: 0.9930 / 0.9050 / 0.8804 at c = 2 | [P] PROOF 4.5; [C-param] |
| Single-shear-call callers on W6805 (CubeJerry's #6805 native) price ≤ 0.9237× | [C-param] |

**Other layouts.**

| result | tag |
|---|---|
| **The junk role is a disguised ρ = 3 caller** (JUNKROLE, an outside-session lane of Mason's). Dilation identity: P = −(I − e_J ãᵀ)(I − b̃ e_Jᵀ). The J-stages vertex-cover K_{8,9}. The honest D-free junk (JF1) prices exactly at SINGLEHUB's ρ = 3 ceiling, 1.0739 / 0.9796 / 0.9532, below B. A D-scaled junk does not cross | [P] PROOF 4.6; [N]; [C-param] |
| **ρ ≥ 3** (RHO3CROSS). Relation dim ≤ ρ − rank(Σ witness Z_j), so δ = 1 is possible only at the two outer boundaries. This is tight on SINGLEHUB's ρ = 3 root: 13 inner boundaries at 0, both outer boundaries at 1. Best prices: ρ = 3 one-hub 1.0612 / 0.9685 / 0.9426; ρ = 3 two-hub 1.0153 / 0.9301 / 0.9062; ρ = 4 chain 1.0242. All are below B | [P] PROOF 4.7; [C-lane]; [C-param] |
| **Arm trees** (ARMTREE). Block rank bound (sketch): #roles meeting stage sets A, B ≥ 2·rank sgn(a − b), so interleaving in time costs shared roles. Two-hub two-piece layouts violate it (337 violations at L = 8). A 4-hub tree toy at k = 8 prices 0.59× B(8). Not closed as a theorem | [P sketch; C-lane; C-param] |
| **β = 4g + 2 = 34** (BETA): 2 uncancelled hubs (2g), arm tops (2g) and the interior (+2). The per-stage lift 8 = h − 1 is the F₂⁸ frame dimension. The hub degree k is forced. **The arm-top degree k/2 is forced only under nesting** | [P] PROOF 4.8; [C-param] |
| The prize if the hubs were split per arm (an illegal layout): +5.2% on shadows. Halving the lift is not available | [C-param] |

### 5.2 Nesting

| result | tag |
|---|---|
| **NESTPROOF.** Lemma S gives a semiseparable Gram. The outside-mask part B_k of the early x has dim b_k ≤ 2k − 2 and is the −1 eigenspace of the prefix (a reflection block). b_1 = 0, so the outermost stage is nested. The Floor bound weakens to \|Z_k\| ≥ 2(k+1) + 2 − b_k without nesting | [P] PROOF 4.9 |
| **NEST5.** Nesting is **not** implied by Lemma S + prefix commutation. A one-arm L = 3 solution with a dying role (b_2 = 1, \|Z_2\| = 7) is certified by Newton to residual 1e−69. It lies outside the two-arm Floor setting, so it refutes only "nesting is forced", not B's optimality | [C-lane, mpmath] |
| **DYINGEXACT.** The L = 4 two-arm dying-role layout is infeasible for every t ≠ −1 (rank/eigenspace proof). The nested B(4,3) control is built exactly | [P] PROOF 4.10; [C-lane] |
| **DYINGGEN Theorem 1.** At the innermost stage, for any arm length and any number of dying roles: c = −1 is forced and \|Z_{m−1}\| ≥ 2(m−1) + 4 − b. Lemma 2 adds \|E_{m−2} \ D\| − 1 when the top index is m − 2 | [P] PROOF 4.11 |
| **Still open.** Nesting at interior stages, b ≥ 2 and \|E\| ≤ 1. β = 34, and B's optimality beyond the nested family, rest on these | open |
| Non-nested layouts: no sliding-window layout passes the exact rank checks (L = 8: 7,162 / 61 / 2 violations at w = 1 / 2 / 3). If such layouts were legal, they would price 1.339 / 1.204 / 1.167 at w = 1 | [C-lane; C-param] |
| The float-solver evidence (dying-role two-arm L = 4: 0 of 114 starts against a 4% control rate; non-nested L = 4: 0 of 24) is [N], superseded where DYINGEXACT applies | [N] |

### 5.3 κ(k) law: extensions beyond #7607

The closed-form caller C(k), S(k) = 96k − 208, β = 2(2h − 1), κ* = 1/((2h − 1)k*), the Lambert-W k* and κ ~ ε/(β ln k)
shipped in #7607 §E1 (`kformula.py`). New here (KFORMULA, RES-REC):

| result | tag |
|---|---|
| Dimension families with the same optimal caller, g = h − 1, native D ∝ g: BW16 κ* ≈ 0.00184, BW32 0.00085, P104⊗P104 0.00046. So κ*(h) = Θ((1 − c/v)/(h log h)), decreasing in h. The native-∝-g scaling is a modelling assumption | [C-param; S] |
| The buildable layout sweep (1,422 layouts) peaks flat at L ≈ 16–17. L = 16 sits +0.02% above L = 17, which is model noise, and matches the exact optimum k = 17 | [C-param] |
| A positive limit κ_∞ = ε/α would need bounded-header callers joined by tree nodes. No theorem excludes them outside one nested root, and no construction exists | [S] |

## 6. Decoders

| result | tag |
|---|---|
| **Residual identity** (DECLIFT9, an outside-session lane of Mason's): Q[t, s] = Σ path descents b_j mod 2, one rank-1 term per unit descent, whatever the lifts and merges. Hence **C ≥ n = 104** for odd-denominator networks and **C ≥ 16** at half level (the DEC-only floor was 21). Checked on 800 random networks | [P] PROOF 5.1; [C-lane] |
| Lifted kept chains void the ADICWALL partial-replacement bound. Merge-only relays are legal and cheaper, but reach only ports that need neither chain. All 124,146 merge configurations cost ≥ 57 | [P; C-lane] |
| The caller op X_p → Y_p needs a paid descent (q·q = 1) | [P] PROOF 5.2 |
| **H10DEC.** On the h = 10 labels (P104 on 103 ports, port 88 → e₁₀), an exact decoder costs **57** (8 E8 rows with 88 zeroed, plus one climb-1 row). C_{h=10} = 1 + C(103), so the true minimum lies in [1 + floor(103), 57]. The ASYMPORTS c = 50 was a floor artefact. h = 10 stays killed at its gate G2 (U packing) | [C-lane; P] PROOF 5.3 |
| **MOD3DEC.** On F₂ labels, 1/3 is a 2-adic unit, invisible to the residual identity. There is no mod-3 identity, and rank-8 rows climb ≥ 7, so there is no sub-56 decoder over Z[1/6]. The "70 vs 68" figure belonged to the radix-3 world and was a MILP catalogue bound, not a theorem | [P] PROOF 5.6 |
| **QDEC.** The 3-adic graded bound equals the Q-rank bound (max s/r = 2, attained by A2⁴), so it adds nothing | [P] PROOF 5.7; [C-lane] |
| **FOOLSET.** Isolation and fooling sets are capped by rank_F₂ = climb (≤ 9), and they give lower bounds where the certificate lemma needs upper bounds. Nothing new | [P] PROOF 5.4 |
| **ODDGRAPH.** The odd (orthogonal) graph is SRG(120,63,30,36), of degree 55 on P104. Q has GF(2) rank 9 and real rank 104. There are 2,025 orthogonal 8-frames, each orthogonal pair lies in 15 of them, and 759 lie inside P104. 56 is not a graph degree: 56 = rank_R(G) × climb = 8 × 7 | [C `labels.py`] |
| Climb-1 all-odd rectangle covers need 104 terms | [P] |
| **LIFTDEC.** Under the lift (q, 1), the bare row law makes the decoder free: 13 frames give pairing rank 0, a sign the target became wrong. With nondegenerate owned frames, a clique row costs ≥ 2 dim W, so rectangle designs cost exactly 104. No sound sub-56 lifted decoder exists | [P] PROOF 5.5; [C-lane] |
| **XDEC** (already in #7606 I7) and the merge/relay families are not repeated here | — |

## 7. Shape and framework

| result | tag |
|---|---|
| **SHAPE.** The (log n)^{1−κ} is p transform bits per coefficient, in one outer level. The saving is the inner width recursion, with κ = a* − O(g). A growing compiled template has L(N) ≥ N^τ for every N, so a(N) ≤ a*: at most the ~1e−15 gap is recoverable | [P] PROOF 6.1 |
| The k-family unrepaid mass is μ = S/M_T = 0.0051 (k = 8), 0.0048 (17), 0.0025 (64), 0.0008 (256): μ = Θ(1/(gk)) | [C-param] |
| **BOOTSTRAP.** Theorem A: self-application gives Δκ = 0 exactly, since the binding rows make no multiplier call. Theorem B: one outer level is optimal, by concavity of x^{1−a*} | [P] PROOF 6.2–6.3 |
| Self-application is legal after small clause changes; the stack discipline at unbounded depth is unwritten | [S] |
| **SLOTKNOB.** a = 1 − ln(s/W)/ln m. At the frontier, m, W and s are one compile number N, and f enters only through constants. No slot knob exceeds 1.0× | [P] PROOF 6.4 |
| **MUCENSUS.** Over 5,246 archived words with ledger-matched callers, max μ = 0.0103. Bounded-header (projective-plane) families give 0.0038–0.0050, decaying. Naive C(17) pairings up to 0.12 are artefacts of mismatched ledgers | [C-lane] |
| **NEWFRAME.** The char-2 walls trace to A12 (binary addresses, F₂ labels, Z/4 phases). Radix is not in SPEC. Over F₂, the minimum number of vvᵀ summing to B is rank B, or rank B + 1 iff B is alternating and nonzero; in odd characteristic it is always rank B | [P] PROOF 6.5; [C `oddradix.py`] |
| Generalised Lemma E′: unipotent natives never reach equality, in any characteristic | [P] |

## 8. Radix 3 and the spec challenge

| result | tag |
|---|---|
| **SPECCHALLENGE.** Of the clauses our walls rest on, only A12 (binary radix) is over-conservative with a κ lever. A28 (ascending-only MOVEs) is over-conservative but worth ≈ 0. Exactness → formal ε is worth ≤ 0. The constant template is worth ≤ 1e−15. One slot per child, common frames at gates, A29 credit and exact owned restore are necessary | [P / Q] |
| **QUTRIT.** Lemma Q: no live plane is a λ-pseudo-reflection, in any radix. Exhaustive 2×2 monomial tables cover both radices | [P] PROOF 6.6; [C-lane] |
| **Endpoint wrappers** (SPECCHALLENGE, audited by WRAPAUDIT). In odd p, K_{v,c}^j = r·D_a·P_s·K_{v,c}·D_b for every non-isotropic v and j ≢ 0, with chirps D and an F_p address scaling P_s. The wrappers commute with K_u for u ⊥ v. There is no solution on isotropic lines. The one-sided gauge K² is dense | [P] PROOF 6.7; [C `oddradix.py`] |
| **Lemma Z** (O1SPLIT): if T₀ = 0 and Σo = m, every unit has rank u₀ = m − o. H3, live planes and QUERY are not admissible. So **the per-port +1 survives in odd radix for every exponent pattern**: joint_mono needs ≥ 37 per A port per word. Admissible units: QSELF, park1 and C3 swap planes | [P] PROOF 6.8; [C `oddradix.py`] |
| An independent read-only audit of Lemma Z found it sound. The m = 2 tables are complete over F₇ and F₁₃, and the m = 4 search covered 548,000 conjugates | [C-lane] |
| **SPLITK.** The split K/K⁻¹ contract is not legal as written (SPEC pins K^{⊗e} per role). This verdict stands, but its pricing argument was replaced: see Corrections | [P] |
| **C3NATIVE.** By the radix-3 det argument, o = 1 admissible units are illegal alone. The split swap diag(k, 1)·S·diag(k, 1)⁻¹ is legal (det R = 1, o = 2) and reaches m. Whether it supplies the contract's crossing is open | [P] PROOF 6.9; [C-lane]; open |
| **R3BUILD.** The radix-3 decoder target is **H**, not N: the net map is I, and side wires are lossless only between label-orthogonal ports. So every 3-integral radix-3 decoder costs **c ≥ v = 112**, for any labels and any odd radix, and no radix-3 route crosses. Break-even is c ≈ 66.7–68.5 at ρ = 2 and ≈ 70.9–72.6 at ρ = 1 | [P] PROOF 6.10; [C-lane; C-param] |
| **R3THIRD.** With 1/3 denominators Thm B is vacuous, not weak. What survives is rank_Q M ≥ 14 (full-support rows ≥ 112). M = (G∘G − J)/3 fits H with rank 36, costing 288 in the row model. The cheapest verified decoder is 14 orthogonal frames of P112, at 112. Nothing below 112 was built | [P] PROOF 6.11; [C-lane] |
| SWAPJ (the ρ = 1 crossing) was stopped as moot unless a decoder below 71 appears. R3TILE (cancelling tilings) is in progress, with no claim | in progress |

## 9. Other negatives (scoped)

| lane | result | tag |
|---|---|---|
| RES-REC / RES-PORT / RES-LAYER / RES-CONTRACT | No resonance. All knobs are smooth: at κ ≈ 3.6e−3, S and D enter additively. Sensitivity at the crossing: one owned unit = −1.126% κ = 284 D0/call; 500 D0 = 1.98%; fan-out 0.4% per 100 D0; skipping one climb step everywhere is worth at most +4.3%. The ratio is monotone in n, and +1 in h ≈ ×0.8. Break-even ΔS on all-B is 32.8 | [C-param] |
| RES-CONTRACT | Free natives are never involutive (tr R = 2(1 + 2t), R² = (tr R)R − I), so the involution clause of classes C / D′ needs a paid odd diagonal | [P] PROOF 6.12 |
| NONLIN | No non-linear ingredient is admissible in a native. A product gate has zero degree-1 part and cannot park the odd unit | [P] PROOF 6.13 |
| ANCHOR9 | Single-step (9,) anchors are illegal, the (1,8) split is forced, and anchors stay at 327 D0 | [P] PROOF 6.14; [C-lane] |
| GRASSCUT | No new floor. Node/set cut: Σ r_F = 711 over 602 frames on #7546, and unions never beat singletons. Pricing every arrival as a stop (1,946.5) is unsound; the native violates it at frame 602. The sound bound is ≥ 551 D0, below the census 1,330.5 | [P] PROOF 6.15; [C-lane] |
| SYMMETRY | No usable symmetry. Stab(Z16) has order 384 and Stab(A, B) = 1. The best element maps 27% of helper routes (4.8% with contacts), and 1,095 of 1,101 helpers have distinct signatures | [C-lane] |
| DUALBUILD | Both exact rank-0 hits so far of the dual-side scan (166 skips F783; 134 skips F789) are exactly edits already in #7603–#7605 (SYLforge, FanPUYen, aliromman). The dual scan independently rediscovers the swarm's chart contractions, and there is nothing new to stack. The remaining stays are being scanned, with no claim | [C-lane] |
| LITSWEEP / LITSWEEP2 | Literature leads: minrank/Haemers, fooling sets, rigidity, subspace-code cut sets, quadric frame partitions. None bounds the decoder directly; the follow-ups above tested them | [S] |

---

## Corrections of our own earlier statements

1. **LITSWEEP2 had the two graphs swapped.** The decoder's "odd" cells (label dot 1) are the integer-orthogonal pairs,
   SRG(120,63,30,36). The degree-56 graph is the label-even graph. LITSWEEP2 also said "135 frames, each orthogonal pair
   in exactly one". In fact there are 2,025 orthogonal 8-frames and each orthogonal pair lies in 15 [C `labels.py`].
2. **SPLITK and QUTRIT: the grade assumption.**
   - Both priced the split contract as if free endpoint wrappers preserved σ-grade. That is true only in radix 2.
   - WRAPAUDIT showed that the two-sided wrapper exists in odd radix, which reversed SPLITK's n_Y charge and QUTRIT's
     "+1 survives" at the pricing step.
   - O1SPLIT then showed that both lanes, and SPECCHALLENGE, checked a single character with freely conjugated
     factors. A real word must hit the target at two characters with the same constant conjugators.
   - With that, Lemma Z restores the +1 for every pattern.
   - Net: QUTRIT's conclusion stands, for a different reason. SPECCHALLENGE's ×1.40 / ×1.32 / ×1.51 envelopes are
     withdrawn.
3. **R3BUILD: target N was a porting error.**
   - RADIX3, QDEC and QUTRIT copied binary's "M = G/2 on the mask". In radix 3 the invariant is "M = δ on the mask"
     (target H).
   - The "c = 64" frame decoder therefore really costs ≥ 176.
   - QDEC's and QUTRIT's +2–7% radix-3 prices, which rested on target N, are void.
4. **HUBCLASS refutes the conjecture "M ≥ n at t = −1"** in the frame model. #7606 listed it as [S]: M = 72 is
   attained on P104.
5. **CALLEROPEN's "B is optimal in the two-arm family"** holds for **nested** masks. Nesting is a Floor-Lemma
   hypothesis, proved only at the outermost (b_1 = 0) and innermost (DYINGGEN Theorem 1) stages. The same applies to
   the arm-top part of β = 34 in #7607's κ(k) law (§E1 there).
6. **PROFILECHK's "possible soundness gap" was a misread of scope** (§2). SLOTKNOB's and SHAPE's θ < 1 sandwich
   applies to the strictified unit.
7. **RES-LAYER's "free single-step anchors" row is void** (ANCHOR9).
8. **The "70 vs 68" mod-3 decoder figure** belonged to the radix-3 world and was a catalogue MILP bound, not a theorem
   (MOD3DEC). The ASYMPORTS h = 10 decoder c = 50 was a floor artefact; the real cost is 57 (H10DEC).
9. **MUCENSUS** and **GRASSCUT** each caught a first-pass artefact of their own:
   - MUCENSUS: naive caller pairing gave μ up to 0.12.
   - GRASSCUT: arrival-as-stop pricing gave 1,946.5.
   Both are reported above only in their corrected form.

## Open next questions

1. **Interior nesting.** Prove b_k = 0 at interior stages of two-arm callers (gaps G1–G4 in PROOF 4.11). This would
   make B's optimality and β = 34 unconditional. First step: an exact L = 5 two-arm search with one dying role at
   stage 2.
2. **Hub U layer.** Does a one-plane public partner layer deliver (G/2 − I)y below 2,817 D0/call? That is the hub
   crossing (§4).
3. **Radix-3 decoder.** Is there a cancelling tiling of spilled A2/HIT rectangles giving a target-H radix-3 decoder with
   ΣΦ ≤ 67 (ρ = 2) or ≤ 71 (ρ = 1)? It is the last radix-3 escape (R3THIRD).
4. **h = 10.** Is C(103) = 56, which would make the h = 10 decoder exactly 57?
5. **Bounded headers.** Does a bounded-header caller stitched by tree nodes give κ(k) a positive limit? (This is also
   #7607's open question 3.)

## What is not included, and overlap

- **Excluded as work in progress:** the network-compiler route (REBUILDKIT, NETC2–NETC7, NETCAUX), R3TILE, and the
  continuing dual-side scan (DUALSCAN2).
- **Already in #7606:** the Cut Lemma (WEBS), XDEC, PARALLEL, KSLOT, MULTIMIX and BEAUTY100's all-B analysis.
- **Already in #7607:** dual-word price invariance (DUALWORD), the κ(k) core law, `layout_price`, `cap_check`, and the
  main-902 drop found on the dual.
- **Already in #7608:** DUALAUDIT and REPAIR902.

## Credits

All checkers and lane code are ours (DreamingOfClouds with Claude Opus 5.5, via Claude Code). Four lanes are Mason's
outside-session lanes (DreamingOfClouds): the TOY4 S2 proof, CALLEROPEN, JUNKROLE and DECLIFT9; so is WEBS, whose Cut
Lemma shipped in #7606 and is used here.

Swarm work referenced:

- ToikY: #7546.
- Rohan Arun (rohanarun): #7113 signed caller.
- SYLforge: #7603.
- FanPUYen: #7604.
- aliromman: #7605, whose word is vendored as data.
- CubeJerry: #6805 W6805 native; #7000 selected record.
- Clear1nsight and the P104 price and replay lineage: conventions.
- unpaidmoon: `research/p104-6372-clear-form-gap`, whose pinned candidate is read as data.
- The PR968 authors: the P104 labels.

See [NOTICE](NOTICE).
