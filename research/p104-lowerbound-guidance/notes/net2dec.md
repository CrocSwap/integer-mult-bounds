# NET2DEC N2D (Nov 20, Opus, theory + small exact fuzz). Own code: ngfuzz.py, ngfuzz2.py, ng2node.py, ngmin.py (-> ng1.log, ng2.log, ngmin5.log). 1 proc, threads=1, seconds. No Lean, advisor, push or kill.

VERDICT: PARTIAL. D >= 56 is NOT reduced to Wall56. What does transfer exactly is every "potential-type" (2-adic rank) decoder floor, with the drop D in place of the mass C. New [P]: half-integer networks satisfy 2n <= (h+1)·D, i.e. **D >= 21 on P104**. That is the same as the decoder floor (ADICWALL §2) and beats WALLCORE's 16. Per-row decoder laws do NOT transfer. Smallest counterexample: 2 nodes, 1 relay, h=5, D=4.
How this differs from earlier lanes: RS §3 / HT §1 built F2 potentials (e=0) and called the Z/4 lift "not linear". Here the lift is handled with inclusion–exclusion generators, and adding the forward and mirror bounds makes the relay cross-terms cancel exactly.

## 0. Setting, scope
- NetW as in Net8.lean, over labels q_p in F2^h (n ports, odd weight). Q_tp = q_t·q_p in {0,1} ⊂ Z. M = G N F with N = (I−H)^{-1}, and M∘Q = diag(c): diagonal c_t ≠ 0, odd off-diagonal cells 0, even cells free.
- Class HALF-NET: there is a gauge (node scalings λ_k, reader/port scalings) in which F, H, G are 2-adically integral and v_2(c_t) <= 1 for all t.
  - Feasibility is a difference-constraint system on the DAG.
  - E8/NET8 (W = w, F = 2u, c = 2) is inside. Integral networks (v(c) = 0) are inside.
  - The class is not compared with WALLCORE's HALF3.
- Notation: χ_v(p) = v·q_p in {0,1}. T̃_r(v) = χ_v ⊙ r in (Z/4)^n, which is Z-linear in r. Content r_k = row k of NF = F_k + Σ_j H_kj r_j. Drop d_k = dim a_k − dim b_k, and D = Σ d_k.

## 1. THEOREM NG (network graded 2-adic floor) [P]
For a HALF-NET network:
- (fwd) n <= Σ_k [ C(d_k+1,2) + ι_k·d_k·(h − dim a_k) ], where ι_k = 1 iff k receives a relay;
- (mir) n <= Σ_k [ C(d_k+1,2) + o_k·d_k·dim b_k ], where o_k = 1 iff k sends a relay;
- (sum) 2n <= Σ_k d_k[(d_k+1) + (h − dim a_k) + dim b_k] = **(h+1)·D**. On P104 (n=104, h=9) this gives **D >= 20.8, so D >= 21**, for any relay graph and any rank.

Proof.
1. Inclusion–exclusion [P]. For 0/1 values, x_1 ⊕ … ⊕ x_s ≡ Σ x_i − 2 Σ_{i<j} x_i x_j (mod 4). So if v = Σ v_i over F2, then χ_v ≡ Σ χ_{v_i} − 2 Σ_{i<j} χ_{v_i} χ_{v_j} (mod 4).
2. Π̃_k := the Z/4-span of {T̃_{r_k}(v) : v ∈ b_k^⊥}. Take a basis u_1..u_m of a_k^⊥ (m = h − dim a_k) and extend it by c_1..c_d (d = d_k) to a basis of b_k^⊥. By step 1, Π̃_k is spanned by:
   - T̃(u_i) and T̃(c_a);
   - 2χ_uχ_{u'} r_k, 2χ_uχ_c r_k and 2χ_cχ_{c'} r_k, for pairs of basis vectors.
