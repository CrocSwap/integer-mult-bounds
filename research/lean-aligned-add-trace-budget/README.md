# Aligned ADD execution and finite-trace budgets

Four unchanged accepted modules extend the public reference arithmetic with disjoint family storage, actual aligned ADD execution and bounds for every prefix of a finite SCALE/ADD reference trace.

## Author-checked context

κ = 836330098538459/500000000000000000 = 0.001672660197076918 is the source-matched PR1094 context. The selected application is call 000, raw row 2, ADD(L119,L169,1/2). This package does not change κ or prove the full selected-κ multiplication theorem.

## Checked results

- `Current1094Row1FamilyBlocks`: explicitly defined consecutive 2*n-address family blocks give a complete family-view update and preservation of every distinct family view. This is a reference layout, not an adopted physical allocator.
- `Current1094Row2AddReference`: actual read/halve/add/write reference instructions update the target by half the original source while preserving the source and every other family. Its Hosting agreement retains both owner equalities and genuine equality of source and target charts; a frame-zero annotation is insufficient on its own.
- `Current1094Row2DyadicReference`: explicit max-exponent alignment implements the ADD instruction on existing integer/exponent Cells. Full memory and dirty-accumulator decoding agrees at every prefix; endpoint cells and magnitude budgets are derived from the actual original operands.
- `DyadicTraceBitBudget`: assuming initial exponent ≤ P and numerator magnitude < 2^b on the finite full-trace footprint and accumulator, every actual prefix has exponent ≤ P+H and numerator magnitude < 2^(b+A+P+H). Here A and H count that prefix's actual ADD and halve instructions. Other initial memory remains unrestricted. A declared-list variant retains explicit address coverage and initial bounds.

The 30 accepted axiom probes and three printed types are recorded in `ACCEPTANCE.json`. Definitions and theorem statements, including historical preparation labels, are preserved byte-for-byte.

## Scope

These are unbounded Int/Nat/Real reference operations. The footprint, initial bounds, arbitrary dirty accumulator and actual instruction sequence are explicit. The finite bounds are not a selected global precision schedule. Primitive bit operations, physical allocation/initialization, selected chart transport, scratch restoration, uniform recurrence cost and the full multiplication theorem remain separate.

## Attribution and reproduction

James Chang with OpenAI assistance, Apache-2.0. Preserve the original selected PR1094 emitter and owner-routing credits; DreamingOfClouds' PR509/516 LemmaG/LemmaA sources with their Claude-assisted attribution; and Gareth Davidson (@bitplane), with OpenAI Codex assistance, for PR1309 PrefixNorm. Public PR1807 routing, PR1802 Hosting, PR1985 component-store foundations and PR2025 arithmetic are reused at immutable heads. Import-only Stream aliases retain their original bodies and headers. No novelty claim is made for reused prerequisites.

The four shipped sources total 42,243 bytes. Twelve public or deterministically import-derived prerequisites bring the actual research closure to 16 modules / 128,926 bytes. `PUBLIC_SOURCE_MANIFEST.json` pins each source and exact topological order. `REPRODUCTION.md` reconstructs them into fresh temporary directories using an already prepared Lean 4.21.0 / Mathlib installation. Public prerequisites are not copied into this PR, and conflicting original/alias namespaces must not be loaded together.
