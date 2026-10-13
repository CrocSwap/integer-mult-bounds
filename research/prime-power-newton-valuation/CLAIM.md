# Sprint claim and implementation plan

- Track: independent verification; OS-random assignment seed **80**.
- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Branch: `research/seed80-independent-verification`.
- Claimed at 2026-10-13 05:40 UTC; expected finish by 06:15 UTC.
- Object: the coefficient valuations and lower Newton polygon of PR621's
  integral prime-power kernel, not a proposed multiplication construction.
- Method: build tail products in the integer cyclic group ring, reduce in the
  cyclotomic power basis, substitute `u=1-pi`, and extract the ramified valuation.
  Compare with the independent tail-sum formula and a convex-hull computation.
- Domain: every primitive embedding at orders 3, 5, 7 and every repeated
  prime power through `seed+1=81`: 4, 8, 9, 16, 25, 27, 32, 49, 64, 81.
- Deliverable: one standard-library verifier, exact deterministic receipt,
  tests, scoped mathematical note, source pins and handoff. No new kappa.
- Stop after the complete fixed domain, or report the first discrepant exact
  coefficient. No adaptive search or extra computation on a closed search.

## Selection and coordination

Three candidates were inspected: (1) R420 compensation algebra, already covered
by open #731/#737/#760/#762; (2) prime-power resultant replay, already covered by
#668 and composite extensions #666; (3) ramified coefficient valuations and
Newton polygons for #621. Candidate 3 changes the proof obligation and arithmetic
method, rather than merely using a new seed. The open-PR inventory and primary
package contain no Newton-polygon or p-adic-valuation contribution at selection.
The pinned-issue GraphQL query returned no issues, so this is a local claim.
No separate reservation issue was opened.

Selected status was followed from `certificates/selected-result.json` to
`research/community-k492-audit/pr626/replay/ASSEMBLY.json`, its source manifest,
the #626 construction README and maintainer review. The accepted conditional
value is `51110230636731/31250000000000000`, not the pending PR-title values.

## Implementation plan

Goal: independently check exact valuations before deriving any conclusion.
Architecture: a standalone integer engine and rational convex hull; no imports
from the predecessor's field, determinant, inverse or SymPy implementations.
Tech stack: Python 3.11+ standard library. Scope and design are the claim above.

1. Write tests with hand-calculated radix-4 coefficients and radix-8/27 hulls,
   plus nonprimitive/composite and altered-coefficient controls; observe failure.
2. Implement `tail_coefficients(r, power)`, `coefficient_valuation(c, p, a)` and
   `lower_hull(values)`; compare exact expansion against the tail-sum formula.
3. Replay the fixed domain, recording every primitive power and a digest of
   every reconstructed coefficient. Add controls that preserve the old mod-ideal
   zero/nonzero pattern while changing the stronger valuation obligation.
4. A single scoped background worker checks the uniform mathematical argument
   and writes only `PROOF.md`; it does not change the implementation or scope.
5. Reserve the final ten minutes for fresh normal/optimized replay, predecessor
   checks, receipt-mutation failure, source integrity and overlap refresh.
6. Submit at most one independent-verification/research-note PR, with exact
   attribution, AI disclosure and unresolved obligations. Do not alter upstream
   or the selected record.

## Final result and handoff (one claim update)

Completed 2026-10-13 at approximately 06:00 UTC, with the final verification
and handoff phase beginning at 05:51 UTC. Submitted one focused contribution:
[PR804](https://github.com/CrocSwap/integer-mult-bounds/pull/804).

The fixed domain completed: 214 primitive embeddings, 10,268 exact coefficient
valuations, two valuation extractors and eight rejecting controls. Nine focused
tests pass on installed Python 3.12.14 and 3.14.7. The unchanged #621 replay
matches its full published receipt; selected-record/source integrity passes.

The submission refresh discovered Hao Yan's concurrent #796, posted at
05:47:56 UTC, with the same formula and weighted-minimum extraction. The
handoff was therefore narrowed to distinct repeated integral-divisibility
evidence and radix-81 coverage, not priority for the shared theorem. Its pinned
receipt agrees on 160 shared embeddings and 5,894 coefficients, with all shared
hulls and root multiplicities identical. Radix 81 adds 54 embeddings and 4,374
coefficients. The final metadata refresh retained #796 head
`22902155c7875139e43e4fdf15723142d6709bdd`; #800's Clifford path-valuation work
is a different object. Exact comparison pins are in `CORROBORATION.json`.

No kappa change, full repository-suite pass, Linux/CI result, paid inverse,
proof-assistant formalization or independent human review is claimed.
`VALIDATION.md` supplies the commands, scope and remaining obligations.
