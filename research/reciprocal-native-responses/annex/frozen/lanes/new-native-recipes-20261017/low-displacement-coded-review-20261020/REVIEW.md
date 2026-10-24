# Independent review of the low-displacement coded exits

All stated local checks pass. There is no material finding.

This review checks the exact output codes of the rank-thirty and
rank-sixteen native responses. The two codes act on both data banks:
`W48_I64` applies W on the 48 paired ports, and `W112` applies W on all
112 ports. The response matrix does not change.

The rank-sixteen uniform code uses children of rank at most three.
This resolves the rank-nine exit requirement of the earlier matching
path. It does not remove the output code or provide a recursive host.

## Inputs and independent method

The producer input is
[CODED-EXITS-FREEZE.json](../../new-core-transfer-20261017/low-displacement-20261020/CODED-EXITS-FREEZE.json),
at SHA256
`f466ce7bc9d6f5459462acd1799f269a6c2685aea124a3d18f579d542f269936`.
The decompressed payload SHA256 is
`7f7efbd4a080f641b7ffcb774c677c66344de60d57c6ecc67cdfc0e6f2f6f73d`.

The accepted raw phases are fixed by
[NATIVE-REVIEW-FREEZE.json](../low-displacement-review-20261020/NATIVE-REVIEW-FREEZE.json)
and
[EXTENSIONS-REVIEW-FREEZE.json](../low-displacement-review-20261020/EXTENSIONS-REVIEW-FREEZE.json).
Their SHA256 values are
`cfdc4fa0361aa79c1d53a59ff48bdde1715ea8e3eb6b9efbc109c97bcc44a976`
and
`c8fccfbe49ddd8747095a43aa1c1c59b0270bbbf73d94a317a79113191e4e34c`.
The earlier carry-W phases are fixed by
[the matching-code review](../matched-left-gauge-review-20261018/FREEZE.json),
at SHA256
`bc0352b29a7a7244ebea40e8b53e44fa5d16dbb645db87eecbe3e02cf3bbaf46`.

The checker imports no producer or Clifford compiler. It uses the
previously frozen reverse coefficient interpreter for the complete
field map. It uses a separate sparse Gaussian interpreter for each
fresh physical exit.

An inherited exit must have the same ordered entry basis, literal
output circuit, and complete phase recipe. Equal spaces or equal ranks
are not sufficient. The new packet has 352 distinct changed exits.
Of these, 48 are exact entries from the earlier accepted carry-W table.
The other 304 require fresh checks.

For each fresh exit, the check is

\[
 R T_{\rm old}=T_{\rm final}
\]

on every one of the 512 spatial basis vectors. Since \(T_{\rm old}\)
is invertible, this checks the entire operator
\(R=T_{\rm final}T_{\rm old}^{-1}\), including its global phase.
The recipe acts on arbitrary field contents. No zero input or clean
helper assumption is used.

The 304 fresh checks cover 155648 spatial columns and 56623104 exact
nonzero Gaussian coefficients. The word checks bind all 2560 changed
exit occurrences across the sixteen complete words.

Under the inherited tensor model, the complete one-column identity
extends to every field width. The constant phase is part of the
operator. In particular, a factor \(i^c\) in each of f tensor columns
gives \(i^{cf}\), and \(W_f^2=i^fI\). The finite check does not replace
these factors by width-independent phases.

## Exact physical output

Let \(A\) be the accepted response of the chosen family. The logical
forward and backward maps remain

\[
 F_A(x,y)=(x,y+Ax),\qquad
 B_A(x,y)=(x-A^{\mathsf T}y,y).
\]

The physical input is \(X=Qx,\ Y=y\). On a coded port p, the output is

\[
 X_p=W F_9 x'_p,\qquad
 Y_p=W F_9 Q_p^{-1}y'_p.
\]

On an uncoded port, omit W. The literal W circuit is
\(S_{e_0}C_{45}S_{e_0}\), with the phase convention of the pinned
gauge packet. W is placed on the left of the complete raw output.
No Q is moved through W or through the response matrix.

The checker binds every changed source exit to its actual last
ordered canonical basis and to the literal output circuit \(W F_9\).
It binds every changed target exit to
\(W F_9Q_p^{-1}\). This target replacement includes the old inverse
target adapter. The old adapter must be removed.

Every source adapter is retained. Every uncoded target adapter is
retained. Every rank-zero exit is an explicit monomial operation with
one side map. It is not an absent operation.

