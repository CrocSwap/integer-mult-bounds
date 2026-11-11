# Generalized support bound for selected BIT summary descents

Fix the paired #7001 native word, its rational chart catalogue and
its monotone source flow. The only new downward transports are
collectors descending to chart zero. A new collector can use
earlier descended values. Take its main-coordinate row modulo
the span of those earlier values and all retained summary rows.
Co-chart XOR, zero initialization and monotone transport preserve
support on the original lines contained in the current chart
in this quotient. Subtract earlier rows in chronological order
to obtain supported innovations without changing the span of
all rows available for recovery. Timing and recovery are otherwise
overgranted.

The nine literal summary rows projected onto 111 original main
coordinates generate a binary code C of dimension nine. Its
minimum nonzero weight is 48 and its minimum support union for
a two-dimensional subspace is 75. The 111 coordinate functionals
are distinct and nonzero on C. The replay verifies these facts
from the pinned word and checks all catalogue capacities and
2,862 public monotone MOVEs.

## Paid rank budget

Let k of the nine summary rows be replaced, at the target
κ=0.0040075385047236, and write p=1−κ. Require at least 5/3
net paid units per native copy. This is a relaxation of the
full target deficit per 36 repeated copies. The cost of the
k old descents is k·7^p. All catalogue ranks are at most eight.
For total new rank R, the cost is at least R·8^(−κ).
If R≥7k−1, the saving is at most
7^(−κ)+(7k−1)(7^(−κ)−8^(−κ)), which is at most
1+62κ/7 by the mean value theorem and log(8/7)≤1/7.
This is strictly below 5/3. Therefore R≤7k−2.

## Two support tests

Choose linear XOR recovery for the k independent summary
rows modulo the retained rows. Cancel the coefficients of
the k−t highest-rank collectors in those recovery equations.
At least t independent target combinations remain. Select
a t-dimensional subspace of their codeword representatives
in C. Every column outside the union of the remaining
collectors is zero in this subspace.

The support union must have size at least d_t, the minimum
support of a t-dimensional subspace of C. For t≥2,
averaging the two-dimensional subspaces gives the bound
ceil((2^t−1)·75/(3·2^(t−2))). Indeed, a nonzero coordinate
functional on a t-space occurs in a fraction
3·2^(t−2)/(2^t−1) of its two-dimensional subspaces.
Distinct nonzero columns also give d_t≥112−2^(9−t),
since the kernel of restriction to a t-space has dimension
9−t. Use the larger lower bound.

There is a second necessary condition on the sum I of
the remaining collectors' support sizes. A rank-t linear
map of the original nine-dimensional column space can
repeat an output column at most 2^(9−t) times. At least
112−2^(9−t) output columns are nonzero. With N remaining
collectors, each nonzero column incident to at most h
collectors is the sum of at most h of the N coefficient
vectors. There are at most sum(j=1..h, binomial(N,j))
possible subsets. Thus for each h≥0 the number of columns
incident to more than h collectors is at least

```text
max(0, 112−2^(9−t) − 2^(9−t)·sum(j=1..h, binomial(N,j))).
```

Summing these bounds over h bounds I below. The catalogue
capacities bound I above, even with overlapping charts
overcounted. This argument also permits a collector to
use only part of the support of its chart.

## Exact enumeration and pair test

Enumerate sorted rank histograms within R≤7k−2. Keep only
profiles whose tail after dropping k−1 collectors can
cover 48 lines. This precondition is necessary. The
enumeration exhausts 18, 74, 270 and 782 histograms for
k=6,7,8,9. The two support tests leave zero, zero, one and
three profiles, respectively.

The k=8 profile has nine rank-six transports. Two k=9
profiles have ten rank-six transports or one rank-seven
and nine rank-six transports. In each of these three
profiles there are k+1 transports. Cancel every transport
except a chosen pair of rank-six collectors. This imposes
k−1 homogeneous conditions on k target coefficients and
leaves a nonzero codeword supported in the union of that
pair. Equal masks cover at most 30 lines and fail immediately.
For every one of the 16,110 distinct pairs, the columns
outside that union have rank nine. Hence no nonzero
codeword can be supported in the pair and all three
profiles fail.

The nine-summary profile with ten rank-six collectors and
one rank-one collector remains open. The two-chart test
does not include its extra line. This proof also leaves
smaller paid savings, changed chart spaces, nonmonotone
transports, and new target contracts outside its exclusion.
