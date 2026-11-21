# KASYM KA (Nov 20, Opus; theory + exact LP). Own code: ka1 (full cc1 LP duals by family), ka2 (reduced LP, float), ka3 (HP formula),
ka4 (chord dual, float DP), ka5 (chord dual, mpmath-60, exhaustive DP from row definitions), ka6 (sympy identities, discrete q checks, HP monotone),
ka7 (built frames). Logs ka5.log, cert73.log. 1 proc, threads=1. No Lean/advisor/kill/push.
Why this differs: CALLERCUT gave per-k certificates of the RC2 LP. This lane finds the closed-form optimum + dual for ALL k.

## 0. Result
[P] CLOSED-FORM CALLER LAW (scope = the CC witness model: RB §0 frame, Q=0, rho=2, n=2k-2 roles, every D>=2, lambda != -1, role-piece objective).
  c^(.99) <= HP(k) := (208/k) * [ (k-2)(17^s - 16^s) + (8k+1)^s - 8^s k ],   s = .99,  every k >= 3.
Only 3 laws are used: role count n = 2k-2 with D >= 2 (SIGN1), MAINS (2 mains per stage, mains are singleton pieces), RC2_l for l = 3..k.
No SEP, COVER, DYADIC, coord, pfix or witness rows are needed.
HP(k) is the value of the HUBPAIR chart (2 all-main hubs + 2k-4 pure pairs), which is feasible for these laws. So HP(k) is EXACTLY the optimum of the reduced LP.
[P] HP rises on k <= 12 and falls on k >= 13 (real k). Max = HP(13) = 143.2730946.
[C] HP(73) = 128.9436 > 128.891 > HP(74) = 128.7692.
[C] Full-LP certificates (cc2): k72 128.8501 (CALLERCUT) and k73 128.6813 (this lane, cert73.log).

THEOREM [P + C at k = 72, 73]: in the CC model, every caller with k >= 72 stages has c^(.99) < 128.891.
- k >= 74: closed form.
- k = 72, 73: exact dual certificates of the full RC2 LP.
- This closes the [CONJ] gaps 73..127 and k > 128 of CC.md §3.
- The open window of the RC2 route is now exactly k in 5..71.

## 1. The chord dual (closed form)
Notation:
- v2p = 17^s - 16^s (= value of a pure pair = max over pure roles).
- h(D) = v2p - (8D+1)^s + 8^s D (the cost of an all-singleton hub).
- q(D) = h(D)/D.
- l(D) = the chord of q through (2, q(2)) and (k, q(k)), with slope sl = (q(k)-q(2))/(k-2).
- G = q - l.
Dual:
- M = v2p (pure pair). wm = q(2) - sl (MAINS multiplier). sigma = 0 (no SEP).
- S(2) = 0, S(D) = (k-1) G(D)/(k-D) for 3 <= D <= k-1, S(k) = T = (k-1) sl.
- RC2 weights w_l = S(l) - S(l-1), l = 3..k.  (S(D) = sum_{3<=l<=D} w_l.)
Bound: B = nM - 2k sum w_l - 2k wm = (2k-2) v2p - 2 h(k) = (k/104) HP(k).
Design meaning: every all-singleton main hub (D, 1^D) for D = 2..k is TIGHT. D = 2 is the (1,1) main pair. The pure pair is tight.

## 2. Proof of dual feasibility [P]
Price of a type (degree D, piece multiset P with sum D; each singleton main or idle) under the dual, from the row definitions
(RC2_l deep l <= D: sum_{L<l} L(k-L)/(k-1);  shallow l > D: (D^2 - sum L^2)/(k-1)):
  Phi = (8D+1)^s - sum (8L)^s + sum_L L(k-L)(S(D)-S(L))/(k-1) + (D^2 - sum L^2)(T - S(D))/(k-1) + wm #mains.
KEY IDENTITY:
- The defining equations are D S(D) + D(D-1)(T-S(D))/(k-1) + D wm = h(D) for all 2 <= D <= k.
- Apply them at D, and at each piece size L.
- Use D^2 - sum L^2 = sum L(D-L) and sum L(k-L) = kD - sum L^2.
- Then every D-dependent term cancels:
    Phi - v2p = sum_{pieces} L * chi(L)
  with
    chi(L) = [(8L+1)^s - (8L)^s - v2p]/L   for L >= 2,
    chi(1) = 0 (main),
    chi(1) = -wm (idle).
