# Bounded ELF literal discovery: mapping repair and synthetic controls

The v2 helper rejects two ambiguous ELF metadata cases that the original v1 source
accepted: a file-unique literal whose virtual span overlaps a competing LOAD, and
a non-executable entry mapping that shares file bytes with an executable LOAD at a
different virtual address. File-to-VA mapping now checks the reverse mapping over
the full span, including partial/zero-fill memory overlap. Entry PF_X comes from
the unique exact entry-VA LOAD. The rejected source, independent objections and
exact diff remain available.

This is an accepted component from a **closed partial actual-inspection round**.
The independently accepted result is the repaired source plus **23 passing synthetic
cases in normal mode and 23 in optimized mode, over 20 literal buffers**. There was
no actual GCC image inspection or helper.main/decoder run. Full P1/P2/P3/P4 remain
false: **0/4 complete**, closed 2026-11-02 23:55:37 UTC. The capture guard v2/v3
remains REJECT/HOLD because a close error can overwrite an earlier read/pin/write
error. This package contains its inert review and closure evidence, not a guard
executable or repair. The actual 60-second grant was never issued or spent.

## Source and added value

Base commit: `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, tree
`e6898c8ba7a27b71587c32ba3f639259ceeeed91`. Current retained canonical guidance
was refreshed by the parent at 23:44 UTC on 2026-11-02; parent must refresh live
compatibility again before publication. The original catalogue card is pinned in
TASK.json solely as changed-scope infrastructure provenance. No picker was run.

| Component | Bytes | SHA256 |
| --- | ---: | --- |
| repair-v2/passive_image_candidates_v2.py | 11809 | 56b44235f55685d61e5c8b8099d825b4ec5a53987910f506dffad309c12ffb53 |
| controls-v1/literal_fixtures_v1.py | 3022 | 979f719820707490920bf39f3c398129ed6e49b2df898e76a1f7292cc8d8d47d |
| controls-v1/test_literal_candidates_v1.py | 8023 | cbbe3139f6d67d2da653f5aaf4a62f0ab108f5a1cde37e0f444f3ef826ae9ed6 |

The source files and sibling layout are unchanged. The harness authenticates exact
helper/fixture bytes before compiling those same checked bytes into fresh named
non-main modules, calls only inspect on owned synthetic buffers, and checks explicit
conditions without removable asserts. C01 and C02 require actual Stop outcomes;
there is no expected-failure waiver. Synthetic buffers model ELF metadata and are
not claimed to be kernel-loadable executables. The helper retains its guarded
actual-image main as source, but no registered command invokes it.

Nearest related work: [#6397 criterion](https://github.com/CrocSwap/integer-mult-bounds/pull/6397),
[#6362 input constructors](https://github.com/CrocSwap/integer-mult-bounds/pull/6362),
[#6434 raw pilot error accounting](https://github.com/CrocSwap/integer-mult-bounds/pull/6434),
and [#6454 conditional phase frame](https://github.com/CrocSwap/integer-mult-bounds/pull/6454).
This package contributes the separate mapping repair and finite literal controls.
Parent reports #6454 head `e83090c937b920affc87593f02b535e6c9773615`, hosted run
41547936328 attempt 1 completed success with plan success and replay skipped.
That predecessor status is a 2026-11-02 publication observation, not this package's
hosted status or candidate replay. Bounded parent PR coverage currently spans 39
nodes/29 edges; older heads remain historical, and finite graph coverage is not
exhaustive novelty or incorporation proof. The graph is not an executable input.

## Evidence and accounting

- reviews/initial-source retains the original rejection (M01 and M02).
- reviews/repaired-source/HELPER-CONTROLS-SOURCE-v1.json is the independent source
  PASS (`cdf88f0eeaff9ca22d9964a086875a43b5e87a0647de41c4b637129acb553f37`).
- evidence/controls-execution-v1 retains all six raw stdout/stderr/GNU-time files,
  the exact grant, tool-result receipts and ledger. Both stdout records show 23
  unique passes, zero failures, and optimize flags 0/1. These runs preceded packaging.
- reviews/controls-execution/REVIEW-v2.json is the separate evidence PASS
  (`a7bb90acc80f519af72abd87993c31c0b2c3a938d0a6e29508daee7c589520d7`). Its v1
  and metadata clarification remain preserved; the clarification adds no run.
- context/ROUND-CLOSE-v1.json is the full exact closure receipt
  (`e8fc63616c75ad6dd5b5b69620764e29f7e6040ad292c5a5924cd6027a5e2c93`).
- consultation retains only the task-relevant Pro21 response text and local critical
  assessments/addendum. It contains no raw accessibility/sidebar/history capture.

GNU wall observations were 0.16/0.17 seconds, tool wall 0.065126715/0.071047239.
The declared max(toolwall, GNUwall)+0.01 policy charged 0.17+0.18 = 0.35 seconds.
Supplemental combined policy time became 100.130533479 seconds; canonical policy
94.550533479 seconds is unchanged. Individual GNU RSS 22608/22604 KiB does not
measure complete tree peak. Physical costs remain **OPEN_NOT_ZERO**. This archive
adds zero original activity credit: 43.5%, 22/49, full stage gate qualification 20% (2/10), overall milestone qualification 10% (1/10),
and 24 components/52 helpers remain unchanged. Full C05 and V03 are false. A
separate paused application goal remains paused.

## Reproduction contract

Python 3.12 and its standard library suffice. All transitive executable inputs are
package-local and explicitly named in VERIFY.json. Its two registered commands run the narrow publication adapter
run_export_controls.py in normal and optimized modes. The adapter resolves its
own package directory to supply the unchanged harness with the required absolute
v2 helper path and SHA256. No external scientific input or actual GCC
image is required. The harness permits only its sibling repair-v2 helper.

From the repository root, after a separate local parent release:

```sh
python3 -I -B research/h25-elf-literal-discovery-controls/verify_integrity.py
python3 -B scripts/research_package.py --package research/h25-elf-literal-discovery-controls --check-only
python3 -B scripts/research_package.py --package research/h25-elf-literal-discovery-controls
```

The static integrity checker reads data and hashes bytes; it never imports candidate
source. The registered replay executes only the normal/O publication adapter, which calls
only the authenticated NEW synthetic harness main.
For a Git-free export, let PACKAGE be its absolute package directory:

```sh
python3 -I -B "$PACKAGE/verify_integrity.py"
python3 -I -B "$PACKAGE/run_export_controls.py"
python3 -I -B -O "$PACKAGE/run_export_controls.py"
```

These are reproduction instructions, not claims that staging/cold/hosted validation
has already run. At the authoring freeze all new package validation commands remain
UNRUN pending the parent review. Any later outcomes belong in the external
publication receipt bound to the exact commit. No scientific/native/Lean/full
historical suite, target invocation or archived guard execution is authorized here.

SOURCE-MAP.json maps exact exported and newly authored bytes to origins, mode,
Git blob ID, size and SHA256. MANIFEST.json covers every other package file; its
own identity is supplied by the publication tree/external freeze. The source map
excludes itself and MANIFEST to avoid circular self hashes. The integrity check is
archival byte/metadata validation, not scientific acceptance. .gitattributes disables
text, filter, ident and encoding transformations within this package.

SOURCES.json binds the genuine base provenance through Git objects. Local creation
uses a read-only alternate; unrelated base PDF blob
`f0d42d430159f3f46dcf447ecb5df8aa9355e208` is known missing and stays unrepaired.
This is separate from the self-contained component export and does not establish
complete repository object availability. Historical absolute paths in protocol,
reviews and receipts remain unchanged inert provenance; none is followed by replay.

## Publication adapter and read-only export

The upstream runner substitutes {package} with a repository-relative CLI string;
the frozen harness requires an absolute --helper path. run_export_controls.py
resolves its own package directory, checks the harness's exact 8023 bytes/SHA256
before compiling those SAME checked bytes into a fresh non-main namespace with
absolute __file__, then calls only harness.main with the absolute sibling v2
helper path and fixed digest. Unexpected adapter arguments are refused. All
three accepted helper/harness/builder files remain byte-identical. No helper.main,
actual image, decoder, subprocess or network is called by this adapter.

The static checker accepts physical permissions exactly 0644 or read-only 0444,
while MANIFEST/SOURCE-MAP retain logical Git mode 100644. It rejects executable
permissions and links, and checks the 8 MiB file-length cap before and after each
file read. These are publication-only corrections; no actual round is reopened.
All successor validation remains UNRUN pending exact independent source review.

## Remaining limits

Raw literal/reference patterns are candidate discovery only. No instruction
boundary, relocation effect, role/reachability, callee/private-call/alias semantics,
D applicability, runtime frame or operational prefix certificate is qualified.
S04 only retains an interior candidate as unvalidated; S06 only checks nonpromotion
after overwrite. S11role, S12relocations and S13privatecalls are unimplemented
conceptual falsifiers. No complete P1, P2, P3 or P4, feasibility, scientific speedup,
supplier admission, selected-frontier adoption or kappa result follows.

## Open next questions

Structured questions, first steps and blockers are in TASK.json. First-error
preservation remains the immediate source blocker: a later separately authorized
round would need a reviewed capture successor that retains the first read/pin/write
failure through close and secondary cleanup. This closed round does not authorize
that repair. Actual-image boundary/role/effect qualification would then require its
own concrete admission and bounded plan, including S11/S12/S13. No automatic
continuation, new funding or actual-image run is requested by this archive.

## Credit

See NOTICE.md and the unchanged base LICENSE/NOTICE snapshots in notices/.
The complete base CONTRIBUTORS.md is pinned in SOURCES.json and retained in Git history. New contribution material is Apache-2.0. Substantial OpenAI Codex/assigned
GPT-6.1 Sol Max assistance and independent AI reviews are disclosed. Neither
consultation nor AI source/evidence review is human or proof-kernel acceptance.
