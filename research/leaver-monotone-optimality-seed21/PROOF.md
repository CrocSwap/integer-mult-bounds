# A sharp positive-lift obstruction for the eight mutable-leaver cells

Fix one of the eight committed `CORE-*.json` files. The twelve registers have arbitrary initial values and are named x0,...,x5,y0,...,y5. Let M be the exact matrix produced by its `unit` list, acting on column vectors of register contents. The allowed competitor is any finite sequence of elementary additions r_i <- r_i+r_j, i != j, on precisely these twelve registers, with complete endpoint M. No temporary register, subtraction, scaling, or zero initialization is allowed.

**Theorem.** Every such competitor has at least 21 additions. The committed 21-addition word attains the bound. This holds separately for all eight files. For each file the `scaled` list is a fixed diagonal conjugate of its unit word, so the same bound holds for competitors whose gates are exactly the corresponding conjugates of unit positive additions.

## 1. Binary endpoints force the gate classes

Every coefficient in M is zero or one. Every coefficient in every intermediate row is a nonnegative integer, can only increase, and retains its initial diagonal one. Consequently an intermediate coefficient cannot exceed its final coefficient. In particular, if register j is added to i, the final row i must contain the initial variable j.

Direct exact replay gives the following structure in every core. The six x registers form three disjoint ordered pairs (a,b): the final row of a is a+b, and b is unchanged. The six y registers form three disjoint donor/recipient pairs (s,t): row t contains the initial y_s as well as its own y_t; row s contains only its own initial y_s among all y variables. All other cross-y coefficients vanish. Each y row has five of the six x variables.

These facts force exactly three x<-x additions, one a<-a+b for each source pair, and exactly three y<-y additions, one t<-t+s for each target pair. There can be no y<-x interpretation reversal: x cannot receive y dirt, and an x source cannot cross its prescribed source pair. Each forced gate occurs once, since repetition would produce a coefficient at least two. All other gates are y<-x additions. This classification applies to every length, not merely words close to the supplied order.

## 2. Five source-to-target additions per source pair

Fix a source pair (a,b), where a is the mutable source. Project all six y rows onto these two initial coordinates and encode {a}, {b}, {a,b} by 1,2,3. In every core, the three donor/recipient pairs have final types

    (donor,recipient) = (3,2), (3,3), (1,3).

The verification checks this directly for all 8*3 cases; no symmetry or group-transitivity assumption is needed.

Each of the three donors is untouched by any y<-y gate, and each needs a nonempty projection. Hence at least three y<-x additions from this source pair are necessary, one into each donor.

For type (1,3), the donor never contains b. Its recipient therefore needs at least one direct addition from the source pair to receive b. This is a fourth addition.

For type (3,2), there are two cases. If the recipient receives b directly from x, that is a fifth addition. Otherwise it must receive b from its donor at their unique y<-y gate. At that instant the donor cannot contain a, because a is forbidden in the recipient's final row and coefficients never decrease. The donor thus contains b alone at the transfer but needs both coordinates eventually. It requires at least two direct additions, one before the transfer and another afterward, instead of the one already counted. This again contributes a fifth addition. The registers in this case and in type (1,3) are disjoint, so these extra charges cannot coincide.

Every y<-x gate belongs to exactly one source pair: an x register always contains only that pair's coordinates. Summing gives at least 15 y<-x gates, plus the six forced structural gates. Thus the total is at least 21. The supplied words have exactly 3 xx, 3 yy and 15 yx gates and achieve the full matrix, establishing sharpness.

## 3. Independent finite projection check

The verifier independently enumerates each projected problem. A state records whether the source sum a<-a+b has occurred, which of the three y<-y transfers have occurred, and the six projected y rows (two-bit masks). It starts with unmerged sources and zero projected y rows. Each row must stay inside its prescribed final mask. The source sum and y<-y gates cost zero; each y<-x gate costs one. A transfer is permitted only if donor and recipient supports are disjoint. These transitions exactly describe the projected unit-positive operations. Contributions from other source pairs disappear on projection; their operations can be removed. Releasing the global timing shared with those other pairs can only enlarge this projected class.

A complete 0/1 breadth-first shortest-path computation explores every reachable state, without a depth/state cap, and returns minimum cost five for all 24 projections. Each projection has exactly 16,384 reachable states, exhausting its entire bounded state space: two source states, eight transfer masks and 2^10 possible target-coordinate subsets. This is an independent finite check of the per-pair bound, not a search through all twelve-register programs. The global theorem follows from the disjoint charge argument above. Relaxing the (1,3) requirement to (1,1) gives a four-addition projected solution, a control demonstrating that the sharp type hypothesis matters.

## 4. Rational transport and source binding

For every supplied gate i<-i+q*j, the verifier solves q=d_i/d_j over exact rational numbers. It checks consistency around all edges and computes the entire rational matrix independently. With D=diag(d), it verifies M_scaled=D M D^-1. Therefore conjugating an entire allowed competitor by D^-1 is a gate-count-preserving bijection with the unit-positive class. Some cells use -2 as well as -1/2; this is handled exactly, not by an assumed common scale. The receipt records all eight D vectors and actual endpoint permutations to the first cell.

Each named core's `unit` and `scaled` lists must exactly equal the same named entry in `CODED-CELLS-k8.json`. The pinned `cgx_leaver.py` reads the scaled coded-cell list and emits those elementary operations in its coded-triangle branch. The selected-at-base PR1042 README identifies these k8 cells in its construction lineage. The immutable assembly is pinned and its exact kappa is checked only as a provenance guard.

This package does not rebuild that complete construction or replay its native or hosted interfaces. The package's retained `evidence/local/FULL-WORD.json.gz` reports R492 and is an older intermediate, whereas the README describes the rebuilt R480 seven-slot word. It is deliberately not used as evidence of literal selected-word location. PR1049 independently audits the literal final-word cells and endpoint/accounting obligations; that result is cited, not re-executed here.

## Limits

The full dirty-input endpoint is essential; a competitor allowed to change the endpoint and compensate elsewhere is outside the theorem. So are additional registers, arbitrary rational coefficients, cancellations, cross-cell transformations, free initial basis changes, or a cost objective based on paid frame climbs. In particular, a 21-ADD minimum does not prove minimum supplier cost. The diagonal D identifies a restricted gate class; it is not supplied as a free physical operation. There is no new word, helper saving, profile improvement, precision admission, or kappa claim.