Feasibility then reduces to 3 one-variable facts:
- (F1) (8L+1)^s - (8L)^s is decreasing (t^s concave). So chi(L) <= 0 for L >= 2, with equality only at L = 2.
- (F2) wm >= 0.
- (F3) w_l >= 0, i.e. S is nondecreasing on {2..k}.
Proof of (F3):
- Let q be concave and increasing on [2, inf).
- Then G is concave with G(2) = G(k) = 0.
- S(D) = -(k-1) * (secant slope of G on [D,k]). Secant slopes of a concave function fall as the left end moves right, so S is nondecreasing on 2..k-1.
- w_k = (k-1)(q(k) - q(k-1)) >= 0.
Proof of (F2): concavity gives sl <= q'(2), so wm >= q(2) - q'(2) = 0.0541 - 0.0409 > 0.
q facts [P]. Write q = 8^s - r with r = ((8D+1)^s - v2p)/D, u = 8D+1, eps = 1-s.
- r' = N/D^2 with N = v2p - u^{-eps}(8 eps D + 1) (sympy-checked, ka6).
  - m(D) = u^{-eps}(8 eps D + 1) has m' = 64 eps(1-eps) D u^{-eps-1} > 0.
  - m(2) = 1.16 * 17^{-.01} > 1.127 > v2p (v2p < 1 by the MVT).
  - So N < 0 and q is strictly increasing.
- r'' D^3 = u^{-1-eps}(64 eps(1+eps)D^2 + 16(1+eps)D + 2) - 2 v2p (sympy-checked).
  - Divided by u: 2(1+eps) + eps(1+eps)(8D-1) - eps(1-eps)/u >= 2.0093 + 0.0808 D.
  - Need u^{.01} <= (2.0093 + .0808D)/(2 v2p). The right side is >= 1.0421 + .0419 D.
  - For u <= e^100: u^{.01} <= 1 + (e-1)(.01) ln u <= 1.0488 + .0081(D-2) (tangent of ln at D=2). This is < 1.1259 + .0419(D-2).
  - For u > e^100: u^{.01} = u * u^{-.99} < 10^{-40} u, which is far below .005 u.
  - So r'' > 0 and q is concave on [2, inf).
- [C ka6] Discrete check D = 2..20000: min dq = 3.5e-6 > 0, max d2q = -1.8e-10 < 0.
HP monotone [P]:
- HP = 208[v2p - 8^s + ((8k+1)^s - 2v2p)/k].
- d/dk of the last term = (2v2p - m(k))/k^2, and m is increasing.
- m(12) = 1.8724 < 2v2p = 1.9253 < m(13) = 1.9472.
- So HP is decreasing on [13, inf) and its integer max is at k = 13.

## 3. Exact verification [C, ka5 mpmath dps 60, exhaustive DP over ALL partitions of every D <= k, parts unrestricted, mf in {0,1}; phi from row definitions, not from chi]
- k = 3..16, 20, 30, 40, 72, 73, 74, 75, 100, 128, 160:
  - max phi - v2p <= 3e-57;
  - B - HP <= 8e-55;
  - min w_l > 0 (k160: 2.35e-4);
  - wm in [0.021, 0.052].
- The float reduced LP (ka2) equals HP to 4 decimals at k 32, 64, 72..76, 80, 96, 97, 128.

## 4. Dual structure / asymptotics
- As k -> inf at fixed l: w_l -> q(l) - q(l-1) ~ 8^s((l-1)^{-eps} - l^{-eps}) ~ 0.0783/l (scale-free).
- T = sum w_l ~ q(k) - q(2) ~ 0.078 ln(k/2).
- wm -> 8^s(1 - 2^{-eps}) = 0.0541.
- SEP weight is 0.
- This is the "log-uniform relay-cut" dual. The full cc1 LP instead spreads weight ~0.053/(l-1) plus SEP 0.15/k plus pfix1, which buys up to 0.3 below HP at k >= 16 (ka1).
- HP(k) = 208[v2p - 8^s(1 - k^{-.01})] + O(1/k), which is about 200.5 - 16.3 ln k for k << e^100.
  - It is NOT a constant and NOT c/k: it decreases logarithmically.
  - Formal limit 208(v2p - 8^s) = -1429.5. HP(1e3) = 91.2, HP(1e4) = 56.8, HP(1e6) = -10.1.
- [C] Full RC2 LP = HP(k) to 7 digits at every certified k in 4..14. It is strictly below HP from k16 on (k16 142.8088 vs 142.8935; k72 128.8501 vs 129.1199).
  - So [P] CC's sup 143.273 at k13 IS HP(13): the HUBPAIR chart is the exact optimum of {n, MAINS, RC2} there, and only the mask-level HUBPAIR theorem (not a type row) can cut it.

## 5. Soundness / scope
- RC2 rows: cc0 frames pass (tight).
- Built frames [C ka7]: C1 107.91 <= HP(3) 115.42; c33 119.49 <= HP(6) 137.56.
- Scope is the CC model (Q=0, n=2k-2, D>=2). The Q>=1 branch (and #7113-type Q>0 callers) is NOT covered here, just as for CC.

## 6. Next
- (i) Lean: the KEY IDENTITY is pure algebra over the defining equations. Feasibility = F1-F3. This is a short Lean file next to CallerRC2.lean; the real-analysis facts on q need rpow convexity.
- (ii) Mid window k 5..71: the closed form shows that n + MAINS + RC2 can never beat HUBPAIR. Any row that helps must cut the HUBPAIR point itself (the CALLERLAW HUBPAIR theorem is mask-level). The full-LP extras give at most 0.3 at k >= 16.
- (iii) Q>=1 branch: redo the chord dual with n = 2k-1 and no SIGN1/COVER.
