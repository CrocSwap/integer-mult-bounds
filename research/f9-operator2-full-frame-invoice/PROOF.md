# Invoice for the forward full-frame transport of F9 operator 2

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Contract

Use the backward word `F9-SOURCE-DAG-ALL8-WORD.json.gz` inside the unchanged
packet `research/filtered-native-kappa004/inputs/original-packet.tar.gz`.
Its SHA256 is

```text
934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775
```

Operator 2 has column list

```text
(1, 2, 4, 8, 128, 394, 165, 80, 78).
```

Its forward factor `K_G` is the permutation whose rows are

```text
(65, 290, 324, 296, 128, 64, 384, 112, 32),
```

followed by the diagonal whose quadratic rows and linear signs are

```text
(32, 336, 112, 336, 46, 501, 110, 288, 426),
(0, 0, 0, 0, 0, 1, 1, 0, 1).
```

Output bit `i` of a permutation is the parity of row `i` with the input.
These are the same `diagonal_data` rows the merged fixed-vector audit uses.

The priced circuit is the circuit in that audit's checker: the width-9
Fourier adjoint, then this forward `K_G`, then the Fourier. The checker calls
that circuit `F† K_G F`. Each Fourier factor is nine one-qubit `C` gates,
signs `+1` in qubit order `0..8`, and signs `-1` in reverse order for the
adjoint. Amplitudes are the exact states of
`research/active-mode-delivery-frontier/source/quadratic.py`, SHA256

```text
d406584aed1479b75c387bc964b9e797b2f4f75e5f8c6bbea00df07f7d590a91
```

The domain is finite: all 512 computational basis states of width 9, and
both finite programs of this word. The checker evaluates every state and
every event. This is an exhaustive census of that domain. It is not a
statement about the other seven classes, an arbitrary invertible matrix, or
a different word.

## The transport is one monomial

For a state `x` in `F_2^9`, write `q(x)` for the `Z_4` value

```text
q(x) = Σ_i α_i x_i + 2 Σ_i x_i popcount((Q_i >> (i+1)) & (x >> (i+1)))  (mod 4).
```

Let `M` be the linear map with rows

```text
(1, 2, 4, 8, 398, 85, 270, 16, 58),
```

and let `Q` and `α` be

```text
(85, 186, 213, 186, 111, 26, 21, 270, 384),
(3, 1, 1, 1, 2, 0, 0, 0, 3).
```

The census finds, at every one of the 512 inputs,

```text
T|x> = i^{q(x)} |Mx>,
```

with denominator 0. In particular `M0 = 0` and `q(0) = 0`, so
`<0|T|0> = 1`. That one entry is the fixed-vector fact already recorded for
this class. The invoice is the map `(M, q)`.

The same 512 images are reproduced by the two-gate circuit that applies the
diagonal `(Q, α)` and then the permutation `M`. On every input that circuit
has peak support rank 0. So the compiled transport is one diagonal and one
permutation, and it never leaves the computational basis.

The rows of `M` are the images of the nine basis vectors, rearranged as
matrix rows. The weight-2 polarization of `q` determines each upper entry of
`Q`, the diagonal bit of row `i` is `α_i mod 2`, and symmetry fills the
lower triangle. Any other bit in that symmetric representative changes `q`
on a weight-1 or weight-2 vector. The census then checks the resulting
formula on the remaining addresses.

## Frame change

The defining sandwich, on every one of the 512 basis inputs, records peak
support rank 9. Each Fourier factor alone has support rank 9 on `|0>`.
The output of `T` has support rank 0. The compiled diagonal-then-permutation
circuit has peak support rank 0 and the same 512 images.

These are two different numbers. The intermediate peak is the support the
Fourier factors open inside this particular circuit. The compiled support
rank is the support of the operator after those factors cancel. Neither
number is `<0|T|0>`.

## Restoration

Let `S` be the same sandwich with `K_G` replaced by its gate adjoint. On all
512 basis states, `S` is the inverse of `T`: addresses run backwards and
phase exponents change sign. The signed order of `T` is 10, so `T^2` is not
the identity and a second copy of `T` does not restore the basis. `S` is
itself a pure monomial, because it agrees with the inverse table of `T`.

## Target debit

`M + I` has rank 5, so its kernel has dimension 4 and 16 vectors. Those 16
vectors are exactly the addresses fixed by `M`, and `q` is 0 on each of
them. The identity operator agrees with `T` on those 16 addresses, including
0, and on no others. `T` moves the other 496 addresses. The phase histogram
on all 512 addresses is 144, 144, 112, 112 in exponents `0, 1, 2, 3`.

The matrix element `+1` at `|0>` is the address-0 member of that 16-element
set. It does not determine `M`, `q`, or the 496 moved addresses.

## One centre is a different unit

The inherited active-mode contract prices one removed centre job as one
`H8`, a rank-8 canonical transport. The compiled support rank of `T` is 0,
so this transport is not that charge and it does not implement a rank-8
frame delivery.

Both programs of the pinned word were read in full. Each has 0 events of
opcode `center` and no climb of rank 8. The climb histogram in each program
is `2201, 412, 510, 127, 40` at ranks `1` through `5`. The canonical
`local_profile` stores those five counts and also eight units at rank 8.
The profile entry and the climb list are different records. This census does
not retariff the profile entry, delete a centre, or change the selected
exponent `363005817/100000000000`.

Frame 1 is the unique frame of length 9. In each program the unique
width-9 warp of class 2 is opcode `-2` on `L250`, with both frames equal to
1. There is also one width-4 warp of class 2, opcode `+2`, from frame 292 to
frame 3941. The scalar replay tags an opcode sign and does not apply this
Clifford. The backward-sign sandwich, with the linear signs of `K_G` negated,
sends `|0>` to `|352>` with phase `i`. That is a different operator. This
invoice does not identify opcode `-2` with the forward circuit.

## Controls

Inserting a global factor `i` changes the phase of `|0>` from `+1` to `i`.
Deleting both Fourier factors changes the image of address 1. Operator 1's
forward sandwich sends `|0>` to address 48 with phase `-1`, the same image
the merged audit records for that class. The backward-sign sandwich of
operator 2 leaves `|0>`. The square of `T` is not the identity.

No caller, compiler, precision tape, or outer admission is claimed. The five
framework assumptions stay in force. The selected conditional value stays
`363005817/100000000000`.
