# Enforce PR838's coverage contract in the selected replay

Lucas (@ljste)'s PR838 showed that the PR741 composition binding accepted
omitted ancestry stages and artifacts. This follow-up tests the complete
selected PR799 binding on actual archive files and enforces a versioned
coverage contract in the standard Makefile replay paths.

The pristine archived PR799 and historical PR741 replays pass. Removing
`ancestor/complex/local/CLIFFORD-REVIEW.json` and its receipt inventory entry
still makes the original **complete PR799 binding** return
`PASS_REBUILT_PR589_PR799_COMPOSITION`. The new check rejects that witness.
This is an evidence-admission defect, not a disproved scalar identity or
counterexample to the multiplication theorem.

## Implementation

`certificates/replay-coverage/pr741-sw4-v1.json` defines the exact ordered
22-stage sequence and all 44 required artifacts, separately from the candidate
receipt. The producer, manifest and spec are SHA-256 pinned. Stage names and
the 34 explicit artifact declarations are independently compared with the
producer AST; the remaining ten local output names are explicit in the
source-bound contract. The current X4 consumer and producer scripts have
their own version pins. A new producer requires a reviewed contract version.

`scripts/verify_replay_coverage.py` checks exact inventory and stage sequence,
execution-record equality, strict integer exit codes, containment and existing
hash bindings, then runs every original mathematical binding check. For PR799
it also checks top-level execution logs, the stored ancestry binding and result,
and existence of all named native logs. Native stage records have no log
digests; this check does not pretend otherwise.

`scripts/verify_frontier_complete.py` executes the unchanged historical cold
runner inside `work/replay/` and only then atomically publishes the public
`work/RESULT.json`, alongside `COVERAGE.json`. An explicitly reused ancestor must
pass coverage **before** any new native/global work starts. Both standard
`make frontier741-verify` and `make frontier799-verify` now invoke this runner;
`make verify` consequently enforces coverage on its historical PR741 stage.
Both existing cold-replay CI workflows also enforce this gate, with triggers
for contract/entrypoint changes and corrected nested artifact upload paths.
The old runners and binding scripts remain byte-identical because the selected
record pins them as reviewed proof supplements. Direct old-script invocations
retain their historical semantics; they are not the strengthened entrypoint.

The existing PR799 regression fixture uses ordinary copies instead of symlinks
so the same input bytes are tested without requiring Windows symlink privileges.

## Reproduce

Standard library, Python 3.11+; no solver or network:

```sh
python -I -B research/required-replay-coverage/verify.py
python -I -B research/required-replay-coverage/check_package.py
python -B -m unittest discover -s tests -p 'test_replay_coverage.py' -v
python -B -m unittest discover -s tests -p 'test_frontier7*bindings.py' -v
```

The deterministic receipt records the old/current outcome for every mutation.
Expected: `PASS_REQUIRED_REPLAY_COVERAGE 112 original PR799 accepts; 118 enforced rejections; valid historical and selected replays accepted`.
The matrix covers all 22 stage replacements, all 44 single inventory omissions,
all 42 otherwise-deletable ancestor artifacts, empty inventory, inconsistent
execution order, six additional type/hash/admission controls and two missing
selected logs. A public current-binding CLI witness is reproduced, the new
CLI rejects it, and incomplete ancestor reuse is rejected before launch.
Contract tests reject unknown versions, producer drift and escaping paths.

Check an existing complete historical PR799 replay, or the `replay/` directory
of a completed strengthened run:

```sh
python -I -B scripts/verify_replay_coverage.py --frontier 799 \
  --work /absolute/path/to/replay --ancestor /absolute/path/to/ancestor
```

Omit `--ancestor` only when its recorded reuse flag is false and the complete
ancestor is inside the replay's `ancestor/` directory. The explicit path avoids
guessing a relocated reuse directory from old logs. A fresh run can use:

```sh
python -B scripts/verify_frontier_complete.py --frontier 799 \
  --work /fresh/outside/repository/path --ancestor /complete/source-bound/ancestor
```

Without an ancestor argument, the original runner rebuilds it from scratch.
Coverage adds linear work in the artifact bytes plus small fixed manifest/AST
checks; it does not weaken, skip or replace original verification stages.

## Sources, credit and limits

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
PR838: `2a50020bb9564229874cbfbdc112e17b235bacfc`.
Input archives and historical checkers are pinned in SOURCES.json. The contract
was derived from the pinned producer and complete archive, not a mutable
candidate's self-declared inventory. The omission-domain design follows PR838;
its original audit is credited and not superseded or described as repaired in
place. No original PR838 source is edited or imported without attribution.

Credit Douglas Colkitt's reviewed checkers and retained replay; Chafik
Boukhalfa's PR741 construction; PR799's X4 construction; DreamingOfClouds'
PR589 transport on eumemic's PR555 supplier; all original predecessor notices.
Prepared for **nightangelflowerwin-ops** with substantial **OpenAI Codex**
assistance in implementation, testing and writing. Apache-2.0. No independent
human review is claimed. Concurrent PR841 addresses proof-pointer binding,
not these stage/artifact omissions.

Concurrent **PR847**, Chinmay (@chinmayarvind23), head
`72b8406b96ea2e0f37bb5143f594e12d4817c92a`, arrived during validation with
the basic public Make/CI coverage integration and a separately published
success record. That design is explicitly credited; no priority for it is
claimed. This independent implementation adds version-pinned producer and
consumer contracts, full current PR799 reachability evidence, checks on the
selected replay's own logs/result, strict exit metadata, offline source-drift
controls and a fresh native/global replay. The older bindings and selected
proof pins remain unchanged in both approaches. No PR847 code is imported.

Presence and hash consistency do not authenticate execution or independently
re-prove every mathematical artifact. Inherited all-size/compiler, common-label,
mutable-source, hosting, precision/tape and analytic conditions remain.
No kappa, selected record, construction source or `upstream/` byte is changed.
Validation, including any incomplete repository-wide run, is recorded separately.
