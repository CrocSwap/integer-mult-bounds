# Parent return-grid correction

This addendum corrects two sentences in the frozen
`GRID-RESET-PROOF.md`, SHA-256
`408d48513a29c243e2091289489d8b889b7bbb611795266984ea13589b6d4769`.
The package reviewer found the format issue below. The original proof
bytes remain fixed for the review record.

The child relative-error contract includes the child computation and
the conversion of its complete normalized input. It does not include
rounding the unscaled return value to the fixed parent grid. Charge
that return rounding as a separate absolute error insertion of size
at most `2^(-2t-P)` per component.

This distinction is required for a tiny child input. A relative error
bound can demand more fractional bits than the parent format retains.
The child uses its own normalized stream and exponent descriptor.
On return, it unscales and rounds directly to the parent's declared
grid. No ancestor record is widened. This is the convention proved in
`temporal-reuse/HETEROGENEOUS-PRECISION-CONTRACT.md`.

The extra insertion sites fit the existing bound. The raw local word
has 25457 events and 3486 native climbs. Grant one error site to every
old event, one extra return-rounding site to every climb, one site to
each of the 2361 new field passes, and even one site to each of 704
optional entry conversions. This gives 32008 sites, less than `2^16`.
Exact phase, permutation, COPY, CLEAR, and grid-rounding operations
need no such error site; counting them only enlarges the bound.

Every parent return-grid error is on the fine absolute scale, including
returns from ordinary-accuracy children. A child outside the centre
response cone still has zero exact response there. A return-grid error
at a sensitive child is one of the fine absolute insertions. Thus the
coarse cut, fine centre, and suffix error estimates remain valid with
the same P and the same profile of fine relative requests.

The second correction concerns the numerical margin. After substitution
of `P=2B e+2H+4G+32` and `g<=t+B e`, the three upper bounds in the
proof are below their required thresholds by factors at least

    coarse cut: 2^(B e+H+2G+10),
    fine centre: 2^(G+6),
    suffix: 2^(B e+G+10).

The earlier sentence that states a margin of `G+10` or larger is too
strong for the fine centre. The correct `G+6` margin is still positive.
None of the grid definitions, operation counts, native accuracy
assignments, exact endpoint claims, or negative invoices changes.

OpenAI Codex made this correction after independent review. It is part
of the proof packet and must accompany the original proof. Publication
remains on hold.
