# The complete inverse-adjoint reader service

This packet completes the physical inverse-adjoint of the fixed-reader
forward service. It includes the native carrier prefix, all DATA maps,
the whole-cover barrier, and the late query. The old-reader label can be
0 or 1. The current service stage can be 1 or 2. The three pairs are
\((s,t)=(0,1),(0,2),(1,2)\). Both native providers are included.

The complete word costs 14,896 real scalar primitives and has native
rank 1,792. It has no extra field and no odd division. All 416 borrowed
helper fields can have arbitrary input values and are restored.
The map count is an upper bound of 4,384 calls. This packet does not
give a finite real-operation price for these maps, a new helper host,
a closed caller, or a multiplication exponent.

## The exact types

Let P be the pinned set of sixteen selected ports. Let R be its
96-port complement. Put

\[
G_R=\operatorname{diag}(I_P,q_R),\qquad
F_\ell=\operatorname{FULL}_{9+8\ell}.
\]

The physical input level is \(t-1\), independent of the reader label s.
The old reader is the actual routed \(L_s\). The current response is
the actual routed dyadic involution \(A_t\). Define the complete
112-row operator \(D_{s,t}\) by

\[
(D_{s,t})_P=L_sA_t,\qquad (D_{s,t})_R=(A_t)_R.
\tag{1}
\]

The emitted inverse-adjoint service is

\[
(F_{t-1}x,\ F_{t-1}G_Rw)
\longmapsto
(F_t(x-D_{s,t}^{*}w),\ F_tG_Rw).
\tag{2}
\]

The selected records and all ordinary records in w are arbitrary.
The word preserves their logical contents. It does not set a borrowed
baseline to zero. The star includes the inverse owner route of every
coefficient, as well as the matrix transpose.

For comparison, the frozen forward service has the same physical
types and the content map \((x,w)\mapsto(x,w+D_{s,t}x)\).
Equation (2) is its exact inverse-adjoint, with its unitary input and
output frames retained.

## Same chronology, complete physical operation

For chronological gates \(g_1,\ldots,g_n\), the physical operator is
\(U=g_n\cdots g_1\). Then

\[
U^{-*}=g_n^{-*}\cdots g_1^{-*}.
\tag{3}
\]

Thus the chronological order does not change. For each scalar gate:

- Replace `target += c * source` by `source -= c * target`.
- Replace a real scale c by the scale \(c^{-1}\).

All coefficients here are real. Every scale is a nonzero signed power
of two. No CLEAR or noninvertible gate occurs.

Each native child and each physical monomial map is unitary. Therefore
its inverse-adjoint is the same physical operator, with the same global
phase. The emitter retains every native event, phase recipe, input
adapter, output adapter, DATA map, and late map at its original position.
It checks all nine-dimensional monomial matrices for invertibility and
all stored quadratic phases for unit modulus. The exact native recipe
identities are inherited from the pinned independent phase review.
No new native phase recipe is inferred from a binary rank alone.

At every scalar event, the source and target have the same physical
frame. Transposing that event therefore remains legal. The new replay
checks this equality at every event, with the exact live frame ledger.
It checks all 640 input columns. The native prefix gives

\[
x\longmapsto x-(A_t)_R^{*}w_R,\qquad w\longmapsto w.
\tag{4}
\]

The late word then subtracts \((L_sA_t)^*w_P\) from X. Its maps touch
only X and selected Y fields, which are FULL at that cut. Ordinary Y
fields keep their hole frames and do not enter the late query.
Equations (4) and this final subtraction give (2).

The complete physical order remains:

```text
DATA entry
128 native input adapters
complete native carrier cover sweep
96 ordinary output adapters
DATA exit
complete-cover barrier
late inverse-adjoint reader query
```

The late map source fields are not relabelled. A former query target
becomes a scalar source, while its physical map stays at the same place
in the word. This distinction is checked in the serialized program.

