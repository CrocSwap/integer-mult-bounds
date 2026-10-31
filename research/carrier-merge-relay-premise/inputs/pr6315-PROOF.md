# Proofs: network-coded owned carriers on P104

Tags: **PROVED-LEAN** = `lean/NetCode/Walk.lean` (Lean 4 + Mathlib, no `sorry`, axioms `propext`,
`Classical.choice`, `Quot.sound`); **CHECKED-EXACT** = `verify.py` on the PR6030 word (exact rationals and F2).

## 0. Model

Frames are subspaces of F2^9. A public role only ascends (strict inclusion), an owned role only descends and pays
the dimension drop, and arithmetic happens in a common frame. This is the verifier contract replayed by `verify.py`.
Content is not tied to the frame. A public role may hold coordinates whose ports lie outside its frame, as long as
they arrived through owned descents.

Pass to duals. A frame C corresponds to C^perp. An ascent shrinks the dual for free. An owned descent C -> C'
grows it and costs `dim C - dim C' = dim C'^perp - dim C^perp` (`descent_cost_dual`, PROVED-LEAN).
In PR6030, X_j starts on the line <p_j> and Y_j ends in p_j^perp with p_j . p_j = 1 (CHECKED-EXACT). So a receiver
Y_j can use only frames C with p_j in C^perp, and X_j and Y_j never share a frame.

An **information walk** is a sequence of dual subspaces Z_0, Z_1, ... Each node k >= 1 comes from an earlier
node par(k), either by shrinking (free) or by growing (paid). This covers stops, copies, branches and relays
through public helpers: a helper reads at one frame and ascends, and that is a shrink.

## 1. Walk bound and Lemma S (PROVED-LEAN `union_bound`, `lemma_S`)

The union span of the visited nodes has dimension at most `dim Z_0` plus the total paid amount.
*Proof.* A free step adds a subspace of its parent, which is already inside the union. A paid step adds Z_k ⊇ Z_par.
By the modular law, `dim(U ⊔ Z_k) = dim U + dim Z_k - dim(U ⊓ Z_k) <= dim U + dim Z_k - dim Z_par`.

**Lemma S.** Suppose a carrier holding t.x is collected in G = span of its source ports, so Z_0 = G^perp. Suppose
it must reach every receiver j in R. Then it pays at least `dim(G^perp + span p_R) - dim G^perp`, whatever its stops,
branches and relays. This number is the binary rank of the pairing [p_j . p_i] (j in R, i in S), the repository's
COPY cost. One chain attains it. So stops do not make a single carrier cheaper.
On PR6030 both sides equal 7 for each of the 8 carriers (CHECKED-EXACT).

## 2. Lemma A: additions and shedding along one path (PROVED-LEAN `lemma_A`, `lemma_A_rows`)

Let a port p_i lie in C. Let a receiver read at a frame C' ⊇ C, so that p_j ∈ C'^perp. Then p_j . p_i = 0.
Hence content added at C from ports of C changes no costly pair (p_j . p_i = 1) of any receiver served higher on the
same path. It can be loaded at the top instead, so a path with additions or shedding is one term with stops
(Lemma S).

## 3. Lemma M: merges

Carriers c in U merge in a frame with dual W, with combination lambda. Path c has union span Z_c ⊇ W and starts on
the line <g_c>, so it pays at least `dim Z_c - 1` (walk bound). The common tail has union span T ⊇ W and pays at
least `dim T - dim W`. Every receiver of c reads c-content on path c or on the tail, so its port lies in Z_c ∪ T.

*Finite facts (CHECKED-EXACT).*
(i) <g_c> + span p_{R_c} = l_c^perp, of dimension 8.
(ii) g_a . l_c = 1 for a ≠ c.
Hence <g_a, g_c> + span p_{R_c} = F2^9 for a ≠ c, and Z_c ⊔ T = F2^9 (`sup_top_of_cover`).

**General count (PROVED-LEAN `merge_count`).**
`dim Z_c + dim T >= 9 + dim W` (`path_dim`), so `pay_c + tail >= 8` for each c. Therefore
`total + (k-1) tail >= 8k`. A merge with tail <= 1 never beats the 7k of separate carriers, for any k.

**Pairs (PROVED-LEAN `pair_merge` + CHECKED-EXACT `nocover`).**
Suppose two merged carriers pay at most 13. Combining the bounds gives `dim Z_a, dim Z_b <= 6`.
Let N be the receivers of a or b whose need (d_ja, d_jb) is not proportional to lambda.
`must_read_path` (PROVED-LEAN) shows that each such receiver must read a pure path, so N ⊆ Z_a ∪ Z_b.
The exhaustive check is over all 28 pairs, both ratios, and all 11,811 six-dimensional subspaces containing <g_a, g_b>
(WLOG dim Z_a = 6). It finds no cover with the remainder in a subspace of dimension <= 6. So every pair merge costs
at least 14 = 7 + 7.

The decoder rows are unique: on the costly pairs of every port, the 8 carrier rows have rank 8 (CHECKED-EXACT).
So the needs d_j are forced, and d_jc = ±2 exactly when j ∈ R_c.

## 4. Scope

Covered: the unique 8-carrier code of the P104 local word (PR6030 contents, unique up to sign by PR6166).
Covered mechanisms: stops, copies, branches, public relays, additions and shedding along a path, any single merge
with a tail of length <= 1, and every single merge of two carriers.

Not covered:
- merges of three or more carriers with a tail of length >= 2;
- multi-stage merge trees;
- codes with 9 or more carriers, which is the open masked floor C(P104) >= 56 beyond rank 8;
- decoders that read X directly (P-ATOM), and different words or boundaries.

The cut profile of PR6030 is tight: 8 crossings on each level 2..8 of the seven dimension cuts of
`p104-owned-coding-boundaries` (CHECKED-EXACT).
