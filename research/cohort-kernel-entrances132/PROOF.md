# Cancelling dirty responses with a change of basis

2026-10-09 research result. Pure mathematics and exact native finite checks; no Lean certification or publication.

## Universal sufficient rewrite

Let a legal linear helper word act on arbitrary preserved sources, targets and independent dirty helpers. At a cut, select untouched helpers p,i1,...,ik with zero initial frames, full final frames, and first subsequent required frames F_p,F_i. Let R_j denote helper j's propagated initial dirty response in target coordinates at that cut. Require the response outside those targets and the helper's own coordinate to be zero. Suppose, in the actual payload coefficient ring,

    R_p + sum_j c_j R_ij = 0.

Choose an explicitly constructed nondegenerate address frame E contained in every F_j. The following is a sufficient complete rewrite:

- Start helper p at E and omit its original zero-frame initial dirty-correction reads.
- At the cut raise each other selected helper to E, execute helper i_j += c_j helper p, then resume the old word with its actual subsequent frames.
- At the common full final helper frame execute helper i_j -= c_j helper p.
- Preserve and charge every old surviving gate, each added move, every basis gate and its inverse, all copied centers and all outer boundary work.

The elementary basis is Q=I+sum_j c_j e_ij e_p^T. Its off-diagonal part squares to zero, so Q inverse is I-sum_j c_j e_ij e_p^T. Relative to logical input d=Qz, the omitted prefix target response is exactly the displayed zero vector. After Q is installed every logical row therefore agrees with the original word at the cut. The old word gives the unchanged data result and ends with Qz; Q inverse restores z. At each physical frame J, the row invariant is stored row=C_J(logical row). Every new pointwise basis gate has one common frame, and each actual connector realizes C_K C_J inverse along a nested path. Thus arbitrary physical dirt and source restoration are covered; no clean scratch is used.

For e=dim(E), r_j=dim(F_j), the exact raw recursive-child delta is

    -sum_j [r_j] + [r_p-e] + sum_(j != p) ([e]+[r_j-e]),

where [0] contributes no call. Raw rank mass falls by e. No target-path split is introduced because the response is zero. Scalar costs are 2k new basis shears minus the explicitly omitted old reads. After a completed entrance-bank construction the associated stock reduction is e/m per normalized invocation; this last step must be built, not inferred from the rank sum.

## Actual two-helper instance on PR249

The payload is F2. The actual prefix contains 132 disjoint pairs with identical complete target response columns. Each common entrance is the line through a four-coordinate integral vector u with entries +/-1, sum(u)=0, and u^T u=4. Both old first frames have dimension3; E has dimension1. The replacement per pair has raw delta [1]+2[2]-2[3]. Each pair deletes four old initial reads and adds Q and Q inverse: net two scalar gates removed. Across132 pairs:

- Raw histogram delta: rank1 +132, rank2 +264, rank3 -264.
- Raw rank mass434177 ->434045.
- Actual scalar ADD count786623 ->786359.
- All physical helper identities, sources and targets retained.
- No target frame changes or target reads added.

The full current249 rewrite is lead/COHORT249-RECORDS.bin. It passes all20107 independent scalar columns forward and backward, and independent actual chronological/frame/COPY checks. The independent prefix audit verifies232320 pair/target response equalities directly from the original pinned word. The proof of the actual132 pairs is over F2, not over Z; the earlier small signed integer example has separate scope.

## Completed banks and exact exponent

BANK-PROOF.md supplies the actual new projector charts, full bank assignment, distinct normalizers, complete GL-cover routes and endpoint controls. Every new projector has chart determinant +/-4 and a two-sided inverse with denominators dividing4. The maximum new chart factor count30 is below the old548 ceiling.

Per stage, replace1056 pure rank24 banks and308 pure rank4 banks by1320 banks each carrying four rank23 and seven rank4 blocks. All3317400 role/replica/stage assignments are explicitly checked. Literal stock869415 ->869195 over40 replicas and5 stages. The old787 normalizer ceiling still applies, with the new full selector bill626938189600.

New rank1 entrances also add132 rank5 COMPLETION children before bank discharge. Completion counts must be subtracted from the rank5 bucket; deleting the entire bucket would incorrectly remove ordinary rank5 children. The native price uses the independently rebuilt retained histogram directly and avoids this error.

The normalized complete retained profile is m120, W173839, calls3935080, rank mass20825480, deficit35200. The inherited rare-class fallback is included. Exact directed rational bounds prove the coarse saving71097032054791/10^17; the next10^-18 grid point fails. Three finite ordinary iterations from384599/10^10, retained complex saving747454944651775/10^18, eta10^-12 and beta10^-9 give

    kappa = 71046520063283 / 10^17
          = 0.00071046520063283.

All47 strict assembly inequalities pass; the adjacent10^-18 kappa point fails. The same independent native price reproduces PR249's published baseline exactly. The finite/global proof and computed prefix/primitive bounds are FINITE-PROOF.md and its receipts.

This is a finite construction and a mathematical composition under the retained public all-size compiler, common weighted chart, restored-row, routing, prime, precision/recovery and analytic interfaces. It is not an unconditional multiplication theorem, a practical multiplier benchmark, or a Lean/kernel certificate. The public Python eight-stage command was not rerun verbatim on a modified package; the new word, physical frames, actual charts and assignments, five-stage endpoints, prefix bills, recurrence price and outer inequalities were checked by the saved native tools and independent lanes.
