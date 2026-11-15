# Proofs for the P104 follow-up package

Each section gives the statement, its hypotheses and the proof. Numbering follows the README. Notation follows #7606
(`research/p104-odd-unit-per-grading`): frames are subspaces of F₂^h with the standard dot, q_t is port t's label,
X_t is born on the line ⟨q_t⟩ and ends at V, Y_t ends at the hyperplane q_t^⊥, public MOVEs ascend, owned MOVEs pay
|Δdim|. G_s = {frames containing q_s}. The web-general **Cut Lemma** (WEBS, shipped in #7606 §I.3) is used throughout:
for an up-set G, rank(O mod Π) ≥ def(G) = dim(F + Π) − dim F, where Π is the public vectors entering G, O the owned
contents crossing into G and F the finals in G. Its births form: #owned moves entering G ≥ #{j : ⟨q_j⟩ ∈ G, q_j^⊥ ∉ G}.

---

## 1. Owned CLEAR content (CLEARFORM)

**1.1 Rank lemma ⇒ every CLEAR of an endpoint-exact word is lossless.** Work in the scalar projection: rows are linear
functionals of the n public input tokens, owned INIT is the zero row, and ADD/COPY/SCALE act literally (MOVE relabels
the chart). By `research/p104-shared-native-helper-splits/retained/compiler/PROOF.md:87-90`, conjugating each stream
by its chart makes this the exact endpoint on arbitrary full arrays, so it suffices to argue on rows. Let ρ_t be the
rank of the live rows after event t.

- ADD r += c·s (s ≠ r live), SCALE by c ≠ 0 and MOVE are invertible maps of the live tuple, so ρ is unchanged. COPY into
  a zero owned row and INIT add a vector already in the span (or 0), so ρ is unchanged.
- CLEAR of v lowers ρ by 1 iff v ∉ span(other live rows), and by 0 otherwise.
- ρ_0 = n and ρ never increases. If the final public rows are invertible (the endpoint), ρ_end = n, so ρ_t = n for every
  t and no CLEAR lowers the rank: every erased row lies in the span of the other live rows at that moment. ∎

So "lossless" is implied by endpoint exactness, which every admitted word proves anyway.

**1.2 Content theorem.** Let W, W′ be legal, endpoint-exact words with the same header and the same owned
INIT/MOVE/CLEAR events (fields, charts, chronology, lifetimes, peak). Then W′ satisfies `owned_erasure` iff W does, and
every cost term gets the same erasure contribution, whatever rows the two words erase.

*Proof.* The retained contract behind `owned_erasure` (certificates/selected-result.json:95-97) consists of these clauses:

- E1: FINITE-PRECOMPILATION.md:34-35, explicit initialisation and erasure.
- E2: FINITE-PRECOMPILATION.md:250-256, one bank per live unit, with erasure in the fixed scalar cost.
- E3: FINITE-PRECOMPILATION.md:264-268, "field-identity and chronological requirements"; a clear acts only after the
  child unit completes.
- E4: notes/copied-centers-lemma.tex:29-35, erasure is linear in the stream volume.
- E5: research/kappa-rebuild/transfer-audit/h-branch/H-PRIMITIVE-AUDIT.md:51-62, "the discarded value is generally
  nonzero" and no reversible uncompute is required.
- E6: retained/compiler/PROOF.md:97-99 and 333-337, dirty residuals count only through earlier ADD reads.

Taking the clauses in turn:

- E1–E3 depend only on the INIT/CLEAR/MOVE events and unit tags, which are identical in the two words.
- E2 and E4 price erasure by volume, which the chart and field fix. E5 excludes a content-dependent uncompute bill.
- Correctness is the endpoint, and by 1.1 both words are lossless at every CLEAR.
- The κ invoice is a function of paid MOVE ranks and productive targets and has no CLEAR term. The strictification gate
  (§2) takes only the invoice.
- Precision (E6) depends on values held and read before the erase, not on the erased value.

No clause names, limits or prices the erased value. ∎

Scope:

- Owned fields only. Zeroing a public register without a live owned holder is a genuine loss (Rank lemma part 1, #7606).
- The theorem fails in a reversible-uncompute model, which E5 says the retained model is not.

**1.3 The #7608 case** [C `clearform.py`].

- CLEAR #44 (owned 1557, chart 595) erases {451: −1, 1495: 1}. This is an exact Q-combination of 21 live rows (other
  live rank 1501 = n_pub).
- #7605's row at the same CLEAR is the same combination plus −3/2·(x902 + x985).
- All other 73 CLEARs erase identical rows in the two words.

With the identical owned events (DUALAUDIT, in #7608), 1.2 applies.

---

## 2. Separation hypothesis (SEPAUDIT)

FINITE-PRECOMPILATION.md:51-52 and :205-207 require r_max < k_min for the unit fed to the compiler. The admitted
strictification step (docs/research/pr-intake-evidence/pr4416/PROOF-REVIEW.md:139-185; theorem in
research/higher-moment-strictification README §2) takes a product power v, completes every target to ≥ b^v and splits
paid jobs into blocks ≤ c^v < b^v. The paid moment stays below 1 iff α, γ, δ < 1, and the selected #7000 record states
its raw invoice fails separation and strictifies with c = 11, b = 12, u = 1/7, v = 1920
(retained/compiler/PROOF.md:195-198; interval_gate.py:52-83). So the hypothesis applies to the strictified unit, not
the raw invoice. The gate values for #7546, #7605 and #7608 are re-run in `sepgate.py`.

---

## 3. t = −1 toys and hubs

Model (WEBS toy): F₂^m, U-only targets X_t = x_t − y_t at V and Y_t = y_t at q_t^⊥. Helpers are arbitrary (any number,
any web), and owned rows are token-free. φ_d(u) := coef_{x_d}(u) + coef_{y_d}(u). A port s is **tight** if exactly
one owned move enters G_s.

**3.1 Pin Lemma** (TOY4 S2, an outside-session lane of DreamingOfClouds'). If s is tight, every content held at a frame of G_s
lies in Π_s = F_s ⊕ ⟨x_s⟩. In particular φ_d = 0 there for every non-partner d of s.

*Proof.* By the Cut Lemma, Σ_{G_s} ⊆ span(Π) + ⟨o⟩ with |Π| = dim F_s. Σ contains F_s + ⟨x_s⟩, of dimension
|F_s| + 1, because Y_s ends outside G_s. So equality holds. F_s holds x_d − y_d, and it holds y_d only if d is a
partner. ∎

**3.2 Time-cut basis.** Let D be a down-set with no owned move leaving it. Then (finals in D) ∪ (public vectors
crossing out of D) is a basis of B_D = span(tokens born in D).

*Proof.* Contents of D-frames lie in B_D, because owned rows ascend. Project every final to B_D. The finals outside D
land in the span of the crossings (Cut Lemma with no owned crossing). All finals span T. For the count, every public
register born in D either ends in D or leaves it exactly once. ∎

**3.3 Down-set No-Loss (DNL).** Fix a frame g and let D be the closure of down(g) under owned departures. Suppose no
owned move arrives at g and no frame of D lies strictly above g. Then the public outputs of g (departures and finals)
form a basis of W_g.

*Proof.* Apply 3.2 to D and to D′ = D − {g}, which is still closed. Then B_D = span(Rest + finals_{D′}) ⊕ W_g, and
|out_g| = dim W_g. ∎

DNL holds in real time and in the frame-memory relaxation, for any helper web. Its hypotheses are necessary: on 12,000
random frame-memory programs that violate them, the finals still span 1,448 times [C-lane `dnl_test.py`].

**3.4 Charge Corollary.** Let d be a port with a tight non-partner, and let U_d be the union of G_s over tight
non-partners s. Then some frame g ∋ q_d with g ∉ U_d fails DNL.

*Proof.*

1. x_d ∈ W_{⟨q_d⟩}. At a frame satisfying DNL the outputs span W, so some output has φ_d ≠ 0.
2. That output is not a final: only Y_d's final has φ_d ≠ 0, and q_d^⊥ ∌ q_d. So it departs to a frame g′ ∋ q_d.
3. g′ lies outside U_d by 3.1.
4. Repeat from g′. V is pinned, so the chain stops at a frame that fails DNL. ∎

**3.5 The F₂³ decision.** Labels 1, 2, 4, 7, climb 3. In all 13 cut-feasible sets, ports 1, 2 and 4 are tight, so
U_7 = every frame strictly above ⟨7⟩. The frame ⟨7⟩ satisfies DNL in every set. By 3.4 no exact program exists, for
any helpers [C `toy4.py`].

An independent proof is TOY4 S1 (3.6–3.8) with the hand argument of TOY4 §2. Owned descents change nothing: a mass-3
set containing a descent has ascent climb ≤ 2, which the Cut Lemma already kills.

**3.6 Forwarding Lemma** (TOY4 S1). Let s₁ = #owned moves leaving {0}. For any set of label lines,
Σ_L [dim W_L − dim(Out(L) + F_L)] ≤ s₁.

*Proof.* Let D = {0} ∪ lines. Public crossings out of D, births in its complement and finals in D number exactly dim T,
and every final lies in their span plus F_D. A register at L either ends there or leaves. ∎

**3.7 Union Lemma.** Let t's line forward, and let G_1..G_k be up-sets covering the frames above L_t that avoid L_t and
hyp_t. Then Σ_i sl(G_i) ≥ 1, where sl = o − def.

*Proof.* The Cut Lemma gives τ(Σ_G) ⊆ legit(G) + (a space of dim ≤ sl(G)), with τ the quotient by
span{x_j − y_j} + H. Forwarding puts y_t = τ(x_t) in Σ τ(Σ_{G_i}) + τ(F_{L_t}), whose legit parts avoid y_t. ∎

**3.8 Duality Lemma.** O is feasible iff O^⊥ = {(b^⊥, a^⊥)} is feasible, with the same labels and climb.

*Proof.* A frame-memory design is an acyclic linear network code. Transpose every local map, reverse the edges and
relabel f ↦ f^⊥ (inclusion reverses, so ascents stay ascents). The old X_t becomes a Y-type register and the old Y_t an
X-type register. Helpers stay helpers and owned edges stay token-free. ∎

The same map on whole words is the frame-perp transpose shipped in #7607 (`dualword.py`).

**3.9 Pocket Lemma** (TOY5). Any helpers, born and ending anywhere; owned descents are allowed. ψ_t := coef(x_t) +
coef(y_t). A frame f is t-pinned if some tight up-set G′ ∋ f avoids L_t and hyp_t. Take an up-set G, a set of ports T
and N = Up(L_T) \ G. Let R ⊆ T be the ports with L_t ∈ N, hyp_t ∉ N and every frame of G above N t-pinned. Then
o(G) + #(owned moves entering N from outside) ≥ |R|.

*Proof.*

1. N's contents lie in span(births, public arrivals, owned arrivals).
2. N's public outputs (exits into G, finals in N) are killed by Ψ = span{ψ_t : t ∈ R}. Exits land at pinned frames,
   where a tight G′ gives Σ_{G′} ⊆ span{x_j − y_j, y_j (j ∈ J)} + H with t ∉ J. The finals are x_j − y_j, h, or y_j with
   j ∉ R. Ψ has rank |R| on the births x_t.
3. So the outputs have rank ≤ #inputs + owned_in − |R|.
4. F_D ∪ P_G ∪ B_G has dim T elements, spans T together with O_G, and contains every output of N, so its deficiency
   is ≤ o(G). ∎

**3.10 Hub construction** (HUBCLASS). Pick A with A_tt = 1 and A_ts = 0 on non-partners, of rank k, and factor
A = ΛE. The k hubs gather Ey at {0} from the Y mains and move {0} → V. Each partner cell (t, s) gets one helper:

1. at {0}: H += A_ts·Y_s;
2. at ⟨q_t⟩: X_t += H;
3. at q_s^⊥ (which contains q_t): H −= A_ts·Y_s;
4. at V: X_t −= H.

At V, X_t −= Λ_t·hubs. Then X_t = x_t − y_t, Y_t = y_t and H = h, exactly. On P104, A = G/2 has rank 8 = α, so 8 hubs
(M = 72) realise the cut floor [C-lane exact replay, 41,265 events; the fit facts are re-run in `labels.py`].

**3.11 V-funnel lemma.** Suppose the only owned moves are k hubs {0} → V.

- W_V's finals lie in span{x − y} + H, so dim τ(W_V) ≤ k.
- The arrivals' x-parts have rank n, and hubs carry no x.
- So the y-content riding public registers into V has rank ≥ n − k = 96 on P104.

A public y → X layer of rank ≥ 96 is therefore forced. ∎

Clone interaction: sharing works only for additive y → X delivery. A killed departure content (the park) has no side
information, so the Rank/Clone lemma needs owned rank ≥ 96 there.

**3.12 F₂⁴ hubs.** Hub total climb is ≥ n for every F₂⁴ label set.

*Proof.* k ≥ α by the cut lemma, and α = 1 forces an orthonormal set (n ≤ 4), while n ≤ 8 always. ∎

**3.13 Piggyback lemma** (TOY5 §3). An unfed port d cannot piggyback on non-partners' private ascents
⟨q_s + q_d⟩ → ⟨q_s, q_d⟩.

*Proof.* q_s + q_d is even, so it is never a label. No feeder enters G = ∪_s Up(q_s) ∪ Up(q_s + q_d), and each tight
G_s d-pins every landing. ∎

This assumes no owned move lands in Up(q_d) \ G.

---

## 4. Callers

Setting (CALLEROPEN, an outside-session lane of DreamingOfClouds', and SINGLEHUB): ρ = 2, K = WZᵀ, units T = I − 2xyᵀ,
product −I, HOST stages with t ≠ −1. Lemma S: G_ij = ±(WZᵀ)_ij.

**4.1 Crossing Lemma.** Let k, k+1 be consecutive stages, S = Z_k ∩ Z_{k+1} ⊇ X_k, and let j be a witness stage with
(Z_k ∪ Z_{k+1}) ∩ Z_j ⊆ S. Then rank(Y_k, Y_{k+1} | S) = 4. Dually for X.

*Proof.*

1. Suppose cᵀY_{k+1} = aᵀY_k on S.
2. Pair with X_j. Both pairings live on S, and K[k, j], K[k+1, j] carry the same sign, so cᵀW_{k+1} = aᵀW_k.
3. Pair with X_k: aᵀ(K_kk − G_kk) = 0, and K_kk − G_kk = [[1, −2g], [0, 1]], so a = 0.
4. W_{k+1} is invertible (t ≠ −1), so c = 0. ∎

**4.2 Floor Lemma.** Let calls 0..k+1 precede a call r. Assume **nesting** (the X of calls 0..k lie in Z_k) and that
Z_r meets Z_j (j ≤ k+1) only inside H ⊆ Z_k. Then |Z_k| ≥ 2(k+1) + 2.

*Proof.* The pairing matrix of {Y_j | Z_k} against {X_0..X_k, X_r | H} is [G[A+b, A] | G[A+b, r]] with b = k+1.

1. Suppose (α, β) is a null vector.
2. Row b gives Z_Aᵀα = Z_rᵀβ.
3. Rows A give (K_AA − G_AA)α = 0, and K_AA − G_AA = I − 2U is unitriangular, so α = 0 and then β = 0.
4. Hence the 2(k+1) + 2 columns are independent in R^{Z_k}. ∎

**4.3 B in the nested two-arm family.**

- The masks are bounded below by 4.2 and the caps follow from 4.1.
- Given the masks and caps, ending the youngest lines first majorises every feasible schedule (exchange argument, at
  sketch level) and maximises Σ f(8l). That schedule is B's.

Scope: two arms meeting only in the hubs, nested masks, ρ = 2, HOST t ≠ −1, PRICEKIT line model.

**4.4 Shared D is illegal; SL without independence.**

- Legality: rootcheck rejects a repeated stage variable, and the free ops are q-only.
- CALLEROUT's backward induction never uses one z per call, so SL holds per call with Z_k = roles whose target contains
  that D.
- In a one-hub two-arm layout every cross pair must share its D. K_{8,9} is connected, so all calls share one D, every
  role then has degree ≤ 1, and there is no hub. ∎

**4.5 Multi-centre ⇒ ρ ≥ 2c.**

- Each piece has rank K_i = 2, so N_i ≥ |P_i| + 2 + rank(I − M_i^H).
- The hub blocks satisfy ∏ M_i^H = −I, so Σ rank(I − M_i^H) ≥ 2. ∎

**4.6 Junk role = dilated root** (JUNKROLE, an outside-session lane of DreamingOfClouds'). Put a = P[J, C], b = P[C, J] and
m = P[J, J]. Since det P = 1 and n_C is odd, m = −1 − a·b, and

  P = −(I − e_J ãᵀ)(I − b̃ e_Jᵀ),

with ã, b̃ zero at J (expand the product). So a junk caller is a root on C + J with a virtual odd unit reading only J
before time 0 and one writing only J after the end. Mode (a) is ρ = 3 and mode (b) is ρ = 2.

Mode (a): from K + y_J x_Jᵀ = WZᵀ, a stage that does not use J has W, Z of rank 2. So in every cross pair one stage uses
J, and the J-stages form a vertex cover of K_{8,9}: a whole arm. ∎

**4.7 Crossing Lemma for ρ ≥ 3** (RHO3CROSS). With witnesses j, u = cᵀW_{k+1} − aᵀW_k is orthogonal to the row space
of each Z_j. So the relation dimension is ≤ ρ − rank(Σ Z_j^witness), and the rest of 4.1 is unchanged.

- At ρ = 3, two boundaries with δ ≥ 1 have witness sets covering all calls, each of Z-rank ≤ 2 and sharing a call, so
  their total Z-rank is 2 < ρ. Hence δ = 1 only at the two outer boundaries.
- The Floor Lemma becomes |Z_k| ≥ 2(k+1) + 4 − ρ (null dimension ≤ ρ − 2). ∎

**4.8 β = 4g + 2** (BETA). Per port, D0 = Σ_T f(8d+1) − Σ_P f(8l). An arm field of degree j (two per j) cancels its idle
line P[8j] up to ln(8j) + 1, leaving 2 ln k from the interior. What stays uncancelled:

- 2 hubs (degree k, rank 8k+1): 2g;
- 4 arm-top roles (degree k/2): 2g;
- the interior: 2.

So β = 4g + 2 = 34. The per-stage lift 8 = h − 1 is the F₂⁸ frame dimension of each stage variable (rank 8·deg + 1).

- Hub degree k is forced by 4.1, 4.2 and Theorem 1′.
- Arm-top degree k/2 is forced only under nesting (the hypothesis of 4.2). ∎

Also: c copies of C(k/c) give exactly κ(k/c), so multi-centre layouts move along the same curve.

**4.9 Nesting, partial** (NESTPROOF).

- L1 (from Lemma S alone): if v = X_E β is orthogonal to both y's of one later stage, then γ = Σβ_i z_i = 0 and v is
  orthogonal to every later y.
- L2: prefix commutation splits V_k = C(P_k − I) along Z_k | N_k.
- L3: the outside part B_k lies in span(e_0..e_{k−2}), so b_k ≤ 2k − 2. P_k acts on R^{N_k} as the reflection
  I − 2Π_B, and b_1 = 0.
- L4: restricting the Floor pairing matrix to Z_k loses rank ≤ b_k, so |Z_k| ≥ 2(k+1) + 2 − b_k (under hypothesis H,
  that the early y are independent).

Nesting ⇔ b_k = 0 for all k. ∎

**4.10 DYINGEXACT** (L = 4, left arm 3 stages, right arm 1 stage on {0, 1, 8, 9}, hubs {0, 1}, role 3 ∈ Z_1 \ Z_2).
This layout is infeasible for every t ≠ −1.

*Proof.* The thin product gives rank(I + g) ≤ 4 with g = S_2 P_4 R. Stage commutation gives P_4 e_3 = c·e_3.

- Lemma D: if c ≠ 1, then v ∈ span(e_4, e_5) exists with P_4 v = R v = v.
- Fx = fix(P_4 R) has dim ≥ 4, and (I + g)|Fx = (I + S_2)|Fx is injective, so Im(I + g) = (I + S_2)Fx.
- If c ∉ {±1}: (1 + c)e_3 is independent of that image, so the rank is ≥ 5. Contradiction.
- If c = ±1: three vectors of Fx have zero F-part (F = {8, 9}), so π_F(Im(I + g)) has dim ≤ 1. But [R_Fh | I + R_FF] has
  rank 2. Contradiction. ∎

**4.11 DYINGGEN Theorem 1** (innermost stage, any m, r, any number of dying roles). Hypotheses: t_s ≠ −1, prefix
commutation, F-nondegeneracy.

- rank(I + g) ≤ τ and the injection of fix(PR) force every inequality to be tight: rank(PR − I) = q + 2r, dim Fx = τ,
  Im(I + g) = (I + S)Fx.
- Δ_F = 0, and P_D is a reflection (c = −1 is forced).
- dim K_0 ≤ |Z| − q − 2r + b, so |Z_{m−1}| ≥ q + 4 − b.

Lemma 2: if the top index is m − 2, the new-role rows of Y are collinear, so |Z_{m−1}| ≥ q + 4 − b + (|E_{m−2} \ D| − 1).
With b = 1 and |E| = 2 this is DYINGEXACT.

Gaps (not proved):

- interior stages, where no induction is available;
- top index below m − 2;
- |E| ≤ 1;
- b ≥ 2.

---

## 5. Decoders

**5.1 Residual identity** (DECLIFT9, an outside-session lane of DreamingOfClouds'). Give each gathered atom x_s a residual
y = q_s.

- At each unit descent f → g, fix π ∈ f \ g and split y = λπ + y′ with y′ ∈ g.
- Lifts and merges leave y unchanged.
- A deposit into t lies in q_t^⊥, so ⟨q_t, y_end⟩ = 0.

Hence for every path s → t, Q[t, s] = Σ_{descents j} λ_j ⟨q_t, π_j⟩ mod 2. λ_j depends only on the path prefix and
⟨q_t, π_j⟩ only on t, so Σ_paths coef·(Σ_j b_j) = Σ_j a_j b_jᵀ: one rank-1 term per unit descent.

- With odd denominators, M∘Q = I reduces mod 2, so n ≤ C.
- At half level (every path coefficient of 2-adic valuation ≥ −1), the mod-4 expansion gives
  n ≤ Σ_i (1 + min(dim g_i/K_i, D_i)) ≤ Σ_{p=1..C} (1 + min(8, C − p)), so C ≥ 16. ∎

**5.2 Caller op X_p → Y_p.** A free op needs a common frame f with q_p ∈ f ⊆ q_p^⊥. That is impossible, because
q_p·q_p = 1. By 5.1, a free X_p → Y_p would give the identity decoder at cost 0 against n ≤ C. ∎

**5.3 H10 lower bound** (H10DEC). C_{h=10} = 1 + C(103 ports, P104 labels).

*Proof.* M_88,88 ≠ 0 forces a row with 88 in both D and S. e₁₀ is orthogonal to every other label, so that row's pairing
rank is (rank restricted to the 103 ports) + 1, and restricting all rows gives a valid 103-port decoder. ∎

**5.4 Isolation sets** (FOOLSET). An isolation set in Q[D, S] has odd F₂ determinant, so its size is ≤ rank_F₂ Q[D, S] =
the row's climb (≤ 9 on P104). A partial-permutation certificate Z must carry the whole diagonal, so Z = I. ∎

**5.5 Lifted labels** (LIFTDEC). Under the lift q ↦ (q, 1) with form x·y + st, the pairing becomes G mod 2.

- Under the bare row law, 13 disjoint orthogonal frames give M = Σ 1_F 1_Fᵀ at pairing rank 0, so cost 0. The lift
  removes the constraint rather than cheapening the decoder.
- With nondegenerate owned frames, a row covering a clique W has f_start ⊆ f_end ∩ W^⊥ and f_start ∩ rad = 0, so its
  climb is ≥ 2 dim W. Over cliques 2d/size ≥ 1, with equality only for full frames, so rectangle designs cost exactly
  104. ∎

**5.6 Mod 3 on F₂ labels** (MOD3DEC). 1/3 is a 2-adic unit, so 5.1 is unchanged. The labels carry no F₃ structure, so
there is no mod-3 identity. Rank-8 rows over Q have climb ≥ 7 (DECMINRANK, exhaustive), so C ≥ 56 over Z[1/6] for
rank-8 rows. ∎

**5.7 3-adic graded bound** (QDEC). Over F₃ the residual identity is exact. With max s/r = 2 over rectangles (attained by
A2⁴), the graded bound equals the Q-rank bound. ∎

---

## 6. Shape and framework

**6.1 L(N) ≥ N^τ** (SHAPE Route A). Induction on FINITE-PRECOMPILATION.md:198, using (n − s)^τ + s^τ ≥ n^τ, with base
L(e) = e. Hence a(N) ≤ a* for every compiled N. ∎

**6.2 Bootstrap, Theorem A.** κ_{j+1} = min(K, ε + (1 − ε)κ_j). Self-application helps only if the products row binds
(ε < K). Here ε = 1 − 10⁻¹⁴ ≫ K, so Δκ = 0. The binding rows (main, router, Gaussian) make no multiplier call
(08-assembly.tex:913-918; 05-layers.tex:645). ∎

**6.3 Theorem B.** With per-level cost ≥ c·x^{1−a*} per bit and Σ x_i ≥ log n − O(L), concavity of x^{1−a*} (with value 0
at 0) gives subadditivity. So one level is optimal, and an equal L-way split costs L^{a*} times more. ∎

**6.4 Slot knobs** (SLOTKNOB). a = 1 − ln(s/W)/ln m (05-layers.tex:645-650). At the frontier, m = N, W = B_N and
s = P_N, so the exponent is a(N) and 6.1 applies. The axis count f enters only through constants. ∎

**6.5 Symmetric-form fact** (NEWFRAME). Over F₂, the minimum number of terms vvᵀ summing to a symmetric B is rank B,
or rank B + 1 exactly when B is alternating and nonzero (an alternating form is not a sum of rank B squares, since each
vvᵀ has diagonal v). Over odd p every symmetric B is a sum of rank B terms c_j v_j v_jᵀ (diagonalise). [C
`oddradix.py`, exhaustive for small m.] ∎

**6.6 Lemma Q** (QUTRIT). At a character χ, det R(χ) = Δ(σχ)/Δ(χ) with Δ = det M. A λ-pseudo-reflection of image rank r
at every character needs Δ σ-homogeneous of degree e·r ≠ 0. A live plane with c, d ≠ 0 has Δ = cd − ab·k^{α+β}, which
is never homogeneous of nonzero degree. If α + β = 0, then det R = 1, which needs r ≡ 0 mod 3, impossible on a plane. ∎

**6.7 Endpoint wrappers** (SPECCHALLENGE, WRAPAUDIT). In odd p, K_{v,c}^j = r·D_a·P_s·K_{v,c}·D_b for every
non-isotropic v and j ≢ 0, with D chirps along v and P_s an F_p address scaling along v. The v-wrappers commute with
K_u for u ⊥ v.

The word's map is block-diagonal by roles (the contract), so linearity gives A·T_e·B = T_uniform with a diagonal B at
the input and a monomial A at the output. Nothing is left for the parent. [C `oddradix.py` for the identities.] ∎

**6.8 Lemma Z** (O1SPLIT). Work in A = F[k]/(k³ − 1) and let T = ∏ c_j u_j c_j⁻¹ · G with constant conjugators. If
T₀ = 0 (every role has a nonzero exponent) and Σ o(u_j) = m, then every unit has rank(u_{j,0}) = m − o(u_j).

Scope: each unit admits a free normalisation u′_j − I = X_j Ẑ_j(k) π_j with X_j: F^{o_j} → V_j an isomorphism and π_j
k-free. All catalogue units do; [[1, k], [0, k²]] does not.

*Proof.*

1. T − I = Σ_j (u′_j − I)·suffix_j, so Im(T(k) − I) ⊆ ΣV_j. Also (T − I)₀ = −I, so ΣV_j = F^m. Since Σ dim V_j = m,
   F^m = ⊕V_j.
2. In the basis X = [X_1 … X_n], B := X⁻¹TX = ∏_j (I + E_j φ_j) with φ_j = Ẑ_j Π_{j·} and Π = πX k-free. This is a
   Gauss–Seidel product.
3. Downward induction on j: row j of B is supported on block columns ≥ j, and for c ≤ j, (B_{j·})_c = δ_{jc}I + Ẑ_jΠ_{jc}.
   Degree 0 with B₀ = 0 gives Ẑ_{j,0}Π_{jj} = −I (c = j) and Π_{jc} = 0 (c < j).
4. Then u′_{j,0}X_j = X_j(I + Ẑ_{j,0}Π_{jj}) = 0, so rank u_{j,0} ≤ m − o_j, with equality when u_0 − I has rank
   ≤ o_j. rank(u_0) is invariant under k-free left and right multiplication. ∎

A real word must hit the target at two characters (ζ = 1 and ζ = ω) with the same constant conjugators. One character
with free conjugation is exact only in radix 2.

**6.9 Radix-3 det argument** (C3NATIVE). N = G·N_rat·G⁻¹ with N_rat k-free gives det R = 1 per native. So o = 1
admissible units (det R = ω^e, e ≠ 0) are illegal alone. The split swap diag(k, 1)·S·diag(k, 1)⁻¹ has det R = 1 and
o = 2. ∎

**6.10 Radix-3 target is H** (R3BUILD).

- Lemma scalar-motifs (03-motifs.tex:89-115) requires the net map of every invocation to be I.
- A side wire s → t is lossless only if ⟨q_s⟩ ⊆ q_t^⊥ (03:402-405), so the centre is δ on every label-non-orthogonal
  cell.
- With M_net = I and B_tt ≠ 0, MULTIHOP Thm B (rank_F₃(M̄∘B) ≤ total loss for 3-integral scalars) gives c ≥ v. ∎

**6.11 Thm B is vacuous with 1/3** (R3THIRD). With a 1/3 the scaled network computes 3M ≡ 0 mod 3 on every non-orthogonal
cell, so rank_F₃(3M∘B₃) = 0. What survives is rank_Q(M) ≥ 112/rank_Q G = 14, from rank(A∘B) ≤ rank A·rank B. ∎

**6.12 Free natives are not involutive** (RES-CONTRACT). Take M = [[a, bq], [c/q, d]] with q-free entries and
R = σ(M)M⁻¹. Then tr R = 2(1 + 2t), det R = 1 and R² = (tr R)R − I. R² = I forces abcd = 0 and ab(ad + bc) = 0, which
leaves only an even diagonal or the swap monomial. ∎

**6.13 No non-linear ingredient** (NONLIN). Native opcodes are MOVE/INIT/CLEAR/SCALE/COPY/ADD
(p104-main-wire-native/native.py:59-77). A product gate has zero degree-1 part, so deleting it leaves a linear program
with the same endpoint, and it cannot park or cancel the odd unit. ∎

**6.14 Single-step anchors are illegal** (ANCHOR9). The anchor relay must ADD the owned snapshot O_t. O_t lives on Y_t's
chain inside q_t^⊥ (dim ≤ 8), and ADD needs equal frames. So the relay needs a stop of dimension 1..8 after the X read,
i.e. ≥ 2 climb steps. ∎

**6.15 Node cut** (GRASSCUT). For a frame set U, every required non-helper state held in U lies in span(entries into U
from outside + helper arrivals into U), so arrivals(U) ≥ r_U. Helper transport is free, so pricing arrivals as stops
is unsound. The sound version charges each helper's single end stay. ∎
