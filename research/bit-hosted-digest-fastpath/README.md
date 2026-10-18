# Exact faster hashing for the PR589 hosted audit

This opt-in adapter speeds up the **retained nine-stage PR589 hosted-owner
audit** by reusing JSON fragments within one digest invocation. It hashes all
7,843,392 emitted instructions in their original order, produces the same
SHA-256 and event count, and runs the unchanged ownership/window/profile checks
and all 16 inherited rejection controls. No frozen predecessor is edited.

The measured result is in [BENCHMARK.json](BENCHMARK.json). On Python 3.12.3 / macOS arm64:

| Same pinned fixture | Baseline | Adapter | Speedup |
|---|---:|---:|---:|
| Instruction digest | 17.417 s | 1.828 s | 9.53x |
| Complete hosted audit, including mutations | 25.836 s | 10.325 s | 2.50x |

These are one sequential baseline/adapter pair per measurement, with no timing
threshold or cross-machine guarantee. The profiler adds overhead and is not used
for the speedup ratios. This is verification tooling,
with no new supplier, physical admission, mathematical theorem or kappa claim.
The selected frontier and its cold-replay command are unchanged.

## Evidence and exact scope

The base is `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The fixture is
`research/community-hyperplane599-audit/pr589/bit589/v9/hosted`, with its retained
parent template, states, frames and audit receipt. [SOURCES.json](SOURCES.json)
pins every consumed external input by Git blob and SHA-256. The selected record
and task catalogue are historical provenance. This is a replay of that retained
hosted audit, not reconstruction of the word, native arithmetic replay, parent
audit, outer assembly or the entire selected cold replay.

An initial cProfile run measured 7,843,392 `json.dumps` calls consuming 21.455 of
32.421 seconds in the old digest. The adapter encodes each local instruction's
constant prefix/tail once per used orientation, and each call's owner descriptors
once per call. It then concatenates the mapped owner fragments and hashes every
resulting instruction. The full measurements, including the separately timed
complete audit and its mutations, are retained in BENCHMARK.json.

The byte identity follows directly from the specified compact JSON arrays:
serialize the opcode, destination owner, optional source owner, and the unchanged
instruction tail in the same order, with the same commas, brackets, escaping and
newline. Both paths use Python's default `json.dumps` options with separators
`(',', ':')`. The private-source threshold remains the first call's owner count,
exactly the original `2*V + R`; private owners still use the current template's
`live` value. No numeric values, ownership information or instruction fields are
normalized away.

The full expanded instruction stream is never retained. Buffers are bounded by
1 MiB plus one instruction, with tables for the local programs and one call's
owners. There is **no persistent cache**: every invocation rebuilds its fragments.
Changes to calls, owners, local instructions or live stock are immediately read.

`load_auditor()` checks both frozen Python source hashes, extracts only the five
literal hosted-auditor edits from eumemic's pinned `adapt9p.py`, and applies each
at exactly one anchor. It executes that parameterized auditor with only its
`digest` binding replaced. The inherited audit body and its mutations remain
unchanged. Assertion-disabled execution fails explicitly. The direct adapter
checks its code sources; the verifier additionally checks all nine fixture/code
inputs. Input changes require explicit repinning and re-verification; they are
not silently accepted as a new benchmark.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3 -B research/bit-hosted-digest-fastpath/verify.py
```

Expected: `PASS_EXACT_HOSTED_DIGEST_FASTPATH`, 7,843,392 events and digest
`96c7ad2e744e9a503a4ef5ecd52d0f6a8899bdb5efac2e3aafa0db18adf99523`.
The verifier times the baseline and adapted digest on the same loaded template,
then each complete hosted audit once. The two output receipts must be byte
identical and must equal the retained receipt as JSON. It also checks:

- 120 exact byte-stream comparisons over 40 deterministic fixtures at three
  chunk sizes, covering both orientations, private and ordinary sources, empty
  tails, large integers, floating values, escaping, Unicode and nested values;
- ten changed-input controls, each matching the baseline, changing the digest
  and leaving a subsequent original-input digest unchanged;
- rejection of a null source index, changed source bytes and disabled assertions;
- all 16 original ownership/window/profile mutation rejections, in both audits.

The optional `--output /tmp/hosted-digest-result.json` retains a fresh timing
receipt. The registered hook (600-second ceiling) adds provenance/metadata checks:

```sh
python3 scripts/research_package.py --package research/bit-hosted-digest-fastpath
```

For another compatible replay, the adapter has the inherited three-argument CLI:

```sh
python3 -B research/bit-hosted-digest-fastpath/fast_digest.py PARENT_DIR HOSTED_DIR OUT.json
```

`PARENT_DIR` must contain `nine/` and `records/`, as the original auditor expects.
The retained archive stores `records/` one level above `v9/`; the verifier restores
that layout in a temporary directory and never writes into archived evidence.
Other fixtures have not been benchmarked or claimed as verified by this package.

## Session selection and overlap

OS assignment seed **91**, verification engineering; the `replay-runtime` card
is refined to this single bottleneck. The prescribed baseline binding example
passed. Parallel isolated-test scheduling already exists; locale-sensitive
status reads were covered by PR1834. Neither was repeated. Initial overlap
inspection covered 527 open PR bodies, local notes/ledger and the 40 most recently
updated discussions plus recent handoff comments. The full discussion-cache
refresh failed; direct recent-discussion inspection succeeded. No novelty proof
is inferred from this bounded search. The active joint-dual containment-mask work
uses a different verifier and fixture; PR1736 checks PR589 hosting windows but
does not optimize instruction hashing. [Claim and final handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1871).

## Open next questions

A maintainer could integrate the adapter into one actively maintained replay
driver, preserving its pins and comparing its complete receipt once. That would
make the runtime benefit available without opting into this package. Driver
integration and its applicable cold-replay obligations are outside this change;
see the structured question in [TASK.json](TASK.json).

## Credit

The underlying hosted audit credits DaysSky (PR442), Chafik Boukhalfa / chafreaky
(PR444), and DreamingOfClouds (PR463/PR510). The P111 parameterizer and PR555
supplier are by eumemic; the PR589 word is by DreamingOfClouds. The retained
community-hyperplane599 archive supplies the complete benchmark fixture.
Predecessor source/license headers remain intact. This package claims only the
fragment-encoding optimization and its differential evidence.

Prepared by Matthieu Pascal (@mtpsl) with substantial OpenAI Codex assistance.
New work is Apache-2.0.
