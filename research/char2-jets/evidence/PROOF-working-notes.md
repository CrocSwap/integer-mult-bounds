# struct: principled route to (A) at T = 3 — the characteristic-2 shadow

Status keys: PROVEN / CHECKED (exact, script named) / OPEN.

## 1. Lemma CR2 (characteristic-2 realisation) — PROVEN

Let E = {(t,s) : t ≠ s, B_ts = 1} be the off-diagonal support of an admissible B. Suppose there are a field K of
characteristic 2 and vectors P~(t), Q~(s) ∈ K³ with
 (i) supp P~(t) ⊆ π(t), supp Q~(s) ⊆ σ(s);
 (ii) P~(t)·Q~(s) = 0 for every (t,s) ∈ E;
 (iii) P~(t)·Q~(t) ≠ 0 for every t.
Then cost(B) ≥ v.

*Proof.* B has entries in F2 ⊆ K. N := Σ_j D(p~_j) B D(q~_j) has N_ts = B_ts P~(t)·Q~(s), so N = diag(P~(t)·Q~(t)),
rank v. And rank_K D(p~_j) B D(q~_j) ≤ rank_K B[supp p~_j, supp q~_j] ≤ rank_F2 B[R_j, A_j] by (i). ∎

This is Lemma B with the roles swapped: Lemma B moves B to the field of the geometry (Q), and CR2 moves the geometry to
the field of B (char 2). CR2 depends only on E and is **down-closed**: a realisation of E realises every E′ ⊆ E. So
**if the full incidence pattern E_full = `free` is CR2, (A) holds for the configuration for every admissible B at once.**
Degenerate realisations are allowed: points may coincide, lines may coincide, extra incidences and extra zero
coordinates are allowed; the only non-incidences demanded are the v diagonal ones.

*T = 2 (Lemma A) is a one-line corollary:* in P¹ an incidence is an equality p(t) = q(s)^⊥, so any injection of the
finitely many used points of P¹(Q) into P¹(F̄2) fixing [1:0] and [0:1] and sending full-support points to full-support
points realises the whole pattern.

## 2. Data — CHECKED (cr2.py exhaustive DFS over GF(2^k); t1.py, t2.py, t3.py)

- **Full pattern CR2 for every stored configuration except tied_min** (t3.py): aff14, cech_v8, cex_joint_v7,
  cex_wholeTS_v9, gad, nojoint_21_1..14, supmin_fail_v8 realise over GF(2); cex_min_1 (v = 19, 114 incidences) over
  GF(4) (none over GF(2)). So (A) holds on all of them for every B, by Lemma CR2 alone (no SAT, no certificate).
  In particular cost(cex_min_1) ≥ 19 for every B, where every order/label certificate stopped at 18.
- **tied_min: full pattern NOT realisable** over GF(2), GF(4), GF(8), GF(16) (exhaustive). Reason: tied_min is the
  complete quadrangle a₁..a₄ whose diagonal points are the coordinate vertices e₁, e₂, e₃ (the supports force each
  side through its e_k). In characteristic 2 the diagonal points of a quadrangle are collinear (Fano), but e₁e₂e₃ is a
  frame: tied_min is the **anti-Fano (non-Fano) configuration**, the canonical "1 + 1 ≠ 0" gadget.
- **All 217 optima of tied_min are CR2 over GF(2) itself** (t1.py; off-diagonal ones 12, 14, 16, 18, 24). Every optimum
  drops exactly enough of the anti-Fano incidences to become Fano-compatible.
- All minimisers and all cost-(min+1) matrices of cex_joint_v7, cech_v8, supmin_fail_v8, cex_wholeTS_v9,
  nojoint_21_1..4 are CR2 over GF(2) (t2.py).
- verify_cr2.py: end-to-end — for the realisations of cex_min_1 (GF(4)), cex_joint_v7, gad, aff14 (GF(2)): supports
  inside π, σ; for 200 random admissible B each, N = Σ_j D(p~_j) B D(q~_j) over GF(2^k) is diagonal with nonzero
  diagonal, and cost(B) ≥ v. CHECKED.

## 1b. Corollary (2-adic tropical reduction) — PROVEN

