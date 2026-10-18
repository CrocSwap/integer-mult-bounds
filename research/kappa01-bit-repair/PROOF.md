# A target-scale obstruction for compressed-window bit suppliers

This is a necessary-condition theorem about the named model below. It does
not exclude arbitrary bit circuits, other address operators, different
recursive interfaces, or a different multiplication reduction. It supplies no
new bit supplier and changes no selected result.

## Source and hypotheses

The source is `research/format-limits/README.md`, section A.1, especially
(P), (Dfc), (Win), (Sch), and (Bat), at repository commit
`997e6a9ca7b4f95d50e366f61412fd640d72a88a`. Its general-rank extension is
explicitly labelled **argued**, and its numerical checks use rank-one labels.
We prove the result below directly from stated accounting hypotheses; we do
not promote that extension to an independently established supplier theorem.
The selected rank-one bit geometry is independently described in
`research/bit589-projector-ledger/README.md` and
`research/bit-revision3-levers-seed03/README.md`.

Let `s=2K+1>=3` be odd, let `v>0` count ports, let a port label have rank `k`,
and let the local ambient width be `h>k>0`. Put

```
d = h-k,           m = k+s*d.
```

Here `d` is an active frame climb, not the primitive exponent saving. Assume:

1. **Coverage:** for `W` roles, the total paid child rank mass `R` has deficit
   `D=mW-R <= (s-1)*v*k-s*C`, where `C>=0` is the per-invocation copy rank
   charge. For the first obstruction it is enough to take `C=0`.
2. **Active data:** the `s` stages force `2*s*v` active data climbs, each
   of rank `d`. All their rank mass is paid by children of rank at most `d`.
   A child cannot discharge several such frame changes with one uncharged
   combination. This is the relevant single-frame-change (Bat) hypothesis.
3. **Other charges:** every other child has rank at most `m`, and all
   surcharges are nonnegative. Children of rank exactly `m` are granted
   freely as a relaxation of the usual strict recursive shrinkage limit.

No helper lower bound, copy lower bound, chronological hosting restriction,
idle-rank bound below `m`, or supplier precision cost is used. These costs can
only worsen the following necessary conditions. The theorem remains scoped
to the coverage and active-data laws; a construction that changes those laws
is outside it.

At exponent saving `q=1/9`, define the rank pressure

```
P = sum_children r*((m/r)^q-1).
```

The normalized moment is `(R+P)/(mW)`. A necessary condition for strict
admission is therefore `P<D`. The active data alone give

```
P >= 2*s*v*d*((m/d)^q-1).
```

Writing `t=d/k`, and dividing by `v*k`, gives the necessary inequality

```
2*s*t*((s+1/t)^(1/9)-1) < s-1.                 (1)
```

## Every stage count at least five fails if h/k is at least three

For fixed `s>1`, the function

```
f(t)=t*((s+1/t)^q-1)
```

is strictly increasing for `t>0`. To check this, set `x=s+1/t>s`.
Its derivative in `t` is

```
(1-q)*x^q + q*s*x^(q-1) - 1.
```

As a function of `x`, the displayed expression has derivative
`q*(1-q)*x^(q-2)*(x-s)>0`; its value at `x=s` is `s^q-1>0`.

Now suppose `h/k>=3`, equivalently `t>=2`.

* For `s=5`, the left side of (1) is at least
  `20*((11/2)^(1/9)-1)>4`. The strict comparison is the integer inequality
  `2*6^9 < 11*5^9`.
* For `s=7`, it is greater than `28*(7^(1/9)-1)>6`.
  The strict comparison is `17^9 < 7*14^9`.
* For every `s>=9`, it is greater than
  `4*s*(9^(1/9)-1)>s>s-1`.
  The strict comparison is `5^9 < 9*4^9`.

These cases include every odd `s>=5`, and contradict (1). This is an analytic
all-stage proof with three finite integer comparisons, not a stage-count
search.

## The exact three-stage density threshold

When `s=3`, (1) is equivalent to

```
3*((h-k)/(3*h-2*k))^(8/9) < 1.                (2)
```

The left side is also the ideal normalized bill for two banks with no helper
or copy charge. Solving (2) gives

```
h/k < 1 + 1/(3^(9/8)-3) = 3.264451365238...,
k/h > (3^(9/8)-3)/(3^(9/8)-2) = 0.306330187868....
```

Because the width-ratio boundary is greater than three, the preceding
all-stage theorem applies to every `s>=5` at and above that boundary.
Consequently **every odd stage count fails whenever
`h/k >= 1+1/(3^(9/8)-3)`**. Equivalently, an admitted construction in this
model at `q=1/9` must have label density `k/h>0.306330187868...`.
Equality does not pass the strict moment test.

