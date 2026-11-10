# The F9 fixed-vector premise stops at K_G

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Contract

Use the backward word `F9-SOURCE-DAG-ALL8-WORD.json.gz` inside the unchanged
packet `research/filtered-native-kappa004/inputs/original-packet.tar.gz`.
Its SHA256 is

```text
934fea11e51f674ce2031b7d3127b994a921a9d83317b00359292752563a1775
```

This is the word named by PR5720. Its 72 canonical warp classes are the
operators below. Forward and backward program warp events use exactly these
72 operator ids.

PR5720, PR5745 and PR5823 evaluate native address operators on one common
fixed vector and then keep the rational field coefficient. In the scalar
observer this is implemented by leaving that coefficient unchanged when the
frame changes. The question audited here is whether that step is the matrix
element of the operator it names.

## The two operators

For a canonical column list `G_columns`, let `G` be its transpose and let
`K_G = P_G D_Q`. Here `P_G` is the linear permutation `x -> Gx`, and `D_Q`
is the diagonal Gaussian phase whose quadratic rows are

```text
Q_i = e_i XOR sum_j parity(c_i AND c_j) e_j,
```

with `c` the transpose of `G^{-1}` and with linear signs `alpha_i = (Q_i)_i`.
The four variants are forward `K_G`, its adjoint, the same operator with
`alpha` replaced by `-alpha`, and that operator's adjoint. These are the
four signed conjugate variants in the predecessor kernel.

The full-frame transport of the forward operator is `F† K_G F`, where `F`
is the width-9 product of the pinned engine's one-qubit gates `('C', e_i, +1)`
on qubits `0..8`. The adjoint uses sign `-1` in reverse qubit order. This is
the same sandwich the predecessor writes as `ff.adjoint().then(forward).then(ff)`.

Amplitudes are the exact states of
`research/active-mode-delivery-frontier/source/quadratic.py`, SHA256
`d406584aed1479b75c387bc964b9e797b2f4f75e5f8c6bbea00df07f7d590a91`.
That file is the engine already pinned by PR5745. This audit does not call
`clifford_exact`.

## Lemma. Every K_G fixes |0>

Let `G` be any invertible 9 by 9 matrix over `F_2`, and let `K` be any of
the four variants above. Then `K|0> = |0>` with Gaussian numerator `1` and
denominator `0`.

The permutation gate sends the basis index `0` to `G0 = 0`, so the state
offset stays `0` and no support column appears. Each diagonal form is built
from that offset and those columns, so every form is the constant `0`.
A constant-zero form contributes no phase: its constant term, its linear
terms and the quadratic products of two such forms are all zero. Negating
the linear signs, or taking the adjoint, only negates coefficients that are
already multiplied by those zero forms, and the inverse permutation still
fixes `0`. The scalar therefore remains `(1, 0)`.

The 288 word instances are the corollary for these 72 classes. The same
conclusion holds for the identity matrix, which the checker uses as a
control that the statement is not special to this word.

## Census. The full-frame transport does not inherit that identity

For each of the 72 forward operators, `F† K_G F |0>` is a single
computational-basis vector with a unit phase in `{1, i, -1, -i}` and with
denominator `0`. Exactly eight classes send `|0>` to `|0>` with phase `+1`.
The other 64 send `|0>` to a nonzero address. Every class whose address is
`0` has phase `+1`. The eight identity classes and the 64 addresses are
recorded in `RESULT.json`.

The first class, operator `1` with columns
`(1, 2, 4, 8, 64, 19, 104, 197, 325)`, has quadratic rows
`(400, 16, 384, 32, 387, 456, 416, 501, 501)` and linear signs
`(0, 0, 0, 0, 0, 0, 0, 1, 1)`. Its transport sends `|0>` to address `48`.
Those rows and that address agree with the monomial recipe already stored
for this same `G` in the filtered-native fixed-vector kernel. This package
recomputes them and does not read that JSON.

Removing `F` and `F†` restores `K_G|0> = |0>` for every class. Inserting one
`X` before `K_G`, or multiplying by a global factor `i`, is rejected. The
failure is the Fourier sandwich, not the fixed-vector check itself.

## Meaning for the scalar observer

The unchanged-coefficient warp step in the PR5745 observer agrees with
evaluating `K_G` on `|0>`. It does not agree with evaluating the full-frame
physical transport on `|0>`, except on the eight classes named in
`RESULT.json`. PR5823's all-rank `8H8` floor retains the common-fixed-vector
premise and does not become a theorem about `F† K_G F`.

No new κ follows. The selected conditional value stays
`781451/250000000`. The five framework assumptions stay in force.
