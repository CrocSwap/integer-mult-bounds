# NETTENSOR NT (Nov 20, Opus, theory + small exact). Own code: facts.py (-> facts.log), osip.py. 1 proc, threads=1, minutes. No SAT/Lean/advisor/push/kill.
How this differs from earlier lanes: NG (net2dec) and RS used chart-image modules. Here I build the REV-style chart⊗value tensor for networks and test where it can go. I also attack the one-sided (8-gather, rank F = 8) class directly with E8 root data. NET8R left that class open: there, b_end ≤ 1 is not forced.
VERDICT: NOT LOUD. Best new floor: D ≥ 24 for the one-sided (rank_Q F = 8) class, with no premise (NG gives 21). No floor reaches 56. The obstruction is exact (§2) and is the same one-sided decoder law that WQ (i) lacks.

## 1 [P] NETWORK TENSOR POTENTIAL (REV form, any field K, charts = K-subspaces, labels q_p ∈ K^h)
- Define S := Σ_p q_p^⊥⊗e_p + Σ_k b_k^⊥⊗r_k ⊆ K^h⊗K^n, where r_k is the content (row k of NF).
- In ⊥-language a node is an ASCENT a_k^⊥ → b_k^⊥ that costs d_k. A relay is a free descent b_j^⊥ ⊇ a_k^⊥. A gather is a free descent q_p^⊥ ⊇ a_k^⊥.
- ADD: a_k^⊥⊗r_k ⊆ (span so far), so each node adds ≤ d_k to dim S. Deposits put q_t⊗M_t inside S.
- Quotient by Σ q_p^⊥⊗e_p ≅ K^n via v⊗e_p ↦ (v·q_p)e_p. Hence **D ≥ rank_K(Q∘M)**.
- The argument is time-direction-free and self-dual under (b^⊥, a^⊥, G^T, F^T, H^T).
- At K = F2 with 2-adically integral scalars this is RS §3. That gives D ≥ 104 on P104 and D ≥ 96 on Q96 when the diagonal is odd: the network analogue of R ≥ 96.
- [P] LIFT form (network copy of REV §5b): if the visited charts admit an inclusion-preserving, dimension-preserving Q-lift along relays, then D ≥ rank_Q(Φ∘M). So any network with D < 104 (E8/NET8 included) uses a non-liftable chart configuration.
- [C] facts.log: q_s·q_p ≡ 1 + ⟨r_s, r_p⟩ (mod 2) for all 104² pairs (r = E8 roots). The labels ARE the root lines mod 2, but that is a linear map to E8/2E8, not a Q-lift.

## 2 [P] CEILING OF THE TENSOR / CARRY ANGLE (why it cannot give 56 without Wall56)
- Every network floor that is proved without Wall56 also holds for relay-free networks, i.e. decoders, at price = drop. So such a floor is a decoder floor.
- The best decoder potential floors are 21 (NG/ADICWALL, any rows, halves) and the rank-counting cap of 28 (HC). The 8-row mod-4 result of 42 is row-local and does not transfer (N2D O2).
- So any carry-aware tensor (CARRYPOT) caps at the decoder potential floor unless it proves Wall56 itself for half-integer decoders.
- [C, by hand + checked] NG's fwd/mir system is attained at D = 21. Example: 2×(9→4, out-relay) + 2×(5→0, in-relay) + one (5→4) node gives Σfwd = Σmir = 105 ≥ 104. Integrality cannot lift 21.
- [P] REFINED cross term: the fwd cross count d_k(h − a_k) can be replaced by (h − a_k)·(dim(b_k + Σ_{j→k} b_j) − dim b_k). The proof: in NG step 3, 2χ_uχ_c r_j already lies in Π̃_j whenever c ∈ b_j^⊥.
  - The mirror form is analogous.
  - The profile above still meets it (it uses B_in + b_k = a_k), so the optimum stays at 21.
- Angle 2 (chart-image rephrasing):
  - D56_8rows / rigid_gram transfer only through rank-F = 8 rigidity (NET8R), not as chart images.
  - mod-4 mass (m4) is a joint row object. N2D O2 shows it is not a chart-image bound.
  - So the 8-row result yields exactly the one-sided class below and nothing beyond it.

## 3 THEOREM OS (one-sided, rank_Q F = 8: e.g. exactly 8 gathering nodes, any depositors, any relay graph)
Facts used:
- NET8R: M is rigid, so W rows are proportional to roots, and every gatherer has dim a ≥ 8.
- [C] facts.log: every codim-2 flat leaves roots of rank 8 outside it; all 16 kernel normals are NON-labels; P104 = 13 disjoint odd 8-cliques.

Statement [P]:
- (i) WLOG every drop-0 node gathers. A non-gathering node with a = b can be bypassed with M and D unchanged, because b_j ⊆ a_k = b_k. A gathering one has dim b ≥ 8, so its flat b^⊥ holds ≤ 1 vector, which is a kernel normal and hence serves no reader.
- (ii) For l ≤ 8, C_l cuts every walk to the depositors with dim b < l. So |C_l| ≥ rank W_{<l}, where W_{<l} = Σ_{dep, dim b<l} G_{:,k} c_k^T.
- (iii) For every odd 8-clique K: W[K] has rank 8 (8 orthogonal roots), and rank W_{≥l}[K] ≤ #{depositors with dim b ≥ l whose flat meets K}. Hence |C_l| ≥ 8 − ⌊Σ_{β≥l} κ_β n_β / 13⌋. Here:
  - n_β = #non-free depositors with dim b = β; these lie in C_{β+1};
  - κ_β ≤ min(13, N(9−β)).
- (iv) D ≥ Σ_l |C_l|.

Result:
- [C] osip.py minimises this exactly: **D ≥ 24**.
- The minimising profile has depositors (b=4:2, b=5:4, b=6:7, b=7:10).
- Anchor: the E8 profile (8 depositors, b=1) evaluates to 56.

[P] corollary: if all depositors with dim b ≥ 2 share a common 2-dim subspace of b (so every high flat lies in one codim-2 flat), then rank W_{<l} = 8 for l = 2..8 and **D ≥ 56**. This strictly extends NET8R's b_end ≤ 1 case.

## 4 OBSTRUCTION (exact)
- The one-sided floor ignores the decoder condition: Ah_s must lie in span{c_k : k serves s}. Cuts and flat-counting see only where readers sit, not which root directions the contents must span.
- Example: the B-family (8 hyperplane gatherers → common 5-dim B → drop-1 depositors, one per coset of B^⊥) passes every level/clique constraint at about 36. It really costs 24 + Σ_cosets rank(roots in coset), about 124.
- So 56 for the one-sided class needs a count law that couples root spans with label flats. This is WQ §5(i), the same missing law as for relay-free one-sided decoders.
- In the general (rank F, G ≥ 9) class the only route is a realization, which N2D O1 and RZ §1 show is equivalent to the goal.

NEXT: (a) a LEAN lane (Sonnet) for §3(i)–(iii). (b) Add the decoder-span constraint to OS as an exact LP over E8 root flats × label flats. That is WQ (i) with level cuts, and it is the one lever left for the one-sided class.
