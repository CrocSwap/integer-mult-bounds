# Overlap with the incorporated formal packages

This bounded source review was made on 2026-10-12 against upstream main
`db0e57bc7f36b5ac0fc844ad7ce1396165ee6647`. It read the
[integration review][integration], its [exact-head record][integration-record],
the [review ledger][ledger], the merged #442/#509/#516 sources, Task A/B,
and draft #528's README and endpoint theorem. It did not rebuild the other
contributors' Lean packages, rerun their Python checks, or search every open
contribution. It makes no global novelty claim.

The integration record pins #442 to
`4e16d001d505d4f21dd2bcfc44591f9be4c279bd`, #509 to
`7b9c720ecc9f483c383e7cd9c2ab81f06ee5df59`, and #516 to
`1c6b6ff9366a94e1f86a6c5d661a7df75c6ff814`. Thus the incorporated #442
construction is the exact version selected by Task B. The batch also
incorporates #484 and #520; it leaves the selected conditional #531/#523/#493
result unchanged. Incorporation does not establish a full multiplication
theorem.

## What Task B adds, and what it does not

The merged packages already prove general conjugation, physical realization,
helper endpoint, and scheduling lemmas. Task B's additional result is the
Lean verification of the embedded **19,002-instruction R747 invocation**
(#442, stage 2, replica 0, pair 0, forward), including its concrete labels,
Boolean scalar behavior, ownership, coordinate transformations, and clean
temporary guards. It uses its own replay and hosting definitions; it is
not an existing direct instantiation of `LemmaA.lemmaA_streams`.

| Obligation | Incorporated #509/#516 | Task B's selected invocation |
| --- | --- | --- |
| Labels and exact recipes | `LemmaG.Stream.conj_matrix` assumes `RecipesExact` and `WellLabelled`. #484/#509 instance checks supply emitted-word evidence outside Lean. | `SourceFramed.actual_valid`, `SourceMoveGeometry.actual_matrix_run`, and the top-level matrix-realization theorems connect the literal trace to its gauges and matrix operators in Lean. |
| Scalar endpoint | `row_unit`, `row_pair`, and `LemmaA.family_endpoint` assume the relevant scalar row. The #484 application uses Python scalar replay. | `SourceMatrix.arbitrary_dirty_payloads` proves the complete literal normalized endpoint for all 987 live Boolean-valued input streams, including all 747 dirty helpers. |
| Ownership and charts | `realize_run` assumes an injective owner map. `lemmaA_streams` derives injectivity from assumed nonempty, disjoint footprints. #516 checks concrete owners in Python. | `SourceInvocation.oldOwner_injective` and `newOwner_injective`, with `ParentOwnership` and the geometry modules, discharge the chosen original/relocated layouts. The native bridge proves the common-coordinate interpretation. |
| Other invocations and scheduling | `commute_of_disjoint`, `whole_invocation`, `defer`, and `async_window` prove abstract consequences of support, disjointness, or commutation assumptions. Concrete windows and blocks are externally checked. | The multi-host application has the singleton list `[event]`. It checks many hosts within one complete call; cross-invocation residual disjointness is vacuous. It proves no later schedule or window correctness. |
| Arbitrary dirty state | `conj_matrix`, `realize_run`, and `lemmaA_streams` already quantify over arbitrary input functions/global states under their hypotheses. The concrete #484 endpoint application requires empty private registers. | The selected live helpers and retained exterior have arbitrary, possibly correlated Boolean payloads. Its designated private temporary starts blank and is restored; the original bank outputs are returned as actual outputs. |

The source declarations behind the left column are
[`conj_matrix` and the row lemmas][lemma-g],
[`realize_run`, `family_endpoint`, and `endpoint_indep`][realize],
[`lemmaA_streams`][streams], and the
[`Schedule` support/interleaving theorems][schedule]. The merged
[instance-check descriptions][lemma-g-readme] and
[owner/window checks][lemma-a-readme] identify the external boundary.
The right column is collected in
[`SourceInvocation.lean`](../lean-multi-host-source/SourceInvocation.lean),
with the scalar endpoint in
[`SourceEndpoint.lean`](../lean-multi-host-source/SourceEndpoint.lean).

Accordingly, the proposed description that the merged results “offer no
arbitrary-workspace theorem” is too broad. They **do** have universal abstract
state theorems. Nor does Task B prove all their concrete scheduling hypotheses.
The defensible distinction is that Task B discharges the listed local
obligations in Lean for one literal word, within the stated state model.
Its coordinate geometry is parameterized by a field with `2 ≠ 0` and an
invertible cover map; the data payloads in this instance are Boolean.
Neither contribution supplies unrestricted dirty initialization of every
register kind or a complete physical-machine theorem. In particular, #509's
copy/clear event semantics directly overwrite/clear a value; Task B separately
checks its concrete COPY/ERASE legality guards.

Task B's comparison uses explicit old/new input embeddings, assigning defaults
to slots unused by a layout. It is not equality on arbitrary complete global
allocations. Source JSON parsing and extraction remain an external provenance
boundary, checked by `check_sources.py`; Lean checks the embedded literals.
The pending ranges **15..21 and 1..28 are hand-supplied** in `pendingTag`.
`tag_pending_contains` proves target-mask containment only. Nothing binds
these ranges to the source schedule. The singleton completion is visible in
[`PhysicalSourceConnection.lean`](../lean-multi-host-source/PhysicalSourceConnection.lean).
The full cover sweep, later child execution, costs, all-size compilation,
analytic transfer, and κ remain outside Task B.

## Draft #528

GitHub's read-only API check at 2026-10-12 02:33 UTC found
[#528](https://github.com/CrocSwap/integer-mult-bounds/pull/528) open and draft,
head `df5bbdbf837df908ce2324ed880141918a19db5d`, with no merge recorded.
Its `CurrentMain.PR516CompleteBankEndpoint.full_state_endpoint` combines
#516's helper endpoint and rest-independence theorems with an exact complete
state split. It is explicitly universal over the helper and **all other
physical families**, with no clean-helper or clean-rest premise.

Its [theorem][pr528-theorem] still takes owner injectivity, the actual word's
execution equality, recipes, labels, a complete helper unit row, a zero
off-diagonal helper column, and the bank-operator identification as hypotheses.
Its [README][pr528-readme] explicitly says that no selected finite witness or
physical word was newly checked. This overlaps Task A's abstract endpoint and
composition concerns. Task B supplies concrete local source evidence in a
different model, but is not yet an adapter satisfying #528's premises; its
clean temporary and common input embeddings must be respected in any such
connection. Nothing here proves the all-replica partition, sweep order, or
global boundary premises of that proposed connection.

## Toolchain and provenance

The following mismatch and effort estimate describe the pre-port review.
The current package has since passed a fresh Lean 4.21.0 build with the exact
upstream Mathlib pin; see [VALIDATION.md](VALIDATION.md). The overlap analysis
and mathematical scope remain unchanged.

The incorporated packages pin Lean **4.21.0** and Mathlib
`308445d7985027f538e281e18df29ca16ede2ba3`. Task A/B pin Lean **4.33.0**;
Task B pins Mathlib `db584cd6d46c92f209a44c0f1c829460d327499d`.
The package stays independently reproducible at its existing pins. No shared
Lake dependency or source compatibility with 4.21.0 has been established.

A port has not been attempted. An initial compatibility check could take a
few hours; a working estimate for a complete port and recorded replay is
**several focused engineering days**, plus build time. This is a planning
estimate, not a measured result. Task A has six replay modules; Task B has
52, including about 6.6 MB of local Lean source dominated by literal
certificates. Likely work includes core/Mathlib API and tactic compatibility,
kernel-reduction performance, and updating the runner's version/dependency
checks and receipts. A failed large certificate replay could materially
increase that estimate. Choosing a maintained standalone 4.33 package versus
a 4.21 port needs maintainer guidance.

PR493's [explicit inherited-assumption statement][pr493-readme] and
[NOTICE attribution through PR472][pr493-notice] establish the
PR493 → PR472 → PR442 lineage. They establish **provenance only**: the
selected R747 proof does not transfer to a PR493 invocation.

Credit remains with DaysSky for #442, DreamingOfClouds for #484/#509/#516,
James Chang (`jamesyc`) for #528 and its reused endpoint machinery, and the
predecessors named in their retained notices, including Jacob Sussman's E8
construction. This review and the local verification contribution were
prepared with substantial AI assistance.

[integration]: https://github.com/CrocSwap/integer-mult-bounds/blob/db0e57bc7f36b5ac0fc844ad7ce1396165ee6647/docs/research/community-formal-20261012-review.md
[integration-record]: https://github.com/CrocSwap/integer-mult-bounds/blob/db0e57bc7f36b5ac0fc844ad7ce1396165ee6647/docs/research/community-formal-20261012-integration.json
[ledger]: https://github.com/CrocSwap/integer-mult-bounds/blob/db0e57bc7f36b5ac0fc844ad7ce1396165ee6647/docs/research/pr-ledger.md
[lemma-g]: https://github.com/CrocSwap/integer-mult-bounds/blob/db0e57bc7f36b5ac0fc844ad7ce1396165ee6647/research/e8-lemma-g-lean/LemmaG/Stream.lean#L294
[realize]: https://github.com/CrocSwap/integer-mult-bounds/blob/db0e57bc7f36b5ac0fc844ad7ce1396165ee6647/research/e8-lemma-a-lean/LemmaA/Realize.lean#L70
[streams]: https://github.com/CrocSwap/integer-mult-bounds/blob/db0e57bc7f36b5ac0fc844ad7ce1396165ee6647/research/e8-lemma-a-lean/LemmaA/Streams.lean#L62
[schedule]: https://github.com/CrocSwap/integer-mult-bounds/blob/db0e57bc7f36b5ac0fc844ad7ce1396165ee6647/research/e8-lemma-a-lean/LemmaA/Schedule.lean#L40
[lemma-g-readme]: https://github.com/CrocSwap/integer-mult-bounds/blob/db0e57bc7f36b5ac0fc844ad7ce1396165ee6647/research/e8-lemma-g-lean/README.md
[lemma-a-readme]: https://github.com/CrocSwap/integer-mult-bounds/blob/db0e57bc7f36b5ac0fc844ad7ce1396165ee6647/research/e8-lemma-a-lean/README.md
[pr528-theorem]: https://github.com/CrocSwap/integer-mult-bounds/blob/df5bbdbf837df908ce2324ed880141918a19db5d/research/lean-complete-bank-endpoint/PR516CompleteBankEndpoint.lean#L48
[pr528-readme]: https://github.com/CrocSwap/integer-mult-bounds/blob/df5bbdbf837df908ce2324ed880141918a19db5d/research/lean-complete-bank-endpoint/README.md
[pr493-readme]: https://github.com/CrocSwap/integer-mult-bounds/blob/c3a9a436b84fe44fdc223a5784d84736d1c2d3c7/research/e8-bit-carrier-skeleton/README.md#L147
[pr493-notice]: https://github.com/CrocSwap/integer-mult-bounds/blob/c3a9a436b84fe44fdc223a5784d84736d1c2d3c7/research/e8-bit-carrier-skeleton/NOTICE.md#L42
