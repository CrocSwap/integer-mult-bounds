# Independent finite frame ledger for PR2917

**Finite accounting audit; no new κ or supplier admission.** This package checks
Mason Hale's nine additional paired-helper extractions in
[PR2917](https://github.com/CrocSwap/integer-mult-bounds/pull/2917), pinned at
`224bd5e56041c40078ff6b5fa7393733a215de5c`. Both `base` and `extra` providers pass.
The immediate parent is Jeremy Diviney's [PR2908](https://github.com/CrocSwap/integer-mult-bounds/pull/2908)
at `51309592971e3b5be935599eed2a95404dc7781e`.

## What this adds

The predecessor `vendor/preload_move.py:frame_report` and
`vendor/audit_local.py` both use essentially the same pivot-basis and climb
calculation. Here a frame is its complete subset of `GF(2)^9`: at most 512
vectors, constructed by XOR closure. Dimensions are obtained from cardinality;
containment and equality are set operations. No predecessor Python is imported
or executed. This is a different implementation of the **frame implication**,
not a claim of independent verification of the whole construction.

The new replay derives every positive climb, every separate centre descent,
and the terminal climbs from the ordered operations. It checks actual subspaces,
not merely dimensions, including signed prelude warps, all 512 images of each
invertible warp map, dual perpendicular transport, lifted frame maps and the
symplectic identity. It then compares the derived histogram with the word's
report. It reconstructs nine sequential **frame projections**, checks each
declared old-frame preimage and candidate index, and compares the final
frame-bearing sections with the frozen final word. Compensation algebra is not
part of that projection.

| Derived quantity, for either provider | Parent | Final |
| --- | ---: | ---: |
| Paid profile | 2407 H1 + 640 H2 + 262 H3 + 128 H4 + 26 H5 + 8 H8 | 2416 H1 + 640 H2 + 280 H3 + 110 H4 + 26 H5 + 8 H8 |
| Positive paid events | 3471 | 3480 |
| Paid rank mass | 5179 | 5170 |
| Sum of 408 helper widths | 3323 | 3314 |
| Width inventory | 4:26, 5:2, 7:62, 8:87, 9:231 | 4:26, 5:2, 7:62, 8:96, 9:222 |
| Private cleanup buffers | 73 | 82 |

The extraction order is `424, 428, 412, 331, 299, 320, 511, 304, 499`.
Each of the first three steps changes the profile by `3 H1 - 2 H2`; each of
the last six changes it by `H2 + 3 H3 - 3 H4`. Therefore the net change is
`9 H1 + 18 H3 - 18 H4`. Each extracted helper changes width from nine to eight;
all other widths are unchanged.

All **13** declared frame edits satisfy the stronger geometric identity
`new_frame = old_frame ∩ E_normal`, with `E_normal` the extraction hyperplane.
Twelve edits lower an A-operation frame from dimension eight to seven. The
thirteenth lowers helper499's inherited `restore[40]` scale frame from nine to
eight. Restoring only that frame to FULL makes its later rank-eight touch at
`restore[114]` illegal, although the scalar operation itself is unchanged.

A useful cross-check telescopes the frame dimensions. Warps preserve dimension;
ordinary climbs sum to endpoint dimension minus entrance dimension. Centre
readout descents are charged separately and do not lower the main-word carrier.
The source/target contribution is `112*8 + 112*8 = 1792`; eight centre descents
contribute 64. Thus:

```
parent: 1792 + 3323 + 64 = 5179
final:  1792 + 3314 + 64 = 5170
```

The cleanup audit independently constructs the inverse-reverse **syntax** of
the forward non-target program, omitting the prelude, and substitutes `704+h`
for every protected helper `h`. It checks every actual cleanup operation,
reciprocal/negated coefficient, inverse warp identifier, full frame and private
buffer name. The buffer sets equal exactly `704 + helper_final`, with no direct
cleanup reference to a protected helper. This does **not** prove that those
buffers return to zero. Intermediate stage cleanup is derived syntax, not
comparison against separately stored stage words.

## Reproduce

Python 3.12, standard library only. From repository root:

```sh
python3.12 -I -B research/paired-helper-frame-ledger/verify.py
python3.12 -I -B research/paired-helper-frame-ledger/test_verify.py
python3.12 -I -B -O research/paired-helper-frame-ledger/verify.py
python3.12 -I -B -O research/paired-helper-frame-ledger/test_verify.py
python3.12 -B scripts/research_package.py --package research/paired-helper-frame-ledger
```

Expected marker: `PASS_PAIRED_HELPER_FRAME_LEDGER`. Verification is read-only.
The local environment, successful commands and reviewed code hashes are recorded
in [VALIDATION.json](VALIDATION.json); hosted CI is separate.
`RESULT.json` records both providers, all stage profiles, exact edit locations,
section histograms and hashes of the derived event ledgers. To inspect every
paid event and helper width, use `verify.py --details` and redirect stdout to a
file **outside** the package. This output is freshly calculated, not loaded from
the frozen receipt. Exact comparison uses canonical JSON so that Boolean and
floating aliases cannot stand in for integer receipts.

`INPUTS.json` pins the four gzip words, nine transform JSON files and retained
credit text by SHA256, byte length and Git blob. The wrapper also pins the
manifest itself. These are immutable source bytes, not regenerated compressed
outputs. The source commit and original paths were authenticated against Git
at intake; offline replay checks the frozen source inventory and bytes.
`SOURCES.json` pins the original catalogue and selected-record provenance;
they are not live mathematical inputs. The generic metadata check needs that
base Git history. The standalone replay needs only this directory.

Controls cover equal-rank unequal frames, chronological ordering, warp preimages
and invertible but wrong maps, omitted endpoint charges, forged inventories,
the helper499 scale refit, cleanup aliases/inverses/types, transform bindings,
input corruption and strict JSON. A separate XOR-pivot oracle checks all 128
generating subsets of the seven nonzero three-bit vectors, their 16 subspaces
and all 256 ordered containment pairs. Checks remain active under `-O`.

## Scope and overlap

The `independent-moment` card was selected with OS nonce
`9e2c1aa952cf9f74c87b48ad6e7d6ac1` from priority revision 5 at main
`8c8bcecb03def61bca701dd3b045932d39c48022`. Its rank-ledger method was refined
to this new nine-step input. The
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18972911)
records the boundary with mdumitrean's concurrent allocation work on PR2917.
The entry overlap search covered 476 open PR bodies including drafts, 2657
local notes/tasks/ledger records, and manually inspected relevant current
Discussion threads. Cached PR pagination is a non-atomic snapshot; Discussion
pagination, arbitrary diffs and unpublished work were not exhaustively covered.
No matches would not certify novelty. See `TASK.json` for exact coverage and
remaining questions.

