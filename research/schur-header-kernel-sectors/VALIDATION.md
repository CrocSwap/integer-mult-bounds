# Verification record

The registered check passed in isolated, warning-strict CPython 3.12.13,
in normal and optimized modes. Both runs printed
`PASS_SCHUR_HEADER_KERNEL_SECTORS` and matched RESULT.json.

The complete H domains contain 1,244 matrices: all d=1,2,3 matrices over
F2 and all d=1,2 matrices over F3 and F5. The 98 additional cases vary
singular 00 factors, source-sector bases, padding, endpoint Jordan chains
and repeated nonsplit factors. There is a separate empty-00 case and six
rejection or necessity controls. Each accepted case builds the full original
commuting projectors, the header, the identity pivot and the actual Schur
pair. It checks rank K=2d, every returned basis, the independent joint-kernel
dimensions and the complete central similarity invariants. The receipt
records the full finite domain digest. It is not an all-field proof kernel.

Four actual code mutations failed in both modes before receipt comparison:
an unprojected 00 basis, an incorrect 11 dimension, omission of the two
pivot deductions from a1, and removal of the sharp factor-rank gate.

The eight retained predecessor files match their pinned bytes. The source
classifier, matrix helpers and complete-invariant oracle are unchanged.
The full-history wrapper is unpassed in this shallow checkout. Direct
ancestry checks for every declared source pin, the committed-byte check,
official export integrity and read-only Git-free replay are separate
publication checks. Their receipts are kept with the public handoff.

No independent human or proof-kernel review, Lean, native tape, selected
cold replay, full caller/compiler test or complete kappa calculation was
run. No physical cost, header probability or ordered-pair classification
follows from this finite check.
