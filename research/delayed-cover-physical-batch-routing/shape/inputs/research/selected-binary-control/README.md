# Binary control at a selected BIT head-ADD site

We implement the complete numerical callback at the first-column head-ADD
site of [PR2405](https://github.com/CrocSwap/integer-mult-bounds/pull/2405).
Raw high fields, matrix entries, generated weights, descriptor indices and
offsets stay in binary words through execution. We then consume the encoded
coefficient in a complete ADD and its inverse with binary loop counters.

For a fixed selected request vocabulary and odd prime q, the callback computes

```text
M = q^w
P = (g sigma B0) E_r (g sigma B0)^-1
t = (-P_i0 / P_00) A_(if+j) / A_j * x mod M.
```

We prove the word-operation invariants, generated-expression refinement,
owned-scratch erasure and uniform local charge in [PROOF.md](PROOF.md).
Under the retained root coupling, the callback fits the conservative
`A_q w^1800` preparation allowance. The complete ADD costs `C_q V`, where
V counts its payload bits. The constants may depend on the fixed prime and
selected catalogue. We retain the selected frontier unchanged.

## Execution boundary

We compile rational source constants and finite low-class/source labels
before runtime, independently of input width and high digits. Runtime uses
single-symbol tape access, unit head moves and fixed register roles. It
includes modular multiplication and inversion, 64-dimensional preparation,
the full 128-dimensional fallback table, generated Good/Pair/unit weights,
binary division/reversal of indices and the final offset multiplication.

Only labels from fixed finite sets enter native control. The checker blocks
runtime word inspection and checks forbidden decoding calls in the five
runtime modules. The host-integer code in `oracle.py` supplies fixtures and
expected values outside execution. A source scan is a regression guard;
reviewers should also inspect the runtime call graph.

We implement a finite-alphabet word machine with written all-length
arguments. We have not emitted a full transition table or checked this
implementation in Lean. The full selected residual, recursive child
boundary and family/owner/global XOR/COPY/ERASE caller remain open.

## Evidence and reproduction

We bind the replay to the actual COPY510 request and a nonidentity owner
MOVE request in the selected main source. We compare their complete raw
fixtures with pinned predecessor literals, then compare binary preparation
against direct raw-projector arithmetic outside the runtime.

The replay covers 20,480 projector entries and 277 preparation-table entries,
including dense high fields and moduli 9, 27 and 25. Nine callback cases
exercise varying coefficients, both Pair orientations, two reset forms and
a root extent of `2^600`. In the tail-Pair test, the requested values change
across the reversal boundary. Reset tests preserve global field slots and
skip dead numerical preparation.

We also check 1,858 operand pairs for modular add/subtract/multiply, 106
inverse/nonunit cases, 1,984 divisions, 256 carry/borrow pairs and 129 complete
countdowns. At the complete 15,552-bit ADD site, we check each output bit's
source coordinate, apply the inverse and audit erased scratch. Fourteen
controls test source/rank/range faults, root/modulus validity, reset-slot
compaction, spectator padding, forbidden decoding and scratch leaks.

Run from the repository root with Python 3.12 and no third-party packages:

```sh
python3.12 scripts/research_package.py --package research/selected-binary-control --check-only
python3.12 scripts/research_package.py --package research/selected-binary-control
```

The registered replay runs normal and optimized Python modes, each with a
600-second limit. `RESULT.json` contains a compact receipt and SHA256 of the
canonical complete result, including operation counts. To inspect that full
result, run:

```sh
python3.12 -I -B research/selected-binary-control/verify.py --emit
```

We developed and checked this package on macOS arm64 with CPython 3.12.13.
Finite cases support the written proof; they do not exhaust all widths or
the selected global trace. We have not run a selected cold replay, a new
Lean build or an independent human review for this contribution.

## Files for review

| File | Review target |
| --- | --- |
| `words.py` | Binary arithmetic, bounded register ownership and erasure |
| `matrices.py` | Full selected projector and Good/Pair preparation |
| `records.py`, `controller.py` | Encoded programs, stacks, indices and offset |
| `stream.py` | Binary counters and complete ADD/inverse payload path |
| `sources.py`, `oracle.py` | Fixed compilation and separate expected arithmetic |
| `check_words.py`, `check_callback.py`, `controls.py` | Exact checks and rejection controls |

## Open next questions

1. Can the selected caller preserve the physical field contract through a
   complete residual and its recursive child? Begin with the two source-bound
   requests here and connect every adapter coefficient and inverse. The
   missing complete caller still blocks selected global execution.
2. Can a formal compiler connect these word routines to an explicit finite
   machine? Begin with the word arithmetic and ownership invariant, then
   the typed stacks. A formal operational model and checked composition
   remain necessary for that stronger claim.

We record structured first steps and blockers in [TASK.json](TASK.json).
[NOTICE.md](NOTICE.md) retains predecessor and concurrent credit;
[SOURCES.json](SOURCES.json) pins the inputs and pending dependencies.
Jose Manuel (`jmbarrancoml`) prepared this work with substantial OpenAI Codex
assistance. We coordinated the scope in
[Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18944524).