This audit does not replay the predecessor's scalar or free-operator identities,
compensation correctness, 632-column forward/dual audit, native implementation,
buffer-zero proof, owner allocation, physical stock, precision, moment/root
calculation, outer admission or all-size/compiler hypotheses. It does not
change the selected record, any predecessor package, or the frontier. The
82 cleanup names do not establish an 82-register feasible physical schedule;
the inherited ambient dimension 73 is a different quantity.

## Open next questions

1. Does the pinned final word, including compensation and cleanup, have the
   claimed operator endpoint and zero-buffer behavior? A reviewer can first
   authenticate PR2917's full source closure and replay its declared operator
   checks. This package supplies only the frame/accounting component; primary
   success and independent coverage must remain separate.
2. Does a source-bound native owner allocation for that unchanged word satisfy
   complete physical-stock, precision and outer-admission obligations? Continue
   from the current canonical allocation claim, first checking its exact word
   and allocation pins. A local cap or profile alone cannot discharge those
   obligations. That work is intentionally left to its active owner.

## Credit

Prepared by ToikY with substantial OpenAI Codex assistance, including separate
AI implementation, adversarial-test and mathematical-review agents. This is
not independent human review or proof-assistant verification. New code and
documentation are Apache-2.0.

Mason Hale contributed the nine extractions and 13 enabling frame edits in
PR2917. Jeremy Diviney supplied the immediate paired-helper408 construction
and compensation/cleanup architecture in PR2908. Jeremy Kothe supplied the
preload and frame chronology in PR2894 (`18d03c447886895ef9abf888398178e0428533ca`)
and PR2833. Retained upstream attribution, including Yiyang Lu, Dugongue,
Marius-Paul Dumitrean, Philippe Van Velzen, Tekalign and icekylinx, appears in
the byte-identical [SOURCE-CREDITS.md](SOURCE-CREDITS.md). Its descriptions of
the primary package's replay are predecessor statements, not checks claimed
by this audit. No predecessor executable code is vendored here.
