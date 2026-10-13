# PR741 composition receipt coverage audit

**Research audit and supplemental evidence check; no new kappa.** The pinned
`scripts/verify_frontier741_bindings.py` accepts incomplete complex replay
evidence when omissions also change its self-declared receipt inventory.
Its 22-stage check enforces count, distinct names and successful exit codes,
but does not require the producer's actual named stages. Its artifact loop
hashes supplied entries without requiring the complete producer inventory.

The experiment uses ordinary temporary files, the unmodified published checker
and the archived composed replay. All additions are confined to this directory.
Neither the selected frontier nor its source packages or `upstream/` is changed.

## Concrete result

Starting from the complete archived replay, the original checker accepts:

| Mutation domain | Completed cases | Original result | Supplemental result |
| --- | ---: | --- | --- |
| Replace one required stage with an unrelated successful command and delete its real log | 22/22 | Accept | Reject |
| Remove one artifact inventory entry, retaining the file | 44/44 | Accept | Reject |
| Remove one entry and delete the corresponding file | 42/42 | Accept | Reject |
| Empty the inventory, with files retained | 1/1 | Accept | Reject |
| Empty the inventory and delete all 42 indirectly consumed artifacts | 1/1 | Accept | Reject |
| Rehash `STAGES.json` after changing its order, leaving receipt stages intact | 1/1 | Accept | Reject |

The remaining two artifacts, `RESULT.json` and `global-replay/ASSEMBLY.json`,
are read directly by the checker. Their entries can be omitted but the files
cannot be deleted in this experiment. Among the 42 deletable artifacts are
the scalar/frame audit, Clifford phase review, wrapper checks, owner output,
admission controls and independent moment outputs. This does not show that
their mathematical contents are wrong; it shows that their continued presence
is not necessary for the original binding to return PASS.

For each stage substitution, the receipt and hashed `STAGES.json` consistently
record the replacement, and the replacement log has its correct SHA256. The
real named stage log is absent. Thus neither a bad hash nor disagreement
between the two stage records explains the finding. Two witnesses also invoke
the public binding CLI with assertions enabled: replacement of
`all-native-phase-edges`, and deletion of all 42 artifacts. Both exit zero and
write `PASS_REBUILT_PR589_PR741_COMPOSITION`.

Six negative controls remain rejected by both checkers: a missing stage at
reduced count, a failed stage, a wrong package pin, a corrupt listed hash, a
missing still-listed file, and a wrong kappa with a correctly rehashed assembly.
The pristine evidence passes both checks. The full deterministic outcomes are
in [EXPECTED.json](EXPECTED.json).

## Reproduction and supplemental check

From the repository root, using Python 3.11 or later and its standard library:

```sh
python3 -I -B research/frontier741-receipt-coverage-audit/verify.py
```

Expected result:

```text
PASS_SCOPED_PR741_RECEIPT_COVERAGE_AUDIT 111 altered-evidence cases accepted by original; 117 mutations rejected by supplement; pristine accepted
```

The command checks runtime source SHA256 pins, extracts ordinary archive members into
a temporary directory, invokes the original check on actual file mutations,
and compares every outcome against the committed receipt. It does not execute
the expensive supplier construction, use a solver or contact GitHub.
`--write-expected` regenerates only this directory's receipt.

The supplement requires the exact ordered stage names and artifact keys, and
equality between receipt stages and `STAGES.json`, before invoking the original
checker. The stage names are independently extracted from the pinned
producer's top-level `run` calls. The frozen artifact inventory contains the
producer's 34 explicit files and the ten `local/` outputs in the pinned archive.
This is an explicit contract for this producer version, not a schema inferred
from the possibly incomplete candidate receipt.

To apply the combined predicate to another fresh replay of this same producer:

```sh
python3 -I -B research/frontier741-receipt-coverage-audit/verify.py \
  --coverage-check /absolute/path/to/bit /absolute/path/to/complex
```

