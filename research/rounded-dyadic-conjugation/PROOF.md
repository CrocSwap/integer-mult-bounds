# Rounded dyadic conjugation and a sharp root carry

This scoped proof concerns the two local replacements and the displayed B0
repair in Hanson Sun / bbMisk's PR1526. That work supplies the exact word and
its exact-arithmetic context. Its optimality theorem is a cited predecessor
result, not a claim re-established here.

## Rounded child contract

Fix a positive grid spacing h. All public real coordinates lie in hZ.
Complex arrays use this contract separately on their real and imaginary
coordinates. Coefficients and source products can be arbitrary real numbers.
Define the translation-equivariant nearest rounder

```
Q_h(t) = h floor(t/h + 1/2).
```

At a tie it chooses the larger grid point. A signed rounded query updates
its destination by `s Q_h(F(source))`, where s is +1 or -1. Its source and
other roles stay fixed. Rounding happens before applying the sign. The
literal inverse subtracts the identical rounded value. It does not evaluate
`Q_h(-F(source))`. The latter convention can fail at ties.

Within a halved-root interval the root uses the common h/2 grid. The scale
operations H and D divide and multiply the root by two exactly. This is a
specified additive child contract. A child with target-dependent errors,
inexact scaling or input-dependent precision needs a separate argument.

## The local theorem

Let v=Bx and let z be an arbitrary dirty root in hZ. Application order is
left to right. The refined source interval is

```
H; z += s Q_(h/2)(v); D
    z -> z + 2s Q_(h/2)(v) = z + s Q_h(2v).
```

The equality follows directly from the floor definition. Its error against
`z+2sv` has absolute value at most h/2 in every real coordinate. Two ordinary
rounded queries instead give `z+2s Q_h(v)`, with sharp error bound h.
Both bounds are attained: v=h/4 attains h/2 in the refined interval, and
v=h/2 attains h for the repeated interval. No hZ-valued endpoint can have
a uniform error below h/2, since the ideal increment can equal h/2. Thus the
refined endpoint is minimax optimal in that output lattice.

For the output query, linearity gives

```
D; y += s Q_h(Az); H
    (z,y) -> (z, y+s Q_h(2Az)).
```

It has the same sharp h/2 coordinate error without refining the output grid.
Both intervals have exact literal inverses under the stated sign rule.
They do not require zero dirty data.

For H B D, one extra fractional bit for the root is sufficient, and necessary
in the fixed common-grid representation of its initial exact H: H sends z=h
to h/2, which is absent from hZ. An equivalent residue flag also has two
possible classes modulo h. This necessity concerns representing this H,
not every possible implementation of the doubled query. The final H of
D A H acts on 2hZ and needs no finer fractional grid. Doubling can also
need one more magnitude bit. Neither storage nor either scan is free here.

## Local accuracy does not preserve the complete root boundary

Take the literal B0 repair displayed in PR1526:

```
B0- A1- H B0+ D A2+ B1+ A0+ B0- A2- B2- A1+ B1- A0- B2+
```

All ordinary B queries use Q_h; the B0 query between H and D uses Q_(h/2).
All A queries use Q_h and never change the root. Sources never change.
The first B0- is halved and then doubled, so its eventual root contribution
is -Q_h(v). The special B0+ contributes Q_h(2v). The later B0- contributes
-Q_h(v). B1 and B2 each cancel exactly. Therefore, for arbitrary linear
operators, source data and dirty root,

```
z_final = z_initial + rho_h(v),
rho_h(v) = Q_h(2v) - 2 Q_h(v),       v = B0 x0.
```

This is an exact endpoint formula for this rounded word. It makes no claim
that the rounded output rows equal their ideal linear values.

Set r=v-Q_h(v), so -h/2 <= r < h/2. Integer translation equivariance gives
rho_h(v)=Q_h(2r), hence

```
rho_h(v) = -h  if -h/2 <= r < -h/4,
            0  if -h/4 <= r <  h/4,
           +h  if  h/4 <= r <  h/2.
```

All three cases occur. For a tie-free counterexample choose h=1, B0=1/8,
x0=3 and z_initial=0. All public inputs are on the integer grid. Take the
other source values and all A maps to be zero. The refined word ends at
z=1, although its exact-arithmetic root boundary requires z=0. The signed
partner x0=-3 ends at z=-1. These examples also establish the sharp root
error h. They are errors of this newly specified rounded extension, not
errors in PR1526's exact-arithmetic theorem.

The refined word restores its dirty root exactly if and only if every real
coordinate has rho_h(B0x0)=0. Merely adding the one fractional bit does not
establish this condition.

## Two explicit ways to satisfy the root boundary

First, retain Q_h for the special B query, while retaining the h/2 root
representation for exact H. Then H B D is exactly the same rounded map as
two coarse B queries. The complete root restores for all inputs, but the
local error bound remains h. This option gives no local accuracy gain.

Second, use the refined query and append a root shear by -rho_h(B0x0)
after every output read. This restores the root and leaves the already
computed outputs fixed. Its inverse adds the same correction before the
literal inverse of the word. The correction has exactly three possible
values per real coordinate. Computing, delivering or retaining it requires
an explicit bill; no free correction or optimal implementation is claimed.
This is an algebraic repair of the root boundary only.

A coarse whole-target rounding is a different operation. With v=0, the
map `z -> 2 Q_h(z/2)` identifies z=-h and z=0 under the stated tie rule.
It loses arbitrary dirty information. It cannot replace the refined
additive child as a reversible exact H-B-D interval.

## Scope and evidence

The proof applies in every finite array dimension coordinatewise. The
verifier checks exact rational local intervals, the carry partition and
the full 15-event word with noncommuting two-coordinate matrix maps and
arbitrary dirty fixtures. It also multiplies literal inverse words.
Finite fixtures corroborate the implementation; the universal claim rests
on the equations above. A complete rounded connector output-error budget,
native child realization, physical correction bill, compiler admission,
precision/tape hosting and a new multiplication theorem remain open.

The new result was produced by Nick Petalas. Credit Hanson Sun / bbMisk
for PR1526, Ross Richardson for PR944, martinxxx9 for PR1088, and the
retained signed-connector lineage. Nearest-grid rounding and elementary
error transport are classical. Independent human and formal proof-kernel
review are unclaimed. Apache-2.0.
