# Cancelling cleanup sandwiches: argument and scope

**Setting.** This is the five-stage bit word of Dugongue's #272: frame-filtered collective kernels and target-prefix
sharing on Dugongue's #259 multi-cut kernel condensation of eumemic's #249 transported entrances. Payload arithmetic is over F2. Address geometry is over
Q with the form G = 9I − J on the 24 local coordinates; a frame is a nondegenerate subspace with projector
P = B^T (B G B^T)^{-1} B G. Every register's chain is charged per stage by its frame increments, and completed
endpoints are banked by the inherited completed-core identity (research/community-round8-audit/BANK-SCHEDULE.md).

**The sandwich.** Let c be the first kernel cut of #272's word. A helper a is selected when every gate on a after c
is one of exactly three, in this order,

    t += a,   a += b,   t += a,

and no gate strictly between the first and the third uses t as a control. No selected helper is the source or
target of another selected helper.

**Scalar identity.** Write a_0 and b_1 for the values of a and b just before the middle gate. The three gates add
a_0 + (a_0 + b_1) = b_1 to t and leave a = a_0 + b_1. Since t is not a control in between, delaying or advancing what
t receives does not change any other register. The rewrite performs a += b at c and t += b at the middle position.
It agrees with the original whenever b at c equals b_1 and a is not read between c and the middle gate. These side
conditions are not assumed: `sandwich272.py` replays all 20,107 formal columns (sources, targets and arbitrary
dirty helpers) over F2 and requires every register to end as itself and every target as itself plus its source.
Omitting either new gate makes the replay fail on 99 rows.

**Frames.** At c, a and b sit at frames S_a and S_b. The early gate runs at F = S_a + S_b, which has dimension 4 for
every selected helper and a nonsingular Gram matrix for 9I − J (checked modulo 1000003, which implies rank 4 over
Q). Every new adjacent pair of frames is checked for exact rational inclusion. The middle gate keeps its inherited
frame. After c the helper has no gate, so its chain ends at F: the inherited cleanup climb from dimension 4 to 24 is
not needed. #272's independent legality checker accepts the new word with these final frames.

**Endpoints.** Each selected helper enters at a rank-one gauge S and now ends at F with P_S P_F = P_F P_S = P_S. Its
completed relative endpoint is therefore the partial swap D_(P_F − P_S), of rank 3, on arbitrary contents, by the
same identity that #186 and BANK-SCHEDULE.md use for completed cores. Its bank residual changes from width 23 to
width 3. Over #272's 120 replicas this frees 11,880 width-23 slots: 2,970 banks [23^4, 4^7] are dissolved, their
20,790 width-4 blocks fill 693 banks [4^30], and the 11,880 width-3 residuals fill 297 banks [3^40]. Each stage has
1,980 fewer banks. #272's own bank review charges every role 24 − dim(entrance), as if each chain ended at full;
this re-tiling is the only step that accounts for the shorter chains, and `endpoints272.py` checks it exactly.
`endpoints272.py` gives every new endpoint and connector an exact chart within #259's bound of 548 elementary
factors (below #272's normalizer ceiling), with all entries below 2^80, so the inherited prime admission applies.

**Accounting.** Per helper the histogram loses two rank-21 steps and gains two rank-1 steps and one rank-20 step:
the rank mass falls by 20. With the stock falling by the same amount through the banks, the deficit is unchanged.
The new word is priced by #272's unchanged exact engine and 47-constraint assembly, which first reproduces its own
baseline. #272's finite invoice and fixed-prime refinement run on the new word and bank inventory.

**Scope.** Proved by hand: the three-gate identity above. Computer, exact: the formal F2 replay, frame
nondegeneracy and inclusions, endpoint ranks and charts, bank tiling, price and finite invoice. Every all-size
interface that #272 retains stays an assumption, and #272's inherited audits are relied on, not repeated. No claim
is made that 99 is the largest such set.