3. Relay closure. Let u ∈ a_k^⊥. Then χ_u F_k = 0, since q_p ∈ a_k on supp F_k. Also u ∈ b_j^⊥ for every relay j→k, since b_j ⊆ a_k. Hence:
   - T̃_{r_k}(u) = Σ_j H_kj T̃_{r_j}(u) ∈ Σ_j Π̃_j;
   - 2χ_uχ_{u'} r_k = Σ_j H_kj [T̃_{r_j}(u) + T̃_{r_j}(u') − T̃_{r_j}(u+u')] ∈ Σ_j Π̃_j.
   So Π̃_k ⊆ Σ_{j→k} Π̃_j + span Γ_k, where Γ_k consists of:
   - the d elements T̃(c_a);
   - the C(d,2) elements 2χ_cχ_{c'} r_k;
   - the m·d cross terms 2χ_uχ_c r_k. These exist only if ι_k = 1; with no relay in, r_k = F_k and they vanish.
4. Row t of M∘Q (mod 4) equals Σ_k G_tk T̃_{r_k}(q_t). Here q_t ∈ b_k^⊥ whenever G_tk ≠ 0, so each term lies in Π̃_k. Inducting in topological order, every row lies in span ∪_k Γ_k.
5. Lifting gives an integer R ≡ M∘Q ≡ diag(c) (mod 4) with rank_Q R <= Σ|Γ_k|. Multiply the rows with v(c_t) = 0 by 2. The result is ≡ 2·diag(odd) (mod 4), so (that matrix)/2 is invertible mod 2 and rank R = n. This gives (fwd).
6. (mir) is (fwd) applied to the dual NetW (b^⊥, a^⊥, G^T, F^T, H^T), which is legal by RZ §5, with M^T∘Q = diag(c). Its in-relays are the original out-relays, and h − dim(b^⊥) = dim b.
7. (sum): add (fwd) and (mir), using ι, o <= 1 and a − b = d. ∎
- For a relay-free network (ι = o = 0), (fwd) is exactly ADICWALL's n <= Σ C(r_k+1,2), with drop in place of price.
- Relays cost exactly the cross terms, and fwd + mir telescopes them to h+1 per unit drop. This is the same ratio as decoders, so the floor transfers with no loss.

## 2. THEOREM N4 (network half-level carry identity) [P]
- Integral gauge with M∘Q ≡ 2I (mod 4). Write X_walk := Q∘(cover/2) mod 2, where cover(t,p) = #{gather→deposit walks t←d←…←g←p whose scalars are all odd} = (ĜÑF̂)_tp, Ñ = Σ Ĥ^i over Z.
- Then over F2: I + X_walk = L with rank L <= 2D. Hence D >= rank_F2(I + X_walk)/2, which is HC's corollary with C replaced by D.
- Proof:
  1. Reducing mod 4 gives N ≡ Ñ + 2ÑH'Ñ. So M ≡ ĜÑF̂ + 2(G'N̄F̄ + Ḡ N̄H'N̄F̄ + Ḡ N̄F').
  2. Rows of Q∘(G'N̄F̄) lie in Σ Π̄_k, where Π̄_k = T_{r̄_k}(b_k^⊥). This is RS §3, dim <= D.
  3. The other two terms have rows Σ_d Ḡ_td T_{z_d}(q_t), where z_k = F'_k + Σ_j (H'_kj r̄_j + H̄_kj z_j).
  4. For v ∈ a_k^⊥: T_{z_k}(v) ∈ Σ_j (Z_j + Π̄_j). Therefore Σ Z + Σ Π̄ ⊆ Σ_k [T_{z_k}(C_k) + T_{r̄_k}(C_k)], with dim <= 2D. ∎
- The exact cost comparison holds: each unit of drop gives at most 1 rank unit to each of the two potentials, just as rank B_k <= 2r_k for decoder rows.
- Limit: the walk family's X is a rectangle family with even covers (decoder-shaped), but its row mass is unbounded. With free rectangle families X is arbitrary (doubled 1×1 rectangles), so N4 needs a structural bound on rank X_walk. It does not reach Wall56.

## 3. Tests [C]
- ngfuzz.py, random integral NetWs, labels = all odd vectors of F2^h, 2–6 nodes, entries in Z/4, μ4 = # Smith invariants of M∘Q not ≡ 0 mod 4:
  - h=3..6 legal (ng1/ng2, 15,000 nets): 0 violations of fwd, mir, sum or N4. fwd tight in about 100 cases.
  - CONTROL with the relay rule b_j ⊆ a_k dropped: fwd 1, mir 2–4, N4 25–31 violations. The tests have teeth.
- RELAXED law (decoder strength, no cross term: μ4 <= Σ C(d_k+1,2)) is FALSE for legal networks (ng2node, ngmin5.log).
  - Smallest counterexample, h=5: node j has a_j = F2^5, b_j = <2,8,20> (dim 3); a single relay feeds node k with a_k = b_j and b_k = <22>.
  - d = (2,2), D = 4, μ4 = 7 > 6 = Σ C(d+1,2). fwd bound 10, mir bound 12. Full F, G, H are in ngmin5.log.
  - So no node-preserving map "network → integral rows, row price <= drop" exists, even mod 4. Relays carry 2-adic content that rows of the same prices cannot.
- Adversarial anchors:
  - NET8/E8 (relay-free, D=56): 2·104 <= 10·56, true.
  - WALLCORE D=16 profile: 208 > 160, so it is excluded inside HALF-NET. Mirror alone gives 53 < 104. This agrees with WALLCORE's [P] that it cannot be realised.

## 4. Obstructions to the asked reduction (exact)
- O1 [P, trivial]. Given Wall56 plus E8, "every network has a decoder of mass <= D" ⟺ "every network has D >= 56". So the reduction must be structural; it cannot be a lemma that is easier than the goal.
- O2 [P+C]. Per-row decoder laws do not transfer to networks:
  - the Smith law (counterexample in §3);
  - and therefore rigidity, PRICE7, ALL-OR-NOTHING and Lemma T, which are all row-local.
  - Wall56 as stated (rational, row-supported) cannot be invoked on network data. Network data form walk families of unbounded row mass. G3 (RZ §1) separates them, but only in the bipartite model; in the symmetric model, universality is open.
- O3 (angle a). Its endpoint "network D<56 ⇒ decoder-wall counterexample" fails:
  - the network mod-4 object is a walk-family pseudo-decoder, not an object of row mass <= D (O2);
  - m4 >= 56 is strictly stronger than Wall56 (HC §6), so it is not an allowed premise.
- O4 (angle b).
  - The halves of a cut are not decoder targets: Y = content at the cut has no diagonal or odd structure.
  - Wall56 implies sub-walls only additively [P]: Σ_i m(T_i) >= 56 over any port partition, since direct sums of block decoders have zero cross cells. Hence m(T) >= 56 − |T^c|. Single-subset walls are not implied.
  - So cut-and-flatten reduces to NET9's μ-weighted bound, which has no positive floor without a waist (NETCUT).
- TRANSFER PRINCIPLE (what does reduce) [P for e = 0 (RS) and e = 1 (NG)]:
  - Any decoder floor proved as "n <= μ_{2^(e+1)} of a matrix ≡ M∘Q, generated by chart images χ_v ⊙ r over v ∈ b^⊥" holds for networks at the same per-drop rate.
  - So the missing premise for networks is exactly a POTENTIAL-TYPE Wall56: the HC half-cover law stated as a (Z/4)^n module bound on chart images. That statement is not the rational Wall56.

## 5. Next
1. LEAN lane (Sonnet): formalise NG. Spec: §1 steps 1–7. Abstract labels, F2 subspaces, Z/4 vectors; reuse the Net8 NetW with Z_(2) entries. A non-vacuity instance is the 2-node network above.
2. Add the NG fwd/mir rows (node types with in/out flags) to WALLCORE's joint IP (jlp2). It may lift 21 by combining with SOLE / CAP / clique-cut, but scopes must be intersected (HALF3 ∩ HALF-NET).
3. Decoder program: phrase any new half-level bound (HALFCANCEL / PRICE7 successors) as a chart-image module bound. Networks then follow by §1's telescoping.
