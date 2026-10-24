# Validation record

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Base: `ff3cc58e370d0f678e529246f8c73e8094e18fcf`.
Runtime: CPython 3.12.13; standard library only.

Both registered isolated, warning-strict normal and optimized commands pass
and reproduce RESULT.json. Eight actual source tuples cover source sizes
9 through 257, excesses 1 through 13, two Gaussian alpha values, halfwidths
2 through 4, and entry precisions 64 through 96. The target precisions are
12, 18 and 24. All 103,717 original matrix entries are checked. Twenty-four
complete signed complex RHS cases pass; six also match a separate pivoted
rational dense solution. Eleven malformed, geometry or funding controls
reject. Seven exact gap cases include a gap smaller than 2^-1000.

The 258-row case uses a 257-row selected block, gap 1/16, 31 coefficient
bits, 39 internal bits, 492 factor products and 1,314 solve products. These
counts exclude the separately recorded source setup and boundary scans.
This is not a production benchmark or an improvement to the selected kappa.

The original-H residual before final rounding, plus the known final rounding
and analytic terms, certifies the target for every finite test input. The
finally rounded residual divided by d is too loose in the 97- and 257-source
cases. RESULT.json records that diagnostic as false; it is not described as
a failed consumer target. Exact public outputs agree with truncation of the
independently residual-checked internal output.

Four actual code mutations fail in normal and optimized mode, before receipt
comparison: omitted wrap entries fail the original-reference residual;
source-index scatter changes a hole; a fixed 16-bit gap floor fails small-gap
checks; and omitting analytic error accepts an unfunded source. Mutation
copies use the same authenticated source inputs. Package bytes are unchanged.

An initial receipt check found a tuple/list serialization mismatch in the
specification field. The verifier now uses the same JSON list representation.
No mathematical value or validation threshold changed for that repair.

The all-parameter implication is a written proof. The finite checks do not
validate production parameter funding, the analytic interval backend or a
physical tape. No Lean, Docker, independent human review, selected cold replay
or complete kappa calculation was run. The full-history wrapper is unpassed
in the shallow checkout; direct declared-pin ancestry is checked separately
for publication. No predecessor or selected-frontier file is edited.
