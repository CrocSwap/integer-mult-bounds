# A weighted raw controller with an invertible ordinary block

This theorem gives the exact ordered content map for raw selected
exchanges when the ordinary block of the local core is a unit. It covers
the five-minor selected set, and any other split with the stated unit
condition. It includes the selected self-block term in the forward call.
The theorem does not require Q to commute with a matrix block.

## Local blocks

Split the core matrix at stage j as

```text
J_j = [[R_j,L_j],[C_j,H_j]],     K_j=H_j^-1.
```

Let Q be the selected diagonal native operator and let `q=Q^-1`.
The selected physical exchange, followed by the clean backward core and
then K_s on completed ordinary X, gives

```text
h = q b-R_s Q a-L_s v,
w = K_s u-v-K_s C_s Q a,
d = Q a,
r = v.
```

Here `(a,u;b,v)` are the local input contents. A further upper operation
`h-=L_s w` gives

```text
h = q b-L_s K_s u-T_s Q a,       T_s=R_s-L_s K_s C_s.
```

The dependence on borrowed input Y is then diagonal: selected X has
coefficient q on b, and ordinary X has coefficient -I on v. All other
terms depend only on original X. This upper operation is useful because
it removes the ordinary borrowed baseline from selected X.

At stage t, first apply H_t to ordinary Y. Use the physical selected
exchange, the clean forward core, and the second physical selected
exchange. For input `(h,k;d,v)` the resulting map is

```text
X_A = h+q R_t q d+q L_t k,
X_U = k,
Y_A = d,
Y_U = H_t v+C_t q d+H_t k.
```

The term `q R_t q d` must be retained. It vanishes for the old single
minor split, but it is present for a selected set with multiple minors.

## Complete content controller

Use m pairs. Let `s_i=2i+1` and `t_i=2i+2`. Write the original data as
`(a_i,x_i;b_i^0,y_i)`. Form only the ordinary X suffix
`z_i=x_i-z_(i+1)`, with `z_m=0`. Use the original full first forward
shear, so `b_0=b_0^0+a_0`, `eta_0=y_0+z_0`, and `b_i=b_i^0` for i>0.

For each pair, run the balanced backward word. The optional postupper is
either present at every pair or absent. If a next pair exists, apply K_s
to its idle ordinary X, add that value to active ordinary X, and subtract
active ordinary Y from next idle ordinary Y. Run the balanced forward
word. Subtract the same idle ordinary X, add retired ordinary Y to next
idle ordinary Y, and then reset idle ordinary X by H_s. At the end use
the descending ordinary X triangle.

The preparation and reset of idle X are actual operations. This note
does not infer their native legality from their content matrices.

Define

```text
c_i = -K_si C_si Q a_i,
w_i = K_si z_i-eta_i+c_i,
k_i = w_i+K_si z_(i+1),
E_i = H_ti K_si,
r_i = E_i x_i+H_ti c_i+C_ti a_i,
eta_(i+1) = y_(i+1)-eta_i+r_i.
```

Retired selected Y is `Q a_i`. Retired ordinary Y is `r_i`. Before the
last ordinary triangle, completed ordinary X is `w_i`. After that
triangle its value is

```text
Z_0 = -y_0+(K_s0-I)z_0+c_0,
Z_i = -y_i+K_si z_i+K_s(i-1)z_(i-1)-r_(i-1)+c_i+c_(i-1), i>0.
```

The selected X endpoint without the optional postupper is

```text
f_i = q b_i-R_si Q a_i-L_si eta_i+q R_ti a_i+q L_ti k_i.
```

With the postupper it is

```text
f_i = q b_i-L_si K_si z_i-T_si Q a_i+q R_ti a_i+q L_ti k_i.
```

These identities follow by substitution into the local maps. In the
ordinary retirement, `eta_i+k_i=K_si x_i+c_i`; this cancels the borrowed
baseline. In the final ordinary X formula, substitute the Y bridge into
`w_i+w_(i-1)`. The descending tail is required so that it uses the old
`w_(i-1)`. No relation between different stage matrices is needed.

## A selected decoder reduction

Suppose the postupper is present. Completed ordinary X gives every w_i
by inversion of its final triangle. One positive selected Q operation,
followed by a full-frame scalar subtraction, gives

```text
g_i = Q f_i-L_ti w_i
    = b_i-Q L_si K_si z_i-Q T_si Q a_i
      +R_ti a_i+L_ti K_si z_(i+1).
```

Thus g_i differs from the original selected borrowed input only by a
function of original X. There is no remaining eta_i term. The first
pair also has the stated `+a_0` from the first full forward call. This
reduction is exact, but it is not a complete decoder: the original
ordinary suffixes in the response are not yet supplied in a usable
physical frame.

The ordinary retired code has invertible block `E_i=H_ti H_si^-1` and
an explicit selected-input response. Original selected X is present in
productive selected outputs. These properties remove two algebraic
obstacles from the single-minor raw code. They do not by themselves
prove that E_i can be removed within the native budget. In particular,
normalizing all ordinary retired Y to full fields and then restoring
their required hole frames generally incurs two native operations per
ordinary field. Such a decoder must be priced in full.

## Verification and scope

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/check_weighted_raw_controller.py
```

Expected output:

```text
PASS_WEIGHTED_RAW_CONTROLLER
```

The checker uses formal ordered words with only Q inverse cancellation
and `H_jK_j=K_jH_j=I`. It checks all endpoint blocks and active ordinary
cuts for one through six pairs, with and without the postupper. It also
checks the selected normalization formula. The negative controls omit
the selected self-block term and reset idle X too early. This is a
content proof. It is not a native phase, owner, finite precision, or
complete recursive cost proof. Independent review remains required.

The weighted recurrence was derived by the upstream-refresh lane. The
balanced local words and their scalar implementation are from the
native-escape and new-core-transfer lanes. The coordinating lane proposed
the five-minor split. This note adds the ordered selected endpoint and
checks the full event order. This work used AI assistance. No publication
is authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
