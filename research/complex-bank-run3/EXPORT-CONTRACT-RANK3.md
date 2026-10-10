# The rank-3 rung's export contract

**What the supplier's program must publish for C1-C7 to become a bank increment at this rung.**

`obligations.json` states C1-C7 for the complex ladder of this package, and
[EXPORT-CONTRACT.md](research/complex-bank-run3/EXPORT-CONTRACT.md) turns them into an
interface the importer can accept or refuse -- addressed to the supplier whose word the
ladder banks. This file writes **the same contract at one rung**: the rank-3 family of
PR233's source-assisted v4 layer, the first family of that row whose own volume fills whole
width-66 banks. Two things make it worth writing separately rather than reading off the
general form:

* the rung's family **divides the bank width** (`66 = 22 * 3`), so its assignment is one
  uniform tiling with **no padding at all** -- the T1 obligation the padded schedule exists
  to satisfy does not arise here, and the acceptance test that checks the assignment
  therefore *rejects* a padding register instead of asking for one;
* the retained row **re-prices above the published top of the ladder and prices bit-bound**:
  after this rung the complex coarse saving no longer binds, so the next lever is the bit
  leaf and not the supplier.

The machine-readable twin is [export-contract-rank3.json](research/complex-bank-run3/export-contract-rank3.json),
authored by [rank3contract.py](research/complex-bank-run3/rank3contract.py); the assignment
it is checked against is instanced by [instantiate_rank3.py](research/complex-bank-run3/instantiate_rank3.py)
into [occurrences-rank3.json](research/complex-bank-run3/occurrences-rank3.json). Every
digest, count and status quoted below is derived in that author and re-derived by
`verify.py -> check_rank3_export_contract`, which also resolves every citation -- so the
contract cannot cite a number that is not in the bytes it names.

## 1. The row, read not assumed

The rung is priced on a row that this package's pins did not carry until this contract, and
that is **not merged**: PR233's layer certificate at head `109a857`, vendored here
byte-identical as
[references/pr233-source-assisted-v4-layer.certificate.json](research/complex-bank-run3/references/pr233-source-assisted-v4-layer.certificate.json)
(3,988 bytes, sha256 `691cb0aaeb0d6b99…`). The digest is what pins it: if the branch moves,
`check_manifest` fails closed and this contract has to be re-taken rather than reused.

