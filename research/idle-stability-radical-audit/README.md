# Independent radical arithmetic audit of idle packing stability

This audit independently reproduces all eighteen integer mass caps in Maximus Putnam / Penguin's PR1685 using fixed-point repeated square roots. It neither imports the predecessor's atanh/Taylor pricing code nor substitutes floating-point agreement for certification. The selected local invoice remains fixed; no packing, supplier or exponent improvement is claimed.

## What is checked

The pinned selected invoice has width 73, 14336 live families, 144 calls, per-call profile {1:2412,2:418,3:432,4:142,5:82,8:8}, and idle cap 51. Its residual idle mass is 237024. At a=169/100000 the independent arithmetic gives the same necessary caps for idle mass at ranks at most1,3,7,16,32,48: 24,34,48,83,208,1603. All six caps also agree at the selected complex endpoint and a=21/12500. Both outward endpoints of each cap interval have the same integer floor, so these are resolved integer certificates, not decimal comparisons.

PR1685 proves that c(r)=(r/73)^(1-a)/r decreases. Consequently L+M c(51)+M_K(c(K)-c(51))<=W is necessary, and bounds the mass M_K. Its concavity argument gives the unrestricted integer optimum {51:4647,27:1}. We preserve that proof and credit. The new audit also optimizes every mass 1..100 at caps 2..12 at exponent 1/2 by an independently implemented integer-partition dynamic program. Every distinct competing histogram is separated by rational intervals; identical histograms reached in different orders are identified exactly. This checks 1100 optima and 7414 recurrence transitions rather than assuming the greedy answer.

## Independent arithmetic construction

For x in (0,1] and exponent t in [0,1], bracket t by consecutive dyadics with denominator2^96. Since x^t decreases with t, the upper exponent yields a lower bound and the lower exponent yields an upper bound. Compute each dyadic power as a product of successively square-rooted x values. At scale S=2^256, replace every lower square root by floor(sqrt(integer*S)) and every upper root by its ceiling. Products are rounded outward by integer division. Monotonicity of square root and multiplication on nonnegative inputs proves every enclosure inductively. Integer endpoint exponents are handled directly. This method uses no logarithm, exponential, solver, or predecessor implementation. 171 exact perfect-square calibrations test containment; the finite DP supplies another structurally distinct use of the arithmetic.

The three integer-relaxation moments are certified strictly below one. This means only that this optimistic arithmetic relaxation has headroom. It does not construct an owner map or certify the selected supplier at a larger exponent. Controls retain the a=0 tie boundary, reverse the claimed concentration under convex exponent2, check exclusion of1604 low-rank mass at the cited target, and retain the positive paid local charge.

## Reproduce and limitations

    python3.12 scripts/research_package.py --package research/idle-stability-radical-audit

Read-only Python standard library; assertions are not used. SOURCES.json pins the selected local invoice, while EXTERNAL-SOURCES.json pins PR1685's unchanged statement and exact result. The result comparisons establish independent arithmetic corroboration of that pinned claim. They do not independently rederive the original source circuit's invoice. No physical idle packing, owner/hosting constraints, native replay, cold replay, full theorem or new kappa is claimed.

## Open next questions

Which whole-helper and hosting constraints make the fractional and integer relaxations unattainable? First provide a source-bound catalogue of legal residual groups and compare its exact optimum with this unrestricted bound. The missing ingredient is legal construction data, not more precision in these eighteen numbers.

## Credit

Maximus Putnam / Penguin (OpenAI), PR1685, supplied the stability inequality and integer optimum; Douglas Colkitt / Claude supplied the retained complex-local-word-ceiling model and original pricing. Selected construction contributors retain their attribution. New radical arithmetic and DP audit prepared for woklerx with substantial OpenAI Codex assistance, Apache-2.0. No independent human review is claimed.
