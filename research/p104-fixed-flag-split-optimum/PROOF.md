# Exact split-gather optimum for eight fixed flags

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Result and contract

Fix the geometry, eight chain pairs and eight ordered flags in Nick Petalas's
[PR #7748](https://github.com/CrocSwap/integer-mult-bounds/pull/7748), at
`5ca92afebe8ed0208c9a1ffbee0424f98a9eff6e`. Use its one-read-per-chain model.
For every source column and active chain, allow arbitrary rational gather
pieces at legal levels. The pieces must sum to one on that chain. Count the
nonzero even off-diagonal entries of the complete 104-by-104 decoder.

**The exact minimum is 4,745.** With one gather per active chain, the minimum
on these same flags is 4,814. Signed splitting removes 69 entries across
44 improved columns. Source column 4 has minimum 43, compared with the
published split value 44 and the single-gather minimum 45.

The matching schedule has 490 nonzero gather pieces across 416 active
column-chain pairs. Every diagonal entry is 2 and all 5,720 odd off-diagonal
entries are zero. The piece count is the cost of this witness only; no
minimum piece count or physical cost optimum is claimed.

The fixed flags are essential. DreamingOfClouds's
[PR #7689](https://github.com/CrocSwap/integer-mult-bounds/pull/7689)
reports a 4,216-entry witness over other flags. That witness is not replayed
here. The present result does not improve the reported best global decoder,
its class ceiling, a complete supplier, or kappa.

## 1. Replace pieces by free prefix coefficients

Let tau_k(t) be the reader birth level and sigma_k(s) the gather deadline.
These are reconstructed from the pinned binary flags. Let w_k(s,t) be the
integer Gram weight in the source formula. If a_k,g is the gather piece at
level g, define

```text
c_k,j = sum_(0 <= g < j) a_k,g.
```

For an active chain and a fixed source s, legality and total coefficient one
are equivalent to

```text
c_k,0 = 0;
c_k,j is an arbitrary rational for 1 <= j <= sigma_k(s);
c_k,j = 1 for j > sigma_k(s).
```

In one direction, sum the legal pieces. In the other direction, recover
`a_k,g = c_k,g+1 - c_k,g` for `0 <= g <= sigma_k(s)`. These differences
have sum one and use only legal levels. There are at most eight levels.
Thus the free rational prefix variables describe the entire stated class;
there is no coefficient bound, denominator bound or finite-value search.
Variables that have zero weight at every reader can be omitted.

Each decoder entry is the affine rational form

```text
D_t,s = sum_k w_k(s,t) c_k,tau_k(t).
```

The verifier reconstructs this form for every one of the 10,816 entries.
All 104 diagonal forms are the constant 2. All 5,720 odd off-diagonal
forms are the constant zero. Thus these requirements impose no remaining
constraint on the free prefixes. Choices in different source columns
are independent within this formal decoder contract.

## 2. Certify the maximum number of zero forms

There are 48 even off-diagonal positions per source column. In total,
4,715 forms are constant and nonzero. They must remain in the junk set.
The other 277 positions depend on at most six variables per column.
Group forms whose zero equations are the same. Normalize each integer
row, including its constant term, by the greatest common divisor and
make its first nonzero entry positive. Its weight is the number of
positions represented by that equation.

For each column, let the distinct equations be `A_i x + b_i = 0`, with
weights `w_i`. There are at most eight distinct equations in any column.
The certificate gives 23 incompatible subsets across all columns. Each
has explicit integer coefficients lambda with

```text
sum_i lambda_i A_i = 0,
sum_i lambda_i b_i != 0.
```

Such a subset cannot consist entirely of zero entries, over Q or over R.
Enumerate the subsets of equations that contain no certified incompatible
subset, and find their maximum total weight. Every actual zero set is
among these subsets, so this yields an upper bound on zero entries.
Subtract it from the number of variable entries to get a lower bound on
nonzeros. It is enough that the listed contradictions are sound; the
matching schedule below proves that the bound is sharp.

For a separate check, rational Gaussian elimination tests consistency of
all subsets directly, without the contradiction list. Its feasible subsets
agree exactly with the contradiction test. There are only 1,400 subsets
across all 104 columns, including each empty subset.

The only columns with a positive additional penalty are:

| Source column | Extra nonzeros beyond its fixed entries |
| --- | ---: |
| 4 | 3 |
| 13 | 1 |
| 18 | 1 |
| 38 | 1 |
| 41 | 2 |
| 49 | 1 |
| 53 | 1 |
| 59 | 1 |
| 65 | 4 |
| 69 | 1 |
| 72 | 2 |
| 82 | 7 |
| 83 | 1 |
| 84 | 1 |
| 88 | 2 |
| 92 | 1 |

Their sum is 30. Hence the complete decoder has at least
`4715 + 30 = 4745` junk entries. `RESULT.json` gives each column's
variables, normalized equations, weights, contradiction coefficients,
minimum, attaining prefix values and legal gather pieces.

## 3. Matching schedule and single-gather comparison

The certificate supplies a rational point for each column. Convert it to
gather pieces by the difference formula in Section 1. Both the unchanged
source routine and a separate direct sum over individual pieces produce
the same complete decoder. Its affine forms also give the same entries.
The schedule has exactly the lower-bound number in every column, so the
sum 4,745 is attained.

The verifier separately enumerates all legal single-gather schedules in
each column. There are 1,242 schedules in total across the independent
column problems. Their minima sum to 4,814. This is not enumeration of the
Cartesian product of all column schedules; independence makes that product
unnecessary. Exactly 44 columns improve with splitting.

Column 4 gives a small example that can be checked without the full table.
Write `x2,x3,x4` for the chain-3 prefixes at levels 2,3,4, and `y1` for
the chain-6 prefix at level 1. There are 40 fixed nonzeros. The other
zero equations and their weights are

```text
y1 = 2       weight 1
x4 = 2       weight 2
x4 = 0       weight 2
x3 = 2       weight 1
x3 = 0       weight 1
x2 = 2       weight 1.
```

At least two positions survive the contradictory x4 pair and at least one
survives the x3 pair. Set all four variables to 2. This gives 43 nonzeros.
An attaining gather schedule is

```text
chain 0: (level 0, +1)
chain 2: (level 0, +1)
chain 3: (level 1, +2), (level 4, -1)
chain 5: (level 0, +1)
chain 6: (level 0, +2), (level 1, -1).
```

The unobserved chain-3 prefix at level 1 is zero in this witness. Moving its
first piece from level 1 to level 0 has no effect on the weighted readers.
The chain-6 split removes one more entry than the predecessor's 44-entry
schedule. Replacing `y1=2` by `y1=1` restores that entry and gives 44.

## Verification and limits

The six retained source files have exact Git blob and SHA-256 pins. The
source geometry reconstructs the Gram matrix from eight basis profiles,
checks binary label parity, and authenticates the original 104-port matrix
and label hashes. The unchanged source verifier also runs in each mode.

The new checker verifies all affine forms, the 23 integer contradictions,
all 1,400 subsets by two methods, every matching schedule, and all 1,242
single-gather schedules. Four additional rational prefix families give
416 full column checks, including negative and nonintegral coefficients.
Controls reject a false contradiction, a lost optimum, a late gather and
a wrong total. Removing a necessary contradiction lowers the claimed
bound, as expected.

All data and arithmetic are exact. The proof and finite certificate are
open to independent review; no human or formal proof-kernel acceptance is
claimed. The full PR7689 Lean and global flag suites, selected cold replay
and Docker were not run. More flag choices, split reads, other row models,
native realization, transport, storage, restoration and the complete paid
caller invoice remain open. All five selected framework assumptions remain.
