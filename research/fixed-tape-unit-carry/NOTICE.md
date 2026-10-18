# Attribution and scope

David Arias supplies PR2776 at `7de16285a02ebb45cf46e7501baa7eafa78335e3`:
the fourteen-tape machine model, finite assembler, counter converter, split/merge
and cleanup macros, original proof, and independent dense interpreter.
Required source files and supporting proof remain byte-identical in `predecessor/`; `EXPORTS.json`
records its Git blob IDs and SHA256 hashes. The export retains its Apache-2.0 license.

Jose Manuel supplies the selected `qadic_streams.py` lowering and its retained
ordered-affine stream lineage. That file is frozen separately from main at
`e24ccc79caa1943fb126c61b45032fefddf2d3f2`. The original source notice remains
unchanged. The general affine method is predecessor work.

This package adds the unit-carry phase, its all-size invariant and exact cost
comparison, a distinct coordinate gather oracle, source-specialization checks,
and controls for the changed boundary. It claims no first affine-routing theorem.

Prepared for Charles Bethin with substantial OpenAI Codex assistance in the
implementation, mathematical derivation, verification, and writing. New material
is Apache-2.0. There is no independent human or formal-kernel review.
