# Attribution and license

Prepared for Ali Romman (@aliromman), with substantial OpenAI Codex
assistance in research, proof, implementation, verification, and writing.
One assigned AI agent prepared this package. Parent-agent review is
separate from independent human review. New material is Apache-2.0.

Ali Romman's PR1038 supplies the dirty quadratic-phase interface, three
rounded real shears, exact inverse, dirty-target error proof, independent
interval oracle, and test-data and tape-observer patterns used here.
`chirp.py` derives its dirty wrappers and precision function from that
source. `DERIVATION.diff` records the change. The original files remain
byte-exact under `vendor/pr1038/`, with Git-blob and SHA256 pins.

The retained PR985 solver credits Rohan Guliani's PR846 Euclidean
decomposition, Charles Bethin's PR764 suffix estimate, and Chafik
Boukhalfa's PR628 dirty kernel lineage. Chafik Boukhalfa's PR479 supplies
the retained chirp family and scalar cost context. Ross Richardson's
PR948 gives independent symbolic evidence for the predecessor phase
stream. The original notices remain in the package.

The PR1054 constant-coefficient precision result and PR1025 analytic
root-height result were read for their scope. Neither is an executed
dependency or an assumed combined theorem here. The previous local
cyclic-stability work separates raw coefficient growth from necessary
precision; this package makes no contrary obstruction claim.

Multiplicative quadratic-phase recurrences, Machin series, Taylor series,
and three-shear plane rotations are established methods. No literature
priority is claimed. This contribution supplies their explicit reversible
stream, uniform guard bound, exact cleanup, and paid integration with the
specific dirty solver.
