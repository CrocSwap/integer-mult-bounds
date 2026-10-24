# Independent review of reduced selected interfaces

All 18 complete frozen words pass the independent review. The short
eight-port normalized backward word costs 89,200 real dyadic scalar
primitives. The short 24-port word costs 89,592. Each has 3,507 native
children with rank mass 5,073. No material defect was found.

For each selection and both providers, the short and long words have
the same complete map on arbitrary data and workspace. This is stronger
than equality of the original-X block. The review covers all borrowed
Y terms, the actual order of port operators, every helper output, and
all private and owned outputs.

## Exact inputs and method

The producer freeze is
`new-core-transfer-20261017/bipartite-eight-transfer-20261018/FREEZE.json`,
SHA-256
`84b1156a0c58ced62ee5834a92d02147346032f7a8beb181b3efe35a539d86f1`.
Its payload has decompressed SHA-256
`740c10032c464723f4cdfecf054ef586832f9563055c62d48a78b6d9f055b62d`.
The eight-port response source freeze has SHA-256
`c147770b253d8b33a18ba6edb766ab505d203ba8ecd16507764d9a8c1c98e1c1`.
Its payload has decompressed SHA-256
`0c832994c1d06562a8db0b9b3d940f6f6143c37beed983f874a69f2bf6ecfdee`.
The checker verifies the complete frozen artifact manifests.

The review imports no producer module. It uses the previously frozen
independent reverse interpreter from
`structured-transfer-review-20261018/check.py`, SHA-256
`d55b2bcdce6764fb97d38bae212840047a739ecf20f17d180f3435e613e2df90`.
That review's freeze has SHA-256
`fade8160a807a2687a007a67dec3f21cfe4ebcc1840130c6650e4e2acbc6fa3b`.
This extension adds a separate rational elimination routine. It derives
the required block inverses directly from the actual response matrices.
It does not use a producer-supplied inverse as its expected result.

The interpreter pulls output columns backward through each full word.
All arithmetic is exact. Each port Q and each native warp is a free
invertible operator. Only adjacent inverse letters cancel. Forward
and backward warp alphabets are disjoint. No step assumes that a port
operator commutes through a coordinate matrix.

## The general normalization reduction

Let the actual symmetric core response be

```text
J = [L B]
    [D H].
```

After the selected physical input exchange, the raw backward word gives

```text
X_S = q b - L Q a - B v,
X_U = u - D Q a - H v,
Y_S = Q a,
Y_U = v.
```

The original-X coefficient, acting on `z=(Qa,u)`, is

```text
C = [-L 0]
    [-D I].
```

If L is invertible, the exact inverse is

```text
N = [-L^-1    0]
    [-D L^-1  I].
```

Thus first apply `X_S <- -L^-1 X_S`, then apply
`X_U <- X_U + D X_S`. The second step must read the changed selected
fields. The full result is

```text
X_S = Q a - L^-1 q b + L^-1 B v,
X_U = u - D L^-1 q b - (H-D L^-1 B)v,
Y_S = Q a,
Y_U = v.
```

This reduction needs only an implementation of the selected inverse
and the lower shear at the common completed frame. It does not need
H inverse or the inverse of the full response J.

For comparison, suppose H is invertible and put

```text
U_B = [I -B],     A = U_B diag(I,H^-1) C.
      [0  I]
```

The long scalar suffix is
`A^-1 U_B diag(I,H^-1)=C^-1=N`. This proves equality of the entire
suffix maps, including all borrowed terms. The checker verifies this
identity by independent exact matrix inversion and verifies both
literal complete words against the same ordered expected map.

## Actual eight-port construction

The selected set is
`[0,7,15,36,42,46,79,89]`. The checker derives all blocks from the actual
signed source response. Exact elimination gives `det(L)=1/16` and
`det(H)=2^60` on the full 104-port ordinary bank. It verifies both
inverse orders for L, H, C, and A. Every entry in these maps and their
inverses is dyadic.

The selected inverse is a literal 28-operation scalar word at cost
192. The lower shear has 144 ADDs with coefficient magnitude `1/2`,
at cost 1,440. The complete short suffix costs 1,632. The raw backward
core with its selected exchange costs 87,568. Their total is 89,200.

The two ordinary gauges each cost 3,696. Each contains the exact
previously reviewed 64-port Hadamard word, with its 32 physical
exchanges included in the scalar bill. The current 40-port ordinary
gauge is also checked as a literal scalar word. No eight-port boundary
word reads or writes an owned or private field.