For a simpler exact corollary, every geometry with `h/k>=4` fails. Its
three-stage bill is at least `3*(3/10)^(8/9)>1`, witnessed by
`3^17>10^8`. Thus the bit E8 line geometry `(h,k)=(8,1)` and its hypothetical
rank-two geometry `(8,2)` both fail in this model even with all helpers and
centre charges removed.

## What a three-stage repair would still have to pay

Suppose the geometry clears the density test. Grant every unit of copy rank
mass a child of the maximum local rank `h`, with every other non-data expense
zero. The copy pressure is at least
`3*C*((m/h)^(1/9)-1)`, while coverage loses `3*C`. Hence strict admission
requires

```
C/(v*k) <
[2-6*((h-k)/k)*((m/(h-k))^(1/9)-1)] /
[3*(m/h)^(1/9)],                 m=3*h-2*k.   (3)
```

This uses the copy-rank cap `h` in (Bat), in addition to the earlier
hypotheses. It is a necessary allowance, not an attained copy price.

| h | k | k/h | Ideal data bill | Strict copy-rank allowance C/(v*k) |
|---:|---:|---:|---:|---:|
| 8 | 1 | 1/8 | 1.084063962275 | none; data already fail |
| 8 | 2 | 1/4 | 1.028821775684 | none; data already fail |
| 3 | 1 | 1/3 | 0.985156473147 | <0.063046005269 |
| 8 | 3 | 3/8 | 0.960793691650 | <0.143312658260 |
| 5 | 2 | 2/5 | 0.945249921321 | <0.183911638463 |
| 8 | 4 | 1/2 | 0.874896779682 | <0.308879754981 |

Thus even the density-one-third candidate needs a complete decoder with copy
rank per port below 6.31% of the label rank, before helpers, framing,
restoration, hosting and any other local expense. No such decoder is supplied
here. Density-one-third is a geometrically meaningful target that survives
this relaxed arithmetic, but is far from sufficient.

## The rank-one positive-definite three-dimensional attempt fails

There is a stronger obstruction for one concrete surviving geometry. Suppose
`h=3,k=1`, the label form is positive definite, and decoding is a sum of binary
scalar outer products. Require the resulting fitting matrix to have diagonal
one and to vanish off the diagonal unless the two port lines are orthogonal.
Price a term by the rational rank of the pairing between the spans of its
reader lines and source lines. This is a label-decoder restriction, not a
restriction on every possible bit circuit.

Any finite collection of lines in a positive-definite real three-dimensional
space has a pairwise nonorthogonal subset of size at least `v/4`. To see this,
identify the form with the standard dot product and choose a generic rotation
so every coordinate of every representative is nonzero. Orient each line so
its first coordinate is positive. There are four sign choices for the other
two coordinates. Two representatives of the same sign choice have positive
dot product. One class has at least `ceil(v/4)` members.

Restrict the fitting matrix to such a subset `S`; it is `I_S` over `F2`.
Every scalar outer product has restricted binary rank at most one. If a term
has zero pairing-rank cost, it is identically zero on `S x S`: any nonzero
restricted entry would exhibit a nonzero pairing between two lines in `S`.
Thus each nonzero restricted term costs at least one, and rank subadditivity
gives total copy charge `C>=|S|>=v/4`.

This contradicts the necessary allowance `C/v<0.063046005269...` from (3).
Hence the positive-definite three-dimensional rank-one **label-decoder**
attempt cannot repair the target even with all other local costs waived.
The elementary upper bound `0.063046005269...<1/4` is checked in the receipt.
Indefinite label forms, arbitrary non-label circuits, and general rank-k
subspace systems are outside this argument.

## Tensor and aggregation boundaries

A uniform direct-sum lift `(h,k)->(d*h,d*k)` preserves the ratios in (1)--(3).
Tensoring with an identity of dimension `d` has this same scaling. It cannot
turn a failing rank-density screen into a passing one.

A literal tensor power of the port subspace in its ambient space has density
`(k/h)^d`, which decreases for `h>k` and `d>1`. It also fails to provide the
needed density gain by itself. These statements do not cover a redesigned
subspace embedding, a new coverage law, or a global operator decomposition
that changes the active-climb obligation.

The active-child cap is substantive: if the rank mass of the three-stage E8
line example is arbitrarily repacked into rank-`m` children, its fractional
bill becomes `3*(h-k)/m=21/22<1`. This is an intentional scope control. Such
repacking violates the stated active-climb cap and is not a physical word.
The present theorem therefore identifies a hypothesis a block construction
must change; it does not rule out that construction universally.

Finally, passing `q=1/9` only leaves a possible strict neighborhood. The
retained outer transfer needs positive margin beyond the boundary to claim
`kappa=1/10` with all finite transfer losses. This package establishes no
outer-transfer margin or multiplication theorem.
