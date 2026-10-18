# Parallel layer-end controls for the frontier1042 leaver chain (opt-in, byte-identical receipts)

**Status: tooling improvement (verification engineering). No new κ, and no check is changed or
weakened.** It extends merged PR1059, whose runner is pinned to the T37 variant only, to the
leaver variant that the frontier1042 chain runs five times.
Track 85–94 (verification engineering), assignment seed 89 (OS CSPRNG via Python `secrets`).
Base commit `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08` (selected κ = 0.001672660197076918,
frontier1094).

## What it speeds up

A cold `make frontier1094-verify` runs `scripts/verify_frontier1042.py` as its
`baseline1042-cold` stage, and so does `make frontier1042-verify`. The recorded frontier1042 run
took 1162 s, with the #799 baseline reused. Its `chain` stage (`reproduce_leaver_chain.py --id
k8`) took 711 s of that, and **530 s of the chain are its five layer-end-control steps**:

| Step | Word (payload) | Recorded seconds |
|---|---|---:|
| `lec-p6n` | p6n `25c40614…` | 139.8 |
| `lec-promo` | promoted `84d4da2e…` | 115.5 |
| `lec-jx` | jx `84d4da2e…`: the k8 X4 exchange is the identity, so this is the promoted word again | 116.3 |
| `lec-hyb` | hybrid `c836d892…` | 78.5 |
| `lec-frames` | final `db2c7cfb…` | 79.4 |

Each step runs `layer_end_controls_leaver.py` v2 (`4ba676f1…`), LeaverSAT's variant of the signed
per-end controls, through the pinned `run_portable.py` launcher (`322d29d4…`). The script audits
the unmutated word and 95 mutated words with PR635's `hpe_audit_and_transport.run` (`c9a05ff2…`).
Every mutant must be rejected for its pinned reason, and the not-applicable sites must equal the
declared ones. The 96 audits are independent pure computations.

The runner also accepts the T37-type variant `layers_p6n/layer_end_controls.py` (`fc58c569…`),
which is merged PR1059's target, and checks it against the archived T37 receipt. That variant
runs in the T37 replay's `u8-native` stage (77 s recorded). It also runs at least twice in a cold
frontier1042 run:
- in complex741's p6n stage (`complex-sw4-frame8/construction/layers_p6n/reproduce_p6n.py:66`);
- in #799's native stage (`gauge44-frames-x/construction/jx/reproduce_jx.py:79`).

Scripts are accepted **by digest**, so every byte-identical copy is covered: three copies of
`4ba676f1` and ten of `fc58c569` on main. This also covers the `4ba676f1` copies in open claims
PR1104 (head `d8982686`) and PR1107 (head `6123fc5d`), at `research/gauge44-ends7-t16`, as
checked at those heads.

These steps run on every cold `frontier1094-verify` or `frontier1042-verify`, and on every chain
rebuild, such as a batch's shared candidate replay. The recorded frontier1094 replay (58 s) reused
the completed frontier1042 baseline. Claims that reuse the k8 chain as ancestry do not rerun these
steps.

## How

`lec_parallel.py` is a drop-in for one step. It takes the same arguments and environment
(`PR635_CODE`, plus `LEC_REASON_PINS` for the leaver variant), runs under the chain's interpreter
settings, and prints the same output. It parallelizes the audits **without editing or
re-implementing the pinned launcher, script or audit**:

1. **Record.** The pinned launcher runs the pinned script once, with a stand-in
   `hpe_audit_and_transport` that only records the exact gzip bytes of each trial word. The first
   (unmutated) word gets success and every other word gets a placeholder rejection, so this pass
   decides nothing. Its receipt goes to a scratch directory and is discarded. As each word is
   recorded, the real audit of it starts in a worker process.
2. **Evaluate.** Every distinct word is audited in a worker by the real, digest-checked PR635
   `run`. The worker captures exactly the outcome `trial()` would see (success, or the
   `AssertionError` arguments) and the audit's printed output.
3. **Replay.** The pinned launcher runs the unchanged script again. Its stand-in prints the
   captured output and returns or raises the real outcome for the identical bytes. The script's
   own assertions accept or reject every control, check every pinned reason and the
   not-applicable sites, and write `COLD-END-CONTROLS.json`. The sequence of trial words must
   equal the recorded one, and a word the record pass never saw is an error.

**Outcome key.** Outcomes are keyed by three values:
- the sha256 of the exact trial bytes;
- the routing path exactly as `trial()` passes it to the audit, made absolute but not resolved
  (PR635's reader picks gzip or JSON from that path's suffix);
- the routing file's sha256.

If an audit worker process dies, the run fails rather than waiting for a lost task.

**`chain_lec.py`** runs the five steps as `lec()` does, sharing one worker pool and one outcome
table. Because `lec-jx` builds exactly `lec-promo`'s 96 trial words, it reuses those outcomes and
audits nothing. It also checks each step:
- **Before.** It binds the word's payload to the recipe pin that the chain asserts when it builds
  that word (`COLD-LAYERS-RECIPE-P6N`, `PROMO-RECIPE`, `RECIPE-X4`, `RECIPE-U8`,
  `FRAME-RECIPE-LV`).
- **After.** It applies `lec()`'s own checks against `CHAIN-PINS-k8.json`: the pins-file digest,
  PASS status, 95 rejected controls and the declared not-applicable sites.

## Benchmark (same machine, same inputs; descriptive only)

Machine: macOS 26.5.2 arm64, 10 cores, Python 3.14.8, `--jobs 10`, on a shared machine with load
average 5–12. [`BENCHMARK-macos-arm64.json`](BENCHMARK-macos-arm64.json) is the raw receipt written
by `verify.py --serial` with the committed code. The only change is that the repository root is
stripped from its paths. The measurement was taken at `ce7ad1b6`.

| Step | Recorded serial (maintainer) | Pinned serial | Parallel | of which record / audit wait / replay |
|---|---:|---:|---:|---|
| `lec-p6n` | 139.8 s | 54.6 s | 17.3 s | 9.8 / 0.8 / 6.6 s |
| `lec-promo` | 115.5 s | 69.9 s | 18.6 s | 10.0 / 0.9 / 7.7 s |
| `lec-jx` | 116.3 s | 66.6 s | 14.9 s | 8.2 / 0.0 / 6.7 s (0 audits: reused) |
| `lec-hyb` | 78.5 s | 59.1 s | 25.3 s | 14.5 / 0.9 / 9.9 s |
| `lec-frames` | 79.4 s | 64.1 s | 24.1 s | 14.6 / 1.5 / 8.0 s |
| **five steps** | **529.5 s** | **314.3 s** | **100.2 s (3.1×)** | |
| T37 `layer_end_controls.py` (secondary) | 77.0 s | 81.2 s | 26.2 s (3.1×) | |

Two earlier full runs of the same algorithm, before the review fixes to the routing key, the
ENTERING argument and worker loss, gave 266.7 → 97.1 s and 293.5 → 143.6 s for the five steps.
What remains is the pinned script's own mutant construction: deep copy, JSON and gzip of each
word. By design it runs twice, as the record and replay columns. The audits mostly overlap the
record pass, with a wait of 0.8–1.5 s per audited step. On a busy machine, the single-threaded
record and replay passes compete with the workers.

## Evidence of equivalence

`verify.py` (no flags) checks the following:

- **Archived maintainer receipts.** All five `COLD-END-CONTROLS.json` from the parallel run must
  equal the receipts in the selected replay archive (`selected-replay.tar.gz`, `22c3f4dc…`, every
  member digest pinned) **byte for byte**. One field is rewritten first: `word`, the input path
  that the pinned script records. It goes from `/private/tmp/batch1047-selected/chain/…` to this
  run's directory, and the archived receipt must contain that path exactly once.
- **T37 variant.** It gets the same check against the T37 replay archive (`t37-replay.tar.gz`,
  `48285025…`), on its barch word bound to PR870's `RECIPE-U8` pin.
- **Controls** on the final word, through the same runner. No control may leave a receipt.
  - C1: a corrupted unmutated word (one gate coefficient doubled) fails at the pinned script's
    own first assertion, `unmutated cold-end word must pass`.
  - C2: a forged acceptance of one mutant's outcome makes the pinned script fail with
    `cold-end mutation accepted`. This shows that real outcomes decide, not the record pass.
  - C3: a forged rejection with an unrelated message makes it fail with `rejected for the wrong
    reason`. This shows that the pinned reasons are still checked.
  - C4: a one-byte change to the pinned script, or to PR635's audit, is refused before any work.

`verify.py --serial` (the benchmark) additionally checks the **pinned serial reference**. All six
receipts must be byte-identical to those of the pinned launcher and script, run serially on the
same paths with one process per step as the chain runs them. The step logs must be identical
except for the audit's own wall-clock `"seconds"` value.

`test_package.py` checks the following:
- the placeholder semantics and the pins;
- the recipe pin set, including that the k8 X4 pin equals the promoted pin (the word bindings
  themselves are checked by `chain_lec.py` under `verify.py`);
- that `run_pinned` restores `sys.argv`, `sys.path`, the stand-in module, `sys.stdout`,
  `Path.write_text` and `gzip.compress`;
- that the launcher's portable gzip header reaches the trial words;
- that the routing key keeps a symlink's own suffix;
- that a killed worker fails the wait;
- that the real audit accepts the final word and rejects a corruption.

## Using it

```sh
python3 -B research/frontier1042-lec-parallel/verify.py --work NEW_DIR            # ~3 min
python3 -B -m unittest discover -s research/frontier1042-lec-parallel -p test_package.py
python3 -B research/frontier1042-lec-parallel/verify.py --work NEW_DIR --serial   # + pinned serial (~9 min)
python3 -B research/frontier1042-lec-parallel/chain_lec.py --chain WORK/chain --out NEW_DIR
python3 -B research/frontier1042-lec-parallel/lec_parallel.py WORD ROUTING OUT [ENTERING] [--script PINNED_SCRIPT]
```

The `chain_lec.py` command runs the five steps on a completed `reproduce_leaver_chain.py`
output. The `lec_parallel.py` command runs one step as a drop-in, with the environment set as for
that step.

The expected last line of `verify.py` is `PASS_FRONTIER1042_LEC_PARALLEL`. Everything needs only
standard-library Python 3.11+, no network and no inputs outside the repository. No Makefile
targets are added: `research/community-batch1099-audit` pins the Makefile by exact digest, so any
append would fail `scripts/verify_pr_reconciliation.py`.

**Not wired.** `reproduce_leaver_chain.py` and `verify_frontier1042.py` are unchanged and still
run the serial steps. They are manifest-pinned, so wiring is the maintainers' call. There are two
ways to wire it:
- Run `chain_lec.py` once after the frames step. That keeps the shared table, so `lec-jx` is
  reused.
- Replace each `lec()` command with `lec_parallel.py WORD ROUTING OUT`, run without the launcher
  prefix, because the runner executes the pinned launcher itself. Each step then starts its own
  pool and table, so `lec-jx` is audited again. The benchmark above uses the shared table.

The selected verifier's three `phases` steps (cells, chain and slots stages; 469 s recorded) call
the same pinned `phases_full.py` and `clifford_exact.py` as the merged PR1041 runner, so that
runner takes them unchanged. This package does not re-measure them.

## Relation to other work

- **PR1059** (ours, merged) applies the same record/evaluate/replay design to the T37 variant
  only. Its runner hardcodes that digest, and its verify, pins and receipts are bound to T37. This
  separate package leaves PR1059's pinned files untouched. Compared with it, this package:
  - accepts both variants by digest;
  - runs the five leaver steps of the frontier1042 chain;
  - adds execution through the pinned launcher;
  - captures the audit output, so step logs match;
  - shares one outcome table across steps;
  - adds recipe bindings, the `CHAIN-PINS` checks and the forged-outcome controls C2 and C3.
- **PR1137** (Wronskode, open, head `e3b8fa39`) targets the same five steps differently. It
  provides a faster exact re-implementation of PR635's audit, cross-checked against the pinned
  one, and reports 2.53× in a single process. This package runs the pinned audit **unchanged**
  and uses more cores instead. The two compose partly:
  - Here the audits mostly overlap the record pass, with 0.8–2.2 s of wait per audited step across
    the recorded runs.
  - A faster audit would remove that wait and reduce CPU contention with the record and replay
    passes.
  - It would not shorten the floor, which is the pinned script's own mutant construction. That
    construction runs twice and takes about 7–27 s per step here.
- **PR1041** (ours, merged) covers `phases`. PR853 (navinor, merged) and PR1101 (rcfc-jreed, open)
  run independent stages of the #741 replay concurrently. This package parallelizes inside a step
  and composes with all of them.

## Scope

This package accelerates individual steps. It discharges no mathematical obligation, the selected
κ is untouched, and the timings are local measurements. A non-`AssertionError` failure of an
audit makes the replay fail with a `RuntimeError`, where the serial script would fail with the
original exception. Both are failures.

## Credit

- LeaverSAT: the leaver variant `layer_end_controls_leaver.py`, with per-word reason re-pins.
  Q6Reviewer signed v2 and `LEC-REASON-PINS-k8.json`.
- LecReviewer: `LEC-REASON-PINS-STACK-k8.json`.
- DreamingOfClouds: `layers_p6n/layer_end_controls.py`, LayerReviewer's signed adaptation of
  PR635's `cold_end_controls.py`. Also PR484's `audit_gk.py`.
- icekylinx (with GPT-6 Astra assistance): PR635's `hpe_audit_and_transport.py`, adapted from
  PR425/433, PR484 and Round19's transport. Also the gauge44 package.
- LeaverSAT and LeaverSAT2: the k8 leaver cells and recipes.
- ColdWitness: `reproduce_leaver_chain.py`.
- Jeremy Kothe, Rohan Arun and Hao Yan: the frontier1042 composition.
- Jeremy Kothe and NewBArch: the PR869/PR870 barch word.
- Jonathan Capalbo: the PR942 replay.
- Douglas Colkitt, with OpenAI Codex assistance: maintainer orchestration and the replay
  archives.
- Prior concurrency tooling: PR853 and PR921 (navinor), PR1101 (rcfc-jreed), PR1041 and PR1059.
- Wronskode: PR1137, a concurrent fast-audit approach to the same steps.
- Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic)
  via Claude Code. Candidate selection used parallel read-only scouting and judging subagents, and
  two adversarial review subagents checked the package. New material is Apache-2.0.
