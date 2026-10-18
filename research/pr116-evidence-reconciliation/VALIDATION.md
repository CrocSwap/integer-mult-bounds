# Validation and limitations

The first section records validation at original submission. Its selected PR942,
642-entry ledger and `changed_since_review` context are historical. PR116 was
subsequently incorporated and closed; the 2026-10-16 integration keeps those
later decisions and adds only a historical evidence pointer through the generator.

Local validation on 2026-10-13, macOS arm64; CPython 3.14.6 and system CPython
3.9.6. Only standard-library code is used by the new checker.

Completed before submission:

- Ordinary and isolated optimized replay match all fields of `RESULT.json`.
- `test_package.py`: 28 tests pass normally and under `-I -O -B`; 26 reject
  specific transport/parser/evidence corruptions, with two positive controls.
- An offline copy outside the repository passes the checker and all 28 tests
  on Python 3.9.6 from an unrelated working directory, with no changed bytes.
- Rebuilding `CERTIFICATE.json` from the retained Git objects and downloaded
  input snapshots produces byte-identical JSON. The rebuilt capsule passes.
- `python3 -I -B scripts/verify_selected_result.py`: selected PR942 record passes.
- `python3 -I -B -m unittest discover -s tests -p test_selected_result.py`: five
  tests pass.
- `python3 -I -B -m unittest discover -s tests -p test_pr_reconciliation.py`:
  14 tests pass.
- `python3 -I -B scripts/verify_pr_reconciliation.py`: the complete 642-entry
  base ledger and all explicit family/evidence/closure checks pass.
- Only PR116's remaining question and companion pointer changed in the ledger;
  all other rows, heads, attribution, dispositions and counts are retained.
- `git diff --check` passes. The selected certificate and `upstream/` have no
  changes from this contribution.

This is a new offline source/evidence check. The 42 successful checks and three
focused verifier executions are recovered historical GitHub results, not new
CI or a fresh execution of the original package. The author's standalone
full-suite archive was not recovered. No full `make verify`, supplier cold
replay or Lean compilation was run. No mathematical assertion was weakened or
old input rewritten to make a replay pass.

Final integration check: rebased onto
`2921874911956718fcaaaf9396fe8267b3cfa9f0`. The original research base remains
`8bddbee377e2f3ce1f1247196c4b290d55767d20`; all consumed historical objects,
PR116's upstream head and the selected result are unchanged. On rebased
implementation `b5d7e5150f3f25c68107403c6ed035a5c8253c4a`, the optimized 28-test
package, complete result replay, byte-identical capsule regeneration, five
selected tests, 14 ledger tests, selected-record checker and complete 642-entry
ledger checker all pass again. Subsequent changes are documentation only.
The open queue was refreshed through PR1003; no competing PR116 reconciliation
was found. The PR279 work that prompted the pivot has now merged separately.
`codex` and `codex-automation` labels are unavailable in the upstream repository.

## Current-ledger revision — 2026-10-16

Integrated with canonical main `67b122d33d6c599a49f65d50afa2f3fe8d790d02`.
The original source capsule, result, producer, checker and 28-test package are
byte-identical to submitted head `ed1ac8286bd52f212e9063c5c82ac7e71619f93d`.
Historical source commits and all attribution remain unchanged.

The generator consumes the new `PARENT-EVIDENCE.json` and regenerates both
central ledger files. A complete comparison against that main confirms that
all 2,356 existing PR records and every pre-existing field/evidence item are
preserved. The only additions are this input's SHA-256 and one PR116 evidence
entry; the Markdown changes only PR116's evidence link. In particular, PR116
stays incorporated/CLOSED with its review completion and closure receipt, and
PR1007 is not promoted to a completed review.

Fresh CPython 3.14.6 checks pass:

```sh
python3 -I -O -B research/pr116-evidence-reconciliation/verify.py
python3 -I -O -B research/pr116-evidence-reconciliation/test_package.py
python3 -I -B -m unittest discover -s tests -p test_pr116_ledger_evidence.py
python3 -B scripts/reconcile_pr_queue.py
python3 -I -B scripts/verify_selected_result.py
```

The original 28 tests and two new ledger regressions pass. The latter preserve
every later decision and reject a mismatched parent/head without mutating the
row. Regeneration is byte-stable. Selected-record integrity passes for the
current `836330098538459/500000000000000000`; no selected cold replay is claimed.

The broader historical ledger checks are **not green on this main**. Both the
unmodified pinned main and this revision fail `scripts/verify_pr_reconciliation.py`
on the identical stale hyperplane source pin for `scripts/verify_hpe_lean_binding.py`.
Both also report the same eight errors in the 25-test `test_pr_reconciliation.py`
suite: the accepted-successor pin for `scripts/run_isolated_tests.py`, and old
family projections for PR1155/1175/1758/1763/2046/2162/2244. These sources,
test cases and disposition records are unchanged by this revision. These
baseline failures are reported separately from the successful scoped checks;
no historical evidence is rewritten to silence them. Hosted CI for the revised
head remains a separate publication gate.

## Later current-main review continuation

The follow-up integrates canonical main
`38746ad3f6ffebcc0275e286b1dbb733d7c696dd`. An independent comparison of the
merged tree against that exact main covers all 2,397 ledger records: only
PR116 gains the expected historical-evidence pointer. Every other field,
record, attribution, review-completion and closure decision remains identical.
The source inventory gains only the pointer file's digest; every existing
input digest and all 100 efficient1800 dispositions are preserved. Both
ledgers regenerate byte-for-byte. Relative to the previous author head,
current main supplies 41 added records and 61 updates to existing records;
these later decisions are retained rather than overwritten by the historical
source-identification result.

The frozen capsule, result, producer, checker and package tests retain their
original bytes. Fresh command results and their exact published head are
reported in the PR follow-up; hosted CI remains separate. The earlier broader
historical-check failures above describe their pinned run, not a new claim
about all checks on this later main.
