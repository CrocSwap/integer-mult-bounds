# Opposite owned routes require both directions under the fixed interface

## Boundary and claim

Use exact [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) with the signed [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113), as pinned in `PROVENANCE.json`. Clocks are zero-based and cuts precede the named clock. The nested charts 549 and 559 differ by one rank. The old owned1549 goes 549→559 at MOVE40538. Old owned1527 goes 559→549 at MOVE40556. The interval starts immediately before MOVE40536 and ends after ADD40559.

At the initial cut the complete left bank has 12 roles `[111,121,173,235,752,881,891,937,999,1501,1522,1549]` and the right bank has only the zero-initialized owned1527. Three unchanged ingress values reach the right chart on public moves, 613 at MOVE40536, 611 at MOVE40546 and 1279 at MOVE40548. Those values, their clocks and all outside behavior are held fixed. There are no other boundary MOVE positions through ADD40559. The replacement may use arbitrary exact within-side operations and either one unidirectional transfer in the stated interval or none. It has no other route into either side and must preserve the old first outward reads. In particular, locally created scratch can depend only on the admitted inputs to that side.

## Exact separation

Write `u` for old1549 at the initial cut and `c,l,d` for the three ingress values. The old right observer 613 after ADD40539 equals `c+u`. The old left observer 173 after ADD40557 equals its initial value plus `c−l/3−2d`. This follows by the literal two ADDs into 1527 and the intervening SCALE/ADD operations. Both old observers must be reproduced independently of how an implementation chooses to use the one direction.

- Retain 549→559. On public input `x1=1` and all others zero, the entire initial left bank equals zero, matching the all-zero input. The old right ingress at MOVE40536 equals `1/2`; old173 after ADD40557 equals `1/2`. On all-zero input it is zero. The proposed left computation receives no input from the right and cannot distinguish the two cases.
- Retain 559→549. On public input `x1=1, x18=−1/2, x142=1` and all others zero, the entire initial right bank and all three fixed ingress values equal zero, matching the all-zero input. Old1549 at the left entrance is `1/2`; old613 after ADD40539 is `1/2`. The proposed right computation receives no input from the left and cannot distinguish the two cases.

The reverse solver derives the separators from exact normalized coefficient rows. The independent literal forward runner checks the exact probes, the intervening scalar identities, the full observed bank and ingress values, unchanged owner lifetimes, and 67 INIT and one COPY guard per trace. Each omit-ADD mutation erases the affected observer's response while preserving the initial banks and ingresses. The proof compares global legal public inputs, so it does not assume the old local rows are independently assignable.

## Price and limits

The exact caller has 17 native copies. Keeping either original rank-one route and removing the other would save at most `17 H_1 = 17` from the binding raw signed moment, with productive ranks fixed. Any extra rank-one call in each copy consumes that gross. Neither retained direction meets the required old outputs even before ordinary, routing, ownership, precision and tape costs. No constructed edit or κ gain follows.

Changed external ingress values, new earlier encodings, different routes and interface changes remain open. This is a fixed-boundary arbitrary-input exclusion. It does not assert a lower bound for replacing the pair under other contracts.
