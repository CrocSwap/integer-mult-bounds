# Proofs and status

Status tags: **[proved]** written proof from the stated hypotheses; **[checked]** exact finite computation by `verify.py`
on the literal inputs; **[model]** a statement inside an explicit bookkeeping hypothesis. Nothing here changes a κ.

Notation. `p = 104` ports `q_1..q_104 ∈ F2^9` (odd weight), `dot(a,b) = popcount(a & b) mod 2`; a pair is *odd* when
`dot = 1` (the diagonal is odd). A native word has 771 public registers (208 main registers: for each port one input
climbing from the frame `<q>` (dim 1) to dim 9 and one output climbing from dim 0 to the hyperplane `q^⊥` (dim 8);
the others are helpers), private (owned) registers, and events MOVE, INIT, CLEAR, SCALE, ADD, COPY, each acting at
one frame. The **invoice** is `T = k·H + T_out`, `P = k·Pd + P_out` where `H` is the histogram of helper ranks
(final dim − initial dim of every non-main public register), `Pd` the histogram of MOVE ranks (|dim change|) of one
native call, and `(T_out, P_out)` the caller's target and paid tables. `S = Σ (T−P)·r`.

## 1. Native accounting

**Proposition 1.1 [proved].** For a legal native word, `Σ r·Pd = 16p + Σ r·H + O`, where `O` is the sum of dimension
drops of the private MOVEs. Hence the native margin per call is `Σ r·H − Σ r·Pd = −(16p + O)`.

*Proof.* A public MOVE requires `F_old ⊊ F_new` (climb) and a private MOVE `F_new ⊊ F_old` (descent); an ADD, COPY or
SCALE acts at the single frame of its registers. So the MOVE ranks of a public register sum to `dim final − dim initial`
(MOVEs of one register chain). Summing over public registers gives main climbs plus helper ranks; the 208 main registers
climb by 8 each (checked), i.e. `16p`. Private MOVEs contribute `O`. ∎

[checked] Replay of the #6702 word (legality, exact endpoint `identity + XY block`): `Σ r·H = 4204`, paid mass 5924,
`O = 56`, `5924 = 1664 + 4204 + 56`. Replay of the #6349 word: `4226`, `5946 = 1664 + 4226 + 56`. The #6805 and #6824
histograms (retained constants of those packages) differ from the replayed #6702 histogram by exactly the retime/split
edit: helpers `{4:+1, 5:+1, 9:−1}` and paid `{1:+1, 5:+1, 6:−1}` for #6805; `{7:+1, 9:−1}` and `{1:+2, 3:−1, 4:+1, 5:−1}`
for #6824 over #6805. Each edit has `Σ r·Δ` equal on the two sides (rank conserving).

## 2. Caller accounting

For a caller word with `k` stages, `T_out` has one target of rank `(q-exponent mod 2) + 8·#stages` per declared diagonal
term (weight 104) and `P_out` one rank-1 job per thin query (weight 104) and one rank-`8·#stages` job per idle event
(weight 208, or 104 for IDLE_ONE).

**Observation 2.1 [checked].** On the literal callers of #6726 (final and unretired) and #6348:
(a) for every stage `s`, (target incidences of `s`) − (idle incidences of `s`) `= 208 = 2p`;
(b) the outer margin is `p(17k − 1)`: 31720 (k = 18), 33488 (k = 19);
(c) `17k − 1 = 16k + (odd-rank targets) − (thin queries)`, with `32 − 15` at k = 18 and `34 − 16` at k = 19.

Part (a) gives `Σ_stages 8·2p = 16kp` for the stage units; the odd-rank targets (the "+1" of ranks `8s+1`) add `32p`
and the rank-1 thin queries subtract `15p`. This is the literal-counting identity of #4697 (`(p+2)(2b+1) − 1` per port with
`b = 8`) carried to the tree-shaped and fragmented callers; it is **not proved for an arbitrary caller**.

## 3. The surplus identity

