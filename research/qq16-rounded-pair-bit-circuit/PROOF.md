# A Boolean invoice for the signed nearest-even pair

## Statement and model

Let `w>=1`, `L=w+2`, and `s` be a fixed sign in `{-1,1}`. The four real
integer inputs `ar,ai,br,bi` lie in `[-2^(w-1),2^(w-1)-1]`. The unsigned
rounding exponent satisfies `0<=d<=L-2`. Define

```
sr=ar+br; si=ai+bi; dr=ar-br; di=ai-bi
v=(sr-s*di, si+s*dr, sr+s*di, si-s*dr)
out_j = 2^d * nearest_even(v_j / 2^(d+1)).
```

This is the `integer_pair` formula in the retained PR2807 source. There is
a Boolean circuit with four signed `L`-bit outputs computing it exactly.
With a fixed exponent its gate count is

```
G_fixed = 52L - 4d + 8.
```

With `k=bit_length(L-2)` exponent-input bits, the runtime-exponent circuit has

```
G_runtime = 24Lk + 52L + 4*2^k + 4k + 4.
```

The basis is two-input AND, XOR, OR and one-input NOT. Constants, wires,
sign extension and fan-out are free. The sign is fixed when building either
circuit; the runtime variant takes `d` as binary input. The legal exponent
range is a precondition. No check of an out-of-range bit pattern is included.
These are exact counts of the emitted construction, with redundant gates
left in place, and constructive upper bounds on minimum gate complexity.
They are neither optimality claims nor reversible circuits.

The proof below is uniform in width. The bounded builder supports widths up to
4096; finite test coverage is separate from this quantified argument.

## Signed raw arithmetic

Sign-extend each input to `L` bits. Use the usual full-adder identities

```
t = a XOR b
sum = t XOR carry
next = (a AND b) XOR (carry AND t).
```

The two carry terms cannot both be one, so XOR gives their union. Each
bit uses five gates. Subtraction complements all `L` bits of the second
operand and starts with carry one. Discard the final carry in each adder.

There are eight adders and four complemented subtrahends, costing `44L`.
The sign selects the two raw additions and two raw subtractions by wiring.
Every raw row has three positive input coefficients and one negative.
Writing `H=2^(w-1)`, its exact interval is `[-4H+1,4H-3]`, inside the
signed `L`-bit range. The earlier pair sums and differences fit as well.
Thus modular adder outputs represent the actual signed intermediate values.

## Nearest-even with signed bits

For any signed `L`-bit raw value `v`, Euclidean division gives

```
q = floor(v / 2^(d+1))
v = q*2^(d+1) + r,  0<=r<2^(d+1).
```

The guard bit is bit `d` of `v`; sticky is the OR of bits `0..d-1`;
the retained low bit is bit `d+1`. This description also holds for negative
two's-complement integers, because the low bits represent the Euclidean
remainder. Therefore the correct increment is

```
inc = guard AND (sticky OR retained_low_bit).
```

It increments exactly above half or at an odd tie. The output is
`(q+inc)*2^d`. An increment cell uses one XOR and one AND per bit.
Arithmetic-right shift by `d+1`, with one additional sign bit, represents
`q` in `L-d` bits. The extra sign bit prevents positive ties near the top
of the retained range from wrapping. Append `d` low zero bits after the
increment, yielding `L` output bits.

For the fixed rounder, starting sticky at constant zero uses `d` OR gates.
The increment predicate takes two more gates; the increment uses `2(L-d)`.
Thus one rounder costs `2L-d+2`, and four plus the raw arithmetic cost
`52L-4d+8`.

## Runtime exponent and discarded bits

Use a barrel shift with one stage for each bit `d_i` of `d`, in ascending
order. At stage `i`, let `t=2^i`, and let `y` be the pre-stage signed word.
Compute `lost=OR(y[0:t])`, then

```
sticky = sticky OR (d_i AND lost)
y = mux(d_i, arithmetic_shift_right(y,t), y).
```

By induction, `y=floor(v/2^p)` after the partial shift `p`, and sticky is
the OR of the original low `p` bits. If the stage is selected, its low
`t` bits are exactly the next original bits discarded. All partial shifts
are at most the legal final `d<=L-2`; sign extension creates no spurious
discarded bits. It is essential to read `lost` before updating `y`.

A mux is `a XOR (select AND (a XOR b))`, using three gates. The right
shift therefore costs `3Lk` gates. The lost/sticky logic costs

```
sum_i ((2^i-1)+2) = 2^k+k-1.
```

Now use `guard=y[0]`, `retained=y[1]`, the two-gate increment predicate,
and a constant arithmetic-right shift by one. Increment this sign-extended
`L`-bit value using `2L` gates. A logical left barrel shift by `d` costs
another `3Lk` gates. One runtime rounder costs
`6Lk+2L+2^k+k+1`. Four plus `44L` prove the stated formula.

The rounded output cannot overflow `L` signed bits: its absolute value is
at most `|v|/2+2^(d-1)`, at most `2^(L-2)+2^(L-3)`, strictly less than
`2^(L-1)`. The same conclusion holds when `d=0`. The retained quotient
also has room for its increment. Final discarded barrel bits therefore
do not lose part of a mathematical output.

## Conditional instantiation of the QQ16 finite format

PR2807's finite-format proof gives `W=Qmax+E+20` and strictly bounds every
completed within-line real component by `2^(Qmax+E+16)=2^(W-4)` in common
integer units. Conditional on that inherited bound, take `w=W-3`, `L=W-1`.
The omitted high input bits and restored high output bits are redundant
sign bits. Its admitted `d<=W-3` is exactly our `d<=L-2`. All arithmetic
fits the predecessor's `W`-bit register allocation.

Its example `W=456` gives `w=453`, `L=455`, `k=9`:

| Variant | Exact gates per signed pair |
|---|---:|
| Fixed d | `23668-4d` |
| Runtime binary d | `124028` |

Each tensor factor has at most `D/2` pair instances per owner. The source
declares 336 lines, with `lambda` factors and `N` owners per line. Thus the
runtime pair-kernel subtotal is at most

```
168 * G_runtime * lambda * N * D
= 20836704 * lambda * N * D   when W=456.
```

This counts gates in an unrolled collection, or gate evaluations when the
same circuit is reused. It does not count reusable hardware area. It includes
the barrel selection for a supplied binary exponent. It excludes finding
that exponent by scanning components, range validation, whole-word scalar
ADDs/CLEARs, native wrappers/maps, addresses, physical control and movement,
storage, and the eventual output consumer. This is one explicit arithmetic
subtotal, not a complete decoder invoice or a recursive rank-one tariff.
