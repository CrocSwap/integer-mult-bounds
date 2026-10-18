# Bounded implementation and verification decisions

Separate Before Serializing Shared State led to one owned package/cache,
one fresh branch and OS locks only for shared Git/claim transactions.
Prove It Works led to the actual source-bound word replay, exact one-layer
trace projection, separate numeric-depth interpreter and committed export
replays. No extra agents or worktrees were created.

Every new executable path is terminating, iterative and uses explicit
exceptions that remain enabled under Python optimization. The fixed input
hashes bind all event and recipe collections before interpretation. There
are 53,118 events, 712 fields, native ranks at most nine, 512 used cover
maps, 73-bit owner matrices and 512-point active kernels. Primary slopes
are independent of lambda. The numeric control interpreter permits only
integer depths 1 through 8. Input files are capped at 24 MB, decoded
certificate/member payloads at 12 MB, archive inventory at 1000 entries,
source manifest at 32 KiB and retained/receipt files at 64 KiB. No archive
symbolic or hard links are accepted. File and archive streams close on all
exits. Subprocess controls have 30-second timeouts and checked outcomes.

Functions stay below 60 physical lines after formatting. CLI output uses
exclusive creation. The source manifest has an exact byte pin and receipts
use canonical JSON, so Python's bool/int equality cannot admit type
mutations. Controls copy files with fresh writable regular destinations
beneath their own TMPDIR and never chmod source, links or shared runtimes.
No interpreter or tool installation is changed.

Rule: 3, fixed memory capacity.
Location: binding.py, verify.py, independent.py and test_verify.py.
Reason: Python and standard-library rational/JSON operations allocate.
Scope: This finite source-authenticated terminating checker.
Compensating control: Fixed input bytes, 712-field states, at most nine
native factors and numeric control depth eight bound all live collections
and rational values. Traces stream into SHA256 rather than retaining cuts.
Verification: Warning-strict registered/direct and optimized control runs.
Follow-up: A native implementation requiring allocation guarantees needs
fixed arrays and an explicit integer/rational bit-capacity proof.

Rule: 8, metaprogramming.
Location: dataclass declaration in verify.py and unittest discovery.
Reason: Python supplies bounded field methods and test dispatch.
Scope: One immutable four-field record and five local behavioral groups.
Compensating control: Direct explicit verifier calls, fixed test inventory,
source authentication and no dynamic source evaluation/import factories.
Verification: Normal and optimized replays execute all entry points.
Follow-up: Replace generated record methods if a native checker is built.

Rule: 10, diagnostics.
Location: This package only.
Reason: No compiled build or repository-wide static type checker is changed.
Scope: Four new Python files and the registered hook.
Compensating control: Warnings-as-errors, optimized behavioral tests, Ruff
checks/format, AST compilation and explicit boundary validation.
Verification: Exact commands and results are retained in CHECKS.json.
Follow-up: A physical implementation needs its own strict compiler/runtime
analysis; these interpreted diagnostics are not a type or allocation proof.
