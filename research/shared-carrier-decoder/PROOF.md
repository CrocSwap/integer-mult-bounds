# Physical word and composition proof

This proof concerns the finite module in `model.py`. The exact checks in
`verify.py` supply the finite identities used below. They are not a formal
proof of the integer-multiplication theorem.

## 1. The decoder

Let `r_i` be the 120 E8 root lines, with representatives of squared norm two.
The code stores `2 r_i` as integer vectors. Let

```text
f0=e0+e1, f1=e0-e1, f2=e2+e3, f3=e2-e3,
f4=e4+e5, f5=e4-e5, f6=e6+e7, f7=e6-e7,
beta=e0+e2=(f0+f1+f2+f3)/2.
```

Remove the eight `f_k` and `beta`. The remaining set has 111 lines. The
constructor obtains labels `u_i` in the standard dot-product space
`V=F2^9` and checks all 14400 identities

```text
u_i dot u_j = (<r_i,r_j> + 1) mod 2.
```

It constructs an orthonormal chart from the pairing matrix. No search result
or choice of a random seed is used. Every label has norm one. Put
`H_a = u_a^perp` and `E = span(u_f0)`.

The direct gather and scatter matrices are

```text
Q[k,i] = <f_k,r_i>,     D[t,k] = <r_t,f_k>/4.
```

Since the `f_k` are orthogonal and have squared norm two,
`D Q = G`, where `G[t,i]=<r_t,r_i>/2`.

Replace the first gather row with `Q'[0,i]=<beta,r_i>`. Keep the other seven
rows. Thus `Q'[0]=(Q[0]+Q[1]+Q[2]+Q[3])/2`. Use

```text
D'[t,0] = <r_t,f0>/2,
D'[t,j] = (<r_t,f_j>-<r_t,f0>)/4  for j=1,2,3,
D'[t,j] = <r_t,f_j>/4             for j=4,5,6,7.
```

Substitution gives `D' Q'=D Q=G`. The verifier checks every one of the
12321 entries with rational arithmetic. There are 444 nonzero direct gather
entries and 441 changed gather entries. The respective scatter counts are
444 and 507.

For each gather row with root normal `a`, its support labels lie in `H_a`.
The line `a` is removed, so each nonzero inner product is `+1` or `-1`.
The label identity then gives `u_i dot u_a=0`. The constructor also checks
that each support spans all eight dimensions of `H_a`.

## 2. The nonzero endpoint is last

The seven unchanged terms copy from `H_fk` to zero. The changed term copies
from `H_beta` to `E`. The product `<beta,f0>=1` gives `E subset H_beta`, so
this copy has rank `8-1=7`. Every direct copy has rank eight.

A target needs the changed term exactly when `<r_t,f0>` is nonzero. The line
`f0` is removed, so this product is `+1` or `-1`. The label identity gives
`E subset H_t`. There are 55 such targets.

Process all seven zero-endpoint copies first. Every target stays at zero
through those reads. For the last copy, move each of its 55 targets from zero
to `E`, read the copy, and then move it to its required sink `H_t`. The other
56 targets move directly from zero to `H_t`. These paths are nested. No
later operation needs a target back at zero.

The old-value compensation occurs before any target moves. It is therefore
legal for all eight terms at zero. Cleanup uses only sources, use helpers,
and centres at FULL. It does not use a target. The order thus works for every
target and for every compensation and restoration operation. The negative
control that puts the nonzero-endpoint copy first fails the common-frame
check on a later target read.

## 3. Scalar identity with arbitrary dirty helpers

There is one dirty use helper `h_ki` for each nonzero gather coefficient,
and one dirty centre `c_k` per term. Give each helper an independent initial
value. Both modules have the same stock of 452 helpers. The changed module
uses 449 of them and sends the other three directly from zero to FULL.

For each term, let `b_k=c_k+sum_i h_ki` denote its old combined value. The
literal chronological word has these eight stages:

1. Add all use helpers to their centres at zero.
2. Subtract `sum_k D[t,k] b_k` from each target at zero.
3. Subtract the same use helpers from their centres.
4. Add `Q[k,i] X_i` to each use helper at its source line.
5. Add all updated use helpers to their centres at `H_a`.
6. Copy each centre to its stated endpoint and add the required scatter terms.
7. At FULL, subtract all updated use helpers from their centres.
8. At FULL, subtract `Q[k,i] X_i` from each use helper.

Use `D',Q'` for the changed module. After stage five, centre `k` holds
`b_k+sum_i Q[k,i] X_i`. Stages two and six therefore add exactly `D Q X`
to the targets. Stage seven restores every centre to its independent initial
value. Stage eight restores every use helper. Sources never change their
logical value. The three inactive helpers never change their logical value.

This argument applies component by component to arbitrary complex vectors.
The sparse rational replay checks all 674 logical input columns. A second
interpreter propagates one integer column at a time with denominator four;
it obtains the expected Gram map directly from the roots. It does not use
the sparse row result as its expected value.

## 4. Exact native frames and the composition bridge

