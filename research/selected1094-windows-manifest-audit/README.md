# Selected PR1094: Windows manifest-key admission failure

**Reproduced portability defect and tested repair candidate. No new kappa.**
The unchanged selected final-stage entry point stops on native Windows before
creating its output directory: `Submission file inventory or hash changed`.
All file bytes match their pins. Its two inventory guards serialize relative
paths with `str(...)`, producing backslashes instead of the manifest's `/`.

At canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
`research/complex-t16-rare-pattern-exchanges/verify.py` has this problem at
lines 9–10 (submission) and 18 (extracted upstream archive).

| Guard | Pinned payload files | Keys whose spelling changes | Digest mismatches |
| --- | ---: | ---: | ---: |
| Submission | 13 | 3 | 0 |
| Extracted PR1087 archive | 179 | 160 | 0 |

For example, the unchanged `data/PLAN.json` becomes `data\PLAN.json` on
Windows. The second guard is independently executed on the authenticated
archive: it has the same defect, although the unmodified full entry point
cannot reach it on Windows because the first guard fails.

## Repair candidate and coverage

Replace `str(f.relative_to(P))` with `f.relative_to(P).as_posix()`, and make
the corresponding change for `source` in the second guard. The audit applies
these two substitutions **only to separately compiled in-memory guard ASTs**.
It changes neither the selected script nor its manifest, archive or source pins.
This is a reviewable repair candidate, not an installed production repair.

The test executes the actual pinned assignments/assertions. Filesystem
enumeration and SHA-256 reads are real; the cross-platform models replace only
the string conversion of a relative path. Both original guards accept POSIX
spelling and reject Windows spelling. Both corrected guards accept the
unchanged fixtures. Native guard execution agrees with the host's path model.
On Windows, a child process also runs the unmodified original entry point and
requires the exact first-guard failure before output-directory creation.

All 192 payloads are then individually changed and individually omitted on
disk while the original manifests remain fixed. Two extra-file and two
same-bytes rename controls also reject. Three additional controls corrupt the
immutable wrapper script, its manifest, or its archive and require source-pin
rejection before code evaluation: **391 rejections total**. Fixtures are
restored and checked again. The frozen assertions are compiled with
`optimize=0`, so the audit's own `-O` run retains their checks.

For this fixed, authenticated inventory, the repair is a bijective spelling
change: canonical names have no backslashes, colons, absolute prefixes or dot
components; their Windows spellings are distinct. The enumerated files,
exclusion predicates, raw SHA-256 values and exact dictionary-equality
conditions are otherwise identical. This establishes the coverage of these
two guards, not a generic path sanitizer or a mathematical supplier proof.

## Reproduce

From a checkout containing the pinned inputs (Python 3.12, standard library):

```sh
python3.12 -I -O -B research/selected1094-windows-manifest-audit/verify.py
python3.12 scripts/research_package.py --package research/selected1094-windows-manifest-audit --check-only
python3.12 scripts/research_package.py --package research/selected1094-windows-manifest-audit
```

Expected marker:

```text
PASS_SELECTED1094_WINDOWS_MANIFEST_AUDIT guards=2 files=192 controls=391 no_new_kappa
```

`RESULT.json` records deterministic evidence, including every affected key.
`SOURCES.json` pins all 14 wrapper-package files and the frozen selected source
manifest; the selected record and catalogue are historical provenance.
The archive's complete member hashes are also checked against its original
manifest and PR1087 source inventory. The direct verifier does not need Git;
the repository metadata checker uses the pinned base commit.

The optional `--root` accepts a relocated minimal source export. `--report`
writes host-specific observations separately from the deterministic receipt.
`--write` regenerates the receipt only after the same checks have passed.

## Local evidence and limits

The investigation ran on native Windows with CPython 3.12.14. The original
PR1824 portability caller failed at the first manifest guard. Separately,
`scripts/research_baseline.py` passed after invoking its path with the Windows
extended-length prefix: that verified all 1,579 selected input files and
retained the selected kappa `836330098538459/500000000000000000`.
The ordinary long workspace path initially caused Python to omit overlong
paths; this environmental setup issue is distinct from the reproduced
separator defect, which also occurs in short temporary directories.

See `VALIDATION.json` for executed commands and results. The local sandbox
requires a writable temporary directory; the runs set process-local `TEMP`
and `TMP` to a workspace directory, using its extended-length Windows path.
Neither system settings nor repository inputs were changed.

No complete final-stage, cold ancestry, native mathematical supplier, Linux,
macOS or hosted-CI replay is claimed. Pure-path models are not OS execution.
PR2040/2059/2101 cover payload equivalence and reference binding downstream of
these guards; their results are credited, not repeated or replaced here.

## Open next questions

Run a separately versioned successor wrapper with the two POSIX-key changes,
then diagnose its next Windows failure while retaining all assertions and
strict complete-output comparisons. This matters because inventory success
alone is not supplier admission. The first step is to bind the successor to
the original source and record its two-line delta. Full downstream execution
is outside this audit's bounded scope; see the structured question in
`TASK.json`.

## Credit and overlap

Rohan Arun supplied PR1094; Jeremy Kothe supplied the frozen PR1087 strict
verifier, with Hao Yan's T16 controller and the retained supplier lineage.
Douglas Colkitt supplied the selected driver and review records. Josie
Elliston's PR1824 posed the Windows replay question. Maxime Fleury and Antoine
Olivier established the payload/container convention. Credit commdata2338's
PR2040 and Adam Gall's PR2059/2101 for later comparator and reference work.

The one-shot assignment selected verifier engineering, nonce
`effac00be71b189171c4803530783d88`, priority revision 4. `TASK.json` records
the refined card, method choice, predecessor heads and partial overlap
coverage. The local overlap helper lacked authenticated `gh`; supplemental
live PR searches and Discussion reads do not imply a complete-board search.
No advance public claim was posted.

Prepared for `josecarlosgonzalezroque-design` with substantial OpenAI Codex
assistance in investigation, implementation, testing and writing. Self-reviewed;
no independent human review claimed. New work Apache-2.0. All predecessor
licenses, frozen files and selected-frontier metadata are unchanged.
