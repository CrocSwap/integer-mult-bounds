# Independent review of the portable unit-transfer extension

Result: PASS. No material finding remains in the frozen ten-file package.
No package file was changed during this review. This review covers the
implementation and its stated local contract. The coordinating agent's
new publication proof and README are not part of this snapshot.

The reviewed stage is
`publication/native-source-codes-package/unit-transfer-extension`.
The full file pins are in `UNIT-TRANSFER-PACKAGE-REVIEW.json`, SHA-256
`a2214f2c9d07ea1e7f1ab2269c11bab2ec0df78bd2fb45a6a6af043c075d4af1`.
The separate review checker has SHA-256
`bc0e6f3908c77a4694d3071b52954447d59745ea775416d9726f24809950216d`.

## Cold replay and source preservation

The reviewer copied only the ten implementation and certificate files
to `/private/tmp/unit-transfer-review-tcw16oox`. From that directory the
reviewer ran:

```sh
python3 -I -O -B /private/tmp/unit-transfer-review-tcw16oox/replay_unit_transfers.py --repo /Users/aliromman/.codex/worktrees/native-source-codes/IntegerMultiplicationBounds --out /Users/aliromman/Projects/IntegerMultiplicationBounds/work/centre-encoding-campaign-20261014/lanes/interface-proof/package-review-unit-transfer/cold-output
```

The observed output was:

```text
PASS_UNIT_TRANSFER_EXTENSION
Four published examples and both unit transfers passed all 712 formal input columns.
The eight positive and eight inverse native recipes passed all 8192 Gaussian columns.
The complete supplier and kappa calculation are unchanged.
```

Every cold output is byte-equal to the frozen stage output. The replay
receipt has SHA-256
`3e3bc56578c80ff37bf91bc18211b30d42e8ffb3996c935c3ba4be06f4056f4a`.
The new decompressed program payload has SHA-256
`91746d608eb40cd2463879637dee10b3682463ff6001024d723154a4903fde4a`.

The six inherited files are byte-equal to their Git objects at commit
`7649d9ceecec949541bec4bbde5929344166ba59`. The four published examples
retain their exact combined payload
`da312b84be11c580c129e284736dee81d55d63716d77611d839178c29ad25600`.
The source loader reads the archive through `git show` at
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`; it does not read a worktree
copy of the supplier. The cold entrypoint has no campaign import.
Its explicit checks remain active with Python optimization enabled.

## Separate reconstruction

The reviewer ran `review_unit_transfer_package.py` with `-I -O -B`.
It imports only the Python standard library. It does not import the
package producer, package verifier, or a campaign module. It independently
reads the pinned Git archive, derives the centre rows, reconstructs both
clean-J words, and reconstructs all five new boundary blocks. Both full
streams equal those reconstructions and the already reviewed local B/F
streams. The accepted local review pins are recorded in the new receipt.

Reverse propagation checks each new word on all 712 formal input
columns. The backward map is `(X-Y,GY)` and the forward map is
`(G^-1 X,Y+G^-1 X)`. The 480 arbitrary helper contents are restored under
their inherited complete native jobs. All eight owned private inputs
finish zero. The added boundary work uses only C0. It does not preserve
an arbitrary C0 value, and no inverse claim is made for private clearing.

The separate checker also checks every chronological source read, both
literal source inverse orders, and six successive source words. It
derives `RP=LK=I`, `LP=0`, the ordered formulas for G and its inverse,
`LG=R`, and `RG=R-L`. The rank-16 section has action
`P -> Z`, `Z -> Z-P`. Its 96-dimensional complement is fixed. The first
identity power for the actual source matrix is six.

All 8192 new native columns were checked with exact Gaussian integers.
The input child is the intrinsic positive `C_p`, before every inherited
entry adapter. The output child is the intrinsic inverse `C_p`, after
the complete forward endpoint and source update. Its left translation
is `p`; removing that translation gives the wrong inverse. The proof of
commutation with FULL uses their expressions as polynomials in commuting
address translations. The canonical hole frame ID supplies a subspace,
not a replacement for the retained full endpoint operator. These exact
identities tensor at every positive size and commute with a common
disjoint exterior frame. They do not remove routed access costs.

## Cost and controls

Each word has 20,694 ADDs, 707 SCALEs and 48 CLEARs. Its real scalar
allowance is 217,898: 202,138 for the retained core, 9,056 for the source
code, and 6,704 for the selected target update. It adds eight rank-one
children and sixteen monomial maps. The complete child profile is
`{1:2420,2:418,3:432,4:142,5:82}`, with rank mass 5530.

The separate exact formal triangle bounds have ceiling logarithms 100
for B and 86 for F. These are scalar-word bounds, not complete recursive
precision invoices. Monomial maps are counted; their full supplier
compiler cost is not included in the scalar total.

Separate controls reject omitted compensation, wrong factor order,
source coding on the wrong side of the core, output correction before
the source update, missing native lines, wrong inverse direction, and
wrong global phase. The cold package replay also checks the final private
clear, noncentral ordered-ring instances, singular M and M-I instances,
and each missing ring hypothesis. Its controls reject an FBF signed-swap
claim and a sixth-power claim for products from different charts. The
general ring proof has a separate proof review; finite matrix cases are
not a substitute for that proof.

The review checker is an external campaign artifact. Its input snapshot
and the accepted local-word comparison use recorded workspace paths.
The package entrypoint above is the portable reproduction path. Do not
present the external checker as a second portable package command.

Routed chart composition, controller closure, final source-code removal,
recursive child hosting, complete storage/address/precision costs, and
the final supplier invoice remain open. The forward companion is not
the inverse backward call. No supplier or kappa improvement is claimed.
