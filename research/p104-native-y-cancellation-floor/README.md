# The Y-cancellation arrival floor for P104 native words (no κ)

**No new κ.** This package proves, for the 104 ports of P104, where the public cancellation in each Y register must enter, how many
non-Y arrivals it needs under one stated hypothesis, and which frame pairs can supply it with only two arrivals. Nothing is priced and
no word is constructed.

## Setting

Ambient space `F2^9`. For a port `p` with vector `q_p`, `H_p = q_p^perp` is the hyperplane that is Y_p's final frame. `ports(f)` is the set of
ports whose vector lies in the frame `f`. `Orth(p) = {p' != p : q_p . q_p' = 0}`. `𝟙` is the all-ones functional, so `v.𝟙 = wt(v) mod 2`.

Operation rules used (verifier text):

* public MOVEs strictly ascend, owned MOVEs strictly descend; ADD and COPY act at a common frame;
* X_p starts at `[q_p]` and ends with `e_Xp`; Y_p starts at dimension 0 and ends at `H_p` with `e_Yp + e_Xp`;
* births carry only the register's own unit;
* an owned MOVE arrival is replaced by a fresh symbol, so every value is a public part (a combination of the units) plus a symbol part.

**Lemma A (content in frame).** The public x-support of any register lies in `ports(its current frame)`.
*Proof.* X_p is born at `[q_p]`, and no other birth has x-content. An ADD or COPY at a frame moves only content supported on the ports of that frame.
A public MOVE goes to a superset frame. An owned arrival resets the public part to 0. ∎

**Lemma C (span at a frame).** Every value held at a frame `phi` has its public part in the span of the public parts of the arrivals at `phi` (MOVE arrivals and births).

## Statement

**Theorem.**

1. **(General, owned-only routing.)** Every port has odd weight, so `q_p` is not in `H_p`, and every frame inside `H_p` contains no `q_p`.
   Hence the `e_Xp` coefficient of Y_p's final value comes entirely from owned symbols: X content reaches Y_p's final value only via owned
   descents. This holds for every legal native word.
2. **(Under H3.)** Let `S_p` be the x-support of the public part of Y_p's final value, and assume

   **(H3)** `S_p` is contained in `Orth(p)` and spans `H_p`.

   Let `g_p` be the last frame Y_p visits before `H_p` (dimension 0 if Y_p makes a single jump), and `A_p` the set of non-Y registers that make a
   public MOVE into `H_p`, each from its source frame `a_r`. Then `S_p ⊆ ports(g_p) ∪ ⋃_{r ∈ A_p} ports(a_r)`, and therefore
   * `A_p` is non-empty for every port;
   * `|A_p| >= 2` if Y_p has no interior stop below `H_p`;
   * two arriving frames `f1, f2` (each a proper subspace of `H_p`) cover `Orth(p)` **exactly when** they lie in a parity-complementary pair of hyperplanes
     `K = H_p ∩ a^perp`, `K' = H_p ∩ (a+𝟙)^perp`. There are exactly 127 such pairs per port, and no single hyperplane of `H_p` covers `Orth(p)`.
3. **(Remark: H3 is not forced.)** Legality does not force H3. `S_p = ∅` is attainable by one extra owned rank-1 term per port (per native call),
   which delivers `e_p` to Y_p through an owned descent so that no public cancellation of x content is needed. Its cost is not computed here.
   Dropping H3 for a port therefore costs one owned rank-1 paid move per port per call.

**Scope.** (1) is for the P104 instance and all legal words. (2) is conditional on H3. The statement concerns frame supports only: it
says nothing about junk, owned-symbol intake or arithmetic, which can add further constraints, and it prices nothing.

## Proof

**(1)** Frames inside `H_p` are subspaces of `H_p`; since `q_p . q_p = wt(q_p) mod 2 = 1`, `q_p` is not in `H_p`, so `p ∉ ports(f)` for those frames. By
Lemma A the public part of Y_p never has `e_Xp` content at a frame inside `H_p`. Y_p ends with `e_Yp + e_Xp`, so the `e_Xp` coefficient
arises from owned symbols, which enter by owned (descending) MOVEs. ∎

**(2) Support inclusion.** Y_p's final public part is a sum of what Y_p read. Reads at interior frames `f ⊆ g_p` have support in `ports(g_p)` (Lemma A).
Reads at `H_p` have public part in the span of the arrivals at `H_p` (Lemma C): Y_p's own arrival (support in `ports(g_p)`), births at `H_p`
(no x-content), and arrivals of registers in `A_p` (support in `ports(a_r)`). Hence the union.

**Floor.** Every `a_r` and `g_p` is a proper subspace of `H_p` (public MOVEs strictly ascend), so each lies in a hyperplane of `H_p` and `ports(·)` of it lies in
the ports of that hyperplane. Under H3 `S_p` spans `H_p`, and a set inside one hyperplane of `H_p` does not span `H_p`. So the union needs at least two
hyperplanes. If `g_p` is an interior stop it supplies at most one, so `|A_p| >= 1`. If Y_p has no interior stop, `g_p` is the dimension-0 frame
with `ports(g_p) = ∅`, so `|A_p| >= 2`.

**Exact two-cover.** Take hyperplanes `K1, K2` of `H_p` with `Orth(p) ⊆ ports(K1) ∪ ports(K2)`. Write `K_i = H_p ∩ b_i^perp`. For
`a` not in `{0, 𝟙, q_p, 𝟙+q_p}` (so both are hyperplanes of `H_p`), `K = H_p ∩ a^perp` and `K' = H_p ∩ (a+𝟙)^perp` cover `Orth(p)`: each `v ∈ Orth(p)` has odd weight, so `v.a` and `v.(a+𝟙)` differ and one is 0. That gives
127 covering pairs: the 255 hyperplanes are the functional classes `a` mod `q_p`; the class of `𝟙` meets `Orth(p)` in nothing (its partner would be all of `H_p`), and the other 254 classes pair up as `{a, a+𝟙}`. Conversely, the
exhaustive count in `check.py` finds, among all C(255,2) hyperplane pairs of `H_p`, exactly 127 covering pairs, so they are exactly the complementary ones. Two arriving frames
cover only if they sit in a covering pair, so only if they sit in a complementary pair. No single hyperplane covers because `Orth(p)` spans `H_p` (rank 8, checked). ∎

**(3)** If one owned rank-1 term delivers `e_p` to Y_p through an owned descent, Y_p's `e_Xp` content no longer needs a public cancellation of the
orthogonal entries, so `S_p = ∅` and H3 fails for that port. Each such term is one owned paid move per port per native call. ∎

## Exact checks (`check.py`, `verify.sh`)

From the 104 ports of `research/p104-designer-toolkit-v2/words/5561.json.gz`, recomputed from the port list only:
all weights odd and `q_p ∉ H_p`; `|Orth(p)| = 48` and GF(2) rank 8 for all 104 ports; the 255 hyperplanes of `H_p`; no single covering hyperplane; exactly 127 covering
pairs per port, all of the form `{a, a+𝟙}`. Marker: `PASS_P104_NATIVE_Y_CANCELLATION_FLOOR`.

## Open next questions

1. Is there a legal native word in which every Y_p has no interior stop and exactly one parity-complementary pair of arrivals at `H_p`, with the arrival junk balanced?
2. Which cheaper route than one owned rank-1 term per port per call makes `S_p` empty, or removes H3 for a group of ports?
3. For a specific legal word, how many interior stops are cover-critical? This needs a native word that is part of the base repository.

The structured form with first steps and blockers is in `TASK.json`.
