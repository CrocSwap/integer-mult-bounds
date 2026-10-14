# Attribution and license

New actual-port lift construction and independent verification prepared
with substantial OpenAI assistance in research, code, proof checking,
certificate generation and writing. This is not independent human peer
review. New files follow the repository's Apache-2.0 license.

The Turyn geometry, glue classes, original nine-clique parity certificate,
parity-projector argument, and earlier per-profile fitting results are from
**DominikScholz's PR598**, incorporated head
`615ca6f06fdea0c50dbef733370c47349e25c555`, and its packages
`research/leech-lattice`, `research/turyn-code-space`, and
`research/turyn-port-labels`. Their notices disclose OpenAI GPT-6 Astra
assistance and remain unchanged. This contribution claims no priority for
the general parity method or the previous binary profile dimension-nine
obstruction.

The source geometry credits R. J. Turyn, J. H. Conway, N. J. A. Sloane,
E. Bannai, Gabriele Nebe, Vincent Corlay, Joseph J. Boutros, Philippe Ciblat,
Loic Brunel, and SageMath contributors. The exact source notices are pinned
and retained in the standalone replay package.

The new part is a simultaneous actual-port lift of the nine eight-class
restrictions **within each individual profile**, plus explicit upper-bound
labels and code-disjoint verification. It does not lift the original global
twenty-four-class cliques. Applying the inherited rank argument to the
actual-port covers removes the prior per-profile restrictions to symmetry,
scalar labels, and F₂ rather than arbitrary characteristic-two fields.

The earlier new `turyn-profile-cnf` package supplies the independent
standard-library coordinate generator used during construction. Its
delivered files are preserved unchanged. Only that new, hash-pinned helper
is imported by the generator; the default verifier imports no such helper.

The overall research framework is maintained by Douglas Colkitt / CrocSwap
and inherits the source and contributor lineage preserved in the repository.
The original-base PR799 conditional frontier is historical context only;
subsequent upstream selections are separately dated in the local claim.
