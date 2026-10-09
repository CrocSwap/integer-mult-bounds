# The normalizer's export contract

**What the complex supplier's program must publish for C1-C3 to become a bank increment.**
`obligations.json` -> `unconditionality` records that C1-C7 and R1-R4 are one missing artifact:
the literal operation program, then the columns, charts, witnesses and envelope re-run on the
word it banks. This file says exactly what that artifact has to contain, in what form, and how
each part is checked -- so that the work stops being "a construction" and becomes an interface
the importer can accept or refuse. The machine-readable twin is
[export-contract.json](research/complex-bank-run3/export-contract.json), and every digest and
count quoted below is asserted against the pinned bytes by `verify.py -> check_export_contract`.

## 1. What the pins already publish (the starting point, read not assumed)

| published today | value | where |
| --- | --- | --- |
| the supplier's own verdict | `PASS conditional finite witness` | PR193 certificate, `status` |
| the gap | "A literal globally renumbered operation program is not exported" | `complex_profile.status` |
| its receipts | "literal globally renumbered program/replay remains a downstream integration task" | `assembly.construction_receipts.status` |
| complex profile | `m = 66`, `W_per_vertex = 12,052`, `deficit_per_vertex = 1,320`, `h = 22`, `v = 1,320`, `rank_per_vertex = 794,112`, `physical_R = 9,412`, `loss = 440` | `complex_profile` |
| its arithmetic | coefficients `[[-2,1],[-1,1],[-1,2],[1,2],[1,1],[2,1]]`, `denominator_lcm = 2`, root `7.009184438594e-04` | `complex_profile` |
| its **digests** | `exact_scalar_program_sha256 = 3b4e671d…`, `exact_lift_certificate_sha256 = 1d81a79b…` (path `research/source-assisted-v4/.work/lift.certificate.json.gz`), `flow.witness` `51da02c6…`, `proof_chain_sha256 = {frames.json 434b815…, graph.json a4d350f…, record.json 2065cba…}` | `complex_profile`, `lift` |
| its column checks | `checked_source_columns = 1,320`, `checked_target_rows = 1,320`, `read_counts = {center: 22, deferred: 2,310, side: 3,135}`, `target_chains_nested`, `all_fresh_columns_equal_identity`, `all_centers_in_phase1`, `all_target_cap_reads_in_phase2` | `complex_profile.contract_checks` |
| its exact lift | `inverse_elementary_gates = 58,165`, `nodes = 18,532`, `physical_R = 9,412`, `witness_path = …/flow.witness.json`, `checker_path = …/exact_complex_flow_lift.py`, `checker_sha256 = 9d841bcf…` | `lift` |
| its flow | `frames = 18,532`, `vectors = 26,200`, `incoming_dependencies = 24`, `outgoing_dependencies = 8,116`, `edge_basis_values = 42,787`, birth/retirement histograms, `cache_sha256 = {frames.json, graph.json, record.json}`, `source_sha256 = {…/physical/frames.json, pairs.json, …}` | `flow` |
| its regeneration recipe | "Run `source_aligned_local_v4.py`, PR184 `complex_frame_flow.py` …, PR184 `exact_complex_flow_lift.py`, and this checker on the PR168 v4 producer cache" | `complex_profile.regeneration` |

Two readings matter. First, the supplier publishes **digests, counts, statuses and paths** --
never a body: `3b4e…`, `1d81…`, `51da…`, `434b…`, `a4d3…`, `2065…` are all hashes of artifacts
that live in its own workspace (`research/source-assisted-v4/.work/…`) or in a PR168 v4 producer
cache, and none of them is in the pins. Second, its own `flow` block says of itself:
*"Modular equal-frame flow price, retaining dirty kernel lifts and complete full-frame cleanup.
**Not an exact supplier certificate.**"* The exact object is the `lift`/witness pair, and the
contract below is addressed there; a modular flow price is explicitly **not** acceptable evidence.

## 2. The required exports

Each export names what must be published, the form it must take, the digest it must reproduce and
the obligation it unblocks. "Reproduce" means: the published body hashes to the digest the
certificate already carries, so the contract asks for *bodies behind existing hashes*, never for
new trust.

| id | the program must publish | form and cardinality | digest it must reproduce | unblocks |
| --- | --- | --- | --- | --- |
| **E1 program** | the literally renumbered operation program, in canonical order: per node its canonical id, operation kind, incoming and outgoing edge ids, and its span | JSON, integers only, exactly `18,532` nodes and `58,165` inverse gates | `lift.exact_scalar_program_sha256 = 3b4e671d…` | C2 (the word to re-run), C1 |
| **E2 frames** | the bodies behind the three cache digests: `frames.json` (integer kernel basis per frame; `edge_basis_values = 42,787`; edge nullity histogram), `graph.json` (parents, children, `incoming_dependencies = 24`, `outgoing_dependencies = 8,116`), `record.json` (provenance) | JSON, canonical integer bases | `434b815…`, `a4d350f…`, `2065cba…` (`proof_chain_sha256` / `flow.cache_sha256`) | C1, C3 |
| **E3 lift and witness** | the exact rational local lifts and inverse gate programs per node, plus the flow witness they were checked against | JSON/gz bodies, denominators `<= 2`, coefficients in the six published pairs, `denominator_lcm = 2` | `lift.certificate_sha256 = 1d81a79b…`, `witness_sha256 = 51da02c6…` | C1 (the projectors the normalizer moves), C3 |
| **E4 chronology** | per vertex the read/write tables: target read chains (nested), source controls at paid-parity frames, and the deferred/side/centre reads with their counts | JSON tables, `read_counts = {center: 22, deferred: 2,310, side: 3,135}`, `checked_source_columns = 1,320`, `checked_target_rows = 1,320` | the `contract_checks` block itself | C2, C3 |
| **E5 children** | the per-bin occurrence inventory of the absorbed families in the shape of the bit word's `inputs/absorbed-occurrences.json`: `counts_per_vertex`, `occurrences_per_vertex` as integer tuples per kind, `row_identity_per_vertex`, `source_pins` | JSON, per vertex `1,062` rank-11, `264` rank-16, `66` rank-20 items with each child's **frame/chain identity** | the pinned inventory's five `source_pins` digests as the format precedent; the flow's own `retirement_histogram` already counts these children (`"1:20": 198`, `"2:20": 1320`, `"2:21": 2640`) | C5, C6, C7, and C1's item-to-block side |
| **E6 envelope and integrity** | the paid moment envelope in the form `arithmetic.py` consumes (retained stock, deficit, retained histogram, worst-case bad fraction, fallback), plus the package path, its head, every digest of E1-E5 and the list of acceptance predicates actually run | JSON envelope + manifest | `complex_profile` totals and histograms, which this package already prices | C4, R4 |

