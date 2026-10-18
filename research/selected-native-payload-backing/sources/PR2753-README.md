# A completed recursive caller for the selected BIT construction

This package removes the `64 <= n < 128` restriction from the executable caller in [Jose Manuel's PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697). An internal child now runs the same complete selected caller over its whole packet and returns to its suspended parent. Its unused row stock, frozen field directory, generated coefficient program and ordered spectators are passed explicitly. The caller terminates at the existing below-64 leaves.

This closes a central implementation gap: the earlier executable only handled widths for which every child was already a leaf. The earlier recursive closure note supplied a mathematical recurrence with a completed callee premise; this package supplies that callee in the logical stream implementation and accounts for its nested storage. It also repairs an inherited sign operation whose per-column cost would otherwise grow with atom precision.

**The multiplication exponent does not change.** The selected conditional value remains κ = 0.001672660197076918. The executable establishes the baseline `p=1` time recurrence under the stated source and root-coupling hypotheses. Its routing and leaf swaps still cost `O(wV)`; it does not establish the stronger selected H2 contracts, a compiler to a fixed number of physical tapes, or the outer multiplication transfer. It is a substantive step on the actual caller, not a new exponent certificate.

## What is new

- A decreasing-width dispatcher with explicit ENTER / INVOKE / RETURN boundaries, one complete child invocation across all current high-prefix ordinals, and an iterative scheduler that avoids a Python recursion-depth restriction.
- Exact child geometry across the original head/gap/tail layout, including same-bank children, odd half-resets and remainder peeling at widths above the previous range.
- Separate child stock `U` and spectator `B`. Their product is never used as a substitute for available fresh rows. Each child gets separate numerical arenas and its own serialized source-bound program.
- A sign implementation with linear complete-fibre traffic. In particular, the fixed two-slice retreat does not copy a padded residue counter once per atom.
- A full logical live-symbol ledger for payload, keys, directories, numerical banks, continuations and suspended parents. Under the explicit canonical root-coupling hypotheses in [PROOF.md](PROOF.md), the bound is `< 11 V_root + F_q`, where `F_q` is fixed-q source compilation storage. This is not a Python heap bound or a completed physical tape-space theorem.

The stock is the compatible selected stock

```
K = lcm(28416,28425) |GL64(Fq)| q^(4096(w-1))
  = 269241600 |GL64(Fq)| q^(4096(w-1)).
D(n) = 0 if n < 64, otherwise 1 + D(42 floor(n/64)).
root rows = t K^D(n), t >= 1.
```

A child receives exactly `V/(28416 |GL64(Fq)|)` payload symbols. Thus retaining suspended parent states produces a geometric storage sum. The proof derives a sufficient row-capacity exponent `k <= 8195 w log2(e)` and retains the divisibility and outer-padding obligation; merely supplying `q^k` rows does not satisfy the executable contract.

## Scope and source boundary

The base is canonical main `7b39515117fe26e75d16c268877391f1bdaa5640`, priority revision 5. The selected result and its scientific inputs remain unchanged. [TASK.json](TASK.json) records the current-main and overlap checkpoints, the explicit user-directed scope refinement and next questions.

A matching [recursive-boundary claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18957230) by jmbarrancoml appeared at 19:47 UTC, after this task started at 19:19:46 and checked overlap. This is an independent construction and joined logical-reserve argument; exclusive novelty is not claimed. Nick Petalas concurrently completed [PR2743](https://github.com/CrocSwap/integer-mult-bounds/pull/2743), the sharper first-range payload/key result. Our coarse payload allowance is not a claim to that result, and the finer first-range count-storage result [PR2749](https://github.com/CrocSwap/integer-mult-bounds/pull/2749), published during validation, remains separate.

The runtime import graph actually uses the byte-for-byte [PR2697 export](predecessor/) at `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`; [PREDECESSOR.json](PREDECESSOR.json) authenticates all 50 files before executable imports. Candidate modules at this package root override only the changed components. No pending source is treated as admitted to the selected frontier. [SOURCES.json](SOURCES.json) pins every external live input, including the inherited profile/stock proofs. [EVIDENCE.json](EVIDENCE.json) authenticates the four retained component-proof/notice files before execution; their separate attribution is preserved.

The constructor accepts internal widths `n >= 64`; below-64 cases are completed trace leaves, not new root `SelectedNode` entry points. The compatible all-size stock and canonical program/directory form are input hypotheses. The local divisibility guard alone does not certify adequate stock for an arbitrary entire tree.

## Evidence and reproduction

Use CPython 3.12, standard library only, from the repository root:

```sh
python3.12 scripts/research_package.py --package research/selected-bit-recursive-caller
```

[VERIFY.json](VERIFY.json) declares the bounded commands. A particular suite can be replayed directly:

```sh
python3.12 -B research/selected-bit-recursive-caller/verify.py --suite recursion
```

The suites have deliberately different claims:

| Suite | Evidence |
| --- | --- |
| `source` | Full selected provider catalogue and 7,843,392 literal caller events; generated coefficients, global schedule, complete gapped endpoint, and two distinct sampled high fields. |
| `node` | Complete four-family GL2 Boolean-column model including MOVE, COPY, IDLE, bridge, exchange, exact source preservation and scratch cleanup. |
| `recursion` | Independent ordered-layout oracle; actual `peel.run` above the old range; selected descriptor/frame handoffs `256 -> 168 -> 84` with controlled tiny payload consumers; 1,501 scheduler frames; malformed-return, failed-construction and exception cleanup controls. |
| `nested` | Complete two-level physical execution on a separate dimension-2, q=2 toy with all six GL2 low classes. It uses a coordinate-projector root and full conjugated GL2 children, with actual node/driver/trace/layout and stream operations and test-only source/coefficient fixtures. It is not execution of the enormous selected GL64 payload. |
| `controls` | Sign endpoints and counter-cost regression, stale gather/scatter witnesses, bridge/exchange directions, invalid stock, omitted/changed source pins, and exact receipt mutations. |

No finite model proves all widths. The parametric argument is in [PROOF.md](PROOF.md); the tests independently challenge its geometry, chronology, source binding and cleanup boundaries. The selected-frame check is explicitly a controlled callee fixture, and the q=2 toy is outside the selected odd-prime admission domain.

Verification is read-only and compares complete typed receipts in [RESULT.json](RESULT.json), including their canonical SHA256 digests. Explicit generation uses `--emit-to NEW_FILE` and refuses to overwrite a file. Assertions are required for independent test code; direct optimized runs are rejected. [VALIDATION.md](VALIDATION.md) records the actual environment, commands and outcomes.

## Open next questions

1. **Can this logical caller be compiled to the required fixed tape inventory with the same charges?** The next concrete step is a serialized frame-bank/continuation layout with cursor movement, template cleanup and reuse charged on every return. The full live-content ledger is available; the existing Python tape objects are not that compiler.
2. **Can routing and ordinary leaf swaps satisfy the selected H2 primitive contracts?** Start with the actual `routes.py` and `bitstream.py` paths reached by this caller, preserving complete-prefix order and source ownership. Replacing only the recursive callback cannot remove their `O(wV)` charge. This is the immediate time bottleneck between the baseline recurrence and the stronger selected H2 saving. The baseline can already feed the inherited conditional ordinary-caller bootstrap, once its physical and outer-wrapper premises are supplied.
3. **Can the compatible reserve be supplied by the outer borrowing wrapper?** Implement the stated compatible-row padding and restoration, preserving the `U` coordinate and full metadata ledger. The capacity inequality alone does not establish the wrapper, and the complex supplier and analytic transfer remain separate obligations.

## Attribution

David Arias, with substantial OpenAI Codex assistance, including mathematical, implementation and independent-checking subagents. This is not independent human review or a proof-assistant verification. New work is under Apache-2.0.

Jose Manuel (`jmbarrancoml`) supplied the executable first-range caller and its selected source chain. The complete retained [NOTICE](predecessor/NOTICE.md) credits the selected word, hosting, full-ring normal forms, coefficient grammar and packet contracts. We additionally credit starship-s's PR2731 residual storage, NickPetalas's PR2708 route/key storage and ywz65's PR2688 directory bound. Those component results are not claimed here as new. The earlier mathematical recursive closure and compatible-stock construction remain explicit proof dependencies.
