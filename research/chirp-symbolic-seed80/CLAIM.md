# Local sprint claim

- Track: independent verification or formalization; OS-random assignment seed **80** (`secrets.randbelow(100)`).
- Base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
- Scope: PR479 `ChirpStream.advance` at `40dd01058439cdffae3e3b41c4fe52edaccf5f91`: exact modular quadratic invariant, carry/reset state, lexicographic transition and complete-period restoration.
- Method: execute the pinned transition on independently implemented symbolic integer polynomials; certify coefficient identities under explicit branch guards, then check exact finite transitions and fault witnesses. No numerical exponential, full tape implementation, or new kappa claim.
- Deliverable: standalone source-bound checker, exact deterministic certificate, rejecting controls and a short proof/scope note.
- Expected finish: 2026-10-14 01:32 Australia/Melbourne (2026-10-13 14:32 UTC). Forty-minute working allocation; final ten minutes reserved for verification and handoff.

## Selection and coordination

The three narrow candidates were (0) a weighted cyclic-inverse identity, (1) the PR524 carry-filter invariant, and (2) the PR479 streamed-chirp transition. `80 % 3 = 2` selects the third after overlap screening. The first has extensive pending exact checks (#692, #804, #820 and related work). The second directly overlaps #918, including singleton-axis cases. The third has a numerical exact replay in its own package but no independent symbolic transition check located in the open-PR inventory.

The fetched selected record names conditional kappa `1661957774647029/10^18` and PR890. Its actual T21 construction and maintainer review were read; that result and its suppliers are outside this claim. CONTRIBUTING.md, current-status.md, the review ledger and archived negative-search scopes were inspected. The ledger lists PR479 as unreviewed at the same head, not an accepted supplier.

The GitHub pinned-issue query returned no pinned issues. The two open issues (#650 and #913) are not sprint claim threads, so no reservation issue/comment was created. The initial inventory contained 714 open PRs; a latest-25 refresh was performed immediately before this local claim. #684 concerns the Gaussian block domain, #940 Fourier source layouts, and #918 the different carry-filter packing. No overlapping symbolic PR479 check was found. No delegated workers are used.

## Completed result

Independent symbolic verification passed: 27 carry patterns and 587 state equalities, corroborated by 8,605 small-state transitions, 21 wide transitions, 16 rejecting controls and two equivalent rewrites. No source defect, new supplier or new kappa is claimed. The complete receipt, proof scope and commands are in README.md and VALIDATION.md.

Reviewable contribution: [research/independent-seed80](https://github.com/RossRichardson/integer-mult-bounds/tree/research/independent-seed80/research/chirp-symbolic-seed80). The submitted PR URL is recorded in the external handoff.

The 14:09 UTC full-queue refresh contained 717 open PRs through #946. PR479 was still at its pinned head. Related #684 and #940 examine Gaussian block-domain and Fourier-layout obligations; #481 consumes the streamed-phase accounting without independently checking its transition. No competing symbolic transition check was found. The subsequent main integration adds other circuit and verification packages; it does not touch this target or change the selected kappa. No pinned sprint issue exists, so this is the single local claim-result update.
