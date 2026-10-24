# A Fibonacci support bound for two output banks

## Exact model

Let K be a field and let m>=2 banks each contain N coordinates. All mN
initial coordinates are independent variables. In particular, extra banks
contain arbitrary dirty data. A program is a finite composition of these gates:

1. A monomial map within one bank, and a permutation of whole banks. These
   may be arbitrary and may depend on N. We grant them zero cost in the bound.
2. A charged ADD scan `x_i <- x_i + c M x_j`, with i distinct from j, c in K
   and M monomial. It changes only bank i. Let S count these gates.
3. A unary gate `x_i <- U x_i`, where every row of U has at most `2^r`
   nonzero entries, for an assigned nonnegative integer r. Let R be the sum
   of these assigned exponents. Unary native gates are covered when their
   actual row supports satisfy this hypothesis.

Monomial means a permutation times an invertible diagonal matrix. Each gate
acts on the full bank volume. Invertibility of the unary gates is unnecessary
for the lower bound, although reversible applications require it. General
free bank GL, additions with source and destination in the same bank,
multi-bank native gates and partial-volume operations are outside this model.
An ADD with several summands must count each separate scan.

For each bank i, let sigma_i be the maximum number of nonzero coefficients
in any scalar row of its current linear map from all initial coordinates.
Write A and B for the largest and second largest sigma_i, counting banks
with multiplicity. Thus two equally large banks give A=B. Initially A=B=1.
Zero rows are permitted later. Define F_0=0, F_1=1 and F_(k+2)=F_(k+1)+F_k.

## Theorem

At every program cut,

```
A <= 2^R F_(S+2),          B <= 2^R F_(S+1).                 (1)
```

Consequently, if each of two distinct required output banks has a row with
at least D nonzero old-input coefficients, every implementation satisfies

```
2^R F_(S+1) >= D.                                           (2)
```

This holds for every finite m. Restoring arbitrary dirty helpers only adds
endpoint requirements, so cannot invalidate the necessary inequality.
The count S is a serial gate count, not a parallel depth or a count of
traversals that fuse several ADDs.

## Proof

A monomial map only reorders and rescales scalar rows, so preserves sigma_i.
A bank permutation preserves the sorted support profile.

Consider one ADD with distinct banks i,j. Each new row of bank i is the sum
of one old row of i and one scaled old row of j. Cancellations can only
decrease support. Thus sigma_i' <= sigma_i+sigma_j <= A+B. All other bank
support sizes are unchanged. After changing one bank, the second largest
size is at most A, regardless of whether the changed bank becomes largest.
Therefore

```
A' <= A+B,                 B' <= A.
```

If (1) holds before this gate, the Fibonacci recurrence proves it afterwards
with S replaced by S+1 and R unchanged.

A unary gate of exponent r replaces each scalar row by a linear combination
of at most 2^r old rows of its own bank. Its support size grows by at most
2^r. Every bank's size is therefore bounded by 2^r times its previous size,
including the unchanged banks. Sorting preserves componentwise inequalities,
so A'<=2^r A and B'<=2^r B. This proves (1) after replacing R by R+r.
The initial profile satisfies (1) with S=R=0. Induction over the finite gate
list proves (1). Two required dense banks force B>=D and give (2).

The argument applies to total row support across all initial banks. If the
required density is already present in one particular old-input block, it
also lower-bounds this total support. Unknown dirty inputs cannot be treated
as zero to erase those coefficients.

## Two full chirps

The paid scan escape in Ross Richardson's #4023 uses, on L internal bits,

```
alpha=(1+i)/2, beta=(1-i)/2,
C=[[alpha,beta],[beta,alpha]],    C_L=C tensor ... tensor C.
```

Both alpha and beta are nonzero. Every row of C_L has exactly 2^L nonzero
entries. The inverse exchanges alpha and beta and has the same density.
Thus either endpoint `diag(C_L,C_L)` or `diag(C_L^-1,C_L)` on two arbitrary
independent banks, with restored dirty helpers if used, requires

```
2^R F_(S+1) >= 2^L.                                        (3)
```

With no unary native gates, define
`s_L=min { s>=0 : F_(s+1)>=2^L }`. Then S>=s_L. The first working example
is L=3: F_4=3, F_5=5, F_6=8, so S>=5. The earlier single-maximum
support argument gives S>=3 here. Since F_(L+1)<2^L for every L>=1,
the new integer floor strictly improves that estimate. We claim no
implementation attaining s_L.

For L>=1, the elementary induction F_(s+1)<=phi^s, where
`phi=(1+sqrt(5))/2`, gives the exact real inequality
`S >= L log(2)/log(phi)` when R=0. The displayed integer minimum is the
stronger usable statement. Hence no number of these inter-bank ADD scans
bounded independently of L can produce both chirps without native queries.
For general R, (3) is a necessary tradeoff, not an independent native-query
optimum. Any separate query lower bound keeps its own alphabet hypotheses.

## Why the distinct-bank premise matters

Allow a buffered same-bank update `x <- (I+2X_j)x` over F5, where X_j flips
address bit j. It is invertible because its two eigenvalues are 3 and -1.
Three such updates on one eight-coordinate bank give row support eight.
One inter-bank ADD into a second independent bank gives supports 8 and 9.
If all four updates were charged as the theorem's ADDs with R=0, its second
support bound would be F_5=5, which fails. Those first three gates instead
have to be excluded or counted as unary support exponents. This is an
explicit alphabet boundary, not a counterexample to (1).

## Evidence boundary

This is a scoped written proof. The finite verifier enumerates support-size
relaxations and executes separate exact F5 matrices as corroboration.
Neither establishes a complete multiplication theorem or a physical tape
cost. The chirp tensor is used only for its density, with its predecessor
construction and invoice cited rather than replayed. Formal proof-kernel
and independent human review are unclaimed.
