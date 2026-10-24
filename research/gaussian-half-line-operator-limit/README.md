# Gaussian half-line inverse limit

JoyboyBrian, with substantial OpenAI Codex assistance. Scoped written theorem with exact finite corroboration; no new kappa.

For fixed alpha>0 and the original full cell N=floor(1/theta), the checkerboard inverse scaled by sqrt(theta) converges in operator norm, under an explicit two-edge step embedding, to two copies of a half-line Volterra operator. [PROOF.md](PROOF.md) gives the full infinite-product coefficient, boundary domain and quantified remainder. This resolves the boundary-layer implication left formal in Ryanson Jonathan #4435 and open after Nick Petalas #5150, beyond JoyboyBrian #5103's matching-order upper estimate. All finite q-LDU identities retain Jose Manuel/#4193, Vlado Vojdanovski/#1673 and classical lineage credit.

The exact limit is alpha exp(b/4)/(2 sqrt(b) P(b)^3), b=pi/alpha², P(b)=product(1-exp(-2br)). A growing-alpha limit is not inferred. The complete cell is untruncated; the first source fixture is alpha3,theta1/400,N400.

Run `python3.12 -B scripts/research_package.py --package research/gaussian-half-line-operator-limit`. Both normal and optimized commands use standard-library exact rational elimination and unchanged source exponent AST, without fitting a numerical norm. RESULT and SOURCES are mandatory and the entire receipt has typed canonical JSON equality.

No coefficient-preparation or inverse-application algorithm, rounded-prefix guarantee, tape/movement/storage tariff, native admission, outer transfer or integer recovery is supplied. These are obligations, not zero charges.

## Open next questions

See PROOF.md: uniform growing-alpha estimates, other section/endpoint scalings, and an actual complete rounded caller remain separate.
