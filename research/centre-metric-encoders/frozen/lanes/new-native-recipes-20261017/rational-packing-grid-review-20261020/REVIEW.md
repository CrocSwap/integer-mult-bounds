# Independent review of the paid rational packing and grid

The frozen scalar packet passes. Both complete code words agree with
the actual 112-port C16 matrix and its adjoint on all 1,280 real input
columns. The 528 outside complex fields remain arbitrary and unchanged.
The exact scalar invoices, divisibility domains, and stated local
prefix bounds also pass. No material error was found.

The [producer freeze](../../bridge-access-20261017/rational-unitary-packing-20261020/FREEZE.json)
has SHA256
`2db9b1d5425dea76345ecbfde9a601e47a620693fc5e58350d311db292fc5fdc`.
Its actual matrix source has decompressed SHA256
`b460c1b4603f4b75da5ca4bf1da4a642f2cc4d970599f9c1068832e7b230ac32`.
This is the first C16 packing of the actual reader. It is not a
modification of the later native-compatible C24.

The [checker](check.py) uses a pinned independent rational-arithmetic
helper. It imports no producer interpreter. A reverse column pass
checks each literal word. A separate forward pass checks every
instruction boundary. All input hashes are in
[INPUTS.json](normal-final/INPUTS.json), and the finite results are in
[REVIEW.json](normal-final/REVIEW.json).

## Literal word and cost

The review reconstructs A, B, the paid middle permutation, and

```text
R = (1/3) diag(A*,A*) P diag(B,B)
```

directly. It checks both norm-three identities, the exact R matrix,
and both unitary orders. It verifies the four actual disjoint port
quartets and the complete preliminary-code joins.

The full code adjoint word is the literal reverse inverse of the
full code word. Both complete inverse products pass. The review
also checks C16's actual reader decoder: its support has sixteen
complex coordinates and its product with C16 is the original
sixteen-row reader. The reader is bound to the accepted actual
source matrix.

| Word | Old real scalar units | Real ×3 scans | Real /3 scans | Instructions | Prefix row one-norm | Binary height | Odd height |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Four R blocks | 840 | 16 | 16 | 256 | 7 | 1 | 1 |
| Four R* blocks | 840 | 16 | 16 | 256 | 6 | 1 | 1 |
| Complete C16 | 5702 | 16 | 16 | 2110 | 17 | 2 | 1 |
| Complete C16* | 5702 | 16 | 16 | 2110 | 28/3 | 2 | 1 |

There is no scratch field or native child. The old scalar tariff is
computed only from the dyadic component instructions. Multiplication
and division by three remain separate scan opcodes.

The words act at a proved common complex frame. Their complete real
matrices are complex-linear. Individual real-component instructions
need not commute with that complex frame. The complete word must
remain contiguous, with no native operation, map, or partial-field
use inserted inside it. The displayed prefix bounds refer to the
physical input components at that common cut. They do not include
primitive ADD interiors or recursive child arithmetic.

## Exact division domain

Put `R0=Z[i,1/2]` and `N=3R`. The review performs elimination directly
over `F9=F3[i]`. It obtains Gaussian rank one for N, and separately
obtains real rank two for its real matrix.

The first row, normalized by its first nonzero entry, is

```text
(1, (1-i)/2, -(1+i), -1) modulo 3.
```

Consequently, for `x in R0^4`,

```text
Rx is in R0^4
if and only if
x0 + ((1-i)/2)x1 - (1+i)x2 - x3 = 0 modulo 3.
```

The independent check enumerates all 6,561 residue inputs in each
direction. Exactly 729 inputs satisfy the literal division contract.
For both R and R*, that contract is exactly the condition that the
complete output is dyadic. For R it also agrees with the displayed
Gaussian congruence.

This finite test proves the full R0 domain. Every tested condition
depends only on the residue modulo three. The prefix matrices have
at most one factor three in their denominators; changing an input
by an element of `3R0^4` changes every relevant postdivision value
by a dyadic value.

Cpre is a dyadic unit. Thus it does not impose this congruence on
arbitrary input. The full code check rejects the contract with only
a binary root guard. It proves every actual division on every
column after the one required ternary level is supplied.

For the four R blocks, a local numerator factor `2×3` suffices.
For a complete code word, `4×3` suffices relative to integral input
numerators. These factors describe the local binary and ternary
guard. They are not a complete recursive grid or an uncharged
representation change.

## Independent proof of exact power growth

The review recomputes the trace of the actual complete C16:

```text
trace(C16) = (11+7i)/6,
h3(C16) = h3(C16*) = 1.
```

There is a finite-field proof of the all-power claim. It does not
need an eigenvalue calculation.

Let `A=3C16`. Its entries belong to R0. Reduce A modulo three to
obtain `Abar` over F9. The exact trace is

