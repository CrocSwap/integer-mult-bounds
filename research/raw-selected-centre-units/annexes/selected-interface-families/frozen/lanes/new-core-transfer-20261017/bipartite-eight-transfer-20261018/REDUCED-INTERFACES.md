# Eight-port physical interfaces and a shorter exact normalization

The new signed response admits a complete physical interface with only
eight selected ports. Its balanced backward and forward words cost
91,264 and 91,472 real scalar primitives. An additional normalized
backward word costs 89,200. It has exactly the same complete map as the
99,472-primitive path that first makes the borrowed-source block
diagonal and then applies the full data inverse. Both paths are emitted
and replayed on arbitrary data and workspace.

All these words retain native rank mass 5,073 and 3,507 native children.
They add no native child, private field, or owned-field operation. The
short backward normalization needs only a selected eight-port inverse
and a scalar lower shear on the completed X bank.

The same reduction applies to the preceding 24-port construction. A
coherent selected-query word gives its exact normalized map at 89,592,
instead of 96,012. The preceding frozen words remain valid at their
original bills.

This is a local result. It does not complete routed-stage code transport
or the supplier recurrence, and it makes no complete kappa claim.

## Exact source and required interface

The signed source is
`controller-followthrough-20261017/bipartite-eight-20261018/FREEZE.json`,
with SHA-256
`c147770b253d8b33a18ba6edb766ab505d203ba8ecd16507764d9a8c1c98e1c1`.
Its native payload has decompressed SHA-256
`0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee`.
It selects

`S=[0,7,15,36,42,46,79,89]`.

The other 104 ports form U. Of these, 40 are in the centre block and 64
are in the negative Hadamard block. Write the actual symmetric response
as

```text
J = [L B]
    [D H].
```

The source proves that L and the 40-port ordinary block are dyadic units,
both with determinant `1/16`. The other 64-port block has a dyadic
inverse. Thus H is a dyadic unit on all 104 ordinary ports. The full
48-port response has determinant `5^8`; its dyadic inverse is not
required by this construction.

The source forward and backward cores implement `(x,y+Jx)` and
`(x-Jy,y)`. Each costs 87,360 scalar primitives. Their actual native
records equal the retained provider records. The canonical words equal
the words in the preceding physical transfer, so its native phase bridge
and orientation-specific literal-dual recipes apply without a change.

Use the same physical endpoint convention as the preceding transfer:
input `X=diag(Q_p)x`, `Y=y`; completed output, after removal of the common
FULL frame, `X=x'`, `Y=diag(Q_p)^-1 y'`. All formulas below keep these
port operators in their actual order. Write Q for the selected diagonal
operator and `q=Q^-1`.

## Complete balanced words

The source supplies a 1,648-primitive word for H on the 40 ordinary centre
ports and its literal inverse at the same cost. Each word uses data
fields in place and no owned field. Bind these words to the actual
initial-Y and completed-X frames. Append the preceding exact 64-port
Hadamard word or its literal inverse. Each costs 2,048 and includes 32
physical field exchanges. Thus each complete ordinary gauge costs 3,696.

The checker verifies the full 104-port maps and both matrix inverse
orders. No field exchange, admission, or frame conversion is implicit.
The boundary gauges have no C0 operation. All eight owned fields remain
the responsibility of the native core, which clears them and returns
them zero.

Each selected exchange costs 26 primitives, so one eight-port pass costs
208. With logical input `x=(a,u)`, `y=(b,v)`, the raw backward word gives

```text
X_S = q b - L Q a - B v,
X_U = u - D Q a - H v,
Y_S = Q a,
Y_U = v.
```

Its cost is `87360+208=87568`. Applying H inverse to the completed X_U
gives the balanced backward word:

```text
X_S = q b - L Q a - B v,
X_U = H^-1 u - H^-1 D Q a - v,
Y_S = Q a,
Y_U = v.
```

Its cost is `87568+3696=91264`. The physical selected Y fields contain
the common FULL transform of the original a.

The balanced forward word applies H to current ordinary Y, exchanges S,
runs the forward core, and exchanges S again. It gives

```text
X_S = a + q (L q b + B u),
X_U = u,
Y_S = b,
Y_U = H(u+v) + D q b.
```

Its cost is `87360+2*208+3696=91472`. These operations use the current Y
bank before the core and completed data after the core. They do not use
an old query at a later view.

## A general exact normalization reduction

The reduction in this section requires only an invertible selected
principal block L. It does not require H inverse. If L and its inverse
have dyadic scalar implementations, the reduction is a dyadic physical
word at the completed common frame.

The original-X coefficient of the raw backward map, acting on
`z=(Qa,u)`, is

```text
C = [-L 0]
    [-D I].
```

Its inverse is

```text
N = [-L^-1     0]
    [-D L^-1   I].
```

Thus apply the following two operations to the completed raw X bank:

