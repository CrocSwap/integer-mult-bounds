# Separate OpenAI-assisted review

Two separately assigned agents reviewed the proof and implemented independent
finite checks without importing primary or predecessor code. This is not
independent human review or proof-assistant verification.

- REVIEW-A.md and REVIEW-A-ADDENDUM.md cover the all-width quotient/image
  proof, three-edge graph components, general coset bound and convexity
  corollary. `independent.py` also checks every width-six three-edge space
  and generated two-edge cases at widths five and six, including restrictions
  to active five-dimensional subspaces.
- REVIEW-D.md covers the five-dimensional uniqueness argument, explicit
  pool, cube-lattice/free-coordinate split and general-bound corollaries.
  `independent_witness.py` independently reconstructs all 496 width-five
  rank-one idempotents and all 372 proper nonzero subspaces.

Both reviews accept the scoped statements with the resolved clarifications
recorded in their notes. The final pool proof SHA256 is
`1fad3fa92b26bcd290b179ee3b714c3d25017bc63fa2439124e2e10ddb2c374c`.
The independent checks pass normally and the authors' optimized runs agree.
Reports INDEPENDENT.json and INDEPENDENT-WITNESS.json retain their output.
The primary normal and optimized runs also agree exactly.

No predecessor scientific suite, selected multiplier replay, native compiler,
or all-size admission is asserted. Review metadata distinguishes this written
proof and its finite evidence from those unrun obligations.

## Additional bridge-word theorem

FIVE-CORE-WORD.md SHA256
`c24c74b47d34144e0f3c812c192edae92f199c0f25e26f95cc9b7c25dd5d0852`
was separately audited after the pool theorem. REVIEW-A-WORD.md and
REVIEW-D-WORD.md explicitly check the paid-generated exponent group,
associated-graded relation ideal, star independence, partner elimination,
chronology and final monomial cancellation. They distinguish restricted
bridge deletion from any full ambient spectator-preserving program edit,
and check the ambient rank conclusion through target multiplicity matching.

The primary quadratic checker covers 11,064 bounded words; the separately
authored whole Laurent checker covers 720 labeled six-call orders, including
480 rejected interleavings and a wrong-sign control with the same linear
kernel. All eight declared command arrays passed under CPython 3.12.14;
VALIDATION.json records exact commands, durations, output hashes and scope.
The universal word theorem rests on the written proof, not finite searches.
