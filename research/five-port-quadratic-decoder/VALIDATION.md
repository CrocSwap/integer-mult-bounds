# Verification and handoff

Exact base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
Branch: `research/structural-decoder-seed40`.
Contribution type: **research note / scoped negative result**.

## Completed checks

- CPython **3.12.12**, isolated optimized execution: the primary checker
  accepts all 17 explicit minors, exact decoder/coefficient checks, rational
  ceiling and nine mathematical/contract rejection controls.
- CPython **3.14.6**, isolated optimized execution: the separately written
  set-feature / Bareiss checker accepts all 17 minors at a second prime,
  computes two integer determinants, and obtains the identical rational ceiling.
- All **six package tests** pass. They compare both elimination implementations
  with the permutation definition on 123 matrices, reject omitted obligations
  and changed source text, exercise a singular minor with distinct valid labels,
  and distinguish a scalar-valid decoder from invalid linear geometry.
- A clean export of the canonical staged Git blobs to a directory containing
  spaces passes both optimized checkers. Both regenerated receipts are
  **byte-identical** to the committed receipts. Existing output-file preservation
  is checked through the real CLI: rejection leaves the sentinel bytes intact.
- `make selected-record-check` passes. The selected certificate and `upstream/`
  have no changes. Staged whitespace validation passes.

Exact commands, exit statuses, runtimes and the exported tree identity are
in `evidence/checks.json` and `evidence/clean-export.json`; stdout is retained
beside them. Timings are evidence of completion, not a performance claim.

## Coverage and limits

The 17 minors cover corrector rank at p=5..13 and star pairing rank at p=5..12.
Their validity extends to every target/star by the written permutation argument.
The p>=13 extension is proved by embedding the p=13 corrector witness; the
all-stage result follows from the displayed inequalities for every s>=3.
No failed finite search is called an impossibility theorem.

The result assumes the exact quadratic Gram, independent source variables,
drop-free gathers and corrections, separately charged star totals, and the
fixed-window pressure/active-climb accounting. It implements no supplier.
All-size realization, common-label/mutable-source, hosting, precision/tape,
bit H1-H5 and analytic obligations remain. Neither checker is a formal
multiplication proof; both implementations were prepared by the same
AI-assisted contributor and need external review.

Full repository-wide `make verify`, unchanged supplier cold replays, Linux
and hosted CI were **not run or claimed** for this isolated research package.
No shared generator, existing test, global certificate or selected source was
changed. Reproduction of this result takes only the standalone commands in
README.md.

## Overlap and current context

The initial snapshot contained 717 open PRs. The final full refresh contained
707 through PR954, with no duplicate five-port quadratic result. PR954's body
was read: it concerns E8's first punctured-reader rank loss and is distinct.
PR446's consumed head is unchanged. The newly fetched main is
`007664306fff84fbb1c9a1b4053b69f439764034`; it still selects PR890 at
`1661957774647029/10^18`. The contribution retains its exact earlier base and
immutable source pins. Its new package path is absent from refreshed main.

There is no pinned sprint coordination issue. The claim is local; the completed
result is linked there. Publication and CI status belong to the PR handoff,
not to the finite mathematical certificate. No merge is authorized or attempted.
