# PR236 source-to-receipt reconciliation claim

- Track: research consolidation; OS-random assignment seed **95** (`secrets.randbelow(100)`).
- Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- Branch: `research/seed95-pr236-independent-audit`, for WeberChen8128's fork only.
- Object: PR236 at `f825b6fdfd763f189db3aa1c02fdd5d604c85a01`; reconcile its 14-file source package with the preserved round-nine kernel evidence and the ledger's missing source-integration distinction.
- Method: exact Git/source/archive inventories, source-map and receipt dependency bindings, independent recount of recorded axiom reports, and corruption controls. No fresh Lean build or change to the selected frontier.
- Deliverable: deterministic evidence JSON, one replay command, regression controls, attribution and an explicit inventory of unavailable evidence.
- Time budget: about 30 minutes from 2026-10-13 17:28 Hong Kong time; reserve the final quarter for verification and handoff; expected finish 17:58.

Candidates considered were #210's 147 unmatched paths, #236's source-package versus published-evidence gap, and #279's 12 unmatched target-prefix paths. Seed `95 % 3 = 2` initially selected #279. The public open-PR search found #828 already reconciling exactly that change, so the scope moved to #236 before implementation. Searches for open PRs mentioning `236` found no competing source-reconciliation task; title hits for unrelated mathematical constructions are not treated as claims.

The public issue index had one open issue (#650, Discussions) and no sprint coordination issue. GitHub's API returned Forbidden, while public HTML and read-only Git fetches worked. This is therefore the local claim; no separate reservation issue was opened. PR metadata will be refreshed before handoff. No PR will be opened without the user's approval.

Attribution: James Chang (`jamesyc`) authored PR236; the maintainer's round-nine audit supplied the historical Darwin receipts and scope review. This reconciliation is prepared for WeberChen8128 with substantial OpenAI Codex assistance, under Apache-2.0.

## Result update, 2026-10-13 17:50 Hong Kong time

The pre-handoff exact search for `"PR236"` found Will Richards's open PR746 at
`ee3580bd708d82b5bdfda6a2bc3f0a34710be50e`. The initial numeric `236` search had
missed that result. Its source restoration and original-parser reconciliation
overlap the initial scope, so this contribution was narrowed to an **independent
source-command and log audit**, with a distinct directory and branch. No copy
of the original package is imported. Unlike PR746, this checker never loads
the submitted parser: it independently masks nested comments/strings, derives
the source command lists, and parses multiline recorded axiom output.

The [result and method](README.md) and [deterministic report](REPORT.json) confirm
all 3,606 source command lists, 7,253 internal dependency edges, 14,320 recorded
declarations (2,816 axiom-free), six theorem mirrors and eight scientific-input
Git identities. No disagreement was found in the pinned corpus. Missing
compiler/object bytes remain explicit limitations. All 22 focused tests pass
normally and under `-O`; the complete report also agrees in both modes.
The existing selected-record check, 549-PR reconciliation and its 14 tests pass.

Refresh confirmed upstream main, PR236 and PR746 still at the exact heads cited
above, and still no sprint coordination issue. Credit to PR746 is explicit in
the README. The user requested approval before PR creation: the result is
prepared for review, with no PR opened and no merge performed.
