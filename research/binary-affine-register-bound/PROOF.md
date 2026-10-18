# Exact cost in the binary affine register model

This is a written, all-dimension theorem about the following operation
alphabet. The finite checks are corroboration, not its universal justification.
It is not a theorem about the selected rational-address supplier.

## 1. Complete model and bill

Fix `d >= 1` and `r >= w >= 1`. Let `G = AGL_d(F2)`, with
`g=(A,b)` acting on an address as `x -> A x + b`. Multiplication is composition;
the rightmost factor acts first. Let `R = F2[G]` be the **formal group algebra**.
The labels need not commute. A register word is an `r` by `r` matrix over `R`.
It must work on every `R`-module and every register input, not just one finite
point-action representation.

Write the homogeneous representation and its displacement rank as

\[
 H(g)=\begin{pmatrix}A&b\\0&1\end{pmatrix},\qquad
 \rho(g)=\operatorname{rank}_{\mathbb F_2}[A-I\mid b].
\]

The complete alphabet is:

* A free scalar basis change `B in GL_r(F2)`. Thus arbitrary scalar XOR
  preparation/restoration is allowed for free in this optimistic paid-call
  relaxation. These maps do not change addresses.
* One **paid unit call**
  \[
    D_N(g)=I+([g]-1)N,
    \quad N=uv^T,\quad v^Tu=1,\quad \rho(g)=1.
  \]
  Here `N` is a binary rank-one idempotent and `g in G`. Both nonzero
  translations and rank-one affine transvections are paid units. In particular,
  translations are not free. Every occurrence costs one, including any that
  undo an earlier call.

No other address map, COPY, erasure or clean-register creation is free. The
`r-w` extra registers may be as numerous as desired but must be restored for
**arbitrary dirty inputs**. Their availability itself is granted for free in
this relaxation. A positive physical implementation would still need to price
its real scalar work, storage and caller interfaces; granting these favors
cannot weaken the lower bound below.

The required boundary is exactly

\[
 F=\operatorname{diag}([g_1],\ldots,[g_w],1,\ldots,1)
 \quad\text{in }M_r(R).
\]

**Theorem.** Its minimum number of paid calls is

\[
 \boxed{\displaystyle\sum_{j=1}^{w}\rho(g_j)}.
\]

Thus neither noncommuting binary affine labels nor arbitrarily many restored
dirty registers save a paid call against the direct bill in this alphabet.
This does not identify `rho` with the selected supplier's rational frame rank.

## 2. Free scalar operations do not hide a charge

Move every scalar basis change to the right through the paid calls. Conjugating
one call by `B` replaces `N` with `BNB^-1`, another binary rank-one idempotent,
and leaves `g` unchanged. Any mixed word therefore becomes a product of paid
calls followed by the product `B_total` of all free scalar maps.

The augmentation homomorphism `R -> F2`, `[g] -> 1`, sends every paid call to
the identity. The required boundary also augments to the identity. Hence
`B_total = I`, and the normalized word consists only of its original number
of paid calls. This argument does not allow free address transformations:
they are a different operation class and cannot be normalized by this scalar
augmentation argument.

## 3. Representation-rank lower bound

The group homomorphism `H` extends linearly to a ring homomorphism
`R -> M_(d+1)(F2)` and entrywise to an `r(d+1)`-dimensional representation.
Commutativity of `G` is never used. The image of a paid call is

\[
 \widehat D_N(g)=I+N\otimes(H(g)-I).
\]

Consequently `rank(widehat D_N(g)-I) = rank(N) rho(g) = 1`.
For any square matrices `P,Q`,

\[
 PQ-I=(P-I)Q+(Q-I),\qquad
 \operatorname{rank}(PQ-I)\leq
 \operatorname{rank}(P-I)+\operatorname{rank}(Q-I).
\]

Induction bounds the displacement rank of an `s`-call word by `s`. The
image of the required target is block diagonal, so its displacement rank is
`sum_j rho(g_j)`; every restored extra-register block contributes zero.
This proves the lower bound for every word length, register count and address
dimension. Intermediate mixing with dirty registers is unrestricted.

