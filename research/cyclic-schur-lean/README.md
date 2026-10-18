# Exact cyclic Schur elimination in Lean

This package proves the exact chain and closure reduction used by Rohan
Guliani's PR846 and Ali Romman's PR985. The proof applies to every length
`n` and stride `w` with `0 < w ≤ n`. It uses Lean 4.21.0 and its core/Std
libraries. It needs no Mathlib package or external proof dependency.

The result is a formal proof of one exact elimination step and its two
sequential passes. It does not change the selected construction or kappa.

## Statement

Let the scalar type be any `Lean.Grind.Semiring`. Coefficients need not
commute. Let `x_i` and `b_i` be arbitrary data and coefficients. The parent
system is

```text
y_i = x_i + b_i y_((i+n-w) mod n),      0 ≤ i < n.
```

Pass A computes the following entries in increasing index order:

```text
z_i  = x_i,                          i < w
pi_i = b_i,                          i < w
z_i  = x_i + b_i z_(i-w),             i ≥ w
pi_i = b_i pi_(i-w),                  i ≥ w.
```

Set `e(k) = n-w+k`, `c_k = z_e(k)`, and `a_k = pi_e(k)`. Lean proves that
the exact closure system is

```text
Y_k = c_k + a_k Y_((k+n) mod w),      0 ≤ k < w.
```

Its stride is `(w - n mod w) mod w`, the natural-number form of
`(-n) mod w`. The theorem `child_predecessor` proves the equality of the
two index maps. It includes the case in which the child stride is zero.

The reconstruction formula is

```text
y_i = z_i + pi_i Y_(i mod w).
```

`scalar_schur_iff` proves both directions: a parent solution restricts to
a child solution and has this reconstruction formula; a reconstruction
from a child solution satisfies every parent equation. The separate
theorems `scalar_reconstruct` and `scalar_reconstruct_tail` prove the
parent equations and exact return of every child entry.

`scalar_exists_iff` proves that a parent solution exists if and only if a
child solution exists. `solutions_eq_iff_tails` proves that two parent
solutions agree if and only if their tails agree. These statements do not
assume invertibility, unique solutions, a norm bound, or a division rule.
They therefore also cover singular systems. Only entries in the active
index ranges are compared; functions outside those ranges are irrelevant.

## Connection to the source loops

`scanPass` is an explicit left-to-right array-update evaluator. Step `i`
writes entry `i`. It reads the seed if `i < w`; otherwise it reads entry
`i-w` from the current array. The initial array can have arbitrary values.

`scanPass_prefix` proves that every written entry is the recursive chain
value. `scanPass_suffix` proves that every unwritten entry is unchanged.
`passA_correct` specializes this evaluator to the pair update for `z` and
`pi`. `passA_tail_correct` gives the exact data sent to the child.
`passC_correct` specializes it to the seeded scalar update.
`passC_solves_parent` proves that this executed Pass C solves the parent
when its seed solves the child system.

The source map below uses immutable Git commits. `SOURCES.json` also gives
SHA-256 and Git blob identifiers for the inspected files.

