# A physical 24-port interface for the structured centre core

The complete local words use the new structured response from
`controller-followthrough-20261017/structured-centres`. They select 24
ports, use no new native child, and retain the native rank mass 5,073.
The backward word costs 91,368 real scalar primitives. Its variant with
a diagonal borrowed-source block costs 91,944. The forward word costs
91,894. These bills include all selected exchanges, both parts of each
scalar gauge, and the owned-field admission and frame resets.

The full original-X response of the diagonal backward word is a dyadic
unit. An emitted scalar inverse on the completed X bank costs 4,740.
The complete backward word with this inverse costs 96,684. Its original-X
response is exactly `diag(Q_S,I_U)`. This statement includes the actual
physical Q operators in their original order.

This packet proves a local interface. It does not supply a decoder
between routed stages or a complete supplier. It gives no change to the
complete kappa bound.

## Source, representation, and sign

The source freeze has SHA-256
`5e762396d55ac47b34bbe60e30c62a429ddd6fc1f018cb4b4b94d3670d374a19`.
Its native payload has decompressed SHA-256
`2b9de1454c2025ae4e230bd64de36b4f6c937628c63fc5afede6640dd3c0e1e1`.
The source response is

```text
E = E_64 direct-sum (-I_48 + K^T K/2),
E_64^2 = 4I_64,
K K^T = 12I_8.
```

Select the first three of the six orthogonal eight-port minors in the
source receipt. Call these 24 ports `S`. Call the other 88 ports `U`.
The set `U` contains 24 centre ports and all 64 Hadamard ports. Each
restricted centre row has six signed unit entries on each side.

The emitted core uses `J=-E`. The checker changes the signs at exactly
184 scalar transfer sites in each orientation. The paired backward site
is the literal transpose of the corresponding forward site. All native
records and all other scalar records are unchanged. Both orientations
still cost 87,360 scalar primitives. The full replay proves

```text
forward:   (x,y) -> (x, y + Jx),
backward:  (x,y) -> (x - Jy, y).
```

Each `Q_p` is the actual port operator. Write `Q_S` for their diagonal
action on selected coordinates, and write `q_S=Q_S^-1`. The physical
input convention is `X_p=Q_p x_p` and `Y_p=y_p`. At the completed output,
after the common FULL frame is factored out, the physical convention is
`X_p=x'_p` and `Y_p=Q_p^-1 y'_p`. The checker inserts these conversions
explicitly. It cancels only adjacent inverse operators on the same port.
It does not commute a Q operator through a scalar coordinate map.

## An explicit scalar word on the other 64 ports

The Hadamard part has eight pairs of four-port groups. The checker derives
each pair directly from the actual response support. It orders the second
group so that the negative response between the two groups is

```text
T = [ 1 -1 -1 -1 ]
    [-1 -1  1 -1 ]
    [-1  1 -1 -1 ]
    [-1 -1 -1  1 ].
```

On four fields, use the pairs `(0,1),(2,3),(0,2),(1,3)` with respective
signs `d=-1,1,-1,1`. For each pair perform

```text
a += d*b
b *= 2
b -= d*a
```

This sends `(a,b)` to `(a+d*b,b-d*a)` and costs 18 primitives. After
the four pair operations, negate fields 1 and 2. The result is `T` and
the cost is `4*18+4=76`.

Apply this word to both groups. Then exchange their four corresponding
physical fields. Each exchange is the literal word

```text
a += b
b -= a
a += b
b *= -1
```

It costs 26 primitives. Thus the full 64-port word costs
`16*76+32*26=2048`. No field exchange is free or implicit. Its matrix is
`-E_64`. Reverse the complete scalar word, negate each ADD coefficient,
and replace each SCALE coefficient by its reciprocal. This gives the
literal inverse `-E_64/4`, also at cost 2,048. Exact replay checks both
inverse orders on all data and owned fields.

## The ordinary gauge and the physical boundary

Partition `J` by `S,U`:

```text
J = [J_SS J_SU]
    [J_US H   ].
```

On the 24 ordinary centre ports,

```text
H    = I - K_U^T K_U/2,
H^-1 = I - K_U^T K_U/4.
```

On the other 64 ports use the exact words above. The resulting complete
`H` and `H^-1` are dyadic inverses on all 88 ordinary ports. The checker
proves both matrix inverse orders and the actual scalar maps.

Use the pinned, coherent serial gauges from `RANK8-GAUGES.json` on the
centre ports. Their unmodified costs are 1,236 for H and 1,332 for its
inverse. They copy into a zero C0, compute a query, scatter it, and
subtract the updated query to restore C0 to zero. The physical binder
admits C0 with one CLEAR. For a FULL-frame word it also resets the zero
C0 to the initial frame with one final CLEAR. The checker requires C0
to be zero before this final reset. It does not erase a data-dependent
query to make the gauge pass.

The complete Y gauge costs `1236+2048+2=3286`. The complete FULL-X inverse
gauge costs `1332+2048+4=3384`.

Each selected physical exchange costs 26, so a full pass on S costs 624.
Let the original logical input be `x=(a,u)`, `y=(b,v)`. A selected input
exchange, followed by the backward native core, gives

```text
X_S = q_S b - J_SS Q_S a - J_SU v,
X_U = u - J_US Q_S a - H v,
Y_S = Q_S a,
Y_U = v.
```

