# PR236: independent source-command and recorded-axiom audit

This research-consolidation result adds **independently implemented source and
log parsing** to the PR236 evidence chain. It complements Will Richards's open
[PR746](https://github.com/CrocSwap/integer-mult-bounds/pull/746), inspected at
`ee3580bd708d82b5bdfda6a2bc3f0a34710be50e`, which restores the source package and
reuses the original driver's parsers. Here neither original parser is imported
or executed: a separate scanner masks nested comments and quoted strings before
checking every source import and requested axiom command, and a separate parser
recounts the retained multiline axiom reports. The implementation found full
agreement on the pinned corpus. It does not import the source package, change
a PR disposition, or establish a new exponent.

At base `f567884aeb8851b6e794af1184119a3bfbe1e631`, the ledger records a completed
finite kernel audit of [James Chang's PR236](https://github.com/CrocSwap/integer-mult-bounds/pull/236),
but no source-package integration location. These are different facts. The
following exact reconciliation explains which artifacts are present and how
they connect; it is not a request to close that PR.

## Result

- None of the **14 submitted package files** has a byte-identical ordinary
  tracked-file counterpart in the pinned base tree. This is an exhaustive
  Git-blob comparison, not merely a check of the original directory name.
- The submitted `INPUT_MAP.json` is retained byte-for-byte inside
  `pr236-kernel-evidence.tar.gz`. The submitted `offline_check.py` produces the
  retained Darwin driver with exactly three documented edits: policy name,
  removal of the address-space field, and removal of the `RLIMIT_AS` call.
  Therefore those two files are recoverable from named retained evidence;
  the other twelve are not recovered by these two mechanisms. This is not an
  assertion that no other archive anywhere contains some of their bytes.
- Every one of **3,606 accepted Lean sources** in the submitted archive matches
  its mapped SHA256 and historical receipt. Independent lexical scanning also
  recovers exactly the mapped imports and audit requests, including **101
  modules without audit requests**. All **7,253 internal dependency
  edges** bind to the object digests recorded in the prerequisite receipts.
  The module order, rebuilt/reused partition, complete receipt/log inventory,
  map equality, log hashes and summary hashes agree.
- An independent parser recounts **14,320 recorded declaration audits**,
  including **2,816 recorded axiom-free declarations**. The remaining observed
  axioms are exactly `Classical.choice`, `Quot.sound` and `propext`.
- All **eight scientific inputs** are also byte-identical to their actual
  files at scientific target `d1d6c070f5a8c684727ee7ec35d930f9ebfa9758`.
  The six readable principal theorem files equal the corresponding accepted
  archive sources.
- The retained evidence archive has **no `.olean` objects or compiler binary**.
  It preserves their digest claims, not the bytes needed to independently
  revalidate them. The checker explicitly reports that limitation.

The historical summary partitions the accepted set into 3,602 rebuilt modules
and four modules reused from that audit. Its policy name contains `subset`, but
its complete source/receipt inventory covers all 3,606 modules. Conversely, this
later Darwin audit does not establish a full run of the original Linux-capable
driver under its advertised 4 GiB address-space limit. The original PR README's
planning estimate and the later adapted audit describe different executions.

## Reproduce

From a checkout containing this contribution, with Python 3.11+ and Git:

```sh
python3 -B research/pr236-independent-command-audit/verify.py --fetch --check research/pr236-independent-command-audit/REPORT.json
```

Expected result:

```text
PASS_PR236_INDEPENDENT_SOURCE_COMMAND_AND_LOG_AUDIT
3606 sources/receipts/logs; 14320 recorded declarations; 2816 recorded axiom-free declarations; 8 scientific input Git matches
No compiler or .olean bytes present; no fresh kernel compilation.
```

`--fetch` performs read-only fetches of missing exact commits from upstream.
Once those Git objects exist locally, the same command without `--fetch` works
offline. It reads the **pinned base**, not later working-tree copies of the
historical evidence. It does not execute either submitted driver, extract
archives onto the filesystem, install Lean, or regenerate existing artifacts.
Long-term reproduction still requires retention of the pinned submitted Git
objects; this contribution is not an archival import of PR236.

The report records the full 14-file inventory and source/evidence digests.
To regenerate only this report, use `--write` in place of `--check`.

Run the focused controls with:

```sh
python3 -B -m unittest discover -s tests -p test_pr236_independent_command_audit.py -v
python3 -O -B -m unittest discover -s tests -p test_pr236_independent_command_audit.py -v
```

All **22 tests** pass in both modes. Corruptions cover missing/changed sources,
scientific inputs, dependency cycles, receipt coverage, source/dependency/policy
bindings, missing/duplicate/disallowed axiom reports, failed compiler receipts,
and archive ambiguity. Source controls rehash modified import/audit commands
and exercise nested comments, escaped quotes and multiline strings containing
command-like text. Duplicate JSON keys and Boolean/integer substitutions are
rejected. Several controls repair the outer log/summary hashes
after mutation, so rejection must come from the broken inner obligation.
A deliberate positive boundary control consistently substitutes an absent
object's digest throughout the synthetic receipt graph: the structural check
still passes and explicitly refuses to call that object verification.

## Pins, scope and attribution

| Role | Exact commit |
|---|---|
| Upstream base and retained maintainer evidence | `f567884aeb8851b6e794af1184119a3bfbe1e631` |
| Submitted PR236 package | `f825b6fdfd763f189db3aa1c02fdd5d604c85a01` |
| Historical scientific inputs | `d1d6c070f5a8c684727ee7ec35d930f9ebfa9758` |

The new checker establishes byte/provenance, independent command-list agreement
and recorded-evidence consistency. Its scanner supports the literal single-line
`import` and `#print axioms` syntax used by this frozen corpus; it is not a
general Lean parser or elaborator. It does not independently reconstruct source
extraction, rerun a kernel, verify the missing compiled objects, or revalidate
the installed Lean standard library. Full Lean parsing/elaboration and the
historical compiler's honesty remain trust boundaries. Its axiom
recount concerns recorded logs, not a newly executed `#print axioms` command.
Pinned Git objects and source/archive digests authenticate the inputs before
the structural checks; a self-consistent fabricated evidence collection is
not a substitute for those pins.

The package concerns historical conditional κ = `4609169/10000000000`, not
the base's selected #799/#589 result. No current-frontier instantiation,
all-size compiler/analytic theorem, global tape-cost result, or new κ follows.
See the retained [scope review](../community-round9-audit/pr236-scope-review.md)
for the actual theorem boundaries, including the scratch-bank obstruction.

Credit belongs to **James Chang (`jamesyc`)** for PR236, its accepted sources,
source map, original driver and fixtures; to **Douglas Colkitt's maintainer
review** for the round-nine Darwin adapter, receipts, logs and scope audit; and
to the paired-cube construction's original contributors, including
**icekylinx**, with their notices retained at the pinned scientific target.
**Will Richards (`williamreidrichards`)**, with disclosed OpenAI Codex assistance,
already proposed source restoration and parser-reusing reconciliation in PR746;
this contribution deliberately provides independent parser cross-checks and
direct Git-object verification rather than another restoration proposal.
This independent reconciliation was prepared for **WeberChen8128** with
substantial **OpenAI Codex** assistance, under the repository's Apache-2.0
license. It imports no new predecessor source files.

The [local sprint claim](CLAIM.md) records OS-random seed 95, candidate selection,
the avoidance of overlapping PR828, the later discovery of PR746 and resulting
independent-parser scope refinement, and the observation/coordination limits.
