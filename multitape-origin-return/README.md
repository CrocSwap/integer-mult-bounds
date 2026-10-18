# Multiplication with paid return of all six tape heads

One fixed finite six-tape machine multiplies every pair `a,b < 2^n`, genuinely
halts, and returns **all six heads to physical coordinate zero** in at most
**280n² + 282n + 71** transitions. Only the padded `2n`-bit MSB product remains,
on `sumReverse`; the other five tapes are globally blank. Width zero is included.
The input remains two supplied padded LSB stack words, with every head at zero.

This closes the previous concrete multiplier's head-return interface: its clean
endpoint had heads at `n,n,-2n` on three erased tapes. The new four-state table
uses the existing padded product as its clock. It preserves every tape cell,
moves the accumulator right once per output bit, and moves each operand head
left once per pair. A reverse scan restores the output head using its actual
blank boundary. Exactly `4n + 2` extra scanner transitions and one scheduler
handoff are charged:

`(280n² + 278n + 68) + 1 + (4n + 2) = 280n² + 282n + 71`.

No width or unbounded counter is stored in finite control. Padded zero bits are
real symbols, so both zero products and width zero are handled by the table.
No coordinate relabeling, implicit return operation or hypothetical child is
used. The operands are consumed, as in the retained clean multiplier.

## Checked interfaces

All names below are under `MultitapeToolkit`.

| Interface | Actual conclusion |
|---|---|
| `IntegerMultiplicationHeadReturn.exact_correct` | Four-state literal table, exact `4n+2` completed run, every head zero |
| `IntegerMultiplicationHeadReturn.step_preserves_cells` | Every actual scanner transition preserves the entire cell bank |
| `IntegerMultiplicationOriginRestored.product_correct` | Actual completed multiplication at the displayed full bound |
| `IntegerMultiplicationOriginRestored.output_heads`, `output_cells` | Literal origin heads and full product-only returned bank |
| `IntegerMultiplicationOriginCertificate.exists_fixed_origin_multiplier` | One fixed program quantified before every width/operand; full head/cell/value endpoint stated explicitly |
| `IntegerMultiplicationOriginApplications` | Minimal-width natural inputs, ZMod/signed residue labels, and arbitrary finite-bank embeddings with dirty spectator preservation at every prefix |

For embeddings, every active head returns to zero; arbitrary spectator heads and
whole cell functions are preserved. Natural input padding and signed residue
labels describe supplied representations, not paid parsing. ZMod output is the
full exact double-width natural product with its ring label, not an executed
truncation. The theorem/API source gives the exact quantifiers.

## Verification and reproduction

Lean **4.34.1** and Mathlib **d13f23b723b8a846827a245b89c10fc7d3f11612** are pinned.
All proof dependencies are bundled source or pinned Mathlib/Lean; no personal
project, prior toolkit checkout, local artifact or external multiplication oracle
is required to reproduce:

```sh
python3 -I -B verify.py
python3 -I -B replay.py --out /absolute/new/check --cache-project /path/to/pinned/cache --lean /path/to/lean
```

The first command checks the complete source inventory, 1,425 literal scanner
controls (including dirty work/extra tapes and corrupt-movement rejection), and
audit-report corruption controls. It does not run Lean. `replay.py` performs a
complete cold rebuild of all bundled modules in a fresh output directory, then
audits every defining-module declaration, including private/generated/global
helpers, and runs four actual Lean ownership/axiom fixtures. Only `propext`,
`Classical.choice` and `Quot.sound` are admitted. Even unused package axioms are
rejected. External dependency binaries are supplied pinned cache artifacts;
this package does not independently rebuild all Mathlib.

For this local release, **58 unchanged dependency modules are reused from the
previous fresh checked release**, after matching each exact source/artifact hash,
closed imports, toolchain and dependency revisions. **All four new modules and
the aggregator receive fresh independent kernel checks**, followed by a fresh
complete transitive-axiom audit and real negative fixtures. `REUSE.json` binds
that reuse; it is not reported as a new full cold rebuild. `expected/AXIOMS.json`
records the complete declaration inventory; `MANIFEST.json` binds all shipped
files. The external final distribution receipt binds these to the upload batches.
Hosted CI and independent human review are not claimed.

## Actual-source overlap and attribution

This extends the actual toolkit in PR2775 and its PR2235/1641/1379/64 and
Problem1.8 lineage, retaining source notices and Apache-2.0 licensing.
Main was refreshed to `a571dfa6e21bbe2d3b9cac48e5b078df59e49b68`; 20 PRs updated
since the preceding 2026-10-15T20:58:55Z checkpoint were fetched, through PR2775.
The reviewed source set is bounded, not an exhaustive novelty search.

Dan Brown and Kenny Daniel's MIT-licensed external development, linked by
[PR2411](https://github.com/CrocSwap/integer-mult-bounds/pull/2411), already supplies
complete asymptotic multiplication on finite Mathlib TM2 machines. The inspected
[Theorem.lean](https://github.com/platypii/integer-mult-bounds-lean/blob/4f40b5bc74235274835fe6952b9b90ac414786b0/IntegerMultBounds/MathlibTM2/Theorem.lean)
exposes `MulInTime ((2^34 : Real)⁻¹)`; its compact endpoint already cleans local
stacks and returns canonical output. Those external claims were inspected, not
independently replayed here. Its existing `MarkedReturn.return_exact` also proves
paid return scans. PR2769 supplies concrete paid parking-bank restoration.

The focused addition here is simultaneous physical return of this particular
six-tape multiplier's displaced heads, using its product as the finite-control
clock, plus arbitrary dirty-spectator embedding. We claim no first multiplication
proof, first return scan, new padding mathematics, improved exponent, selected
kappa change, or complete selected fast-algorithm verification. No external
platypii proof source is copied or imported. Substantial OpenAI Codex assistance
included one root and three parallel agents; no Jev was used.

## Open next questions

- Implement a charged serialized/signed parser into the explicit two-stack input
  ABI; supplied padding and residue labels do not implement parsing.
- Add actual marking and buffer placement for the arbitrary-bank caller ABI.
  Origin heads make the endpoint reusable, but do not by themselves prove that bridge.
- Develop charged variable-depth recursion/routing. This package gives a concrete
  quadratic leaf and return routine, not the full fast recursive algorithm.
