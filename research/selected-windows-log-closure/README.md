# Complete Windows selected-stage comparison with authenticated log conversion

This package closes PR2344's explicit composed-caller/log-policy handoff. It
freshly executes PR2336's pinned Windows successor and compares all **105 strict
outputs plus the complete outer log** through PR2344 and PR2101's unchanged
predicates. Before changing a log byte or digest, it authenticates all **30
same-side raw references**. Only the eleven named inner logs and the outer log
admit CRLF-to-LF conversion; bare CR and every other byte difference reject.

No frozen source, selected record, scientific algorithm or kappa changes.

## Scope and evidence

The `portable-replay` selection and precise refinement are in `TASK.json`.
`SOURCES.json` pins all 43 live scientific inputs and historical provenance.
`PREDECESSORS.json` pins eleven unchanged vendor files by Git head, blob and
SHA256, including their source manifests and original attribution.

The original PR1094 entry point's native-Windows manifest rejection was
reproduced. That failure and its two `.as_posix()` substitutions are **inherited**
from PR2316/2336. The new result is composition with the stricter complete
comparison and an authenticated log policy, rather than another discovery of
the path failure or a new successor implementation.

The scientific child compiles the original entry point with exactly PR2336's
two checked substitutions and `optimize=0`; all inherited assertions remain.
Ten archived PR1042 local inputs are checked against their complete source
receipt. Reviewed PR1094 output and assembly are bound to their immutable
archives and committed receipts. The current selected scientific inputs remain
the historical baseline; this is not a replay of every ancestor.

On native Windows 11 build 26300 / CPython 3.12.7, a fresh execution completed
all eleven strict stages and passed the new complete comparison. The 17 raw
file differences comprise the eleven CRLF logs, six-role receipt, reordered
invoice and its two consumers, and two timing/log-reference receipts. Those
are explicit policy cases, not ignored files. The registered optimized replay
passed six positive and 203 rejecting controls recorded in `CONTROLS.json`
in 258.533 seconds, including an 86.156-second native stage. Separate AI
source/proof review found no blocking issue; it did not repeat the long replay.

The first local attempt stopped in inherited bit controls because the sandbox
TEMP directory was not writable. Repeating with a writable workspace TEMP/TMP
resolved that environment failure. It is not a mathematical defect or part of
the new acceptance policy.

## Why normalization does not waive the evidence

`compare_logs.py` first calls PR2344's exact role adapter and PR2101's raw-edge
admission. Only then does it canonicalize the eleven named logs and rebind the
corresponding 22 stage-log hash fields. The full predecessor comparator runs
again on the normalized representation. The outer log retains the complete
13-line, same-side timing check. `PROOF.md` states this implication precisely.

No global string replacement, generic `log_sha256` exemption, basename role
matching, unknown-field stripping, or floating-point JSON comparison is used.
An exact serializer preserves Decimal/integer/Boolean distinctions when
writing the two normalized stage receipts. Unchanged scientific JSON and gzip
payloads retain the predecessor's complete typed comparison.

## Reproduce

From repo root, standard-library Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/selected-windows-log-closure --check-only
python3.12 scripts/research_package.py --package research/selected-windows-log-closure
```

The registered parent is optimized; the mathematical child is not. To preserve
the work and execution report, pass a fresh `--work DIRECTORY` and optional
`--report FILE` directly to `verify.py`. Default replay is temporary and does
not overwrite committed evidence. Use writable TEMP/TMP when sandbox policy
requires it. `--skip-controls` is diagnostic only and is not registered acceptance.

Controls include all 105 output omissions; repaired semantic changes to every
inner log; bare CR; stale raw links after otherwise-valid line-ending changes;
missing fresh timing fields; every outer-log line; misbound input roles; changed
scientific content and invoice with repaired references; invalid JSON; exact
numeric type preservation; and unchanged predecessor corruption. Positive
controls retain native output, reference identity, LF, CRLF and mixed per-log
representations. These finite controls support the documented boundary; they
are not a formal implementation proof.

## Limits

This is one native-Windows final-stage run and a composed representation policy,
not a full cold supplier replay or proof-assistant verification. PR2344's narrow
root grammar remains: canonical POSIX paths and ordinary absolute Windows
drive paths; UNC, device and extended-length roots reject. Detached processes,
arbitrary log syntaxes, new output schemas and unclassified digest graphs are
outside this policy. No Linux/macOS execution of this new caller, hosted CI,
independent human review or maintainer acceptance is claimed. All inherited
all-size/compiler, common-label, hosting, precision/tape and analytic obligations
remain unchanged.

## Open next questions

Can an earlier PR1042 stage receive an equally complete source-bound output and
reference policy? This matters for cold ancestry portability. First select one
stage, inspect every output and raw edge, then execute it with its declared
native dependencies. The blocker is that stage's separate schema, provenance
and native dependency review; this package does not generalize by dropping
unclassified fields.

## Credit

Credit Dennis / antunishdPursuit (PR2336), AAAmirinu (PR2344), Adam Gall
(PR2101/2059), commdata2338 (PR2040), josecarlosgonzalezroque-design (PR2316),
Josie Elliston (PR1824), Maxime Fleury and Antoine Olivier, and Rohan Arun,
Jeremy Kothe, Douglas Colkitt and the retained supplier lineage. Vendor source
bytes and notices are unchanged. Prepared for ywz65 with substantial OpenAI
Codex assistance in investigation, implementation, checking and writing.
Apache-2.0; no independent human review is claimed.
