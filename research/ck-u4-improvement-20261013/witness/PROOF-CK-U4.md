# Transfer of four dimension-eight ends to CK

The pinned PR637 JP8 recipe differs from pinned PR635 by a 56-gate premix
prefix and 20 appended low-frame tail gates, followed by a new FULL cleanup.
The portable constructor verifies the unchanged premix suffix and inherited
146-gate tail before extracting those additions. It applies exactly those
additions to pinned PR637 CK, with no new forward absorption.

The four helpers 233, 265, 425 and 441 use the common frame
`[256,128,64,32,16,8,6,1]`. Their tails share dimension-four accumulators.
After the extended main program and low-frame tail, exact sparse rational
replay gives unit rows and columns for all 66 ended helpers. This includes the
four new helpers and every previously ended helper. An exact dyadic
Gauss–Jordan remainder then restores all non-target, non-ended registers at
FULL. Every low-frame end remains untouched by that remainder.

The 56 added premix gates run at the empty frame after the existing wrappers.
The proof does not infer compatibility merely from equal end frames: the
unchanged native auditor checks every scalar column, arbitrary dirt,
compensation, monotone frame chain and local cone. A separate Fraction/GF2
checker, importing neither constructor nor native auditor, verifies ended-row
and column isolation, non-target restoration and every frame. Six focused
mutations per supplier exercise the new premix, accumulator and terminal frame.
The inherited CK raw-word suite rejects 51 mutations.

Only four residual widths change, from 9 to 8 at helper indices 9, 41, 201 and
217. The exact local paid-profile delta is `{1:+8,2:-4,4:+4,5:-4}`. Literal owner
repacking restores the global rank mass to 520,704; the independent owner
checker recomputes all 35,424 roles, intervals, physical families, native widths
and paid profile before a separate rational interval engine verifies the moment.

Chi Zhao, with substantial OpenAI Codex assistance. The transferred gates are
Jeremy Kothe's PR637 CarrierBypass construction; inherited attributions remain
in NOTICE.md. All inherited finite-certificate premises remain unchanged.