| published by the row | value |
| --- | --- |
| its verdict | `PASS source-assisted v4 word with this package's physical layer` |
| its physical audit | `PASS exact fused physical candidate, all formal source/target/dirty columns` |
| the word | `m = 66`, `W_per_vertex = 12,052`, `deficit_per_vertex = 1,320`, `rank_per_vertex = 794,112` |
| its own price | `complex_saving = 3549537/5*10^9 = 7.0991e-4`, `kappa = 6768823/10^10`, `binding = bit` |
| its child histogram | `3: 29,964`, `4: 11,517`, `18: 7,920`, `20: 66` (and `16: 243`, the old rung 3's family, which on this row is no longer a whole-bank family) |
| its lift | `nodes = 18,532`, `physical_R = 9,412`, `max_denominator = 2` |
| its layer | `frames = 17,789`, `frames_changed_from_pr168 = 0`, `pairs = 2,310`, `packed_digit_bits = 24` |
| its columns | `source_columns = 1,320`, `target_columns = 1,320`, `dirty_columns = 13,372` per direction; mutations `early-read REJECTED`, `missing-read REJECTED` |
| its column checks | `checked_source_columns = 1,320`, `checked_target_rows = 1,320`, `read_counts = {center: 22, deferred: 2,310, side: 3,135}`, `all_fresh_columns_equal_identity` |
| its audit sources | five digests under `layer.audit_source_sha256` |
| **what it does not publish** | no key containing `bank`, none containing `assign`, none containing `occurrence` -- machine-read by the author and re-read by `verify.py`. The only per-child inventory in the pins is still #219's bit-side `inputs/absorbed-occurrences.json` |

That last row is the whole reason this contract exists at this rung: the row publishes the
word's *accounting* and its physical candidate's *column counts*, and publishes no bank, no
block layout, no item address and no per-child provenance.

## 2. The rung's geometry, and why there is no padding here

| quantity | value |
| --- | --- |
| children per vertex | `29,964` (three registers each) |
| registers per vertex | `3 * 29,964 = 89,892` |
| three-copy volume | `3 * 89,892 = 269,676 = 66 * 4,086` |
| banks | `4,086` three-copy (`1,362` per copy) |
| block pattern | `66 = 22 * 3`: 22 rank-3 blocks of three registers, **every bank exactly filled** |
| padding | `0` registers, `0` per bank -- the padded schedule's T1 does not arise |
| address rule | item `i` -> bank `i // 22`, block `i % 22`, offset `3 * (i % 22)`; last address `(bank 4085, block 21, offset 63)` |
| table digest | sha256 over `item,bank,block,offset` lines: `71cb207f763fba75285d829241d330d3210d619f0adf3b79114305a0bf0d9f6c` |

The assignment is **instanced on our side** already, and that is what makes the export's
first test a bijection rather than a count: `occurrences-rank3.json` enumerates the 89,892
items, their banks, blocks and offsets, and passes `verify.py`.

The ledger the assignment induces, three-copy rows throughout:

| quantity | before | after |
| --- | --- | --- |
| stock `W` | `36,156` | `32,070` (drop `4,086` = the bank count) |
| deficit | `3,960` | `3,960` |
| mass | `2,382,336` | `2,112,660` (drop `269,676` = `banks * 66`) |
| children | `635,067` | `545,175` |
| families | `20` | `19` (the largest child stays rank `20`) |
| histogram digest | -- | `6e825f3357ba09352d6eee2a190895f414e5f9a83d0ff4772a7d002aae470bc4` |

The family takes `681/6016 = 11.32%` of the ledger's mass, and what remains still holds
whole-bank families: rank `4` (2,094 banks), rank `18` (6,480) and rank `20` (60) by the
volume criterion -- all three of which fail rank-divides-width and therefore still owe T1's
padding. They are the *next* rung's business, and this contract names them only so that it
does not look exhaustive.

### 2b. The price this rung carries, and it is bit-bound

| quantity | value |
| --- | --- |
| retained coarse saving | `417325324839139/5*10^17 = 8.346506496783e-4`; the next `10^-18` grid point up (`834650649678279/10^18`) is excluded |
| bit leaf | `7.282510899902e-4` -- the published leaf, re-derived here through #219's vendored arithmetic rather than read, and asserted equal to `certificate.json -> calibrations.run1.bit_leaf` |
| budget | the leaf itself (`bit_leaf_headroom = 0`): the complex branch, at `8.346506496783e-4`, is *above* it |
| kappa | `1819302815717/25*10^14 = 7.277211262868e-4`, `binding = bit` |
| complex ceiling | `417325324839139/500417325324839139 = 8.339545889388e-4`, i.e. `1.06e-4` **above** the kappa: this rung is not ceiling-tight the way the published ladder's rungs are |
| assembly | the unchanged 47-constraint assembly is green at that budget, and green tightly: its smallest strict constraint is `lambda - tau = budget * eta = 7.282511e-28 > 0`. Its own adjacent `10^-18` point is rejected |
| gain | `+2.2655%` over the published top of the ladder, `711599961413937/10^18 = 7.11599961413937e-4` |

**None of this is a published claim.** The row's PR is not merged, `certificate.json` still
carries the old ladder's kappa, and this file states what the rung *would* price and what it
*would* take. The contract's own `our_side.allowed_to_move` block records exactly that.

## 3. The required exports

Each export names what must be published, the form it takes, the digest or identity it must
reproduce and the obligation it unblocks. "Reproduce" means: the published body is checked
against a number the row or this package already carries -- never new trust.

| id | the program must publish | form and cardinality | what it must reproduce | unblocks |
| --- | --- | --- | --- | --- |
| **G1 assignment** | the item-to-bank/block/offset map for all `89,892` items onto `4,086` banks x `22` blocks x `3` registers, the per-bank layout of all `66` registers with none padding, the per-copy table of `1,362` banks, and a digest over the whole table | JSON, integers only, one row per item plus one row per bank | the `71cb207f…` table digest and the counts of `occurrences-rank3.json` | C1, C5 |
| **G2 normalizer** | the literal operation program of this layer in canonical order (per node: id, kind, incoming and outgoing edge ids, span) together with the map sending each item's true residual projector to the block G1 assigns | JSON, integers only; `18,532` nodes, `physical_R = 9,412`, `max_denominator = 2`, `89,892` items moved | `lift.nodes = 18,532`, `lift.physical_R = 9,412`, `lift.max_denominator = 2`, and the five `layer.audit_source_sha256` digests | C1 |
| **G3 program and columns** | the renumbered program and the formal-column checks re-run on the word after the re-assignment: every source, target and dirty-register column over F2 and over the defining integers, target chronology nested, source controls at paid-parity frames, both mutation controls rejected | JSON tables of integer addresses plus the column summary; `1,320` source, `1,320` target, `13,372` dirty per direction, `packed_digit_bits = 24` | the row's `checked_source_columns`, `checked_target_rows`, `read_counts`, `dirty_columns`, `pairs = 2,310`, `mutations` | C2, C1 |
| **G4 charts, colouring, witnesses** | exact charts (integer kernel bases, fraction-free inverses, replayed elementary factors) for every frame the new blocks use, the colouring of the `269,676` new incidences, and distinct integer Gram/prime witnesses for every one of those frames | JSON bodies per chart plus a colouring and a witness table; `89,892` charts, `269,676` incidences | `lift.max_denominator = 2`; PR205's precedent (`physical_roles = 17,114`, `swaps = 733`, `longest_swapped_path = 11`) | C3 |
| **G5 provenance** | one entry per child of the rank-3 family with its frame or chain identity, in the shape of the pinned bit-side inventory | JSON: `counts_per_vertex`, `occurrences_per_vertex`, `row_identity_per_vertex`, `source_pins`; `29,964` per vertex, `89,892` items, `4,086` banks | the row's `child_histogram[3] = 29,964`, the pinned inventory's shape, and this package's own item/bank counts and table digest | C5, C6, C7, C1 |
| **G6 envelope and integrity** | the paid moment envelope of the retained row in the form `arithmetic.py` consumes (retained stock, deficit, retained histogram, worst-case bad fraction, the convention's fallback), plus every digest of G1-G5 and the list of predicates actually run | JSON envelope plus manifest; retained stock `32,070`, deficit `3,960`, mass `2,112,660`, children `545,175`, families `19` | `occurrences-rank3.json`'s retained stock, deficit, mass and histogram digest | C4, R4 |

### 3b. The gate is executable: ten bodies, in the importer's own dialect

The contract is not a description of an interface: `importer66.py` consumes it directly.  Each
export names the **bodies** it requires -- `assignment.json` (G1), `normalizer.json` (G2),
`columns.json` (G3), `charts.index.json.gz`, `charts.json` and `incidence.json` (both published
byte-for-byte, hashed and never parsed) and `prime-witnesses.json.gz` (G4), `children.json`
(G5), `envelope.json` and `integrity.json` (G6): **ten bodies across the six exports** -- and
each gate is declared in the harness's own vocabulary (`equals`, `bijection`, `at_most`,
`flags_true`, `distinct_below`, `counted_in_tables`, `equals_in`, `declares_every_body_on`), so
there is no translation layer between the contract and the code that decides it.

```sh
cd research/complex-bank-run3
python3 -B importer66.py --contract export-contract-rank3.json             # refuses: exit 2
python3 -B importer66.py --contract export-contract-rank3.json --partial   # reports: exit 4
python3 -B importer66.py --contract export-contract-rank3.json --self-test # exit 0
```

Two of the checks are comparisons this package already holds rather than restatements: G1's bank
table must carry the `71cb207f...` table digest and the counts of `occurrences-rank3.json`
(which is what makes A2's bijection a bijection against *this package's* addressing rule), and
G5's `counts_per_vertex[3]` must be the row's own `child_histogram[3] = 29,964`, read out of the
pinned certificate rather than from the contract.

The five exit codes are the two other contracts' five, and every one of them is exercised:

| code | what it means here |
| ---: | --- |
| 0 | admissible: every body present, the gate green and the pinned replay checker passed |
| 1 | a check failed: A1 on a tampered body, or a declared bound, bijection, flag, witness, table or comparison broken |
| 2 | refusing: at least one of the ten bodies absent (the state today), or a checker supplied that the contract does not pin |
| 3 | gate green, replay NOT RUN: no checker was supplied |
| 4 | partial: the gate run on the bodies present, for reporting only; nothing is discharged |

`--self-test` builds synthetic bodies out of the contract's own declared expectations, patches
the anchored digests to the synthetic hashes -- streams included, written as they are published
-- and then breaks each declared check in turn: **thirteen cases, all passing**.  That is what
makes "the gate is executable" a measurement rather than a claim.

One gap is recorded rather than papered over.  **The row publishes no checker digest**, so there
is nothing for the harness to accept: a walk of the pinned certificate finds no key containing
`checker` anywhere, and its nearest published evidence is `layer.audit_source_sha256`, five
source digests, which is a digest *set* and not a checker.  The harness therefore reports the
replay NOT RUN when no checker is supplied (exit 3) and refuses any checker that is (exit 2),
and `check_rank3_export_contract` asserts the absence against the pinned bytes.  A green gate on
these ten bodies would still not be an *admissible* import: this rung's physics stays a stated
dependency until the row publishes a checker.

## 4. Acceptance tests

| id | test | the bound it is held to | reject control |
| --- | --- | --- | --- |
| **A1** | every body hashes to a digest the row or this package already published, and the row's audit sources are declared by digest | five `layer.audit_source_sha256` digests, `max_denominator = 2`, the `71cb207f…` table digest | any altered byte fails the hash; a matching one is evidence of identity, not correctness |
| **A2** | the assignment is a bijection with **no padding** | `89,892` items onto `4,086` banks x `22` blocks x `3` registers, all `66` registers of every bank used, `1,362` banks per copy, padding `0` | an item placed twice, a block without its item, or a bank with an unused register -- the padding ranks 16 and 20 need would fail here |
| **A3** | no other bin of the ledger moves | children `635,067 -> 545,175`, families `20 -> 19`, mass drop `269,676 = 4,086 * 66`, stock drop `4,086`, largest child `20` unchanged, histogram digest reproduced | one child of another bin moving, or a stock drop that is not the bank count |
| **A4** | the retained row re-prices the top, bit-bound | coarse `8.346506496783e-4` with the next `10^-18` point up excluded, budget = the leaf `7.282510899902e-4`, kappa `7.277211262868e-4`, `binding = bit`, tightest of the 47 constraints `7.282511e-28 = budget * eta`, adjacent grid point rejected | quoting the row's own coarse saving (`7.0991e-4`) or the row's own kappa (`6.7688e-4`), or a point whose next `10^-18` step also assembles |
| **A5** | the columns of the modified word | `1,320` source columns, `1,320` target rows, `13,372` dirty columns per direction, `packed_digit_bits = 24`, `2,310` pairs, `read_counts 22/2,310/3,135` | counts quoted from the row instead of coming out of the exported tables, or a mutation control that reports PASS |
| **A6** | the incidence colouring of the new incidences | two-colouring with a conflicting assignment rejected, at the fraction-free chart inversion; PR205 precedent `swaps 733`, `longest_swapped_path 11`, `physical_roles 17,114`; this rung's incidences `269,676` | a conflicting assignment accepted |
| **A7** | distinct integer Gram/prime witnesses for every frame the new blocks use | the retained prime threshold (PR205: all `17,114` physical roles witnessed); this rung's charts `89,892` | a repeated witness, or a residual factor above the bound |

A2 is the test this rung adds to the general form: "no padding" is not a remark about the
schedule but a property of the exported map, and a body that filled a bank by leaving a
register idle would be refused even though it is a *uniform* tiling of the sixteen-coordinate
or twenty-coordinate kind.

## 5. C1-C7 restated at this rung

The obligations themselves are `obligations.json`'s and are quoted verbatim in the contract
(`obligations_restated[*].quote` is resolved against that file by `verify.py`); what this
table adds is what each one *means here*, and what would discharge it.

| id | at this rung | exports | status |
| --- | --- | --- | --- |
| **C1** | build the `4,086` width-66 banks and the normalizer that sends each of the `89,892` items' true residual projectors to its assigned block | G1, G2, G3, G5 | `OPEN_PHYSICAL_HALF_INSTANCED_COMBINATORIAL_HALF` |
| **C2** | re-run the formal columns on the word after the rank-3 family leaves, reproducing `1,320 / 1,320 / 13,372` and the read counts | G3 | OPEN |
| **C3** | charts, colouring and witnesses for the `89,892` new blocks and their `269,676` incidences -- uniform, because rank 3 divides the width, so no padding frame is introduced | G4 | OPEN |
| **C4** | envelope parity at this rung's numbers: retained stock `32,070`, deficit `3,960`, mass `2,112,660`, children `545,175`, families `19`, histogram digest `6e825f33…`; coarse `8.346506496783e-4`, kappa bit-bound at `7.277211262868e-4` | G6 | OPEN |
| **C5** | the rank-3 family's provenance: `29,964` children per vertex, `89,892` items onto `4,086` banks x `22` blocks, each with its frame or chain identity | G5 | `INVENTORY_INSTANCED_AT_SCHEDULE_LEVEL` |
| **C6** | the retained row's next whole-bank family (rank `4`, `2,094` banks) -- which does **not** divide the width and so still owes T1's padded tiling as well as its provenance | G5 | `OPEN_NOT_THIS_RUNG` |
| **C7** | the same for the families beyond (`18`, `20`; the retained eligibility is `[4, 18, 20]`, all failing rank-divides-width) | G5 | `OPEN_NOT_THIS_RUNG` |

C6 and C7 are deliberately outside this rung's scope: absorbing rank 3 does not touch them,
and pretending otherwise would make the contract an inventory instead of a rung. The
inherited bit-side R1-R4 travel with the contract unchanged.

## 6. What the contract deliberately does not ask for

* **No internal id stability.** Only a canonical renumbering map and the bijection test A2.
* **No program text beyond canonical data.** G2 is nodes, kinds, edges and spans -- not a
  listing in the supplier's own language.
* **No sources for the row's own claims.** The importer re-runs the columns (A5) and
  re-charts the frames (A6): a boolean in `contract_checks` is a claim to reproduce.
* **No padding.** Rank 3 divides the width; A2 rejects a padding register rather than
  asking for one.
* **Nothing about the retained row's further families.** C6 and C7 are the next rung's.
* **No asymptotic interfaces.** General Clifford/tensor, uniform weighted compilation,
  restored rows, routing, paid layout, prime supply, precision/recovery and fixed tape stay
  the stated assumptions they already are -- so this contract can buy a conditional finite
  witness, never a theorem (`obligations.json -> unconditionality`).

## 7. Failure semantics, and the state today

**Today: 0 of the 6 required bodies exist** on the supplier's side, and that reading is
machine-checked rather than asserted: the author walks the vendored certificate for keys
containing `bank`, `assign` and `occurrence` and finds none, and `check_rank3_export_contract`
re-reads the same three empty lists. The import therefore fails closed: the rung stays a
scheduled target and the kappa keeps its conditional flag.

The one exception is **on this package's side of the interface**: the combinatorial half of
C1 -- the item-to-bank/block/offset assignment -- is instanced (`occurrences-rank3.json`,
digest `71cb207f…`), which is what makes G1's and G5's acceptance a bijection in both
directions rather than a count of items nobody can name.

Once the exports exist the discharge is mechanical, and ordered:

1. **A1** admits the anchored bodies, and G2's normalizer becomes a re-assignment over
   published frames -- the physical half of C1.
2. **A2** makes the assignment a bijection with no padding; **A3** closes the inventory and
   the item-to-block half of C1.
3. **A5** re-runs C2 on the modified word; **A4** closes C4 and R4; **A6** and **A7** close
   C3.

What that buys is the rung -- and it buys it on a row that is pinned to an unmerged branch,
so the honest description of this file today is *an interface and a target*, not a result.
The next lever it identifies is not the supplier: after this rung the complex branch sits
`1.06e-4` above the binding budget, so the ceiling is no longer what is being spent.  The
measurement that confirms it is `rank4rung.py` ->
[rank4-rung.json](research/complex-bank-run3/rank4-rung.json): banking the *next* family
(rank 4) is not realisable at the bank count the volume criterion prices, its T1 padding cannot
be saturated (nine slots short), the mixed tiling that does exist draws at least 22 of the
bank's 66 registers from other bins, and none of it moves κ by a single `10^-18` step -- the
coarse saving rises by `+8.89%` on the priced ledger and by `+114.8%` on the best tiled one
while κ stays `1819302815717/25*10^14`.  The lever is the bit leaf, and the same module says
exactly how much of it each further target needs.
