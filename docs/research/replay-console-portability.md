# Unicode coverage labels on legacy replay consoles

The registered runner accepts UTF-8 `VERIFY.json` metadata, but a valid coverage
label such as `Verify κ → ∑ and café 🚀` failed at `print("CHECK " + checks)`
when stdout used strict cp1252 or ASCII. The verifier command never ran. This is
reproducible with redirected Python output on Windows, or on any host by setting
`PYTHONIOENCODING=cp1252:strict` and `PYTHONUTF8=0`.

`scripts/research_package.py` now applies `errors="backslashreplace"` to its own
stdout before reporting and executing commands, following the existing
`find_overlap.py` reporting policy. It retains the output encoding: cp1252 keeps
the representable é and displays κ as `\u03ba`; UTF-8 preserves the full text.
The package bytes, pins, command arguments, timeouts and child environment are
unchanged. The child's own stream policy is also unchanged.

## Evidence and reproduce

The public-CLI regressions in `tests/test_research_onboarding.py` create a real
temporary Git repository with pinned input and complete package metadata.
Before the fix, the success test fails under cp1252 and ASCII with encoding
errors and passes under UTF-8. After the fix it checks all three encodings,
including both a successful child and a child exiting 7. The child's printed
policy remains `strict` with the original `PYTHONIOENCODING`. Drifted source pins
still prevent execution, and a Unicode missing-path diagnostic still exits
nonzero without a success marker. Package slugs and final status fields are
ASCII-restricted by the existing metadata validator.

```sh
python3.12 -B -m unittest \
  tests.test_research_onboarding.PackageTests.test_cli_unicode_coverage_survives_legacy_stdout \
  tests.test_research_onboarding.PackageTests.test_cli_unicode_coverage_does_not_relax_source_pins -v
python3.12 -B -m unittest discover -s tests -p 'test_research*.py' -v
```

On CPython3.12.14, all 67 research-tool tests pass with three existing Linux-only
process-state tests skipped on Windows. This is runner portability evidence, not a replay of every scientific package
or a complete selected-supplier proof. The fix does not promise that a child
verifier's own non-ASCII output is portable; child policy remains its contract.

## Assignment and provenance

Started from canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority
revision 4. Picker nonce `bddca01f5ef217509065498948a8a64a`, verifier-engineering,
`portable-replay`, scope key `831cc1a3c8f9ff01b197`. Scope is refined from
reproducible environment failures to one command-reporting failure. The prescribed
baseline bindings control passed; no source hashes or mathematical comparisons
were relaxed. The selected-record SHA256 remains
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

The canonical [reproduced-finding claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18950766)
records the task and public completion pointer. Initial complete overlap snapshot
covered 739 PRs and 1,213 Discussion records at 2026-10-15 14:01:51 UTC; the final
live refresh covered 751 PRs and 1,216 Discussion records at 14:10:12 UTC,
complete pagination and no warnings. Canonical main was unchanged. No code-diff
search or novelty guarantee is claimed. Related PR2531 fixes UTF-8
file decoding in a Lean recipe; this failure is the runner's output stream, after
metadata decoding has already succeeded. The credited PR1298 onboarding work already fixed metadata reads and overlap
reporting; PR1834 fixed test-suite document reads. This patch addresses the still
reproducible command-coverage print in the execution path. The existing overlap-console regression
in the same test file provides the established display-policy precedent.

Contributor: ywz65, with substantial OpenAI Codex assistance in diagnosis, tests,
code and writing. Existing runner, metadata validation and source checks remain
credited to their authors, including Douglas Colkitt. No independent human review
or hosted CI pass is claimed.

## Open next questions

If a named child verifier fails on its own Unicode output, reproduce that child
with its prescribed environment and define a local reporting contract there.
Changing every child environment here would be a separate compatibility decision;
no such failure or broader change is claimed by this patch.
