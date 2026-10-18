# All-prefix register invariants for the PR628 word model

**Scoped Lean formalization with bounded source binding; no new kappa.**
This proves the four source/target invariants used by the local phase identities
in [PR1294](https://github.com/CrocSwap/integer-mult-bounds/pull/1294), at the level
of a raw-address word model of PR628's reserved-depth dispatcher. The proof
covers every finite binary factor tree, every completed-leaf prefix, both call
signs, and the shared deeper scratch. The connection to the actual Python
dispatcher has the explicit finite coverage below; Python semantics and an
all-size compiler-correctness theorem remain outside the formal proof.

## Formal statement

Let distinct source/target addresses `x,y` lie below the first scratch address
`d`. A node uses `d` for its connector and gives both children the same deeper
pool starting at `d+1`. Its positive word is `L+ R+ L- R-`; its negative word
is `R+ L+ R- L-`. For every emitted leaf, Lean proves

```
src = x or d <= src       dst = y or d <= dst
src,dst < d + height(tree).
```

Leaves act on a single mutable state `Nat -> V` by adding a value depending
only on their source to their destination. Coordinate preservation follows
without a linearity assumption. Target-translation equivariance additionally
assumes commuting additions. Axis preservation additionally assumes an additive
zero and zero-preserving leaf maps. These premises hold for ideal linear
shears; the proof does not derive them for the numerical leaf implementation.

For left/right child prefixes `P,Q`, let `R,S` be genuine right inverses of
those prefixes. [four_phase_invariants](Dispatcher.lean) proves

```
P(axis_y(v)) = axis_y(v)     Q(axis_y(v)) = axis_y(v)
(R(state))_x = state_x      (S(state))_x = state_x.
```

For linear maps, these are exactly `P e_y = Q e_y = e_y` and
`e_x^T R = e_x^T S = e_x^T`. The inverse identities are explicit hypotheses;
sign reversal is not silently assumed to supply them. The proof includes a
general lemma that coordinate preservation passes to a genuine right inverse.
No factors commute in these statements, and the register value type may itself
be an array or vector of any dimension. The proof uses Lean 4.28.0 core/Std,
with only `propext` and `Quot.sound` in the seven audited statements. There are
no proof placeholders, custom axioms, or native evaluation oracles.

## Source correspondence and evidence

Base: `ef5f39403610d231a0c27e8a6b4f08c10209bcd6`. The consumed dispatcher is
Chafik Boukhalfa's PR628 at `0768f97d06c623b8211e651543c66135796b62bf`, retained
unchanged under `research/dirty-prefix-precision/vendor/pr628/dirty.py`.
[SOURCES.json](SOURCES.json) pins the exact Git blobs and SHA256 values. The
selected record and task catalogue are historical provenance; live code/proof/
notice inputs are separately declared in [VERIFY.json](VERIFY.json).

The independent checker extracts only the authenticated `compose` function,
retains its input guards, and records calls to a completed-leaf stub. It checks
the recursive AST, including factor slicing, scratch slicing, both schedules
and recursive argument forwarding. The model's `d` is a scratch **address**;
Python's argument named `d` is the traversal **orientation** and is separately
checked in both directions. Neither numerical leaves nor predecessor checkers
are imported.

- 66 distinct signed traces at factor counts 1 through 32 and the seed-selected
  count 75; 132 source executions including both orientations; 36,846 leaf
  events across the distinct traces.
- 147,384 exact scalar-matrix row/column obligations at all nonempty prefixes
  of both child embeddings, with inverse matrices maintained by right-column
  updates. Nonlinear dirty-state cases separately check source preservation
  and target-translation equivariance at every prefix. These finite cases
  corroborate the universal proof.
- 18 fresh Lean theorems directly equate the literal Python traces to `emit`
  at counts 1 through 8 and 75, both signs. All are proved by `rfl` with no
  axiom dependencies. The source-to-model bridge is bounded, not a theorem
  about executing arbitrary Python programs.
- 19 controls cover wrong ports, parent-scratch reuse, reversed-word mistakes,
  a wrong factor partition, actual source/target aliases, insufficient scratch,
  omitted semantic premises, forbidden proof axioms, three broken Lean models,
  and a false source-trace equality. Six package tests additionally exercise
  actual source/receipt/proof-source corruption, read-only relocation,
  deterministic regeneration, overwrite refusal and missing theorem audits.

[EXPECTED.json](EXPECTED.json) records deterministic Python evidence;
[FORMAL.json](FORMAL.json) records the separately executed kernel checks.
[VALIDATION.json](VALIDATION.json) records local commands, environment and limits.
Finite traces do not prove the all-tree theorem, and the all-tree theorem does
not certify the Python interpreter or the rounded leaves. The explicit AST
check, kernel trace equalities and source pins delimit that remaining bridge.

## Reproduce

With Python 3.12+ and installed official Lean 4.28.0, from the repository root:

```sh
python3 -I -O -B research/dirty-dispatcher-invariants-seed75/verify.py
```

Expected:
`PASS_DISPATCHER_INVARIANTS formal=7 kernel_traces=18 python_traces=66 controls=19 kappa=unchanged`.
Use `--lean /absolute/path/to/lean` when not using elan. The verifier compiles
fresh temporary objects, checks the compiler version/commit and theorem axiom
inventories, and compares both receipts. `--write` and `--formal-write` create
new receipts and refuse to overwrite existing files. Default replay writes
nothing into the package. [The scoped workflow](../../.github/workflows/dirty-dispatcher-invariants-seed75.yml)
pins the official Linux toolchain archive by SHA256.

```sh
python3 -I -O -B research/dirty-dispatcher-invariants-seed75/test_package.py
python3.12 scripts/research_package.py --package research/dirty-dispatcher-invariants-seed75
```

The generic registered replay runs Python evidence and six package tests only;
its output explicitly says `Lean=NOT_RUN`. The full command above or the
dedicated workflow is required for the formalization claim. Hosted CI status
is separate from local execution.

## Boundaries and predecessor credit

The existing Gareth Davidson / @bitplane
[nonlinear-commutator formalization](../lean-nonlinear-commutator/README.md)
proves completed-call restoration and ordered-product semantics. This package
adds raw-address **prefix** semantics and the four phase invariants identified
by Philipp / @mightyOil in PR1294; it does not claim priority for the underlying
mathematical facts. Charles Bethin's
[PR1278](https://github.com/CrocSwap/integer-mult-bounds/pull/1278) supplies the
squarefree interval induction and phase formulas. Its factor-support induction
and PR1294's 18 free-algebra equalities are not re-proved here.

The completed-leaf source-only contract, fixed nonaliased phase/coefficient
inputs, actual inverse implementation, rounding/precision estimates, physical
register realization, hosting/tape/compiler interfaces, and multiplication
reduction remain separate obligations. No selected supplier cold replay,
numerical speedup, precision reduction or stronger exponent is claimed. The
selected conditional PR1094 value remains `0.001672660197076918` at this base.

## Open next questions

Formalize PR1278's squarefree factor-support induction over this raw-address
word model. It is needed to connect these invariants to the commuting interval
bound. A feasible first step is a typed free-polynomial semantics with a
two-child disjoint-support lemma; that formal semantics and its interval
normal-form theorem are still missing. An all-size source-to-model compiler
proof would separately strengthen the present bounded Python connection.
[TASK.json](TASK.json) records the scope, seed, local claim, alternatives,
overlap coverage and structured follow-up.

## Attribution

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in scope selection, proofs, code, tests and writing. Credit Chafik Boukhalfa
(PR628/905), Charles Bethin (PR1278), Philipp / mightyOil (PR1294), Gareth Davidson
(existing formalization and PR877), 0xkilgore (PR663), and the retained upstream
contributors. New work is Apache-2.0; existing sources and notices are unchanged.
This is machine-checked scoped mathematics, not independent human review.
