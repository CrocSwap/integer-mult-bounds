# FLUSHROW FR (Nov 20, Opus, theory + exact replay). Own code here: fr_relaxed.py (→ relaxed.log), fr_split.py (→ split.log), fr_pinned.py (→ pinned.log), fr_walk.py (→ walk.log). venv, 1 proc, threads=1; no SAT/Lean/advisor/push/kill. Engine: G2C gfa.py (read-only import).
Why this differs from G2CLUSTER/UPHASE: those priced lifetimes one at a time under the "helper final is y-cold" model. Here (i) the model itself is tested; it is too weak. (ii) The two residuals (a) and (b) are related by an exact run surgery, not by row design.

All statements are PORT-GENERAL: any label set Q ⊆ odd vectors of F2^N, any N.

VERDICT: R ≥ m(Q) for ALL runs is NOT proved.
- (a) reduces exactly to (b) [P+C].
- (b) is FALSE in the model UP/G2C wrote down [P+C, LOUD in that model only]. It must be posed in the PINNED model (helpers restore their token), which is the real SPEC ("restore forces their privates").
- In the pinned model, per-lifetime laws provably cannot close (b) [P+C]. The flush-row [CONJ] is FALSE [C].

## 1. Relaxed-model counter-run (LOUD in the relaxed model; NOT a PR56 counterexample) [P+C]
UP §1 / G2C allow any helper whose FINAL y-part is cold, without requiring it to restore its token. Under that rule the following runs at R = 0 for every Q. For each port t:
1. Blank the helper: A@{0}: A+=H_t, H_t−=A, CLEAR A. This costs 0 and throws away h_t.
2. H_t += Y_t, then H_t climbs to <q_t> for free. Its content y_t is now HOT.
3. X_t −= H_t.
4. Clean H_t: B@<q_t>: B+=H_t, H_t−=B, CLEAR B. This also costs 0.

Exact results (relaxed.log):
- Checked on {1,2,7}, on the 8 odd vectors of F2^4, on Q96 and on P104 (labels from halvpay/f56run_nomix.pkl).
- Every case: legal, R = 0, X_t = x_t − y_t EXACTLY, Y_t = y_t, helper finals 0 (no y at all), identity 0 fails, odd-cell 0 fails.
- So R = 0 < m(Q) (on Q96, m = 56 under Wall56).
- The FA rows are hot: price 1 at cost 0, one per port.

Control: the honest per-port run gives R = |Q|. The pinned check flags every blanked helper (3/8/96/104 violations).