Expected: `PASS_PR741_COMPOSITION_WITH_REQUIRED_EVIDENCE_COVERAGE`. This leaves
the replay untouched. A different producer or selected frontier needs a newly
reviewed coverage contract. The supplement preserves the original scalar,
owner, source, artifact-hash, endpoint and outer-constraint checks. It does not
prove that a supplied log reflects an actual execution, authenticate arbitrary
receipts, or independently recompute the mathematical certificates.

## Pins, scope and attribution

Base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
Selected conditional kappa:
`1661202643272239/1000000000000000000 = 0.001661202643272239`.
Audited PR741 source head, as recorded in the selection:
`e516b1463606840a15f80aac1995d64ce0092e89`.
[SOURCES.json](SOURCES.json) records SHA256 and exact base Git-blob IDs for
the binding checker, its four repository input files, existing regression tests,
producer, immutable replay archive, selected record and maintainer review.
The selected-record pin records the immutable base snapshot as historical
context; it is not a runtime dependency on the moving selection file. All nine
runtime input pins are checked. The archive's exact container hash is
appropriate here because it is a committed immutable input; no
regenerated gzip hash is used as a mathematical equality test.

The final upstream refresh reached
`f567884aeb8851b6e794af1184119a3bfbe1e631`, which selects PR799 at conditional
kappa `1661634653669567/1000000000000000000`. The audited PR741 checker and
all nine runtime inputs remain byte-identical there. The investigation keeps
its original base and object; it does not audit PR799's new construction.
The [PR799 binding at that pinned refresh](https://github.com/CrocSwap/integer-mult-bounds/blob/f567884aeb8851b6e794af1184119a3bfbe1e631/scripts/verify_frontier799_bindings.py)
calls this PR741 checker for ancestry and then performs additional checks.
Acceptance of the mutations by that complete newer wrapper is not claimed.

Seed **72** selects the adversarial audit track and rotates the two complete
traversals. The domains are all 22 single-stage replacements, all 44 single
inventory omissions, all 42 deletable single artifacts, two combined omissions,
one inconsistent execution-stage record and six controls. The stopping rule
is completion of these finite domains,
not finding a first omission. No randomized search or general impossibility
result is claimed. [CLAIM.json](CLAIM.json) records candidate selection and
coordination checks; no pinned sprint issue existed.

The exact implication refuted is that a PASS from this pinned composition
binding requires the producer's complete stage-name sequence and all
inventoried artifact files to remain present. This is a checker admission
finding, not a counterexample to
the multiplication theorem, the finite construction, its strict 47 inequalities,
or its previously completed replay. The all-size/compiler, common-label and
mutable-source, whole-call hosting, precision/tape and analytic assumptions
remain inherited. The audit is neither a fresh supplier replay nor a formal
proof of the full theorem. The published checker stays byte-identical because
it is a selected proof supplement; the new predicate is separately reviewable.

Credit Douglas Colkitt's composition binding, archived replay and maintainer
review; Chafik Boukhalfa's PR741 construction and its retained source notices;
DreamingOfClouds' PR589 bit transport on eumemic's PR555 supplier; and the
predecessors credited in the [selected review](../../docs/research/community-frontier741-review.md).
PR704's review-ledger projection audit and PR740's finite-menu admission audit
are distinct prior examples of corruption controls, not dependencies of this
experiment. PR777's incorporated frame checker has a different mathematical
scope. Their contributions are not superseded by this note.

Contributor: Lucas (@ljste), with substantial OpenAI Codex assistance for
investigation, implementation and documentation. No independent human review,
delegated-agent review, remote CI success or stronger exponent is claimed.
New work is under the repository's Apache-2.0 license; predecessor files and
notices are retained unchanged.

The [local validation record](VALIDATION.json) includes an isolated relocated
optimized replay, rejection of altered expected evidence and altered checker
source, the supplemental CLI's positive and missing-file controls, seven
existing regression tests, strict type checking and the unchanged selected
record check. Full repository and fresh supplier replays were not rerun.
The final refresh examined 630 open PRs and found no matching coverage audit.
