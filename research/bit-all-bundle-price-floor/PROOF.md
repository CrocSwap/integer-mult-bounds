# Every fixed-library direct bundle retains the original BIT price

For the selected PR7001 native word, an arbitrary finite bundle of direct
nested deliveries cannot reduce the price of any original paid arrival.
The claim holds in both orientations, for every tariff `rank^t` with
`0<t<=1`. The original single delivery attains the floor. This is a
scoped finite-word theorem, supported by exact replay. It is not a
universal obstruction to changed BIT networks and gives no new kappa.

## 1. Fixed contract

Keep all 659 public inputs independent. For each original MOVE, keep its
destination chart, event deadline and required binary row. At a chart `b`,
grant the span `V_b` of its entrance rows and its original paid arrivals
strictly before that deadline. Grant retention and scalar XOR formation
for free. A direct delivery sends one row of `V_b` to the destination `d`
and pays `s_b^t`, where `s_b` is the positive dimension difference. The
two chart subspaces must be nested over the rationals. Grant `V_d` for free.

The source library is complete for this model: INIT creates zero, a
cocharted ADD stays in the span, SWAP carries a row with its chart, CLEAR
removes a row, and MOVE adds a row to one chart at later deadlines. This
is the fixed-library contract of Ali Romman's PR7723. Nick Petalas's
PR7739 permits a sum of direct deliveries and proves the one- and two-donor
floor. The new result closes its nine remaining higher-arity cases.

Repeated deliveries from one chart can be combined into one row there.
The combined row has the same delivery rank and no greater price. Thus
any feasible finite bundle reduces to distinct nonempty donors. The proof
below even grants repeated donors when it bounds support, so this reduction
is not needed for that upper bound.

## 2. Strict saving requires smaller total rank

If the original arrival rank is `r`, and a bundle has positive ranks
`s_1,...,s_k` with sum `R`, then

```text
sum_i s_i^t = R^t sum_i (s_i/R)^t >= R^t,    0<t<=1.
```

Each fraction lies in `[0,1]`, so its t-th power is at least itself.
Thus a strictly cheaper bundle must have `R<r`. Every donor in such a
bundle is individually lower rank. A target outside the sum of all those
donor libraries and `V_d` cannot be supplied by any cheaper bundle.

The unchanged PR7739 checker reconstructs all original libraries and
checks this full sum at all 5,742 arrivals. It excludes 5,733. Its nine
exceptions are forward arrivals into chart 0, from charts 510 through
518, at events `26861+8i`, `0<=i<9`. Each has old rank seven. The complete
donor sum contains these targets, but that sum ignores total rank.

We rerun the predecessor's exact source and all its pair checks. We do not
claim its 5,733 exclusions or its pair enumeration as new results.

## 3. Keep one quotient for all nine deadlines

Let `V_0` be the chart-0 library strictly before event 26861. Its dimension
is 524. Ordered binary elimination defines a linear projection `Q` from
the 659 independent-input coordinates to a systematic 135-dimensional
quotient. It clears each pivot in descending order. Its kernel is exactly
`V_0`: it kills that basis, leaves every nonpivot unit coordinate free,
and its rank is 135.

Use this same projection at all nine deadlines. A quotient rebuilt after
each arrival can turn one-coordinate donor rows into dense representatives;
that would lose the support bound needed here. This proof instead leaves
the later free destination rows explicit.

Write `g_i` for the projected target at event `26861+8i`. At deadline `i`,
the free destination library in this fixed quotient is

```text
F_i = span(g_0,...,g_(i-1)).
```

Exact replay checks this equality, including dimension `i`, and checks
that the current target is not inserted early. Each of the 514 eligible
lower-rank donor libraries is unchanged over the nine deadlines. The
checker compares all eight later snapshots with the first, for 4,112
library equality checks. Other intervening arrivals go to charts outside
this eligible set. The proof uses the checked equality, not that observation
as an unverified shortcut.

