# Separate decoder reductions

These identities are follow-through from the controller review. They
give exact content inverses and identify specific query inputs. They
do not give a native decoder or a recursive invoice. In particular,
they do not convert a retired hole-frame array to a full-frame array
at no cost.

## Raw controller: one fresh retired query in each reverse step

Use the notation of the raw review. Undo the final ordinary X triangle
to obtain w_i. The other final outputs are f_i, d_i=Q a_i, and r_i.
Recover a_i=q d_i in content coordinates. Set z_m=0 and process the
pairs in reverse order. Let delta be zero for corrected F and one for
raw F. Define

```text
k_i = w_i+z_(i+1),
t_i = B_ti k_i,
e_i = t_i+delta a_i,
p_i = B_si r_i-B_si k_i+B_si D_ti e_i,
beta_i = f_i+q t_i-p_i,
v_i = r_i-k_i+D_ti e_i,
z_i = w_i+v_i+D_si beta_i-D_si Q a_i,
b_i = Q beta_i.
```

The forward local implies `v_i=r_i-k_i+D_ti e_i`, so p_i=B_si v_i.
The selected output then gives beta_i=q b_i. The backward ordinary
output gives the stated z_i. These are direct substitutions; no odd
division or stage commutation is used. They prove the reverse induction.

At the end, recover the original inputs by

```text
x_i = z_i+z_(i+1),
y_0 = v_0-z_0,
y_i = v_i+v_(i-1)-r_(i-1),   i>0,
b_0^0 = b_0-a_0,
b_i^0 = b_i,                 i>0.
```

At each reverse step, the only query in these formulas that directly
reads the current retired ordinary bank is B_si r_i. The query t_i
reads w_i plus the already recovered next suffix. The remaining terms
use the two selected query values and small cross-stage products.
This is an exact reduction to one fresh rank-eight retired-Y query per
pair, provided the next suffix and the resulting ordinary updates are
available in the needed views.

Those conditions are not proved here. The retired r_i is in the target
hole frames. Its query is in the old s_i chart, whereas the retirement
was at t_i. Also, the updated z_i must be used by the previous reverse
step. The identity does not provide this frame transfer. Calling every
term a rank-eight correction does not price its ordinary scatter.

For the restricted original-X-zero map, this query has a precise
information role. Completed X determines w_i and
`h_i=f_i+q B_ti w_i`. One additional echo B_si r_i gives
`B_si v_i=B_si r_i-B_si(I-D_ti B_ti)w_i`. It then gives b_i and v_i,
and hence all original Y. This is a sufficient selected-dimension
observation per pair for that restricted problem. The mod-3 nullity
bound in the review is not a native price for this observation.

## Weighted controller: two small query factors for the ordinary inverse

The weighted retirement satisfies

```text
r_i-C_ti a_i = H_ti H_si^-1 (x_i-C_si Q a_i).
```

It follows that

```text
x_i = H_si H_ti^-1 (r_i-C_ti a_i)+C_si Q a_i.             (1)
```

This is an ordered two-factor inverse. It is not a high-degree
polynomial inverse. After (1), form the original suffixes z_i and set

```text
eta_i = K_si z_i-K_si C_si Q a_i-w_i.
```

The original y values follow from the same Y-bridge inverse:
`y_0=eta_0-z_0` and
`y_i=eta_i+eta_(i-1)-r_(i-1)` for i>0. For the postupper variant,
write `g_i=Q f_i-L_ti w_i`. Then

```text
b_i = g_i+Q L_si K_si z_i+Q T_si Q a_i
      -R_ti a_i-L_ti K_si z_(i+1).
```

Subtract a_0 from b_0 to undo the first full F0. This gives a complete
content inverse. The checker also verifies the version without the
postupper.

For the actual five-minor split, write
`H_j=I-M_j N_j`, with M_j the ordinary restriction of the injection and
N_j the ordinary query. The actual matrix has N_j M_j=9I. Hence
`H_j^-1=I-M_j N_j/8`. Let `r'=r_i-C_ti a_i`. Equation (1) can be evaluated
as

```text
q_t = N_ti r',
v = r'-M_ti q_t/8,
q_s = N_si v,
x_i = v-M_si q_s+C_si Q a_i.
```

The two queries each have eight output fields, even though the selected
bank has forty fields. The difference `H_si H_ti^-1-I` has image in
the sum of the two eight-field injection images. Its rank is therefore
at most sixteen fields. This bound does not identify a cheap physical
scatter into the 72 ordinary target fields.

`check_decoder.py` reads the actual R from the new-core interface. It
checks the five selected minors, the ordinary Gram matrix, and both
orders of the 72-dimensional H inverse with integer numerator matrices.
Thus the five-minor specialization is tied to the actual source matrix,
not only to a formal rank-eight model.

## Why completed X alone supplies no clean weighted query

The weighted postupper output does not supply an additional clean query
of original ordinary X from its completed X bank alone. To see this,
fix original X. Undo the final ordinary triangle. The original-Y part
of w_i is `-eta_i`, and the eta recurrence is unit lower triangular in
the original y inputs because r_i is independent of original Y.
Normalize selected X to g_i. Its original-Y part is exactly b_i.
Thus the map from all original Y to all completed X is a unit.

For a fixed original X, completed X can therefore take every value as
original Y varies. A linear observation of completed X that removes
all arbitrary original-Y dependence must be zero. In fact, the same
surjectivity statement prevents any function of completed X alone
from giving a nonconstant, baseline-independent query of original X.
The productive selected outputs add the known a_i, but do not add a
query of the ordinary original X.

This is a restricted observation statement. A decoder can read ordinary
retired Y, change the controller, use related rather than independent
input roles, or retain an additional record. The two query factors in
(1) are the specific remaining access task for this unchanged endpoint.
The statement is not a general lower bound on native work.

## Verification and scope

Run from the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/controller-review-20261017/check_decoder.py
```

Expected output:

```text
PASS_CONTENT_DECODER_REDUCTIONS_ONLY
```

The checker uses the separate reverse controller engine in this review
directory, not a producer engine. It verifies all original input blocks
after the displayed inverse for m=1 through 8, both raw F choices, and
both weighted postupper choices. It uses exact ordered words. The
actual Gram and inverse check uses exact integers. No physical native
word, global owner path, storage schedule, or complete cost was emitted.
No kappa improvement follows from this packet.