Consequences:
- [P] No argument that uses only "public finals are y-cold" (G2C §6's proposed "global final-cold") can prove (b).
- A proof must use exact token restoration of helpers. This is the hypothesis the REVERSE tensor potential uses ("relays S_j,z_j → F_j,z_j"), and its relay terms cancel only because of it.
- A token alone is not enough: step 1 blanks a token helper for free. RESTORATION is the operative constraint.
- Side note [C]: G2C's odd-cell identity also needs non-X finals to be x-free and X finals to have x-part exactly x_t (x-balance). Without these, 3/165 fuzz runs whose y-parts are cold still fail (split.log development).

## 2. SPLIT reduction: (a) ⊆ (b) [P+C]
The surgery runs before every owned intake into d that comes after an output of d (C = d's chart; G is a fresh helper with token g):
- MOVE G→C; G+=d; INIT d'@C; d'+=G; G−=d; d'−=G; CLEAR d.
- Afterwards d' = content(d) exactly, and G ends at g exactly (pinned).

What the surgery preserves:
- No owned move is added or removed, so R is unchanged.
- Every original final and every receipt is unchanged.
- Every lifetime becomes GTD.
- No owned→owned ADD is needed.

[P] So HostToDec_Q for all pinned runs follows from HostToDec_Q for pinned runs whose lifetimes are all GTD. Descend-then-reintake is not a separate case. It becomes a GTD lifetime with a HOT intake (the hand-over content is generally hot at C).

[C] split.log:

| run | result |
|---|---|
| G2C epoch2 walk | 1 hand-over, R 5 = 5, finals equal, G restored, GTD after |
| 5,000 fuzz runs (UP generator, seed 23) | 9,414 hand-overs; 3,367 runs were non-GTD before |
| asc56 no-mix | 0 hand-overs, R = 56 |

Fuzz detail: 0 illegal, 0 R changes, 0 final changes, 0 unrestored, 0 non-GTD after, 0 identity fails, 0 invariant violations. On the 113 runs that meet the identity's preconditions, odd-cell fails are 0 before and 0 after.

## 3. Flush rows: the [CONJ] is FALSE; rectangle covers [P+C]
Walk C0 →(up a) C1 →(down 1, C2 a hyperplane of C1) C2 →(up b) C3, with γ0 taken at C0, α1 output at C1, γ2 taken at C2 and α3 output at C3. Cost is a+b+1.

[P] Generic chart prices, when the labels span:

| cover | price |
|---|---|
| forward α1⊗γ0 + α3⊗(γ0+γ2) | 2a+b (C0⊄C2) or 2a+b−1 (C0⊆C2) |
| flush | the same as forward |
| backward (α1+α3)⊗γ0 + α3⊗γ2 | a+2b |

[P] The F2 rank of the lifetime pattern is a+b, so there is no rank obstruction.

[C] walk.log (N=6, all odd labels, exact gfa rows):

| shape | cost | flush rows | backward cover |
|---|---|---|---|
| up3/down1/up1, C0⊄C2 | 5 | 2+4 = 6 | 5 |
| up3/down1/up1, C0⊆C2 | 5 | 3+3 = 6 | 5 |
| up2/down1/up2 (G2C shape) | 5 | 1+4 = 5 | — |
| up3/down1/up2, C0⊆C2 | 6 | 7 | 7 |

- For the up2/down1/up2 shape, the forward and backward covers are 6 each. With odd labels the flush rows reach 5 here, but they exceed 5 at the generic count.
- For up3/down1/up2, C0⊆C2, the forward cover is also 7, so all three covers overcount. Whether some label-split decoder reaches ≤ 6 is open.
- §2 makes this moot for the theorem.

## 4. Pinned model: per-lifetime laws cannot close (b) [P+C]
fr_pinned.py, per port t:
1. O'_t@{0} copies h_t.
2. H_t += Y_t at {0}, then climbs free to <q_t>.
3. O'_t climbs to <q_t> (cost 1).
4. O_t@<q_t>: O_t += H_t, O_t −= O'_t (now y_t), X_t −= O_t, H_t −= O_t (H_t back to h_t).

Exact results on {1,2,7} and on Q96:
- Legal, all finals pinned, R = |Q|, identity and odd cells 0 fails.
- Lifetimes: O_t has cost 0 and price 1 (hot); O'_t has cost 1 and price 0.

The row must be charged to O'_t, the climber that carried the cancelling TOKEN. That is cross-lifetime, through the h-coordinate.

[P, short linear-algebra proof; not replayed] PAST-TRACED IDENTITY (pinned or not; GTD runs):
- Expand each owned intake through its public's past: P(τ) = token_P + past intakes. Contents of owned m at its outputs are final (GTD).
- The owned-to-owned transfers U_km need out(m) < in(k) < out(k), so they are acyclic in first-output order.
- Hence ŵ_m = w_m + Σ_k U_km ŵ_k is well defined.
- On ALL token cells (x, y, z), receipts = Σ_m ŵ_m ⊗ a_m, where a_m consists only of token pieces tagged with their ENTRY chart (cold there).
- The O/O' witness: a_O = h + y_t[entry {0}], a_O' = h[entry {0}], with ŵ_O = −e_t and ŵ_O' = +e_t. The h pieces cancel, leaving −e_t ⊗ y_t[entry {0}], priced ≤ dim<q_t> − 0 = 1 = cost(O').

[CONJ SEPARATION-PAYS] In pinned GTD runs, the pieces of {(ŵ_m, a_m)} can be regrouped so that each group satisfies two conditions:
- its labels lie in the span of charts climbed by owned registers that carry its token pieces up from their entry charts;
- the cancelled token coordinates are exactly those forced to 0 by restoration (z-balance) and x-balance.

That gives Σ price ≤ R, i.e. R ≥ m(Q) for all runs. This is the decoder-valued form of the REVERSE tensor potential. The tensor potential proves the GF(2)/Z_(2) shadow, R ≥ rank_F2(Q∘M).

LADDER (updated): R ≥ m(Q) for all pinned runs ⇐ [CONJ SEPARATION-PAYS] on pinned GTD runs. G2C's NRI and class F/P are the special case where every piece's entry chart is the intake chart.
NEXT:
- (i) A pinned-run fuzz generator, needed to test SEPARATION-PAYS. Random runs violate restoration; use compute → owned-climb uncompute.
- (ii) Prove SEPARATION-PAYS for single-carrier runs: each helper absorbs foreign tokens only below its first hot read.
- (iii) Lean: the SPLIT surgery and the relaxed counter-run are short exact statements over RegionCore runs.
