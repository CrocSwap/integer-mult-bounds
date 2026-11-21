# YCARRIER YC (Nov 20, Opus, theory + exact census). Own code: census.py (-> census.log, census.pkl), hyper.py (-> hyper.log), levelcut.py (-> levelcut.log). stdlib, 1 proc, threads=1.
Why not a retread: JOINTDR showed ONE carried relay is free locally; NETATTR/NETDOUBLE/NET2DEC bound networks by potentials or cluster maps. This lane asks whether carriers can push a whole P104 call below 112, and answers with a relay-blind GLOBAL cut law plus a P104 carrier census.

VERDICT: no κ lead. Carriers cannot beat the rung in the 8+8 regime, whatever relay graph they carry [P]. In general a carried word's D is bounded below by a relay-blind level-cut sum [P, fuzz C]. So y-carriers save R only; they never lower the D-side bound. The residual (≥9 gathering or ≥9 depositing descents with low-rank level slices) is exactly NET-D56 / Wall56's open ≥9-row regime. The E8 network's content cannot be carried at all [C].

## 1. Word → NetW bridge, all relays [P]
Map every Legal call to a NetW whose total drop equals D EXACTLY:
- split each owned lifetime at every chart change;
- a segment at chart c is a zero-drop node (a = b = c);
- a descent c → c' is a node (a = c, b = c');
- an owned ASCENT c → c' is a relay (b = c ⊆ a = c'), paid in R;
- a read of a public (y, x or helper) at chart c is a set of relays from every node that deposited into it earlier; each such node had b ⊆ (public's chart at deposit) ⊆ c, because publics only ascend;
- a public load is a deposit G entry; it must land on even cells or cancel (y), or be undone (x and helper finals are pinned).
Hence carried relays (JOINTDR's y-carrier) and owned-carried relays are the same NetW object. A carrier changes R, never the network that bounds D.

## 2. LEVEL-CUT LAW, port-general, relay-blind [P; C fuzz]
For any NetW (hence any Legal call), with N = (I−H)^{-1}, C_l = {k : dim b_k < l ≤ dim a_k}, and
  M_l = Σ_{g: dim a_g ≥ l} Σ_{d: dim b_d < l} G[:,d] N[d,g] F[g,:],
we have **D = Σ_l |C_l| ≥ Σ_{l=1}^{h} rank_Q M_l**.
- Proof:
  1. Relays satisfy b_j ⊆ a_k, so chart dimension never drops across a relay.
  2. Hence every walk from a gatherer with dim a ≥ l to a depositor with dim b < l contains a node of C_l: the first node whose b falls below l.
  3. Factor the walk sum at that first C_l node. This gives rank M_l ≤ |C_l|.
  4. Each node of drop d lies in exactly d of the sets C_l. ∎
- This is NET8's level cut (LEANSWARM/NET8) with the rigidity input removed.
- [C] levelcut.py: random legal networks at h = 3, 4, 5 with scalar relays (1, −1, 2, 1/2) of ANY slack; 400 trials each.
  - 0 violations; tight in 139, 130 and 90 trials.
  - Control with the relay rule off: 50, 59 and 49 violations.
- Corollary A [P]: a call whose network has ≤ 8 gathering and ≤ 8 depositing NODES (NET8's count; a whole lifetime is one node when all its deposits carry its final content, since NetW only needs q_p ∈ a and b_j ⊆ a for mid-lifetime gathers/reads) has D ≥ 56, whatever its carriers. Carrier loads count as deposits, so a carrier can only add depositors.
  - Proof: DFR rigidity gives dim a ≥ 8 and dim b ≤ 1, so M_l = M for l = 2..8, and rank M ≥ 8 (clique8).
  - So "take NET8 / asc56 and replace tight structure by carried slack relays" provably cannot go below 56 on D. The construction in the brief is closed.
- Corollary B [P]: D ≤ 55 needs some level l ∈ [2,8] with rank M_l ≤ 7. That requires part of M to be carried ONLY by walks that start at a gatherer with dim a < l or end at a depositor with dim b ≥ l, i.e. non-rigid rows of Φ or Λ (≥ 9 rows). This is RZ §6 sharpened to a per-level statement.
- R side: carriers cannot touch it. An R-side relay is a descent, and publics never descend (JD [P]).
  So, with carriers, OWN112 ⟸ [Σ_l rank M_l ≥ 56 for every carried P104 network] + [R ≥ 56].

## 3. P104 carrier census [C exact, census.py / hyper.py]
Setting: ports = 70 of weight 3 plus 34 of weight 7. Every port is even against exactly 48 others, so each carrier hyperplane q_t^⊥ holds exactly 48 ports.

All 511 hyperplanes v^⊥, by the number of ports inside:

| normal v | 44 ports | 48 ports | 52 ports | 56 ports | 60 ports | 0 ports |
|---|---|---|---|---|---|---|
| port | — | 104 | — | — | — | — |
| odd non-port | — | 1 | 44 | 94 | 12 | 1 |
| even | 12 | 94 | 44 | 105 | — | — |

Charts a with at least one carrier port t (a ⊆ q_t^⊥), all charts counted exactly:

| dim a | charts with a carrier | carriers per chart |
|---|---|---|
| 8 | 104/511 (20.4%) | ≤ 1 |
| 7 | 21164/43435 (48.7%) | ≤ 2 |
| 6 | 606614/788035 (77.0%) | ≤ 4 |
| 5 | 3059693/3309747 (92.4%) | ≤ 8 |

[P] The odd vectors of a^⊥ form an affine hyperplane of it, so a chart of dim d has at most 2^{8−d} carriers.

The y-carrier condition, read correctly:
- the carrier meets k at a chart X on k's DESCENT path, with b_j ⊆ X ⊆ q_t^⊥;
- the carried content r_j (j's FULL content, upstream relays included) lies on t's even set E_t (48 ports).
- So span(L(supp r_j)) + X ⊆ q_t^⊥.

★ [P + C] RIGID CONTENT IS UNCARRIABLE unless its span is a port hyperplane.
- If span(supp r_j) ≥ 8 (the DFR-rigid case), a carrier exists only when that span equals q_t^⊥ and holds exactly 48 ports.
- t7669: its 8 D-chain gather charts are 52-port hyperplanes with odd NON-port normals (127, 162, 42, 97, 76, 266, 104, 289).
- So no y can carry content of any E8 row or chain, nor read into those charts. Every slack relay out of rigid content must be owned (cost R ≥ e) or tight.

Capacity is NOT the wall [P].
- Each y_t climbs 0 → q_t^⊥ (8 dims), and stints on one carrier can be nested.
- So the free slack available per call is ≥ 8·104, far more than any network uses.
- The binding facts are §2 (level ranks) and the even-set/rigidity condition above, not climb budget.

## 4. The obstruction, stated as one law
- **CARRIER WALL** [P]: D_call ≥ Σ_l rank M_l^net, relay-blind. Free carriers exist only for content of span ≤ 8 lying inside a port hyperplane (48 ports).
- Hence a sub-112 carried call needs BOTH:
  1. a level slice of rank ≤ 7, which forces non-rigid (≥ 9-row) Φ or Λ;
  2. its zigzag relays (NA §3 type: deposit, then carry up, then gather) carrying content inside some E_t.
- The missing global step for proving 112 from Wall56 is therefore exactly: "Σ_l rank M_l ≥ 56 for half-integer P104 networks". This is a per-level rank statement. It is implied by NET-D56 and implies D ≥ 56; it is not implied by Wall56 by any argument known here (cluster maps fail, NA C1).

NEXT:
- (i) Lean the general level cut (extend Net8Cut.cut_rank; easy).
- (ii) Exact test of LEVEL-WALL on decoders: for decoders (relay-free; a = span S, b = S ∩ W^⊥, drop = price), is Σ_l rank M_l ≥ 56 on the E8 orbit and Gibbs-resampled decoders (TAU48 sampler)? If it fails on decoders it fails for networks. If it holds tightly, it is the right network-native target.