**Theorem 3.1 [proved from 1.1 and 2.1(b)].** With outer margin `p(17k−1)` and native margin `−(16p + O)`,
`S = (17k−1)p − k(16p + O) = (k − 1)p − kO = k(p − O) − p`.
With `p = 104` and `O = 56`: `S = 48k − 104`. The local balance `H − C + 17p` of #4697 equals `p − O = 48`.

*Consequences.*
(i) `S` depends on the native word only through `O`; any edit with equal `Σ r` on both sides (splits, retimes, lifts that do
not change `O`) leaves `S` fixed, and an edit that lowers `O` by `δ` raises `S` by `kδ`.
(ii) [checked] `S = 760` for #6702, #6805, #6824 on the #6726 caller (k = 18) and `S = 808` for the #6348 caller on the
#6349 native word (k = 19), each also `= (k−1)p − k·56`. Over the chain `ΔS = 48Δk − Δp` (the kernel-era invoices of #4697,
`800 = 48·19 − 112` and `753 = 48·18 − 111`, fit the same shape).
(iii) The remark that `S` moved at only three frontier jumps was **not** reproduced: the callers of the
intermediate words (e.g. #6398) are not available as literal inputs here, so only the checkpoints above are claimed.

**Proposition 3.2 (first order) [proved].** Let `F(t) = Σ (T−P) r^(1−t)` and `D(t) = −F'(t) = Σ (T−P) r^(1−t) ln r`. Since
`F(0) = S` and `F(κ) = 0`, `S = ∫_0^κ D(t) dt = κ·D̄`. [checked] On the four invoices `S/D(0) < κ < S/D(κ)`, each bound within
0.7 % of κ (for #6805: κ = 0.0033081451891428, S/D(0) = 0.0032862, S/D(κ) = 0.0033303).
κ values from the literal invoices (50-digit bisection): #6726 root on the #6702 word 0.0033072446848536,
#6805 0.0033081451891428, #6824 0.0033082345661432, #6348 caller on the #6349 word 0.0031498130060577 (this last is not a
published figure).

## 4. Mixed port sets [model]

**Hypothesis H-mix.** Call `j` acts on a live set `A_j` of `a_j` ports, `U = ∪ A_j`; its native margin is `−(16a_j + O_j)`
and the caller margin is `17Σ a_j − |U|` (for `A_j = U` this is 2.1(b)). Then `S = Σ (a_j − O_j) − |U|`.
**Cost law** (#968 Theorem 4, `p' = 120 − a_j ≤ 24`): any exact 8-term decoder has `O_j ≥ c(a_j) = max(a_j − 48, 56)` for
`96 ≤ a_j ≤ 120`.

**Proposition 4.1.** `S ≤ Σ min(48, a_j − 56) − |U| ≤ 48k − |U| ≤ 48k − 104`, with equality iff `A_j = U`, `|U| = 104`
for all `j` and every `O_j = 56`. Uniformly, `S(a) = (k−1)a − 56k` rises with `a` up to 104 and `S(a) = 48k − a` falls beyond
it: each line above 104 nets −1.
*Proof.* `a − max(a−48, 56) = min(48, a−56) ≤ 48`, and `|U| ≥ max a_j`. For the mixed case
`Σ min(48, a_j − 56) − |U| ≤ k·min(48, |U| − 56) − |U|`, the uniform value at `|U|`, maximal at 104; equality forces
`a_j = |U| = 104`. ∎ [checked] uniform maximiser 104 at k = 18 and 19 (caps 760 and 808, equal to the literal `S`);
20000 random mixtures respect `S ≤ 48k − 104`. H-mix is a bookkeeping extension, not derived from a literal mixed word.

## 5. E8 structure of the ports

**5.1 [proved].** On `E = 1^⊥ ⊂ F2^9` (even weight), `Q(e) = wt(e)/2 mod 2` satisfies
`Q(e+f) = Q(e) + Q(f) + e·f` (as `wt(e+f) = wt e + wt f − 2|e∧f|`). Even-weight vectors by weight: 36, 126, 84, 9;
`Q = 1` on weights 2 and 6 only, so 120 nonsingular points and 135 singular nonzero vectors: the form is `O+(8,2)`. With
`e = v + 1`, the nonsingular points are the odd `v` of weight 7 (36) and 3 (84). [checked] 120 and 135.

**5.2 [checked].** The 104 ports are 70 of weight 3 and 34 of weight 7, all among the 120. Missing: weight 3 `{7, 25, 42,
52, 67, 76, 82, 97, 104, 137, 162, 266, 289, 448}`, weight 7 `{127, 491}`. The vectors `p + 1` span `E` (rank 8), so `Q` is
determined by the ports.

**5.3 E8 model [checked, all 7140 pairs].** Weight 3 with support `T` ↦ `u = e_T − (1/3)·1`; weight 7 with zero set
`{i,j}` ↦ `u = e_i − e_j` in the sum-zero `R^9`. All `|u|² = 2`; for distinct lines `⟨u,u'⟩ ∈ {0, ±1}` (3780, 1680, 1680 pairs)
and `⟨u,u'⟩ = 0` iff the pair is odd. This is the relation `S9 = ⟨r_i, r_j⟩ + 1 (mod 2)` of #968 §1. Orthogonal roots lie in
`R^8`, so odd cliques have size ≤ 8; [checked] 2025 cliques of size 8 (orthoframes) among the 120 lines, none of size 9,
759 among the ports.

**5.4 Frames and the stabiliser.** [checked] The 16 missing lines contain exactly two 8-cliques `F1 = {67,104,137,162,266,289,448,491}`
and `F2 = {7,25,42,52,76,82,97,127}`, disjoint, so the ports are `P120 − F1 − F2` (the structure of #968 §5). The 8×8 incidence
matrix (non-orthogonal pairs) has 8 distinct rows of weight 4, closed under complement.
*Stabiliser.* Let `G` be the group of linear `g` of `F2^9` with `dot(gx,gy) = dot(x,y)` and `g(ports) = ports`. [proved] Such `g`
fixes `1` (the unique `v` with `v·x = x·x` for all `x`), preserves parity, and `Q∘g − Q` is a linear functional (same polar
form) vanishing on the spanning set `{p+1}`, so `g` preserves `Q`, the 120 points and the missing set `M`. [checked] There are
384 dot-automorphisms of the 16-set `M`; each extends to the 8-dimensional span of `M` uniquely and to `F2^9` in at most the
two ways allowed by the radical, and exactly 384 of the extensions preserve the ports. `|G| = 384`, faithful on ports, with
orbits of sizes 48, 32, 24; ports 69 and 276 lie in the 48-orbit.

**5.5 Frame pairs [checked, orbit statement cited].** Frames disjoint from `F1`: 1260, split by the number of distinct incidence
rows into 896 (8 rows), 336 (4 rows), 28 (2 rows). The 364 = 336 + 28 are exactly #968's frames "some pair of F1 lines shares
four F0-neighbours", which admit no frame-pair decoder; the literal pair has 8 distinct rows, so it is in the 896 class. That
these are single orbits of the frame stabiliser is cited from the census of #968; here only the invariant is computed.

## 6. Public wall and O versus Gram

**6.1 Wall [proved], 6.2 O versus Gram [checked].** In the symbolic replay every private descent output is a fresh symbol
`z`; `P` is the coefficient of public input `X_j` in the final row of output `Y_i`. A descent-free path from `X_j` to `Y_i` moves data by
ADDs at one frame; public registers only climb and a private register keeps its frame until a descent (which starts a new
symbol), so the frames along the path never shrink and `<q_j> = init(X_j) ⊆ F ⊆ final(Y_i) = q_i^⊥`, i.e. `dot(q_i,q_j) = 0`.
Hence `P = 0` on every odd pair including the diagonal. [checked] 5824 ordered odd pairs (= 104·56), `P ≠ 0` on 4972 of the
4992 even pairs; entries of `P`: 0 (5844), −1/2 (3338), 1/2 (1614), ±1 (10 each).
Let `O = I − P` (what the private descents must supply; rows `Y`, columns `X`), `G_ij = σ_iσ_j⟨u_i,u_j⟩/2` with signs `σ` found by
propagation on the entries of absolute value 1/2 (consistent on all 104 ports). [checked] `O` equals `G` except in exactly 40
entries, 20 in the row of port 69 and 20 in the row of port 276 (in each row 10 entries are 0 where `G = ±1/2` and 10 are ±1 where
`G = ±1/2`); 80 entries of `O` are asymmetric; `rank G = 8`, `rank O = 10`, `rank(O − G) = 2`. Whether the removed 16 lines
could have been chosen otherwise is not addressed.

## 7. Private-descent mass

**7.1 Hop graph [checked].** Replaying the #6702 word: 47 private lifetimes, of which 28 never move and 19 contain the 24
descent hops. Join hop `h` to hop `h'` when the symbol `z_h` occurs in the row of the register at `h'` (same-register
succession and ADD forks included). There are exactly 8 components. Each starts at dimension 8, ends at dimension 1, and has
drop total 7 (chains `8→4→3→1` ×4, `8→5→1`, `8→7→6→1`, `8→7→5→1`, `8→7→6→5→1`), so `O = 8·7 = 56`.

**7.2 Certificate [checked].** For each of the 43435 seven-dimensional subspaces `V ⊂ F2^9` (kernels of the 43435 planes of
functionals), the integer lifts `3u` of the ports outside `V` have rank 8 modulo 1000003; since the lifts lie in the 8-dimensional
sum-zero space, they span `R^8` over `Q`. For hyperplanes `V` the rank is 8 except for exactly 16, the hyperplanes `m^⊥` for the
16 removed lines `m` (rank 7, 52 ports outside).

**Lemma 7.2 [proved from the certificate].** If `a ∈ R^8` is nonzero, the set `S(a) = {j : ⟨a,u_j⟩ ≠ 0}` spans a subspace of
`F2^9` of dimension ≥ 8. (If it lay in a 7-dimensional `V`, then `a ⊥ u_j` for all ports outside `V`, which span `R^8`.)

**7.3 Theorem (conditional) [proved from 7.2].** Suppose the private part `O` equals a Gram-type operator of rank 8, i.e. `O = Σ_{k=1}^8 c_k r_k^T`
with all `r_k` in the row space and all `c_k` in the column space of `G`, and each term is carried by its own single-stage hop
chain (its row support is read at the top frame, its column support written at the bottom frame), the 8 chains disjoint.
Then `O_mass ≥ 56`.
*Proof.* Public registers read into a private register sit at frames containing `init(X_j) = <q_j>` (ADD needs equal frames,
public frames only grow), so the top frame contains `span{q_j : r_k(j) ≠ 0}`, of dimension ≥ 8 by Lemma 7.2. Written into `Y_p`
at frames inside `final(Y_p) = q_p^⊥`, the bottom frame lies in `(span{q_p : c_k(p) ≠ 0})^⊥`, of dimension ≤ 9 − 8 = 1. Private
frames only descend, so the chain's mass is ≥ 8 − 1 = 7; eight disjoint chains give ≥ 56. ∎

*Scope.* Not covered: rank `O` > 8 (the literal word has rank 10), terms read or written at several frames, forks or shared
hops, completions `O = G + Δ` with `Δ` on even pairs of rank > 8. The bound agrees with the floor `cst ≥ 56` of #968 (a different
model) and is attained by the literal word's chains (7.1); this is evidence of tightness, not a proof for the word.

## 8. Controls (all executed)

Caller without one idle event (stage balance fails); paid mass off by one (`S ≠ 760`); a public MOVE reversed (legality
fails); a port replaced by an odd vector of weight 5 (not nonsingular); a port swapped for a removed line (frame count
759 → 742); ports restricted to one hyperplane (67 of the 7-dimensional subspaces then fail rank 8); a hop edge dropped
(components 8 → 9); costs one below the #968 floor (S exceeds the cap by 18); a live set of 90 lines (outside the cost law).
