# Two exact chart contractions over the open #7601 word

The emitted P104 native yields a conditional numerical bound **κ = 0.003650000454083** on the retained 17-stage application. It is an independent change on top of the two fusions proposed in open #7601. The raw crossing is in \([0.0036500004540838632736187363,\,0.0036500004540838632736187364]\). The retained old word has a strictly negative price at this claim. The bound relies on the same five source premises and the same completed conditional BIT supplier. The full compiled multiplier and external admission remain outside this local replay. [Open #7601](https://github.com/CrocSwap/integer-mult-bounds/pull/7601) · [#7546 complete conditional application](https://github.com/CrocSwap/integer-mult-bounds/tree/99438c43df7aac1e5dbcc43c1578fcd886c119ec/research/p104-role902-direct-lift)

## Contractions and exact interference test

Indices below are zero-based in pinned #7601 head `eccf3d1fe814ea86a373d37a783105ceb853c390`.

| Public role | Old MOVE indices | Old chart IDs | Rank path | New child |
| --- | --- | --- | --- | ---: |
| 166 | 41976 and 43482 | 327 → 783 → 907 | 2 → 5 → 7 | 5 |
| 134 | 42076 and 43522 | 618 → 789 → 913 | 3 → 5 → 7 | 4 |

Role 166 is untouched in its open middle range. Role 134 receives two adjacent ADDs from role 315 with coefficients \(+1/2,-1/2\) before its unchanged later reads. There is no other access to 134 while it occupies chart 789, and neither ADD writes 315. Remove them both. All other scalar and owned instructions keep their relative order. Ordinary gates disjoint from the moving role commute with advancing its second MOVE. Each direct signed child is \(F_C F_A^{-1}\), since the unchanged middle-frame operator cancels. This point applies even when the original two moves have many other live roles between them.

For all independent public inputs, the exact normalized output, public charts, owned INIT/MOVE/CLEAR sequence and actual erasure rows equal #7546 as well as #7601. All 1,501 public rows are checked. The old 74 owned lifetimes and 47 owned moves remain, and COPY occurs only on a live zero owner. The checker verifies all 512 forward and adjoint columns for each of the two new compositions and the two inherited #7601 compositions. Absolute phase and its inverse are checked, including a phase mutation that changes the matrix without changing its signed Pauli tableau.

## Transfer criterion and where it stops

With only SCALE and incoming ADD while one public field is in chart \(B\), the normalized value at its exit is \(m x+d\). Here \(m\ne0\) is the product of intervening scales and \(d\) is the sum of incoming source forms with their full later scale weights. The field is never read by another role in this interval. Therefore changing its chart early cannot affect any other stored rows. The precise tracked two-cut question is whether \(d\) lies in the sum of the coframed source spans immediately before the first MOVE at chart \(A\) and immediately before the second, using the *other* live rows at chart \(C\). If \(d=d_A+d_C\), add \(d_A/m\) before the first MOVE, execute one MOVE to \(C\), apply \(m\) and then add \(d_C\) at the old exit. This realizes exactly the original exit and preserves every unrelated lifetime. Both solution operators refer to unchanged other rows at their respective cuts. A coefficient solution over the rationals still has to pass the source scalar, phase and precision contracts.

For the 1,035 receive-only or untouched public pairs in #7601, exact source support excludes 756 using one input coordinate absent from all available stock. A full projected rank over \(\mathbf F_{1009}\) excludes 43 more, using all distinct stock rows independent modulo the prime and an increased augmented rank. Another 25 are excluded by rational elimination. There are 209 unresolved under this calendar's stock width and rational-fill budgets. The two zero residuals above are emitted and replayed. This result allows ordinary repair only at the two stated cuts and grants the exact stock there. It leaves additional cuts, multiple simultaneous edits, the mixed read/write classes, and enlarged native stock open.

## Complete 17-stage checks

The new native paid rank delta against #7601 is \(\{2:-3,\ 3:-1,\ 4:+1,\ 5:+1\}\), preserving rank mass. Two native MOVE positions and two ADD positions are removed. The exact routed invoice has **110,400 paid calls and 22,461 independently productive fields**, rank surplus 1,424. At κ=.005 the precise complete price change against #7601 is +0.5187053050271 or more. The candidate's residual moment there is −521.2925564756187 at the upper endpoint. At .0227 it is −7094.9261817940628. The contraction shows a conditional improvement near the selected value.

The signed receipt freshly executes the same #7113 Laurent application, checks the integer caller grid, constructs every ordered paid position and helper ownership and rederives the phase polynomials on 13,600 contacts. Orthonormal completions are independently chosen. Each of the four new changed physical chart pairs is validated for arbitrary columns, and every other chart pair retains its old certified operator. Tensoring those identities preserves the routed action at each native width, under the old compiler contract. The exact input/output and all unchanged owned retirement contents are compared over the Gaussian address model through this chart identity and the complete scalar replay.

The fixed-grid replay recovers the native odd scale 1125 and fractional height 25. A fresh forward defect bound with adjoint witness checks, applied to the new complete word and then the 17-stage caller, yields the precision factor 2430. The rebuilt budget includes **782,733,348** ordinary work, **25,457,272,480** elementary map records and **43,923,200** scalar services. The latter is higher than #7546's 43,840,512 owing to the inherited premix from #7601. These are conservative source-unit counts. The directed inherited gate verifies the input-lift moments, strictification including higher moments, retained BIT budget, and all 54 strict and four functional outer inequalities at the new claim.

The replay checks an exact changed boundary, fresh precision and resource inequalities, and the retained conditional composition of the remaining source-complete machinery. It inherits the unchanged finite compilation and analytic recovery contracts, and has not executed a fully materialized multiplier, all components of the upstream hosted package, or obtained public admission. No external update was made.

The canonical emitted uncompressed JSON has SHA-256 `fd32412a33cd72b557f474223c7bcd669b20a0aeaabf8d7040f396e7070dddbf`. Run the checker in [README.md](README.md) to rebuild and authenticate the gzip, proof receipts and counterexamples.


