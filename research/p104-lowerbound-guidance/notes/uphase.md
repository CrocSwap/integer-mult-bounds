# UPHASE UP (Nov 20, Opus, theory + exact replay). Own code in this dir: fattr.py (engine), asc56.py / asc56mix.py / asc56adj.py, adjoint.py, gadgets.py, fuzz.py, gettoy6.py (rebuilds RELAYTREE toy6 → toy6_word.pkl) + toy6chk.py → toy6.log. venv python, 1 proc, threads=1; no SAT/Lean/advisor/push/kill.
Why this differs from HT / HTD-PRICE / RS / RM / REVERSE / CARRYPOT / HALVPAY: those are potentials (rank-valued, so they collapse on dyadic carries; HALVPAY's U phase has E = 0) or they need HNF. Here the output is a DECODER (a list of rows), built by an exact linear identity. Charges are moved forward in time onto the owned register that cleans a public, which is the "cancellation pays" direction HALVPAY asked for. Scalars and denominators play no role (halvings are free), so all of the 2-adic difficulty goes into Wall56@Q96, the allowed premise.

VERDICT: [P] CANCELLATION-COST LAW (future attribution, FA) and its transpose (PA).
- Together they reduce R >= 56 to Wall56@Q96 for every run whose owned lifetimes are "gather-then-deposit" (GTD) and either cold-intake or dual-cold-output. Public relays of ANY shape are allowed: helpers, x/y-mixing, halvings, public hot deliveries into X (O3), and K-jumps through helpers.
- The real asc56 U runs (no-mix and mixed) are in the class. They give exactly the E8 decoder: 8 rows of price 7 = cost 7, so 56 = R. The master form is rank Y^ + rank Z^ = 28 + 28, block rank 56 = R (P104).
- The class boundary is the rendezvous on a Y carrier (G2), which is in neither class. It is not a counterexample to HostToDec, since R = |Q| there. It is the minimal run where per-lifetime attribution fails. That residual, plus multi-epoch lifetimes, is what is left of HostToDec_Q.

## 1. Setting
- Charts are F2-subspaces of F2^n. Values are Q-combinations of symbols. ADD d += lam*s needs equal charts. Publics only ascend.
- Owned registers are INIT (value 0) .. CLEAR (discard allowed). Moves are nested, and the cost is sum |d dim|.
- Targets X_t: charts contain q_t, final x_t - y_t (plus even-cell side info if wanted).
- Sources Y_s: charts lie in q_s^perp, final y_s.
- Every other public (helper/relay) has a final whose y-part is cold at its final chart. Tokens are the usual case.
- The start state is arbitrary as long as the X y-content is supported on even cells. This covers the full run (start x_t) and also the HALVPAY post-relay state x + (G/2 - I)y.

## 2. Future-attribution identity [P]
- Sweep forward. W_P (a vector over targets) is the total weight with which public P's content has been referenced so far.
- Each ADD d += lam*s into a public d references s with weight omega = lam*([d = X_t] e_t - W_d). The reason: d's content at an earlier read equals final_d minus d's later intakes.
- If s is public, set W_s += omega. If s is owned, record an output event e with alpha_e = omega, chart C_e and content c_e.
- Identity: final(X_t) - start(X_t) = sum_P W_P[t] final_P + sum_e alpha_e[t] c_e. This is exact telescoping, and the recursion runs strictly forward in time.
- (a) CHART INVARIANT. W_P[t] != 0 implies q_t ∈ chart(P) now; alpha_e[t] != 0 implies q_t ∈ C_e. Proof by induction: references are born where q_t ∈ chart(X_t), and a public's later charts contain its earlier ones.
- (b) Y-final terms sit on even cells: q_t ∈ chart(Y_s) ⊆ q_s^perp. Helper finals are cold at their final chart, so their terms are even too.
- (c) X-final terms are removed by x-balance (receipts have zero x-part). The result is the EFFECTIVE content ĉ = c|_y − Σ_s c[x_s]·final(X_s)|_y. In particular ĉ = c|_y when owned registers never hold x.
- => On every odd cell (t,s), including the diagonal: receipts = Σ_e alpha_e[t] ĉ_e[s]. Receipts are −I there.
- COROLLARY (odd-blind relays) [P]: a run with no owned registers delivers exactly 0 on every odd cell, over Q, whatever the relays, halvings or mixing. toy6 is an instance (§5).
- What this says: a public that delivers hot content into X has to end cold. Whoever cleans it is charged, at a chart that contains q_t. Relays, halvings and mixing among publics cost nothing and need no normal form.

## 3. Decoder corollary (class F) [P]
- Class F: each owned lifetime does all its intake before any output (GTD), and every intake's effective content is cold at the intake chart (supp ⊆ {s : C ⊆ q_s^perp}).
- Rows are one per lifetime: w_k = Σ_{e∈k} alpha_e and v_k = ĉ_k. Then:
  - D_k ⊆ labels in B_k = Σ (output charts), by (a);
  - S_k ⊆ labels in A_k^perp, where A_k = ∩ (intake charts).
- PRICE: rank_F2 Q[D_k,S_k] <= dim B_k − dim(B_k ∩ A_k). The pairing B × A^perp factors through B/(B∩A).
- COST: cost_k >= dim B_k − dim(B_k ∩ A_k). Proof:
  - Nested steps: φ(Z) = dim Z − dim(Z∩X) moves by at most |d dim| per step, so cost(X→Y) >= dim Y − dim(X∩Y).
  - Induction over the intake charts uses dim C_j + dim(A_j∩C_{j+1}) >= dim A_j + dim(C_j∩C_{j+1}) (modularity, A_j ⊆ C_j). This gives cost up to the last intake C_a >= dim C_a − dim A.
  - After the last intake, the ascent is >= dim(C_a + B) − dim C_a.
  - Summing gives >= dim(C_a+B) − dim A >= dim B − dim(B∩A), by modularity again.
- => {(w_k, v_k)} is a Q-mask decoder of the odd pattern on any port set (P104, Q96), with Σ price <= R.
- So R >= m(Q96), and **Wall56@Q96 ⇒ R >= 56**.
- Unconditionally (ORBITLP master form): if the rows rescale to (1/2) W V^T with W, V 2-adically integral, then R >= rank[[Y^,*],[0,Z^]] >= rank Y^ + rank Z^ for every y ⊆ D, z ⊆ S. So R >= 56 also follows from DOUBLE56's [CONJ] rho_A + rho_B >= 56, in its Q96 form.

## 4. Transposed law (class P) [P, transposition principle]
- The adjoint run is: reversed op order, ADD d += lam*s -> s += lam*d, C -> C^perp, INIT <-> CLEAR.
- It is a legal run of the same type: publics still ascend, the owned cost is unchanged, and X_t <-> Y_t swap roles with the same labels (C ∋ q iff C^perp ⊆ q^perp). It delivers exactly M^T.
- FA on the adjoint gives class P. The condition is GTD plus DUAL-COLD OUTPUTS: for each output of owned k into public P at chart C, the forward reach of P's content into the finals of X_t and Y_t only touches ports with q_t ∈ C.
- The rows are (reach, virtual intake profile), and the profile is supported on ports that are cold at the intake charts. So the price is <= cost exactly as in §3.
- PA charges a K-jump through a helper to the owned register that cancels the helper's junk (G3 below). This is the rational version of "the receiving rise pays", with no co-travel hypothesis.

## 5. Exact tests [C]
| run | legality / targets | identity | invariants | class | rows: price (cost) | Σ price | master form (P104) |
|---|---|---|---|---|---|---|---|
| asc56 U, no-mix (halvpay/f56run_nomix.pkl, 38,103 ops, 624 helpers, 10k+ halvings) | 0 / 0 | 0 fails | 0 / 0 | F and P | 8 × 7 (7) | 56 = R | Y^ 28, Z^ 28, block 56, rank(I+X) 56, lower-left 0 |
| same, Q96 restriction | — | 0 / 4,962 odd cells | — | — | 8 × 7 | 56 | Y^ 27, Z^ 28, block 55, rank(I+X) 54 (= RM) |
| asc56 U, MIXED (f56run.pkl; x/y-mixing, den 2^-5, not dyadic) | 0 / 0 | 0 | 0 / 0 | F | 8 × 7 (7) | 56 | 28 + 28 = 56 |
| adjoint of asc56 no-mix | 0 legality | receipts = M^T on all 104² cells | — | F on the adjoint (so P) | 8 × 7 | 56 | — |
| G1 deposit helper with halving (O3), {1,2,4} | targets met, R = 3 | 0 | 0 | F and P | 1,1,1 | 3 | — |
| G2 rendezvous on Y_r (REVERSE gadget, signed) | targets met, R = 3 | 0 | 0 | NEITHER | O2: price 1 (cost 0); O1: 0 (cost 1) | 3 | — |
| G3 K-jump through a helper | targets met, R = 3 | 0 | 0 | P only | P rows charge O1 | 3 | — |
| RELAYTREE toy6 seed 1 (toy6chk.py; 945 ops, 108 relays, 224 public deliveries into X, scalars ±1/2, 1/8; 0 owned) | 0 legality, X = x + Zy exact | 0 | 0 / 0 | trivially F | none | 0 = R | odd receipts 0 of 130 |
- FUZZ (fuzz20k.log): 20,000 random exact runs over Q (n = 3, 4; 2–5 ports; scalars ±1, ±1/2, 2, 3/2; rendezvous-biased births; no target constraint). Results:
  - identity fails 0;
  - invariant violations 0;
  - transposition mismatches 0;
  - in-class rows 547, with 0 price > bound and 0 bound > cost.
- TEETH:
  - hot-intake lifetimes have price > cost in 207 of 796;
  - letting publics descend breaks the invariants (864 / 230 runs) and the price lemma (6).

## 6. What is left, and the minimal counter-run
- G2 is the minimal shape outside F ∪ P. It is an owned lifetime that BOTH takes hot content from a public carrier (Y_r holding y_c at <1>) AND writes back into a public whose own final it reaches (it cleans Y_r).
- Per-lifetime attribution fails there: the cost sits on O1, which carried the cold junk y_r up, while the hot row sits on O2, which was born at the hot chart. The total still balances (3 = 3).
- [CONJ MIXED] Runs whose lifetimes are each F- or P-type (G3 + G1 mixtures) still admit a decoder with Σ price <= R. Not proved: composite paths F-row → public → P-lifetime → X leave B_k.
- Multi-epoch lifetimes (intake after output; HT §5 / O2) are excluded. Abel rows overcount: intake at C1, deliver at D1, intake at D1, deliver at D2 gives Σ price up to 2 dim D2 − dim D1 − dim C1 > cost.
- LADDER (updated): PR56 R-side ⇐ Wall56@Q96 + [every lifetime GTD and (cold-intake or dual-cold-output)]. The earlier ladder needed HostToDec_Q with O1/O2/O3 open. O3 is now closed over Q. O1 is closed when the carrier is a helper whose junk is cancelled; only the Y/X-carrier rendezvous (G2) and multi-epoch reloads remain.
NEXT: (i) a cluster law for G2. Merge owned lifetimes joined by owned→owned ADDs (O1 → O2 in G2) and price the cluster's rows by the cluster's cost. Test on G2 and on random hot-intake fuzz runs (the 207 per-row failures: do clusters fix all of them?). (ii) Lean: FA identity + invariant + price/cost lemma is short (RegionCore Run with W vectors), and the transpose is a matrix transpose.
