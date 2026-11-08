# Independent first-face Reference join review

Separately assigned source-aware OpenAI Codex review for @CubeJerry. Read-only component and composition review; not human or proof-kernel certification.

## Source pins and verdict

No blocking composition error found in the tested version. SHA256 pins:

| Source under research/ | SHA256 |
|---|---|
| first-face-reference-join/join.py | 2631e4c41bd923230a57d723e4f903b1f38b1a3d9772ff87b76d5e1d7f2dc1e8 |
| shrinking-reference-halo/engine.py | 38ca22b213a0291cc7ba821baf513db289c1c3e7c24c579c5eff3349280484b2 |
| shrinking-reference-halo/tensor.py | b3cfe3c18988a89d4a639e8104db7a87f7029d556c74c2e0f60d687ec6be5e80 |
| sparse-halo-tape-transaction/tapes.py | 80b246fafae0adf53af7561e1be59f4374e6294d66bb7a12ef9524b9ef4f2a78 |

Final receipt revision: `join.py` SHA256 `8a9c2796207a03bda3881494c5b87d8076831a070ca05f9c492b7e6d0c60c1bf`. The numerical path is unchanged. The new receipt explicitly includes encoded plan parameters (including arbitrarily large J at W=0 and gap numerator/denominator) and monotone counters in its control carrier. Reviewed the changed receipt and reran the complete1D spectator fixture successfully against this hash. A zero-band descriptor with J=2^400 produced459metadata bits and517carrier units, confirming J is not bounded accidentally by the halo. Full two-axis replays were against the earlier positive-path hash; B separately reruns both modes of the portable oracle on the final package.

## All-size compatibility

For target interval [t,t+m), common saved halo b, and consumer halo b_i<=b, the codec keeps offsets b-b_i<=u<m+b+b_i and recodes v=u-(b-b_i). Thus (t-b_i)+v=t-b+u exactly before periodic reduction. This binds the consumer input to the canonical original-source suffix without translating or rephasing the reference. Coordinatewise interval filtering preserves lexicographic order, including when consumer packed field widths differ from the transport's ell+2 widths.

The consumer returns offsets b_i+r, 0<=r<m, hence canonical target t+r. The first boundary coordinate and its side uniquely determine the rectangle; prior axes are interior and subsequent axes unrestricted. These rectangles partition boundary targets. Each saved axis length is below its period, so local offsets are injective modulo the period. The actual one-hot face field sorts in reverse face-index order; `g-onehot.bit_length()` correctly decodes that order. Entirely missing rectangles can be caught by the complete dense return merge even when the local codec sees no record from them.

Payload bits pass physically and unchanged from the already-gathered source copies through the codec. The dense source is destroyed by the core test before the consumer runs. Negative zero is rejected by consumer numeric decoding, not silently normalized. Current interior words are kept as opaque bits. One fixed eight-role consumer pool is reused and cleared between rectangles.

All live codec metadata describes one rectangle, counters, and packed fields. The product counters have O(B) bits, and all coordinate fields together have O(B) bits. Sparse arithmetic can be charged O(w^2) per saved/returned record or rectangle. This is a macro tariff, not a measured finite transition count. The exact receipt width must include both grid precision and packed-coordinate widths; numerical and source-preparation costs are additional inherited charges. A subsequent receipt-only revision needs its own pin.

## Executed independent checks

Reproduce from the repository root (portable loader adapted for isolated mode):

    python3 -I -B research/first-face-reference-join/independent_review.py

Expected marker: `PASS_INDEPENDENT_JOIN_FULL_GRID`.

The oracle uses a dense full torus and its own signed quotient/coefficient rounding, applying the fixed-source recurrence axis by axis. It does not use consumer Layout, local rectangle assembly, apply_line, apply_tensor, or the author's standalone-consumer oracle for expected values. Host arrays are external test data only.

| Fixture | Saved | Returned | Cropped | Rectangles | Exact returned bits |
|---|---:|---:|---:|---:|---:|
| 1D32, spectator bit, common b1, consumer b_i=(1) | 32 | 16 | 0 | 8 | 352 |
| 2D32x32, common b1, consumer b_i=(1,0) | 1024 | 448 | 288 | 16 | 9856 |
| 2D32x32, common b2, consumer b_i=(1,2) | 1904 | 624 | 432 | 16 | 13728 |

Synthetic operators use signed nonstationary band entries, irregular identity holes and nonzero wrap entries. Both real and imaginary source components have both signs. The two-axis cases exercise zero consumer halo and nontrivial iterations on both axes. Transport action counts:1294652,77497511,137199151. Consumer read/write/move counts including archive cleanup:118624,4743360,13502688. Runtime about70seconds for these three cases.

Both Tape constructors and diagnostics inspect/snapshot throw throughout codec+merge+erase. External observers invoke saved originals outside production calls. Every case preserved the same eight role identities; all local roles ended at origin, zero live bits, with all retained backing zero. Archive bytes and origin were preserved; old prepared tables erased; saved bytes preserved before erase; all30transport roles except final erased.

Actually executed controls: raw negative-zero source rejected with `noncanonical negative zero`; a canonical source-suffix bit flipped through tape movement/read/write rejected with `canonical source suffix binds saved offset`.

Actual Reference(61,3,2,1,8,32): all20boundary target values exactly match the full-grid rounded recurrence. Source holes are11,32,53; hole32 is returned. Two nonzero periodic wrap entries are present. Source coefficients come from the authenticated service; expected evaluation uses the independent dense recurrence. Parent separately checked original inverse solves.

## Limits

Finite checks supplement the universal identity and partition proof; they are not a proof of all parameter instances. Arbitrary dimensions and unequal core-index widths were checked in the predecessor transport review, not exhaustively through this numerical join. General composition inherits the source band/gap/common-grid/radius contract and the consumer theorem. The entire composed numerical program still uses explicitly priced scalar/control macros. The core remains a destructive test double. No proof assumption is removed globally, and no new kappa is claimed.

## Integration replay addendum

The complete registered normal and optimized replays were subsequently run on
the final `join.py` hash `8a9c2796207a03bda3881494c5b87d8076831a070ca05f9c492b7e6d0c60c1bf`.
Both full two-axis runs and the actual-reference case passed. After excluding
only measured wall time, the independent semantic receipts agree exactly.
The portable review loader uses an exact path for `full_grid_oracle.py`, so
`-I` isolation is supported. This addendum records integration replay of the
independent oracle; it is not an additional independently written algorithm.
