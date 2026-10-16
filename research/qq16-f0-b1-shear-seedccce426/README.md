# QQ16 selected-state shear at the F0/B1 cut

This package tests one reversible data-map insertion between the retained
forward `F0` and backward `B1` calls. For each of the eight selected A/T
coordinate pairs it applies

```text
X_T <- X_T + X_A
Y_T <- Y_T - X_A
```

The map preserves every selected `X_T + Y_T` sum and is invertible. On the
exact eight-direction selected-input witness for the fixed QQ16 pair, the
zero-shear B1 T output is zero. With the shear, the post-B1 T output has rank
eight over the exact payload-constant regular-cover group algebra. The
verifier emits eight output coordinates with exact minor determinant
`-1/4096`.

This is a local interface mechanism. It resolves the cited witness at the
post-B1 cut; it does not show that the later controller tail keeps these
values, produce a complete controller, admit a supplier, or improve κ.

## Reproduce

From the repository root, with Python 3.10 or later and only the standard
library:

```sh
python3 -I -B research/qq16-f0-b1-shear-seedccce426/verify.py
```

Expected output:

```text
PASS_QQ16_F0_B1_IDENTITY_SHEAR_WITNESS
source_A_rank=8; zero_shear_T_rank=0; sheared_post_B1_T_rank=8
exact_nonzero_8x8_minor_det=-1/4096
```

The checker rebuilds the pinned QQ16 scalar matrix and all 73-bit owner
routes, constructs the eight `h_k` inputs from the exact group-algebra
formula, verifies `B1 h_k = 0` and the `2112 I` identity coefficient of
`B2 h_k`, then propagates both the control and sheared states through the
ordered B1 map. `RESULT.json` records an explicit nonsingular eight-row
minor, including its exact owner-map keys and rational coefficients.

## Local charge

At the common `completed(0)` data frame, the inserted map costs 16 scalar
additions per owner: eight writes into existing `X_T` fields and eight into
existing `Y_T` fields. It allocates no helper, changes no coefficient or
precision, and adds no recursive child or cover-map operation. The A source
is not overwritten; the A/T addresses are distinct; the inverse shear is
available by reversing the two signs. The operation preserves the selected
sums and leaves the inherited 480 ordinary helpers untouched.

This is the complete local data-map charge. The full controller, subsequent
tail behavior, and supplier cost are open, so these 16 additions are not a
κ claim or a complete supplier invoice.

## Open next questions

- Does the retained ordinary tail preserve the eight values revealed in the
  T output, or do later events erase them again? First step: propagate the
  exact sheared witness through the next frozen event and test the complete
  selected-output kernel. Blocker: the current package stops at B1.
- Can the shear be integrated into a full controller with its complete
  address, hosting, precision, and restoration bill? First step: derive the
  next ordered interface identity before pricing any longer word. Blocker:
  no full controller or supplier is supplied here.
