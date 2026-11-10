# Scalar pair-placement price obstruction

This package closes one proposed equal-orientation change to the eight-field
shortest scalar root. A common rank-four pair at sites (1,2) forces a commuting
common pair at (5,6) to have rank at least five. For every possible second-pair
rank, rank-two endpoints and exactly one paid fragment from each pure paired
bank give a complete recursive invoice strictly worse than an allowed #6726
allocation. The rank-five difference is `104*(i(d+e)-1)<0`; the eight-inventory
census proves that larger ranks lose more.

The proof is in `PROOF.md`; exact source bindings are in `ORIGINS.json`.
Run these standard-library checks (about one second each):

```
python3 -I -B verify.py
python3 -I -B independent_invoice.py
```

`RESULT.json` and `INDEPENDENT-INVOICE.json` are retained receipts. Each check
is read-only unless `--write` is explicitly supplied. Normal and optimized
replays pass. The first check covers four exact rank-five fixtures, formal
arbitrary-input matrix identities in both central characters, complete invoice
reconstruction, and failed-prefix/missing-idle controls. The second independently
reconstructs every invoice coefficient and all eight necessary inventories.
Optional independent modular corroboration is
`python3 -I -B reviews/a_matrix_review.py`. Review boundaries and the exact
reviewed proof snapshot are preserved in `REVIEW-COVERAGE.md`.

This is a scoped negative result, with no new kappa or selected-frontier change.
Paid fragments are optimistically granted, not physically constructed. It does
not exclude additional retirements, two fragments in one bank, nonpure fragment
groups, zero-pure-bank cases, other placements, larger first-pair rank, longer
words or coupled controls. The five inherited all-size assumptions remain.

## Open next questions

 a construction outside this fragment contract needs an
actual new retirement or changed site geometry and a favorable complete invoice.
Increasing the second pair's rank alone does not reopen this placement.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Ali Romman, Cinna Davis, zxv and retained predecessor authors keep the credit
specified in the proof and copied source notices.

## Registered replay and provenance

From the repository root, run `python3.12 -B scripts/research_package.py --package research/p104-scalar-pair-invoice-obstruction`. Expected: `PASS_REGISTERED_RESEARCH_PACKAGE`. All five registered commands are read-only. `SOURCES.json` binds canonical catalogue, selected-record and license provenance. `ORIGINS.json` authenticates the retained pending-source files by original repository, exact head, path, Git blob and SHA256; the local verifier checks both digests. No full-history preflight or selected cold replay is claimed. The source files and scientific receipts are unchanged from the frozen worker package; packaging renames its source manifest to fit the generic schema and adds this registration. See `LEAD-REVIEW.md`.
