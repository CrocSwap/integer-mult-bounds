# Independent native review of route32

All stated local native checks pass. There is no material finding.

This review checks the complete raw native word for the frozen route32
response. It checks the declared response on all 640 input columns, the
actual frames and endpoint adapters, every new physical phase recipe,
and the complete local native and scalar invoice.

The response model and its centre capture codes have separate proof
obligations. This native review does not prove those algebraic claims.
It does not include the proposed common-root output gauge.

## Frozen sources

The producer
[freeze](../../new-core-transfer-20261017/low-displacement-20261020/route32/FREEZE.json)
has SHA256
`28354cf747adc5c2a10393f02035a936e0e0fa3f666717b419f4eaaeed1814af`.
The decompressed native payload SHA256 is
`2f037b4757c46efb849bcfd8ad6cc2919d8486c5a9001d6325152446caf0f3e5`.
Its embedded model must equal the model file at SHA256
`85d44223697700a916e4cffeb334c8f82179f6535f7b0db64a37eddf37bedf52`.

The prior accepted native tables are fixed by
[NATIVE-REVIEW-FREEZE.json](../low-displacement-review-20261020/NATIVE-REVIEW-FREEZE.json)
and
[EXTENSIONS-REVIEW-FREEZE.json](../low-displacement-review-20261020/EXTENSIONS-REVIEW-FREEZE.json),
at SHA256
`cfdc4fa0361aa79c1d53a59ff48bdde1715ea8e3eb6b9efbc109c97bcc44a976`
and
`c8fccfbe49ddd8747095a43aa1c1c59b0270bbbf73d94a317a79113191e4e34c`.
Their raw payloads are pinned separately in the checker.

The new word retains the actual 112 supplier port directions from the
accepted cyclic geometry. It declares no selected ports and uses all
112 ports in its ordinary bank. The review does not transfer a principal
inverse from the old selected-eight partition.

## Exact phases and legal access

The checker imports no producer, Clifford compiler, or producer phase
checker. It uses the previously frozen independent reverse coefficient
interpreter and the independent sparse Gaussian spatial interpreter.

The complete native table has 1049 entries. Of these, 752 have exactly
the same ordered input basis, ordered output basis, and full phase
recipe as an accepted rank-thirty or rank-sixteen entry. Each reused
entry records its accepted source key. Equal spaces or equal ranks
are not sufficient for reuse.

For each of the 297 new entries, the spatial interpreter checks

\[
 R T_{\rm old}=T_{\rm new}
\]

on all 512 input basis vectors. This proves the complete physical
operator \(R=T_{\rm new}T_{\rm old}^{-1}\), including its global phase.
Each exact comparison uses Gaussian integer numerators and powers of
two as denominators.

The fresh checks cover 152064 complete spatial columns and 25726976
exact nonzero coefficients.

All 224 external endpoint adapters are exactly equal to accepted
records. Their frame IDs also retain exactly the same ordered bases.
Their previous phase checks therefore apply. This review does not
repeat those accepted calculations.

Under the inherited tensor model, the full one-column operator
identity holds for every field width. Constant phases remain part of
the tensor operator: \(i^c\) on each of f columns gives \(i^{cf}\).
The review does not replace this phase by one width-independent factor.

At each native occurrence the frame ledger checks the actual field
and input frame, strict subspace inclusion, the ordered frame key,
and the exact child rank. Each scalar ADD must have the same actual
source and target frame.

These checks justify the coordinate interpretation of the scalar
word. If two fields have frame T, the physical ADD is
\(Tz_t+cTz_s=T(z_t+cz_s)\). A native step changes T but retains the
logical field. No spatial operator is commuted through a scalar
coefficient matrix.

## Complete maps and arbitrary state

Let E be the pinned response matrix. The exact logical maps are

\[
 F(x,y,h)=(x,y+Ex,h),\qquad
 B(x,y,h)=(x-E^{\mathsf T}y,y,h).
\]

The physical input is \(X=Qx,\ Y=y\). The physical output is
\(X=F_9x'\), \(Y=F_9Q^{-1}y'\). In particular, the backward response
is \(-E^{\mathsf T}\), not \(-E^{-1}\).

The checker replays both directions for each of the two providers.
It checks all 640 independent input columns by reverse propagation
of the output coefficients. It also confirms that the two providers
have exactly equal words. All final frames are checked.

Every operation acts on the 224 data roles. The other 416 roles keep
their arbitrary input values and frames. There are no owned fields,
private fields, CLEAR operations, or hidden helper accesses. These
unchanged roles receive no productive advance.

For each provider and direction, a negative control removes an actual
nonzero transfer. The resulting complete map must differ from the
declared response.

## Local invoice

Both directions and both providers have the same invoice:

| Item | Count |
| --- | ---: |
| H1 children | 944 |
| H3 children | 48 |
| H5 children | 64 |
| H6 children | 64 |
| Native children | 1120 |
| Native mass | 1792 |
| Real scalar primitives | 4312 |
| External endpoint maps | 224 |
| Native side-map upper bound | 2240 |
| Owned or private fields | 0 |

The scalar price check admits only the accepted dyadic ADD and unit
scale words. No odd division occurs in this native word. The endpoint
maps and child side maps are counted separately; they are not free.

The complete scalar prefix array norm bound is 14 in each direction.
This bound applies at the top-level event boundaries. It does not
bound the internals of a scalar primitive or a recursive child, or
give the full roundoff estimate.

The native mass still telescopes to eight for each data role. The
child profile and scalar cost differ from the earlier responses.
Equal mass alone is not an equality of recursive cost.

## Scope and reproduction

The checker establishes a native implementation of the exact response
stored in the pinned model. The determinant, correction rank,
route-class preservation, principal inverses, and two centre capture
codes require the separate model review. The cost of a capture code
is not included in the native invoice above.

The common-root gauge, moving-code transitions, legal access for a
subsequent inverse code, odd-denominator implementation, productive
helper progress, recursive hosting, terminal decoding, and the complete
supplier remain separate. This review does not change the selected
frontier or prove an improvement in the complete kappa calculation.

Run from the workspace root, with one CPU:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/route32-native-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/route32-native-review-20261020/normal
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -O -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/route32-native-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/route32-native-review-20261020/optimized
```

The required final line is:

```text
PASS_INDEPENDENT_ROUTE32_NATIVE
```

The final result and input receipts must be byte-identical.
`REPRODUCTION.json` records that comparison and a new hash check of
all consumed sources.

Both final runs passed. The result and input receipts are byte-identical.
All 28 consumed source files retain their pinned hashes.

The source packets retain credit for the route split, shared-root
geometry, cyclic flags, response, capture codes, and native lowering.
AI assistance was used. No PR, push, commit, or publication is
authorized. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
