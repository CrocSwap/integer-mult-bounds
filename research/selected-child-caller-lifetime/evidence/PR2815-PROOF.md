# Source lifetime proof

## Domain and entry residents

Use the unchanged source exports in `SNAPSHOT.json`. Let d be a fixed integer
from 1 through 128, c a positive encoded column count, n an encoded parent size
with dc <= n, and M=q^w with fixed q>=2 and integer w>=1. The residue Ring
satisfies its canonical modulus/one-high-bit-margin contract. The distinct
index arena has sufficient width and margins for all intermediate addresses
through 2n and for the source division operations. Geometry has its original
`Unsigned` arithmetic, a borrowed c and a one Word containing 1. Constructor
literals, inputs and borrowed unrelated Words are already live before each
entry baseline. The three spectator inputs are positive canonical Count tapes.
For the selected application d=64 and 64<=n<128, so c=1.

Execution is sequential, successful, has sufficient capacity, and has no
observer or concurrent mutation that changes numerical residents. Borrowed
Words and templates enter with their heads at 1. In embedded mode the logical
atom positions lie in [0,2dc); in flat mode they lie in [0,2n). A binary call
has ordered distinct positions. The physical map is increasing and is

```
p(x) = x + 2(n-dc) if embedded and x>=dc, otherwise x.
```

In particular 0<=p(x)<2n. These conditions ensure all subtractions and power
exponents in `extents` are nonnegative. They also exclude malformed encodings,
reverse atom order, overflow and failed allocation. Those rejection paths do
not have the successful-return cleanup contract.

Let B_R and B_I count ALL live residue/index Words immediately before the
particular method being bounded. Include the Ring, Geometry, Layout, event
positions, suspended caller, unrelated matrices and every other borrowed
numerical slot. The entry baselines for different methods are not interchangeable.
Count/Counter tapes and returned cardinalities are not numerical arena Words;
their space, contents and movement are separate obligations. No claim here
bounds Python heap use or complete machine storage.

## Primitive allocation lifetimes

All numerical allocations pass through `Arena.zero`. `copy`, `add` and
`subtract_exact` allocate exactly one result. Their digit scans allocate no
nested numerical Words and restore their input heads. `compare` allocates none.
`times_small` owns one running result. It creates doubled before freeing that
result, then creates the next result before freeing doubled when the digit is
one. It therefore has at most two additional Words, including its final result.
Its finite multiplier is at most 128.

`Unsigned.divmod` owns scan, quotient and remainder. A digit step creates
shifted before freeing remainder. If subtraction is necessary, it then creates
the new remainder before freeing shifted, after the old remainder is gone.
Thus its peak is four additional Words, and its successful return owns two.
This counts the actual sequence, not scan plus all historical remainders.

`radix_power` owns divisor and power during each division. The six-Word peak
is divisor and power plus the division's four. After each division it frees
old power and remainder before yielding with the new quotient as power.
Generator close frees its two residents. For M=q^w>1, its first division
performs a digit step and attains six. `multiply_atom_power` only adds a
Counter tape. A zero exponent does not enter `radix_power` and allocates no
residue Word; every positive exponent enters it and attains six. Repeated
iterations are successive lifetimes. Count products, marginal copies, gap
multiplication and in-place cardinality arithmetic allocate no arena Words.
This derivation also credits the primitive lifetimes used by PR2759/2810.

## Constructor and physical map

`Layout.__init__` computes core=dc, extra=2(n-dc) and total=2n. After core
and remaining are allocated, `times_small(remaining,2)` uses at most two more
Words, for four in total. remaining is freed; core and extra persist during
the two-Word multiplication producing total, again attaining four. It returns
with exactly three distinct owned indices. It allocates no residues.

`physical` copies the input or calls the original `Geometry.plus`, which uses
one `Unsigned.add` result and checks its carry. It therefore allocates exactly
one index and returns it. It preserves the input in either branch.

## Unary/binary extents and full fibre

Let a=p(first), and b=p(second) when present. For a unary call set b=a.
The exact returned prefix and suffix cardinalities are

```
pre  = before * M^a * (gap if a>=n else 1)
tail = suffix * M^(2n-b-1) * (gap if b<n else 1).
```

A binary call additionally returns

```
middle = M^(b-a-1) * (gap if a<n<=b else 1).
```

Exactly one output contains the intervening gap. For unary calls the two
conditions partition the cases. For binary calls the alternatives are both
atoms below n, both at/above n, and a<n<=b. The source's separate tests are
precisely these alternatives. `marginal()` returns each positive cardinality
with its own single high zero bit. These formulas are also the independent
integer oracle in the finite checker.

A unary call retains a while calculating after=total-a and count=after-1,
for three additional indices. A binary call retains a,b plus after,count,
then frees after,count before allocating distance=b-a and count=distance-1.
Both intervals have exactly four additional indices. Count operations allocate
no index Words. All these owned indices are freed before returning the
cardinality tapes; all numerical entry slots, bytes and heads are preserved.

Each power call needs at most six residues, with no numerical residue retained
by Layout between powers. Its exact residue peak is six iff at least one of
a, 2n-b-1, or, for binary calls, b-a-1 is positive. A unary call always has a
positive exponent because n>=1 and a+(2n-a-1)=2n-1. A binary call with n=1,
a=0,b=1 has all exponents zero and peak zero. Positive tail or middle exponents
attain the residue and index maxima together. If only the prefix exponent is
positive, the six residues occur before the after/count indices exist, so the
table gives coordinatewise maxima without asserting simultaneous sharpness.

`fibre` returns before*gap*suffix*M^(2n). It allocates no indices and needs
exactly six residues because 2n>0. It restores all numerical entry residents.
`close` allocates nothing and erases/frees core,extra,total. Unlike `extents`,
it consumes those three entry slots; its final numerical delta is (0,-3).

At completed allocation cuts each full live Word occupies bits+1 non-LEFT
symbols. Partial initialization/erasure occupies no more and allocates no
additional numerical Word. Including the permanent template in each arena,
the binary-extent occupied-content upper bound is therefore

```
(B_R+7)*(b_R+1) + (B_I+5)*(b_I+1).
```

Replace five by four for unary extents. This excludes LEFT markers, erased
backing capacity and all nonnumerical tapes. Finite scans count every allocated
slot, including erased slots, rather than assuming those slots are empty.

## Conditional selected adapter composition

Inherit the exact source and successful-callee premises of PR2801's pinned
`evidence/CALLER-ENTRY.md`. Before an adapter ADD, the suspended caller owns
columns and fields, three Geometry indices, three Layout indices, and four
trace/event indices, totalling twelve above ALL `Consumer.apply` entry
residents. `stream_runner.action` calls the two-bank `layout.extents` before
`add_pass`; the coefficient callback is invoked by the later ADD traversal.
The extents return Count tapes and no numerical Words. Consequently the exact
same `(0,12)` numerical context is live before extents and before the callback.

The present component has excess `(6,16)` above `Consumer.apply` entry during
binary extents. PR2810, separately inherited with its PR2781/2801 contracts,
bounds the following complete adapter ADD by `(37672,34)`. The maximum of
these successive phase allowances is `(37672,34)`, so preceding extents do
not increase it. Do not add their temporary counts. This conditional corollary
is not a replay of the coefficient, directory, complete caller or physical
implementation. Initialization, validation, child and non-ADD phases still
require their own same-baseline analysis.