The bit-side twin of this contract is already half-met in the pins: PR205's packed certificate
publishes a banked word's *shape* -- `m = 72`, `banks = 45,842`, `gauge_roles = 2,200`,
`incidences = 154,026`, `patterns = [{rank24: 2, rank4: 6} x 3,300, …]`, `color_stats`, and the
digests `word_sha256 = 0728ed1c…`, `chart_sha256 = 22662b85…`, `incidence_sha256 = 76bff256…`,
with `status = PASS exact actual-chain chart and incidence checks`. That is the export shape E1-E4
must reach on the complex word, and R1's precedent to extend.

## 3. Acceptance tests (what "verifiable form" means)

| id | test | bound it is held to | reject control |
| --- | --- | --- | --- |
| **A1** | every body hashes to the digest the certificate already published | `3b4e…` (program), `1d81…` (lift), `51da…` (witness) | any altered byte must fail the hash; a matching one is not evidence of correctness, only of identity |
| **A2** | a complete frame-record bijection between the supplier's ids and the canonical ids, plus `frames` and `edge_basis_values` reproduced | `18,532` frames, `42,787` basis values | a renumbering that is not a bijection, or an id used twice, is rejected |
| **A3** | fraction-free chart inversion and replayed elementary factors on every frame, with the denominator bound | denominators `<= 2`; `max_abs_numerator <= 2` | a factor that does not replay, or a denominator above the published bound |
| **A4** | the formal columns re-run on the modified word: every source, target and dirty-register column over F2 **and** over the defining integers, with the target chronology nested and the source controls at paid parity frames | `1,320` source columns and `1,320` target rows per vertex; `read_counts 22/2,310/3,135` | the column counts must come out of the exported tables, not be quoted from the certificate |
| **A5** | the per-child bijection: the exported occurrences map onto this package's `occurrences66.json` items (3,186 / 792 / 198 three-copy items onto 531 x 6, 198 x 4, 66 x 3) with no other bin touched | item counts per bin, and the flow's own retirement counts | an occurrence outside the ledger's bins, or a block left without its item |
| **A6** | incidence colouring of the new incidences with the conflicting assignment rejected | PR205 precedent: `swaps = 733`, `longest_swapped_path = 11` | a conflicting assignment accepted |
| **A7** | distinct integer Gram/prime witnesses for every frame the new blocks use, residual factors below the retained `q` bound | the retained prime threshold (PR205: `physical_roles = 17,114`, all used frames witnessed) | a repeated witness, or a factor above the bound |

A5 is the test that turns C5-C7 into an increment rather than an inventory: our side of it already
exists (`occurrences66.json` enumerates 4,176 items over 795 banks and passes `verify.py`), so the
export supplies the *identity* of each item and the bijection is checked in one direction and the
other.

## 4. What the contract deliberately does not ask for

* **No internal id stability.** Only the canonical renumbering map and the bijection test (A2).
* **No program text beyond canonical data.** E1 is nodes, kinds, edges and spans -- not a listing
  in the supplier's own language.
* **No sources for the supplier's claims.** The importer re-runs the columns (A4) and re-charts
  the frames (A3); a boolean in `contract_checks` is a claim to be reproduced, not a result.
* **No asymptotic interfaces.** General Clifford/tensor, uniform weighted compilation, restored
  rows, routing, paid layout, prime supply, precision/recovery and fixed tape stay the stated
  assumptions they already are: this contract can buy a conditional finite witness, never a
  theorem (`obligations.json` -> `unconditionality`).
* **No modular flow price.** `flow.status` disclaims exactness; only the `lift`/witness pair
  satisfies E3.

## 5. Failure semantics, and the state today

**Today: 0 of 6 bodies are exported.** Every required export is present in the pins only as a
digest, a count, a status or a path, and `check_export_contract` asserts exactly that reading
against the pinned certificate. The import therefore *fails closed*: the package stays a scheduled
target, the kappa keeps its conditional flag, and nothing in C1-C7 changes status.

Once the exports exist, the discharge is mechanical and ordered: A1-A3 make E2-E3 admissible and
C1's normalizer becomes a re-assignment over published frames; A4 re-runs C2; A5 closes C5-C7 and
the item-to-block half of C1; A6-A7 close C3; E6 closes C4. That is the whole of what the contract
buys, and it is stated in the form the supplier can act on: *publish the bodies behind the hashes
you already publish, plus the renumbering map, the chronology tables and the per-child identities.*
