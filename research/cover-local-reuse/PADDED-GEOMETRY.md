# Padded cover with completed groups of three

This construction retains the audited physical local word, its compensated reuse,
and every scalar operation. It changes the ambient space, auxiliary allocation,
and final auxiliary/data transformations. Each local core finishes before the next
core uses its scratch bank.

## Cover and paid data endings

Start with the inherited spaces `A`, `B`, `C` of dimensions 24, 23, 23 and add an
orthogonal two-dimensional space `D`. Write `E0 = A + B + C` and `E = E0 + D`, so
`dim E = 72`. The inherited port involutions `R12,S` and `R23,S` act identically on
`D`; use the full finite group `G = O(E)`. Its order and the resulting wire stock
remain in the finite scalar/router and assembly charges.

For every actual triple port, the three local data segments have exactly their
inherited frames inside `g E0`. At the end of stage three, the first data bank has
frame `g E0` and the second has frame `g(E0 intersect q-perp)`. Their final frames
are `E` and `(g q)-perp`. Each extension has dimension two and therefore costs one
width-two child. Both data banks pay this cost: `2v` children per vertex, or `6v`
per three-vertex accounting cell.

The exact endpoints may be chosen as `(F_E0, F_E0 T_q^-1)` before finishing. Apply
`F_total F_E0^-1` to each bank. The exact operators then become
`(F_total, F_total T_q^-1)`. The original input Pauli correction, sign and bank
exchange still produce two copies of `F_total`. This argument uses an exact
operator ratio and its checked rank; it does not equate arbitrary lifts merely
because their binary symplectic matrices agree.

## Sequential sharing in every stage

Let `tau` cycle the three coordinate blocks of size 24. It is orthogonal and has
order three. Right cosets of `<tau>` partition every stage's invocation set into
three distinct vertices `k`, `k tau`, `k tau^2`; their active spaces are mutually
orthogonal and cover `E`. Each stage allocates a separate bank of `R` physical
roles per coset. Within a coset, run all three cores to completion in a fixed
order. Data positions remain distinct within a stage, as in the inherited cover.

A completed local core accepts arbitrary physical dirty scratch. Its transparent
scalar word cancels all scratch contributions to the data and restores the
logical scratch; its prescribed physical residual need not be the identity.
For entrance gauge `T_sigma`, a forward core's residual is

`P = F_active T_sigma^-1`.

The middle reversed core has residual `P^-1 = T_sigma F_active^-1`. The common
stage offset is orthogonal to that core's active space. It commutes with both
active operators and cancels from the completed residual:

- Forward entrance/exit: `F_offset T_sigma`, `F_offset F_active`.
- Reversed entrance/exit: `F_offset`, `F_offset T_sigma F_active^-1`.

An offset may intersect another core's active space. That does not obstruct the
sequential construction: the next complete core accepts the arbitrary physical
scratch left by its predecessor. No residual is moved through an unfinished
scalar gate, and the internal scalar operations of different cores are never
merged.

For one physical role, let the three completed residuals in a stage be
`R1`, `R2`, `R3`. Define its final transformation by the exact operator equation

`Tail = F_total (R3 R2 R1)^-1`.

Then `Tail R3 R2 R1 = F_total`, including the exact phases. The three residuals
act on separate tensor factors. Applying the inherited general Clifford rank
formula to each factor gives tail rank `3 dim(sigma)` in both forward and reversed
stages. This includes degenerate source gauges. The checker constructs the
binary symplectic operators for every physical source-frame type and checks this
rank independently in all three stages.

A zero-width tail is still a physical rank-zero Clifford adapter: a fixed binary
address permutation with unit quadratic phases. It is excluded only from the
positive-width recursive-child multiset. The outer certificate adds the explicit conservative supplemental charge
`32 (m+1)^3 (|G| R + 2 |G| v)` for the completed auxiliary tails and both data
endings per vertex. It recomputes the entire semantic guard after adding this
charge. The inherited local and finite-router reserves remain paid as well.

## Complete paid profile

Let `H` be the complete one-invocation local histogram after removing only the
old two-stage bridges, endpoint copies and old exteriors. It includes source and
target movements, physical auxiliary transitions and copied-center children.
Let `s_d` count actual physical roles whose source gauge has dimension `d`.
For a three-vertex accounting cell, all three stages contribute:

- Nine unchanged copies of `H`.
- `3 s_d` final auxiliary children of width `3d`, omitting only width-zero
  recursive children while retaining their physical adapters.
- `6v` data-ending children of width two.

The persistent stock is `W_cell = 6v + 3R`. For the frozen audited supplier,
`v = 2024`, `R = 26597`, so `W_cell = 91935`, rank mass is `6612144`, deficit is
`7176`, and the largest child has width `66 < 72`. The deficit is exactly
`3(2v - 3 ell)` with `ell = 552`; the two new data dimensions are fully paid.

`padded_checks.py` checks every physical source-frame type, every one of the 2024
actual ports, every stage's offset and orientation, the three-cycle partition,
the complete histogram and controls rejecting omitted data endings or residuals.
These finite checks retain the inherited all-size Clifford, scalar transparency,
weighted-bit, fixed-tape and analytic interfaces as explicit dependencies.
