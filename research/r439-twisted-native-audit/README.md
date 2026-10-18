# Native replay of the two twisted-star R439 words

**PR1868's two absorbed words pass the previously unrun native 5/9/11-stage
checks.** This closes that finite replay handoff. The twisted contract, circuits
and three-ADD savings belong to Sagar Thakrar's
[PR1868](https://github.com/CrocSwap/integer-mult-bounds/pull/1868), pinned at
`6b222d01fee072bcd3a680e6a96ae7d22e13bcac`. No new circuit, supplier admission or
kappa is claimed.

The inherited native programs check **F2 scalar columns** and **chronological
frame/COPY legality** separately. They do not execute physical address-transform
operators on the helpers' values. Passing them therefore does not prove the
helper climb-additivity premise or a general non-literal cleanup theorem.

## Exact scope and result

Base is main `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; the selected record remains
PR1094, with the PR589 bit supplier. The prescribed PR1062 first example and
selected-source baseline check passed at entry. Card `bit-helper-contract` is
refined to the native obligation explicitly left open by PR1868. Its active
symbolic-contract audit is complementary; see [TASK.json](TASK.json) and
[discussion 1886](https://github.com/CrocSwap/integer-mult-bounds/discussions/1886).

The new Python code independently rebuilds the three documented changes:
remove the trailing D restorations `506 ^= 374`, `507 ^= 355`, `514 ^= 367`,
then replace the single sources of A[288], A[290], A[304] by 69, 72, 360.
The complete decoded words, including unchanged B, C and metadata, must equal
the pinned PR1868 payloads. No PR1868 producer or verifier is imported.

Each candidate and its exact parent is exported, staged, and checked by freshly
compiled, unchanged native programs. A separately written Python event derivation
must match the complete exported record bytes. It also checks all 661 local
dirty-input columns in both directions, COPY/ERASE closure, and integer positive
envelopes. [RESULT.json](RESULT.json) retains all native receipt fields except
elapsed time and the temporary input pathname.

| Local word | ADDs | Forward bound F | Reverse bound B | Local / nine-stage bits |
| --- | ---: | ---: | ---: | ---: |
| PR1062 parent | 11,500 | 25,717 | 5,911,840 | 95 / 182 |
| PR1868 absorbed PR1062 | 11,497 | 25,717 | 5,858,638 | 95 / 182 |
| PR1188 parent | 10,492 | 13,667 | 3,758,418 | 91 / 175 |
| PR1868 absorbed PR1188 | 10,489 | 13,667 | 3,748,680 | 91 / 175 |

The strict inequalities are checked as integers:
`64 F^3 B^2 < 2^104` and `2^18 F^5 B^4 < 2^192`.
The latter specializes the pinned inherited `global_k.py` formula to K=4 and
18 bridge layers; its source expression is checked without executing the
hosted emitter. Reported bit lengths do not replace the strict checks.

Every word has 2,911 MOVE records, nine rank-seven COPY/ERASE pairs, rank mass
5,129 and profile `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`. Ordered frame
paths for every register and copy windows equal the respective parent's.

| Native schedule, per word | Formal columns | Scalar ADD bill | Bridge ADDs | Fresh copies | Reverse-stage copies |
| --- | ---: | ---: | ---: | ---: | ---: |
| 5 stages | 883 | 5 × local ADDs | 666 | 45 | 18 |
| 9 stages | 1,327 | 9 × local ADDs | 1,998 | 81 | 36 |
| 11 stages | 1,549 | 11 × local ADDs | 2,664 | 99 | 45 |

All four words pass all three schedules, including the 439 arbitrary helper
inputs and final temporary closure. Native legality separately establishes
nested frame moves, common-frame ADDs and immutable COPY-source lifetimes in
the unhosted local stream. Its source-owner/selection inputs are empty; this
is not a global physical owner assignment or bank admission.
Its inherited `nondegeneracy_checked_by_separate_exact_bank_audit` receipt flag
is a fixed annotation: this package does not run that separate audit.

## Failure controls and evidence limits

The twelve native runs retain **192 inherited omitted-bridge controls**. These
are the checker's reduced bank-matrix controls (6/18/24 per schedule), not 192
reruns of mutated physical streams.

There are **18 additional controls**, nine for each candidate:

- Deleting all three restorations without editing A passes with clean helpers
  but corrupts 102 outputs on arbitrary helper inputs. All three native stage
  binaries reject that stream at the local defining-decoder boundary.
- Undoing each individual A compensation is rejected by the five-stage binary.
- A wrong common frame preserves the scalar endpoint but is rejected by native
  legality. An undercharged COPY rank is also rejected there.
- A passing receipt with one formal column removed is rejected by the harness.

Five package test groups additionally reject 168 native receipt corruptions,
six candidate changes and source/hash/JSON corruption. A minimal relocated
worktree resolves the same pins, and altered parent/candidate bytes stop the
actual entry point before compilation. These tests complement the native
programs; they are not an independently authored replacement for those programs.

This package does not reprove the twisted equations, their necessity, or the
single-edge census. It does not run the original H1–H5 owner checker; PR1868's
four recorded syntactic failures remain. Physical/common-frame realization,
all-size compiler, native address/projector action, hosted emission/invoice,
precision/tape recovery, outer assembly and analytic transfer are unrun or
inherited. No full selected-frontier cold replay or proof-assistant check was
performed. The positive envelopes price only the named local/prefix guards,
not an eleven-stage or hosted-supplier precision invoice.

## Reproduce

Use Python 3.12 and the retained bit-supplier build environment: a C++17 compiler
and real Boost headers. No third-party Python packages or network access are
required. On Ubuntu, `g++` and `libboost-dev` supply the native dependencies.
Set `CXX` and `BOOST_INCLUDE` for nonstandard installations. Missing dependencies
fail the replay; no native check is silently skipped.

```sh
python3 scripts/research_package.py --package research/r439-twisted-native-audit --check-only
python3.12 scripts/research_package.py --package research/r439-twisted-native-audit
```

The registered command uses `-I -O -B`; all new checks remain active under
optimization, while the inherited exporters run in isolated child interpreters
with assertions enabled. Native processes have individual 90-second timeouts
and the complete registered replay has a 300-second bound.

For durable raw logs, command arguments, binaries, generated records and complete
native receipts, use a **new** directory:

```sh
python3.12 -I -B research/r439-twisted-native-audit/verify.py --output /tmp/twisted-native-replay
```

Expected final line:

```text
PASS_R439_TWISTED_NATIVE_AUDIT words=4 absorbed=2 stages=5/9/11 columns=883/1327/1549 bridge_controls=192 added_controls=18 no_new_kappa
```

`--write` explicitly regenerates RESULT.json after a complete replay. Immutable
compressed predecessor inputs have exact byte pins; reconstruction compares
their full decoded JSON. [SOURCES.json](SOURCES.json) pins nine live main inputs
and historical catalogue/selection provenance; [PREDECESSOR.json](PREDECESSOR.json)
pins the four retained PR1868 files. Full Git history is needed for historical
provenance. Local validation details are in [VALIDATION.json](VALIDATION.json);
hosted CI is a separate observation.

## Open next questions

Can one exact absorbed word pass the complete hosted-supplier invoice under an
accepted twisted interface? The first step is to bind its candidate and native
receipt to the hosted emitter and independent ownership/invoice audit. That
would connect this finite replay to an actual supplier. Maintainer acceptance
of the helper climb/cleanup contract and a full hosted run remain the blockers.
This package does not settle those decisions. The question is also structured
in TASK.json.

## Credit

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. One agent, no
independent human review. Apache-2.0. Sagar Thakrar owns PR1868's mechanism and
savings; Gareth Davidson/PR1188 and Thakrar/PR1062 supply the parents. The native
programs and exporter are reused unchanged with their original notices.
[NOTICE.md](NOTICE.md) records the circuit, interface and checker lineage.
