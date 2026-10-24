# A native orthogonal response on 64 ports

This note changes the scalar weights of the native interior unit from
`oblique-native-20261017/interior-cut/UNIT-RESPONSE.md`. It does not change a
native call. The new unit has a symmetric 64-port restriction whose square
is `4I`. Its other 48-port restriction is unchanged.

The complete local word costs 86,664 real scalar primitives. It has native
rank mass 5,073 and 3,507 native children. The complete emitted forward and
backward words pass the ordered replay on both source providers. Each
replay checks 640 input columns, restores 408 arbitrary helper fields and
91 private zero buffers, and leaves the eight owned fields zero.

This is a local result. It does not establish a whole-supplier decoder,
cross-stage code transport, or a change to the complete kappa bound.

## The construction

Use the pinned factorization `E = L R` in `UNIT-MODE-CANDIDATE.json`.
Each column of `L` and corresponding row of `R` is one selected response
mode. Multiply the weight of mode `j` by two when

`0 <= j < 64` and `j mod 4` is `2` or `3`.

Keep every other selected weight equal to one. Exactly 32 weights change.
The new factorization is `E_new = L W R`, where `W` is diagonal. Thus

`det(E_new) = det(L) det(W) det(R) = -2^88`.

The matrix remains a unit over the dyadic rationals. The checker verifies
the factorization, its two factor determinants, and the response by a
separate sum of the pinned response directions.

The support has sixteen independent four-by-four blocks and one
48-by-48 block. On each small block, this weight change replaces the two
half-weight modes by unit-weight modes. For example, the block with rows
`[1, 6, 28, 58]` and columns `[75, 82, 86, 93]` becomes

```text
 1  1 -1  1
 1  1  1 -1
-1  1  1  1
 1 -1  1  1
```

Its rows are orthogonal and have squared length four. Its paired block is
its transpose. The full 64-port restriction is therefore symmetric and
has square `4I`. Its inverse is one quarter of itself. The checker proves
these identities by exact matrix multiplication on all 112 coordinates.

The scalar change costs 64 more primitives than the source unit. The
native records are byte-identical to the retained source records.

## Physical scope

The backward word supplies the negative transpose of the forward
response. On the 64-port restriction, that transpose is four times its
inverse. This removes the local transpose-versus-inverse distinction on
those ports, up to a dyadic scalar.

This identity does not identify two different routed stage charts. It
also does not allow a future-stage query on a completed X bank. A supplier
that uses this response must prove the chart transitions and the terminal
map with the physical Q operators in their actual order.

## Reproduction and source credit

Run from the workspace root:

```text
python3 work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/partial-orthogonal/check_partial_orthogonal.py
python3 -O work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/partial-orthogonal/check_partial_orthogonal.py
```

Both commands must end with `PASS_NATIVE_PARTIAL_ORTHOGONAL_RESPONSE` and
the same payload hash. `PARTIAL-ORTHOGONAL.json` gives the full local bill.
`PARTIAL-ORTHOGONAL-PROGRAM.json.gz` contains both native words for both
providers. `FREEZE.json` pins the source and result files.

This work uses the native interior-unit construction and response space
from the oblique-native lane, and the native replay and cost model from
the new-core-transfer lane. It is AI-assisted research. It is not a PR or
a selected frontier result.
