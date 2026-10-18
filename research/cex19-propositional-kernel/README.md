# Kernel-checked propositional core of the 19-line decoder certificate

`Certificate.lean` proves that **2,675 specific clauses of PR2206's lower-bound
CNF cannot all hold**, using 602 explicitly written propositional derivations.
Lean 4.34.1 checks the complete proof with only `propext`, `Classical.choice`
and `Quot.sound`. The file uses ordinary `Or.elim`, contradiction and previously
proved clauses. There is no SAT solver, native-evaluation axiom, trusted RUP
checker, `sorry` or additional axiom in this formal proof.

The exact theorem is

```lean
Cex19Core.core_unsat (v : Nat → Prop) : ¬ Cex19Core.Satisfies v
```

`Satisfies` is a proposition structure with one field for each retained original
clause. A positive DIMACS literal `n` is `v n`; a negative literal is `¬v n`.
Each clause is their disjunction, ending in `False`. Original clause IDs remain
in field names `c123`, and derived clause IDs remain in theorem names `s10000`.
The theorem is closed: it asserts that no valuation can supply every field.

This reduces the trust boundary of Nick Petalas's exact-cost certificate in
[PR2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206). Its minimum
raw pairing cost **21** and its witness remain credited to that predecessor.
**The rational rank-to-CNF encoding argument is not formalized here.** Neither
the cost-21 witness nor a full decoder-rank theorem is claimed as a new Lean
result. No general rank-three bound, physical supplier or new kappa is claimed.

## Source and proof correspondence

The exact predecessor head is `b0990688174b6f2c6b13410c30974237364eddcd`.
Its unchanged encoder, configuration, RUP proof, receipt, README and notice
are retained under `source/`, with Git blob and SHA256 pins in `SOURCES.json`.
All pins are checked **before** executing the encoder's authenticated bytes;
cached Python bytecode is not imported. This encoder is a comparison subject,
not an independently implemented rank encoding.

The full formula has 2,856 variables and 9,964 clauses. Its canonical DIMACS
SHA256 remains `7c89c203e5cc4552f1090b4b8cd54ed617bd9bc91cd3ba39591c389c861c1fe1`.
The external replay regenerates that exact formula and compares every byte to
`lower.cnf`. Every addition in `trace.json` is bound to the corresponding one
of the predecessor's 1,301 RUP additions. The trace supplies explicit antecedent
IDs; a separate simple assignment checker confirms that each antecedent is
unit or contradictory at the point used, ending in contradiction for every
addition. Future, satisfied, nonunit and missing-conflict hints are refused.

Backward dependency closure from the final empty clause selects 2,675 original
clauses and 602 additions, using 25,711 antecedents. The complete original-ID
list is in `RESULT.json`. There is no claim that this is a smallest core.
The untrusted generator emits a direct proof of each selected addition by
assuming its literals false and eliminating each antecedent's disjunction.
The last addition is `False`, yielding `core_unsat`.

`kernel.py` deterministically regenerates the entire Lean file and compares its
UTF-8 text exactly. The external correspondence between these propositions and
the original DIMACS clauses remains a Python check. Once emitted, the Lean file
is self-contained and its logical validity does not depend on that generator,
the predecessor encoder, the RUP interpreter or a recorded success message.
The distinction matters: a valid proof of the wrong formula would not settle
the predecessor problem, which is why the external bindings remain explicit.

## Reproduce

Python 3.12 standard library, from the repository root:

```sh
python3.12 -I -O -B research/cex19-propositional-kernel/verify.py
python3.12 scripts/research_package.py --package research/cex19-propositional-kernel
python3.12 -I -B research/cex19-propositional-kernel/check_lean.py --lean /path/to/lean-4.34.1/bin/lean
```

The first two commands authenticate and bind inputs, check every trace step,
regenerate the exact Lean source and reject four altered certificate controls.
**The registered Python hook does not run Lean.** The third command performs
fresh full kernel compilation, audits the theorem's axioms, compiles a positive
43-clause projection, and rejects two alterations to that actual small proof:
a used source clause replaced by `True`, and a missing referenced derivation.
An invented-axiom report is also rejected. The small controls test the proof
pipeline; they are not substitutes for the full 602-derivation compilation.

These commands were run locally with CPython 3.12.14 and Lean 4.34.1. Windows
may require `TEMP` and `TMP` pointed at a writable workspace. Compilation has
a 600-second limit. No performance improvement is claimed. Normal replay does
not rewrite evidence. `test_boundary.py` additionally checks source corruption
before executable import, wrong/missing receipts, changed formal source, and a
Git-free export whose files remain unchanged.

The original 19-line configuration has 114 free pairing bits. The predecessor's
written Schur/rank-factorization argument explains why every cost-at-most-20
pairing would satisfy the full CNF. This package checks the propositional core
and its external source binding, not that algebraic implication, the upper
witness, source-to-Lean correspondence inside the kernel, or physical admission.
No selected-supplier cold replay, independent human review or hosted-CI pass is
claimed. Selected records and frozen packages remain unchanged.

## Open next questions

Can the three fixed pivot-block reductions and the residual rank-factorization
budget be formalized against these exact clauses? Start with the implication
from a cost-at-most-20 fitting matrix to an assignment satisfying the full CNF.
That would connect this propositional theorem to the mathematical lower bound.
The predecessor's separate question of a short reusable structural inequality
also remains open; a smaller proof dependency core does not answer it.

## Credit

DreamingOfClouds supplied the 19-line configuration and earlier 20-to-22 bounds
in PR2111/2162. Nick Petalas supplied PR2206's exact-cost witness, Schur encoding,
RUP certificate, written completeness proof and two Python checkers. Their
source and notices remain unchanged. Lean and its standard-library authors
provide the proof kernel and logical infrastructure.

Prepared for **ywz65** with substantial OpenAI Codex assistance in proof
generation, checking and writing. New work is Apache-2.0. This contribution
claims the concrete propositional kernel proof and binding work, not literature
priority for RUP, propositional proof reconstruction or the predecessor result.