Let ν be a valuation on a field K ⊇ Q extending v₂ (e.g. Q₂(2^{1/n})), ϖ a uniformiser-power with ν(ϖ^{a}) = a for
a ∈ (1/n)Z. If some a ∈ ((1/n)Z)³ satisfies, for every t,
  ν(p(t)·q(t)) = min_{j∈π(t)} (ν p_j(t) + a_j) + min_{j∈σ(t)} (ν q_j(t) − a_j),
then the full pattern is CR2, so (A) holds for every B. *Proof.* Replace p_j ← ϖ^{a_j} p_j, q_j ← ϖ^{−a_j} q_j: all
products p(t)·q(s), hence all incidences and supports, are unchanged. Scale each vector to minimum valuation 0 and
reduce to the residue field (char 2): incidences reduce to incidences, supports can only shrink, and the hypothesis
says the diagonal product has valuation exactly 0, so it reduces to a nonzero element. ∎
*Special case a = 0:* **if every primitive integer p(t), q(t) has p(t)·q(t) odd, (A) holds for every B.** The ultrametric
inequality always gives "≥"; equality fails exactly when the leading terms cancel — the two-odd-terms cancellation of
tied unit lines. tied_min: p·q = ±1 ± 1 = ±2 on every line, and min_j a_j − max_{j≠k} a_j ≤ 0 < 1 for every a, so no
tropical scaling works — consistent with its being anti-Fano.

## 1c. The per-B alternative and direct sums — PROVEN (remark)

Write Qmin(E) := min Σ_j rank_Q B′[R_j,A_j] over rational B′ with supp B′ ⊆ E ∪ diag, B′_tt ≠ 0. Lemma B: Qmin ≥ v.
Witnesses for cost(B) ≥ v: **(L)** Qmin(supp B) ≤ cost(B); **(C)** supp B is CR2.
On a direct sum X ⊕ Y (no incidences between), Qmin, cost and CR2 behave additively / conjunctively, so (L) can borrow
slack between components: e.g. tied_min's full B has cost 24 but Qmin = 12 (a lifted optimum is a sub-support), so
B_X ⊕ B_full satisfies (L) even for a non-liftable B_X with excess < 12. The alternative "(L) or (C)" fails on
B_X ⊕ B_Y as soon as B_X has Qmin(supp B_X) > cost(B_X) and B_Y is a **non-CR2 B with Qmin(supp B_Y) = cost(B_Y)**,
e.g. a non-CR2 minimiser of a tight configuration Y. None is known: every optimum of tied_min is CR2. So the
alternative, per B, is equivalent on direct sums to "no tight non-CR2 minimiser coexists with a non-liftable B";
the robust form is per strong component (Lemma SCC), and inside a component it is the selection question of §3.

## 2. The char-2 side is complete: generic realisation = split certificate — PROVEN (completeness conditional on a standard min-max, CHECKED on instances)

**Lemma GR.** For any field K ⊇ F2 and any support-compatible P~, Q~ ∈ K^{v×3} (supp p~_j ⊆ R_j, supp q~_j ⊆ A_j;
**no incidence or diagonal condition**), cost(B) ≥ rank_K (B ∘ P~Q~ᵀ), since B ∘ P~Q~ᵀ = Σ_j D(p~_j) B D(q~_j).
The best such bound is the generic rank GR(B) := rank_{F2(X,Y)} (B ∘ XYᵀ) (X_tj, j ∈ π(t), Y_sj, j ∈ σ(s), indeterminates).
CR2 is the special case where B ∘ P~Q~ᵀ is diagonal. Hybrid: it suffices that the *violated* incidences
{(t,s) ∈ E : p~(t)·q~(s) ≠ 0} form an acyclic digraph (then B∘P~Q~ᵀ is triangular after reordering).

