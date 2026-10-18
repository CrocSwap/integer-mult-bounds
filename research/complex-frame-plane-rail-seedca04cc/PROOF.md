# Finite closure and ceiling argument

## Claim

For the pinned selected PR1094 local word, the 36 coordinate subspaces `P = span(e_i,e_j)` and each eligible helper-helper A/B gate have been exhaustively considered as a one-time plane injection followed by least common-frame propagation. Among closures preserving the original exact A/B target-level and centre-frame interfaces and all final endpoints, the best paid profile has exactly the selected baseline profile. Thus this mechanism, in this finite domain and under the fixed-template model, gives no ceiling improvement, in particular not the catalogue's required 5% improvement.

The claim is about this word and this family of frame schedules only.

## Least closure and cost

The replay constructs an ordered list of events from the selected word. It includes scalar gates in A and B, then inserts the exact target-level and centre-frame constraints at their A/B boundary, followed by cleanup events and every final target or helper endpoint. Each event records its original output frame `F` and the incoming frames of its participating registers.

After injecting `P` at a selected helper-helper gate, any later gate reached by an active register must place both gate operands in a common output frame that contains the original `F` and `P`. The least such frame is `span(F,P)`. The enumerator assigns exactly that frame, updates both participants, and keeps propagation active precisely when the augmented output still has a new dimension beyond `F`. If a target-level, centre-frame, or final endpoint does not already contain `P`, the schedule is rejected. This is a direct monotone event replay: it neither skips an induced climb nor adds a frame dimension not forced by the seeded plane and gate.

At each changed event, the script replaces the original per-register climb ranks by the exact new ranks `dim(span(F,P)) - dim(incoming_frame)`, including both gate operands. The original chain profile is decomposed into these gate/interface/endpoint climbs and a checked fixed remainder of eight rank-8 units. The new chain profile is added back to that fixed remainder. It verifies that total paid rank mass is conserved when the same exact endpoints are retained.

## Exhaustion and controls

There are `binom(9,2)=36` coordinate planes and 2,525 eligible helper-helper additions in A/B, so the enumerated domain has 90,900 plane/gate pairs. There are 90,331 non-noop pairs. Of these, 89,737 violate an exact internal interface or final endpoint; 56,830 of the rejections occur at an internal target-level or centre-frame barrier. The remaining 594 closures are priced. They realize 13 distinct profiles. A saved negative-control witness injects `[1,2]` at event 0 and reaches register 60's exact centre frame at event 3563, which does not contain `[1,2]`; this pair must be rejected.

The profile search uses the exact interval arithmetic in pinned `complex-local-word-ceiling/ceiling.py` for the 5%-above-baseline gate and for each surviving profile's ceiling. The floating bisection in `search.py` only chooses which closure to serialize; the exact ceiling intervals over all 13 profiles independently certify that the selected profile is the maximum and strictly separate it from the other 12. The best profile is the original profile, and its exact ceiling bracket equals the exact baseline bracket. Its lower endpoint is `1690054109/10^12`; the largest other-profile upper endpoint is `1690012017/10^12`, leaving a strict gap of `42092/10^12`.

## Independent native check

`BEST-WORD.json.gz` serializes the best closure while retaining the selected scalar program. The pinned `gauge44-slots/independent/audit_local.py` independently checks the exact scalar map in both orientations, all literal frame chains, centre levels, dyadic units, entrance-zero response, wrapper exclusion, and final helper row/column cones. Its receipt records the same paid profile and selected dimensions. The verifier also changes the candidate's claimed rank-1 paid count by one and requires the native auditor to reject it with `paid profile mismatch`.

This native audit is local evidence for the candidate. It is not global owner admission, full supplier reproving, or an exponent reprice. The no-improvement conclusion follows only from the bounded exact profile enumeration and the pinned fixed-template ceiling model.