For a binary subspace `U`, use the retained exact operator
`T_U = clifford_exact.canonical_frame(9,U)`. Its source bytes are pinned in
SOURCES.json. In particular, `T_0=I` and `T_FULL=F=C^tensor9`. The preimage
Lagrangian is

```text
L_U = {(u,u+z): u in U, z in U^perp}.
```

The verifier applies each exact signed Pauli tableau to a basis of `L_U` and
checks that the image has zero X part. Both spaces have dimension nine.
The intersection formula gives

```text
d(L_U,L_W) = dim(U)+dim(W)-2 dim(U intersect W).
```

Use the following invariant at every event: a role whose logical vector is
`v` and whose frame is `U` contains exactly `T_U v` as its physical array.
It holds at the advertised input endpoints. Each event preserves it:

- **Move.** Apply the exact operator `A=T_W T_U^-1`. The array becomes
  `T_W v`. `lower_child(A)` emits two monomial adapters around one contiguous
  `C^tensorr` child, where `r=d(L_U,L_W)`. The verifier checks its rank, signed
  Pauli tableau, and exact image of the zero basis vector. Equality of the
  signed Pauli action gives equality up to a scalar; the zero-vector image
  fixes that scalar. A ratio that commutes with all Z operators is diagonal;
  commuting with all X operators makes its diagonal constant. Thus the check
  proves the exact operator identity,
  including phase, on every input vector.
- **Scalar add.** The two roles have the same exact `T_U`. A physical AXPY
  gives `T_U v + q T_U w = T_U(v+q w)`. No equal-frame change is assumed free:
  every role is constructed with the same canonical representative, and every
  actual change has its own emitted native adapters.
- **COPY begin.** Allocate one complete temporary stream and copy `T_U c`
  into it. Apply the paid child `T_W T_U^-1` to that copy. It now contains
  exactly `T_W c`. This child is in the same rank and adapter invoice as every
  original move. Its volume is the complete source volume, including control
  and spectator values.
- **COPY reads and disposal.** Each target is at `W`, so its AXPY has the same
  interpretation as above. The retained centre stays at `U` and is not changed
  during the lifetime of the copy. The replay checks this fact. After the last
  read, erase the temporary stream. Copies are sequential, so one temporary
  stream suffices. Allocation, reads, and erasure have separate paid entries.

Induction over the emitted word now connects the scalar identity to the
actual physical circuit. The result is not a scalar check followed by an
unrelated phase check: each scalar incidence and each COPY is bound to its
exact live frame and exact native transition by this invariant.

Let `S` be the scalar map from section 3. Let `A_in` and `A_out` be the block
sums of the exact input and output frame operators. The whole physical map is

```text
P = A_out S A_in^-1.
```

Both modules have identical `A_in` and `A_out`: sources enter at their lines
and leave at FULL; targets enter at zero and leave at `H_t`; every helper
enters at zero and leaves at FULL. A helper with initial physical vector `h`
therefore leaves with `F h`. The claim is logical restoration at FULL,
not physical identity on the helper array. External host charts or different
endpoint conventions would need their own charged adapters. This module does
not claim admission to the selected host.

## 5. Inverse transpose and the temporary stream

The package also executes `P^-T`. Use dual frames `R_U=T_U^-T`. Replace each
scalar shear `v_t += q v_s` by `v_s -= q v_t` in the same chronological order.
For a product of chronological shears, inverse transpose preserves this order.
The all-column replay checks the resulting map `X -= G^T Y`.

A move uses `(T_W T_U^-1)^-T`, so it carries `R_U v` to `R_W v`. For a COPY
block, start a zero temporary stream at `R_W`. Accumulate `-D[t,k]` times each
target into it. At the end, apply `(T_W T_U^-1)^T` and add the result once to
the retained centre at `R_U`. The identity

```text
(T_W T_U^-1)^T R_W = R_U
```

proves the required action. The copy transpose has the same Fourier rank.
Every target is constant during this dual copy block. The aggregate is thus
exactly the sum of the dual scalar shears. This orientation pays eight zero
scans and eight additional centre AXPYs in place of eight copy assignments.
It erases the same eight sequential temporary streams.

The verifier lowers and phase-checks every executed dual move and COPY. The
separate Gaussian-integer interpreter executes both orientations for both
modules and compares all final physical arrays with their stated operators.
The rank-seven COPY is also checked on all 512 basis columns.

## 6. Finite size and numerical scope

The exact replay uses 512 addresses per original role. It has no floating
point arithmetic. The maximum logical row L1 norms are 113 in both forward
words, 32 in the direct inverse transpose, and 105/2 in the changed inverse
transpose.

A C factor increases the maximum real or imaginary component by at most two.
An exact canonical frame and a lowered child each have at most nine C factors.
Converting an input source from its line frame costs a factor at most two.
A dual temporary sum can be bounded by the difference of two scalar prefixes,
which costs another factor two. A factor four covers scalar intermediates in
the pair formula. Thus `2^22 * 113 = 473956352` is a conservative finite
component prefix bound relative to the largest physical input component.
Permutations and unit phases do not increase that component norm.

This bound is deliberately loose. It does not supply a fixed-precision
implementation, an all-size rounding argument, or a tape admission theorem.
The written argument and its finite checks have not had independent human
review.
