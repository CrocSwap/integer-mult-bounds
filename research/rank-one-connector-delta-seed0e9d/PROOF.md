# Exact identity and complete local cost

All vectors and maps are over F2. Let `n >= 2`, with standard basis
`e_0,...,e_(n-1)`, and define

```text
J = 1 1^T             (the all-ones n by n matrix)
R = e_0 e_0^T         (rank one)
B = J
B' = B + R
C = e_0 + e_1         (an n by 1 source-update map)
```

For the fixed vector `u` and source `x`, set `x' = x + C u`. Since `1^T C=0`
and `e_0^T C=1`,

```text
B C = 0,       R C = e_0 != 0.
```

The requested pair map on arbitrary dirty boundary registers is

```text
x_final  = x + C u
u_final  = u
z_final  = z
y1_final = y1 + B x
y2_final = y2 + B' (x + C u).
```

Here `x,u,z,y1,y2` are all arbitrary at entry. The output registers and the
connector are distinct; no clean value is assumed in them.

## General transition identity

For any two maps `B1,B2` with the same source and connector spaces, let
`x' = x + C u` and `R = B1 + B2`. After a first complete readout using `B1`,
the connector is `z0 + B1 x`. The unique vector correction that makes the
connector equal the second call's required entry value `z0 + B2 x'` is

```text
Delta z = B1 x + B2 x'
        = R x' + B1 C u.
```

The equality follows by expanding `R x'`: `B1x + (B1+B2)x' + B1Cu`
reduces to `B2x'` because `x+x'=Cu` and the two `B1Cu` terms cancel. The
correction is unique as a vector because the desired connector value is fixed
for every input. Thus the exact composition is

```text
y1 += z; z += B1 x; y1 += z;
x += C u; z += (B1+B2) x + B1 C u;
y2 += z; z += B2 x; y2 += z.
```

The previous same-map dirty-connector adapter is the case `B1=B2`, when
`R=0` and the correction is `B1 C u`. The new mechanism has `R != 0`; when
`B1 C=0`, the necessary correction is just the source-dependent map-delta
application `R x'`. The family below chooses `R` rank one and nonzero, so the
source change is material to the transition (`R C != 0`).

## Paired schedule

Charge one scalar XOR/ADD for every nonzero coefficient in each displayed
matrix update. Use this sequence:

```text
y1 += z
z  += B x
y1 += z
x  += C u
z  += R x
y2 += z
z  += B' x
y2 += z
```

In the fifth line, `x` is already `x'`. After the first three lines,

```text
y1 = y1_initial + B x_initial
z  = z_initial + B x_initial.
```

After the source update and rank-one transition,

```text
z = z_initial + B x_initial + R x'
  = z_initial + B x' + R x'       (because B C = 0)
  = z_initial + B' x'.
```

The final three lines therefore add exactly `B' x'` to `y2` and return `z` to
`z_initial`. This proves the complete target map for every entry state. Each
line is a reversible XOR shear; reversing their order gives the inverse.

## Restored-call baseline

The reference schedule treats each map as a separate complete call that returns
the dirty connector to its entry value. For a map `M` and output `y`, its
paired readout/restoration is

```text
y += z
z += M x
y += z
z += M x
```

The first three operations add `M x` to `y`; the fourth restores `z` because
the field has characteristic two. Run this with `M=B` for `y1`, mutate `x`
with `C u`, then run it with `M=B'` for `y2`. It implements the same target
map and closes the connector between calls.

## Fully charged local invoice

The model is the direct matrix-entry XOR alphabet: an update `v += M w` is
charged `wt(M)` scalar ADDs, with no free row sharing. This is a literal
instruction count, not an assertion that the matrices need that many gates in
an unrestricted linear-circuit model.

The weights are

```text
wt(B)  = n^2
wt(B') = n^2 - 1
wt(R)  = 1
wt(I)  = n
wt(C)  = 2.
```

Both schedules pay four output readouts (`4n`) and the same source update
(`2`). The restored-call baseline pays two `B` updates and two `B'` updates:

```text
baseline = 2 wt(B) + 2 wt(B') + 4 wt(I) + wt(C)
         = 4 n^2 + 4 n.
```

The paired schedule pays one `B`, one `B'`, and the rank-one transition `R`:

```text
paired = wt(B) + wt(B') + wt(R) + 4 wt(I) + wt(C)
       = 2 n^2 + 4 n + 2.
```

Thus it saves `2 n^2 - 2` direct scalar updates, positive for every `n >= 2`.
At `n=4` the weights are `16,15,1,4,2` and the complete bills are `80` and
`50`, respectively.

Within the declared direct row-add alphabet, this is the best rank-one delta
for `B=J_n` subject to `R C != 0`. Write `R=u v^T`. Then `v^T C=1`, so `R` is
nonzero and has at least one nonzero entry. Every one of its entries flips a
one of `J_n` to zero, so `wt(B')=n^2-wt(R)`. The saved bill is
`wt(B)+wt(B')-wt(R)=2n^2-2wt(R) <= 2n^2-2`, attained by `R=E_00`. This is an
entry-count optimum in this fixed family, not an optimum over all linear
circuits or connector schedules.

