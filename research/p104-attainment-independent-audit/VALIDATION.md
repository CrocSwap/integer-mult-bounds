# Validation and remaining scope

Prepared for ferdy252 with substantial OpenAI Codex assistance, November 5,
2026. Environment: Python 3.12.13, macOS 27.0.1, arm64, standard library only.

## Actual checks

1. Current-main orientation at
   `7c49fe32c55de02c2c873655c804b16e4c3fef0a` passed
   `scripts/research_selected_baseline.py`. This is source/metadata evidence
   only, resolving selected #6030; no selected construction replay was run.
2. `scripts/research_package.py --package research/p104-attainment-independent-audit
   --check-only` passed exact main-provenance pins and metadata checks.
3. The registered normal and optimized commands both passed all 18 cases and
   four semantic fault controls. The first direct checker run also passed.
   No predecessor verifier or primary result file was imported or executed.
4. A standalone copy of the package, outside Git and with an empty `PATH`,
   passed both direct commands. Normal/optimized output was identical and
   SHA256 was
   `088e82e3cb07fd4dcdd6fcca697be2ed25f6029b626c801c4000e6afa841d5ed`.
   All copied file bytes remained unchanged. Initial cold-run wall times were
   approximately 0.054 and 0.099 seconds; these are host timings, not mathematical
   operation bounds. A final explicit check of the malformed query factors
   was then added; registered and cold normal/optimized checks passed again
   with the same output digest.
5. In a temporary package copy, appending text to the retained source proof
   made both normal and optimized actual CLI calls exit nonzero with
   `source SHA256 mismatch`. The original proof remained unchanged.
6. A separate AI agent derived the all-size argument from the source text.
   Another AI agent independently checked the algebra and then statically
   reviewed the new checker. The primary agent reviewed and integrated the
   derivation. These are separate AI roles, not independent human reviewers,
   proof-kernel checks, or independent end-to-end executable implementations.

The four executable faults are: last-column sign; lost extra input; swapped
queries 1 and 2; and omitted last-column tail. The final control first passes
full endpoint equality and then fails final-site compatibility. PROOF.md
section 8 gives its exact rank-one defect. This is a control outside the
source hypotheses, not a counterexample to PR6717.

The standalone commands are:

```sh
python3.12 -I -B research/p104-attainment-independent-audit/verify.py
python3.12 -I -B -O research/p104-attainment-independent-audit/verify.py
```

Only this package is new. No shared verifier, frozen predecessor, selected
record or catalogue was changed. Hosted CI status is reported in the PR;
this file records local checks and makes no hosted-success claim.

## Source and overlap limitations

The source head `3c9072b8738323dda9f9c7dfb421d578ed3fc17a` and empty review/comment
feedback were checked live. Main was fetched again before submission and
remained `7c49fe32c55de02c2c873655c804b16e4c3fef0a`; guidance, priority revision 8
and selected #6030 were unchanged. Initial overlap covered 680 open PR bodies,
6,801 Discussion records and all 8,917 in-scope local notes. A fresh pre-submit
check is recorded in TASK.json and the canonical Discussion.

Snapshots are non-atomic. The helper does not search every diff or nested
source file, and closed work is covered only through local notes/ledger plus
a targeted all-state PR6717 query. No absence-of-overlap proof is claimed.
The pending source's three copied texts are verified locally against their
original SHA256/Git blob IDs. Its commit is not required in local Git history.
The generic package runner checks only the main-provenance pins in SOURCES.json;
the standalone checker checks the external copied-source pins.

## What remains unverified

The universal lower bound in PR6717 sections 2-6 is outside this audit;
PR6721's section-6 review is predecessor evidence, not rerun here. No native
supplier, complete paid invoice, precision/tape, ownership, compiler, recursive
or outer theorem was checked, and no selected framework assumption was
discharged. The proof is written algebra. The finite tests corroborate
conventions; they are not an exhaustive all-size or proof-kernel verification.
