# Attribution and scope of reuse

Prepared for **Rafael Guevara (@alephnan)** with substantial **OpenAI Codex
assistance** in research selection, mathematical derivation, source review,
coding, finite verification, and writing. No independent human review or
proof-assistant formalization is claimed. No sub-agents were used.

The direct mathematical predecessor is **Ali Romman's PR #621**,
"Prove uniform prime-power cyclic inverse bounds", incorporated into
CrocSwap/integer-mult-bounds. Its nonvanishing argument, resultant/cofactor
circle estimate, derivative estimate, cyclic-operator context, and original
Fourier transfer are retained. The original proof and attribution notice
are copied byte for byte under `vendor/`, with source and hash pins in
SOURCES.json. Their substantial OpenAI Codex assistance remains disclosed
in the original notice. The weighted Cauchy-Schwarz method is standard;
this contribution applies it to the predecessor's explicit constants.

The underlying kernel comes from the OpenAI exact-DFT preprint at commit
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`, source anchors `loc:newton`
and `loc:fourier-factorization`. The Newton/q-Pochhammer factorization is
classical; the predecessor credits Alexey Kuznetsov's "Using q-calculus
to study LDLT factorization of a certain Vandermonde matrix". We do not
claim to have independently reviewed those external sources or to have
proved a new kernel definition.

The selected-result snapshot retains the reviewed #626/#543 source and
full contributor lineage. No new supplier or selected exponent is claimed.
Nearby contributions #628, #663, #666, #668, and #692 are acknowledged
for their distinct rounded-inverse, restoration, composite, resultant,
and stride investigations. Their code is not a dependency of this package.

All new code and text are contributed under the repository's Apache-2.0
license. The unchanged upstream LICENSE is included. No literature-priority
claim is made.
