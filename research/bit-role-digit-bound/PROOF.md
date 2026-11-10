# The selected BIT role digit satisfies c_B <= 2^(H1+13) <= N^2

This is a scoped arithmetic consequence of an inherited nested-width bound.
It is not a new census of the compiler, a materialized role count, a smaller
fit threshold, or a change to the selected frontier.

## 1. Selected stage

The selected claim `certificates/frontier6030/CLAIM.json` records

```text
admitted_BIT_saving = 17/5000
BIT before cover rank_encoding = 2^25986965159937
```

The same rank and admitted saving are the ordinary BIT record in
`research/query-thinned-controllers/RESULT.json`: `uniform_H1 = H1`,
`uniform_N = 2^H1`, `tensor_power = 1024`, `target_floor_base = 18`,
`atom = 1/250`, and

```text
prime_rule = odd q > 2^26*N^5
```

with the recorded avoidance of fixed denominators and rank witnesses.
Write `N = 2^H1`. For every prime allowed by that rule,

```text
log2(q) > 26 + 5*H1.
```

The stock formula in `research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md`
section 8 is written there as a LaTeX display. The selected-stage band
proof transcribes it as:

```text
k <= D*(N^2*(w-1) + ceil(log_q(B*|GL_N(F_q)|))) + ceil(log_q S_old) + 1.
```

`B` is the productive role count of the compiled uniform program. Define

```text
c_B = ceil(log_q B).
```

`research/selected-bit-stage-stock-band/PROOF.md` proves that the parent
stock fits for `t = log2(e) >= 52182660963735` once `c_B <= N^2` and
`k_old <= e/4`. `research/selected-old-leaf-reserve/README.md` proves the
external old-leaf reading `S_old = 1`, hence `k_old = 1`, and leaves `c_B`
open because `B` is not materialized.

## 2. Inherited nested-width bound

This package does not re-prove the source census. It uses the bound stated
in `research/lockstep-live-role-audit/constant_c.py` for the #4436 nested
widths, and the identification that file already makes when it bounds the
`log2 B` term of `W(w)` by `N*X`. In that reading the stock formula's
productive role count is the nested-width count `B_N`. The mixed-flow note
states a different, untensored `C_N`; this proof uses the tensored formula.

```text
Wv = W^v,  Pv = M^v + Wv*b^v,
C_N = Wv*(Wv+Pv+1)^(h+1),  h <= H1,
B_N <= C_N^N.
```

Here `W` is the productive-field count of the BIT invoice, `M` is its paid
rank mass, `b = 18` and `v = 1024`. For a positive integer `n`,

```text
ulog2(n) = n.bit_length() = floor(log2 n)+1 > log2 n.
```

Therefore

```text
X = ulog2(Wv) + (H1+1)*ulog2(Wv+Pv+1)
```

satisfies `log2(C_N) < X` whenever `h <= H1`, and

```text
log2(B_N) <= N*log2(C_N) < N*X.
```

The verifier recomputes `X = 471715391583208384` from the pinned invoice.
That integer has 59 bits, so `X < 2^59`.

## 3. Comparison with the prime rule

Let `den = 5*H1+26`. The recomputed values satisfy

```text
X < 2^13 * den.
```

Combine this with section 2 and `log2(q) > den`:

```text
log_q(B) = log2(B)/log2(q) < (N*X)/den < 2^(H1+13).
```

If `0 <= y < 2^E` and `2^E` is an integer, then `ceil(y) <= 2^E`. Hence

```text
c_B <= 2^(H1+13).
```

Since `H1 >= 13`,

```text
2^(H1+13) <= 2^(2*H1) = N^2,
```

so `c_B <= N^2`. The band note already says this comparison follows from
the nested-width bound; the arithmetic above is the missing calculation.
Together with the cited reading `S_old = 1`, the sufficient guard

```text
t >= 52182660963735  implies  k < e/2
```

no longer depends on an unknown role count.

## 4. What this does not do

The obstruction side of the band, `t <= 52182660963729`, does not use `B`.
The six integers of `log2(e)` between that obstruction and the sufficient
guard remain unresolved. The additive role term is at most `2^(H1+13)`,
while the matrix term at one level is `N^2*w = 2^(2*H1)*w`. Their ratio is
at most `2^(13-H1)`, so replacing the hypothesis `c_B <= N^2` by this
sharper digit bound does not move the published guard by one bit of
`log2(e)`. No `actual_stock_coefficient` is chosen, and kappa stays
`781451/250000000`.