```text
trace(Abar) = (11+7i)/2 modulo 3 = 1+2i != 0.
```

A nilpotent matrix over a field has trace zero. For example, a
basis adapted to its kernel filtration makes it strictly triangular.
Therefore Abar is not nilpotent. In particular, `Abar^m` is nonzero
for every positive integer m.

But `A^m=3^m C16^m`. Its nonzero residue means that at least one
entry is not divisible by three. Hence `h3(C16^m)>=m`.
Multiplication of the original coefficients gives the reverse
bound `h3(C16^m)<=m`. Therefore

```text
h3(C16^m) = m, for all integers m >= 1.
```

For the adjoint the residue trace is `1+i`, also nonzero, and the
same proof applies. The full residues of `3C16` and `3C16*` each
have rank four. The rank-one statement belongs to one quartet's
numerator N; it is not a rank-one claim about the complete code.
The first four exact powers in each direction are separate finite
controls for this proof.

The theorem is unchanged by a fixed dyadic-unit change of basis.
If G and its inverse have no factor three in their denominators,
then

```text
h3(G^-1 M G) <= h3(M)
```

and the reverse inequality follows by conjugating back. Thus a
fixed legal dyadic stage view cannot remove this power growth.
The same conclusion holds after tensoring with an identity.
No claim about products of different stage codes follows from
this statement.

A full bounded three-adic lattice that is stable under C16 would
bound all its powers in the coordinate norm. The exact growth
excludes such a lattice. In particular, no such lattice can be
stable under both the actual Cpre and the complete packing Rall.

R alone is different. Its order is exactly four. A finite invariant
lattice is obtained by summing the four images of the coordinate
lattice. The independent check also confirms the producer's signed
interleaving example: `3RS` has nonzero residue trace `-2+2i`.
It therefore has the same unbounded unmatched power growth.

## Paid grid and matching types

The scan review checks all finite-control transitions and 16,380
signed division or multiplication cases through width twelve.
It uses modular inversion to compute the expected quotient,
separately from the producer's scan interpreter. The signed tests
reject nonmultiples and multiplication overflow.

The source-backed scan bound remains `4(w_g+1)` arithmetic-head
steps per real record. Descriptor work is separate. Thus one
complete code direction adds at most `128 n(w_g+1)` arithmetic-head
steps for the 32 odd scans when each field has n records.

The retained root-grid theorem applies if each completed recursive
child has a proved Gaussian-dyadic endpoint on all roles. If a
finite parent has local odd height at most M and recursive edge
depth at most D, the common exponent is `K=M(D+1)`. Every numeric
root stream must be converted, including arbitrary borrowed
values. Addresses and tags are excluded.

The two outer conversions cost at most
`8 N_real K(w_g+1)` arithmetic-head steps. The added width is at
most `2K` bits. A full binary guard and descriptor costs remain
separate. The final physical endpoint must be dyadic on every role
before exact outer unscaling.

C16 itself is not such a completed dyadic child. Its unitarity does
not change that fact. Matching rational boundary types are allowed:
the exact products `C_out A C_in^-1` cancel adjacent types in order
when A is dyadic on the complete semantic state. The caller must
prove all whole-state types, decoded child-entry types, and local
prefix bounds. A code on 112 fields does not supply a type for a
recursive call on one field.

A useful bounded case is already proved by the literal words here.
The matched pair C16 followed by C16* has prefix odd height one:
the inverse word retraces the first word's intermediate states.
This does not imply a height-one bound for unmatched C16 calls or
for an unproved recursive caller.

The 224-view common-FULL access count remains a separate conditional
access statement from the pinned general-stage proof. It does not
admit mixed holes or make view execution free. All 96 ordinary
diagonals of this particular C16 are nonzero, so this scalar packing
does not inherit the current off-diagonal native realization.

## Reproduction and scope

Run the checker under both modes into new directories:

```text
python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/rational-packing-grid-review-20261020/check.py --out <new-directory>
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/rational-packing-grid-review-20261020/check.py --out <another-new-directory>
```

Expected output:

```text
PASS_INDEPENDENT_RATIONAL_PACKING_GRID
```

The reproduction record compares the receipts and input manifests
byte for byte and checks every consumed source hash again.
The missing-instruction control rejects a damaged packing word.

This review establishes the paid scalar words, their exact grid
requirements, and the stated reuse limit. It does not establish a
changed native response, mixed-hole access, a complete recursive
child, a new helper host, or an improvement to the full supplier.

The original packing and preliminary code came from the
independent-review lane. The bridge-access lane supplied the paid
packing and grid packet. This review supplies a distinct replay,
an exhaustive domain check, and the finite-field power proof.
AI assistance was used.

No PR, commit, push, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
