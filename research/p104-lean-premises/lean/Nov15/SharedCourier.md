# SharedCourier.lean: shared-snapshot courier (GB1 section 3). No sorry, ~10 s, 2.9 GB peak. Axioms: [propext, Classical.choice, Quot.sound] (tc_cleanup: [propext, Quot.sound])
Source: internal notes Reuses TokenCancel (events, `run`, `Legal`, XCLOSE shape) and FibreK (`Helper`, `gap`, d0 table); Delivery is not built in this tree, so `courierD0` is restated (same formula as Delivery.courierD0 / FibreK.d0_native).

**Model.** A give = (consumer, coefficient, stop chart). Shared courier y: `born y cp`, `add y p 1 cp` (pick up row p once), then per give `move y g; add consumer y a g`. Separate plan: one courier per give (`seg`: born, pick, move, deliver, clear).

**(1) Exactness.**
- `shared_row`: every register r != y ends with `row r + cf G r • (row p + e_y)`, `cf G r` = total coefficient given to r.
- `sep_row`: for the separate plan every non-courier r ends with `row r + cf G r • row p + tokSep` (one token e_{y_j} per give).
- `exact_mod_tokens`: same plan (`G = L.map snd`): shared row - cf•e_y = separate row - tokSep, i.e. identical `row r + cf • row p`.
- `tc_cleanup`: TC. A consumer holding `tau + k•e_y` and a token holder x (row e_y) at the same chart: ONE ADD of -k gives exactly tau, and -k is the only such coefficient (hand-proved instance of XCLOSE).
- Hypotheses (scope): p is not a consumer and not a courier, consumers are never couriers, couriers distinct, and the snapshot row p is constant during the chain (all gives see the same content). Both plans are exact only modulo tokens; the shared plan leaves ONE token per consumer (cf•e_y), the separate plan one per give; cleanup needs a token holder co-present with the consumer. The courier's own row is garbage until cleared (not modelled for the shared plan).

**(3) Legality.**
- `legal_tail_iff`: the chain is Legal iff `okTail`: each consumer present at its stop chart, no stop at z, and every stop except the last is not V (a MOVE never leaves V).
- `legal_shared_iff`: the whole shared plan is Legal iff y is fresh, p is at cp, and `okTail` (relative to the location map with y at cp).
- Ascent is NOT visible to `Legal` (`legal_blind_to_order`: swapping two stops keeps Legality); `Ascending` (IsChain ≤ on cp :: stops) is an extra frame-order constraint to impose separately (Delivery section 3, time order).

**(2) Cost under Theorem K (D0 table).** D0 of a courier = f(e-b) - sum f(hop gap), f(r) = r ln r (`courierD0_gaps`; order-free by `courierD0_perm`, so the beta side G-chain -> F -> V is priced the same).
- Shared: hops a0 (pickup), a_0..a_k (k gives, last hop to V). `sharedCost a0 k a = f(a0+R) - f(a0) - sum f(a_i)`, R = P_{k+1}.
- k separate couriers (3 hops each: a0, P_j, R-P_j): `sepCost a0 k a = sum_j [f(a0+R) - f(a0) - f(P_j) - f(R-P_j)]`.
- `diff_formula`: sep - shared = (k-1)(f(a0+R) - f(a0)) - sum_j [f(P_j)+f(R-P_j)] + sum f(a_i), exact.
- `split_ineq` (convexity of x ln x, two-point majorisation `maj`): sum_j [f(P_j)+f(R-P_j)] <= (k-1) f(R) + sum f(a_i).
- `shared_le_sep` (k >= 1): shared <= separate. `shared_eq_sep_one`: equality at k = 1 (MINCH = 2 in GB1 is exactly this). `shared_lt_sep` (k >= 2, a0 >= 1, R >= 1): strict. `saving_ge`: saving >= (k-1)(f(a0+R) - f(a0) - f(R)) > 0.
- `example_k2`: a0 = 1, gaps 1,1,1: shared 8 ln 2 vs two separate 12 ln 2.
- Condition for the shared courier to be cheaper: k >= 2 consumers on the chain and nondegenerate gaps; no other condition on the stop positions (the sum over cost is always <=). The D0 per helper goes UP (more stops) while the helper COUNT drops k -> 1; GB1's 9,003 -> 7,387 helpers and D0 58,591 -> 49,185 are consistent in sign.
- Scope: same endpoints (birth 0, end V), same pickup hop, ascending hops (gap = difference), P0 = D0 table. Not covered: the helper-count term of Theorem K beyond D0 (pi multiset is shared by construction), real tariff r6 routing.

No statement of GB1 section 3 found false. (Not proved here: the Z[1/30] / rank / V-mix claims of the pipeline.)
