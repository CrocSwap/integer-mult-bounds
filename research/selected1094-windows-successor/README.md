# Selected PR1094 final stage: Windows successor evaluation

A separately versioned, source-bound wrapper executes the selected final stage
on native Windows. It applies only PR2316's two relative-path key conversions
in memory; the original supplier files, archives and selected record are unchanged.
This is a portability receipt, with no new kappa or full-theorem claim.

## Result and exact scope

The unchanged selected entry point rejects Windows paths at `Submission file
inventory or hash changed`, before creating output. The successor completes all
11 PR1087 strict stages and returns selected kappa `0.001672660197076918`.
Its input is the ten archived `slots/local` files, each authenticated against
the PR1042 receipt. Earlier cold ancestry is not rebuilt.

The [execution receipt](VALIDATION.json) records Windows, interpreter and timing.
All 105 output files are checked against the reviewed PR1094 archive:

| Class on this Windows run | Files | Required equality |
|---|---:|---|
| Bytes | 88 | Exact bytes, including all 22 gzip outputs |
| Logs | 11 | Exact bytes after CRLF to LF conversion |
| Invoice | 1 | Every JSON key and value, preserving value types; dictionary order may differ |
| Assembly and admission receipts | 2 | Every value except the invoice hash, which must match each actual invoice |
| Independent T16 receipt | 1 | Every value after relocating exactly six input-path keys |
| Stage receipts | 2 | Every value except nonnegative finite wall times and log hashes; hashes must match actual logs, whose normalized contents are compared |

In particular, **ASSEMBLY.json is not byte-identical** to the selected archive.
Its sole differing leaf is `input_sha256.fresh_invoice`: the invoice has the
same typed JSON content but a different dictionary order. Separately, Windows
log CRLF bytes change the log hashes in both stage receipts. The checker follows
those dependencies; it never simply discards hash fields. No gzip waiver is used.
The six independent input digests agree after mapping their Windows/POSIX paths.

## Successor delta and source binding

The authenticated `research/complex-t16-rare-pattern-exchanges/verify.py` has only
these two substitutions before compilation:

```python
str(f.relative_to(P))       # replaced by f.relative_to(P).as_posix()
str(f.relative_to(source))  # replaced by f.relative_to(source).as_posix()
```

The original path remains `__file__`, so its exact original package inventory
and archived source manifest remain enforced. The source hash and exact one-match
count for each substitution are checked. `compile(..., optimize=0)` preserves
all original assertions even when this evaluation is invoked with `-O`.
The strict subprocesses run without `-O` or inherited `PYTHONOPTIMIZE`.
The successor writes replay outputs only to temporary directories.
[SOURCES.json](SOURCES.json) pins all 22 direct inputs to canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.

The comparison permits no global path-string replacement, arbitrary volatile
keys or blanket hash exclusions. Sixteen corruption controls cover invoice and
assembly proof values (including integer-to-boolean changes and duplicate keys),
invoice links, independent input pins and unmapped paths, log content and links,
kappa, invalid timing, gzip bytes, missing/extra output, changed original source
and an undeclared timing field. Outputs must return to their positive
comparison after the controls.

## Reproduce

From the repository root, with Python 3.12 and only the standard library:

```sh
python3.12 scripts/research_package.py --package research/selected1094-windows-successor --check-only
python3.12 scripts/research_package.py --package research/selected1094-windows-successor
python3.12 -I -O -B research/selected1094-windows-successor/verify.py --report /absolute/path/receipt.json
```

The registered command deliberately exercises an optimized parent. Its successor
and all inherited strict checks retain assertions. The package can replay on other
platforms, but only native Windows is evidenced here. A later environment with an
unexplained output difference must fail rather than broaden normalization.

## Overlap and limitations

This follows [PR2316](https://github.com/CrocSwap/integer-mult-bounds/pull/2316)
head `1b732744b66cc3461559d52349ae07fa31d444f8`, which checked the inventory
guards only and explicitly requested a separately versioned successor replay.
The earlier [final-stage portability audit](../selected-final-stage-portability/README.md)
covered macOS and left Windows unrun. This contribution adds actual native Windows
execution and an explicit dependency-aware comparison of the resulting receipts.
It does not claim discovery of the two-conversion repair.

[Discussion 2333](https://github.com/CrocSwap/integer-mult-bounds/discussions/2333)
is the canonical investigation. [TASK.json](TASK.json) records priority revision 4,
the fresh overlap search and the deliberate handoff override after the initial
P104 candidate proved covered. Search coverage is not proof of novelty.

This is neither a cold selected replay nor independent verification of the
multiplication theorem, stock envelope or precision assumptions. The inherited
strict verifier checks its own transitive inputs; this package pins its direct
inputs rather than claiming an independently complete transitive manifest.
The selected reproduction command remains unchanged and still rejects Windows
inventory keys. No selected frontier, historical source or policy is altered.

## Historical CI dependency

The contribution branch also incorporates the pending historical CI repairs in
[PR2055](https://github.com/CrocSwap/integer-mult-bounds/pull/2055), through
`92276c22f6f419bbefd870bf2bb373bc41b0c643`. The first hosted run of this
package's branch failed six clone/test jobs because the historical PR53 checks
read optimized live helpers instead of their unchanged source-pinned versions.
The shared repair runs those checks in authenticated temporary copies. It also
retains exact reconciliation bindings and assertion safety. Original repair
commits and attribution are preserved; no selected source pin is changed.
This CI dependency can be reviewed separately from the Windows evaluation.

## Open next questions

The structured questions in [TASK.json](TASK.json) give first steps and blockers:

1. Execute complete native Windows cold ancestry with immutable source pins.
   This would test construction before the archived PR1042 inputs; it is outside
   this bounded final-stage evaluation.
2. Maintainers can review a new portable entry point and canonical invoice
   serialization. Adoption requires a separately versioned policy decision;
   this evaluation does not modify the selected record.

## Credit

PR2316: josecarlosgonzalezroque-design, with OpenAI Codex, for the manifest-key
failure and proposed delta. Selected PR1094: Rohan Arun, using Jeremy Kothe's
PR1087 strict verifier and the retained PR1018/1005/869/799/741 lineage.
Douglas Colkitt supplied the selected replay receipts and archives.
JosieElliston's final-stage portability audit supplied the comparison scope and
archived-input binding pattern. Maxime Fleury and Antoine Olivier supplied the
repository's regenerated-container comparison guidance. Their source-specific
notices remain unchanged; no predecessor code is vendored here.

New work: Dennis / antunishdPursuit, with substantial OpenAI Codex assistance in
investigation, implementation, execution, self-review and writing. No independent
human review claimed. Apache-2.0.
