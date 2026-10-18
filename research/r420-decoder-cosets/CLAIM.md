# Sprint claim

- Track: bit supplier; OS `secrets.randbelow(100)` assignment seed **3**.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60` (origin/main).
- Started: 2026-10-13 04:52 UTC; expected finish: 05:25 UTC.
- No pinned coordination issue (GitHub GraphQL pinnedIssues returned empty).
- Three candidates: resynthesize a phase-A quad; change decoder-total source
  representations using the dead-register kernel; shorten full-frame cleanup.
  Quad synthesis overlaps #691; cleanup overlaps #710. Choose decoder cosets.
- Exact scope: the nine FULL-frame decoder totals in #543 R420. Enumerate
  source-null dependencies among available dead-register values and use a
  bounded seed-3 greedy descent to reduce the **complete** binary XOR count,
  including changed frame-zero dirty compensation and literal cleanup.
- Unlike #708, permit the helper-dirt operator to change and recompute D;
  do not import its restored operand-pair sharing. No paid-moment or kappa
  improvement is assumed. Stop if the complete optimistic cost does not help.
- Deliverable: frozen replacement recipe, exact dirty-column verification,
  negative controls, cost evidence and a scoped research construction or
  negative result. Selected frontier and upstream remain unchanged.
- Reviewed selected certificate, #626 review/construction dependencies, review
  ledger, #543 construction/family limitations and open PR metadata through
  #725. #711/#718 address scheduling, not decoder source cosets.

## Completed handoff

[PR #748](https://github.com/CrocSwap/integer-mult-bounds/pull/748): one
index-3 decoder source-coset replacement saves 244 complete local binary XORs,
including changed D and literal C. All 660 columns, original frame/interface
checks, native counts/bounds and six rejection controls pass; no new κ.
Search stopped at 32 trials / 2,997 scored candidates, five accepted moves.
The final portion was reserved for exact verification, clean archive replay,
source/optimized-mode controls, independent static AI review and handoff.
Final overlap refreshed through #747, including distinct #731/#733/#742 work.
No selected-frontier or upstream changes. See README and VALIDATION for limits.
