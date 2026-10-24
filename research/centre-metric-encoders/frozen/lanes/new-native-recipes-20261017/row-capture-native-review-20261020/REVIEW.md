# Independent review of the selected-row native service

The frozen word forms the sixteen centre rows of the actual rank16
response in sixteen existing target fields. It preserves arbitrary
target baselines and all 416 fields outside the two data banks.
It uses no new field, private field, or odd-arithmetic scan.

The local service and its direct-FULL refinement pass the independent
checks below. No material defect was found. The output representation
has changed. Its use by a complete recursive caller remains open.

## Inputs and independent method

The main producer
[freeze](../../new-core-transfer-20261017/low-displacement-20261020/row-only-capture-20261020/FREEZE.json)
has SHA256
`5321a8ff856042c5ca30ce6b29b90a51ccd4dcf02317820243bfffbb433c84d8`.
Its decompressed payload SHA256 is
`7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2`.

The separate direct-FULL
[freeze](../../new-core-transfer-20261017/low-displacement-20261020/row-only-capture-20261020/DIRECT-FULL-FREEZE.json)
has SHA256
`f0d3b0d7c8d93e391089a2d28066dd02b4a9b28e306dea5f4e7cb5fc895b054e`.
Its decompressed payload SHA256 is
`fa3342f8b4ddf286f6f67922f4184486ec0162610e4de6a457de3eed0750504c`.

The actual source word is the rank16 extension at decompressed SHA256
`d466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4`.
The controller's scalar
[freeze](../../controller-followthrough-20261017/row-capture-20261020/FREEZE.json)
has SHA256
`0810ec37cb70d819a1d40f817476a41dd1151535309972af1b5b1db2bcb42baf`.

The checker imports no producer code. It constructs the pivot inverse
from the exact signed Hadamard Gram matrix. It then constructs C,
its inverse, CE, and the encoded response independently. It checks
the scalar words by reverse output-column propagation. A separate
forward row pass checks the complete map and every scalar prefix.

The physical phase interpreter is the pinned independent integer
Gaussian interpreter from the isotropic-pair review. It uses literal
address maps and exact Gaussian coefficients. It does not import
the producer's Clifford compiler or phase checker.

## Exact code and physical contract

The independent derivation is in [DERIVATION.md](DERIVATION.md).
Let \(E=I+UV\), and let P be the ordered set

```text
0,27,36,111,20,7,57,46,1,3,6,8,17,18,24,23.
```

Put \(W=V_P^{-1}V\). The actual pivot Gram matrix is
\(\operatorname{diag}(2I_8,I_8)\). This gives a direct exact inverse
for \(V_P\), with both inverse orders checked.

Define C to have rows W on P and identity rows elsewhere. The
correction \(C-I\) has square zero and rank sixteen. Thus

\[
C=I+\iota_P(W-\pi_P),\qquad
C^{-1}=I-\iota_P(W-\pi_P).
\]

The checker verifies both matrix inverse orders and both literal
scalar inverse orders. The code and inverse are dyadic and each
cost 1760 old real scalar units. They need no extra field.

The actual rows satisfy

\[
WE=\operatorname{diag}(-5I_8,-7I_8)W.
\]

The selected rows of CE are therefore those same sixteen queries
with multipliers -5 or -7. The scalar late-query word adds these
rows to an arbitrary existing target value. It costs 3424 units.
It does not divide by five or seven.

Write \(q=Q^{-1}\). For physical input \((Qx,y)\), the exact output is

\[
X'=F_9x,\qquad
Y'_P=F_9[C(y+Ex)]_P,\qquad
Y'_R=F_9[q(y+Ex)]_R.
\]

