# Depth-first continuation stack at the new c

The PR2809 simulator is not executed. The model is the depth-first reading of
`BIT.md` §2 at `c = 8667/5000000`, with the width recurrence written there.

## Parameters

`q = 2^89 - 1`, `W = 28416`, `M = 269241600 = W · 9475`, and
`N = |GL_64(F_q)|`. Let `G = W N` and

```text
K(w) = M · N · q^(4096(w-1)).
```

For an integer address length `e ≥ 1`,

```text
w(e) = min { j ≥ 1 : j^5000000 ≥ e^8667 },
D(0) = 0 for n < 64,
D(n) = 1 + D(42 · floor(n/64)) for n ≥ 64.
```

`w(e)` is `ceil(e^c)`. `D(e)` is the number of recursive cuts in the written
width recursion. `BIT.md` calls a bound on this depth `h`.

## Model

One ancestor chain is parked. After a node of volume `V`, the next parked
payload has volume at most `V/G`, then `V/G^2`, and so on, for `D(e)` cuts.
Each cut stores one integer of size at most `K(w)^{D(e)}`. A stream that
contains an `e`-bit address field has volume `V ≥ e`. The physical stream
`P G S q^(2e)` of the older ordinary-interchange proof is a special case.

Cells count payload symbols and parameter bits in the same unit. One bit is
one cell. That is the more expensive of the two natural units, because a
`q`-ary digit holds 89 bits.

## Lemma 1. Width for small addresses

For every integer `e` with `2 ≤ e ≤ 2^576`, `w(e) = 2`. For every integer
`e ≥ 2`, `w(e) ≥ 2`.

`576 · 8667 = 4992192 < 5000000`, so `(2^576)^8667 = 2^4992192 < 2^5000000`.
Any positive integer `e ≤ 2^576` therefore satisfies `e^8667 < 2^5000000`,
and `j = 2` is admissible. For `e ≥ 2`, `e^8667 ≥ 2^8667 > 1`, so `j = 1` is
not admissible.

## Lemma 2. The suggested level-1 allowance fails

`BIT.md` gives the child payload the volume `V/G`. The first step named by
`research/bit-stock-recurrence-audit` compares a level against

```text
V / (G · q^(4096(w-1))).
```

At level 1 the two quantities differ by exactly `q^(4096(w-1))`. Lemma 1
makes this factor at least `q^4096` for every integer `e ≥ 2`. The child
payload alone is already larger than that allowance. The same comparison at
`e = 1` has `w = 1` and factor `1`, so the hypothesis `e ≥ 2` is sharp.

This does not by itself refute `O_q(V)`. The allowance is smaller than the
geometric ratio `1/G` by that same factor.

## Lemma 3. Payload series

For `G > 1`,

```text
sum_{k ≥ 1} V / G^k = V / (G - 1) < V.
```

`G = W N > 2`. The sum does not depend on `c`, on `e`, or on cutting the
chain off early.

## Lemma 4. Two coarse steps halve the width

For every integer `n ≥ 64`, the value after two steps of `n ↦ 42·floor(n/64)`
is at most `floor(n/2)`.

Let `f = floor(n/64)`, `x = floor(42 f / 64)` and `r = (42 f) mod 64`. Then
`42 f = 64 x + r` with `0 ≤ r < 64`. Both `42 f` and `64 x` are even, so `r`
is even. Write `r = 2 s`. Then

```text
672 x = (21/2) · (42 f - 2 s) = 441 f - 21 s ≤ 441 f ≤ 512 f,
```

hence `84 x ≤ 64 f ≤ n`. The two-step value is `42 x`, so twice that value
is at most `n`.

## Lemma 5. Depth bound

For every integer `n ≥ 64`, `D(n) ≤ 2 (bitlength(n) - 6)`. For `n < 64`,
`D(n) = 0`.

If the two-step value is below 64, then `D(n) ≤ 2`. Every `n ≥ 64` has
bit length at least 7, so the claimed bound is at least 2. If the two-step
value `n2` is at least 64, then `D(n) = 2 + D(n2)` and `n2 ≤ floor(n/2)`, so
`bitlength(n2) ≤ bitlength(n) - 1`. The inductive hypothesis on `n2` gives

```text
D(n) ≤ 2 + 2 (bitlength(n) - 1 - 6) = 2 (bitlength(n) - 6).
```

`n2 < n`, so the induction is well founded.

## Lemma 6. Encoding bits

`bitlength(K(w)^D) ≤ D · bitlength(K(w))`, because
`K(w) < 2^{bitlength(K(w))}`. Across `D(e)` cuts the parameter bits are at
most

```text
D(e)^2 · bitlength(K(w(e))).
```

On `2 ≤ e ≤ 2^576`, Lemma 1 gives `w = 2`. The exact value
`bitlength(K(2)) = 729117` is computed in `verify.py` from the product
formula for `|GL_64(F_q)|`. The maximum of `D(e)^2 · 729117 / e` on
`2 ≤ e ≤ 200000` is attained at `e = 448`, where `D(448) = 4` and the
quotient is `11665872 / 448`. The least integer `C` with
`C · e ≥ D(e)^2 · 729117` for every such `e` is therefore `26040`.
`26039 · 448 < 11665872`, so `26039` is not enough.

For `200000 < e ≤ 2^576` the Lemma 5 bound is still at most `26040 · e`.
`verify.py` checks the left edge of every bit length in that range, which is
where a fixed numerator over a growing denominator is largest. For
`e > 2^576`, `w(e) ≤ 2^{ceil(bitlength(e) · 8667 / 5000000)}`, and

```text
bitlength(K(w)) ≤ bitlength(M N) + 89 · 4096 · (w - 1),
```

because `q < 2^89`. The same depth bound times this bit length stays at most
`26040 · e` for every bit length from 577 through 20000. From there through
bit length 100000, `4 L^2 (bitlength(MN) + 89·4096) · 2^{t(L)}` still has
bit length at most `L - 2`, with `t(L) = floor(L · 8667 / 5000000) + 1`.
At bit length 100000 the coarser majorant `L/577 + O(log L)` leaves
thousands of bits of slack against `L/2`. One later step can spend at most
three of those bits. Any window of 577 bit lengths increases `floor(L/2)`
by 288 and increases the majorant by at most 3, so the slack keeps growing.
Thus for every integer `e ≥ 2`,

```text
parameter bits ≤ 26040 · e.
```

The maximizing address length has `w = 2`. Any smaller positive `c` that
still forces `w(448) = 2` produces the same constant.

## Theorem

Under the model above, for every integer `e ≥ 2` and every volume `V ≥ e`,

```text
parked payload + parameter bits ≤ V/(G-1) + 26040 V ≤ 26041 V.
```

The constant depends on `q` through `N` and `K`, and on the checked
arithmetic. It does not depend on `e` or on `V`. In this model the serialized
ancestor stack keeps `O_q(V)` visited space at the new `c`.

## A different parking reading

If each of the `D(e)` cuts instead parked a fresh copy of the root volume
`V`, the total would be `D(e) · V`. For every `n ≥ 265`,
`42 · floor(n/64) ≥ floor(n/2)`, so each step drops the bit length by at most
one while the width stays above 264. Hence `D(n) ≥ bitlength(n) - 9` once
the bit length is at least 9. At `e = 2^26050`, `D(e) ≥ 26042 > 26041`, and
`D(e) · V` exceeds the constant of the theorem. That reading is not
`O_q(V)`. `BIT.md`'s geometric sentence is the reading proved here. The
serializer that would decide which reading the machine implements is not
inspected in this package.
