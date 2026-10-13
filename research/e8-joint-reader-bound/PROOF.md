# Joint-reader obstruction through 55 E8 punctures

**Scoped structural negative result.** In the root-only E8 binary label
decoder with additive star copy-rank accounting, no deletion of at most 55
of the 120 real root lines improves the copy-cost/live-port ratio `63/111`.
This extends the at-most-35 exclusion of Chi Zhao / PR631 and the
36-puncture equality analysis of Philipp (@mightyOil) / PR875. The new step
is a compatibility constraint on two distinct readers subjected to the
**same** deletions; it does not assume the existence of nine simultaneously
cheap readers.

This is a written mathematical argument supported by exact finite root/code
arithmetic, not a proof-assistant formalization. In particular, the
finite checks are not an enumeration of all puncture subsets: the geometric
reduction and support-union argument below supply their coverage.

## 1. Precise model and inherited facts

Let `L_0,...,L_119` represent the 120 unoriented E8 root lines in doubled
standard coordinates, each of squared norm 8. Define the binary matrix

```
B_st = (1 + L_s · L_t / 4) mod 2,
C = rowspace_F2(B).
```

The entries before reduction modulo two are integers. The inherited exact
code census is

```
dim_F2 C = 9,
{ wt(c) : 0 != c in C } = { 56, 64, 120 },
weight multiplicities = { 56: 255, 64: 255, 120: 1 }.
```

For a deleted set `P` of root indices, put `p=|P|` and `v=120-p`. For a
nonzero reader `c in C`, its physical star rank is

```
s_P(c) = rank_Q { L_t : c_t=1 and t not in P }.
```

The cost under discussion is

```
C_star(P) = min { sum_{i=1}^9 s_P(c_i) : (c_1,...,c_9) is a basis of C }.
```

This is the star decoder model used by Joel Pulikkan / GamingPuzzled's
PR620 and inherited in PR631. It assumes unrestricted independent input
bits and additive costs for star totals. Additional totals whose
functionals span `C` contain a basis, so their nonnegative costs cannot
improve this minimum. This reduction does not identify star rank with
general source/reader pairing rank.

For `p<=55`, restriction from `C` to the live ports is injective: a
nonzero codeword that vanished there would have its entire support in `P`,
contradicting the minimum weight 56. Consequently all nine reader
dimensions remain necessary, and independence before and after restriction
agrees. An invertible change of binary label coordinates preserves these
conditions.

The proof inherits the sharp single-reader deletion thresholds from PR631:

| Rank bound d | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Minimum required deletions delta_d | 56 | 55 | 53 | 50 | 44 | 36 | 26 | 1 | 0 |

Thus `s_P(c)<=d` requires `p>=delta_d`. The last entry is the trivial
full-space extension of the predecessor's table. Also inherited is its
small-puncture identity, valid for `p<=13`:

```
C_star(P) = 72 - rank_F2 { u_t : t in P }.
```

Here `u_t` are the binary labels of the deleted root ports, in any fixed
nine-dimensional label coordinates. We need only its consequence
`C_star(P)>=72-p` for `p<=8`. These inherited facts, their finite census,
and their coverage arguments are preserved in
[the pinned PR631 source](sources/pr631/README.md); they are not new claims
of this contribution.

## 2. Root-line capacities of physical spans

For `d=0,...,8`, let `M_d` be the maximum number of the 120 root lines
contained in a root-spanned rational subspace of dimension at most `d`.
The exact capacity table is

| Dimension bound d | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| M_d | 0 | 1 | 3 | 6 | 12 | 20 | 36 | 63 | 120 |

The standard parabolic types attaining the nontrivial entries are
`A1,A2,A3,D4,D5,E6,E7`; full E8 gives the last entry. Counts are of
**lines**, so are half the corresponding numbers of signed roots.

