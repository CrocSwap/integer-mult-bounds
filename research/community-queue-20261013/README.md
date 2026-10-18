# Queue review, 2026-10-13

This is a local review checkpoint based on main
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. It does not change the selected
result, publish an integration, or close a GitHub PR. The selected conditional
value at this base is **κ = 0.001635527380375392**.

## Frozen queue

The initial live snapshot contains **586 open PRs**, including **87 drafts**.
Comparison with the published historical ledger gives:

| Recorded coverage | Open PRs |
|---|---:|
| Outside the recorded inventory | 149 |
| Unreviewed at the recorded head | 280 |
| Partially reviewed at the recorded head | 147 |
| Already marked changed since review | 6 |
| Live head differs from the ledger | 4 |

These are coverage categories, not new approvals. In particular, partial
review does not imply complete mathematical or implementation review.
The four newly observed head changes are #226, #275, #469 and #620.
[OPEN-SNAPSHOT.json](OPEN-SNAPSHOT.json) pins the live heads;
[QUEUE-RECONCILIATION.json](QUEUE-RECONCILIATION.json) retains every comparison.
Later arrivals are outside this frozen round.

The ending refresh contains **598 open PRs**: 12 arrivals, #768–#779,
with the five priority heads #675/#695/#704/#740/#741 unchanged.
[ENDING-SNAPSHOT.json](ENDING-SNAPSHOT.json) retains this later observation.

## Completed scoped reviews

| PR | Contributor | Outcome |
|---|---|---|
| [#675](https://github.com/CrocSwap/integer-mult-bounds/pull/675) | Tekalign / tekuuu | Independent ownership-boundary audit passes; correctly distinguishes timing from scalar correctness. |
| [#695](https://github.com/CrocSwap/integer-mult-bounds/pull/695) | Joshua Snider / jsnider3 | Completed Linux evidence reconciles with the selected source and assembly; missing-payload limitations remain explicit. |
| [#704](https://github.com/CrocSwap/integer-mult-bounds/pull/704) | roife | Fixes a reproduced ledger-projection validation gap; five mutation experiments and 14 focused tests pass. |
| [#740](https://github.com/CrocSwap/integer-mult-bounds/pull/740) | Alexander Templeton / azide0x37 | Binds the archived finite-menu evidence and rejects invalid certificates under optimized Python; seven tests pass. |

All four are ready for integration within these stated scopes. Their changed
files are copied byte-for-byte from the pinned PR heads, with original
attribution retained. [REVIEWS.json](REVIEWS.json) records findings and
[SOURCE-COVERAGE.json](SOURCE-COVERAGE.json) records full changed-file coverage.
The accompanying logs are fresh reviewer executions on Python 3.12.
The combined offline reconciliation, selected-source check and whitespace
check pass. No full supplier rebuild is needed for these four changes.

#675 does not identify a failure of production admission. #704's metadata
mutations do not describe corruption of the committed ledger. #740's
assertion-disabled false PASS does not invalidate the committed historical
certificate; its documented assertion-enabled execution correctly rejects
the altered input. Preserve these distinctions when communicating the work.

## Frontier candidate

[#741](https://github.com/CrocSwap/integer-mult-bounds/pull/741), Chafik
Boukhalfa / chafreaky, claims **κ = 0.001661202643272239**, approximately
**1.57% above the selected main result**. Its own increment over #699 is
smaller: eight frame changes preserve the scalar program, endpoint frames,
helper widths and owner placement, while moving each affected pair of paid
ranks from (2,3) to (1,4). Concavity of r^(1-a), for 0<a<1, explains the
strict moment improvement with unchanged rank mass.

The new package preserves the contributions of Jeremy Kothe's construction
and read exchanges, icekylinx's gauge construction, eumemic's #589 bit
supplier, and the other contributors listed in its provenance. Reviewing
this aggregate witness does not establish complete changed-file coverage
of every predecessor PR and does not justify closing those PRs wholesale.

The audit pins #741 at `e516b1463606840a15f80aac1995d64ce0092e89`.
All 298 declared vendored source files were compared against their actual
Git objects, not just the package's self-declared hashes. The 12 admission
files were checked against the pinned #699 predecessor: 11 are byte-identical,
and the remaining assembler preserves all assertions and changes descriptive
scope text. The newer live #699 head changes only its README and manifest.

The exact-head [Linux CI run](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/38349298170)
passed on Python 3.11 and 3.14. A separate fresh Python 3.12 reviewer replay
**passed all 22 top-level stages**, reproducing the claimed value. It includes
the fresh ancestor and construction chain, both orientations on 728 columns,
2,953 phase edges, wrapper/owner/admission controls, independent literal
accounting, both moment engines and all 47 strict outer constraints.
[Review receipt](PR741-REVIEW.json), [result](PR741-RESULT.json),
[complete replay archive](pr741-fresh-replay.tar.gz). The unchanged,
already-incorporated PR589 bit supplier was repriced, not rebuilt here.
Neither replay
establishes the inherited all-size compiler, mutable-source/common-label,
complete-call hosting, precision/tape or analytic transfer hypotheses.

The late-arriving [#777](https://github.com/CrocSwap/integer-mult-bounds/pull/777)
by Tekalign independently finds the same eight changes and credits #741's
earlier publication. Its explicit 512-point subspace checker was reviewed
and executed under optimized Python against this round's freshly built
before/after words: the complete local recount and 12 controls pass.
[Scoped receipt](PR777-SCOPED-REVIEW.json). This is useful independent
verification and parallel-contribution credit. Only that checker is covered
here; the remaining PR777 files and full pipeline are not thereby approved.

## Next review batches

1. Finish #741's integration-specific source/selected-record bindings and
   dependency disposition map before changing the selected frontier.
2. Review [#681](https://github.com/CrocSwap/integer-mult-bounds/pull/681) as a
   composed circuit batch. Its claimed addition/instruction reductions are
   not new κ values. Check the changed precision allocation and full hosted
   replay before resolving its six imported research packages. #670/#674
   have only subset coverage in that proposal and must remain distinct.
3. Group the remaining audits, formalization, tooling and negative results
   by common dependencies. Keep source review, execution, incorporation and
   closure separate; preserve independent and parallel contributor credit.

The central historical ledger has not been regenerated to pretend these
local decisions are published. A publication pass must bind this evidence,
refresh each remote head and record the actual integration/closure state.
