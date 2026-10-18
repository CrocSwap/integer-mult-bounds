# Exact statement and source-interface follow-up

This review addresses the [PR #1026 triage request](https://github.com/CrocSwap/integer-mult-bounds/pull/1026#issuecomment-6161280106).
The complete Lean source, its four mathematical controls and the axiom guard
were reviewed. A fresh build passed on 2026-10-14. No proof correction was
needed. This is a formalization of the exact reduction, with no new kappa.

## Pins and fresh build

Reviewed head: `c4be063c0afb634db7aa02bc1876ff29640bec65`.
Refreshed main: `418e40eb2572d930b58c1cf9b82b41c0fc7ee08d`.
Original base and source subjects remain those in `SOURCES.json`; no pin was
changed to follow a moving PR head.

```sh
sh research/cyclic-schur-lean/verify.sh /path/to/lean-4.21.0/bin/lean
```

This command exited 0 with the official compiler commit
`6741444a63eec253a7eae7a83f1beb3de015023d`. It used one Lean worker and a
fresh temporary build. The theorem report matched `AXIOMS.txt` byte for byte.
The final lines were:

```text
PASS_CYCLIC_SCHUR: 102 theorems; standard axioms only
PASS_AUDIT_GUARDS: incomplete proof and package axiom rejected
```

The complete build-log SHA-256 was
`47f3cb9bb50be35e0881d9361b2e2cc5f3c4cc78353b5d3529138dc474ace624`.
No toolchain installation, dependency upgrade or shared cache change was
needed. No root-wide or selected-supplier replay was run.

## What the checked statement covers

| Obligation | Checked statement | Boundary |
| --- | --- | --- |
| Parent index | `predecessor_mod` | Requires `w <= n` and an active index. |
| Closure tail and stride | `endpoint_mod`, `child_predecessor` | Uses `n-w+k` and `(-n) mod w`, including zero child stride. |
| Ordered coefficient products | `chain_affine` | Multiplication order is preserved over `Lean.Grind.Semiring`; commutativity and inverses are not assumed. |
| Actual model reads | `scanPass_prefix`, `scanPass_suffix` | A written entry uses the current predecessor; unwritten entries retain arbitrary initial values. |
| Two scalar passes | `passA_tail_correct`, `passC_solves_parent` | The exact child equations are a premise of reconstruction, not a proved numerical solver guarantee. |
| Solution correspondence | `scalar_schur_iff`, `scalar_exists_iff`, `solutions_eq_iff_tails` | Covers singular systems and equality on active indices. It does not assert unique solvability. |

The proof is parametric. The four fixed examples detect index/coefficient
errors; they are not the basis for its all-length claim. The audit checks all
package theorems, including generated lemmas. It accepts only `propext`,
`Quot.sound` and `Classical.choice`; the two invalid-proof probes fail for
the specified axiom violations.

## Source correspondence and remaining obligations

All four source files in `SOURCES.json` were recovered from their pinned Git
objects and their SHA-256 digests were checked. The [PR #846](https://github.com/CrocSwap/integer-mult-bounds/pull/846) files are still
byte-identical at its refreshed head. Its `bits=None` Pass A, tail slice and
Pass C correspond to the operations and indices above.

[PR #985](https://github.com/CrocSwap/integer-mult-bounds/pull/985) now has head `da1cdf8ed4ac9b1b8378dfec73f77ff4e81a4f70`.
Its proof is unchanged from the pinned `9df42a99dd8497b6e7d46cd2507bb89071372640`.
Its solver file has two changes: each input-validation loop binds one
`data[i]` read to `value` before its grid comparison. The chain, child stride
and closure implementation are unchanged. The historical source pin is
therefore retained, with this later source comparison stated separately.

This comparison is a code review, not a formal Python translation theorem.
The Lean proof does not establish FIFO or block-swap routing, fresh-power
return times, rounded coefficient accuracy, dirty restoration, recursive
termination, physical cost or the multiplication theorem. Those remain the
separate [PR #846](https://github.com/CrocSwap/integer-mult-bounds/pull/846) / [PR #985](https://github.com/CrocSwap/integer-mult-bounds/pull/985) family review. The exact algebraic result can be
assessed on its stated scope without treating those interfaces as proved.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
This is an author-side follow-up, not independent human review or a merge
approval.