| Eight-port complete word | Scalar primitives |
| --- | ---: |
| Raw backward | 87,568 |
| Balanced backward | 91,264 |
| Diagonal backward | 92,704 |
| Long normalized backward | 99,472 |
| Short normalized backward | 89,200 |
| Raw forward | 87,776 |
| Balanced forward | 91,472 |

The short normalization saves 10,272 primitives relative to the long
word. This equals two complete ordinary gauges and two upper shears:
`2*3696+2*1440=10272`.

## Actual 24-port construction

All records of the old scaled 24-port long word are unchanged in the
new packet. The new short suffix implements the same N at cost 1,608. The
complete words therefore cost 96,012 and 89,592, a difference of 6,420.
Both are checked as complete native computations.

The short suffix uses the existing C0. Each centre row queries six
selected fields, divides this dyadic query by four, and scatters the
negative signed query to its 12 supported ports. The selected row has
squared norm six. Thus its updated query is minus one half of its old
query. Scaling the stored quarter-query by minus two and subtracting
the updated query restores C0 to zero. Distinct selected row queries
are orthogonal, so the other row queries are unchanged by that scatter.
The final 24 selected negations produce N.

The reverse checker inserts zero observables before every COPY into C0
and every CLEAR after the first admission. The short complete word has
ten such observables; the long complete word has 20. Each observable
pulls back to zero. Thus no data-dependent query is erased before reuse
or during the final frame reset.

## Native records, frames, and arbitrary workspace

Every complete retained core equals the corresponding frozen source
core. Every native event equals its counterpart in the clean provider
word. The complete canonical geometry also equals the exact compressed
phase-provider input bytes. The review checks all scalar frames, native
child ranks, warp classes, adapters, residual helper endpoints, and
private lifetimes.

Each complete replay covers 640 input columns: 224 data fields, 408
helper fields, and eight owned fields. It also checks all 91 private
output fields. Helpers are restored in the source logical coordinates,
with the exact inherited physical wrapper contract. Private outputs
are zero. All owned outputs are zero in the initial frame. Owned
admission is the permitted CLEAR operation; arbitrary borrowed helper
restoration is a separate checked condition.

The actual endpoint conversion is explicit. Physical input X is the
portwise Q transform of logical x. At the completed output, after the
common FULL transform is removed, physical X is logical X and physical
Y is the portwise inverse-Q transform of logical Y. The complete
normalized original-X block is exactly `diag(Q,I)`. Every selected
physical Y output is the common FULL transform of the original a.

Both families reject a test that incorrectly moves the diagonal Q
factor across the full data inverse in the borrowed term. Both
eight-port providers also reject a test that performs the lower shear
before the selected inverse. These controls test the two order claims
that are decisive for the construction.

The native profile is unchanged in all 18 words:
`2433H1+724H2+228H3+102H4+20H5`. This is 3,507 children and rank mass
5,073. No native child or private field is added. No odd-division scan
is used. The scalar bills include the complete core, every physical
selected exchange, every boundary gauge, and all owned operations.

Native phases inherit the exact earlier orientation-specific phase
review. This extension introduces no native event and does not rerun
the native phase interpreter. The source pins and unchanged event
bindings make that dependency explicit.

## Scope

The result establishes complete local interfaces and a reusable
normalization reduction. It does not establish inter-stage code
transport, all caller views, caller exterior phase closure, child
hosting, recursive precision, a complete supplier, or a new complete
kappa bound. The small selected inverse does not by itself supply a
global controller.

## Executed verification

From the workspace root, both commands passed:

```sh
python3 -I -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/reduced-transfer-review-20261018/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/reduced-transfer-review-20261018/verified-normal
python3 -I -B -O work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/reduced-transfer-review-20261018/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/reduced-transfer-review-20261018/verified-optimized
```

Each run ended with `PASS_INDEPENDENT_REDUCED_SELECTED_INTERFACES`.
The receipts and input records are byte-identical between the two
modes. The receipt has SHA-256
`ec9ecf398f9f79981c0fa2001019122b0bbabc591ca6b08aa3be4d9e44fd3abf`.
The input record has SHA-256
`fd7a6502f8639fa07b8c2a408dcb525cbda42c8a44d9f2539737dcc1a20da89a`.
All claim checks use explicit exceptions and remain active under `-O`.

The proof, checker, and review records use AI assistance. Source and
previously frozen review files were preserved. No PR, push, commit,
or publication was made.
