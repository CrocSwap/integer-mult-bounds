# One premium adjacent swap: an exact dirty-register tariff

In the formal `F2[S_n]` register model, making one adjacent generator more
expensive does not enable cross-register savings. If `s_p` costs `beta` and
all other adjacent generators cost `alpha`, where `0 <= alpha <= beta`, the
exact cost of a heterogeneous diagonal target tuple is

```
alpha * sum_j inv(w_j) + (beta - alpha) * sum_j c_p(w_j),
c_p(w) = #{i : 1 <= i <= p and w(i) > p}.
```

This answers the S4 price `(1,2,1)` first experiment in
[PR1989's weighted-price handoff](../symmetric-adjacent-cut-bound/README.md#open-next-questions),
and proves the same statement for every `n >= 2`, every cut `1 <= p < n`,
and every finite number of restored dirty spectators. It does not settle
arbitrary unequal prices, supply a native BIT implementation, or improve kappa.

## Model and lower bound

Use the exact formal model of
[PR1989's proof](../symmetric-adjacent-cut-bound/PROOF.md). Multiplication is
`gh = g after h`. Registers are column vectors over `F2[S_n]`. A paid call is

```
D_N(s_i) = I_R + ([s_i] + 1)N,
s_i = (i,i+1),  N = u v^T over F2,  v^T u = 1.
```

Arbitrary scalar `GL_R(F2)` mixing may occur for free anywhere in the word.
For every finite `R >= W`, the complete endpoint must be
`diag([w_1],...,[w_W],1,...,1)`. All input registers are arbitrary, all
spectators return unchanged, and all off-diagonal couplings vanish.
Preparation and restoration are charged. There are no free address maps,
resets, erasures, or clean-input assumptions. Identity targets and an empty
target list are allowed.

Let `Q` be the total paid-call count and `Q_p` the count carrying label `s_p`.
PR1989's ordered-pair cut proves

```
Q >= L,   L = sum_j inv(w_j).
```

This is inherited evidence, not a new unit-price theorem. To bound `Q_p`,
use the natural permutation action on `F2^n`, split into the address spaces
`H = span(e_1,...,e_p)` and `K = span(e_(p+1),...,e_n)`, including all register
roles in both halves. For any represented operators `U,V`,

```
(UV)[K,H] = U[K,H] V[H,H] + U[K,K] V[K,H],
rank((UV)[K,H]) <= rank(U[K,H]) + rank(V[K,H]).
```

Scalar mixing has crossing block zero. The crossing block of a paid factor
is `N tensor P_(s_i)[K,H]`, with rank one for `i=p` and zero otherwise.
For a permutation `w`, its crossing block has exactly `c_p(w)` nonzero
columns, which are distinct standard basis vectors. The diagonal endpoint
therefore has crossing rank `C = sum_j c_p(w_j)`. Iterating the inequality
in chronological order proves `Q_p >= C`, including all dirty spectators.

Every legal word consequently costs at least

```
alpha*Q + (beta-alpha)*Q_p >= alpha*L + (beta-alpha)*C.
```

Both coefficients must be nonnegative. A representation is used only for
this necessary lower bound, never to accept a full formal endpoint.

## Simultaneous attainment by descent sorting

The two bounds are simultaneously attainable for each permutation. This
step is essential: independent lower bounds alone would not prove an exact
weighted optimum.

Start with the one-line list `w(1),...,w(n)` and sort it as follows.

1. Sort the first `p` positions and the last `n-p` positions separately,
   swapping only adjacent descents within each block.
2. If a value greater than `p` remains in the left block, swap positions
   `p,p+1` and repeat step 1. Otherwise stop.

After step 1, if the left block contains a value greater than `p`, its last
value is greater than `p`. There must also be a value at most `p` in the
right block, since the two blocks together contain each value exactly once.
Its first value is at most `p`. Thus the boundary swap is an adjacent descent
and decreases `c_p` by exactly one. Internal swaps preserve `c_p`.

Every swap in the procedure removes exactly one inversion. There can be no
infinite loop. When `c_p=0`, each sorted block contains its own value set,
so the whole list is the identity. The procedure uses exactly `inv(w)`
swaps in total and exactly `c_p(w)` copies of `s_p`.

If the sorting swaps are `t_1,...,t_l`, then
`w t_1 ... t_l = e`, hence `w = t_l ... t_1`. Execute the coordinate-projector
calls `D_(E_j)(t_1),...,D_(E_j)(t_l)` chronologically on target role `j`.
Column operators act rightmost first, so their final product is `[w]` on
that role. This is an identity in the full formal group algebra. Concatenating
the role words gives the required heterogeneous endpoint and leaves every
spectator untouched at every step.

The attaining circuit needs no extra roles, scalar changes, copies, or
unpriced cleanup. Its full formal bill is exactly the displayed lower bound.
Zero tariffs remain covered. Physical realization and its additional charges
are not asserted free.

## Verification

The uniform result follows from the written argument above. The executable
checks corroborate its finite instances and test the stated boundaries;
they do not constitute a proof-assistant verification.

The standard-library verifier checks the constructive sorting counts against
independent exact weighted Dijkstra distances, checks represented factor
charges, and checks full formal endpoints with dirty spectators. It also
checks that omitting a call, reversing noncommuting calls, or leaking a dirty
spectator changes the required endpoint. The `beta < alpha` control shows
why this tariff formula is not asserted outside its domain.

Ordinary and optimized CPython 3.12 replays passed with:

- 126 complete Dijkstra runs and 206,436 exact tariff comparisons, covering
  every permutation in S2 through S7, every cut and six price pairs, including
  zero and rational prices; 34,406 constructed sorting words.
- 2,100 paid-factor and 3,500 free-mixing crossing-rank checks.
- All 576 ordered S4 target pairs with a dirty spectator, plus a noncommuting
  pair under all 168 scalar GL3 changes and their inverse restoration.
- 45 invalid-input, four formal-endpoint and two source-drift rejections,
  plus zero-price/identity controls and two nonfaithful-representation checks.

The discounted-label boundary has an explicit counterexample: in S3, the
reversal with `p=1, alpha=2, beta=1` costs four, not the formula's five.
This is outside the theorem, and the tariff API rejects it.

From the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/symmetric-single-premium-tariff
python3.12 -I -O -B research/symmetric-single-premium-tariff/verify.py
```

Exact source pins and historical assignment provenance are in
[SOURCES.json](SOURCES.json), and scope/overlap metadata are in
[TASK.json](TASK.json). This package does not run the selected-supplier cold
replay because it changes neither the selected construction nor its inputs.

## Open next questions

Does a heterogeneous tuple admit sharing with more than one premium adjacent
label, or with one discounted label? Start with S4 prices `(2,1,2)`: compute
exact direct distances, then seek a common weighted cut certificate or a full
formal sharing witness. The present two-count proof does not settle that
price vector. A matching lower bound, not more digits of a known moment, is
the missing step.

Native adoption separately needs a physically legal address/scalar interface,
all frame/hosting/restoration and precision/tape charges, and a complete
recursive profile. No such supplier or all-size multiplication theorem is
claimed here.

## Credit

Ross Richardson's PR1989 supplies the formal symmetric-group model, the
unit-price theorem and the explicit S4 weighted handoff. Its cut method
credits Adam Gall's PR1941 and Ross Richardson's PR1966; the retained
predecessor sources remain unchanged. The adjacent descent and crossing-rank
arguments are standard methods, not claimed as new general techniques.

Concurrent [PR2544](https://github.com/CrocSwap/integer-mult-bounds/pull/2544),
by ywz65 at `9fb1552f12ca4777ca660461a8b602e709285f99`, proves the asymmetric
coordinate-SWAP tariff in the two-generator model. That overlapping special
case is credited. This contribution adds arbitrary symmetric groups, cuts
and heterogeneous target tuples under one premium label, with simultaneous
attainment by a constrained sorting procedure. It does not claim priority
beyond these checked repository sources.

Prepared by starship-s with substantial Hermes (`gpt-6-astra-900k`) and
OpenAI Codex (`gpt-6-astra`) assistance. No independent human review or
formal-kernel verification is claimed. New work is Apache-2.0.
