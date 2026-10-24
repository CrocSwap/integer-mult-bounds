# Exact output codes for both low-displacement responses

The native exits of both new responses admit the previous common
left output code W. The uniform output code no longer requires
rank-nine children. For the rank-sixteen response, its maximum child
rank is three. This is a local representation result. It does not
remove W or prove a complete supplier.

Let

```text
W = S_e0 C_45 S_e0
```

be the literal circuit in the pinned isotropic-pair-gauge packet.
The new emitter uses the frozen exit compiler and its exact physical
phase checks. It applies that compiler to the new words' actual
ordered source bases.

Two output representations are emitted:

* W48_I64 applies W to both data banks on the 48 paired ports.
* W112 applies W to both data banks on all 112 data ports.

At a coded port p, the exact physical output is

```text
X_p = W F9 x'_p,
Y_p = W F9 Q_p^-1 y'_p.
```

At an uncoded port, omit the initial W. The input convention remains
X=Qx, Y=y. The response itself does not change. In particular, there
is no commutation of W with Q and no free re-interpretation as a raw
endpoint.

## Actual exit replacement

For each coded source with last canonical frame Gamma_U, the final
edge is the exact operator W F9 Gamma_U^-1. All such sources share
the same W F9 frame. The inverse physical pair code remains legal.

For each coded target with last frame Gamma_V, the new intrinsic
exit is W F9 Q_p^-1 Gamma_V^-1. The old external target adapter is
removed. A rank-zero intrinsic exit is an explicit monomial event;
it is not omitted.

The new six-mode paths reach rank six before the source exit.
The exact coded source exit has rank two, in place of rank three.
The 48 pair-mode target exits become monomial. These calculations
use the actual source bases and phase maps; the result is not
inferred from a mass subtraction.

The small-clique exits depend on the clique size. In the
rank-sixteen word they start from rank-seven flags. Under the
uniform W output, the source exits have rank three and the target
exits rank two. The earlier matching word started its small sources
on lines and required rank-nine exits under the same W output.
The new flags therefore resolve that specific native-rank issue.
Recursive hosting remains a separate obligation.

## Complete local invoices

Every row below applies to both providers and both directions.
The scalar operation sequence is unchanged.

| Response and output code | Native profile | Children | Mass | Real scalar primitives |
| --- | --- | ---: | ---: | ---: |
| Rank30, W48_I64 | 988 H1 + 48 H2 + 55 H4 + 55 H5 + 9 H6 + 9 H7 | 1164 | 1696 | 5288 |
| Rank30, W112 | 988 H1 + 48 H2 + 55 H5 + 55 H6 + 9 H7 + 9 H8 | 1164 | 1824 | 5288 |
| Rank16, W48_I64 | 1472 H1 + 112 H2 | 1584 | 1696 | 7384 |
| Rank16, W112 | 1408 H1 + 112 H2 + 64 H3 | 1584 | 1824 | 7384 |

Each word has 48 inline monomial exits. W48_I64 retains 176 external
endpoint adapters; W112 retains 112. There are at most two side maps
per native child, in addition to the listed inline monomial and
external endpoint maps. These maps are not claimed to be free.

All 640 input columns remain independent. The 416 other fields keep
their original values and frames. There is no owned or private
workspace. The forward and backward scalar prefix bounds remain
46 and 30 for rank thirty, and 22 in both directions for rank sixteen.

## Verification and use

The source event schema is converted exactly to the frozen exit
compiler's rational scalar schema. The converted raw word is
replayed before any exit changes. Each output word is then checked
on all 640 columns, including every equal-frame scalar access and
every exact native or monomial source frame. The serialized packet
is read back and replayed again.

Every changed physical exit receives a fresh compiler lowering and
an independent Pauli and exact Gaussian-state comparison. The old
native phases remain pinned. The source pair-code metadata comes
from the exact cyclic-family payload.

Run emit_coded_exits.py with --out naming a new directory. Repeat
with optimized Python and a different new output directory. The
expected status is PASS_LOW_DISPLACEMENT_CODED_EXITS. Both payloads
and receipts must be byte-identical.

The W48_I64 mass saving is useful only if the caller can consume the
mixed representation. The uniform W112 representation has a larger
mass but a uniform exterior code. Neither word proves a free stage
transition, a free terminal inverse, helper progress, or the final
recursive cost. The complete controller must retain the stated
ordered physical outputs.

The coherent-port and root lanes supplied W. The oblique-native
lane supplied the exact exit compiler and its previous matching
application. This packet binds that construction to the new cyclic
paths and proves the resulting profiles. AI assistance was used.
No PR or publication is authorized. Before any future description,
read /Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
