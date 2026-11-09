# Independent review and verification scope

The authoring AI derived the universal signed Horner/residue/quotient,
marker and positive cost arguments and implemented the flat table. Runtime
executes unchanged predecessor `Controller.primitive` and `execute_table`.
The author-suite direct integer floor/range oracle is independently
implemented from the transition arithmetic. Normal/optimized package
replays are regression and portability checks, not new mathematical proofs.

## Separate lead AI review

The lead independently reviewed the complete arithmetic proof and literal
table, including signed/cancellation admission, both marker rewinds and
59/27/33 per-position counts supporting the slack 128U phase bounds. Its
separate raw source census confirmed 61,052 ADD plus exactly one COPY;
only three ADD tokens are installed. It found no issue under the explicit
canonical/ownership/context-head and fixed odd-divisor premises.

The lead then wrote a separate direct runner with its own numeric encoding,
decoding, signed integer floor and heterogeneous-width input generation.
It invoked the unchanged primitive with the submitted immutable table,
sharing only the retained checker hardware and executor. It did not import
the author-suite arithmetic oracle. The untouched script and result are
`review/compact-add-lead-check.py` and `review/compact-add-lead-review.json`.

It checked 219 heterogeneous-width fields, widths 1..41, obtaining 139
successes and 80 correct final-overflow rejections. Coverage includes the
three actual cancellation witnesses, six additional coefficients, most-
negative/sign endpoints, W<d, dirty old work and two read-only context
heads initially inside their bodies. The largest measured ratio of combined
row plus physical cost to the advertised bound was 50065/464523. Source,
contexts, markers and success cleanup/failure public protection were checked.

The exact reviewed/tested table SHA-256 is
`fe8a28fd523ebb7ec78dce4ba0855b3070a6cbff470602cd62f8d3ff445e0f0a`.
The lead result records proof SHA-256
`997a2d98167fa94742f5e9978d19ef962d0518cff78b66331ff73385b24fe9c9`.
The final proof SHA-256 is
`80035605d92c0a1cceb1f802f4adcfeb1b60590a4b7335b612f8c4f67079ceb0`;
the sole difference is the explicit actual-input half-grid-error paragraph
immediately before Section 5. Removing that paragraph reproduces the
recorded prior proof hash. The lead separately confirmed that corollary.
No table, oracle, runtime or cost formula changed after this check.

The supplied lead script accepts the package path as its argument and
regenerates the JSON beside itself; use normal Python, since its assertions
are intentional verification checks. It is not one of the optimized author
regression suites. Replaying it against the final proof changes only its
recorded proof hash, besides reproducing its deterministic counts.

This is separate model-assisted mathematical and implementation review,
not human review, proof-kernel certification or full physical caller replay.
The bounded tests do not replace the universal proof or close the remaining
full-catalogue, native, format, recursive, cost-cap and recovery obligations.
