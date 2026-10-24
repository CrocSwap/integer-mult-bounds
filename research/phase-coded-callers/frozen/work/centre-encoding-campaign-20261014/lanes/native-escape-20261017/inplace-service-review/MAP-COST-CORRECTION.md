# Scope correction for the simultaneous translation cost

This addendum corrects the map-cost statement in the frozen REVIEW.md,
SHA256 d0315887769ec9bc12527a4bdb255b7804b0675b7638767a19062587b41e89cf.
The earlier file is preserved as evidence. Read it with this correction.

The claim that all 144 Walsh translations have a direct O(V) lowering
as complements of one contiguous f-bit address field is withdrawn for
the general retained layout. The resulting claim that the whole body
has fixed linear stream cost is also withdrawn.

The primary source `upstream/build/sections/05-layers.tex` puts one
selected bit at offset rho inside each K-bit chunk. There are f chunks
in each slot. A simultaneous shift g_j flips the selected bits in one
slot and leaves its other bits unchanged. For K>1, these f selected
bits are interleaved with unselected bits. Collapsing the prefix and
suffix does not make them one contiguous f-bit address field. Therefore
the proposed map y -> -1-y modulo 2^f is not that physical map.

The shortcut is valid when K=1. At general K it would need an explicit
packed extraction view and its cost, or a separate lowering of the
interleaved complement. Neither was proved in the frozen review.

Retain the producer's original invoice of 144 simultaneous translation
maps and the cost of the applicable packed-map backend. Retain the
sixteen outer view maps. Do not price any of these maps as a single bit
operation or use the withdrawn O(V) shortcut in a supplier recurrence.
The producer's frozen proof did not make that shortcut.

The following independently checked results are unchanged: every
literal arithmetic map, both inverse orders at all 512 modes, all nine
formal input columns, zero owned output, the complete scalar invoice,
the exact translation-kernel coefficients, all 64 completed-level phase
identities, the one-C0 owner contract, and the zero native-child count
of the declared word. The direct marked-counter conditional scans are
also unchanged. Their marks can be placed at the actual selected-bit
positions; the proof applies to arbitrary positions.

The one-bank code remains a useful local construction with explicit
map obligations. It is not a complete new supplier or kappa bound.
The owner-review lane found the layout error while extending the word
to a forward encoder. The coordinating agent was informed immediately.
OpenAI Codex assisted the check. No PR, commit, or push was made. Before
any future PR description, read
/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md.
