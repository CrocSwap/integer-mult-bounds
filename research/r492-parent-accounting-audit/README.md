# Audit of provider and parent helper accounting

The selected PR626 invoice correctly uses provider `R=492` for helper routes
and fixed parent `R0=504` for its retained bank and stock envelope. This audit
reproduces that finite accounting and resolves a contradiction in the reported
revert-control expectations. It does not claim a new kappa.

The precise discrepancy is in
[`PROOF-NOTE-R.md`, line 26](../complex-k492-owner-repair/PROOF-NOTE-R.md#L26).
Its introductory expectations say that the R0 controls pass when R differs
from 504. The table's `emit.parent_R0` and `invoice.parent_R0` rows instead
substitute provider R into parent stock and report failure. The evidence
paragraph agrees with those rows. The correct distinction is:

- Substituting 492 for a required parent count of 504 must fail.
- Substituting the equal literal 504 for the derived parent bank count must
  preserve the result.

The original pinned note is retained unchanged. The
[maintainer review](../../docs/research/community-k492-review.md) already says
the scratch 32-site revert suite was not submitted. This package supplies new
evidence for a smaller, explicitly bounded accounting audit. It does not
reproduce that missing suite or its R=504 fixture.

## Reproduce

From the repository root, using only the Python standard library:

```sh
python3 -I -B research/r492-parent-accounting-audit/verify.py
```

Expected output:

```text
PASS_R492_PARENT_ACCOUNTING_AUDIT: 9 finite guards, 7 source rejections, 1 identical control, 4 input rejections
```

`--emit` prints the deterministic evidence in [EXPECTED.json](EXPECTED.json).
The default command also checks that evidence for exact equality. The command
works from another working directory when given the script's absolute path.
It also works under `-O`: the audit's own checks use explicit exceptions, and
the selected source assertions are compiled with optimization disabled.

Validation passed with normal and optimized Python, and from a committed-file
export containing only this package and the nine pinned inputs in an unrelated
working directory. Normal and optimized evidence is byte-identical. Changing
a pinned source byte is rejected before replay. `make selected-record-check`
also passes. The full `make verify` and cold supplier reconstruction were not
rerun because no supplier, shared verifier or selected artifact changes here.

## Exact result

The independent recount reads the parent and provider word dimensions, the
selected dispatch and the per-provider, per-orientation invoice entries.
It does not import the supplier's arithmetic engines. It retains the parent's
nine-bank geometry and the published scalar primitive and wrapper receipts
as assumptions, then sums their charges independently.

| Quantity | Exact value |
|---|---:|
| Parent helper count, from 728 columns minus 224 data columns | 504 |
| Provider helper count, from 716 columns minus 224 data columns | 492 |
| Helper routes, two directions across 72 complete calls | 70,848 |
| Parent bank charge, nine banks of 504 helpers | 4,536 |
| Parent live / physical stock | 11,704 / 12,218 |
| Hosted live / physical stock | 7,168 / 7,670 |
| Compiler factor | 25,934,336 |
| Nonlocal items / outside work | 4,904,682 / 39,242,128 |
| Complete parent-envelope price P | 1,833,791,190,783,112 |
| Rebase correction | -300,156 |
| Hosted rebased price | 1,833,791,190,482,956 |
| Retained prior allowance plus complete fresh P | 4,711,738,180,507,680 |

The stock equations are
`parent_live = 7168 + 9*504`,
`parent_physical = parent_live + 504 + 8 + 2`, and
`physical = 7168 + 492 + 8 + 2`.
The rebase correction is
`65*(7670-12218) + (7168-11704) = -300156`.
All charge categories are recorded individually in the evidence.

The audit also extracts the original `assemble.py` statements from the
`parent_live` assignment through the last finite-invoice check, lines 118–153
at the pinned base. It executes these unchanged statements on the selected
receipts and checks agreement with the independent recount. The extraction
has unique AST boundaries and the complete source file is hash-pinned.
The nine finite guards use the original implementation; they are replayed,
not independently reimplemented. The invoice recount is the independent part.

## Controls and their meaning

The eight source controls each change one uniquely matched expression in an
in-memory copy. Seven fail at the parent identity or exact invoice comparison.
Replacing `9*parent_banks` by `9*504` preserves every captured result. Four
additional input controls exercise the independent recount by changing stock,
wrapper work, scalar work or local adapter work. No source file is modified.

With all other inputs held fixed, changing provider route R to 504 increases
P by **358,516,260,864**. Changing only the parent bank R0 to 492 decreases P by
**22,407,266,304**. Replacing the rebase coefficient 65 with 64 increases the
rebased price by **4,548**. The source checks detect each mismatch.

The route substitution overcharges. Its rejection establishes disagreement
with this exact invoice, not that every enlarged conservative allowance is
mathematically unsound. The controls are concrete failed checks. They are
neither counterexamples to the selected construction nor impossibility results.

## Pins, scope and credit

Base commit: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Assignment seed: **70**, drawn with `secrets.randbelow(100)` from OS randomness.
[CLAIM.json](CLAIM.json) records the candidate selection, stopping rule and
overlap check. No pinned sprint coordination issue was available.

The selected source is Chafik Boukhalfa's PR626,
`660de893d27bb7abd1d5b01b1640207528a5c851`, building on Jeremy Kothe's
PR622 `f69477f4f6d3c7eb1f740b166881bffed4ffa9f6` and PR623
`e39a615ca601ce5d62abeb24f3fcdb8644ca1005`. The retained bit supplier is eumemic's
PR543 `2065fe4f72a914d907f1046603f5a36f17018535`; this audit does not replay it.
The accepted conditional kappa remains `51110230636731/31250000000000000`.
[SOURCES.json](SOURCES.json) pins every consumed fixture and source by SHA-256.
Compressed hashes bind committed inputs; no regenerated gzip bytes are used
as a test of mathematical equality.

GlobalR and AtomReviewer supplied and corrected the R/R0 generalization.
The retained envelope and invoice descend from icekylinx's PR531 and the
PR552/PR558 lineage, with DreamingOfClouds' cold helpers and Rohan Arun's
recurrence work retained. Their [package notice](../complex-k492-owner-repair/NOTICE.md)
and [parent notice](../direct-delivery504-global/NOTICE.md) preserve full credit.
The concurrent [PR675](https://github.com/CrocSwap/integer-mult-bounds/pull/675)
audits owner timing and bridge omission. It is related context, not a dependency
or the same accounting experiment.
The refreshed queue also includes [PR717](https://github.com/CrocSwap/integer-mult-bounds/pull/717),
which prices moment sensitivity to structural changes. This audit instead
checks the selected finite invoice and its R/R0 mutation expectations.

Only the named accounting slice is replayed. Earlier scalar, frame, phase,
whole-owner and wrapper admission remains inherited from the selected review.
The retained prior allowance is a pinned receipt value, not freshly derived
here. Moment endpoints and the 47 outer assembly constraints are outside this
audit. All-size compilation, common-label and mutable-basis realization,
hosting, normalized residuals, precision/tape and analytic transfer remain
conditional. Finite arithmetic and rejection controls do not prove the full
multiplication theorem.

Prepared for **thakrarsagar** with substantial **OpenAI Codex** assistance,
including a separate agent's arithmetic and code review. This is not
independent human peer review. New work uses the repository's Apache-2.0
license. The selected frontier, pinned historical sources and `upstream/`
are unchanged.
