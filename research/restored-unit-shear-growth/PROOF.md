# Sharp intermediate growth under exact restoration

This proof and its application were produced by Nick Petalas. Apache-2.0.

## Contract and theorem

Let n>=2 and L>=0 be integers. A gate on n rows is exactly

```
x_i <- x_i + epsilon x_j,       i != j, epsilon in {-1,1}.
```

All other rows stay fixed. A word has length ell<=L, and its complete
integer matrix is I_n. This is full restoration for every original input,
including every dirty workspace row. There is no scaling, self-addition,
native operator, rounding, source insertion or free operation.

Set F_0=0, F_1=1 and F_(a+2)=F_(a+1)+F_a. Let P_k be the prefix matrix
after k gates, with P_0=I. Write |P|_max for its largest absolute entry,
and ||P||_infinity for its largest absolute row sum.

**Theorem.** With d=min(k,ell-k), every cut satisfies

```
|P_k|_max       <= F_(d+1),
||P_k||_infinity <= F_(d+2).
```

Consequently, over all allowed words and all their cuts, the exact maxima are

```
max |P_k|_max        = F_(floor(L/2)+1),
max ||P_k||_infinity = F_(floor(L/2)+2).
```

Both maxima are attained by one word on two rows. Any additional rows stay
fixed, so allowing arbitrarily many dirty rows cannot increase the maxima.
These are maxima under an **at most L** budget. We do not assert an
identity word of every exact length, or sharpness at every specified cut.

## One-way growth lemma

First ignore the endpoint. For each row of a prefix matrix take its
absolute row sum, and sort these n nonnegative numbers. Let a>=b be
the two largest. Updating one row changes its norm to at most the sum
of the norms of two distinct old rows, hence at most a+b. The new
second largest norm is at most a, since only one row changes. Thus the
ordered pair of largest norms is componentwise bounded by

```
(a,b) -> (a+b,a).
```

Initially it is (1,1). Induction bounds it after t gates by
(F_(t+2),F_(t+1)), so ||P||_infinity<=F_(t+2). Decreases and sign
cancellations do not invalidate this upper bound.

Apply the same argument to the absolute values in one fixed column.
Initially the two largest are (1,0). They are bounded after t gates by
(F_(t+1),F_t). Each column therefore has largest entry at most F_(t+1),
which proves |P|_max<=F_(t+1). This argument applies separately to each
column and does not assume independent signs across columns.

## Use both sides of the cut

Write S_k for the matrix of the remaining ell-k gates, so S_k P_k=I.
Then P_k=S_k^-1. A gate's inverse is another allowed gate, with its
sign negated. Reversing the remaining gates and negating their signs
therefore writes the **same P_k** as a word of length ell-k.

The one-way lemma gives both bounds with t=k and with t=ell-k.
The Fibonacci numbers are nondecreasing, so taking the smaller gives
the two stated cut bounds. Since min(k,ell-k)<=floor(L/2), the global
bounds follow. No norm estimate on the final identity is substituted
for the inverse-word argument.

## Attainment and the magnitude guard

Put s=floor(L/2). Starting with two rows, alternate positive additions

```
x_0 += x_1, x_1 += x_0, x_0 += x_1, ...
```

for s gates. Execute their inverse gates in reverse order. The resulting
word has length 2s<=L and endpoint I. At its midpoint, its two row sums
are F_(s+2),F_(s+1), in one order. For s>=1 its largest entry is
F_(s+1), as follows by the same alternating recurrence in the two columns.
For s=0 the midpoint is I, with both maxima equal to one. This proves
attainment, simultaneously for both bounds.

If every original real or integer input satisfies |x_i|<=H, the triangle
inequality gives the uniform intermediate magnitude cap

```
|x_i(k)| <= H F_(floor(L/2)+2).
```

For H>=0, set both active initial rows equal to H in the attaining word.
The larger midpoint row attains this cap exactly. Arbitrary spectator
inputs remain unchanged. Hence the cap is the least possible universal
cap from L and H alone for n>=2. If H is a nonnegative integer and
M=H F_(floor(L/2)+2), the smallest two's-complement width sufficient for
every state is 1+bit_length(M), with bit_length(0)=0. The positive
attainer also proves necessity of this symmetric-range width.

This guard applies to exact row states. It does not bound the error of
rounded shears, local arithmetic temporaries with a different evaluation
order, coefficient preparation, tape movement, or native Gaussian gates.

## Verification boundary and relevance

The all-dimension and all-length assertions rest on the proof above.
The finite matrix census evaluates every signed unit ADD word through
length eight on two rows and length five on three rows. It tests each
identity word's individual cuts and reports their exact counts. The
separate oracle evaluates integer cube corners, without matrix operations
or imports from the model. Checking all corners determines identity and
the induced infinity norm over this characteristic-zero model, since
the corners span and each row's absolute sum is attained at a corner.
All words in the two declared oracle domains are enumerated too.

The proof isolates an exact restoration-aware precision input. A complete
selected caller contains operations outside this alphabet, so there is no
automatic replacement of its existing precision guard or scalar allowance.
No source word, predecessor theorem, native map or historical count is
replayed as the contribution. Independent human and formal proof-kernel
review, physical implementation and all five framework assumptions remain
unclaimed. No new kappa follows.