Postcompose with `H^-1` on FULL X_U. The complete balanced backward word
then gives

```text
X_S = q_S b - J_SS Q_S a - J_SU v,
X_U = H^-1 u - v - H^-1 J_US Q_S a,
Y_S = Q_S a,
Y_U = v.
```

In physical coordinates, selected productive Y is exactly the common
FULL transform of the original `a`. The bill is `87360+624+3384=91368`.
The word reads only the present input before the native core and the
completed X bank after it. It does not read an old Y query at the end.

For the forward word, apply H to the current ordinary Y bank in the
initial frame. Then do a selected input exchange, the forward native
core, and a selected output exchange. The resulting map is

```text
X_S = a + q_S (J_SS q_S b + J_SU u),
X_U = u,
Y_S = b,
Y_U = H(u+v) + J_US q_S b.
```

Its bill is `87360+2*624+3286=91894`. Both selected exchange passes are
physical operations. The first and last use the initial and FULL frames,
respectively.

## A diagonal borrowed-source block and a full data inverse

After the balanced backward map, apply

`X_S -= J_SU X_U`.

Only the 48-port centre block has a cross term. Since
`K_U H^-1=-K_U/2`, the extra selected update can use the same six-entry
query that the serial H inverse already holds in C0. Scatter
`-K_S^T C0/4` to the selected X ports before the query is restored. This
adds 48 ADDs with coefficient magnitude `1/4`, at cost 576. The source
query restoration remains valid because it reads only U. The complete
fused suffix costs 3,960.

Let `P` be minus one on S and plus one on the 24 ordinary centre ports.
Define the full data map

```text
A_48  = P - K^T K/4,
A_64  = -E_64/4,
A     = A_64 direct-sum A_48,
L     = diag(Q_S,I_U),
D     = diag(q_S,-I_U).
```

The complete diagonal backward word is

```text
X' = A L x + D y,
Y'_S = Q_S a,
Y'_U = v.
```

Thus the coefficient of the original borrowed Y bank in X is exactly
diagonal. Its bill is `87360+624+3960=91944`.

The source proves and emits

```text
A_48^-1 = P + P K^T K P/4.
```

On the 64-port block the inverse is `-E_64`. Bind the source 48-port data
inverse to FULL X and append the actual 64-port word. The complete scalar
inverse costs `2688+2048+4=4740`. The checker executes both literal inverse
orders, including C0 restoration. It also executes the entire native
diagonal backward word followed by this suffix. On all 640 input columns
the result is

```text
X'' = L x + A^-1 D y,
Y''_S = Q_S a,
Y''_U = v.
```

The checker separately extracts all original-X columns and verifies that
they are exactly `L`. The complete cost is `91944+4740=96684`.

## Exact checks and limits

The payload contains six complete words for each of the two providers:

| Word | Scalar primitives | Native rank mass |
| --- | ---: | ---: |
| Raw backward | 87,984 | 5,073 |
| Balanced backward | 91,368 | 5,073 |
| Diagonal backward | 91,944 | 5,073 |
| Normalized backward | 96,684 | 5,073 |
| Raw forward | 88,608 | 5,073 |
| Balanced forward | 91,894 | 5,073 |

Each complete word checks all 640 formal input columns: 224 data fields,
408 arbitrary borrowed helpers, and eight arbitrary owned fields. It
restores every helper, restores all 91 private zero buffers, and leaves
all eight owned fields zero. All scalar frame constraints, every warp,
every native climb, and all private-buffer lifetimes are checked. The
native profile is `2433H1+724H2+228H3+102H4+20H5`: 3,507 children. The
scalar gauges use only the already owned C0. They add no native child,
child wrapper, private field, or helper access.

The native phase dependency is the unchanged source geometry and the
orientation-specific recipes in `new-native-recipes-20261017`. Backward
uses the literal-dual lowering already established for that provider.
The present checker proves that all native records are unchanged. It
does not rerun the lower-level Pauli and Gaussian-state phase verifier.
An independent review of this new physical transfer is a separate
artifact; it is not inferred from the older core review.

All matrices and all operator coefficients use exact fractions. Normal
and optimized Python runs must give byte-identical payloads and receipts.
The checker has no assertion that can disappear under `python3 -O`.
Run it with a new output directory each time:

```text
python3 work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/structured-centres-transfer-20261018/emit_structured_transfer.py --out-dir /tmp/structured-transfer-normal
python3 -O work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/structured-centres-transfer-20261018/emit_structured_transfer.py --out-dir /tmp/structured-transfer-optimized
```

Each run must end with `PASS_STRUCTURED_CENTRES_PHYSICAL_TRANSFER` and
payload hash
`334ae2c970d591fd2999d4472dea2add296c978d5e7479b69210e4c3d05f76ff`.
The checker rejects an existing output directory. The local freeze pins
the proof, checker, source pins, payload, and receipt.

The supplier still needs code transport between routed views, a caller
exterior phase proof, storage and hosting rules, a complete precision
bound, and the full recursive bill. An invertible local response does
not discharge these obligations.

This work builds on the structured response and coherent centre gauges
from the controller-followthrough lane, the response-space construction
from the oblique-native lane, and the earlier physical exchange and
native replay work in this lane. It is AI-assisted research. No PR,
commit, or push is part of this packet. Before any future PR description,
read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
