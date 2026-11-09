## Summary

The retained scalar executor is described using Python row dispatch and
three-bit coded ports. Its prior proof states qualitative finite-control
expansion. This package supplies an explicit finite microstate generator
on the same fixed tapes and seven-symbol alphabet, with exact source
success/rejection behavior and a numerical serialized TM-clock bound.

**No new kappa, full caller, recursive Controller lowering or tariff
conversion is claimed.**

## Exact result and scope

For a fixed, nonempty, closed N-row six-opcode table and P>=1 distinct fixed
ports, the generated transition program has at most 48N+3P+4 states.
Decoder values, branch targets and port identities are finite control;
the target performs no runtime source-row lookup or host integer work.
One dispatch no-op per source row and one transition per raw tape action
give exactly **C=A+U**, where A includes successful origin scans and U
includes terminating halt/reject rows. Positive finite precompilation F,
including source labels and any 7^P full transition expansion, is charged
separately: total F+A+U.

The lowering preserves the first blank probe and repeated first-bit read,
partial malformed-code rejection heads, unused111 rejection after all
three rewind moves, left-origin restoration before rejection, frontier
blank materialization and all success-origin returns. Rejection performs
no success cleanup. Looping tables have finite-prefix equivalence; no
universal termination claim is made.

This is the no-readonly-context `execute_table` interface only. Controller
recursion, wrappers/retirement, source/header installation and even unused
readonly contexts remain separate. Fixed labels are terminal observables,
not uncharged printed strings. The simulator's host storage is not the
target machine. Initial head sites and historical visited regions remain
charged; no host allocator-capacity equality is inferred.

## Sources and novelty

Canonical base: [CrocSwap `7c49fe32`](https://github.com/CrocSwap/integer-mult-bounds/commit/7c49fe32c55de02c2c873655c804b16e4c3fef0a).
Source machine: [CubeJerry's compiled owned-bank lifecycle](https://github.com/CubeJerry/integer-mult-bounds/tree/ab239cb6ee884e7a900dd9101c34448077fad0b0/research/compiled-owned-bank-lifecycle),
including the [exact executor](https://github.com/CubeJerry/integer-mult-bounds/blob/ab239cb6ee884e7a900dd9101c34448077fad0b0/research/compiled-owned-bank-lifecycle/machine.py),
blob `acf475e4fccaff2fb64bd5b0b3f3fc0d246dc592`.
Small numeric examples retain [the rounded scalar tables](https://github.com/CubeJerry/integer-mult-bounds/tree/6476455a1cf7cd29d6a2a81c3b6f02fd3a3bbf57/research/current-rounded-scalar-tables)
and [the exact scalar Builder](https://github.com/CubeJerry/integer-mult-bounds/tree/13193a22b1070a74a8580c5d3ea27470443f815a/research/current-scalar-flat-tables).
The machine convention comes from [canonical 02-streams.tex](https://github.com/CrocSwap/integer-mult-bounds/blob/7c49fe32c55de02c2c873655c804b16e4c3fef0a/upstream/build/sections/02-streams.tex).

Six source/reference files are authenticated by exact commit/path/blob/
SHA256. The classical finite-control simulation principle and prior
qualitative expansion are credited. New artifacts are the actual finite
graph generator/sample, precise source failure semantics, closed grammar,
state/setup/backing statement and exact chosen clock. C=A+U does not
identify these clock units with the ordinary-work invoice's tariff rho.

## Reproduction and verification

```bash
python3 -I -B research/scalar-table-microcontrol/verify.py
python3 -I -O -B research/scalar-table-microcontrol/verify.py
```

Expected `PASS_SCALAR_TABLE_MICROCONTROL`. Standard library only;
runtime verification needs no Git/network/solver.

The author checks 107 exact traces/endpoints/clocks: 17 primitive cases and
90 small rounded-SCALE cases, with 79 successes and 11 range rejections.
Eleven static grammar controls reject; omitted initial-probe and omitted
left-restoration graph mutants are detected. A bounded self-goto prefix
tests the nontermination qualification.

Separate operational review checks 2,827 admitted generated executions,
30,375 microsteps and 12 negative controls against an independent oracle.
Separate model review checks 253 graphs, 1,226,848 explicit transition
instances and 17 negative controls with its own graph/transition checker.
Both normal/optimized replays agree. Unchanged scripts, receipts, full
review notes and the lead's source/proof review are included; portable
commands are in REVIEW.md and the registered manifest.

## Remaining obligations and credit

The actual source/header/readonly-context and Controller interfaces,
complete owned/history costs, common-volume tariff conversion and whole
supplier remain open. All global foundational assumptions and the selected
certificate are unchanged. No accepted-bound improvement is inferred.

Prepared for **@CubeJerry** with substantial **OpenAI assistance**.
Credit the originating lifecycle, exact/rounded scalar and canonical
stream-model authors. The two complementary reviewers and lead used shared
pinned source; this is separate model-assisted review, not human or
proof-kernel acceptance.