```text
X_S <- -L^-1 X_S
X_U <- X_U + D X_S
```

The second operation uses the already changed selected X fields. The
complete map becomes

```text
X_S = Q a - L^-1 q b + L^-1 B v,
X_U = u - D L^-1 q b - (H-D L^-1 B)v,
Y_S = Q a,
Y_U = v.
```

This proves the required original-X response `diag(Q,I)`. It also states
the entire borrowed-source response. No Q operator moves through L,
B, D, or H.

When H is also invertible, compare this with the longer path. Let

```text
U_B = [I -B]
      [0  I],

A = U_B diag(I,H^-1) C.
```

The longer path applies H inverse, then the upper subtraction `U_B`,
then A inverse. Its complete scalar suffix is

`A^-1 U_B diag(I,H^-1)=C^-1=N`.

This is equality on the full X bank, including every borrowed-source
term. It is not only equality of the original-X coefficient. It also
leaves Y unchanged. The checker executes both literal paths through the
native core and checks that all 640 output columns agree.

For the signed eight-port source, the emitted data factor is literally

```text
lower(-D); (-L on S); (H^-1 on the 40 ordinary ports); upper(-B).
```

The selected-only factor has 28 scalar operations and costs 192. Its
literal inverse implements `-L^-1` at the same cost. Each cross shear
has 144 half-coefficient ADDs and costs 1,440. The short normalized word
therefore costs

`87360+208+192+1440=89200`.

The diagonal backward word costs `91264+1440=92704`. The complete A
inverse includes the 4,720-primitive source word and the 2,048-primitive
64-port factor, so it costs 6,768. The long normalized path costs
`92704+6768=99472`. The exact reduction saves 10,272 primitives. This
equals two ordinary gauges plus two upper shears:
`2*3696+2*1440=10272`.

## The same reduction on the 24-port response

The preceding positive component response has

```text
L = I - K_S^T K_S/2,
L^-1 = I - K_S^T K_S/4,
D = -K_U^T K_S/2,
K_S K_S^T = 6I.
```

The short suffix can use one already owned C0. For each centre row,
query its six selected inputs, scale the query by `1/4`, and scatter its
negative signed entries to all 12 supported ports. Scale C0 by `-2`
and subtract the updated selected query. This restores C0 exactly.
After all eight rows, negate the 24 selected fields. The result is
precisely N. The 64 Hadamard ports are unchanged.

The suffix costs 1,608, including C0 admission, its final zero-frame
reset, and all 24 sign changes. C0 must be zero before each new COPY and
before the final reset. The checker verifies these conditions. The
complete word costs `87984+1608=89592`. It equals the preceding complete
96,012-primitive normalized word on every input column, including the
arbitrary owned input and borrowed data.

## Verification, dependencies, and limits

The payload contains fourteen complete eight-port words and four
complete 24-port normalization words. Every word is checked on both
source providers. Each replay covers all 640 input columns, restores
408 arbitrary helpers and 91 private zero buffers, and leaves all eight
owned fields zero. Scalar frames, child ranks, warp order, private-buffer
lifetimes, and all scalar invoices are checked. The native profile is
`2433H1+724H2+228H3+102H4+20H5`.

The signed eight-port boundary words use no owned field. The 24-port
short suffix uses one existing owned field and restores it coherently.
None of these words adds a native child or private field. All scalar
coefficients and all operator coefficients use exact fractions.

The checker pins all source manifests and validates every file named by
the two source freezes. It proves exact canonical equality and exact
native-record equality with the earlier phase-checked provider. It uses
the established forward and literal-dual backward recipes. It does not
rerun the lower-level phase interpreter. Independent review of these
new complete words is a separate artifact.

Run with new output directories:

```text
python3 work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/bipartite-eight-transfer-20261018/emit_reduced_interfaces.py --out-dir /tmp/reduced-interfaces-normal
python3 -O work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/bipartite-eight-transfer-20261018/emit_reduced_interfaces.py --out-dir /tmp/reduced-interfaces-optimized
```

Both runs must end with `PASS_REDUCED_NATIVE_SELECTED_INTERFACES` and
decompressed payload hash
`740c10032c464723f4cdfecf054ef586832f9563055c62d48a78b6d9f055b62d`.
Normal and optimized receipts and payloads must be byte-identical.
The checker rejects an existing output directory.

The signed response and principal-unit proof come from the controller
lane. Its source credits the bridge-review lane for the ordinary and
general data gauges, the budget-geometry lane for the sharp eight-port
lower bound within the sign family, and the oblique-native lane for the
response space. This packet adds the literal physical transfer and the
short exact normalization. It also uses the earlier native replay and
phase-checked provider work. This is AI-assisted research.

Routed-stage transport, caller exterior phase, storage hosting, recursive
precision, and the complete supplier bill remain open. Local principal
units do not establish these obligations. No PR, commit, or push is part
of this work. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
