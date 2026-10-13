# Executed validation scope

Environment: Linux, CPython 3.12.14 and 3.13.16. No external Python packages
are required. Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.

Completed locally:

- `python3 -I -B research/ck-signed-coefficient-routes/verify.py` passes.
  It checks both complete scalar programs on 725 arbitrary-input columns,
  496 coefficient pairs, all 1,080,288 signed one-read cases, exact costs,
  literal positive prefixes, exact fractional depth, original SPEC/program
  pins and conditional local arithmetic. The Fraction engine and the second,
  integer-only engine agree on the full primitive words and on work precision.
- All 15 mathematical/interface controls reject their intended mutations, and
  each must fail with its stated reason. Every one of the 1,117 actual runs
  also rejects omission of its final clear.
- `python3 -I -B research/ck-signed-coefficient-routes/test_package.py`:
  **6 tests pass**, including relocated `-I -O -S -B` execution, alternative
  gzip compression, and rejection of source, route-cost, coverage, invoice and
  signed-instruction corruption.
- `make selected-record-check` passes with the unchanged selected conditional
  value `1661634653669567/1000000000000000000`.
- `scripts/verify_frontier626.py` passes from a fresh work directory (bit543,
  declarations, complex626, owner check, helper interface, bindings).
- `admission.py` on that run passes: identical CK native inputs, dedicated
  coefficient-work stock, re-issued invoice with every strict check true,
  unchanged CK fractional depth (8) and global prefix (286), and the retained
  assembly plus admission controls reproducing kappa
  `51110230636731/31250000000000000`. A control raising the recorded depth is
  rejected. The receipt is pinned as ADMISSION.json.

Measured costs of the construction, not hidden by endpoint equality:

- Literal positive prefix: 40 -> 43 bits forward, 62 -> 63 backward; the
  retained 192-bit allowance passes.
- Fractional depth: 3 -> 4 bits forward (8 work steps exceed the original
  forward depth), 8 -> 8 backward; the provider maximum stays 8.
- Private work is live across target updates within a run; it is hosted in
  the two dedicated coefficient-work registers.

**Not run:** complete `make verify`, Lean and hosted CI. The native
frame/wrapper evidence is the fresh frontier626 replay, which applies because
the CK event stream is byte-identical. Admission covers the historical PR626
composition only, not the current #799 X4 frontier. No existing generator or
selected construction is modified; only this standalone package is added. This is not a formal proof of the full
multiplication theorem.

Both verification implementations were written by AI agents for Joseph /
AmazedBot and share the cost model and input data; they guard against coding
slips, not shared misreadings. No human review is claimed. New code and notes
are Apache-2.0; predecessor credit and source notices are retained.
