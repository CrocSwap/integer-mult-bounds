# Sharp source floor from five inventory summaries

This is a scoped written proof, produced by Nick Petalas. Apache-2.0.
It uses Ali Romman's all-height source telescope from
[PR #5318](https://github.com/CrocSwap/integer-mult-bounds/pull/5318) as a
premise. The binomial counting identity and monotone comparison are elementary;
no literature-wide priority for those methods is claimed.

## Contract and credited premise

Treat each productive or paid position as a separate token, including repeated
ranks. Let productive ranks have exact minimum L and maximum M, with
2 <= L < M. There are W productive tokens, exactly t of rank M, where
1 <= t < W. There are Q paid tokens, each with positive integer rank below L.
Assume Q >= W. For an integer cap c >= 1, let g be the unique nonnegative
integer satisfying L^g <= c < L^(g+1).

For d in 0,...,g, let F_d(c) count words consisting of d ordered paid tokens
and g-d ordered productive tokens whose rank product is at most c.
The paid and productive positions are distinguished. There is no factor
binomial(g,d) choosing their interleaving. The chronological source model
and its Pascal matching are exactly those of the credited predecessor.

Write D_d(c) = Q^d W^(g-d) - F_d(c). The predecessor proves

```text
S(c) = W^(g+1) + (Q-W) sum_(d=0,...,g-1) D_d(c).       (1)
```

This note neither replays that package nor claims a new source census.
The new question is the sharp lower envelope of (1) with only
L, M, W, Q, t fixed.

## Pointwise theorem

Define

```text
B_d(c) = Q^d sum_(k=0,...,g-d)
           binomial(g-d,k) t^k (W-t)^(g-d-k)
           [L^(g-d-k) M^k > c].

E(c) = W^(g+1) + (Q-W) sum_(d=0,...,g-1) B_d(c).       (2)
```

Square brackets denote an indicator. Then S(c) >= E(c). Moreover E(c)
is the exact minimum of S(c) over all inventories with these five summaries.
The empty sum gives E(c)=W when g=0.

To prove the inequality, preserve token identities and replace every
nonmaximum productive rank by L and every paid rank by 1. Preserve all t
maximum-rank tokens at M. Every word's rank product weakly decreases.
Consequently each word still above c after replacement was above c before
replacement, so D_d(c) >= B_d(c).

For the replaced word, choosing its k maximum-rank productive positions
and their identities gives precisely the summand in (2). All Q^d paid
token words have the same replaced rank 1, but remain distinct words.
Multiplying by the nonnegative Q-W in (1) proves the inequality.

The replaced inventory itself has the required exact minimum, maximum,
counts and separation. Its productive histogram is
{L: W-t, M: t}; its paid histogram is {1: Q}. Every preceding inequality
is equality for that inventory, proving sharpness. This is sharpness over
the summary-data class, not attainment by a native or physical compiler.

The sign condition matters. For example, take L=2, M=4, W=3, t=1, Q=1
and c=4. The collapsed inventory has 17 sources, whereas productive ranks
(2,3,4) and the same single rank-one paid token have 11. Thus (2) is not
a lower bound if Q<W. If Q=W, (1) makes every source count W^(g+1).

## Sharp bound throughout a height slab

Within a fixed height g, the indicators in (2) decrease as c increases.
Therefore the best uniform floor from these summaries on the entire slab
L^g <= c < L^(g+1) is E(L^(g+1)-1). This is attained by the collapsed
inventory at that integer cap. At the upper cap, the indicator is exactly

```text
L^(g-d-k) M^k >= L^(g+1).                             (3)
```

The distinction between >c and >=L^(g+1) is the integer boundary, not
a relaxation. In particular, rank product equal to c is eligible and
must not be charged as a deficit.

## Power-1024 application

The following are cited source facts from PR #5318 and the retained
[#4470 invoice](../joint-helper-lattice/RESULT.json), not results
reverified here. Under that unchanged historical product, completion and
split rule,

```text
v = 1024,
L = 21^v, M = 145^v, W = 10928^v, t = 224^v,
Q >= Q0 = 64620^v > W, and every paid rank is below L.
```

Exactly t maximum-rank tokens remain because a product of v productive
ranks equals 145^v precisely when every factor is one of the 224 rank-145
tokens. The completion floor is below this maximum. The inherited lower
bound Q>=Q0 includes the fact that each raw paid call yields at least one
positive split call; completion may add more.

The exact small integer comparisons are

```text
21 < 145 < 21^2,       145^2 > 21^3.
```

At g=1 and the slab's upper cap, even M is eligible, so the best uniform
summary-data floor remains W^2. At g=2, exactly the pair of maximum-rank
productive tokens is ineligible in the collapsed depth-zero word. A word
with only one maximum has product L M < L^3. At depth one, even M < L^3
is eligible. Equations (2) and (3) therefore give the exact summary minimum

```text
min_(L^2 <= c < L^3) S(c) = W^3 + (Q-W)t^2.           (4)
```

The minimum in (4) ranges over inventories with the declared summaries
as well as caps. For the actual historical inventory it is a lower bound,
not an asserted exact source count. Substituting Q>=Q0 gives the new
explicit correction

```text
S(c) >= 10928^(3072)
        + (64620^1024 - 10928^1024) * 224^2048
      > W^3.
```

More generally, for every g>=2 and every cap in its height slab, any
depth-zero word with at least two maximum-rank tokens is ineligible:
L^(g-k)M^k >= L^(g-2)M^2 > L^(g+1) > c for k>=2.
Counting just these words in (1) proves

```text
S(c) >= W^(g+1) + (Q0-W)
        * (W^g - (W-t)^g - g*t*(W-t)^(g-1))
      > W^(g+1).                                    (5)
```

Equation (2) can be stronger because it retains other depths and threshold
terms. Formula (5) is a simple explicit correction valid throughout every
height slab g>=2 of the actual power-1024 model. The all-height quantifier
is proved above; the executable does not enumerate its enormous heights.

## Scope

This improves a mathematical source-count lower bound for an unchanged
historical nested compiler. It supplies neither a higher accumulated K/N
coefficient nor a smaller compiler width. The selected #7000 construction,
kappa, physical stock, routing, ownership, native realization, precision/tape,
all-size admission and analytic recovery are unchanged. No complete
multiplication theorem or independent human or proof-kernel review is claimed.
