# Exact boundary of the formal and external claims

| Claim | Evidence here | What remains external |
| --- | --- | --- |
| Equality on every Boolean basis vector determines equal linear maps | `basis_complete`, proved by induction on the input dimension | None within its declared `Bool` vector model |
| A finite listed XOR circuit is linear | `run_linear` | Interpreting physical operations as these gates |
| Basis equality implies equality on arbitrary indexed Boolean streams | `basis_to_stream` | Establishing its basis-equality premise for the retained 661-wire files |
| Equal stream outputs may precede any identical continuation | `continuation_substitution` | A physical continuation and its complete state interpretation |
| The two retained D prefixes have the same 661-by-661 matrix | Distinct integer-row and literal Boolean-column Python engines; exact compressed source pins | Python/JSON/gzip execution and compressed-word-to-gate translation |
| Both literal D prefixes use the common zero frame and source-free target/helper operands | External typed adapter checks | Frame semantics, physical implementation and inherited chronological assumptions |

The Lean gate language allows a destination equal to its source; that operation
is still XOR-linear. The external physical-prefix adapter is stricter and
requires distinct target/helper operands. The formal theorem does not silently
prove any stronger physical gate-admission rule.

The continuation claim holds the continuation **identical**. It does not claim
that the complete original PR589 word equals the complete PR1062 candidate,
whose B/C sections also differ. The intended application substitutes one D
prefix into the candidate's fixed remaining continuation, as described by the
credited semantic-D predecessor. This package does not replay or formalize
that complete supplier.

All 661 Boolean input columns include sources, targets and arbitrary helper
dirt. Equality on source columns alone is insufficient, as the explicit
`target111 ^= helper222` control demonstrates. The generic Lean theorem is
uniform over index types, not an extrapolation from a few sampled stream lengths.
The actual 661-wire finite premise has not been moved into Lean.

The registered Python hook does not invoke Lean and cannot certify a fresh
kernel run. `check_lean.py` requires a live compiler and recompiles the exact
source plus its examples; no stored log or receipt is accepted as a substitute.
The source hash identifies the reviewed Lean text but does not authenticate a
compiler binary or arbitrary hostile elaborator output.

No new H2/K admission, integer payload bound, frame/hosting schedule, all-size
physical compiler, tape/rounding theorem, kappa, or complete multiplication
theorem follows from this package alone. The existing ADD-count improvement
and semantic-D supplier argument belong to the credited predecessors.
