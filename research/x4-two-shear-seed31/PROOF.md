# Exact boundary and cost argument

Let `u=C_i h`, `v=C_j h`, with arbitrary initial target vector `y` and arbitrary
helper vector `h`. Write

```
S12(a) = [[1,a],[0,1]], S21(b) = [[1,0],[b,1]],
T = S21(b) S12(a) = [[1,a],[b,1+ab]].
```

The chronological preparation S12 then S21 sends `y` to `Ty`. The transformed
panel adds `TC h`. Undo S21, then S12: the output is
`T^-1(Ty+TC h)=y+C h`. Both targets can be dirty. The helpers are only read.
For every elementary addition the inverse-transpose exchanges source/target
and negates its coefficient. These inverse-transposes execute in the same
chronological order: `(M_k ... M_1)^-T = M_k^-T ... M_1^-T`.
The independent replay tests both maps and rejects reversing that chronology.

The old per-real-component lowering for nonzero reduced dyadic `q=n/2^d` is

`H(q)=3+floor(log2(abs(n)))+popcount(abs(n))+d`, with `H(0)=0`.

The initial work clear, leading source read, binary doubles, remaining source
reads, denominator halvings, signed target accumulation and final work clear
are all priced. Reusing arbitrary work is sound because of the initial clear.
The primitive interpreter tests its incoming value as an independent column.

For a pair, write `H(C)` for the sum of entry costs. The complete two-shear
price is

`H(C_i+a C_j)+H(b C_i+(1+ab) C_j)+2H(a)+2H(b)`.

The last two terms pay both preparation and restoration. Complex real cost
is twice this entire expression. The comparison baseline is the minimum of
the identity and each one-shear orientation/coefficient in the same menu,
including that shear's preparation and restoration.

For quarter-grid inputs `x/4,y/4` and `a=p/2,b=q/2`, the transformed coefficients
are `(2x+py)/8` and `(2qx+(4+pq)y)/16`. `verify.py` uses this integer formula.
The separate checker uses Fraction matrix multiplication and counts actual
emitted primitive sequences; it shares neither this formula nor the price
formula. Both fully enumerate the 6,216 pairs and 72 two-shear choices per
pair, and agree on the whole histogram and per-pair floors.

The winning pair's bill is `648 -> 484 -> 356` per component. Hence its saving
over the strongest declared one-shear baseline is `2*(484-356)=256` real
primitives. Its complete saving against identity is `2*(648-356)=584`.
This is exact within the finite menu and fixed primitive invoice, not a
lower bound on arbitrary dyadic circuits, target forests or global schedules.

All these additions are within source-bound frame zero. Other target rows
receive increments from immutable helpers, so their updates commute with the
displayed pair circuit. This supplies a local algebraic substitution argument.
It does not supply a rebuilt native/global supplier receipt. In particular,
local cancellation-free envelopes increase and must be repriced in a complete
implementation before any precision-admission or recurrence claim.
