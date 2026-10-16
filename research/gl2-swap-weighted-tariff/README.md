# Sharp asymmetric label tariffs for coordinate SWAP

In the formal coordinate-SWAP model, assign fixed nonnegative real prices A and B
to the two paid labels a and b. For t target roles and any finite `R >= t`
arbitrary-input roles, the exact minimum is

```text
                 t * (2 min(A,B) + max(A,B)).
```

This closes Open next questions item 2 of Aaron Wang's
[PR2444](https://github.com/CrocSwap/integer-mult-bounds/pull/2444), which proposed
weighted BFS for t=2,3. No further search is required for that tariff change:
even arbitrary noncommuting projectors and restored dirty spectators cannot
beat the cheaper of independent `aba` and `bab` words.

The total-call bound `3t` and its general cut argument are **inherited**, credited
to Ross Richardson's [PR1989](https://github.com/CrocSwap/integer-mult-bounds/pull/1989)
and its explicit coordinate-SWAP corollary
[PR2415](https://github.com/CrocSwap/integer-mult-bounds/pull/2415).
The additional result here is the two individual label counts and their sharp
weighted combination, with exact zero-price and changed-premise boundaries.
This is a scoped formal-model theorem, not a new native supplier or exponent.

## Model

Work in `F2[G]` for `G=GL_2(F2)`, with

```text
a = [1 1]    b = [1 0]    s = aba = bab = [0 1].
    [0 1]        [1 1]                    [1 0]
```

Every paid factor is `D_N(g) = I_R + ([g]+1) N`, where g is exactly a or b
and `N=uv^T` is a binary rank-one idempotent (`v^T u=1`). Its price is A or B,
independently of N, position, R and the surrounding word. Arbitrary scalar
`GL_R(F2)` maps may be interleaved for free. There are no additional free address
maps, clean allocations, resets, erasures or copies. Every role begins arbitrarily.
The endpoint is coefficientwise equality with
`diag([s] I_t, I_(R-t))`; every spectator is individually restored, with no
off-diagonal residual. Spectators may be reused arbitrarily during the word.
These are exactly PR2415's model hypotheses; only the two label prices change.
For t=0 the empty word attains zero; all statements allow A=0 and/or B=0.

## The two per-label bounds

Apply the natural two-dimensional representation linearly to the group algebra.
It need not be injective: a necessary consequence of a formal identity suffices
for a lower bound. Order the resulting `2R` coordinates by address coordinate,
so each operator has four `R by R` blocks. For an operator M define

```text
q_a(M) = rank_F2 M_12,       q_b(M) = rank_F2 M_21.
```

For arbitrary compatible U,V, block multiplication gives

```text
(UV)_12 = U_11 V_12 + U_12 V_22,
(UV)_21 = U_21 V_11 + U_22 V_21.
```

Rank subadditivity and `rank(XY) <= min(rank X, rank Y)` imply
`q_a(UV) <= q_a(U)+q_a(V)` and the same for q_b. This holds regardless of
commutation, invertibility or intermediate dirty couplings, so it applies to
arbitrarily long prefixes with any surrounding paid and free factors.

The natural images of paid factors and free scalar maps are

```text
D_N(a) -> [I N]      D_N(b) -> [I 0]      S -> [S 0].
          [0 I]                [N I]           [0 S]
```

Their `(q_a,q_b)` charges are `(1,0)`, `(0,1)` and `(0,0)`, respectively.
The target is `[[I-P,P],[P,I-P]]`, where `P=diag(I_t,0)`, hence its two crossing
ranks are both t. Applying subadditivity to the actual entire word proves

```text
                 n_a >= t,             n_b >= t.
```

No normalization of scalar mixing is needed, and no clean-state restriction is
introduced. All R roles are included in every block rank.

## Combining with the credited total bound

PR2415's source-bound specialization of PR1989 gives `n_a+n_b >= 3t` under the
same hypotheses. Briefly, the natural action of `GL_2(F2)` on its three nonzero
vectors identifies a,b with adjacent transpositions in S3. Its action on six
ordered distinct pairs splits into increasing and decreasing pairs. Each paid
label crosses exactly one independent direction in this cut; free scalar maps
cross none; SWAP crosses three per target. The same block-rank subadditivity
therefore gives `3t`. This paragraph restates the predecessor's proof; it is not
new work here. Exact source heads and the unchanged main proof hash are in
SOURCES.json.

If `A <= B`, then

```text
A*n_a + B*n_b = A*(n_a+n_b) + (B-A)*n_b
             >= 3A*t + (B-A)*t = (2A+B)*t.
```

Every coefficient used to multiply an inequality is nonnegative. Interchanging
a and b proves the other case. On each target role j, the coordinate projector
`E_jj` and word `aba` give exactly `[s]` on j and identity everywhere else;
`bab` does the same. Choose `aba` when A<=B and `bab` otherwise, and concatenate
over all t target roles. These full formal words attain the stated price and
leave every arbitrary spectator untouched. Thus the lower bound is sharp.

For example, `(t,A,B)=(5,1,2)` costs 20 exactly, and `(5,0,2)` costs 10 exactly.
Zero-price calls may be used freely often, but the number of positive-price
calls is still bounded as above. If both prices vanish, the minimum is zero.
The theorem is about minimum value, not uniqueness of optimal words.

## Checks and limitations

`verify.py` independently builds the six binary matrices, full group-algebra
convolution, full register matrices, their natural images and binary block ranks.
It imports no predecessor implementation. Its complete receipt records:

- 54 exact formal attaining endpoints, both orientations, t=0..8 and
  R=t,t+1,t+2; these include arbitrary dirty spectators by coefficient equality.
- All 1,302 paid factors for R=1..5 with their separate `(1,0)/(0,1)` charges;
  every two-role free scalar map on both sides of all 12 two-role paid factors
  (144 compositions).
- 2,160 mixed paid/free prefixes for R=1..6, checking the natural homomorphism,
  both rank inequalities and accumulated label bounds. These are deterministic
  sample words, not a complete search over words.
- All 25 pairs from prices `{0,1/3,1,2,7/2}`, t=0..8, against every count pair
  `t<=n_a,n_b<=4t` satisfying the three inequalities; both attaining prices.
- Controls demonstrating why each count inequality is needed, detecting a
  full-formal corruption invisible in the natural representation, rejecting an
  omitted attaining call, and verifying the direct-SWAP changed-alphabet case.
- A negative-price boundary: `D_N(a)^2=I` coefficientwise, so if A<0, appending
  arbitrarily many `aa` loops makes the cost unbounded below. Likewise for B<0.
  Nonnegative prices are therefore a substantive hypothesis.

These finite checks support the written all-parameter proof; they do not replace
it. The natural representation is used only as a lower-bound image; complete
formal coefficients verify every claimed endpoint. The inherited `3t` theorem
is not independently formalized in a proof assistant here.

The result does not cover role-dependent or state-dependent prices, different
paid labels, higher-rank calls charged as one, partial spectator restoration,
restricted clean input states, nonlinear operations, or the abelian rational
frame model. Nor does it supply native address conversion, hosting, precision,
tape bounds, a recursive child invoice or an integer-multiplication theorem.

## Reproduce

Python 3.12+, standard library, from repository root:

```sh
python3 -I -O -B research/gl2-swap-weighted-tariff/verify.py
python3 -I -O -B research/gl2-swap-weighted-tariff/test_boundary.py
python3 scripts/research_package.py --package research/gl2-swap-weighted-tariff
```

Default verification is read-only. `--out NEW_FILE` regenerates the complete
receipt and refuses overwrite. Checks use explicit failures, including under
`-O`. The boundary test verifies unchanged Git-free replay, corrupt/missing
receipt rejection and exclusive regeneration.

## Open next questions

1. Can a physically legal changed address label cross multiple directions for
   less than the corresponding invoice? This matters because fixed a/b tariff
   asymmetry is now closed. Start with one named native implementation and its
   full recursive charge; arbitrary formal labels have no such implementation.
2. What is sharp when label prices depend on the projector support? The weighted
   combination above uses a single price per label. First classify attainable
   projector-specific crossing charges; support-changing free scalar maps make
   the price convention itself part of the contract.

Contributor: ywz65 with substantial OpenAI Codex assistance. Credit remains with
Ross Richardson's general cut theorem and coordinate-SWAP bridge, Aaron Wang's
explicit asymmetric-tariff handoff, and their cited model predecessors. TASK.json
records the original picker, scope change, exact freshness and separate AI review.
No independent human review, new selected frontier or frozen-source edit is claimed.
