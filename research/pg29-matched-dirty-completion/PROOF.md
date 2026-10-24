# Matched-stub scalar completion over GF9

Let `F=F3[t]/(t^2+1)`. The transcript in `dirty-word.json` specifies 182
invertible local maps of size five. It orders their inputs and outputs on
175 boundary stubs. The first 157 boundary inputs are message variables.
The other 18 inputs are the two ends of each of nine C edges. The last
18 outputs are the two ends of each of nine J edges. Every boundary input
is a separate formal variable in the first replay.

The transcript is a finite matrix over F, not a physical recursive supplier.
It uses the projective-plane code of Braverman and He, with each former zero
C stub made an independent input. Its field operations and local program are
checked separately from the original verifier.

## Independent-stub map

The complete boundary transfer is

```text
M = [ I157  F ]
    [  G    H ].
```

The exact replay gives `rank(F)=9`, `rank(G)=9`, and `rank(H)=18`.
It gives `rank(M)=175` and an invertible 18 by 18 Schur matrix `H-GF`.
These ranks do not make M a permutation of its input roles. In particular,
F and G are nonzero. Arbitrary independent C inputs can affect message
outputs, and messages can affect J outputs.

The separate replay checks every local five by five matrix, follows every
one of the 735 physical edge transmissions, and compares all 175 output
coefficient rows with the saved transfer. It then checks rank(M) by exact
elimination over F. This is coverage of every input, not random testing.

## Matched inputs and the quotient

Let P be the 18 by 9 matrix that gives the same value to both input stubs
of each C edge. Its nine columns are indicators of the nine disjoint pairs.
Let Q choose one output from each J pair. The exact checks establish:

1. `FP=0`.
2. The two rows of G in each J pair agree.
3. The two rows of HP in each J pair agree.
4. `D=QHP` is invertible.

Put `B=QG`. On the 166-dimensional input space `(x,z)`, the matched transfer
therefore has the exact form

```text
(x,z) -> (x, Bx + Dz).
```

The two copies of every J output agree before the quotient is taken. Thus
choosing one row per pair loses no information on this specified input
subspace. The result does not assert equality for arbitrary independent
values on the 18 C stubs.

Apply D inverse to the nine returned values, then subtract `D^-1 B x`.
The composite is

```text
(x, Bx + Dz) -> (x, D^-1 Bx + z) -> (x,z).
```

The matrices in `PG29-FACTORS.json` give this complete scalar correction.
`completion.py` computes them with separate field arithmetic and checks all
166 formal columns of the identity. It also checks both products with each
inverse and compares every saved factor entry. The correction `D^-1 B`
has rank nine and 1,243 nonzero coefficients. D has 74 nonzero coefficients.
These are matrix counts, not recursive call costs.

## Interface and cost boundary

This is a complete finite scalar identity on the matched input subspace.
The correction uses unrestricted linear combinations of the message and
junk values. It does not supply legal rational common frames for these
combinations. It does not price preparation of matched inputs, the physical
return of pairs, frame transitions, controller access, or recursive children.
The 735 transmissions are the original network's physical edge count;
they are not an admitted paid profile for integer multiplication.

A physical implementation must first realize the matched-input injection,
all local maps, the quotient, and the complete inverse correction at legal
frames. It must then charge them and restore every borrowed value. A matrix
inverse at the boundary does not meet those obligations. No complex companion,
complete supplier, or kappa improvement follows from this scalar identity.
