# Lead review of scalar-table microcontrol

Prepared for @CubeJerry with OpenAI assistance. Canonical base:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

The construction inspected here is `lower.py`, SHA-256
`f378d44b7a208ac9b876549a28afe0b6905d74ba109194b83bd2e3becbe5b671`.
Its retained interpreter is the unchanged lifecycle `machine.py` at
`ab239cb6ee884e7a900dd9101c34448077fad0b0`, blob
`acf475e4fccaff2fb64bd5b0b3f3fc0d246dc592`.

## Critical argument checked

I read the original `CodedPort` methods, successful `origin` loop and
`execute_table`, and compared them directly with the generated graph.
The decoder includes the initial blank probe and the repeated first-bit
read. Invalid physical symbols reject at the currently displaced head;
binary111 completes its three reverse moves before rejection. A rejected
left step restores the old head. These distinctions affect both the
operational contract and the exact clock, and cannot be abstracted away.

Each table row has a distinct dispatch state. The primitive graph then
performs exactly the ordered raw tape actions of that row, or selects its
fixed successor, cleanup entry, or rejection terminal. Successful cleanup
links three-state origin loops in ascending port order; rejection skips
success cleanup. Induction at row boundaries, refined at each raw action,
establishes the simulation relation. Terminal states have no charged
outgoing transition. Thus the selected serialized machine has C=A+U,
where U includes the fetched halt/reject row and A includes successful
origin actions. This is an exact clock of this implementation, not an
optimal-machine lower bound or an equality with invoice tariff units.

An independent manual count gives

`S = N + 4 + 3P + 46B + 9W + 13R + 5L + J`,

for B branch rows, W writes, R right moves, L left moves and J literal
rejects. A branch contains 1 preliminary probe, 7 prefix reads, 14 forward
steps and 24 reverse steps. Hence S<=47N+3P+4; the advertised 48N bound is
valid without removing unreachable states.

Canonical `02-streams.tex` permits stationary heads and at most one-cell
read/write/movement per tape per step. Every emitted nonterminal therefore
has a literal realization on the same fixed P tapes and seven symbols.
Expanding ignored symbols into a full simultaneous transition table costs
at most S*7^P entries and belongs to the finite setup cost. N,P and source
rows are fixed before runtime data vary; a family with growing templates
requires its own uniform setup proof. Initial head positions must be
included in visited-region accounting. No target head moves to an extra
cell, and no target tape content changes outside the matched raw actions.
Identity writes in a formal transition table do not justify a different
host backing-list allocation convention.

## Verification classification

The lead executed the author's 107-case verifier successfully; that is a
regression replay, not an independent oracle. Independent operational
review separately used 2,806 primitive cases,2,843 original table cases,
2,827 admitted generated executions and 12 detected negative controls.
The complementary model review independently checked 253 emitted graphs,
1,226,848 literal transition instances and 17 negative controls. Their
universal graph/model arguments, rather than finite coverage alone,
support the all-input theorem for the admitted fixed program.

## Limits and publication condition

The retained lifecycle proof already provided qualitative finite-control
simulation. The explicit graph, numerical state bound and exact selected
clock are the new contribution. The source grammar is deliberately
narrowed to positive distinct ports, unique branch keys and closed typed
rows. No totality theorem for arbitrary loops, binary-context interface,
Controller continuation, lifecycle wrapper, whole caller, tariff exchange
rate, global assumption removal or kappa improvement follows.

This review approves the pinned construction argument. Final proof and
metadata wording, immutable inputs, registered gates and committed-tree
publication remain separate gates; a changed implementation needs an
updated critical review.

The complete proof was subsequently read and approved at SHA-256
`fa06bcf3660f871a972915a32942f20cc76187f449086d97e957a1bf83445b89`.
It includes the setup term, excluded contexts, inactive-head convention,
failure behavior and nontermination qualifications identified above.
Package metadata and committed-byte/export checks remain publication gates.
