# Four exact pre-sink retimings

The source is the post-restoration, pre-sink word of PR #320 at commit
`1b37957d1520c80b6ea796bf418e52be5109c2d4`. It has 386,972 records, 336,292 scalar ADDs,
and raw SHA-256 `ec2bfcc1d1fd9227beeddb0afa78a2c2ff6e10d49bff55183bc77ac84f4b79fd`.
The frozen selection also pins the exact scalar projection, old frame basis hashes and explicit new bases.
Record indices below are zero-based in that word; scalar tuples use its literal register identifiers.

| record | scalar tuple (destination, source, coefficient, category) | frame rank |
| ---: | --- | --- |
| 278344 | (8726, 8729, 1, 30) | 8 → 9 |
| 278588 | (8763, 8766, 1, 30) | 8 → 9 |
| 278670 | (8775, 8778, 1, 30) | 8 → 9 |
| 279118 | (8868, 8869, 1, 30) | 13 → 14 |

Category 30 is `kernel_setup`. No scalar operation is inserted, deleted or reordered in this stage.
The four frames were found with PR #320's inherited constructed join/meet search, applied before the sinks.
Discovery is not a proof dependency: verification reads the four explicit frozen bases.

For each retiming the checker binds the actual input record, old rank and basis hash, registers the explicit
new basis, checks its rank and nondegeneracy, and computes integer source columns through the actual scalar
word. The new frame must contain the exact source span of every non-target operand. It then discards old
MOVE records and rebuilds every MOVE path from the scalar and COPY events, requiring nested adjacent frames,
fixed initial and final maps, and unchanged COPY lifetimes. It checks byte-for-byte equality of the scalar/COPY
projection and checks the scalar hash separately. It independently reconstructs the paid-call census from the
required frames and endpoints, verifies emitted and reconstructed censuses agree, and checks every nested pair
also on reflected annihilators. All predecessor used frames are retained as prime-check obligations.

The endpoint check is `final == producer['final_state']`. This is needed because the preceding restoration
stage has already shortened 240 helper endpoints. Entrances and endpoint completions remain identical, and
`raw_ledger.rebind_presink` compares the actual completion census with the previous ledger before assembling
the five-stage histogram.

The one-stage delta is exactly `{1:12, 2:-8, 8:-3, 9:3, 13:-1, 14:1}`. Its call-count delta is +4 and rank-mass
delta is zero. For φ(r) = r ln(100/r), its score is approximately −1.9305726664024405. The seven terminal
sinks and the same 133 reorder scalar incidences are subsequently replayed on the new word. Re-running the
inherited reorder selector makes 24 equal-cost side-root anchor choices at rank 19 instead of the earlier
rank-18 anchors. This changes the final scalar ordering while preserving the exact reorder histogram delta
and scalar map. Both frozen selections bind to the new records and both stages retain their original
all-column F₂ and inverse replays, omission controls,
integer and source-span checks. The final rank mass, register count, entrances, completions and banks agree
with the predecessor.

The final 386,909-record word has raw SHA-256
`cc9305bfaef3c8d581c4fffae2faa837e2c93e67982ea18ce250962043c1439f`.
The final normalized histogram is computed from those emitted records, not patched into the mathematics.
Both independent rational moment engines certify the bit root `770149364272199/10^18` and reject its next
grid point. All 47 outer inequalities and seven strict margins give
`κ = 30782267613603/40000000000000000`. This is a strict improvement of `2791718532/10^18` over the exact
pinned predecessor. The unchanged complex supplier remains above the binding bit supplier.

The full verifier additionally repeats source integrity, all-column scalar replay, signed integer restoration,
all retained/new exact determinants and prime witnesses, endpoint charts, bank lowering, global projections,
complex program checks, and the finite stock bill. The conclusion is a conditional finite construction under
the inherited all-size compiler, weighted-selector, common-chart, restored-row, routing, prime, recovery,
complex-symbolic and analytic interfaces. It is not an unconditional multiplication theorem.

Original concave descent and constructed-frame methods: Rohan Arun, PR #287/#291, with Anthropic Claude
assistance. P = 10 stage integration and inherited search: Chafik Boukhalfa, with Anthropic Claude assistance.
This four-frame selection, restored-endpoint adaptation and successor package: OpenAI Codex assistance.
Apache-2.0; complete lineage is retained in `NOTICE.md`.