| Source operation | Lean definition or theorem |
| --- | --- |
| [PR846 Pass A](https://github.com/CrocSwap/integer-mult-bounds/blob/4bdb3e755ea7118170a7a34764df955880dec282/research/cyclic-inverse-stride-bridge/stride.py#L99) with `bits=None` | `pairStep`, `passA`, `passA_correct` |
| [PR846 tail and child call](https://github.com/CrocSwap/integer-mult-bounds/blob/4bdb3e755ea7118170a7a34764df955880dec282/research/cyclic-inverse-stride-bridge/stride.py#L115) | `endpoint`, `childData`, `childCoefficient`, `child_predecessor` |
| [PR846 Pass C](https://github.com/CrocSwap/integer-mult-bounds/blob/4bdb3e755ea7118170a7a34764df955880dec282/research/cyclic-inverse-stride-bridge/stride.py#L119) | `passC`, `passC_correct`, `passC_solves_parent` |
| [PR985 source reuse identity](https://github.com/CrocSwap/integer-mult-bounds/blob/9df42a99dd8497b6e7d46cd2507bb89071372640/research/dirty-stride-source-reuse/PROOF.md#L85) | `chain_affine`, `scalar_schur_iff`, `scalar_reconstruct` |
| [PR985 closure views](https://github.com/CrocSwap/integer-mult-bounds/blob/9df42a99dd8497b6e7d46cd2507bb89071372640/research/dirty-stride-source-reuse/dirty_stride.py#L226) | `endpoint n w k = n-w+k`, `childStride` |

This is a proof of the displayed recurrence and the indexed array
evaluator. It is not a formal semantics for Python, the two-stack FIFO,
or the two-tape block-swap interpreter. The source correspondence above is
an explicit code review, not a compiler-correctness theorem.

For PR985, the theorem supplies the exact Schur identity. It does not prove
that the freshly prepared child powers equal the exact chain products.
The return-time formula and the rounding comparison remain separate.

## Reproduce

From the repository root, use an official Lean 4.21.0 compiler:

```sh
sh research/cyclic-schur-lean/verify.sh /path/to/lean-4.21.0/bin/lean
```

The script checks version `4.21.0` and compiler commit
`6741444a63eec253a7eae7a83f1beb3de015023d`. It builds all three modules
in a new temporary directory, with one Lean worker. It discards inherited
Lean search paths and removes only its own temporary build on exit.
It downloads nothing and does not write a package cache.

The output lists the axiom dependencies of every theorem in the package
namespace, including generated equation lemmas. It ends with:

```text
PASS_CYCLIC_SCHUR: 102 theorems; standard axioms only
PASS_AUDIT_GUARDS: incomplete proof and package axiom rejected
```

The count includes compiler-generated helper theorems. The mathematical
result is the parametric proof above, not that count. `AXIOMS.txt` records
the checked dependency report. All dependencies are drawn from `propext`,
`Quot.sound`, and `Classical.choice`. The central scalar Schur theorem
uses only `propext` and `Quot.sound`. No theorem uses `sorryAx`, a custom
axiom, or a native evaluation oracle.

The script also compiles two separate invalid proof probes. The axiom
guard must reject an incomplete proof through `sorryAx` and reject a
declared package axiom. The script checks the exact rejection reason, so
an unrelated compilation error cannot make these controls pass. Those
invalid probes are temporary test inputs, not proof dependencies.

`Counterexamples.lean` supplies four kernel-checked mathematical controls:
the wrong child-stride sign, an early tail start, an omitted chain-start
coefficient, and a stale predecessor read. An explicit eight-entry parent
solution and its three-entry closure fix the first three examples. These
examples support review; they are not the proof of the all-length result.

## Scope and credit

The tested base is `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
Only this new package changes. `upstream/`, the Python solvers, precision
claims, phase contracts, and the selected certificates stay unchanged.

Rohan Guliani's PR846 supplies the chain/closure algorithm. Ali Romman's
PR985 uses its exact identity inside the dirty source-reuse construction.
Chafik Boukhalfa's PR628 and Charles Bethin's PR764 supply predecessor
cyclic-inverse and scan analysis. This package does not claim a new Schur
algorithm or literature priority.

Gareth Davidson's PR896 proves the generic nonlinear dirty commutator. It
does not prove this indexed elimination identity. No PR896 proof source
is imported here. The two results have separate contracts.

This package leaves rounding, norm and precision estimates, original-cycle
return times, reversal and normalization of arbitrary input strides,
recursive solver termination, FIFO correctness, dirty restoration, tape
costs, physical compilation, and the multiplication theorem open. It does
not assert that a numerical child solve returns a solution; it proves what
follows when the exact child equations hold.

Prepared for Ali Romman (@aliromman), with substantial OpenAI Codex
assistance. Apache-2.0. No independent human review or hosted CI success is
claimed. `VALIDATION.md` gives the local checks and their limits.

## Follow-up review

The [2026-10-14 follow-up](FOLLOWUP-REVIEW.md) records the response to the
maintainer triage, the fresh checks and the remaining proof boundaries.
