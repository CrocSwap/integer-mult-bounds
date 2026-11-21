# BRIDGE (Nov 20, Opus, Lean + theory): model hypotheses vs the word model

Owner rule: only Wall56 may stay unproved. Every model hypothesis has to come from WordModelDefs.Word / Reach / Step plus verifier clauses. Not a retread: YC sec 1 was a paper sketch; NET8/DX/NetContract had their network hypotheses ASSUMED. This lane proves the bridge in the kernel.

## 1. Word -> NetW: BRIDGED [P, Lean, kernel-only, axioms std]
Files: lean/decoder-duality/Nov15/BridgeNet.lean (core), BridgeNetInst.lean (#7113 caller), BridgeGNet.lean (GNet form).
- `BridgeNet.inv_of_reach` (generic over R, pb, port map ix): every Reach-able state carries a network invariant (Inv):
  - DAG: H k j != 0 -> j < k
  - relay rule: H k j != 0 -> b_j ⊆ a_k
  - gather rule: F k p != 0 -> port p was BORN inside a_k
  - val_k = F_k + Σ_{j<k} H_kj val_j
  - owned rows = their node's val, with b = the current chart
  - public rows = pi_r + Σ g_rj val_j, with pi supported on ports born inside the chart, and g_rj != 0 -> b_j ⊆ chart
  - Σ drops = ownDrop s
  Nodes come from owned births, owned gates and owned MOVEs. Public registers are wires.
- `BridgeNet.word_netW`: Word cl s + ChartsSubsp + OwnedNested (verifier clauses l.26-31, l.51) + port labels = DW4.labs up to σ give a `N8.NetW` with:
  - Σ drop = ownDrop s EXACTLY, where ownDrop = Σ over owned MOVEs of (dim src − dim dst)⁺, i.e. owned descent;
  - b_k ≤ a_k for every node;
  - c_s = 1 on D ports and 1/2 on B ports.
  Also proved: dim(span chart) = log2|chart| for subspace charts; SafeRungsClique.dot = the F2 dot product of vecOf.
- `BridgeNet.word_net_laws`: for every such word the network has ≥ 8 gathering and ≥ 8 depositing nodes, and it satisfies:
  - DX: Σ_l rank M*_l ≤ ownDrop for every level set L;
  - NET8 node corollary: if there are ≤ 8 gathering and ≤ 8 depositing nodes, then ownDrop ≥ 56.
- `BridgeNet.word7113_net_laws`: the same for caller7113 (t7669/w_s4 caller). The label permutation σ7113 is checked by decide. The 8 non-D ports are exactly P104 indices 96..103 (`nonD_images`).
- `BridgeNet.word_gnet` / `word_bowtie_wall`: the same network as a NetContract.GNet (q = DF.lq, N = Nmat H = 1 + HN). If some iterated tight-chain contraction carries BData and Wall56 holds (FutureAttr.Wall form for the caller's odd-cell pattern), then ownDrop ≥ 56.
- Non-vacuity: `toy_bridge` (a reached 2-event run with drop exactly 1). `hlab7113` discharges the label premise for the real caller. No kernel Word instance (the 150k-event traces are not replayed; same caveat as UniFold7113Inst).
- Consequence: NET-D56 (every P104 NetW has D ≥ 56) now implies owned descent ≥ 56 for every legal word, with no model gap (Lean theorem). NetW results (LevelCutRelay, LevelCutDX, Net8, Net8Cut) are THEOREMS about words. Their own extra premises stay (Net8: exactly 8+8 nodes).

## 2. Other models
| model / files | status | what is missing |
|---|---|---|
| NetW: LevelCutRelay, LevelCutDX, Net8, Net8Cut | **bridged** | — (Net8's 8+8 node count stays a premise of that lemma) |
| GNet: NetContract | **bridged** (BridgeGNet) | headline needs BData of a contraction = conditional |
| BNet: NetBowtie | **conditional** | bowtie shape is a genuine restriction |
| Net4 (Z/4): NetNG D ≥ 21, NetDoubling Net4/FNet | **conditional** | Net4 needs a 2-adically integral network with c_s a unit in Z/4. Word gate coefficients are arbitrary rationals, and B ports already give c_s = 1/2, so this cannot be derived. Rescaling ports fixes c_s but not internal F/G/H integrality. Stays a lemma about integral networks. |
| run model ARun: FutureAttr(T), TensorPot, HalvingLaw, CarrierTree, CFChain/CFRelay* | **conditional** | (i) GTD (`hgtd`) and cold intake (`hcold`, class F/CF) are constructor premises. CT-COVER is false (R2/CTCOVER climb-sharing run), so they are genuine restrictions. (ii) Rendezvous Lemma A adds rank-8 hF/hG/hM. (iii) The ARun ADD is d += l·e with d ≠ e. A word gate (simultaneous combination incl. self-scale) needs a gate-compilation lemma, not formalised. TensorPot also needs integral scalars (not derivable). Derivable parts: owned start at row 0 (birthOwn), publics only ascend (movePub c<d). |
| caller model: CallerSGram, CallerRC2, CallerHP (+SignCore/Prefix/Gram/Support/Adj) | **blocked** | No SPEC-level Lean object for a multi-call caller (WordModelDefs.Caller is port data only), so product = −1, ρ = 2 hosts, n = 2k−2, D ≥ 2, MAINS, pieces/kernel vectors, orth/resol, rowid/colid have no source to derive from. Q = 0 / ρ = 2 (KASYM) are also genuine branch restrictions. char ≠ 2 is free over ℚ. |

## 3. Next
- R side: run the same invariant on the TIME-REVERSED word? Publics descend there, so this is not a Word. A ⊥-bridge needs its own Inv (owned ascents as nodes, publics as descending wires). That is the natural next lane: it would turn the CF/carrier results into conditional-free statements up to the class restriction.
- Tie ownDrop to the rung's descMass (UniTrace fold / WordRungPort D) so word_netW feeds the κ chain directly.
- Caller: define the caller word (outer level) in WordModel terms before any caller bridge.

## 4. Round 2 (coordinator follow-up)
### 4.1 Rung D premise = bridged D [P, Lean, BridgeRung.lean, axioms std]
- `descMass_foldS`: for a legal trace with ChartsSubsp, the folded banked net's descent mass equals ownDrop (exec tr). Public banks contribute 0 (strict ascent).
- `descMass_fold7113`: `BankBanner.descMass (foldBanked7113 …) = ownDrop (exec tr)`.
- `NetD56` is the network statement (every P104 NetW with b ≤ a has Σ drop ≥ 56). `rung_hD_of_netD56`: NetD56 implies the rung premise hD (56 ≤ descMass) for EVERY legal #7113 word. So the rung's D premise is literally NET-D56 on the bridged network: no model gap, only the open network theorem.

### 4.2 R side: NOT bridgeable as a relay-blind cut [P, short]
- Transpose/⊥ of the D network: dim b^⊥ − dim a^⊥ = dim a − dim b. The dual network's total drop is D again, not R.
- DX/LevelCutRelay needs the free edges never to cross a level in the paid direction (relay rule b_j ≤ a_k: free edges never go down, paid nodes go down). The R side would need the mirror rule: free edges never go up. Public wires go up in forward time, and in reversed time they go down together with the reversed ascents. In neither time direction (nor in ⊥ charts) do free edges and R-moves point in opposite directions, so no relay-blind cut can charge level crossings to owned ascents.
- Check: the generic invariant (`inv_of_reach`) with inputs = y2 ports and outputs = x2 ports gives no support constraint. The births at {0} constrain nothing and the finals at V restrict nothing.
- Owned INIT is free at any frame (independent.py INIT: `cur[r]=e[2]`, no price). So the only source of R ≥ 56 is the pinned hosted pattern (y2 → x2 plus carrier cleanup): the rendezvous / ChainWall56@Q96 structure (REUSE96, CARRIER8). Not a level cut.
- Status: R ≥ DX-sum for every legal word is not available. The R side stays CONDITIONAL (class F/CF/carrier-forest lemmas), and per-word R ≥ 56 stays open (not Wall56).

### 4.3 Table for the PR (premise status after BRIDGE)
| result | status | remaining premise(s) |
|---|---|---|
| word → NetW bridge, Σ drop = owned descent (BridgeNet.word_netW, word7113_net_laws) | **unconditional** | verifier clauses ChartsSubsp, OwnedNested only |
| every word network has ≥ 8 gathering and ≥ 8 depositing nodes; DX cut Σ_l rank M*_l ≤ owned descent | **unconditional** | — |
| rung descMass = owned descent (descMass_fold7113) | **unconditional** | — |
| NET8: owned descent ≥ 56 | conditional lemma | network has ≤ 8 gathering and ≤ 8 depositing nodes |
| bowtie/contraction: owned descent ≥ 56 (word_bowtie_wall) | conditional lemma | Wall56 + bowtie data on a contraction |
| rung D ≥ 56 per call (hD) | **open** | NET-D56 (rung_hD_of_netD56); NOT Wall56 |
| rung R ≥ 56 per call (hR, hostedRise) | **open** | no bridge; rendezvous / ChainWall56@Q96 |
| NetNG D ≥ 21, NetDoubling | conditional lemma | 2-adically integral network (Net4) |
| FutureAttr/TensorPot/HalvingLaw/CarrierTree/CF*, Rendezvous Lemma A | conditional lemma | class F/P/CF/carrier forest; GTD; gate compilation; rank-8 hF/hG/hM (Lemma A); integral scalars (TensorPot) |
| CallerSGram/RC2/HP (KASYM) | conditional on the caller model; **bridge blocked** | product −1, ρ = 2, n = 2k−2, MAINS, pieces; Q = 0 branch; no SPEC caller object |
| κ < .0093454 (word rung) | conditional | hD and hR above (plus caller Cert, hV, HSContract as in the audit) |