## 4. Every cheap bundle has support at most 30

For each eligible chart `b`, take the union of the supports of a basis
of `Q(V_b)`. Every row in that space has support within this union.
Cancellation cannot introduce a new coordinate. The exact inventory is
in [RESULT.json](RESULT.json), including every chart, rank, image dimension,
support mask and support size.

| Delivery rank | Eligible charts | Largest support union |
|---|---:|---:|
| 1 | 111 | 1 |
| 2 | 153 | 2 |
| 4 | 70 | 17 |
| 6 | 180 | 30 |

These are all nonempty eligible charts. No other positive rank below seven
occurs. A sum of delivered rows has Hamming weight at most the sum of their
support-union sizes. With total rank at most six:

- A rank-six donor uses the whole budget and has support at most 30.
- A rank-four donor leaves rank budget at most two. The remaining donors
  have support at most two, so the total is at most 19.
- Without a rank-four or rank-six donor, support is at most total rank,
  hence at most six.

Thus 30 is a valid upper bound, without an arity limit. A dynamic-program
relaxation that permits unlimited donors checks the same statement. Its
bounds at budgets zero through six are `0,1,2,3,17,18,30`. The value 30
is not claimed as the exact attainable weight or price for the target.

## 5. The target cosets stay at distance at least 48

A bundle reconstructs `g_i` with free destination XOR only if its sum is
in the coset `g_i+F_i`. Enumerate all `2^i` members of this coset. This is
only 511 exact vectors across the nine deadlines.

| Event | Free dimension | Coset vectors | Minimum Hamming weight |
|---|---:|---:|---:|
| 26861 | 0 | 1 | 56 |
| 26869 | 1 | 2 | 58 |
| 26877 | 2 | 4 | 52 |
| 26885 | 3 | 8 | 50 |
| 26893 | 4 | 16 | 51 |
| 26901 | 5 | 32 | 50 |
| 26909 | 6 | 64 | 50 |
| 26917 | 7 | 128 | 48 |
| 26925 | 8 | 256 | 48 |

The receipt gives each projected target, the full weight histogram and a
selector attaining the reported minimum. Every minimum exceeds 30.
Consequently, no bundle of total rank at most six can supply any exception.
This is an exact finite certificate, not a random search or a bound on
one, two or three donors only.

Together with Section 2 and the 5,733 inherited exclusions, this proves
the price floor at all 5,742 arrivals. The separate set-based interpreter
also checks that the original row belongs to its original source library
and that the original pair is nested, at every deadline in both orientations.
Thus the old rank tariff is attained, not merely a lower bound for an
empty feasible set.

## 6. Consequence, evidence and limits

With productive targets and all other caller charges fixed, replacing
original arrivals by these bundles cannot improve the paid moment for
`0<t<=1`. The compatible signed-margin gain is at most zero, attained
by the original deliveries. Additional nonnegative formation, storage or
restoration charges preserve the exclusion. This closes the arbitrary-arity
question for the stated fixed libraries; another subset-size census cannot
improve the conclusion.

The new interpreter represents rows as coordinate sets. It agrees with
the retained packed-integer interpreter on every paid row in both directions.
The rational nesting computation and full-donor reduction are called from
the unchanged predecessor; they are shared code, not independent checks.
All eight retained files have exact byte pins. Four reduced support-cap
mutants fail. Inserting each current target into its own free library makes
the separation check fail. Strict-budget and binary-sum controls also run.

The result does not permit new charts, intermediate relays, adaptive changes
to the libraries, helper promises, changed target rows or deadlines, or
matrix-valued reconstruction. A relay can change the available information
and needs a new charged contract. No physical construction for free storage
or formation is supplied. The selected cold replay, other predecessor full
suites, Lean and Docker were not run. No independent human or formal-kernel
acceptance is claimed. All five framework assumptions remain, and no new
kappa or selected-frontier change follows.
