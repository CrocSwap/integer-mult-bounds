# Exact call minima under a ternary scratch budget

This is a finite cost audit of the dirty echo from PR673. It extends the
balanced-tree class in Dillon Amburgey's PR689. The echo identity and rounded
leaf are predecessor work. No new multiplication exponent is claimed.

## The admitted class

A leaf is one factor shear and costs one leaf call. Factors retain their given
order. An internal node with at least three factors splits its interval into
three nonempty consecutive intervals, of any sizes. A two-factor node has two
leaf children. No other binary node, unary node, alternate fanout, unequal leaf
price, or cross-call storage sharing is allowed.

A ternary node uses two dirty arrays while its child runs. A two-factor node
uses one. Each child has a separate deeper pool, reused only after the child
restores it. The simultaneous borrowed-array count is therefore

```
S(leaf) = 0,
S(two leaves) = 1,
S(A,B,C) = 2 + max(S(A),S(B),S(C)).
```

Source and target are distinct arrays outside that budget. The original echo
calls `A` and `C` twice and `B` four times. Its complete leaf bill is

```
C(leaf) = 1,
C(two leaves) = 4,
C(A,B,C) = 2 C(A) + 4 C(B) + 2 C(C).
```

These counts include both ladders, both inverse ladders and both target calls.
No child, copy, restoration pass or extra data array is omitted.

## Optimality recurrence

Let `F_s(n)` be the least complete leaf count among admitted trees with `n`
factors and at most `s` borrowed arrays. Use infinity when no tree exists.
For every `s >= 0`, `F_s(1)=1`. Also `F_s(2)=4` exactly when `s>=1`.
For `n>=3`, no tree exists when `s<2`. Otherwise

```
F_s(n) = min_{a,b,c >= 1; a+b+c=n}
         [2 F_(s-2)(a) + 4 F_(s-2)(b) + 2 F_(s-2)(c)].
```

Every admitted tree has one such root split. Every child must fit the remaining
budget. Replacing a child by a cheaper tree with the same factor count and
budget preserves the ordered product and cannot increase the other costs.
Conversely, three minimizing child witnesses form a valid parent. Induction
on `s` proves both the lower bound and attainability of every finite value.

The implementation first computes

```
P_s(m) = min_{a+b=m} [2 F_(s-2)(a) + 4 F_(s-2)(b)],
F_s(n) = min_{m+c=n} [P_s(m) + 2 F_(s-2)(c)].
```

This is the same finite minimum with the first two terms grouped. It does not
relax an integrality, order or storage constraint. Lexicographic tie breaking
chooses a reproducible witness. `None` represents infeasibility; there is no
finite sentinel that can hide a large valid cost.

The independent checker uses the ungrouped triple formula. A second check
enumerates every ordered tree through 14 factors, without optimizing intermediate
states. It compares the minimum at every tested scratch budget.

## Capacity boundary

The maximum admitted factor count at budget `s` is

```
M_(2d) = 3^d,
M_(2d+1) = 2*3^d.
```

The base capacities are one and two. A ternary root has capacity
`3 M_(s-2)`, reached by three maximum-capacity children. Every integer count
from three through this capacity can be split into three positive counts at
most `M_(s-2)`. Induction proves feasibility for every count up to capacity,
and impossibility above it, within this exact tree class.

At maximum capacity, every child must also have maximum capacity. Thus the
complete tree and its cost are forced recursively. At `s=10`, `n=243`, the
minimum is `8^5=32768`. Extra computation cannot improve this fixed-space case
within the admitted class.

## Concrete witnesses

PR689's balanced optimum for 127 factors is 8,800 calls with nine borrowed
arrays. The unrestricted interval sizes admitted here give 7,488 calls at
the same nine-array budget. One minimizing root split is `(47,33,47)`.
The saving is `1312/8800 = 41/275`, about 14.91% of the leaf calls.

