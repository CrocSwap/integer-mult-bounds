# Local sprint claim

- Track: complex supplier; assignment seed **31**, drawn once with Python
  `secrets.randbelow(100)` (operating-system randomness).
- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Selected result at this base: #626/#622/#623 with #543,
  `kappa = 51110230636731/31250000000000000`. Pending PR titles do not
  supersede that record.
- Object: the selected JP8 canonical word's final scalar cleanup. Odd seed
  selects JP8 rather than CK; no search over alternative suppliers.
- Hypothesis: commuting elementary additions can be fused or cancelled in
  the fixed final cleanup without changing its arbitrary-dirt linear map,
  recursive profile, helpers, source-access interface, or frame boundaries.
- Method: exact rational commutation identities, deterministic bounded
  rewriting, full-column replay in both orientations, primitive-cost and
  prefix-envelope checks, and controls that break dependency or restoration.
- Deliverable: one standalone finite circuit result (or an explicitly scoped
  negative result), pinned inputs, executable checker, and exact evidence.
  No new kappa is promised.
- Expected finish: 2026-10-13 14:05 Asia/Seoul (05:05 UTC). Implementation
  stops by 13:55 for verification and handoff.

Three narrow candidates were considered:

1. Fixed-boundary B-phase frame optimization: declined because #698 already
   exhausts the selected CK case; repeating the same method on a different
   seed is insufficient novelty.
2. Raw coordinate-total factory resynthesis: declined because #681 already
   supplies a verified finite local rewrite of that mechanism.
3. Selected JP8 final cleanup compaction: chosen. This changes scalar-word
   dependencies in the restored cleanup, unlike #696's unchanged-macro
   primitive lowering and #681's raw factory synthesis. Existing gate-move
   and cold-end work is predecessor work, not claimed as new here.

The central review ledger, selected construction/review, open PR bodies
(including #651, #679, #681, #683, #687, #696, #698), and open issues were
inspected. GitHub's pinned-issues query returned no entries; the sole open
issue was #650, concerning Discussions. No reservation issue was opened.
The claim is therefore recorded locally. Scope is restricted to this file
family; any delegated review must stay within it.

Contributor: @ellipsi2, with substantial OpenAI Codex assistance in research,
implementation, mathematical checks, and writing. Apache-2.0.

## Experiment update

The complete initial scan found no same-edge addition before its first
noncommuting obstruction. The one evidence-driven pivot stays within the same
JP8 final cleanup: share the existing coefficient-work stream across contiguous
non-unit, equal-magnitude, common-source additions. The scalar word itself stays
unchanged. The new fanout block clears work at its boundary rather than after
each original scalar macro. The favorable budget was 999 forward blocks and
19,688 fewer real-component primitives; the exact finite checker confirms this.
The backward scan has zero eligible blocks. No kappa or global admission claim
is made. The completed search and verification are described in README.md.

## Completed result and handoff

The finite circuit contribution is complete: 999 forward blocks save 19,688
real-component primitives, with unchanged exact dirty-register endpoints and
prefix envelopes in both orientations. See the [result and command](README.md),
[exact certificate](EXPECTED.json), and [validation record](VALIDATION.md).

The final full-queue overlap refresh inspected 536 open PRs through #717.
#696 remains the closest related contribution, with a distinct individual-macro
lowering. New #708 and #710 concern F2 bit circuits, and #717 records format
limits; none supplies this JP8 shared-coefficient block. No pending patch is
imported. A refreshed fetch still resolves main to the exact original base.
No pinned coordination issue exists, so this completed claim stays local.

Submitted: [PR #722](https://github.com/CrocSwap/integer-mult-bounds/pull/722),
as a research note / finite circuit improvement. The immediate pre-submission
refresh reached #721; #719's CK scalar-cleanup obstruction is compatible with
this distinct JP8 primitive-lowering result and is credited in the PR.
