# R439 column 7 needs five taps even with fixed-order scatter interleaving

**Scoped negative result; no new supplier or kappa.** For the frozen PR1062
R439 target-basis circuit, retained-total column 7 needs exactly **five**
scatter ADDs even when its taps may occur at any target and any cut of the
deferred undo. This is checked for the literal 306-gate order and for the
303-gate remainder of PR2115's known `{31,51,52}` split. The known split
already uses five taps for this column, so this mechanism cannot improve
it by changing this column alone.

This answers one part of the interleaving class explicitly left outside
Charles Bethin's [PR2279](https://github.com/CrocSwap/integer-mult-bounds/pull/2279).
It does not repeat that PR's all-ideal 94-ADD theorem, and it does not prove
94 is optimal when every column or the undo order may change.

## Reproduce

From the repository root, with Python 3.12. No third-party packages:

```sh
python3.12 scripts/research_package.py --package research/r439-interleaved-scatter-seed16
```

Expected: primary marker `PASS_R439_INTERLEAVED_COLUMN_FLOOR` with
`column=7 minimum=5 orders=2 dirty_columns=661 controls=12`, independent
marker `PASS_INDEPENDENT_INTERLEAVING_FLOOR`, package control marker, and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=negative-result`.

The manifest runs the primary checker normally and with `-O`, the
independent checker, and actual-entry-point corruption/relocation controls.
Checks use explicit exceptions and remain enabled under optimization.
`verify.py --write` regenerates [CERTIFICATE.json](CERTIFICATE.json).
`verify.py --output /tmp/r439-interleaving-records` also exports the two
literal record streams; this is optional and not needed for verification.

## Evidence and cost

[PROOF.md](PROOF.md) defines the exact model and gives the reduction.
All tap responses are suffix columns of the fixed undo. Exhaustive exact
two-plus-two enumeration excludes every representation with at most four
taps; five explicit taps attain the desired 111-bit response.

| fixed order | distinct tap responses | sums of up to two responses | <=4-tap representations |
|---|---:|---:|---:|
| literal 306 gates | 415 | 83,624 | 0 |
| after the known three-gate split | 412 | 82,435 | 0 |

The independently written reconstruction uses set-valued matrix rows and
forward right multiplication, rather than the primary backward column
engine. It also executes the witnesses forwards. Both check complete
values; hashes never decide mathematical equality. Independence covers
coefficient reconstruction and witness checking; the two engines share the
elementary two-plus-two coverage lemma and have the same AI-assisted author.

The primary checker embeds both witnesses in the complete word and
checks all 661 arbitrary dirty input columns in both directions through
literal COPY/ERASE. It checks every ordered MOVE, operand frame, COPY
lifetime, paid rank and positive majorant. All helpers and the single
temporary are restored. No undo gate or source access is made free.

| complete local schedule | scatter ADDs | total ADDs | COPY/ERASE | paid rank mass | guard bits |
|---|---:|---:|---:|---:|---:|
| PR1062 input | 527 | 11,500 | 9/9 | 5,129 | 95/182 |
| literal-order five-tap witness | 96 | 11,069 | 9/9 | 5,129 | 95/181 |
| ideal-order five-tap witness | 94 | 11,067 | 9/9 | 5,129 | 95/181 |

The second witness matches the known split's scalar count. This is a
lower-bound contribution, not an additional saving. Neither witness is
proposed for selected-supplier adoption. Native phase/parser replay,
whole-call hosting, all-size realization, physical precision/tapes and
outer assembly remain unexecuted or inherited. Interleaving target undo
inside a live COPY also needs explicit admission by a production parser.
Finite checks here do not verify the full multiplication theorem.

## Sources, assignment and prior work

Exact base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The selected record still gives kappa `836330098538459/500000000000000000`
and PR589 on PR555 for the bit supplier; the complex side binds.
[SOURCES.json](SOURCES.json) pins every consumed input, selected-record
provenance, task catalogue and predecessor document. The scientific input
is the committed PR1062 word, not a newer unreviewed headline.

The OS draw was **16**, bit-supplier track, selecting column `16 mod 9=7`.
Three candidate tasks, the local claim, search domain, stopping rule and
overlap coverage are recorded in [TASK.json](TASK.json). No pinned sprint
issue existed. Orientation and the first bounded test completed within the
first eight minutes. Discovery stopped on the exact obstruction; no larger
word search was launched. This is a changed scope relative to the catalogue
H2/K card: it investigates the specific deferred-target interface of
PR2115 and the interleaving question excluded by PR2279.

Credit Sagar Thakrar for PR1062, the deferred basis and attaining split
in PR2115, head `b56dceffad83c88e8ad39ffd82a1bdd55c4130da`.
Credit Charles Bethin for the all-ideal optimum and explicit open
interleaving scope in PR2279, head `81fed971e2269b62eae2ee8e3b6bda394930992c`.
The target basis is Gareth Davidson's PR915; its retained lineage includes
commdata2338, Scott Woolsey Biggart and Sagar Thakrar. The word also retains
Sricharan Vagvala's helper stars, Aaron Wang's B circuits, Ross Richardson's
frame circuit, DreamingOfClouds' PR589 tuning on eumemic's PR555, and the
semantic-interface and exporter contributions of Zhihao Chen, eumemic,
woklerx, Arham Tahir and Dylan Crow. Original files and notices are unchanged.

Prepared by **Sricharan Vagvala (@theon199)** with substantial **OpenAI Codex**
assistance in mathematics, code, verification and writing. Parent-only;
no subagents, independent human review or proof-assistant check. New work
is Apache-2.0, under the repository license.

## Open next questions

Other columns may admit cheaper interleavings. First reconstruct their
suffix-response dictionaries and compare a fully charged witness against
their existing split counts. A per-column improvement must also fit a
single chronological undo schedule with every COPY lifetime paid.

Other commuting undo orders can have different intermediate suffix columns.
Before searching all order ideals again, identify a new response vector
created by a changed order, then test that enlarged tap class. The present
floor applies to only the two stated orders. Structured questions and
blockers appear in `TASK.json`.
