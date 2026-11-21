# LEANCONTRACT (Sonnet, Nov 20). lean/decoder-duality/Nov15/NetContract.lean, imports Nov15.NetBowtie. KERNEL-CHECKED via runlean.sh (rc=0, 9 s, 2.1 GB). Axioms of every headline: [propext, Classical.choice, Quot.sound]. No sorry/native_decide.

## What is proved [P]
- `GNet` = BNet minus bowtie data (hN2 is DERIVED from hN1 via mul_eq_one_comm). `BData Nt γ` = the bowtie fields; `toBNet` glues them.
- `Contractible Nt j k` (series edge): H k j != 0, TIGHT a_k <= b_j (so a_k = b_j), k is the only successor of j (inj), j the only predecessor of k (outk).
- `contract Nt j k hc : GNet` (same index type; j becomes inert: rows/cols 0, charts bot). Data: a'_k = a_j, b'_k = b_k, F'_k = F_k + eta F_j, G'_k = G_k + G_j/eta, H'_{k y} = eta H_{j y}, N' = N off j (eta = H k j).
 (i) legal network in the SAME model: all fields of GNet (hba, hF, hG, hHlt, hH, hN1) proved.
 (ii) `contract_M_odd`: G N F preserved on ODD cells (q_s . q_p = 1) ONLY. Even cells lose the cross term G_j F_k / eta, which vanishes exactly on odd cells (G_j(s) != 0 => q_s perp b_j, F_k(p) != 0 => q_p in a_k = b_j). Not exact on even cells (statement is sharp).
 (iii) `contract_D`: total drop EXACTLY preserved (d'_k = d_j + d_k because dim b_j = dim a_k), not just not-increased.
 `contract_edges_lt`: relay-edge count drops by at least 1 (injection into edges minus (k,j)); `exists_closed'`: every GNet reaches (Reach = iterated contraction) a contraction-closed network (no Contractible pair).
- HEADLINE `contract_D_ge_mass`: Reach Nt Nt' and BData Nt' => mass Nt.q Rec <= Nt.D for any Rec equal to G N F on odd cells. `contract_D_ge_of_wall`: same with Wall hypothesis => N <= D (56 at Q96 still needs Wall56@Q96 as hypothesis).
- Non-vacuity `Toy` (h=2, 2 ports, 2 nodes, over Q): tight chain j -> k, a_k = b_j = <e2>, both nodes gather and deposit. `toy_not_bowtie`: NO BData exists on it (j deposits + has out-relay => hub; k gathers + has in-relay => not out; hshape forces one of them wrong), `toy_reach`/`toyB`: after one contraction it is a (relay-free) bowtie. `toy_headline`: D = 2, mass(diag) <= 2.

## Gaps / honest scope
1. SERIES contraction only: j must have exactly ONE relay out-edge and k exactly ONE relay in-edge. NA 2c's "external relays entering only at k_1 and leaving only at k_s" is exactly iterated series contraction, so the NA statement is covered; but a tight edge whose k has a second in-relay or whose j has a second out-relay (merge/fan nodes) is NOT contracted. Is the surgery valid there? Merging then needs F'_k to depend on which in-neighbour, and fails: [CONJ] only tree-shaped tight sub-networks contract.
2. Contraction is only odd-cell exact (as NA says); the bowtie decoder is then built for the CONTRACTED network, whose M agrees with the original only on odd cells. That is all IsDec/mass need. Even cells of the original are NOT recovered.
3. Tightness a_k = b_j is a hypothesis per edge. Non-tight relays (free ascent e >= 1) are the genuine gap of NA 3 and are untouched; no statement here about when contraction reaches a bowtie. "Bowtie after contraction" is a hypothesis (BData on the reached network).
4. Dead nodes: contraction keeps j as an inert node (charts bot, drop 0). BData on the result must assign it a role/component; any role works (toyB uses singleton hub components).
5. Wall56@Q96 is still a hypothesis; no connection yet to P104 networks (which contracted shapes occur there is open).
6. edge-count lemma gives termination; `exists_closed'` does not say the closed network is a bowtie.
