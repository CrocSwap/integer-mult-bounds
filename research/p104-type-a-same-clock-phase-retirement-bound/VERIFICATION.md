# Verification

The fixed all-plus replay verifies original ±I endpoints, the
unchanged q=+1 erased endpoint, and a missing-query rank-one
control. Independent forward and reverse engines agree entry by
entry on the full 36-by-36 residual for roots 0/18. The common
off-diagonal minor has determinant 64.

The even-coefficient replay verifies the two rank-four calibration
controls and six balanced sign patterns. The first forward attempt
assumed the q=−1 witness indices also gave a nonzero minor at
q=+1. That minor was zero while the full q=+1 difference had
rank four. The corrected forward and independent reverse engines
agree on both calibrations and all six cases. The reverse engine
also detects a damaged control row.

The first independent reverse outer wrapper failed after writing
the complete scientific output because zsh reserves the name
`status`. The exact output was separately verified. The clean
package invokes that same engine directly, checks its process exit
and regenerates the receipt byte for byte.
[Diagnostic receipt](receipts/DIAGNOSTICS.json).

The diagonal replay compares 212 exact anchors across 216 checks.
Both engines agree on all missing roles and the six residual
ranks for the prepriced alternate pair 0/17. The reverse engine
verifies the nonzero 3×3 minor after a one-coordinate change for
every anchored role. The 630 pairs follow from the anchor proof.

The package regenerates both exact prices and six rank receipts
and matches their hashes. It authenticates the shipped payloads
against their original manifests. Altered caller, base price and
engine bytes, and duplicate dependency keys, are rejected. The
replay requires only CPython 3.12 and its standard library.

Direct CPython 3.12.14 replay exited 0 in 1.65 seconds. A
relocated Git-free replay with a cleared environment exited 0 in
1.80 seconds and reproduced all eight receipts byte for byte.
The registered repository runner checked the pinned canonical
source provenance and exited 0 in 2.10 seconds from staging.
The committed-tree check and hosted checks apply to the exact
publication head. [Local replay checks](receipts/REPLAY-CHECKS.json).

[Clean replay](README.md) · [Exact receipt hashes](receipts/SHA256.json).
