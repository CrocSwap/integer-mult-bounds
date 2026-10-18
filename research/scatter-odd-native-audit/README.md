# Odd scatter multiplicity at the actual native boundary

**Finite boundary audit; no new kappa or supplier adoption.** This closes
[PR3004's](../scatter-parity-contract-audit/README.md) third open question for
one explicit full-size word. Tripling an **existing** scatter entry passes the
unchanged symbolic checker and both actual native checkers. It produces all
three selected exporter artifacts byte for byte. Both entry modes of
[PR2992's simple-support guard](../simple-scatter-boundary/README.md) reject it,
as their deliberately stronger contract requires.

Adding three copies of an **absent** entry instead preserves agreement between
symbolic and exported actions but changes the required endpoint. The full
symbolic checker and native column checker both reject that word. An agreeing
odd row alone therefore does not establish a valid defining decoder.

The claim is in [discussion #2976](https://github.com/CrocSwap/integer-mult-bounds/discussions/2976),
following the handoff linked from [#1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18978364).
This separately written harness imports no predecessor audit implementation;
it executes the original checker, exporter, guard and native programs as pinned
audit subjects. Results are finite, author-checked evidence without independent
human or proof-kernel review.

## Four fixed fixtures

Keep every field of the selected PR589 word unchanged except appending entries
to row 0, initially `[4,5,6,7,8]`. The nine retained helper addresses remain
distinct. In particular, absent slot 0 names dirty helper 472.

| Append to row 0 | Occurrences / emitted scatter ADDs | Symbolic endpoint | Exported endpoint / native columns | Both guard modes |
|---|---:|---|---|---|
| nothing | 527 / 527 | pass | pass | accept |
| `[0,0]` | 529 / 528 | pass | reject | reject |
| `[4,4]` | 529 / 527 | pass | pass | reject |
| `[0,0,0]` | 530 / 528 | reject | reject | reject |

All four pass the actual native legality checker, including frame chronology,
COPY/ERASE lifecycle and its rank-mass bill of **5129**. The positive stream has
**27,234 records**, **24,305 total ADDs**, nine rank-seven COPYs and nine ERASEs.
The bad absent-slot streams have one additional ADD and record, without changing
the paid rank mass. Legality success does not certify the defining endpoint.

The baseline and existing-slot triple agree byte for byte on `249-records.bin`,
`249-states.json` and `frames.json`, and on every deterministic field of both
native receipts. The native column checker verifies **883 physical columns**
through five stages, including dirty state and six inherited omitted-bridge
controls. Its unchanged payload-prefix bound is `9528119495320518471870892800`
(93 bits). These fields describe this native test, not a new precision theorem.

The paired-absent and triple-absent words also produce identical artifacts.
Their exported output differs from the required map only at target register
111, with a 98-column discrepancy recorded in [RESULT.json](RESULT.json).
Input column **472** is a one-bit witness. Native columns refuse both at
`local defining-decoder full formal column`, exit 2, without a success receipt.
The triple-absent symbolic refusal is `REJECT targets not y + x: [0]`.

## Why the two odd fixtures differ

For one retained slot with multiplicity `m`, symbolic scatter contributes
`m mod 2` copies of its value, while export emits one ADD exactly when `m>0`.
That observation and the odd-positive criterion are predecessor results.
[PR3128's retained-alias audit](../retained-alias-parity-audit/README.md) explains
why an unqualified semantic necessity statement also needs independent slots.

For a simple row already containing `k`, appending `[k,k]` changes its
multiplicity from one to three. The two new symbolic XORs cancel, and exporter
membership is unchanged. The exporter derives frames, state metadata and other
records from unchanged fields, so all three output artifacts coincide.
For an absent slot, appending three occurrences changes both coefficients from
zero to one. Their agreement says nothing about equality to the original map.
The literal selected instance and its dirty-helper witness are checked here.

The existing-slot triple retains the baseline's native bill: 529 textual
occurrences do not imply 529 emitted scatter ADDs. This supports PR3004's request
for an authoritative count if a future schema admits multiplicity. The current
simple-support schema remains sufficient; rejecting this fixture is intentional,
not a guard defect.

## Reproduce

From the repository root, Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/scatter-odd-native-audit
```

The registered check runs all four real symbolic/export/guard sequences, a
separate complete 661-column F2 record/JSON comparison and seven behavioral test
groups. It does not compile native code. Expected primary line:

```text
PASS_SCATTER_ODD_BOUNDARY fixtures=4 columns=661 guarded_duplicates_rejected=3
```

The explicit native replay also needs a C++17 GCC/Clang compiler with `__int128`;
`CXX` may name its executable:

```sh
python3 -I -O -B research/scatter-odd-native-audit/verify.py --native
```

Expected additional line:

```text
PASS_SCATTER_ODD_NATIVE legality_accepts=4 columns_accept=2 columns_reject=2 controls=2
```

Compilation is serial. The harness snapshots authenticated inputs in a temporary
directory, compiles unchanged `legality_h.cpp` and `columns_h.cpp` with
`HDIM=8, NCOPY=9, VPORTS=111, RHELP=439`, and stages each actual exporter output
using original `stage_cohort.py`. It uses Sagar Thakrar's pinned
[checked 128-bit cpp_int stand-in](../bit589-checked-cpp-int-seed92/README.md),
whose selected include is checked by a compilation probe. This is not a fresh
system-Boost build or a repetition of the stand-in's arithmetic audit.

[NATIVE.json](NATIVE.json) retains full legality and column receipts. Only the
temporary stream pathname and elapsed times are normalized after checking their
form. Default replay compares receipts and writes no repository files.
`--write-receipts NEW_DIRECTORY` reconstructs evidence into an unoccupied
directory and refuses to replace evidence. Direct replay needs no Git when
the package and all declared inputs are present.

Native controls reject an omitted scatter ADD and a truncated stream. Behavioral
tests check every live source pin against byte corruption, COPY/ERASE misuse,
all 64 assignments of a separate six-register scalar fixture, and preservation
of occupied outputs on all three rejected words. Two separate wrapper mutants
bypass only `check` or only `export` validation; actual CLI acceptance tests
detect both. Explicit checks remain active under `-O`; inherited Python
delegates run isolated with their checks enabled.

## Source scope and credit

Base main: `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[TASK.json](TASK.json) records the refined `supplier-boundary-audit` task and stop
rule; [SOURCES.json](SOURCES.json) binds Git blobs and SHA-256 inputs, including
the selected source manifest.

- Nick Petalas, **PR2977** `cd23d242dfe0e7a71cafba0ad5590dc4f2fbf4f2`:
  discovery, paired-scatter counterexample, dirty witness, candidate guard and
  earlier native baseline/paired/single-absent controls.
- Arham Tahir, **PR2992** `b31bf0360ad702b1be71dea7a33edc11711084af`:
  versioned simple-support wrapper and both enforced entry modes.
- Kumagi, **PR3004** `ce08d19f6e43bbc6f552858d93154efe3aa98916`:
  scalar contract audit, count distinction and native odd-row handoff.
- James Reed (jwr404), **PR3099** `80b7b0b452de3c9fa4306f49d12e904a40cfbe2e`:
  [duplicate-boundary corroboration](../scatter-duplicate-boundary/README.md).
  Sricharan Vagvala (theon199), **PR3128** `2bf13e5b55f8318ae74a8f17db36a19447ba8c7f`:
  [retained-alias independence audit](../retained-alias-parity-audit/README.md).
- eumemic and DreamingOfClouds: selected PR543/PR555/PR589 word/checker lineage;
  Dylan Crow: exporter/native checkers; Sagar Thakrar: checked arithmetic
  stand-in; Douglas Colkitt: selected bindings and review. Original source
  notices and Apache-2.0 licenses remain unchanged.

Added scope: the missing native existing-slot triple, its absent-slot contrast,
actual guard acceptance table, exact artifact/receipt comparisons and separate
replay harness. The old mismatch and odd-multiplicity criterion are credited.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0. No independent human review is claimed.

## Open next questions

A separately versioned successor needs an explicit schema and accounting
decision: keep simple supports, or admit multiplicity while binding the actual
emitted ADD count and retained-slot semantics. Review this four-fixture table
together with PR3128's alias premise before repinning such a successor. This is
a supplier-admission decision, not a reason for another local search.

Frozen selected sources and the frontier remain unchanged. The audit does not
rebuild the generator/tuner, prove all odd-multiplicity words valid, run full
selected cold ancestry, verify whole-call hosting or physical projector/bank
realization, prove all-size/compiler/precision/tape or analytic transfer, or
claim hosted CI. Those obligations remain separate from the tested native
legality and scalar column boundaries.
