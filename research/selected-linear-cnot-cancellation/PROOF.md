# Twenty-five CNOTs for the selected left binary map

Claim type: an exact finite word certificate and a scoped all-column proof.
This contribution was produced by Nick Petalas. Apache-2.0.

## Source and new step

Jerry Chen / CubeJerry's [PR #7430](https://github.com/CrocSwap/integer-mult-bounds/pull/7430),
head `39b40c465f7636a4bb6d70af28595fe8f70f4f3f`, binds the left binary
factor of selected MOVE24472 to the matrix with row masks

```text
G = (3, 5, 9, 17, 32, 65, 129, 1, 256).
```

Bit i in a row mask is the coefficient of input coordinate i. Thus

```text
Gx = (x0+x1, x0+x2, x0+x3, x0+x4, x5,
      x0+x6, x0+x7, x0, x8),
```

where every addition is in F2. That source's
[MATRICES.json](https://github.com/CubeJerry/integer-mult-bounds/blob/39b40c465f7636a4bb6d70af28595fe8f70f4f3f/research/literal-selected-linear-maps/MATRICES.json)
records a 27-gate left word. Gate pairs are `(target, control)` in temporal
order, with action `x[target] ^= x[control]`.

The new step removes its adjacent gates at zero-based positions 5 and 6.
Both are `(1,0)`. For `E=I+e1 e0^T`, the scalar product `e0^T e1` is zero,
so `E^2=I` over F2. The full product is therefore unchanged after removing
this adjacent pair. This elementary involution identity is classical; the
contribution is its application to this specified word and the shorter
explicit certificate.

The resulting 25-gate temporal word is

```text
(7,0) (6,0) (4,0) (3,0) (2,0)
(0,1) (1,0) (2,1) (1,2) (2,1)
(3,2) (2,3) (3,2) (4,3) (3,4)
(4,3) (5,4) (4,5) (5,4) (6,5)
(5,6) (6,5) (7,6) (6,7) (7,6).
```

The verifier establishes this new word's matrix identity directly by row
addition from I, rather than relying on correctness of the predecessor's
word. A separate explicit-coordinate oracle checks its entire address
action. No predecessor executable is imported or replayed.

## Every positive column multiplicity

For any positive integer f, let each xi be an arbitrary vector in F2^f.
Apply every gate by componentwise XOR. A gate acts independently on each
bit column, so the new word is the direct sum of f copies of G under the
coordinate/column regrouping. The same cancellation holds at every column.
Consequently the map on all nine f-bit coordinates is exactly G, coordinate
8 is fixed, and reversing the word is its inverse. Any additional untouched
coordinates or payload indices remain fixed as well.

Executing one coordinate CNOT at each column uses 25f elementary column
CNOTs, compared with the cited 27f. This saves exactly 2f such calls. This
is a gate-count statement, not an exact local tape instruction count.

The endpoint equality also holds as a permutation of an arbitrary payload
array indexed by these addresses: every source address has the same image.
It does not supply a new physical staging, erasure or owner-return program.

## Verification and limits

The checker evaluates the new word on all 512 addresses at f=1 and all
262,144 addresses at f=2, including the inverse and the spectator at every
address. It also checks the exact nine-row matrix identity. Three controls
reject an extra deletion, reversed control directions, and a purported f=2
implementation that only updates the first bit column.

The all-f statement follows from the direct-sum proof above; the finite
censuses are corroboration. No minimum CNOT count is claimed. The right
factor, phase recipes, offset, central native operator and the selected
frontier are not improved here. Integrating the word into the literal tape
compiler, executing its new graph, and measuring complete instructions and
historical storage remain open. No physical speedup, supplier admission,
complete multiplication theorem, or new kappa is claimed.

The selected five framework assumptions remain. Independent human and
formal proof-kernel review are unclaimed. The source's matrix/source binding,
27-gate comparison point, and literal implementation belong to Jerry Chen /
CubeJerry. Credit also its #3834, #5188, #6992 and retained native/compiler
lineage. Their results are cited premises, not validation deliverables here.