The selected values include the arbitrary baseline \(Wy\). No
baseline is set to zero or removed from the output contract.
Equivalently, \(Y'=TC(y+Ex)\), where T is \(F_9\) on P and
\(F_9q\) on R. This is an invertible output representation.
No step commutes C or E through Q.

## Complete operation order

The checker derives the deletion from the original literal word.
It removes all events whose target is selected Y. For each provider,
this is exactly 128 H1 calls and 122 scalar events. Those scalar
events cost 928 units.

Every retained event is inspected. No retained scalar event reads a
selected target. All retained events appear in their original order
and with their exact original bytes. Removing only one member of a
selected large pair fails the retained-read check.

The new complete word has four stages:

| Stage | Event interval, end excluded | Real scalar units |
| --- | --- | ---: |
| Current-I precode C | 0 to 232 | 1760 |
| Retained original word | 232 to 2622 | 6456 |
| Sixteen I-to-FULL children | 2622 to 2638 | 0 |
| Late common-FULL query | 2638 to 2886 | 3424 |

Every source and selected target has frame FULL before the late
query. Every scalar addition has the same actual source and target
frame. All final frame declarations are checked. The 96 ordinary
target declarations are unchanged. The selected targets end in FULL.

Both providers pass all 640 independent input columns. A separate
forward pass gives the same complete map. Every field numbered
224 through 639 retains its arbitrary input. No operation addresses
these fields. There is no CLEAR, hidden zero field, or new owned state.
Deleting the precode or late query is rejected by the full-column test.

## Physical phases

There are 1447 distinct retained native recipes. Each is byte equal
to the exact ordered frame pair in the already accepted rank16 word.
The inherited phase proof is pinned by
[the independent extension freeze](../low-displacement-review-20261020/EXTENSIONS-REVIEW-FREEZE.json),
at SHA256
`c8fccfbe49ddd8747095a43aa1c1c59b0270bbbf73d94a317a79113191e4e34c`,
and its base native review. This review does not repeat that full
phase sweep.

The new rank-nine recipe occurs sixteen times. The independent
interpreter checks all 512 spatial input columns against the exact
nine positive coordinate kernels. Every column has 512 exact
nonzero coefficients. The comparison includes the global phase.
A wrong global phase is rejected.

All 112 source entry adapters are exact inherited records. The
96 ordinary outgoing adapters are new explicit inverse monomials.
For each, the checker composes it with the accepted incoming
target adapter in both orders. Every one of the 512 input columns
is exactly the identity in both orders. This proves the outgoing
map to \(F_9q_p\), including phase.

No outgoing hole adapter is present on a selected target. Its
canonical FULL frame is exactly \(F_9\). These exact spatial
identities tensor to every width admitted by the retained primitive
contract. They are exact equalities, not equalities up to phase.

The checker verifies the executed recipes. The producer's
descriptive compiler circuits are not executed by this review.
Their intended endpoint functions are checked through the exact
inverse-adapter identities above.

## Direct-FULL refinement

The accepted native recipe convention uses
\(C_{e_0}\cdots C_{e_{r-1}}\) between its two monomial maps.
At rank nine, this is already the required \(F_9\). Identity
left and right maps therefore suffice.

The checker verifies that direct recipe on every spatial column.
It then compares both complete refined provider words with the
main packet. All events, frames, endpoint views, and matrices are
byte equal. Only the shared rank-nine recipe changes. Thus the
complete-word correctness proof transfers by exact substitution.
There is no need for a new logical-column replay of an unchanged
event list.

The refinement removes the two nontrivial side maps from each of
the sixteen new calls. It does not change their sizes or number.
The native side-map upper bound drops from 3040 to 3008.

## Complete local invoice and precision scope

Each provider has the profile

```text
1392 H1 + 64 H2 + 48 H3 + 16 H9.
```

This is 1520 recursive calls and native mass 1808. The complete
old scalar invoice is 11640. The direct refinement has 112 input
monomial views, 96 output monomial views, and at most 3008 native
side maps. It uses no odd-arithmetic scan or new field.

The high-rank calls remain sixteen rank-nine calls. A complete
recurrence must use their exact sizes. Replacing their costs by
native mass alone is not a complete cost calculation.

The exact content row one-norm over the entire emitted word is at
most 132. The additional content binary denominator height is one.
Both bounds include the precode and the late scaled queries.
Under the unitary native charts, the first bound also applies to
the per-field Hilbert norm at operation boundaries.

These are local content bounds. They do not price primitive
internals, recursive-child guards, rounding error, outer owner
views, or the full numerical precision requirement.

## Reuse and remaining scope

The row-replacement argument is structural. If a forward word has
independent source progress, an isolated selected target set, and
an invertible row code that can be formed at the common input
frame, replace those target paths by frame advances and a late
coded response query. The output retains every arbitrary target
baseline. The present word verifies all these premises.

The separate
[access packet](../../bridge-access-20261017/row-capture-access-20261020/FREEZE.json),
at SHA256
`9d4eda12aa32eb11d97f6a9a88c691152a0c9580ea678cceaacae3d9b06c5b11`,
binds the construction to its literal D25 owner views. This review
pins that packet but does not rerun its phase census.

That packet gives the next current-entry type as Q on selected
carriers and I elsewhere. This is not the old all-I target type.
A later caller must consume that type or implement its conversion.
No such conversion, final decoder, full controller, or recursive
host is included in the local invoice.

This review establishes local centre formation in existing output
fields. It does not establish a complete supplier or a kappa
improvement.

## Reproduction and credit

Run from the workspace root:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/row-capture-native-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/row-capture-native-review-20261020/normal
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python3 -O -B work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/row-capture-native-review-20261020/check.py --out work/centre-encoding-campaign-20261014/lanes/new-native-recipes-20261017/row-capture-native-review-20261020/optimized
```

The required final line is `PASS_INDEPENDENT_ROW_CAPTURE_NATIVE`.
`REPRODUCTION.json` records the byte comparison and final source
hash checks.
Both runs completed with that result. Their result and input
receipts are byte identical. All 44 consumed source files were
rechecked and are unchanged.

The producer proof records the source, cyclic, controller, and
bridge-access contributions. The independent review supplied the
direct-FULL identity-map deduction. AI assistance was used.
No PR, push, commit, or publication is authorized. Before any future
PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
