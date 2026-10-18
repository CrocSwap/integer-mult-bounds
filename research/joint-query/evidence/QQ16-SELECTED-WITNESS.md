# A selected-output witness for the conserved QQ16 pair

The conserved QQ16 pair needs one more source observation before its
selected inputs can be restored. This statement holds even if all five
forward query values are supplied without cost. It concerns the fixed
F0 and B1 maps and the retained ordinary bank program. It does not
exclude a change to those maps, a later ordinary-to-selected read,
an affine helper state, or a paid query operation.

Use the A, T, and U96 sets from QQ16-CONSERVED-CONTROLLER.md. Write
B_s=R_s iota_U. The actual columns give

```text
B_s B_s* = 48 I
```

where * reverses the cover route and transposes the real coefficient.
Every port column has squared norm four. Let e be the first centre
coordinate at the identity element of the regular cover, and set

```text
h = (48 I - B1* B1) B2* e.
```

This is an integer vector of finite support in the regular cover. The
same-stage Gram identity gives B1 h=0. For distinct actual stage-1 and
stage-2 routes, only equal port indices contribute to the identity
coefficient in B2 B1* B1 B2*. Therefore the first coordinate of B2 h
has identity coefficient

```text
48^2 - 4*48 = 2112.
```

In particular B2 h is not zero. No division by 3, 11, or 13 occurs in
the witness. The checker verifies the exact 96 route labels and the
coefficient count. It does not enumerate the full regular cover.

## Arbitrary input and its exact trajectory

Set all banks except pair 0 to zero. In pair 0 use

```text
X_U = h,                 Y_U = 0
X_A = -P_0,A B0 h - P_2,A B2 h
Y_A = -X_A
X_T = P_0,T ell_0,A P_2,A B2 h
Y_T = -X_T.
```

Both selected pair sums are zero. All factors P and ell are the actual
selected route maps. Each is a dyadic unit between its eight selected
coordinates and the query coordinates. Thus X_T is not zero.

At F0, the full source query is zero. Its output is

```text
X_U = h,                 Y_U = h
X_A = P_2,A B2 h,        Y_A = -P_2,A B2 h
X_T = 0,                 Y_T = 0.
```

At B1, the future query is

```text
q2 = R2 Y = B2 h - B2 h = 0.
```

The future query code E2 removes the selected A value. Its source u is
(h,0,0), so b1=B1 h=0. The old X_T driver a1 is zero. The output
after B1 is therefore exactly

```text
Y_0,U = h,
all other ordinary and selected fields = 0.
```

The positive ordinary bridge (0,1) places -h in Y_1,U. F2 has a zero
X source and changes no field. The negative bridge removes that -h.
Every later active ordinary pair is zero. The last three ordinary
bridges leave Y_0,U=h and all other ordinary fields zero. The terminal
moves h to final X_0,U. This is a former Y field with the phased native
output type. Every completed-X descendant is zero.

All selected registers are zero after B1. Consequently, any subsequent
homogeneous linear operation that reads and writes selected registers
only keeps them zero. This includes arbitrary cross-bank, port, and
cover maps, and any selected terminal. The assertion does not permit a
selected operation to read an ordinary bank. The later local calls also
have zero active inputs in the retained ordinary schedule. Thus the
trajectory holds for every such later selected controller, not only
for the first-six-swap choice in the frozen recurrence.

All five forward queries f0,f2,f4,f6,f8 are zero. The complete observation
set consisting of all selected outputs, all completed-X descendants,
and all five forward query histories is therefore zero. The initial
X_0,T is nonzero. No linear decoder from only those observations can
restore that input. This remains true over the rational numbers.

The actual missing information includes B2 h. The initial A correction
also contains B0 h. This result does not make either query expensive by
itself. It identifies an actual required source read or an earlier
change in the content controller.

## Check

Run from the workspace root:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/encoded-controller/check_qq16_selected_witness.py
```

Expected output:

```text
PASS_QQ16_INTEGER_SELECTED_WITNESS
```

The checker pins the actual R, route evidence, and schedule. It checks
the actual Grams, all 96 route distinctions for stages 1 and 2, all
eight identity coefficients, and the ordinary trajectory after B1.
The ordered selected identities above use only the two-sided selected
inverse relations. An independent review must keep the same observation
scope. No general native lower bound or supplier claim is made.
