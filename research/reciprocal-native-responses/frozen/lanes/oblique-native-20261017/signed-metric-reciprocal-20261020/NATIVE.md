# Native reciprocal words with a dyadic signed metric

This packet implements the actual112 response E from `MODEL.md` and its
reciprocal in the two native shear directions. All640 input fields are
arbitrary. The416 fields outside the224 data fields are unchanged.

Write Q=diag(C_qp), q=Q^-1, and let F be the common9-axis advance.
The complete words include the conventional input and output adapters.
They have these physical contracts:

| Word | Physical input | Physical output |
| --- | --- | --- |
| `forward_E` | (Qx,y) | (F x,F q(y+E x)) |
| `backward_transpose_E` | (Qx,y) | (F(x-E^T y),F q y) |
| `forward_inverse_adjoint_E` | (Qx,y) | (F x,F q(y+E^-T x)) |
| `backward_inverse_E` | (Qx,y) | (F(x-E^-1 y),F q y) |

The order of F,q, and E in this table is part of the contract. The
packet does not commute E through the field-dependent Q maps.

## Construction

The frozen odd16 native source has a transfer position for every ordered
off-diagonal pair in each large6-mode block and each small8-clique.
This packet retains every native edge, ordered frame, and endpoint
adapter from its forward word.

At each transfer position, replace the coefficient by the corresponding
entry of E in the native mode basis. Delete a transfer when its new
coefficient is zero. The physical pair-code steps are unchanged. The
all640-column replay proves the first contract.

For the second forward word, use E^-T. This matrix has zero diagonal in
the same mode and physical bases. Thus the same transfer positions
implement it. No new native path is needed.

For each forward word, construct its literal inverse adjoint. Keep the
event order and every native unitary. Replace ADD(target,source,c) by
ADD(source,target,-c). Replace each real SCALE(c) by SCALE(1/c).
All scalar coefficients in this packet are real. Each new ADD has equal
source and target frames because the original ADD did. This proves the
complete native inverse-adjoint relation, including all endpoint
monomials. The two resulting backward words also pass the full content
and frame replay.

This is a direct reciprocal implementation. It does not require the
two-bank metric wrapper described below.

## Full local invoice

Each of the four words has:

```text
1520 H1 + 64 H2 + 48 H3,
native mass 1792,
1632 native children,
6440 real scalar primitives,
224 explicit endpoint monomial maps,
at most3264 native side maps,
zero owned fields and zero private outer fields.
```

Every content prefix is dyadic, with binary denominator height at most1.
The maximum row one-norm is46 for `forward_E`,16 for
`backward_transpose_E`, and30 for each directly retuned reciprocal word.
The invoice is the same for both actual providers.

All1561 inherited native recipe records and all224 endpoint adapter
records are byte-equal to the pinned source. Every actual native event
has the same field, old ordered frame, new ordered frame, rank, and
recipe key as that source. The source phase proofs therefore apply
without a changed hypothesis. This run checks that exact inheritance;
it does not claim a fresh spatial replay of those recipes.

The416 unchanged fields include the existing helper fields and the eight
extra named fields in the source schema. No event reads or writes any
of them. This proves restoration on arbitrary state. It does not supply
the separate productive progress that an outer supplier may assign to
those helpers.

## Paid diagonal conversion

The physical diagonal metric commutes with each individual native map.
It is legal to apply its scalar entries even when different fields have
different frames.

Let D2=diag(J,J). Since E^-T=J E J^-1, the native forward word for
E^-T can also be obtained by pre-scaling both banks by J^-1 and
post-scaling both banks by J. The native backward word with cross term
-E^-1 can be obtained by pre-scaling both banks by J, using the
backward transpose word, then post-scaling both banks by J^-1.

The packet emits and replays both constructions. Each adds128 scalar
SCALE instructions,640 real scalar primitives, and no native child.
The total is7080 scalar primitives. The backward wrapper has binary
height at most2; the forward wrapper has height at most1.

The common-frame one-bank conversion in `MODEL.md` costs320 primitives.
The two-bank native wrapper costs640 because it must restore both
baseline banks. Direct transfer-coefficient retuning gives the same
required shear for6440 primitives and avoids the wrapper surcharge.

## Verification and limits

Run `python3 -I -B emit_native.py --out <new-directory>` and repeat with
`-O`. The decompressed payload and receipt must agree.

The producer checks both providers and all six words. It verifies all640
input columns, every scalar access, every literal native frame, all final
frames, every unchanged helper column, the full local cost, and the
serialized payload. It also deletes one nonzero transfer in each
principal direction and rejects the changed result.

No global controller, centre record, terminal decoder, routed stage
composition, helper progress, recursive host, or complete bound is
claimed here. In particular, the rank16 factor E-P does not by itself
make its centre information available at a later cut.

The native path and phase records come from the new-core-transfer
odd16 packet and its cited cyclic-flag sources. The coordinating agent
supplied the signed-metric identity. The new-core-transfer lane supplied
the physical pair-closed role placement. This lane supplies the actual
reciprocal coefficient words, literal inverse-adjoint directions,
metric wrappers, and exact local invoice. AI assistance was used.

No PR, push, commit, or publication is authorized. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
