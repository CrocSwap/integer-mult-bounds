# Faster exact Clifford comparisons in the current R2 audit

**Verification tooling; no new kappa or supplier admission.** The new
comparator accelerates the exact equality stage of PR3202's complete retained
two-provider native-slice audit by **29.97x** over its original packed kernel
and **20.61x** over the existing table-cached kernel. The entire audit improves
by **1.28x / 1.20x**, respectively; its other checks are unchanged.

The insight is to use a complete algebraic description instead of constructing
every matrix column. For these Clifford operators, signed action on the 18
Pauli generators determines the operator up to a scalar. One whole exact
anchor column fixes that scalar, including global phase. This criterion is
already used by the native producer and is not a new theorem here. The
contribution is a separate exact implementation, its source-bound integration
into the current independent audit, and measured coverage-preserving gains.

## Same-input measurements

Three samples per engine, each in a fresh serial Python 3.12.14 process,
alternating order on the same shared Linux host:

| Engine | Equality-stage median | Complete audit median |
|---|---:|---:|
| Original PR1781 packed kernel | 9.774 s | 39.744 s |
| PR2638 cached-table packed kernel | 6.721 s | 37.467 s |
| Signed Pauli action + exact anchor | **0.326 s** | **31.100 s** |

All nine runs reproduce the **entire predecessor result** and the same
multiset of **253 circuit-pair decisions: 244 acceptances and 9 rejections**.
Every source binding, both orientations, scalar restoration control, wrapper
chronology check and all sixteen semantic mutants per provider remain enabled.
The source audit's existing full-circuit deduplication is unchanged.

[BENCHMARK.json](BENCHMARK.json) retains every sample, process-level timing,
source and engine hashes, complete-result digest and circuit/decision digest.
OS caches were not flushed; there is no timing threshold in CI. The whole-audit
measurements include authentication and isolated snapshot setup. They exclude
native artifact generation, full supplier replay and integer multiplication.
The 30x number describes the equality stage, not the complete audit.

## What remains exact

[engine.py](engine.py) validates the complete gate words, propagates signed
Pauli images and evaluates `U|0>` with sparse Gaussian integers over powers
of two. It uses no floating-point tolerance, random probes or projective
phase normalization. The [proof](PROOF.md) derives each gate rule and the
complete comparison criterion. The API supports one through nine axes;
the actual caller uses nine, hence a 512-dimensional input space.

[controls.py](controls.py) checks the new representation against the original
packed matrix engine on 96 deterministic circuits in dimensions one through
four. It verifies all 480 signed generator images through 4,704 full matrix
column relations, every anchor, and 480 comparison decisions. Two explicit
controls show that Pauli action alone misses global phase and the zero-input
column alone misses a nontrivial character. Invalid gates and singular matrices
are rejected; mutating a cached operand changes the comparison result. These
controls also run under optimized Python.

Only immutable gate tables are cached, at most 64 entries. No new result or
state-vector cache is introduced. A small differential corpus is evidence for
the implementation; the written Clifford argument supplies all-input coverage.
It is not a proof-kernel verification or an independent human review.

## Reproduce and use

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/clifford-pauli-anchor
```

Expected markers are `PASS_CLIFFORD_PAULI_ANCHOR`, `PASS_ANCHOR_EXPORT` and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`. The registered
checks also run a complete optimized replay from a Git-free export in a path
with spaces, and reject changes to a live kernel, retained recipe and verifier.

Direct opt-in replay of the complete unchanged R2 audit:

```sh
python3 -I -B research/clifford-pauli-anchor/replay.py --mode anchor
```

Use `--mode packed` or `--mode cached` for the two reference engines.
An optional `--output FRESH.json` saves the full companion receipt.
Normal commands do not regenerate or modify any source artifact.

To repeat the same-input benchmark (about six minutes on this host):

```sh
python3.12 -I -B research/clifford-pauli-anchor/benchmark.py \
  --rounds 3 --output /tmp/anchor-benchmark-fresh.json
```

For another caller, the drop-in function is `engine.same_operator(a,b,n=9)`.
Before adoption, pin its gate grammar and replay its complete existing
controls. The frozen/default project engines are unchanged.

## Source and scope boundary

Base: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
Pending dependency PR3202:
`259043321323717b7e816d6be38ad5e1f0b69b4c`. Twelve necessary files from that
package are retained verbatim under `vendor/pr3202/`, including its README.
Their original paths, commit, Git blob IDs and SHA256 digests are recorded in
`SOURCES.json`'s `vendored_files` and checked before execution. The generic
runner checks the main-history pins; it does not require the pending PR's
Git objects to exist in a fresh checkout. Direct replay needs no Git/network.

All thirteen live input paths are declared for CI invalidation. `replay.py`
captures and authenticates those plus the twelve retained files before any
predecessor code executes. It installs exactly one comparator hook in a
private copy of the verifier; source/event reconstruction and all its failure
predicates stay unchanged. The complete result and snapshot immutability are
checked afterward. Changes to captured scientific inputs or predecessor
executable sources require an explicit pin update and revalidation; hashes are not a security
boundary against changing both evidence and its pins.

The companion receipt distinguishes the executed comparator from the
historical kernel hash inside the retained result. Its inherited 512-column
fields denote the covered operator domain, not 512 individually simulated
columns in the new engine. The comparison covers every complex input under
the validated gate grammar.

This does not extend PR3202's scientific scope. Full cleanup, other native
operations, physical ownership, precision/tape, the all-size compiler and
supplier/outer admission are not established here. Concurrent PR3208
(`87d63a82defff1ffeea173743106fb97903cbbd6`) supplies a separate R2 cleanup
audit; it is not included in these measurements or certified by this package.
PR3209 optimizes JSON parsing in a different T16 caller. Both are complementary
work. The selected certificate and frozen predecessors are unchanged.

## Open next questions and credit

The [structured handoff](TASK.json) suggests testing a larger native cone
against its existing fastest engine, and profiling the R2 audit's remaining
source/event and mutant-copy costs. No larger-caller speedup is claimed here.
[Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19002067).

Credit Sagar Thakrar/#1781 for the independent packed oracle and conventions;
ywz65/#2638 and Charles Bethin/#662 for the cached baseline and table recurrences;
24kHandsome1201/#3202 for the current audit; the original native producer for
the complete tableau/column criterion; and Nick Petalas, Jeremy Kothe,
Marius-Paul Dumitrean, Hiroki Kumazaki and the retained construction lineage.
[NOTICE.md](NOTICE.md) and the retained README give the fuller attribution.

New work is by Tekalign (@tekuuu), with substantial OpenAI Codex assistance
in algebra, implementation, measurement, checking and writing. Apache-2.0.
