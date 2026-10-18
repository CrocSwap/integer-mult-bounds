# Local validation and handoff

Base: `858771bcca3b8dd5d4ef4aa682a13cc9b7e23920`.
All changes are within `research/signed-connector-transfer-minimum/`.
The original PR1637 head was read back as `9bee6cc01f151b92ccfe147046855715843f066a`, still open, during verification.

## Passing checks

- `/opt/homebrew/bin/python3.12 scripts/research_package.py --package research/signed-connector-transfer-minimum`: `PASS_REGISTERED_RESEARCH_PACKAGE`, including read-only relocation and five on-disk corruptions.
- `python3 -I -B research/signed-connector-transfer-minimum/verify.py`: passing ordinary interpreter replay.
- `python3 -I -O -B research/signed-connector-transfer-minimum/verify.py --search`: `PASS_DISCOVERY_REPLAY`, reproducing the exact stopping log and four-transfer word with Apple clang 17.0.0 / C++17.
- `make selected-record-check`: passing selected record, exact kappa, original source inventory and proof supplements. Selected value remains `836330098538459/500000000000000000`.

Registered replay interpreter: Python 3.12.12.
Other local interpreter: 3.14.6 (main, Jun 10 2026, 10:03:53) [Clang 21.0.0 (clang-2100.0.123.102)].
Platform: Darwin 25.5.0 arm64.

## Evidence scope

The default replay checks all 720 signed one-root paths using two different enumeration implementations; three complete symbolic short-transfer shapes; the short and expanded free noncommutative identities and inverses; 44 short-word semantic mutations; 24 independent dense matrix fixtures covering 660 arbitrary basis columns per direction; two dense semantic mutations; all fields of the independent receipt; and the complete tape bills at L=1,2,3,4,8,16. The source-hypothesis and four-transfer symbolic controls are separate.

The discovery replay completes the finite domain through three transfers (1,641,024 restored source traces) and stops at the first four-transfer word. Length-four coverage is deliberately incomplete. The written arbitrary-coefficient one-way proof does not infer its conclusion from that incomplete search.

The two new implementations were written by one AI agent. No independent human review, proof-assistant proof, selected-supplier cold replay (`make frontier1094-verify`), root `make verify`, native hosting/precision admission or changed kappa is claimed. Hosted CI status is separate and is read after submission.

The upstream repository currently lists neither `codex` nor `codex-automation` labels; no such labels are created by this contribution.

## Submission refresh

The pre-submission overlap helper fully paginated 593 open PRs and 291 Discussion records, with no warnings (snapshots 05:09:18 / 05:10:35 UTC on 2026-10-14). PR1438 and PR1498 were read at their exact heads; their source-port method and distinct binary targets are credited in the proof and README. PR1637 remained at its pinned six-pass head. Main advanced to `1f7a934975e5eacaf83511c9ac870263bf095e05`; its selected-record bytes remain identical to the pinned base. The branch deliberately retains its original exact base. `git diff --cached --check` passes; no upstream or selected files change.

## Published contribution

[PR1651](https://github.com/CrocSwap/integer-mult-bounds/pull/1651) is open for review. Mathematical package commit: `8450afe561333aa6ee1bb9108c3e4f854eaf19c1`. Its clean committed export passes the default Python 3.12 verifier. Publication used the GitHub Git-data API, verifying both tree `4b3abf768997a20733da74fa6d2464ea7885c26f` and commit identity against local Git. The initial registered-package workflow `38515847446` and other hosted checks were queued at readback; this is not CI success. The final handoff commit changes only this receipt and the local claim result. No merge was attempted.
