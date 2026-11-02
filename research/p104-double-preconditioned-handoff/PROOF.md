# Ordered cancellation in the concrete dual pairs

This contribution was produced by Nick Petalas. Apache-2.0.
The dual pairs and column-unit formula are CubeJerry's PR6322, extending
unpaidmoon's PR6297 and Ali Romman's PR5611/5602. The new construction below
uses their exact scalar boundary contract.

## The two noncommuting preconditioners

Let `p=596`, and let `e_i` be a coordinate column. Work over `Z[1/2]`.
Retain the row and two columns

```
a = (5/16)e592^T + (5/16)e593^T + (5/8)e594^T + (3/8)e596^T,
u = -e592 + e593 + e594 + e596,
b = -e188 + u.
```

Both pairings `a u` and `a b` are one. These are boundary functionals and
directions, not assumed values of dirty registers.

Set

```
S1 = I + e592 e593^T,
S2 = I + (1/2)e594 e592^T,
S  = S2 S1.
```

Each shear fixes `e_p` and is invertible by negating its coefficient.
They do not commute: the product of the second nilpotent part with the first
is `(1/2)e594 e593^T`, whereas the reversed product is zero.

First applying `S1` to either column cancels its 592 coordinate. Consequently
`S2` changes no column coordinate afterward. For `d` equal to `u` or `b`,

```
d' = S d = d + e592.
```

For the row, `S1^-1` cancels coordinate 593. The next right multiplication
by `S2^-1` cancels coordinate 592, since `(5/16) - (1/2)(5/8) = 0`.
Therefore

```
a' = a S^-1 = (5/8)e594^T + (3/8)e596^T.
```

The pivot coordinate of `d'` is still one and `a'd'=1`. Apply PR6322's
column-unit formula to get `R'` satisfying `a'R'=e_p^T` and `R'e_p=d'`.
Explicitly its first operation is `x596 -= (5/8)x594`, followed by the
unit injections from 596 to the nonpivot support of `d'`.

Put `R=S^-1 R'=S1^-1 S2^-1 R'`. Then

```
a R = a' R' = e_p^T,
R e_p = S^-1 d' = d.
```

Thus the two inverse preconditioners must execute after `R'`, in the
order `S2^-1`, then `S1^-1`. This order is proof-relevant. Every factor is an
invertible coordinate ADD on arbitrary inputs.

## Literal programs and complete tariff

The source completion is the following six ADDs at frame 3:

```
x596 -= (5/8)x594
x188 -= x596
x593 += x596
x594 += x596
x594 -= (1/2)x592
x592 -= x593
```

The cut completion at frame 1053 omits only `x188 -= x596`.
The inverse of either completion reverses the list and negates every
coefficient. No SCALE, spare role, initialized register or new transport is
needed by these completions.

For a reduced dyadic `c=n/d`, the retained scalar ADD allowance is
`A(c)=2(3+floor(log2|n|)+popcount(|n|)+log2 d)`. Hence

```
A(1) = 8,   A(1/2) = 10,   A(5/8) = 20.
source completion = 20 + 3*8 + 10 + 8 = 62,
cut completion    = 20 + 2*8 + 10 + 8 = 54,
all four boundaries = 2*(62+54) = 232.
```

Inverse costs are identical because the tariff is insensitive to the sign.
All coefficients and inverse coefficients satisfy the retained
`|c|+1 < 2^16` bound. There are `2*(6+5)=22` ADDs. PR6322 already proves
that count minimal for these separately completed boundary maps, with arbitrary
ancillary roles. Its ADD lower bound is cited, not independently re-proved or
replayed here. No weighted optimum follows from it.

## Whole-word application and claim boundary

Use the same historical PR5580 source, cut 13762, pivot 596 and frames
`3 < 1053 < 127` as PR6297/6322. Let `P` and `Q` be its prefix and suffix,
let `W=QP`, and let `R_s`, `R_c` be the new source and cut completions.
The retained constructor checks the exact prefix/suffix equations
`vP=a` and `Qu=b` and the availability of all cut operands before inserting
the new programs. They give

```
e_p^T R_c^-1 P R_s = v P R_s = e_p^T,
R_s^-1 Q R_c e_p = R_s^-1 Q u = e_p.
```

Retire the original arbitrary pivot input at the cut and continue with a
fresh arbitrary input `z`. The output becomes
`R_s^-1 W R_s x - e_p x_p + e_p z`.
The source basis acts only on the independent `(3,127)` helper group, where
`W` is identity, and commutes with the main shear. Thus this equals
`W x - e_p x_p + e_p z`, with retired output `x_p`. Both input freedoms are
preserved. This is the credited coupled-handoff argument applied to the new
boundary maps, not a new general handoff theorem.

The new word has 25,162 events, 736 public inputs and eight owned lifetimes
with peak one. Complete scalar allowance is `217428+232=217660`, using the
predecessor's source allowance as a comparison premise; both exact arithmetic
engines freshly enumerate the new word's complete allowance and endpoints.
They check all 744 formal columns and 553,536 coefficients. Paid profile is
`{1:2211,2:459,3:494,4:94,5:164,6:18,7:14}` and productive helper profile is
`{4:84,5:6,8:15,9:423}`, as in the predecessor handoff.

This proves a legal scalar construction and its finite invoice, without a
new recursive moment, kappa or selected-frontier claim. No weighted optimum,
current-word transfer, native/caller admission, rounded precision/tape bound,
stock or uniform compiler proof is supplied. All five selected framework
assumptions remain. Independent human and formal proof-kernel review are unclaimed.
