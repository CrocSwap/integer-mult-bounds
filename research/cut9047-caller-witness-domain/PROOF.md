# Caller-domain admissibility at cut 9047

No new κ. The selected record stays `781451/250000000`. This note does not
replay the native word. It uses the coframed rows already recorded by
#5546 and the entrance program already recorded by #5402.

## Entrance

The #5413 caller runs `PROVIDER_5402` before the native word. On this word
that schedule is: multiply each mode owner by 2, run the 834-instruction
`input_basis_program`, then execute the word. The same `PROVIDER.json` bytes
are the capsule input of `research/selected-caller-exact-grid`.

Owners `0..223` are mains. Owners `224..631` are helpers. The basis mixes
122 helpers, `basis_roles`. The eight mode owners are

```text
224, 225, 227, 229, 240, 241, 256, 257.
```

Each mode input is also multiplied by the monomial `Km` before the basis.
`Km` is a `D`/`P`/`X`/phase word. It is not an empty native warp word, so it
is not one of the keys in the #5546 row table. The two readings below differ
only in whether that monomial is collapsed to a rational owner coefficient.

The published coframed rows, with every warp word empty, are

| Row | Terms |
| --- | --- |
| L19 | `L19` |
| L300 | `L19 + (1/2)L293 - L298 + L300 + (1/4)L505` |
| L301 | `L19 - L226 - (1/2)L288 + (1/2)L293 + (1/2)L296 - L298 + L301 - (1/2)L302 + L303` |

#5546 shows that `(L300=u, L505=-4u)` and `(L301=u, L226=u)`, with every
other native input fixed, preserve these three rows and move the corresponding
pure coordinate by `u`.

## Owner-rational reading

Ignore the operator content of `Km` and keep only the scalar 2. The resulting
map on the 122 basis owners has rank 122, so it is bijective, and it is the
identity on every other owner. Both published native witnesses are therefore
entrance states:

- public `(L300=u, L240=-u/2, L505=-4u)`, every other public input 0, arrives
  as native `(L300=u, L505=-4u)`;
- public `(L301=u, L226=u)` arrives unchanged.

`L240` is a mode owner. `L226`, `L301` and `L505` are helpers outside the
basis. In this reading the published separators transfer verbatim, because
their native images are exactly the witnesses #5546 already checked.

## Empty-warp reading

Hold every mode input at 0, so no `Km` key is present. Public inputs are then
bare helper atoms. On those atoms the basis sends public `L300` to native
`L300` with coefficient 1, and it also writes that same atom into other native
helpers. The coframed row L301 reads four of them:

```text
L288 = -u/4,  L296 = u/4,  L302 = u/4,  L303 = -u/2.
```

Their L301 coefficients give

```text
(-1/2)(-1/4) + (1/2)(1/4) + (-1/2)(1/4) + (1)(-1/2) = -3/8.
```

So the verbatim public pair `(L300=u, L505=-4u)` still kills rows L19 and
L300, and still moves native `L300` by `u`, but it moves row L301 by `-3u/8`.
It is not a separator in this sector. No other bare public atom reaches native
`L300`, so the leak cannot be removed while keeping native `L300 = u` and
every mode input at 0, except by cancelling it downstream in the row.

`L226` is outside the basis, and row L301 has coefficient `-1` on it. Public

```text
(L300=u, L505=-4u, L226=-3u/8),
```

with every mode input and every other public input 0, adds `+3u/8` to row
L301 and does not meet rows L19 or L300. All three rows stay fixed, and native
`L300` still moves by `u`.

`L301` and `L226` are both outside the basis and outside the mode set, so the
published pair `(L301=u, L226=u)` is already an empty-warp entrance state.
It fixes the three rows and moves native `L301` by `u`.

Thus both pure coordinates remain separated by legal empty-warp inputs. The
obstruction transfers. The extra `L226` term is a correction of the witness,
not a new prefix, basis, or anchor.

## What this does not say

A nonzero `Km` input is a different formal key. This package does not replay
those keys through events `0..9047`, so it does not claim they stay out of the
empty-warp sector at the cut. The witnesses above set those inputs to zero.
Mains, including `L19`, stay fixed. No paid-profile change, new helper
inventory, or selected-record update is claimed.
