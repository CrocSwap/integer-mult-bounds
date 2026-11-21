# Thin caller window: exact relaxation screens

This local investigation concerns the `Q >= 1`, `e = 0` branch of
[#7852 at `41beda1d6435760dc99e38bd7e65f36798aad212`](https://github.com/CrocSwap/integer-mult-bounds/pull/7852).
It gives two high-price **configuration-level** screens at `k = 76`, followed
by rank arguments showing that neither screen can be a tight signed-Gram
frame. It does not bound all `k = 76` legal callers, exhibit a caller, or
improve the complete multiplication bound. The three-stage sign strengthening
and common-piece argument were independently checked by another Codex
research lane.

## Reproduction and sources

```sh
cd .
python3 -B check_thin.py
```

The script checks Git blob identities for the relevant pinned #7852 and
[#7113 at `07a76c5e2738882c0cb322278e56f6cae3c9885d`](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
files, and verifies the #7113 caller SHA-256 against its own pinned replay
receipt. It constructs the masks and pieces, checks the `LawQ` rows, stronger
pairwise RC2 counts, and the per-stage leaf cap. Its exact results and
coefficients are in [RESULT.json](RESULT.json). Every reported bound on
`b^(99/100)` follows from integer inequalities `L^100 <= b^99*10^1200 <
(L+1)^100`, then exact rational interval arithmetic. Decimal endpoints are
rounded outward. The linear-algebra arguments below are paper proofs, not Lean
proofs or an exhaustive search.

The source files are copied under `source/`; their expected Git blob hashes
are recorded and checked in `check_thin.py`. The principal references are
`CallerHPQ.lean` (`Cfg.LawQ`, `Cfg.valQ` and the adjacent closed-form bound),
`HPDual.lean` (`roleVal`, `rowS`), `CallerRC2.lean` (`Pieces`, `rc2_pair`),
`CallerCfgBridge.lean` (word-to-configuration, per-stage leaf bound),
`CallerSGram.lean` (signed Gram matrix and its rank), and `SchemaCostB.lean`
(`repo_eq`). Actual #7113 event pricing is at lines 127–132 of the pinned
`emit_odd_type_ab.py`.

## Price and independent controls

Put `s = 99/100`. For a type-B caller with `k` stages, the pinned prices
charge one item per port:

* a diagonal role with stage mask `M` and odd exponent costs
  `(8 |M| + 1)^s` on the target side;
* a plain `QUERY` costs `1`, `IDLE_ONE S` costs `(8 |S|)^s`, and
  `IDLE_ODD S` costs `(8 |S| + 1)^s` on the paid side;
* each native type-B stage has two rank-8 contacts, charged separately.

Thus the caller expression used here is

`repo = sum(targets) - sum(plain paid) - 2 k 8^s`.

For a tight word, `Q = T = n - (2k-2)`, #7852's `repo_eq` states that this
is `(k/104) cHatQ + sum(delta)`, with one contribution for each odd idle:

`delta(S) = (8|S|)^s + 1 - (8|S|+1)^s` for nonempty `S`, and zero for an
empty `S`. The sign is important: the correction is **added** to the modeled
caller expression. The calculations below treat a synthetic set of stage
masks as if its one thin event were an odd idle on one stage. They do not
claim that such event masks come from any legal word.

The source-bound #7113 control has `k = 17`, 36 roles of each type, and
`Q = 4` for each. Type A has 96 ports and four QUERY events; type B has eight
ports and four `IDLE_ODD` events. The latter are rows 68, 69 with stage set
`[8]` and rows 70, 71 with `[9]` (the caller file uses one-based stages).
Their unweighted sum of corrections is in
`[0.123823636528, 0.123823636536]`; the correction after type-B port weighting
and division by 17 is `[0.058269946601, 0.058269946606]`. Type A's correction
is zero. The reconstructed target and paid rank histograms and both
type-specific prices are in `RESULT.json`.

The independent adjacent `k = 77` control evaluates #7852's closed-form
`104/k * F2(k)` in
`[128.881427773629, 128.881427774249] < 128.891`, consistent with its
stated model bound. The `k = 77` configuration below has modeled value
`[128.873319618419, 128.873319619038]` and, with one singleton odd idle,
the synthetic repo-profile value
`[128.915130196989, 128.915130197606]`. This illustrates the correction; the
configuration is excluded by the structural argument and is not a caller.

## First k = 76 configuration and necessary triple cut

Use zero-based stages `0,...,75`, `n = 151`, `Q = T = 1`:

* two all-stage hub roles, each made of 76 singleton main pieces;
* 73 degree-two roles, each with the single piece `{0,1}`;
* 76 leaf roles, one at each stage, each with one singleton piece.

The 152 main incidences are exactly two per stage. Every `RC2_l` averaged row
for `3 <= l <= 76` equals `2*76*75 = 11400`: the hubs provide the whole row
and the other roles provide zero. The two hubs themselves meet all
`RC2_pair` inequalities for every ordered stage pair and every `l >= 2`.
There are 75 nonleaves, meeting `LC >= 74`, and `76*151 - 76 =
76*(2*76-2) = 11400`, so `LEAFAVG` is tight. Every stage has exactly one
leaf, meeting the stronger per-stage cap of one when `T = 1`.

The target histogram is `{9: 76, 17: 73, 609: 2}`. Assign the one thin to a
leaf's singleton piece as `IDLE_ODD`; the plain paid histogram then is
`{8: 75, 9: 1, 16: 73}`, with the 152 rank-8 native contacts separate. The
model's all-piece histogram is `{8: 228, 16: 73}`. Scaling by `104/76`:

* modeled `cHatQ`: `[129.041555678999, 129.041555679618]`;
* actual-price abstract profile: `[129.083916396761, 129.083916397378]`;
* odd-idle correction: `[0.042360717759, 0.042360717763]`.

This is a feasible point for the listed **relaxation rows**, not a legal
caller. Indeed, a three-stage signed-Gram lemma rules out the entire profile
even if the 73 degree-two masks are placed differently.

### Three-stage sign lemma

Work over a field of characteristic not two. Suppose ordered host stages
`a < b < c` each have two host columns, their diagonal blocks of
`K = 2I + G_diag + G_up - G_low` are invertible, and `rank(K) <= 2`. If the
only roles meeting any pair of these stages are the **same two** roles `H`,
then no such matrix exists.

Proof. Invertibility of any diagonal block forces rank exactly two, and rank
factorization gives `K_ij = X_i Y_j` with all `2 x 2` factors invertible.
For distinct selected stages, off-mask support and the definition of `K`
give `K_ij = sgn(j-i) B_(i,H)^T A_(j,H)`. These cross blocks are invertible,
so all their two-by-two factors are invertible. Set
`D_i = (B_(i,H)^T)^(-1) X_i` and `E_j = Y_j (A_(j,H))^(-1)`. Then
`D_i E_j = sgn(j-i) I`. Column `b` implies `D_a = -D_c`; column `a` implies
`D_b = D_c`; column `c` implies `D_a = D_b`. Hence `2 D_c = 0`, a
contradiction. Thin columns elsewhere do not affect this host-block argument.
The common two-column block condition must hold; applying it to type A uses
the separate regrouping bridge of #7852.

In particular, if two roles are present at every stage, every 3-stage subset
must contain a pair of stages jointly covered by some **other** role.
Counting role/stage-pair/triple incidences gives the necessary inequality

`sum_(r outside H) C(D_r,2) >= ceil(k(k-1)/6)`.

At `k = 76` the right side is 950, while this screen has 73. Equivalently,
the 73 pairs cover at most `73*74 = 5402` of `C(76,3) = 70300` triples
even with multiplicity; so at least 64898 triples are uncovered. This rules
out all placements of its pair masks in a frame satisfying the lemma's
assumptions. The `k = 77` analogue has 74 pairs versus a necessary 976.

## A clustered control and common-piece refinement

A capacity-only triple cut does not close the price window. Replace two of
the 73 pair roles above by two roles with masks `0,...,37` and `38,...,75`,
each a single 38-stage piece. Keep two hubs, 71 pair roles, and 76 leaves.
Every triple has two stages in a cluster, so the non-hub pair-overlap graph
has no independent triple. Its counted pair capacity is
`2*C(38,2)+71 = 1477 >= 950`. All other verified rows above remain valid.
The target histogram is `{9:76, 17:71, 305:2, 609:2}`; the actual plain
paid histogram with one singleton `IDLE_ODD` is
`{8:75, 9:1, 16:71, 304:2}`, with 152 rank-8 contacts separate. Its scaled
modeled value is `[128.965854418359, 128.965854418978]`; the corrected
abstract repo profile is `[129.008215136121, 129.008215136738]`.

This second family is also impossible under the full piece and signed-Gram
hypotheses. The useful refinement of the lemma is: if the **same** set `H` of
`h` roles supplies each of the three pairwise overlaps, and there are `h-2`
independent vectors supported on `H` killed by the three host `B^T` blocks,
the same contradiction holds. Invertible cross blocks make each
`B_(s,H)^T` rank two. Its kernel is exactly the common `(h-2)`-space, so each
factors through one two-dimensional quotient; replacing `B_(s,H)^T` by those
quotient factors reduces to the preceding sign proof.

For a triple inside one cluster, if no pair-role mask lies in that triple,
`H` contains precisely the two hubs and the cluster role. The cluster's
38-stage piece has a nonzero kernel vector supported in `H`: `Pieces.x_supp`
and `x_ker` give support and annihilation; `biorth` against itself gives
nonzero. Thus every triple inside either cluster must contain a pair role.
One pair covers at most 36 in-cluster triples. Each cluster has
`C(38,3) = 8436` triples and hence needs at least 235 internal pair roles;
the two disjoint clusters need at least 470, whereas the configuration has
71. This conclusion holds for any placement of those 71 pair masks. The
checked sample uses `[2,3,4]` in the first cluster.

DreamingOfClouds with Claude Opus 5.5 prepared #7852; rohanarun prepared the
#7113 signed-caller control. The new checks and conditional rank argument
above build on their pinned definitions and do not claim either package's
existing results as new.
