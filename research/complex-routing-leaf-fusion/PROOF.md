# A credited frame refit on the joint twelve-source recovery word

This construction composes Marius-Paul Dumitrean's one-gate refit from
[PR2733](https://github.com/CrocSwap/integer-mult-bounds/pull/2733), head
`a63c55ff56aaa8645d64d1162d1f017b59ded42a`, with Tekalign's joint twelve-source
recovery from [PR2751](https://github.com/CrocSwap/integer-mult-bounds/pull/2751),
head `4cfbb0cc8314d7fb4e8e754545a49a42eb590a69`. The refit is predecessor work;
the new result is its valid composition with the changed recovery word and
the resulting complete invoice. No new scalar identity or refit mechanism
is claimed.

The two source words do not contain this refit. Their unique gate
`393 += 515` is B1151, with zero-based indexing, in both providers. PR2733
performs the corresponding edit at B1149 in its different word. Matching a
register pair is not enough to justify composition: the proof below checks
the actual preceding and following frames in the PR2751 words. The local
symbolic checks also retain the changed source recoveries and dirty-input
corrections.

## Exact changed gate and its legal frames

Frames are binary subspaces of `F_2^9`, encoded by the listed integer vectors.
Their use in the native complex construction retains the predecessor's
common-label, realization and transport contracts. Let

```
P = span(407,66,36,9),                  dim P = 4,
N = span(259,148,66,36,9),              dim N = 5,
O = span(259,132,66,36,16,9),           dim O = 6.
```

At B1151 the current frame of register 393 is P and the current frame of
register 515 is N. The existing gate executes at O. Replace that gate by

```
['add',393,515,1,1,[259,148,66,36,9]].
```

Both operands can reach N: `407 = 259 xor 148` proves `P <= N`, and
`148 = 132 xor 16` gives `N < O`. Each operand's next touched frame has
dimension 7 and contains O. Explicitly they are

```
Q393 = span(256,132,65,36,16,9,3),
Q515 = span(259,128,66,32,16,9,4).
```

Consequently the smaller gate frame still lies between both preceding and
following frames. Every other gate frame, start frame, final frame, warp
entrance/exit, target level and centre frame is identical. This is a legal
monotone frame assignment under the inherited calculus. It does not cross
a warp or alter a private-buffer lifetime.

The scalar gate, coefficient and order are identical. Thus the formal
noncommuting-operator word is unchanged, including all source recoveries,
anticipatory dirty-input corrections and inverse cleanup. The physical
realization of a scalar operation at a legal common frame is an inherited
contract, not a consequence of binary subspace containment alone. The
independent replay checks the complete arbitrary-input maps in both forward
and dual orientations and checks all cleanup operations; native phase and
wrapper replay remains a separate evidence layer.

## Complete local and global paid change

Only the following two frame paths change:

| Register | Source path | Composed path | Paid ranks |
| --- | --- | --- | --- |
| 393 | 4 -> 6 -> 7 | 4 -> 5 -> 7 | `(2,1)` becomes `(1,2)` |
| 515 | 5 -> 6 -> 7 | 5 -> 5 -> 7 | `(1,1)` becomes `(0,2)` |

Zero-rank transitions require no child. Register 393's histogram is
unchanged, while register 515 replaces two rank-one children by one rank-two
child. The local change is therefore exactly `H2 - 2H1`, with unchanged
rank mass. Both providers have the new local profile

```
{1:2364, 2:647, 3:297, 4:120, 5:26, 8:8}.
```

There remain 415 helpers and 72 private buffers per local word. Entrances,
exits, residual widths and chronological owner lifetimes are unchanged.
The source allocation has 666 call equivalents, so the complete change is
`666*(H2-2H1)`. Retaining every source idle remainder gives

```
H = {1:1591740, 2:430902, 3:204396, 4:79920,
     5:22532, 8:5328, 32:1, 48:26558}.
```

Its rank mass is 4,816,512. The dimension remains 73, live stock 66,304 and
physical stock 66,801. All 276,390 owner-role reservations remain part of the
construction. Their reuse is justified by the unchanged allocation inputs
and residual interfaces, and checked by the independent owner replay. It is
not permission to drop hosting, stock or other invoice terms.

No scalar or adapter is added. The mathematical operation count changes
because a recursive frame transition is replaced, not because an additive
implementation constant is smaller. Native generation and the complete
finite invoice accept the changed transition and its phases; the recorded
full release checks this separately from the local proof.

## Strict moment improvement and certified endpoint

For saving `0<a<1`, the native complex moment is

```
M_H(a) = (1/66304) sum_r H_r (r/73)^(1-a).
```

The native exact-complex branch has no bad-class surcharge. This is the
same source contract as PR2751; it is not a new justification for removing
a surcharge. The complete difference from that source is

```
M_new(a)-M_source(a)
  = 666 * 73^(a-1)/66304 * (2^(1-a)-2) < 0.
```

The inequality is strict because `0<1-a<1`. The rank mass is unchanged,
so the moments agree at a=0; a rank-mass check alone cannot detect this
gain. Each rank satisfies r<73, hence the moment is strictly increasing
in a. A strict sign at each endpoint therefore certifies a unique root
between

```
L = 0.001717256973467002308270,
U = 0.001717256973467002308271.
```

`exact_moment_checker.py` supplies a separately implemented rational
enclosure without importing a producer or predecessor arithmetic module.
For x>=1 it writes x=2^k y with 1<=y<2 and uses

```
log(y) = 2 sum_(j>=0) z^(2j+1)/(2j+1),  z=(y-1)/(y+1).
```

After 36 terms the positive remainder is at most
`2 z^73/[73(1-z^2)]`. Scaling by k gives exact lower/upper logarithm
enclosures. The argument `a log(73/r)` is less than 1/100 in the checker
domain. Its exponential is bounded by the degree 20 Taylor polynomial
and the tail `next_term/(1-x/22)`. Positive weights preserve interval
orientation. All comparisons use rational arithmetic; fixed-point
dyadic rounding is only a compact outward representation of the resulting
slacks.

The checker proves `M_new(L)<1<M_new(U)`. It also proves the unchanged
source fails at L. Controls reject the unchanged source, the reversed
mass-preserving fusion, reversed endpoints, the upper endpoint presented
as an accepted lower endpoint and a changed live denominator. These are
finite pricing checks, not validation of native execution or an outer
multiplication theorem.

## Conditional outer target and scope

The admitted conditional target is the exact rational

```
kappa = L - 10^-46 - 10^-70.
```

This uses the inherited **modern outer** contract of PR2751 and its pinned
source chain. The corresponding complete release and ordinary-recurrence
witness were regenerated at the new endpoint and passed; strict native moment
acceptance by itself would be insufficient. See VALIDATION.md for exact
execution coverage and source-bound reuse. `CLAIM.json` records the target and
the current replay status. The retained bit supplier must remain
nonbinding, and every changed source/claim binding must be checked.

Relative to PR2751's reported conditional target, the certified increase is
approximately 1.15387118576e-7, or 0.00671972 percent. This is a small genuine
paid-profile improvement, not a large mechanism change. It is not a
measured running-time improvement.

The accepted selected record at this task's base still reports
`kappa=0.001672660197076918` under its own retained classical transfer and
supplier assumptions. The larger numerical difference from that accepted
record cannot be attributed to this one refit: it includes the predecessor
complex constructions and a changed inherited outer contract. This package
does not edit the selected frontier or promote pending source claims.

The all-size compiler, common-label/source-access realization, physical
hosting/routing, precision and fixed-tape contracts, exact recovery,
ordinary recursion, bit supplier and analytic transfer hypotheses remain.
In particular this finite complex transport fusion does not discharge the
separate all-size BIT routing/leaf H2 obligation. A faster implementation
of that already assumed BIT contract alone would not change the binding
complex paid moment.

The written proof gives the local frame implication and strict moment
comparison. Finite evidence gives exact words, complete finite invoices
and the explicitly recorded replay results. Neither is a proof-assistant
verification or an unconditional multiplication theorem.

## Attribution

Dumitrean supplied the one-gate refit; Tekalign supplied the joint twelve
source-recovery word and its independent symbolic, owner and moment
checkers. Mason Hale's concentrated assignments, Philippe Van Velzen's
pre-life hosting and earlier refits, Jeremy Kothe's invocation order and
allocation, and the source-partner/native/bit/outer lineage retain their
source notices. The exact atanh/Taylor method is standard and retains the
repository's prior interval-pricing attribution, including PR2751.

New composition and checks by David Arias with substantial OpenAI Codex
assistance, including separate mathematical and implementation agents.
Apache-2.0. No independent human review is claimed.
