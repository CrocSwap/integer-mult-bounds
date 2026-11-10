# Reject NUL-bearing export paths

The offline export checker accepted a self-consistent PAX archive containing
`inputs/evidence\x00hidden.json`. Both `check` and `check --check-inputs`
returned `PASS_RESEARCH_EXPORT`, although Python's data-filtered extraction
immediately raised `ValueError: embedded null character` on Windows. The
receipt's inventory, lengths, modes, hashes and input declarations all matched;
the filename was the defect.

PAX extended headers preserve the NUL in the decoded member name. Unlike a
newline or a Unicode character, NUL cannot occur in a Git or filesystem path.
The shared export-specific path check now rejects it with an escaped diagnostic.
This check covers archive members, receipt paths and declared inputs. It does
not change the shared source-pin path policy or any frozen research input.

This is a tooling correction, not a mathematical result or a new kappa. The
checker still does not authenticate a labelled commit or guarantee that every
accepted POSIX filename can be extracted on every platform. Its existing
non-drive-colon and newline policies remain intact.

## Task and sources

- Base: canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
- Priority revision: 8. Selected record: #6030, conditional kappa 0.003125804.
- Picker: `python -B scripts/choose_current_research_task.py --track verifier-engineering
  --seed a8edca6312196a1e52e9c14c69f22b86`.
- Card: `portable-replay`, scope key `91a9a2afec282c926282`.
- Scope status: **changed** from the compressed-payload example to a demonstrated
  filename acceptance failure in the current offline exporter. The question is
  whether an internally consistent archive with a NUL-bearing member can pass
  the public CLI. Success is rejection in both CLI modes while preserving valid
  names and payloads; the bounded domain is four NUL positions and the existing
  export regression suites. No construction-family expansion is proposed.
- Original `scripts/export_research_package.py` SHA256:
  `7126afaebff2328b8d64ba1ce992c497103820284f52d4590a558f97f13965fe`.
- Unchanged `scripts/research_package.py` SHA256:
  `e1256016e7f51827d04fa2179255989f639ae1d97afaa9c16265f85a0c6abd70`.

Read AGENTS.md, autoresearch.md, CONTRIBUTING.md, the standing procedure,
priorities, family gate, selected record and review, and the card's gzip audit.
The required selected binding-only orientation passed after materializing its
declared inputs. The initial Windows checkout hit long paths; enabling local
`core.longpaths`, disabling automatic line-ending conversion and restoring the
fresh checkout resolved that setup failure before verification.

## Evidence and reproduction

Windows 11 build 26300, CPython 3.12.10, Git 2.53.0.windows.3:

```sh
python -W error -B -m unittest discover -s tests -p 'test_research_export*.py' -v
python -I -O -W error -B tests/test_research_export_nul_paths.py -v
python -B scripts/research_selected_baseline.py
git diff --check
```

All 45 export tests pass with no skips; the three new tests also pass under
isolated, optimized Python. The selected baseline reports
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it is not a scientific replay.

Before the fix, all eight CLI rejection cases failed because the malformed
archive was accepted: four NUL positions, each with and without `--check-inputs`.
The new tests construct PAX headers independently of the exporter and confirm
that the same names fail extraction. CLI cases run with an empty PATH, require
nonzero exit without a success marker, and verify the archive bytes are unchanged.
The producer-side control checks rejection of a committed manifest's NUL input
before tree inventory. A positive fixture retains Unicode, CR, LF and CRLF paths
and binary payloads containing NUL. Existing tests retain real-Git export,
publication, corruption, declaration, topology and drive-path coverage.

No POSIX execution, hosted CI success, historical pinned-package replay, selected
scientific replay or full theorem verification is certified by this local run.
The selected result and all five framework assumptions remain unchanged.

## Overlap and credit

Checked the start-here discussion, newest rendered handoffs in #1166, active
discussions, recent open PRs, local overlap helper and targeted all-state PR
searches for NUL/export, null-byte and archive-path work on November 3, 2026.
The local sparse overlap corpus and rendered discussion pagination are partial;
there is no exhaustive novelty claim. No inspected result supplies this guard.

Nick Petalas's open #6204 at `9889f94b6ed045c1069b2e6f7e4471d0322f2f16`
optimizes archive-index reuse while retaining the path checks. That is a distinct
change to the same checker; this rejection should be retained if it is integrated.
#6357 repairs multiline pinned-byte reads. This account's #6334 addresses Git
path newline normalization and #5973 addresses invoice stdout bytes, neither
the PAX NUL case.

Credit Tekalign's exporter, roger-sato's path/topology controls, Ali Romman's
input-coverage work, Mihir Srivastava's Windows fixtures, Nick Petalas's related
checker work, Douglas Colkitt and the retained exporter/Git-reader contributors.
Prepared for josecarlosgonzalezroque-design with substantial OpenAI Codex
assistance, one agent. Apache-2.0; evidence is author-checked.

## Open next questions

Run the new test module on POSIX and another supported Python version to check
the PAX reader and extraction failure across runtimes. The fixture is synthetic,
small and Git-free; no mathematical replay is needed. This local run does not
supply that platform evidence. No wider filename-policy expansion is proposed.