For completeness, the all-subspace reduction is the same one used in
PR631. If `F` is a proper root-spanned subspace, choose a generic real
vector `n in F^perp` that is perpendicular to no root outside `F`. Such
a choice exists because there are finitely many roots outside `F`, each
excluding a proper hyperplane of `F^perp`. Move `n` into the closed
fundamental Weyl chamber. In a simple root system, every positive root has
nonnegative simple-root coefficients. Its inner product with this chamber
vector therefore vanishes exactly when its support uses only simple roots
orthogonal to the vector. The roots in the transported `F` are precisely
those in this standard parabolic span. Because `F` was root-spanned,
the dimension of that span is `dim F`.

It follows that the finite census of all 256 subsets of the eight simple
roots, including the empty and full subsets, computes these capacities for
every root-spanned subspace. For an at-most-d bound, a smaller standard
subset can be extended to size d, so taking the maximum at exact size d
also suffices. The full-dimensional case is immediate. In particular, any
surviving reader of rational rank `d` contains at most `M_d` root lines.
This step concerns physical geometry alone and does not require a common
Weyl transformation for two different reader spans.

## 3. The new joint-reader inequality

Let `c,d` be two distinct nonzero words of `C`, and write `R_c,R_d` for
their supports before deletion. The word `c+d` is also nonzero. By the
minimum weight and the binary support identity,

```
|R_c union R_d|
  = (wt(c) + wt(d) + wt(c+d)) / 2
  >= (56 + 56 + 56) / 2
  = 84.
```

If their surviving rational ranks are `a=s_P(c)` and `b=s_P(d)`, their
surviving sets have cardinalities at most `M_a` and `M_b`. A single set of
`p` deleted ports removes at most `p` members of their union, including
ports shared by both readers only once. Therefore

```
84 - p
  <= |(R_c union R_d) minus P|
  <= |R_c minus P| + |R_d minus P|
  <= M_a + M_b.                                      (1)
```

No disjointness is assumed. Replacing the union by the sum in the second
inequality only weakens the bound and cannot invalidate it. Distinctness
is essential: the argument would fail for `c=d`, because then `c+d=0`.
Members of a binary basis are nonzero and distinct, so (1) applies to any
two of them.

## 4. A lower bound for every basis invoice

Sort the nine reader ranks of any basis into nondecreasing order. Denote
its first two ranks by `a<=b`. Its cost is at least `a+8b`, because the
remaining seven ranks are also at least `b`. Every such basis therefore
supplies integers satisfying

```
0 <= a <= b <= 8,
delta_a <= p, delta_b <= p,
M_a + M_b >= 84-p,
cost_of_this_basis >= a+8b.
```

Minimizing over all bases gives the universal bound

```
L(p) = min { a+8b : 0<=a<=b<=8,
                     delta_a<=p, delta_b<=p,
                     M_a+M_b>=84-p },
C_star(P) >= L(p).                                  (2)
```

This is a relaxation: the feasible integer pairs need not occur for any
puncture set, and the other seven readers are not asserted to attain rank
`b`. Exhausting these at most 45 integer pairs for each `p` gives:

| Deleted ports p | L(p) | One minimizing relaxed pair (a,b) |
|---|---:|---|
| 0 | 72 | (8,8) |
| 1 through 25 | 63 | (7,7) |
| 26 through 35 | 54 | (6,6) |
| 36 through 43 | 53 | (5,6) |
| 44 through 51 | 45 | (5,5) |
| 52 through 55 | 44 | (4,5) |

The compatibility effect is already visible at `p=36`: two rank-five
readers would jointly occupy at most `20+20=40` live ports, although their
support union must retain at least `84-36=48`. More generally, two readers
of rank at most five require at least 44 deletions. This uses shared
deletions and is distinct from the single-reader threshold of 36.

## 5. Ratio comparison and theorem

For `0<=p<=8`, use the inherited bound `72-p`, which is stronger than the
pair relaxation where needed. Cross multiplication gives