## Explicit parity-factor circuit

Because `B=J_n` is rank one, the coefficient-entry schedule is not the best
implementation of the two fixed maps. The following concrete XOR circuit
charges that common structure and gives a stronger comparison. It has one
clean scalar scratch bit `t=0` at pair entry and restores `t=0` at pair exit.
Let `s = sum_j x_j mod 2`; compute it by `t += x_j` for all `j`, fan it out by
`z_i += t` for all `i`, and uncompute it by the same `n` source additions.
For `B' x`, add the one extra update `z_0 += x_0`.

The paired program computes `s` before the first readout and leaves `t=s`
across the source update. Since `C=e_0+e_1`, the update changes two source bits
and preserves `s`. It then applies the single correction `z_0 += x'_0`, reads
the second output, removes `B'x'` using the same `t` and `x'_0`, and uncomputes
`t` against `x'`. The connector and scratch both return to their entry values.

```text
y1 += z
for j = 0..n-1: t += x_j       # t = parity(x)
for i = 0..n-1: z_i += t       # z += Bx
y1 += z
x_0 += u; x_1 += u             # x becomes x'
z_0 += x'_0                    # z += R x'
y2 += z
for i = 0..n-1: z_i += t       # z += Bx' (same parity)
z_0 += x'_0                    # z += R x'; closes z
y2 += z
for j = 0..n-1: t += x'_j      # t returns to zero
```

For a stronger baseline, permit the same `t` to persist across the pair while
restoring `z` after each output call. It applies `B` twice and `B'` twice,
using `t` for each update; the same additive source change preserves `t`.
Its exact order is:

```text
y1 += z
for j = 0..n-1: t += x_j
for i = 0..n-1: z_i += t
y1 += z
for i = 0..n-1: z_i += t      # restore z after first call
x_0 += u; x_1 += u
y2 += z
for i = 0..n-1: z_i += t
z_0 += x'_0
y2 += z
for i = 0..n-1: z_i += t      # restore z after second call
z_0 += x'_0
for j = 0..n-1: t += x'_j     # restore t
```

The exact gate counts are:

```text
pair, connector closed after each call but parity scratch shared: 10n + 4 + p_t
rank-one connector transition:                                  8n + 4 + p_t
saving against this stronger baseline:                                2n

strict independent calls, t also restored between calls:        12n + 4 + p_t
saving against strict independent calls:                             4n
```

`p_t` is the one-time complete cost of supplying and releasing the clean
scratch bit. It is charged once in both schedules and cancels. Every parity
compute/uncompute, fanout XOR, map-delta update, source update, and output
readout is included. The second baseline is deliberately stronger: it already
shares a hidden parity state while still paying to close and reopen the
connector. At `n=4`, its invoice is `44 + p_t`; the paired invoice is
`36 + p_t`, saving eight scalar ADDs. The strict independent-call comparison
is `52 + p_t` to `36 + p_t`.

The same construction works for every nonzero even-weight source-update vector
`c` and any coordinate `j` with `c_j=1`: take `C=c`, choose any output
coordinate `i`, and let `R=E_(i,j)`. Then `J_n C=0`, `R C=e_i`, parity is
preserved by the source update, and the connector patch is the single gate
`z_i += x'_j`. The second map evaluation is the parity fanout plus
`z_i += x'_j`. Writing `k=wt(C)`, the stronger connector-restored baseline and
paired bills are respectively `10n+2+k+p_t` and `8n+2+k+p_t`; the saving is
still `2n`. Strict independent calls cost `12n+2+k+p_t`. This generalization
is proved by the same equations; the executable exhaustive family check uses
the canonical `C=e_0+e_1, R=E_00` representative.

In a typed complete-call model, leave the call tariffs explicit. Let
`c_patch` price the complete correction `R x' + B1 C u`, including any
composition/setup needed to form its coefficients. If `c_B1`, `c_B2`, and
`c_patch` include all source/coefficient access, child work, scratch,
restoration, routing, dispatch and hosting for those respective operations,
then the paired schedule saves

```text
c_B1 + c_B2 - c_patch - Delta_I,
```

where `Delta_I` is the paired schedule's additional admission/preparation and
interface cost relative to two restored calls. It helps exactly when this is
positive. In the demonstrated family `B1 C=0`, so `c_patch=c_R`. The local
factored circuit's one clean bit is part of the pair-level interface and its
complete supply/release cost `p_t` is included equally in both schedules. The
remaining `Delta_I` is zero in this declared register model: the same source
update and four readouts occur in both schedules, and the only schedule change
is the stated connector transition. A real supplier that requires extra
copies, frame changes, routing, host work, child preparation or interface
transitions must add those expenses to `c_patch` or `Delta_I`; none is claimed
here.

This local construction does not identify a selected supplier schedule or
tariff, so the inequality is not evaluated against the selected recursive
moment and gives no `kappa` improvement.
