# A closed formula for canonical rotation switch queries

This proof changes the arithmetic query in Nick Petalas's
[PR #7504](https://github.com/CrocSwap/integer-mult-bounds/pull/7504).
Its endpoint formulas and child-closure theorem are cited premises, retained
with exact bytes in `retained/pr7504/PROOF.md`. The new result is a closed
descent formula, a linear bit-cost query, and a matching worst-case lower
bound. No new kappa or complete compiler follows.

## 1. Contract

Let `h>=1`, `N=2^h`, `1<=s<=N`, and `0<=a<s`. The permutation sends
`x` to `(x+a) mod s` on `0<=x<s` and fixes every padded address. Use the
deterministic component orientation in Cinna Davis's PR4100 canonical
Beneš compiler. A query supplies row `0<=j<2h-1` and its **current wire**
`0<=x<N`. It asks for the Boolean switch bit, not the final destination
of the input token.

All arithmetic inputs have at most `h+1` bits, except the height and row,
which need `O(log(h+1))` bits. The bit-cost statement charges addition,
comparison, Boolean operations and shifts by their binary implementation.
It assumes no precomputed row table or advice about the query inputs.
It does not specify tape roles, ownership, or restoration.

## 2. Replace offset reduction by two interval lengths

Write `A=a` and `B=s-a`. At a nonidentity node, both are positive. For
child branch `c` in `{0,1}`, define the unreduced lengths

```text
A' = floor((A+c)/2),
B' = floor((B+1-c)/2).
```

The source's four parity cases give `s'=A'+B'` and raw offset `A'`.
This can also be checked by writing `A=2u+alpha`, `B=2v+beta`, with
`alpha,beta` in `{0,1}`. If both new lengths are positive, the source
offset reduction does nothing. If `A'=0`, the child is identity. If
`B'=0`, its raw offset equals its modulus, so the source reduces it to
zero and the child is also identity. If both vanish, it is empty identity.

Thus the pair need not reproduce the source's normalized modulus after
identity is reached. It must only preserve the fact that all later bits
are zero. It does: either zero component stays zero under every subsequent
update. This distinction is necessary. Treating `A'=s'>0` as a nonidentity
child gives a wrong central switch already at `(h,s,a,j,x)=(2,2,1,1,1)`.

## 3. Collapse any number of child steps

The child branches of a table query are the low bits of its current wire:
`c_i=(x>>i) mod 2`. For any depth `0<=d<h`, put

```text
M = 2^d-1,        t = x mod 2^d,
A_d = floor((a+t)/2^d),
B_d = floor((s-a+M-t)/2^d).
```

These are exactly the unreduced interval lengths after `d` child steps.
For the first length, repeated halving gives

```text
A_d = floor((a + sum_(i=0)^(d-1) c_i 2^i)/2^d).
```

To prove the step from `d` to `d+1`, use
`floor((floor(z/2^d)+c)/2)=floor((z+c*2^d)/2^(d+1))` for integer `z,c`.
The second length has digit `1-c_i`, whose weighted sum is `M-t`.
The initial case `d=0` gives `(a,s-a)`. This proves both formulas by
induction. Section 2 proves that a zero component correctly represents
every later identity node.

## 4. One endpoint query

Set `d=min(j,2h-2-j)`, `H=h-d`, and `y=x>>d`. After exactly `d`
interior descents, the requested row is an endpoint of height `H`.
The query uses the pair in Section 3 once. If either length is zero,
return zero. If `H=1`, both positive integer lengths must be one; return
one. Otherwise set `S=A_d+B_d` and `A=A_d`.

For the first endpoint, when `j=d`, return

```text
[S and A are odd] [floor(y/2)=floor(S/2)].
```

For the last endpoint, return

```text
[A is odd] [y<S]       if S is even;
[y<A]                  if S is odd and A is even;
[A-1<=y<=S]            if S and A are odd.
```

These are precisely the retained endpoint formulas. In particular, the
last case can switch the first padded wire. Section 3, identity absorption,
and the source's child theorem prove equality to the canonical switch
table for every legal height and query. No network or row is constructed.

## 5. Linear work and optimal order of growth

The query has a fixed number of additions, subtractions, comparisons,
Boolean operations and shifts on at most `h+2` bits. It has no descent
loop. The depth and reflected row need `O(log(h+1))` bit work. All remaining
operations have `O(h)` binary work and need `O(h)` temporary bits.

Variable shift lengths do not require a multiplication or division. A
binary counter can emit the required unary prefix using repeated decrement.
Across `d` decrements, the total number of visited trailing-zero bits is
`O(d+log(d+1))`. A return to the counter's low end changes only the constant.
Copy the remaining field in one pass. The mask and prefix restriction use
the same bounded scans. Since `d<h`, this also gives a sequential bit
implementation with `O(h)` work. It is an arithmetic implementation
argument, not a supplied physical tape program or an owned-work contract.

The order of growth cannot improve for exact standalone bit queries. Fix
`h>=2`, `s=2^h-1`, `j=2h-2`, and `x=0`. With an `h`-bit offset field,
the all-zero offset returns zero. Changing any one offset bit `k` with
`1<=k<h` to one gives a legal even offset `2^k`, and the last-endpoint
formula returns one. An exact deterministic algorithm must inspect all
`h-1` such bits on the zero input. Otherwise an unread bit gives an
indistinguishable input with a different answer. This is a bit-probe lower
bound even if every other descriptor is free.

The lower bound does not rely on a long encoding of zero. For `h>=3`,
fix `x=a=2^(h-1)`, the same odd `s` and last row. The baseline answer is
zero. Changing any offset bit `1<=k<h-1` from zero to one gives answer
one while retaining an `h`-bit positive offset. Thus minimal binary
encodings also require `h-2` probes on this input. The worst-case cost is
therefore `Theta(h)` in either encoding. No claim is made about randomized
error, amortized repeated queries, supplied advice, or word-RAM unit cost.

## 6. Verification and boundary

The verifier compares every entry of all 2,793 networks at heights one
through six against the unchanged canonical graph compiler and the
unchanged source recurrence: 1,633,182 entries per comparison. It also
routes all 152,526 addresses, checks 892,854 descent states, and compares
420 wide queries through height 4096. Six explicit cases reach height
65536. Five changed formulas produce wrong source bits; twelve malformed
domains reject before any identity shortcut. The receipt records exact
witnesses and the 544-bit historical row digest.

The full-height theorem is the induction above, not an extrapolation from
these checks. The executable caps height at 65536 to bound allocation.
The lower-bound fixtures test the stated bit sensitivities. They do not
simulate every possible query algorithm.

Nick Petalas supplied the endpoint and child identities. Cinna Davis's
compiler supplies the separate finite oracle. Both retained executables
are shared comparison dependencies. Their complete historical verification
suites are not invoked. Jerry Chen's PR7593 supplies a literal physical
implementation of the earlier quadratic recurrence; its program and cost
are not replaced here. CRT offset production, descriptor serialization,
owned predicate return, clearing, head restoration, payload consumption,
and complete caller pricing remain open. All five selected framework
assumptions remain. This is author checking with substantial OpenAI Codex
assistance, not independent human or formal-kernel acceptance.