**Lemma Split (expansion of GR).** mod 2, det(B ∘ XYᵀ) = Σ_σ Π_t B_{tσ(t)} x(t)·y(σ(t)); the coefficient of the monomial
Π_t x_{a(t)}(t) Π_s y_{b(s)}(s) is per(B ∘ K_ab) = det_F2(B ∘ K_ab), K_ab[t,s] = [a(t) = b(s)]. After permuting,
B ∘ K_ab = ⊕_c B[R′_c, A′_c] with R′_c = a⁻¹(c) ⊆ R_c, A′_c = b⁻¹(c) ⊆ A_c. Hence
 **GR(B) = SPL(B) := max over row-partitions {R′_c ⊆ R_c} and column-partitions {A′_c ⊆ A_c} of Σ_c rank B[R′_c, A′_c]**
(same argument on minors), and GR(B) = v iff a **perfect split** exists: three square F2-nonsingular submatrices, one
inside each block, whose row sets partition the lines and whose column sets partition the lines. A perfect split
gives cost(B) ≥ v directly (rank of a block ≥ rank of a submatrix): an elementary certificate.

**Min-max (standard independent-matching / linking-system duality, Rado–Edmonds type; cited from memory, not re-proved here).**
 SPL(B) = min_{S,T ⊆ [v]} (v − |S|) + (v − |T|) + Σ_c rank_F2 B[S ∩ R_c, T ∩ A_c].
"≤" is elementary; equality: CHECKED on 300 random (not necessarily admissible) instances, v = 3–6, including 92 with
SPL < v (t9.py: GR by evaluation over GF(2^16) vs exhaustive min over S, T; 0 mismatches).

**Corollary (completeness; conditional on the min-max).** If (A) holds for every sub-configuration W (cost_W(B|_W) ≥ |W|), then for all S, T:
Σ_c rank B[S∩R_c, T∩A_c] ≥ cost_{S∩T}(B|_{S∩T}) ≥ |S∩T| ≥ |S| + |T| − v, so SPL(B) = v. Since (A) is hereditary:
 **(A) at T = 3 ⟺ every admissible B on every configuration has a perfect split.**
So the char-2 Hadamard certificate is *complete* (unlike the char-0 one, whose completeness is (Q ≤ F2)), and the
anti-Fano obstruction of §1 is an obstruction only to the *diagonal* (CR2) form, never to the generic form.
Data: GR(B) = v for 100 random B at each of four densities on tied_min (incl. the full non-CR2 B), cex_min_1, gad,
aff14, cex_joint_v7 (t7.py) — consistent with (A), as it must be.

**Principal split (COL), stronger and FALSE in general.** a = b = c(t) ∈ D(t): cost(B) ≥ Σ_c rank B[L_c, L_c]
(L_c = c⁻¹(c) ⊆ D_c). It holds for all 217 optima, the full B and 200 random B of tied_min (t10.py), but fails on the
private digon (two lines with D = {j}, B = J₂: L_j = both lines, singular), where the perfect split uses a ≠ b.
COL generalises MAS-sum (acyclic L_c) from unit-triangular to nonsingular principal minors.

## 3. The multiplicative realisation: (A) without wild incidences and harmonic lines — PROVEN

