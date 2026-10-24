# Verification record

Both registered isolated, warning-strict CPython 3.12.13 runs passed in normal
and optimized modes. Each process used `-X int_max_str_digits=0` for explicit
large scalar serialization. Both printed `PASS_INVERSE_CERTIFICATE_BIT_BOUNDS`
and matched RESULT.json. No source code or arithmetic was changed for that
runtime option.

The 99 programs include 36 equality certificates and 63 nonzero words.
There are 98 comparisons with the independent reduced-group-word oracle
and 63 literal unipotent-matrix witnesses. All generated certificates pass
the separately transcribed source checker. The audit compares both compiled
models and checks common denominators, candidate/accepted path rows, reduction
results, echelon coordinates and their exact original-row reconstruction.
The proof supplies the all-input and primitive-temporary bounds; the finite
audit does not measure every integer temporary or establish an asymptotic
runtime from samples.

The corpus includes a 16,001-bit scalar, a reducible fraction with two
16,001-bit operands, large coprime denominators, nearly dependent rows,
delayed inverse tails through degree 16, dirty returns, aliases and 80 random
programs. A separate close-row identity has 1,025-bit coordinates despite
small entries. The weighted stress endpoint has 2^64 distinct words, 260
compiler states and 64 invariant rows. Its maximum observed model height is
262 bits; its equality-certificate coefficient height is 254 bits. The stated
bounds are much larger and are not practical resource predictions.

Nine rejecting controls check field, scalar, compressed-input and certificate
size restrictions. Three additional direct audits pass for an empty operator
alphabet, one 257-term scalar assignment, and a zero-coefficient query.
These three audits are separate from the 99-case frozen receipt.

Four actual code mutations fail in both modes, before receipt comparison:

- Set Q to one: the exact model common-denominator check fails.
- Set G to one: a 1,001-bit scalar violates the model height bound.
- Change inverse feedback from minus one to plus one: the independent
  compilers disagree.
- Remove the minus sign from stored elimination coordinates: exact
  echelon-coordinate reconstruction fails on independent close rows.

Eleven consumed files remain byte-exact. The producer, checker, scalar code,
oracles and fixtures retain their original notices. The two downstream
proofs support the composition corollary. Their full orthogonal and detector
replays were not rerun in this package. No independent human/proof-kernel
review, selected cold replay, Lean, Docker, native tape or complete compiler/
kappa calculation was run. The full-history wrapper is unpassed in the
shallow checkout. Source-pin ancestry, committed bytes, official export
integrity and read-only Git-free replay are separate publication checks;
the public handoff records their results.
