# Paid overwrite-COPY transposition audit

Mechanical transposition of the selected R480 FULL cleanup after PR696 lowering costs 30,732 real-component primitives, versus 26,541 for the original stream. The exact surcharge is its 4,191 overwrite COPYs. Directly lowering the transposed macros costs 26,541 and realizes the same full transpose. Thus this is an accounting audit, not a supplier improvement or a claim that transposition must increase the best circuit cost.

| Complete cleanup implementation | Real-component primitives | Complex primitives |
| --- | ---: | ---: |
| Forward PR696 lowering | 26,541 | 53,082 |
| Reverse the primitive stream and implement each full transpose | 30,732 | 61,464 |
| Reverse/transpose the macros, then apply PR696 lowering | 26,541 | 53,082 |

All three use the same 6,680-macro cleanup and one coefficient-work register. Every COPY, ADD/SUBTRACT, CLEAR, double, halve and negate is charged. The explicit primitive inventories and exact matrix digests are in RESULT.json.

## Reproduce

From the repository root, Python 3.10+ with the standard library:

~~~text
python -I -O -B research/paid-copy-transpose-audit-seed67/verify.py
python -I -O -B research/paid-copy-transpose-audit-seed67/test_package.py
~~~

Expected: PASS_PAID_COPY_TRANSPOSE columns=705 controls=6 no_new_kappa, followed by forward/mechanical/direct 26541 30732 26541. The package test reports one minimal relocation and five rejected corruptions. --write regenerates the deterministic result receipt. All runtime checks remain active with -O.

## Precise obligation

On coordinates (s,t), overwrite COPY t <- s has matrix [[1,0],[1,0]]. Its ordinary transpose maps (s,t) to (s+t,0), implemented by ADD s += t followed by CLEAR t. A reversed COPY is wrong: it loses the old s contribution and preserves the wrong output. In the pinned primitive vocabulary, each primitive changes only one destination; the transpose changes both. The verifier also exhausts all 15 programs of length zero or one on two registers with distinct binary operands, with a separate numeric-column implementation. The exact minimum is two for this isolated map and vocabulary, with no extra wires.

ADD/SUBTRACT transpose by swapping source and destination; CLEAR is a self-transpose projection, and diagonal double/halve/negate remain themselves. The primitive order must be reversed. No inversion of a halve is performed. Consequently the literal gate-by-gate transpose costs L + N_COPY; this formula does not describe a globally resynthesized transpose.

The checked full map includes 704 scalar inputs plus an arbitrary private-work input. Its form is diag(M,0), since work is discarded and zero on exit. The mechanical transpose and direct macro lowering both produce diag(M^T,0). This statement concerns the entire 705-dimensional linear map. It is not an inverse of a singular map or a claim derived only from initializing work to zero. The 704 scalar coordinates include caller sources, targets and dirty helpers; none are silently initialized.

The primitive row interpreter reconstructs all three complete matrices. A separately written rational input-column interpreter executes all 704 scalar macro columns without importing PR696 or the row interpreter; the private-work row and column are separately required to vanish. Another numeric-column interpreter checks the isolated COPY minimum. Six controls reject reversed COPY, omission of its CLEAR, reversed ADD/CLEAR order, wrong whole transpose order, inverted diagonal scaling and a dirty-input leak invisible to a clean-work-only test.

## Frozen context, credit and limits

Base ce7ad1b6ab09452c3478723a2e96ed5ff212dc08 selects PR1094, whose owner packing retains PR1042's seven-slot R480 local word. The mandatory source inventory includes the retained replay archive, SLOT-PINS-k8, the PR1094 selected-source binding and Sagar Thakrar's PR696 lower.py. The exact named canonical-word payload is verified against its slot receipt. Only the FULL-frame cleanup is used. Center COPY/allocation/erasure events elsewhere in the supplier are outside this package.

PR696 already prices forward and backward macro streams separately; this audit reports no defect in that predecessor or in the selected emitter. Ryan Haines's PR830 transposes cleared historical JP8 coefficient-work circuits and explicitly pays clears; it is credited as the nearest transpose construction, not accused of assuming the false COPY rule. Its public files view did not expose the complete diff during this overlap check. Our result concerns the pinned PR696 unit-overwrite primitive stream and the complete selected R480 cleanup. PR1032's contracted factory cache and ToikY's PR1118 bounded CK grid synthesis address different optimization classes. No claim is made that the elementary COPY-transpose identity itself is new.

The word, frame schedule, provider inventory, selected kappa and predecessor sources remain unchanged. No general circuit optimum, inverse-transpose supplier, native/Clifford phase admission, prefix/precision bound, hosted invoice or full multiplication theorem is certified. The ordinary scalar transpose result alone supplies none of those obligations. Contributor @woklerx, substantial OpenAI Codex assistance, Apache-2.0; no independent human review claimed.