At 71 factors and eight arrays, `(25,20,26)` gives 2,688 calls, compared with
the balanced minimum of 2,944. At 127 factors with ten arrays, a witness with
root split `(44,29,54)` takes 6,784 calls. This last comparison spends an extra
array; it is not a saving at unchanged storage. Complete nested trees are in
`CERTIFICATE.json` and can be rebuilt from the table.

The completed domain is `1<=n<=243`, `0<=s<=10`: 2,673 states, of which 606
are feasible. This is not a lower bound for other dirty algorithms or for
integer multiplication.

Concurrent PR730 permits general binary nodes as well. Its broader class can
give smaller values: 464 calls at 27 factors and six arrays, where this class
has the forced value 512. The minimum proved here applies only to the stated
ternary class. PR730 is credited in README.md.

## Identity, restoration and precision

Every split uses consecutive intervals. The child maps therefore compose to
the original ordered product, even when the factors do not commute. PR673's
echo identity applies at every node. Induction proves the ideal target map.

For rounded leaves, retain the predecessor's operational contract. A child
adds a deterministic function of its source and deeper initial dirt to the
target. The increment does not depend on the target. The child restores its
source and deeper dirt and has an exact inverse formed by reversing its full
word and its signs. Phase and coefficient inputs must remain fixed. The echo
uses no ancestor array in the deeper pool. Its inverse calls therefore restore
every borrowed array exactly. This argument does not require balanced sizes.

Rounded target values may differ between schedules. Exact restoration does
not imply that the rounded target increment is independent of initial dirt.
The complete inherited error bound remains necessary. Write `N=F_s(n)`,
`n=r-1`, `u=2^-w`, `a=13(r+1)/beta^3`, and `G=2+r/beta`. Under the same leaf
hypotheses and initial joint norm bound `D`, with `a*u<=1` and `u<=beta^2/2`,
the complete executed word has error at most

```
N a (D+1) u G^(N-1).
```

One sufficient execution budget for `p` requested bits is

```
w >= p+1+ceil(log2(N a (D+1)))+(N-1)ceil(log2 G),
```

together with both leaf precision constraints. Factor and phase preparation
retain their separate error allowance. The tests use the actual pinned leaf
and a dense exact inverse; they do not equate the old and new rounded outputs.

## Complete cost and scope

The finite planner takes `O(s n^2)` arithmetic operations and `O(s n)` table
entries. Costs have `O(s)` bits; counters also need `O(log n)` bits. Witness
storage uses `O(n)` scalar tree records. This cost is paid, not treated as free
online work. The source instruction generator additionally permits an
`O(s N)` scalar scheduling allowance. Its stack and active node records are
bounded by the tree depth, and it streams the word.

There are exactly `N` inherited leaves and three length-`L` scans per leaf.
Thus leaf execution pays `3 L N` scalar scan steps, with the inherited arithmetic,
source/phase access, coefficient preparation, scalar workspace and routing costs.
The full inherited precision estimate is used for every undo call as well.
Borrowed data storage is `s` length-`L` arrays in addition to source and target.
No clearing or uncharged copying of dirty arrays is permitted.

The planner's polynomial cost can dominate in an all-size application. No new
asymptotic exponent follows from a finite call-count reduction. The later PR673
integration has a separate unfavorable supplier bill; this audit neither
changes that adapter nor claims to overcome it. No new common-label supplier,
bit-reversible compiler, transform layout, physical hosting plan, full-transform
composition, tape bound, or analytic transfer is supplied.

## Credit and proof status

The DP recurrence and finite space audit were prepared by Ali Romman with
substantial OpenAI Codex assistance. Credit androolloyd's PR673 for the echo,
Dillon Amburgey's PR689 for the balanced ternary minimum and independent evidence,
and Chafik Boukhalfa's PR628 for rounded leaves and dirty composition. PR663
independently audits the binary count. Retained notices credit the complete
cyclic-kernel and analytic lineage. Apache-2.0.

The induction above is a written mathematical argument. Finite replay is not
a proof-assistant formalization or a proof of the multiplication theorem.
No independent human review or literature-priority claim is made.