The same construction applies to any finite word of unitary field maps
and invertible linear scalar gates. It requires the physical frame and
field at each event, not an inverse of its response matrix. If the
forward endpoint is a lower shear with reader D and is the identity
on arbitrary borrowed fields, the new endpoint is the upper shear with
reader \(-D^*\) and is also the identity on those fields. D can be
rectangular or singular. For composition, apply the rule to the complete
physical gate list in its existing chronological order. A new boundary
conversion is needed only when the original words did not already have
compatible physical types.

## Actual D25 source and phase binding

Each field uses the exact regular-cover route
\(h=d\rho_{t,p}\). The route is orthogonal, fixes the port's intrinsic
line, and has the pinned DATA translation. The emitter repeats all
448 entry and 448 exit Z4 identities in the dispatcher. It also checks
the complete Z4 identity and inverse translation of each late FULL map.

The native input and output types in the current body are

\[
\operatorname{diag}(Q,Z),\qquad
\operatorname{diag}(F_9,F_9G_R),
\quad Z=\operatorname{diag}(Q_P,I_R).
\]

The DATA identities identify these types with the two global boundaries
in (2), with the same common exterior. They apply to the new word
because all its physical frame operators are unchanged.

For a unitary input frame I and output frame O, a content map C has
physical action \(OCI^{-1}\). Its inverse-adjoint is
\(OC^{-*}I^{-1}\). This proves the direction of the retained physical
boundaries. It does not reverse the stage progression or exchange the
two DATA views.

The regular-cover replay retains both the input field and the complete
25-axis owner matrix in every coefficient. It lifts the replayed native
prefix through the actual DATA arrays, then executes the literal late
word. For all six provider/pair cases, it equals the direct operator in
(2). Both products with the forward adjoint are the identity on all
640 fields. The actual source-view order is part of this calculation.

## Full invoice and bounds

| Part | Real scalar primitives | Map calls |
| --- | ---: | ---: |
| Native carrier prefix | 6,456 | 224 endpoint adapters |
| Late inverse-adjoint query | 8,440 | 672 |
| DATA entry and exit | 0 | 448 |
| Native child side maps | 0 | at most 3,040 |
| Complete word | 14,896 | at most 4,384 |

The native profile is

```text
1392 H1 + 64 H2 + 48 H3 + 16 H8.
```

There are 1,520 native children and total native rank 1,792. Scalar
transposition and inversion of signed power-of-two scales preserve
the frozen tariff. Native child sizes and physical side maps do not
change.

The exact coefficient row-sum peak of the native prefix is 12, with
binary denominator height one. The late dual on independent inputs
has peak 30 and height two. After the actual native prefix, the complete
emitted-boundary peak is 40 and height two in all six cases.
These are content bounds at the emitted gate boundaries. They exclude
internal arithmetic in a lowered ADD, a recursive child, or a caller.

The original helper owner contract is retained. The same helper fields
and native events occur at the same times, and the new 640-column replay
restores every arbitrary helper value. This does not prove a new
recursive parking construction or change the inherited helper count.

## Verification, scope, and credit

Run `emit_dual.py --output <new-directory>` with normal Python and with
`python3 -O`. The payloads and receipts must be byte equal. The emitter
rejects an existing output directory.

The checks include the complete physical frame ledgers, all 640 native
and routed columns, all 416 helper identities, both inverse product
orders, the 896 DATA phase equations, and all late map phases.
Changing a dual ADD sign fails in both native prefixes and in all three
late queries. The serialized complete words are replayed again.

The packet uses the controller lane's row involution, the native lane's
carrier prefix, the reviewed fixed-reader forward query, and the
independent native, DATA, and late-dual reviews. Their exact paths and
hashes are in the program and freeze manifest. This work was produced
with AI assistance and exact rational computation.

This result supplies a complete backward service with the types in
(2). It does not assert that \(D_{s,t}\) is reciprocal, that it is the
same at different stages, or that a complete caller closes. The original
raw-output phases, recursive hosting, finite map costs, and final
supplier calculation remain separate obligations.

No PR or publication is authorized. Before any future PR description,
read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
