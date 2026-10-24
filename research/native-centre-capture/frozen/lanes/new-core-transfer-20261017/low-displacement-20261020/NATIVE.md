# Native realization of the rank-thirty response

The literal native word implements the full response E from
RESPONSE.md in both directions:

```text
F(x,y,h) = (x, y+E x, h),
B(x,y,h) = (x-E^T y, y, h).
```

The physical input convention is X=Qx and Y=y. The physical output
convention is X=F9 x' and Y=F9 Q^-1 y'. All 640 input columns are
independent. The 416 fields outside the two data banks remain
unchanged. No owned field or private field is used. This is a local
data service; it does not supply productive progress for those other
fields.

The exact local invoice, in either direction, is

| Quantity | Count |
| --- | ---: |
| Rank-one children | 1036 |
| Rank-three children | 48 |
| Rank-four children | 55 |
| Rank-five children | 55 |
| Rank-six children | 9 |
| Rank-seven children | 9 |
| All native children | 1212 |
| Native mass | 1792 |
| Real scalar primitives | 5288 |
| Endpoint adapters | 224 |
| Native side-map upper bound | 2424 |

The implementation checks 1141 distinct native edges and 224 endpoint
adapters with the independent Pauli and exact Gaussian-state
interpreter. These checks include global phase. They are separate
from the scalar-column replay.

## The large 48-port word

The pinned cyclic family supplies the exact paths and the
parameterized scalar events. At each of eight vertices there are six
pair-mode carriers. For every ordered pair of distinct modes, one
source flag and one target flag have the same actual binary frame.
The corresponding coefficient of the signed rank-two block is
substituted at that event. A zero coefficient omits that ADD only;
the fixed native path is retained.

The source and target pair codes use the exact pinned short factors.
The source pair code is applied after the two source lines reach
their pair plane. The target code is applied while both targets are
at I. The inverse source code is applied at FULL. The inverse target
code is applied at the common pair-perpendicular frame, before the
two targets reach their individual holes.

There are 176 nonzero mode coefficients. Of these, 136 are signed
units, 32 have absolute value two, and eight have absolute value
three. Their real ADD cost is 1504. The pair codes and inverse codes
cost 1880 across both data banks. The large-sector scalar cost is
therefore 3384. Its native profile is 624 H1 + 48 H3.

In the backward word, each source carrier receives the negative
coefficient times the corresponding target carrier. Since the pair
code H obeys H H^T=2I, removal of both codes gives the exact negative
transpose -E^T. No scalar response is moved through Q.

## The 64-port clique word

For each clique q0,...,q(k-1), the labels are orthonormal over F2.
At depth d=1,...,k-1, advance source i to

```text
S_i(d) = span(q_i,...,q_(i+d-1))
```

and target j to

```text
T_j(d) = span(q_(j-d),...,q_(j-1)).
```

Indices are cyclic. Then S_i(d)=T_(i+d)(d). Apply the signed unit
coefficient of I-J_k at this common frame. Every off-diagonal ordered
pair occurs exactly once.

Each source starts at its own line. Each target starts at I. After
the last transfer, advance each source to FULL and each target to
its own hole. Every target flag excludes its own q label and is
contained in that hole. Thus every native edge is nested, with
positive rank. No frame change on nonzero data is free.

For a five-clique, each port contributes seven H1 children, one H4,
and one H5. For a three-clique, each port contributes three H1, one
H6, and one H7. The eleven five-cliques and three three-cliques give

```text
412 H1 + 55 H4 + 55 H5 + 9 H6 + 9 H7.
```

There are 238 signed unit ADDs, with real scalar cost 1904.

## Phase and complete replay

The frame table is in canonical binary row form. For each native
edge old -> new, the compiler lowers the exact operator
Gamma_new Gamma_old^-1. A separate interpreter checks all Pauli
images and one exact Gaussian-state column. Together these checks
determine the complete Clifford operator and its global phase.
The child rank is independently checked against the frame-dimension
difference.

For each physical source line Q_p and each target convention
F9 Q_p^-1, an explicit rank-zero adapter relates the convention to
the canonical endpoint frame. All 224 adapters receive the same
independent exact phase check. Both pinned providers have the same
data directions. The new word is consequently the same for both;
the checker verifies that premise from each provider.

The serialized words are read back and replayed on all 640 input
columns. Every scalar ADD has exactly equal source and target
frames. Every native edge has the declared entry frame and a
nested exit. Every final data frame and every untouched field is
checked. Deletion of one nonzero transfer is rejected.

The maximum top-level prefix row one-norm is 46 forward and 30
backward. This does not bound the internal state of recursive
children. The complete recursive precision and host invoice remain
separate.

Run emit_native.py with --out and a new directory. Repeat with
optimized Python and a different new directory. The expected status
is PASS_LOW_DISPLACEMENT_NATIVE. Both payloads and receipts must be
byte-identical. The empty first-attempt directory is retained. That
attempt stopped before phase compilation because its temporary
binary-basis routine did not produce a unique row form. The final
emitter uses complete binary row reduction and checks every common
frame explicitly.

The response remains asymmetric on the 48-port sector. This packet
emits the raw backward transpose. It does not emit the full inverse
as a native response: the small clique inverse has nonzero diagonal.
The general-unit controller can use the explicit common-frame
inverse codes, subject to its own routed access and terminal duties.

The root reciprocal response, the independent-review cyclic flags,
the controller's pair geometry, and the oblique-native phase
construction are the predecessors. AI assistance was used. This
packet does not change the selected frontier or claim a complete
kappa improvement. No publication is authorized.
