# Exact witness calculation

## Frozen object and witness

The source and route model is the selected QQ16 package at the base pinned
in `SOURCES.json`. The inherited witness uses the actual sets

```text
A = [0, 7, 20, 27, 36, 46, 57, 111]
T = [21, 37, 47, 76, 81, 87, 92, 110]
U = the other 96 ports.
```

For each centre basis vector `e_k` at the identity owner, the checker builds

```text
h_k = (48 I - B1* B1) B2* e_k,       k=0,...,7.
```

`B_s` is the actual stage-s query restricted to U, including each port's
exact stage owner map. The checker works in the group algebra of the 73-bit
owner linear maps and uses rational coefficients. Payload translations are
omitted only because every payload block is held constant, as in the
predecessor witness. The exact checks give `B1 h_k = 0` and identity
coefficient `2112 e_k` in `B2 h_k` for all eight k. Applying the invertible
stage-2 A section gives an eight-dimensional vector `a_k=P_(2,A)B2 h_k`.

The ordered F0 witness state immediately before B1 is

```text
X_U = Y_U = h_k
X_A = a_k,  Y_A = -a_k
X_T = Y_T = 0.
```

At zero shear, the retained B1 word returns the erased selected output on
this family; the checker verifies that its T output is the zero group-ring
vector for every k.

## The changed interface

Insert the coordinatewise shear

```text
X_T <- X_T + X_A
Y_T <- Y_T - X_A.
```

For each T coordinate the change in `X_T+Y_T` is zero. The full map is
invertible, with inverse `X_T <- X_T-X_A`, `Y_T <- Y_T+X_A`; it uses no
scratch field. After the shear the B1 inputs have

```text
X_T = a_k,  Y_T = -a_k.
```

In the ordered B word, write `u=E_2 Y`, `a=ell_1 X`, and `b=R_1 u`. Its T
output is `P_(1,T)(b+12a)`. Thus the shear's exact effect is

```text
Delta X'_T = P_(1,T) (12 ell_1 - R_1 E_2) iota_T a_k,
```

where each term is evaluated with the pinned 73-bit owner routes. The
verifier propagates all eight `a_k` as sparse rational group-algebra
vectors. It finds 287,368 distinct owner-map labels in the T outputs and
extracts eight rows, indexed by T port and exact owner map, whose coefficient
matrix has determinant `-1/4096`. This proves the post-B1 T outputs are
linearly independent on the eight-dimensional witness family. The sparse
rows, route keys, and exact coefficients are in `RESULT.json`; the checker
recomputes them from the pinned source.

The zero-shear control has rank zero. The positive result is limited to this
fixed erased family and this post-F0 state shear. It does not prove that
subsequent events retain the output, restore every selected input, or form
a complete controller.

## Cost and remaining obligations

At the F0/B1 boundary all data fields use the common `completed(0)` frame.
The shear therefore uses same-owner scalar adds without changing an owner
map or a frame. Its exact local cost is 16 scalar additions per owner, zero
new helpers, zero new recursive children, zero new coefficient precision,
and zero temporary storage. It reads the existing A fields, writes existing
T fields, and preserves the logical selected sums. The ordinary helper
restoration contract is unchanged.

The route test establishes an exact interface effect, not a priced complete
supplier. Any integration must still propagate the state through the
remaining tail and prove final output/restoration for arbitrary inputs.
There is no new κ claim.
