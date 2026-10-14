# Reference traversal and exact dyadic arithmetic

This four-module package publishes unchanged kernel-checked sources for chart-independent scalar realization, a concrete flat reference traversal, integer/exponent SCALE semantics and aligned dyadic addition. Its small dependency closure makes later reversible and finite-bit refinements reproducible without importing their larger implementation chains.

## Author-checked context

At source-matched κ = 836330098538459/500000000000000000 = 0.001672660197076918, the selected application is PR1094 call 000, forward row 1, SCALE(L119, -1/2). This value identifies the selected scientific context. The package does not change κ or prove the full selected-κ multiplication theorem.

## Checked coverage

- `Current1094Row1ScalarRealization`: scalar action commutes with every supplied linear Hosting chart. Complete duplicate-free component traversal refines the selected row's realized family action.
- `Current1094Row1FlatReference`: concrete real-then-imaginary order, injective bounded addresses, 8*n reference instructions, exact execution/reference equality including the accumulator, per-cell action and preservation outside the block.
- `Current1094Row1DyadicReference`: each Cell decodes as numerator / 2^fractionalBits. Every reference prefix preserves full memory/accumulator decoding. A visited cell becomes (-z, p+1); untouched cells retain both fields.
- `DyadicCellAddition`: alignment to max(pa,pb) uses explicit integer shifts. Addition has exact decoded value and a magnitude bound allowing one carry bit beyond the larger shifted budget.

The first two modules include a thin selected-row application; the traversal and arithmetic are parameterized. The four sources have 27 accepted axiom probes and four printed full types. `ACCEPTANCE.json` describes the exact source-bound acceptance. Historical preparation comments are preserved, including an old uncompiled-proposal label; they are not the final acceptance state.

## Remaining obligations

These are unbounded Int/Nat/Real reference operations. Eight*n is an abstract instruction count. Dirty accumulator behavior is explicit. Physical address/order binding, allocated finite-word representation, primitive bit-time, scratch restoration, rounding and selected global precision, the uniform recurrence-cost supplier and the full multiplication theorem remain separate. Hosting and traversal premises are visible in the theorem types.

## Reuse and attribution

James Chang with OpenAI assistance, Apache-2.0. Existing source headers and credits are retained. PR1802 supplies the current1094 Hosting interface. PR1985 supplies the component-store/explicit reference-operation foundations, including the credited historical generic entry-update slice. DreamingOfClouds' PR509/516 LemmaG/LemmaA sources retain their Claude-assisted attribution. Gareth Davidson (@bitplane), with OpenAI Codex assistance, supplies PR1309 PrefixNorm. The two public import aliases change only their single Stream import; proof bodies and headers remain intact. No novelty claim is made for these prerequisites.

`PUBLIC_SOURCE_MANIFEST.json` pins four shipped sources and seven reused or deterministically import-derived public prerequisites, 11 research modules / 79,813 source bytes. Public prerequisites are fetched into a fresh temporary reproduction directory rather than copied into this PR. See `REPRODUCTION.md` for an immutable recipe using an already prepared Lean 4.21.0 / Mathlib installation. Never load original and alias modules with duplicate namespaces together.