Call an incidence (t,s) (in some block) **binomial** if |π(t) ∩ σ(s)| = 2 and **wild** if |π(t) ∩ σ(s)| = 3 (a
full-support point on a full-support line; M1's obstacle). Call a line t **harmonic** if |D(t)| = 2 and the two terms
of p(t)·q(t) are equal: p(t)·q(t) = 2 p_i(t) q_i(t). Geometrically (when q(t) passes through the vertex e_k): q(t) is
the **harmonic conjugate** of the line e_k p(t) with respect to the two frame sides through e_k. Let H = harmonic lines,
W = the wild incidences, F = lines with both p(t) and q(t) of full support (|D| = 3; F ∩ H = ∅).

**Map φ.** Let K = F2(z_p : p prime) and φ : Q* → K* the homomorphism with φ(−1) = 1, φ(p) = z_p; φ(0) = 0.
Set P~(t) = φ(p(t)), Q~(s) = φ(q(s)) entrywise. Supports are preserved exactly.
- A binomial incidence x_i y_i + x_j y_j = 0 means x_i y_i = (−1)·x_j y_j, so φ(x_i)φ(y_i) = φ(x_j)φ(y_j), i.e.
  P~(t)·Q~(s) = 0 in characteristic 2. **Every binomial incidence is preserved.**
- Diagonal: P~(t)·Q~(t) = Σ_{j∈D(t)} φ(p_j q_j) is a sum of |D(t)| Laurent monomials (φ(±n) = monomial of |n|),
  zero iff they cancel in pairs: never for |D| ∈ {1, 3}; for |D| = 2 iff |p_i q_i| = |p_j q_j|, i.e. (as p·q ≠ 0)
  iff t is harmonic. **The diagonal vanishes exactly on H.**

**Theorem B2.** Let X ⊆ [v] \ H be a set of non-harmonic lines containing no directed cycle of wild incidences. Then
**cost(B) ≥ |X| for every admissible B.** In particular:
 (i) **no wild incidence and no harmonic line ⇒ the full pattern is CR2 ⇒ (A) holds for every B**;
 (ii) no wild incidence ⇒ cost ≥ v − |H|;
 (iii) in general cost ≥ v − |H| − |F| + MAS(W[F]) (wild edges join a full point to a full line, so a wild cycle
   lies inside F).
*Proof.* N := B ∘ P~Q~ᵀ has rank ≤ cost (Lemma GR). Off the diagonal N_ts ≠ 0 only if B_ts = 1 and the incidence
is not preserved, i.e. wild. N[X,X] is triangular in a topological order of W[X] with nonzero diagonal. ∎
By duality (P ↔ Q, B ↔ Bᵀ) nothing changes (both notions are symmetric). Compare Theorem M1 (no full-support point:
cost ≥ v/2): in that class W = F = ∅, so B2 gives **cost ≥ v − |H|**, and (A) unless a harmonic line exists.
CHECKED (t11.py, phi.py): 400 random no-wild configurations (v = 5–9, entries up to 3): φ over GF(2^16) (random z_p)
preserves every block incidence (assert), the zero diagonals are exactly H (400/400); exhaustive minimum cost ≥ v − |H|
on all 379 with f ≤ 20.

**Where this leaves (A).** A counterexample needs harmonic lines or wild cycles. tied_min is no-wild with **all 12
lines harmonic** (p·q = ±1 ± 1): the anti-Fano of §1 *is* the harmonic-conjugate configuration, and "1 + 1 = 0"
is exactly "harmonic conjugate = itself". The two residual mechanisms are thus the two classical char-2 phenomena:
harmonic conjugation (multiplicative, −1 ↦ 1) and the additive trinomial 1 + xy + x′y′ = 0 (wild).

## 4. Jets: the "higher-order construction" — valuative CR2, and a SAT-free proof of cost(tied_min) = 12

**Lemma VCR2 (valuative CR2) — PROVEN.** Let K be a field of characteristic 2 with a valuation ν (e.g. F((ε))), and
P~, Q~ support-compatible over K; put w_ts = ν(P~(t)·Q~(s)). If every directed cycle C of E (incidences in blocks)
satisfies Σ_{(t,s)∈C} w_ts > Σ_{t∈C} w_tt (in particular all w_tt < ∞), then cost(B) ≥ v for every B with
off-diagonal support in E. *Proof.* N = B ∘ P~Q~ᵀ has rank ≤ cost (Lemma GR). det N = Σ_σ Π_t N_{tσ(t)}; a cycle cover
σ ≠ id splits into fixed points and cycles of E, so its term has valuation > Σ_t w_tt, the valuation of the identity
term. No cancellation: det N ≠ 0. ∎
Special cases: CR2 (w = ∞ on E); the acyclic hybrid (every cycle has an edge with w = ∞); B2 (§3).

**Corollary J (first-order jets, no-wild class) — PROVEN.** Let C be no-wild, φ as in §3, and suppose there are
support-compatible X, Y over K with
  (J1) φp(t)·Y(s) + X(t)·φq(s) = 0 for every incidence (t,s) of E   (incidences preserved to first order),
  (J2) δ′_t := φp(t)·Y(t) + X(t)·φq(t) ≠ 0 for every harmonic t     (harmonic points leave their lines at order 1).
Then with P~ = φP + εX, Q~ = φQ + εY over K((ε)): w = ∞ or ≥ 2 on E, w_tt = 0 on non-harmonic lines and = 1 on
harmonic lines, so every cycle has Σ_edges ≥ 2|C| > |C| ≥ Σ_vertices, and **(A) holds for every B**.
(J1) is a homogeneous linear system and (J2) asks v linear functionals to be nonzero on its solution space; over an
infinite field it suffices that **each** δ′_t is not identically zero on the solution space (a vector space is not a
finite union of proper subspaces). So Corollary J is a B-independent **linear-algebra certificate**.

**Theorem T′ (cost(tied_min) ≥ 12, by hand).** φ(tied_min): all entries are ±1, so every point becomes the Fano
centre c = (1,1,1) and every class-k line becomes the Fano line ℓ_k through c and e_k (ℓ₀ = (0,1,1), ℓ₁ = (1,0,1),
ℓ₂ = (1,1,0)) — the Fano collapse of the anti-Fano. Write f_k(t) = X(t)·ℓ_k and g(s) = c·Y(s). Since ℓ₀+ℓ₁+ℓ₂ = 0 in
char 2, f₀+f₁+f₂ = 0 for each t, and (X(t) of full support) any such triple occurs; g(s) is arbitrary (Y(s) has two
free entries). (J1) for an incidence t → s, s of class k: f_k(t) = g(s). The class-k lines on the side {x,y} of M_k
are the two lines (u,k), u in the other pair; so all lines t whose point lies on a side S of M_k need f_k(t) = G_k(S),
the common g-value of the lines carrying S. (J2) for line (u,k): f_k = G_k(side ∋ u) ≠ g(u,k) = G_k(side ∌ u), i.e.
h_k := G_k(S) + G_k(S′) ≠ 0 for the two sides S, S′ of M_k. The constraint f₀+f₁+f₂ = 0 at the four points reads:
at a, Σ_k G_k(side_k(a)) = 0; at the vertex b paired with a in M₀: the same sum + h₁ + h₂ = 0, so h₁ = h₂; likewise
h₀ = h₂, h₀ = h₁. **Solution: h₀ = h₁ = h₂ = h ≠ 0**, any G with Σ_k G_k(side_k(a)) = 0. So (J1)+(J2) are solvable,
and cost(tied_min) ≥ 12 for every B; with an optimum, = 12. No SAT, no enumeration. ∎
CHECKED from the hand formula (tied_min_jet_cert.py, exact over F2, so K = F2((ε)) suffices): h = 1 gives (J1) on all
72 incidences and (J2) on all 12 lines; N = B∘P~Q~ᵀ at a random ε ∈ GF(2^16) has rank 12 for the 217 optima, the full B
and 300 random B (518/518). Also (tangent.py, t15.py): the (J1) solution space of the full 72-incidence pattern has dimension 27 over GF(2^16)
and every one of the 12 functionals δ′_t is nonzero on it.

**Reading.** tied_min = anti-Fano is *not* realisable in characteristic 2 (§1), but it is realisable **to first order
around its Fano collapse**: exactly the equal-characteristic shadow of its 2-adic picture (diagonal products of
valuation ν(2) = 1, incidences of valuation ∞ ↔ diagonal of ε-order 1, incidences of ε-order ≥ 2). This is the
"higher-order construction": the obstruction to char-2 realisation (harmonic conjugation, 1 + 1 = 0) is removed by a
jet of order 1, and the tightness of tied_min is the statement that the jet has order exactly 1 on every line.

## 5. How far the first-order jet reaches — CHECKED; the obstruction — PROVEN

**Data (t16.py, t17.py; exact linear algebra over GF(2^16), random z_p).** Corollary J's hypothesis holds on
**all 4095 sub-configurations of tied_min** and on **1500 random all-harmonic F2S configurations** (v = 4–14, entries
±r^a, r ∈ {2,3,5}): (A) holds on each for every B by a linear-algebra certificate. On 1892 random no-wild
configurations with harmonic lines (mixed supports), it holds on 1889 and **fails on 3** (stored jetfail/jf0..2.json;
v = 11, 9, 9): one or two harmonic lines whose δ′ vanishes on the whole first-order tangent space. Those three are
also not CR2 (GF(2), GF(4), GF(8)), but they are far from tight (exhaustive min cost 12 for v = 9, 14 for v = 9), so
they need either a jet of order ≥ 2, a degenerate base point other than φ, or a B-dependent argument.

**Lemma F (the obstruction is a binary flow) — PROVEN.** Write X(t) = φp(t) ∘ ξ(t), Y(s) = φq(s) ∘ η(s) (every
support-compatible tangent has this form). On a binomial incidence over the pair {i,j}, (J1) becomes
Δ_ij ξ(t) = Δ_ij η(s) with Δ_ij ξ = ξ_i + ξ_j; for harmonic t with D(t) = {i,j}, (J2) is Δ_ij ξ(t) ≠ Δ_ij η(t).
So J fails at t iff the harmonic equation is an F2-combination of incidence equations: a set Z of incidence edges
plus the harmonic edge h with, at each object whose support has size 2, an even number of Z-edges, and at each object
of full support, equal parities of Z-edges over the three pairs {01}, {02}, {12}. Any such Z has |Z ∩ incidences| even
(evaluate at the sign labels ξ_j(t) = [p_j(t) < 0], η_j(s) = [q_j(s) < 0], which give 1 on every incidence and 0 on
every harmonic diagonal). On objects with two-element supports only (a cycle in P¹), Z would be a cycle with an odd
number of incidences, so **no obstruction exists there** — the Q-geometry (−1 ≠ 1) enters exactly through this parity.
With full-support objects the parity condition is "Fano-like" (Δ₀₁ + Δ₀₂ + Δ₁₂ = 0) and flows of even incidence
count can exist (jf0..2).

Full collapse (every z_p := 1, t19.py) does not rescue jf0..2: the same harmonic lines stay immovable at order 1.

## 6. Summary and conjecture

- Duality answered: the char-2 Hadamard witness in generic form (GR = perfect split) is complete given (A), so a per-B
  "(L) or (C)" alternative carries no independent content. The real hierarchy is in the char-2 *realisation order*:
  order 0 (φ / CR2: everything without harmonic lines or wild cycles), order 1 (jets: tied_min, all its 4095
  sub-configurations, all 1500 random harmonic F2S configurations), higher / unknown (jf0..2, harmonic lines immovable
  at order 1, all with slack ≥ 3).
- Decomposition (track 1): tied_min = anti-Fano = harmonic-conjugate configuration; its 44 minimal non-CR2
  sub-configurations (32 of 6 lines: four quadrangle vertices + six sides, each point paired with a side missing it;
  12 of 7 lines) are the atoms of the char-2 obstruction; the six-line ones are tight. Tightness of tied_min = the jet
  has order exactly 1 on every line (diagonal ε-order 1 = ν₂(p·q)).
- **Conjecture (2-adic shadow).** Every configuration over Q admits a char-2 valued realisation (over F̄2((ε))) whose
  diagonal is strictly dominant on every directed cycle of incidences (Lemma VCR2); this would prove (A). It must fail
  for T ≥ 7 (E7/E8), which is a consistency check only.
- Open: harmonic lines immovable at first order (jf0..2), and wild cycles (three-term incidences), which φ breaks.

## 5b. Order-2 jets on jf0..2 — CHECKED (jet2.py, t20–t23)

**Order-2 scheme.** P~ = φ₀P + εX₁ + ε²X₂, Q~ likewise (φ₀ = full collapse, all nonzero entries ↦ 1, defined over F2).
Target: every incidence of ε-order ≥ 3, every diagonal of order ≤ 2 (non-harmonic: 0); VCR2 then applies. With
(X₁,Y₁) ∈ V = ker A (A = the first-order incidence functionals), the order-2 equations A(X₂,Y₂) = b, b_e = X₁(t_e)·Y₁(s_e),
are solvable iff every left-kernel vector z of A gives q_z(X₁,Y₁) = Σ z_e b_e = 0. For an immovable line t
(δ′_t = Σ c_e A_e), the order-2 diagonal is the constant **Q_t = X₁(t)·Y₁(t) + Σ c_e b_e**, independent of (X₂,Y₂).
**Result: for all four immovable lines (jf0: line 0; jf1: line 7; jf2: lines 0, 2), Q_t is identically zero as a
polynomial on V** (t21.py), so the order-2 diagonal vanishes for every jet over every char-2 field. Over F2 the search
finds no point with all q_z = 0 and Q_t = 1 for jf1, jf2 (dim V = 22, 24; exhaustive); the identity explains why.
So the immovability persists to order 2 for a structural reason: the Lemma F flow Z_t also kills the quadratic term.
Order ≥ 3 was not tested. Conjecture: the flow is an exact char-2 obstruction, so **no B-independent valuative
certificate exists for jf0..2**.

**These are not counterexamples, and the B-dependent test works on the optima.**
- jf1: v = 9, exact minimum cost 12 (192 minimisers); 186 pass the first-order jet test on E = supp B (and are CR2).
  The other 6 pass neither test, but cost ≥ v holds there anyway.
- jf2: v = 9, exact minimum cost 14 (12 928 minimisers); every one passes the jet test on E = supp B and is CR2.
- jf0: v = 11, f = 41; small CNF "cost ≤ K" (satlib) is UNSAT for K ≤ 15, so **cost(jf0) ≥ 16 > v**.

**Three-term (wild) cycles (t24.py).** All 300 random configurations that contain a directed cycle of wild incidences
(v = 6–12, entries ≤ 3) are realisable in char 2 with the full pattern (293 over GF(2), 7 over GF(4)), so (A) holds on
each by Lemma CR2. φ breaks wild incidences, so this is not covered by any theorem here: **OPEN** in theory, never an
obstruction in the data.

## 7. Final statement for packaging

**PROVEN.**
- Lemma CR2 (§1): a char-2 realisation of supp B (supports ⊆, diagonal ≠ 0) gives cost(B) ≥ v. Corollaries: Lemma A
  (T = 2) in one line; 2-adic/tropical reduction (§1b): primitive diagonals all odd (after some rescaling) ⇒ (A).
- Lemma GR / Split (§2): cost ≥ rank_K(B ∘ P~Q~ᵀ) for any support-compatible P~, Q~ in char 2; the generic rank equals
  the best split Σ_c rank B[R′_c, A′_c]. (That this split is complete given (A) relies on a standard min-max, which is
  CHECKED on instances, not re-proved.)
- Theorem B2 (§3): with φ(−1) = 1: cost ≥ v − |H| − |F| + MAS(W[F]). No wild incidences and no harmonic lines ⇒ (A)
  for every B; no wild incidences ⇒ cost ≥ v − |H|.
- Lemma VCR2 (§4): a char-2 valued realisation whose diagonal is strictly dominant on every directed cycle gives
  cost ≥ v.
- Corollary J (§4): the first-order jet test, linear algebra, independent of B.
- Theorem T′ (§4): cost(tied_min) = 12 by hand (Fano collapse, h₀ = h₁ = h₂ ≠ 0).
- Lemma F (§5): the only first-order obstruction is a binary flow through the harmonic edge, with an even number of
  incidences; there is none when every object has a two-element support.
**CHECKED (exact).**
- CR2: the full pattern of every stored configuration except tied_min; all 217 tied_min optima.
- B2/φ: 400 random no-wild configurations (incidences kept; zero diagonals = H; cost ≥ v − |H|).
- Corollary J: all 4095 sub-configurations of tied_min; 1500/1500 random all-harmonic F2S; 1889/1892 random
  no-wild configurations with harmonic lines.
- T′: tied_min_jet_cert.py (exact over F2; 518/518 matrices B of rank 12).
- jf0..2 (§5b): immovable at order 1 and order 2 (Q_t ≡ 0); (A) holds there: costs 12, 14 and ≥ 16 against
  v = 9, 9, 11.
- Wild cycles: 300/300 fully CR2.
**OPEN.** (A) at T = 3.
- Conjecture (2-adic shadow), B-dependent form: for every B, or at least for some minimiser, supp B has a char-2
  valued realisation with a cycle-dominant diagonal. The B-independent form is likely false (jf0..2).
- Harmonic lines immovable at orders 1–2: does the flow obstruct at every order?
- A structural theorem for wild cycles.
- Completeness of the split min-max (standard, not re-proved here).