```
111(72-p) - 63(120-p) = 432-48p > 0.
```

For each later interval, its cost bound is constant and `120-p`
decreases, so the smallest guaranteed ratio occurs at the interval's
left endpoint. The exact comparisons are:

| p interval | Lower cost | Largest live-port count in interval | 111 times lower cost minus 63 times largest live count |
|---|---:|---:|---:|
| 9 through 25 | 63 | 111 | 0 |
| 26 through 35 | 54 | 94 | 72 |
| 36 through 43 | 53 | 84 | 591 |
| 44 through 51 | 45 | 76 | 207 |
| 52 through 55 | 44 | 68 | 600 |

All are nonnegative. Thus for every puncture set with `|P|<=55`,

```
C_star(P) / (120-|P|) >= 63/111 = 21/37.
```

PR631 supplies an attaining nine-puncture example with independent deleted
labels and cost 63 on 111 live ports. Accordingly `63/111` is the optimum
ratio over the whole stated domain, although the minimum star cost at most
individual puncture counts is not determined here. In particular the
relaxed lower costs 53, 45 and 44 are **not** claimed to be attainable.
PR875's exact equality-class invoice at 36 punctures gives stronger
information for that class; our cost 53 there is only a sufficient universal
bound.

## 6. Boundary, cost interpretation, and unresolved scope

At 56 deletions a minimum-weight codeword can disappear: choosing its
support as `P` gives a nontrivial kernel of restriction. Nine independent
live reader dimensions are no longer automatic. This proof stops at 55;
it neither asserts nor excludes an improved ratio after dimension loss.

The lower bound is on one necessary copy-cost component. Assigning zero
optimistic expense to helpers, source access, frame changes, restoration
and recursive children cannot overcome this component's ratio obstruction
within the fixed model. This is not a complete supplier invoice, and it
does not rule out improvements to other invoice terms at an unchanged or
worse copy ratio.

The result does not cover general pairing-rank decoders, non-label or
nonlinear readers, extra/non-root ports, correlated inputs, changed stage
geometry, or improvements in another supplier or assembly constraint.
It supplies no new circuit, supplier word, unconditional multiplication
bound, or value of kappa. The selected construction's inherited all-size,
compiler, hosting, analytic, precision and tape obligations remain outside
this note.

## 7. Provenance and attribution

The task base is `91a2094f2e022930069e8cfdc810a3ea1b81cd09`, recorded in
[CLAIM.json](CLAIM.json), with structural-decoder assignment seed 46. The
predecessor source pins are:

- Chi Zhao / [PR631](https://github.com/CrocSwap/integer-mult-bounds/pull/631),
  head `fb893b5ee1317c2da3b297e6fe78eca0857d1a76`: root/code model,
  parabolic-flat reduction, sharp single-reader thresholds, small-puncture
  identity and the at-most-35 ratio theorem.
- Philipp (@mightyOil) / [PR875](https://github.com/CrocSwap/integer-mult-bounds/pull/875),
  head `7f334e4c749fd83d03feb6c1de4e4cda9534c9dc`: first rank-five
  equality-class analysis and at-most-36 exclusion; its retained
  [README](sources/PR875-README.md) provides context, not a dependency of
  inequalities (1) and (2).
- Joel Pulikkan / GamingPuzzled / PR620: the star model, minimum-basis
  accounting and earlier puncture investigations. DreamingOfClouds /
  PR595 and PR602 supply format-limit context; eumemic / PR543 and the
  prior E8 supplier lineage supply construction context.

The new contribution is the common-deletion support-union inequality,
its combination with root-flat capacity and single-reader constraints,
and the resulting exclusion through 55 deletions. No claim of novelty
outside this repository is made. This proof was developed, challenged
and written with **substantial OpenAI Codex assistance**, including an
AI-assisted separate review of the argument; no independent human review
is claimed. The retained predecessor files keep their original attribution
and Apache-2.0 license; this contribution follows the repository license.