The representation is **not faithful on the group algebra**. Only the
implication from a formal identity to a represented identity was used. For
example, the sum of all 24 formal elements of `AGL_2(F2)` is nonzero but has
zero homogeneous image and zero augmentation. Represented equality is therefore
not an acceptance test for formal word identities.

## 4. An attaining factorization for every affine map

First consider `A in GL_d(F2)`, and put `m=rank(A-I)`.
There is a product of exactly `m` linear transvections equal to `A`.
Here is a constructive proof with no dimension cutoff.

If `A != I`, let `V=ker(A-I)`, choose `v` outside `V`, and put `u=Av+v`.
Then `u != 0` and `v` is outside `V + span(u)`. Indeed, the only additional
possibility over `F2` is `v=z+u` for fixed `z`; that would give `Av=z`.
Since `A` is invertible and fixes `z`, it would force `v=z`, a contradiction.

Choose a linear functional `f` vanishing on `V` and `u`, with `f(v)=1`.
The map `T=I+u f` is a rank-one transvection and satisfies `T²=I`.
The map `TA` fixes `V` and also `v`, since `f(Av)=f(v+u)=1`.
Thus `rank(TA-I) <= m-1`. The rank inequality applied to `A=T(TA)` gives
the reverse inequality, so the rank drops by **exactly one**. Repeat until
the identity is reached. Reversing the reduction equation gives an ordered
factorization `A=T_1 ... T_m`. The implementation solves the stated linear
constraints for `f`; it does not guess a factorization length from sampling.

Now let `g=(A,b)` and let `M=A-I`.

* If `b` belongs to `im(M)`, choose `c` with `Mc=b`. Translation by `c`,
  denoted `tau_c`, gives
  `g = tau_c (A,0) tau_c`. Conjugate each of the `m` linear factors by
  `tau_c`. Every conjugated factor has homogeneous displacement rank one
  and their product is exactly `g`. The conjugations describe each paid
  affine label; they are not uncharged instructions inserted into the word.
  This case has `rho(g)=m`.
* If `b` does not belong to `im(M)`, write `g=tau_b (A,0)`. The nonzero
  translation is one paid unit, followed by the `m` linear factors.
  This case has `rho(g)=m+1`.

This includes the identity and pure translations. Each attaining list
contains exactly `rho(g)` allowed labels.

For any scalar idempotent `N` and arbitrary group elements `a,b`, direct
expansion in the formal, possibly noncommutative group algebra gives

\[
 D_N(a)D_N(b)=D_N(ab).
\]

Apply the affine factorization for `g_j` using the coordinate projector
`E_jj`. The factors multiply to the required formal diagonal block.
Concatenating the blocks gives a word of length `sum_j rho(g_j)`, fixes
every other register on arbitrary dirty input, and uses no additional
register, scalar basis change, copy or erased value. This matches the lower
bound with the full paid bill, not merely a represented endpoint.

## 5. Verification, attribution and scope

The finite replay independently compares complete Cayley distances with the
formula for every affine map in dimensions 1 through 4. It also constructs
and checks an attaining factorization for every one of those maps. The native
BFS does not use rank pruning or the factorization algorithm. A separate
small point-permutation BFS checks dimensions 1 and 2. These checks can expose
coding mistakes; Sections 2–4 supply the unbounded mathematical argument.

Rank subadditivity and linear reflection length are classical. For the latter,
see Huang, Lewis and Reiner,
[Absolute order in general linear groups](https://arxiv.org/abs/1506.03332v2),
and delMas and Lewis,
[Reflection length in the general linear and affine groups](https://arxiv.org/abs/1803.03070v1).
The latter paper's affine reflection alphabet differs from ours: we also
permit nonzero translations as one **paid** generator. No new reflection-length
principle or literature priority is claimed.

The contribution is the explicit nonabelian register-model cost statement,
its dirty-register/free-scalar boundary, complete attaining construction and
independent exhaustive certificate. Eumemic's PR288 develops related rank
methods; Ali Romman's PR468 and David Govea's PR720 concern the abelian
rational three-register model. This changes that address algebra and cost
contract; it neither generalizes their rational theorem nor reduces rational
frame entries modulo two. Free address maps, a different unit-price rule,
other payload fields, clean-only boundaries and selected-supplier physical
admission remain outside the stated theorem. No kappa improvement follows.
