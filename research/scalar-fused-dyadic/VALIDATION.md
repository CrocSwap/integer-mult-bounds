# Executed validation

Linux, 2026-10-13. Base `f567884aeb8851b6e794af1184119a3bfbe1e631`.
All performance numbers describe this host and the pinned #799 word.

| Command/check | Observed result |
|---|---|
| `/usr/bin/python3.12 -B -I -S verify.py` (3.12.3) | Complete deterministic receipt matches; 15 native controls reject identically |
| `/usr/bin/python3.14 -B -I -O verify.py` (3.14.4) | Same receipt and controls with optimization |
| `test_kernel.py`, both environments above | Nine tests pass |
| Every-update comparison | All 70,765 native target-row updates and unchanged sources agree; stream digest is committed |
| Arithmetic differential | 810 fused cases, 10,240 complete randomized state prefixes and three invalid-gate cases agree |
| Complete-process benchmarks | Five alternating pairs per interpreter; all 20 complete receipts match the maintainer receipt except timing |
| Minimal relocated checkout | Optimized Python 3.12 passes using only this package and four consumed source/input files, in a path with spaces |
| Altered differential receipt | Changing the claimed checked-column count fails complete receipt comparison |
| Source/archive packaging | Repacking the tar archive with identical member bytes passes; the word recompression positive control passes in both engines |
| Source corruption | Adding a newline to the pinned auditor is rejected before import |
| Existing output | Preserved; the wrapper rejects reuse |
| Selected-record check | Exact κ, original source inventory and proof supplement pass |
| Python syntax | All new modules parse successfully |

Source corruption and output preservation are tests in `test_kernel.py`.
The two deliberately faulty optimizer implementations are tested against the
complete audit. Dropping the destination term is rejected by entrance response
before endpoint testing. Ignoring dual mode passes the forward endpoint and
then fails the dual endpoint. An initial test expected the first mutant to
reach the endpoint guard; its expectation was corrected to the actual earlier
rejection. The optimizer itself did not require a correction.

The minimal-checkout packaging mutations were made only in a disposable copy
and restored between runs. No inherited source file was edited.

## Measurement details

The pilot profile executes 70,765 scalar `apply` calls and shows about 90% of
profiled audit time in that function. It is retained as a hotspot diagnostic,
not a timing comparator. Subsequent reference and fused pilot receipts match.
The final measurements use fresh subprocesses with identical `-B -I` flags,
alternating arm order and the exact same compressed word. Neither run arm
skips native checks or parent-interface binding. Complete stdout and receipt
serialization are included in the external wall/CPU measurements.

The reference/fused wall medians are 0.559843/0.374207 seconds on 3.12.3 and
0.501354/0.345660 seconds on 3.14.4. All samples are retained, including their
full-process and internal-auditor timings. No memory improvement was measured
or claimed. There is no timing pass threshold, cache flushing or CPU isolation.

The later addition of an untimed every-update differential pass changes only
`verify.py`. The benchmarked `adapter.py` and `kernel.py` are unchanged and
their exact hashes are included in both benchmark receipts.

## Current state and scope

At the final queue refresh there were 641 open PRs through #844. Searches
found no matching native scalar fusion package. #824's historical stage-pair
optimization was inspected and remains distinct. The upstream head was still
the exact base above. Only non-PR issue #650 requested Discussions; no sprint
coordination issue was available. Scope and source heads are in CLAIM.json.

Full `make verify`, supplier cold rebuilding, phase/wrapper replay, global
admission/assembly, Lean and hosted CI were not run or claimed for this opt-in
adapter. Its measured scope is the complete independent native audit only.
The selected frontier and `upstream/` are untouched. Inherited realization and
analytic obligations remain; this is not a full theorem proof.

Prepared for Gareth Davidson (@bitplane) with substantial OpenAI Codex
assistance. Apache-2.0; no independent human-review claim.
