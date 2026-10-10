# The bit-side export contract (the twin)

**What the bit supplier's program must publish for the rank-22 realization obligations R1-R4 to
close.** The complex side's [export contract](EXPORT-CONTRACT.md) asks what a supplier must publish
for C1-C3 to become a bank increment. This is its twin for the *other* contract in the same ledger
pair: the rank-22 bank absorption of the bit word
([#219's package](references/pr219-run1/README.md)) certifies the accounting and states R1-R4 as the
remaining physical realization. This file says exactly what a physical realization has to publish,
in what form, and how each part is checked.

The machine-readable twin is [export-contract-bit.json](export-contract-bit.json), and every digest,
count, status and obligation statement quoted below is asserted against the pinned bytes by
`verify.py -> check_bit_export_contract`. The schema, the seven acceptance tests `A1-A7`, the
gate/replay split and the fail-closed reading are the complex side's, unchanged: the two contracts
differ in what they ask for, not in how they are checked.

## 1. What the pins already publish (the starting point, read not assumed)

The bit side is **half-met**, and that is the difference between the two twins. The complex side has
no body export at all; the bit side already publishes, in the pins:

| published today | value | where |
| --- | --- | --- |
| the accounting package's own verdict | `CONDITIONAL accounting construction for the rank-22 bank absorption ... the physical realization obligations R1-R4 are OPEN and the kappa below is conditional on them` | `certificate.json`, `status` |
| and its literal scope | "bank-absorption schedule, accounting and tiling invariants; **no physical column, chart or prime witness is built here**" | `schedule.status` |
| the conditional kappa | `700427501305159/10^18` | `kappa` |
| the absorbed family | rank 22, `ledger_bin_per_vertex = 6,672`, `occurrences_three_copies = 20,016`, `normalization_factor = 3`, `dirt_volume_registers = 440,352`, provenance `1,320 + 24 + 0 + 880` per vertex | `schedule.absorbed_family` |
| the whole-bank condition | `22 x 20,016 = 440,352 = 72 x 6,116` whole banks, stock drop `56,402 - 50,286 = 6,116` | `schedule.banks`, `schedule.row_identity` |
| the retained ledger | `W_after = 50,286`, deficit `5,808`, rank mass `3,614,784`, `857,622` children, largest 21 | `schedule.retained_profile` |
| the tiling candidates | the two admissible patterns of width 72 over `{4, 24, 22}` | `schedule.block_tilings.feasible_patterns` |
| the enumeration | every rank-22 occurrence as an integer tuple per kind, per vertex, with its row identity | `inputs/absorbed-occurrences.json` |
| **the word's base checker** | `4d7c86cd999a1519e0dfb6dcf33a8f26e442a353c3665a0f06881216a260fbf3` | the inventory's `source_pins.checker_sha256` |
| the *unabsorbed* word's formal layer | `20,634` formal columns and `17,114` dirty columns per direction, `1,760` source and `1,760` target columns, integer residual bound `39,780`, packed digit bits `24`, F2 identity and defining-integer decoder both `true`, `new_frames_added = 0` | PR200 certificate, `bit.terminal` / `bit.formal` |
| the *unabsorbed* word's witnesses | `24,401` used frames, `24,401` distinct bases, maximum determinant 118 bits, rule `q > 2^80`, `witness_sha256 = 612f0b91...`, `script_sha256 = 98cd03bc...`, status `PASS exact prime witnesses for every used physical frame` | PR200 certificate, `bit.prime_witnesses` |
| the banked row's physical layer | `m = 72`, `banks = 45,842`, `gauge_roles = 2,200`, `incidences = 154,026`, `physical_roles = 17,114`, `color_stats = {swaps: 733, longest_swapped_path: 11}`, `conflicting_assignment_rejected = true`, `max_den = 18`, `max_num = 5`, `max_chart_factors = 171`, `word_sha256 = 0728ed1c...`, `chart_sha256 = 22662b85...`, `incidence_sha256 = 76bff256...`, `status = PASS exact actual-chain chart and incidence checks` | PR205 certificate, `physical` |

Two readings matter, and they are the reason this twin is a *closed checklist* rather than an open
question.

**First, the physical layer exists -- for the unabsorbed word.** PR200 built and pinned the formal
columns and the prime witnesses; PR205 built and pinned the charts, the incidence colouring and the
reject control. R2 and R3 are those same checks re-run on the *banked* word, and the absorbed family
is not a different object: the inventory's `source_pins.word_p12_sha256` **is** PR205's
`physical.word_sha256`, `0728ed1c...`. So the contract asks for bodies behind digests of a word this
repository already half-holds, not for new trust.

**Second, the digest without the body is the gap.** The five word bodies
(`word_p12.json.gz`, `frames_p12.json.gz`, `graph_p12.json`, `kchron_p12.json`, `profile_p12.json`)
exist in PR200's `prime_witnesses.input_sha256` as hashes of files in the supplier's own workspace,
the witness body as `bit/prime-witnesses.json.gz`, the chart, incidence and word bodies as PR205's
three hashes, and the checker as `source_pins.checker_sha256`. None of those bodies is in the pins.
The one genuinely *new* artifact is the per-occurrence assignment R1 asks for: the enumeration gives
the items, `schedule.py` gives the admissible tilings, and the assignment (item -> bank, offset) with
its normalizer does not exist anywhere yet.

## 2. The required exports

Each export names what must be published, the form it takes, the pinned value it must reproduce and
the obligation it unblocks. "Reproduce" means the published body hashes to the digest the certificate
already carries, or declares exactly the count the pinned accounting already fixed.

| id | the program must publish | form and cardinality | pinned value it must reproduce | unblocks |
| --- | --- | --- | --- | --- |
| **B1 the word and its frames** | the bodies behind the terminal word's five input digests: word, frames (integer kernel basis per frame), graph (parents, children, edges), chronology, and the profile, with the canonical renumbering map from the supplier's frame ids | JSON/gz, integers only; `20,634` formal columns, `17,114` dirty columns, `7,282` changed operation frames, `24,401` used frames, `2,200` selected roles | `prime_witnesses.input_sha256` (all five), `witness_file`, and PR205's `physical.word_sha256` unchanged | R2, R3 |
| **B2 the bank blocks and the assignment** | the rank-22 residual item (one per enumerated occurrence), its coordinate-block shape in a bank of width 72, the selected tiling, and the per-occurrence assignment (item -> bank, offset) with the normalizer sending each item's true residual projector to its assigned block, hashed | JSON tables, integers only; `20,016` items over `6,116` banks of width 72 = `440,352` registers; `6,672` per vertex under factor 3 | `schedule.banks`, `schedule.absorbed_family`, the feasible tilings, the pinned inventory's `counts_per_vertex` and `row_identity_per_vertex` | R1, R4 |
| **B3 charts, colouring and witnesses** | the exact charts of every frame the new blocks use (integer kernel bases, fraction-free inverses, replayed elementary factors), the incidence colouring of the new bank incidences, and the distinct integer Gram/prime witnesses with residual factors | JSON/gz; `24,401` used frames, `17,114` physical roles, `154,026` incidences, `max_chart_factors = 171` | PR205's `chart_sha256`, `incidence_sha256`, `max_den`, `max_num`, `color_stats`, `conflicting_assignment_rejected`, and PR200's `witness_sha256`, frame counts, `rule` | R1, R3 |
| **B4 columns of the banked word** | per direction and ring the formal column tables of the banked word: every source, target and dirty-register column over F2 and over the defining integers, rank-22 transitions realized by bank re-assignment instead of paid children | JSON tables of integer addresses; `20,634` formal, `17,114` dirty, `1,760` source and `1,760` target columns; residual bound `39,780`, packed digits `24` | PR200's `bit.terminal.formal`, `integer_residual_bound`, `packed_digit_bits`, `bit.formal`, `terminal.status`; and R2's statement | R2 |
| **B5 the reject controls** | the negative controls the word's own certificates ran, re-run on the banked word and published with the rejected object: the 4 word controls, the 3 terminal controls, the 21 adverse coarse controls, the 2 rejected adjacent grids and the 6 rejected bank partitions with their 12 weighted cases | JSON, per control the mutated object, the predicate violated and the observed rejection | PR200's `adverse_control_count`, `word_controls`, `terminal.controls`, `coarse.controls` and `coarse.scope`; PR205's `bank_controls`; R3's statement | R2, R3 |
| **B6 envelope and integrity** | the paid moment envelope of the banked word in the form `arithmetic.py` consumes (stock, deficit, retained histogram, worst-case bad fraction `10^-16`, fallback `32*72^2` per retained child), the completion-child ledger, and the manifest of every digest of B1-B5 and the predicates actually run | JSON envelope plus manifest | `schedule.retained_profile` (all of it, histogram included), `schedule.row_identity`, `kappa = 700427501305159/10^18`, `schedule.absorbed_family`; and R4's statement | R4 |

R4 is the one place an export may move a published number, and the contract says so: if R1 introduces
a completion child, the export must add it to the ledger and **publish the recomputed kappa**, and
the citation this contract makes on `kappa` must be re-anchored. Until then B6's gate admits exactly
the zero-completion-child envelope the pinned kappa prices (`completion_children <= 0`), which is the
fail-closed form of the same rule.

## 3. Acceptance tests (what "verifiable form" means)

The tests are the complex side's `A1-A7`, held to the bit side's own published bounds.

| id | test | bound it is held to | reject control |
| --- | --- | --- | --- |
| **A1** | every exported body hashes to the digest the word's certificates already published | `1cb7e8ed...` (word), `ad8e2705...` (frames), `31a09a55...` (graph), `0fab548e...` (chronology), `c44ef864...` (profile), `612f0b91...` (witness), `0728ed1c...` / `22662b85...` / `76bff256...` (PR205's word, chart, incidence) | any altered byte fails the hash; a matching one is identity, not correctness |
| **A2** | a complete bijection between the supplier's frame ids and the canonical ids, with the frame and role counts reproduced | `24,401` used frames and `24,401` distinct bases, `17,114` physical roles, `2,200` selected roles, `2,242` pinned word files | a renumbering that is not a bijection, or an id used twice |
| **A3** | fraction-free chart inversion and replayed elementary factors on every frame the new blocks use | `max_denominator <= 18`, `max_abs_numerator <= 5`, `max_chart_factors <= 171` | a factor that does not replay, or a denominator above 18 |
| **A4** | the formal columns re-run on the banked word: every source, target and dirty-register column over F2 **and** over the defining integers | `20,634` / `17,114` per direction, `1,760` source and `1,760` target columns, residual bound `39,780`, packed digits `24` | counts quoted from the certificate instead of coming out of the exported tables |
| **A5** | the per-child bijection: the exported occurrences map onto the pinned inventory's items with no other bin touched | `20,016` three-copy items over `6,116 x 72 = 440,352` registers, `1,320 + 24 + 880` per vertex | an occurrence outside the rank-22 bin, a block left without its item, or counts that are not the pinned inventory's |
| **A6** | the colouring of the new bank incidences with the conflicting assignment rejected | `154,026` incidences, `swaps = 733`, `longest_swapped_path = 11`, `conflicting_assignment_rejected = true` | a conflicting assignment accepted |
| **A7** | distinct integer Gram/prime witnesses for every frame the new blocks use, residual factors below the retained `q` bound | `24,401` frames, `24,401` distinct bases, maximum determinant 118 bits, rule `q > 2^80` | a repeated witness, or a factor above the bound |

A5 is the obligation's own shape: R1 asks for the residual-type definition, the block shapes and a
**hashed** item -> block assignment, and the schedule already enumerates the admissible tilings
(`{rank4: 1, rank24: 1, rank22: 2}` with 4 blocks, or `{rank4: 7, rank24: 0, rank22: 2}` with 9). The
export supplies the selection and the assignment; the gate checks it against the pinned counts and
the pinned bank table in one direction, and the bijection in the other.

## 4. What the contract deliberately does not ask for

* **No internal id stability.** Only the canonical renumbering map and the bijection test `A2`.
* **No program text beyond canonical data.** B1 is the word, its frames, its graph, its chronology and
  its profile -- not a listing in the supplier's own language.
* **No sources for the supplier's own claims.** The importer re-runs the columns (`A4`) and re-charts
  the frames (`A3`); `bit.formal`'s `identity` and `defining_decoder` booleans are claims to
  reproduce, not results.
* **No re-derivation of the accounting.** The schedule, the whole-bank condition, the retained ledger
  and the conditional kappa are the pinned package's; B6 reproduces them. The single licensed
  exception is R4's completion child, described above.
* **No second bank construction.** The gauge family's absorption is already built and pinned in PR205:
  it is this contract's *precedent*, not its target.
* **No asymptotic interfaces.** General Clifford/tensor, uniform weighted compilation, restored rows,
  routing, paid layout, prime supply, precision/recovery and fixed tape stay the assumptions they
  already are. This contract can buy a completed conditional finite witness, never a theorem
  (`obligations.json -> claim_scope`), and the complex side's twin states the same limit.

## 5. The gate, the pinned checker, and the state today

Both contracts are consumed by the same executable form, [importer66.py](importer66.py), which is
contract-driven: it reads the contract, decides the gate from the bodies' declared data, and refuses
to claim the replay.

```sh
python3 -B importer66.py --contract export-contract-bit.json --self-test
python3 -B importer66.py --contract export-contract-bit.json --exports exports-bit [--checker FILE]
python3 -B importer66.py --contract export-contract-bit.json --exports exports-bit --partial [--json]
```

**The gate** is decidable from what the bodies declare: the hashes (`A1`), the cardinalities and the
frame bijection (`A2`), the chart and witness bounds (`A3`, `A7`), the colouring statistics (`A6`),
the per-child bijection against the pinned inventory (`A5`), and the column counts that must come out
of the exported tables rather than the certificate (`A4`). `--self-test` builds synthetic bit bodies,
patches the anchored digests to the synthetic hashes and breaks each check in turn: the same thirteen
cases the complex contract gets, all four exit codes included -- the thirteenth being the partial
report on the real drop, which the harness also refuses to read as an import. Three defects the real
drop exposed are fixed rather than papered over: a body that is named but absent was being counted as
a *failed* check instead of a missing datum, the anchored-digest and manifest loops crashed on an
absent body instead of reporting the absence, and a body that is present but unparseable remains a
hard failure.

**The replay** is the physics -- the formal columns, the chart replay, the colouring and the envelope
re-derived -- and the harness never claims to have run it. This contract pins the bit word's own
checker, `source_pins.checker_sha256 = 4d7c86cd...`, the digest the rank-22 inventory carries. That
is deliberately *not* the complex side's `lift.checker_sha256 = 9d841bcf...`: each contract pins its
own supplier's checker by digest, and the two are asserted to differ.

**Today: the pins export 0 of 6 bodies, and the drop beside them decides 2 of the 7 tests.** Everything
above is present in the pins only as a digest, a count, a status, a path or an enumeration, so the
contract still *fails closed*: the default import exits 2 refusing the five absent bodies, R1-R4 stay
OPEN, the conditional kappa keeps its conditional flag, and nothing in the ledger pair changes status.

Beside the pins, though, this package now ships `exports-bit/`, and it holds **10 of the 15 required
bodies, 8 of them anchored**:

| export | bodies in the drop | state |
| --- | --- | --- |
| **B1 the word and its frames** | `word.json.gz` `1cb7e8ed...`, `frames.json.gz` `ad8e2705...`, `graph.json` `31a09a55...`, `kchron.json` `0fab548e...`, `profile.json` `c44ef864...`, plus the derived `index.json.gz` | complete |
| **B3 charts, colouring and witnesses** | `charts.json` `22662b85...`, `incidence.json` `76bff256...`, `prime-witnesses.json.gz` `612f0b91...`, plus the derived `charts.index.json.gz` | complete |
| **B2 the bank blocks and the assignment** | `assignment.json` | absent |
| **B4 columns of the banked word** | `columns.json` | absent |
| **B5 the reject controls** | `controls.json` | absent |
| **B6 envelope and integrity** | `envelope.json`, `integrity.json` | absent |

The word bodies and the witness body are the supplier's own bytes, each hashing to the digest its
certificate already published. The two streams are not files upstream -- PR205 published digests of
canonical streams -- so they were reproduced rather than obtained: running PR205's packer unmodified
on the word bodies re-derives both streams byte for byte, and `exports-bit/physical.rebuilt.json`
differs from PR205's published `physical` block in **0 of its 26 fields**. What the bodies do not
declare themselves is declared by `index.json.gz` (B1) and `charts.index.json.gz` (B3), derived by
`bitindex.py` from the bodies and the pinned certificates rather than typed in; neither is anchored,
because an index is a declaration and the bodies it describes are what carry the digests.

The gate on that drop:

```sh
python3 -B importer66.py --contract export-contract-bit.json --exports exports-bit --partial   # exit 4
python3 -B importer66.py --contract export-contract-bit.json --exports exports-bit             # exit 2
```

| test | on the real drop |
| --- | --- |
| **A2** | **PASS**, 9 checks: the six index counts, the frame-record bijection over 220 ids, the zero foreign-replay bound and the presence of the sibling digests |
| **A3** | **PASS**, 17 checks: the colouring statistics, the denominator and numerator bounds, the banked row and the 24,401-entry witness table |
| **A1** | 17 checks pass and 0 fail -- its eight digest anchors all match -- and it is **not runnable**: the manifest that must hash every body arrives with B6 |
| **A6, A7** | 17 checks pass and 0 fail each, and **not runnable**: B5's controls are owed |
| **A4, A5** | no check yet: B4's tables and B2's assignment are absent |

So two of the seven acceptance tests now decide on published bytes, the drop is reportable in part and
**never admissible** (code 4 is never an import), and the replay stays `NOT RUN` until the checker
`4d7c86cd...` is supplied. The run is kept as [bit-drop-report.json](bit-drop-report.json), and
[bitcontract.py](bitcontract.py) authors this twin's machine-readable form from the pinned bytes, so
the contract is reproducible rather than transcribed.

Once the remaining bodies exist, the discharge is mechanical and ordered: `A1` admits the last of
them, `A6-A7` follow B5's controls, `A4` follows B4's tables and `A5` follows B2's assignment -- the
one genuinely new artifact R1 asks for; `A4` re-runs R2 on the banked word; `A6-A7` close R3; B6
closes R4 by reproducing the retained ledger exactly. That is the whole of what this contract buys,
and it is stated in the form the supplier can act on: *publish the bodies behind the hashes you
already publish, plus the assignment the schedule's tilings make possible.*
