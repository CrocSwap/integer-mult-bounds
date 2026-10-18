# Owner-bound successor for the selected strict replay

This optional runner completes the unchanged selected PR1094 strict replay,
then checks that the emitted hosted template contains **exactly the frozen
owner list, including every time**, and names its independently pinned
owner-gzip digest. It writes `BOUND-REPLAY.json` only after both conditions
and the existing strict replay succeed.

The missing equality and proposed guard belong to Josie Elliston's
[PR1959](https://github.com/CrocSwap/integer-mult-bounds/pull/1959), open
question 2. Aaron Wang's [PR2301](https://github.com/CrocSwap/integer-mult-bounds/pull/2301)
executes two accepted counterexamples. The new contribution here is the
runnable successor and its tested composition with the actual strict
caller, not rediscovery of that gap or a new owner theorem.

## Result and contract

`run_bound.py` launches the original
`research/complex-t16-rare-pattern-exchanges/verify.py` in a separate Python
process. That original entry point still checks its file manifest, extracts
the exact PR1087 archive, overlays the selected OWNERS/PLAN/SPEC, and runs
all eleven strict stages. No frozen source is patched, no existing
predicate is disabled, and the selected record/default command is unchanged.

After the subprocess succeeds, the successor:

1. Checks its complete eleven-stage ledger and log hashes against the fresh
   strict `REPLAY.json`.
2. Checks that the executed owner-file bytes equal the independently pinned
   selected owner input.
3. Checks exact typed JSON equality of the **entire** `hosting.pooled_slots`
   list and the pinned owner list: 69,120 records, all eleven fields, list
   order and keys included. This catches `false` and `0.0` in place of
   integer `0`, even though Python's ordinary dictionary equality does not.
4. Checks `hosting.owner_map_sha256` against that pinned gzip's raw SHA256.
5. Binds the same checked template payload to its fresh assembly, owner,
   invoice and HOSTED receipts, and rechecks source pins before writing the
   new success receipt.

The new gate parses exactly the bytes it hashes, rejects duplicate JSON
keys/nonfinite constants, and uses explicit exceptions under `-O`. Inherited
assertion-based stages always run without optimization; optimization and
witness-discovery environment variables are removed from their subprocess
environment. Failed work can retain diagnostic legacy output, but cannot
receive the new `BOUND-REPLAY.json` success receipt. Existing output is
never overwritten.

This is an explicit conjunction of the existing strict acceptance and one
new owner-map postcondition. It does not establish a physical consumer's
behavior merely from metadata, and does not validate all descriptive fields
identified by [PR2273](https://github.com/CrocSwap/integer-mult-bounds/pull/2273).

## Reproduce

Run the successor with a separately prepared, valid selected local provider:

```sh
python3.12 -I -B research/selected-owner-bound-replay/run_bound.py \
  --local /absolute/path/to/slots/local \
  --work /tmp/new-owner-bound-replay
```

The output directory must be fresh and outside the checkout. The supplied
local provider remains subject to the unchanged original content checks.
The new receipt names the original strict receipt and all relevant hashes;
consumers of this stronger contract should require `PASS_SELECTED_OWNER_BOUND_REPLAY`.

The short registered check exercises only the new gate on the archived
selected fixture and its controls:

```sh
python3.12 scripts/research_package.py --package research/selected-owner-bound-replay
```

It reports `strict_replay_executed=false`. To execute the complete
integration test, using only pinned archived PR1042 local inputs:

```sh
python3.12 -I -B research/selected-owner-bound-replay/full_check.py \
  --work /tmp/new-owner-bound-integration
```

This runs the successor under `-O` with inherited `PYTHONOPTIMIZE=2`, while
its original strict subprocesses retain assertions. It then constructs both
PR2301 mutants and reruns their six post-emit stages and twenty final
predicates before applying the new gate. The original PR2301 runner and
final predicates are reused byte-for-byte with their filesystem roots
rebound, not described as an independent reimplementation. A dedicated
`selected-owner-bound-replay.yml` workflow runs this explicit integration
mode. No third-party Python requirements are needed.

## Executed evidence

Local CPython 3.12.3 integration passed:

| Fixture | Existing acceptance | Added gate |
| --- | --- | --- |
| Actual selected positive | All 11 strict stages, all inherited final checks | Pass: all 69,120 roles |
| PR2301 F1: equal-width slots 0/480 swap times 0/1 | All 6 post-emit stages and 20/20 final predicates | Reject: owner list differs |
| PR2301 F2: wrong owner-map digest, all template hash links updated | All 6 post-emit stages and 20/20 final predicates | Reject: digest link differs |

[INTEGRATION.json](INTEGRATION.json) records the actual run, including the
source pins, original replay hashes and each accepted-mutant predicate.
Times/log hashes in the underlying strict run are observational, not
portable mathematical identities. Hosted CI is separate from this local
receipt. The full local integration took about one minute on this host;
there is no general runtime guarantee.

The short [RESULT.json](RESULT.json) check rejects 15 targeted mutations:
the two PR2301 witnesses, changed/Boolean/float/missing times, an extra role
field, changed port, missing/duplicate/reordered roles, a non-list, a
duplicate JSON key, wrong owner bytes and a nonfinite constant. It accepts
two valid generated-template re-encodings and preserves pre-existing output.
Re-encoding permission applies to generated templates only: the frozen
owner gzip and archives remain exact immutable byte inputs.

## Scope and sources

This closes the executable guard handoff in an **opt-in** successor.
Maintainer adoption of the selected entry point remains a separate choice.
The positive integration reuses archived source-bound PR1042 local inputs;
it does not cold-rebuild their ancestry, execute the full orthogonal-cover
payload, establish all-size/compiler/precision/analytic obligations or
change κ. The underlying selected fixture already satisfies this equality;
this repairs an admission implication, not its mathematical data.

Canonical base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision
4. OS-random assignment `1b0fdf6421f5fa138fbf6c777aace45b` selected
`supplier-boundary-audit`; [TASK.json](TASK.json) records the refinement.
Coordination: [Discussion2347](https://github.com/CrocSwap/integer-mult-bounds/discussions/2347).
[SOURCES.json](SOURCES.json) pins all direct gate inputs. The original
strict driver retains its own 21 root-input pins and archive/manifest
checks. The registered gate does not run those inherited stages; the
integration workflow does. [PREDECESSOR.json](PREDECESSOR.json) binds the
exact PR2301 test helper at `0b38025ddb2c06f696c54a18f50b0c0228493eab`.

## Open next questions

- Should maintainers adopt this successor as the selected entry point?
  Review the small runner and both accepted-then-rejected fixtures first.
  Adoption is the remaining policy choice; this package makes the proposal
  concrete without changing the selected default.
- Which remaining descriptive template fields require a semantic contract
  before a physical consumer uses them? Start with an actual reader and
  its required invariant. This depends on a concrete consumer; repeating
  PR2273's field census would not answer it.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

## Credit

Gareth Davidson (`bitplane`) with substantial OpenAI Codex assistance;
author-checked, no independent human review or sub-agents. New work is
Apache-2.0. Josie Elliston (with Claude Code / Claude Opus 5.5) identified
the equality and successor handoff. Aaron Wang (with opencode) supplied
the accepted mutants and reused post-emit test harness, retained under
`vendor/` with its README and license. PR2158's invoice audit and PR2273's
read-set analysis are complementary existing work, not repeated here.

The unchanged strict construction retains Jeremy Kothe's PR1087/PR870,
Hao Yan's PR858 controller/lift/independent check, Rohan Arun's PR1094
owner exchanges, Douglas Colkitt's maintainer composition and the complete
credited BIT/complex supplier lineage. Its archives and notices remain
unchanged.