The same unitary code on both directions preserves the physical
inverse-adjoint relation. To see this, let
\(S=\operatorname{diag}(Q,I)\) be the physical input map and let T be
the declared output map, including the chosen W code. Both S and T
are unitary. The physical maps are \(T F_A S^{-1}\) and
\(T B_A S^{-1}\). Since \(B_A^*F_A=I\), their adjoint product is I.
This statement uses the same declared input and output maps. It does
not turn the coded output into the raw output.

## Complete event stream and arbitrary workspace

All sixteen words are checked: two responses, two codes, two providers,
and two directions. The new and raw event streams have the same event
positions. The checker compares every scalar coefficient and access.
It compares every unchanged native occurrence and its full recipe.
Only the declared final coded exits can change.

The typed frame ledger checks every transformation entry, every final
frame, and every equal-frame scalar ADD. The rational scalar schema
conversion is exact. A reverse pass checks all 640 independent input
columns against the accepted response.

All operations act on the 224 data fields. The other 416 roles retain
their arbitrary values and frames. There are no private fields,
owned fields, CLEAR operations, or hidden helper accesses. In
particular, unchanged helper state is not productive helper progress.

## Complete local invoices

Each row applies to both providers and both directions.

| Response and code | Native profile | Children | Mass | Real scalar primitives |
| --- | --- | ---: | ---: | ---: |
| Rank30, W48_I64 | 988 H1 + 48 H2 + 55 H4 + 55 H5 + 9 H6 + 9 H7 | 1164 | 1696 | 5288 |
| Rank30, W112 | 988 H1 + 48 H2 + 55 H5 + 55 H6 + 9 H7 + 9 H8 | 1164 | 1824 | 5288 |
| Rank16, W48_I64 | 1472 H1 + 112 H2 | 1584 | 1696 | 7384 |
| Rank16, W112 | 1408 H1 + 112 H2 + 64 H3 | 1584 | 1824 | 7384 |

Each word has 48 inline monomial exits. The mixed code has 176
external endpoint maps, and the uniform code has 112. Each native
child has at most two side maps. These maps are not assigned zero cost.
The child side-map upper bounds are 2328 and 3168 for the rank-thirty
and rank-sixteen families.

The scalar prefix array norm bounds are 46 forward and 30 backward
for rank thirty, and 22 in both directions for rank sixteen. These
bounds apply at the top-level event boundaries. They do not bound
primitive internals, recursive child internals, or roundoff growth.

The exact profiles explain the native-rank improvement. The large
paired source flags reach dimension six before the exit. W changes
their rank-three source exits to rank two, while their 48 target
exits become monomial. The rank-sixteen small-clique source flags
reach dimension seven. Their uniform-code source exits have rank
three, and their target exits have rank two.

The earlier matching path started the corresponding small source
exits at dimension one and needed rank nine. These are different
literal paths. The new result does not change the old phase result.

## Scope

The response matrix results and their inverses remain dependencies of
the accepted raw reviews. This packet changes only the local output
representation and its exact native profile. No odd division is added
to the native word.

The mixed code saves 96 units of native mass relative to the raw
1792-mass word. The uniform code uses 32 more units. A recursive cost
cannot be inferred from these mass differences alone. The profile,
side maps, source access, and child hosting must be included.

This review does not provide a free W inverse, a free stage transition,
a terminal decoder, productive helper progress, a complete precision
bound, or the complete supplier. It does not change the selected
frontier or establish an improvement in the complete kappa calculation.

## Reproduction

Run from the workspace root, with one CPU:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/low-displacement-coded-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/low-displacement-coded-review-20261020/normal
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -O -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/low-displacement-coded-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/low-displacement-coded-review-20261020/optimized
```

The required final line is:

```text
PASS_INDEPENDENT_LOW_DISPLACEMENT_CODED_EXITS
```

The checker also rejects retention of the old coded target adapter,
placement of W on the wrong side, and reduction of a child rank
without a new recipe. `REPRODUCTION.json` records the final comparison
of both runs and the final input hashes.

Both normal and optimized runs passed. Their result and input receipts
are byte-identical. The final hash check confirms that all 37 consumed
source files are unchanged.

The source packets retain credit for the cyclic paths, responses,
pair factors, and W construction. AI assistance was used. No PR,
push, commit, or publication is authorized. Before any future PR
description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
