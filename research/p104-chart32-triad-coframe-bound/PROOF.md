# Two fixed-boundary chart-32 triads

The old mover path is 3→32→355 in both windows. The peer enters the frozen block in chart 32 and has its next paid move to 350. The table records the peer contacts immediately before and after the signed block. Both walks count source and destination incidents.

| Mover and peer | Mover paid clocks | Triad clocks | Peer boundary contacts | Exact action on mover and peer |
|---|---|---|---|---|
| 319, 35 | 31303, 38665 | 31304, 31306, 31308 | 31288 ADD reads 35, 31319 MOVE 35 to 350 | (x,y) → (y,x+y) |
| 1081, 807 | 31360, 37214 | 31361, 31363, 31365 | 31358 ADD writes 807, 31374 MOVE 807 to 350 | (x,y) → (y−x,x) |

Each signed 2×2 block has determinant −1 and the stated action holds on arbitrary dirty public inputs. There are no intervening additional contacts with either participant across each triad. The peer entry is an unchanged scalar contact in chart 32, so its old entrance rank is zero. Its outgoing paid rank is one. Keep all exterior contacts, role labels, other operators, owners and productive targets fixed.

Write A and C for the mover's outer binary subspaces and P and Q for the peer's. A common coframe D under nested public MOVEs requires A + P ⊆ D ⊆ C ∩ Q. Here A is zero, P is the span of [50], C is spanned by [30,44] and Q by [50,84]. Since 30 XOR 44 is 50, P is contained in both rank-two upper subspaces. Their union has rank three by GF(2) elimination, so their intersection has rank one and equals P. Thus D must equal P as a binary subspace. Any same-span chart label or wrapper still leaves the transport ranks at (1,1,0,1). The proof makes no assertion about signed chart equivalence for different labels.

At D=3, generator 50 fails the peer entrance inclusion. At D=355, generator 30 fails the peer exit inclusion into chart 350. This excludes all four prepriced endpoints and fixes the common subspace under these two windows and these fixed boundary contacts.

## Directed price

The quote charges the 17-copy difference between old ranks (1,1,p,q) and new ranks (1+s,1−s,p+s,q−s), with s=−1 at chart 3 and +1 at chart 355. Rank zero creates no paid position. The paid and productive baseline counts are 110,519 and 22,461, with signed rank surplus 1,424. The 90-row favorable profile relaxation gives one-site upper 0.2794607590692864, two-site upper 0.5589215181385728 and fixed-target complete upper about −139.15293154226487. An extra paid rank-one charge exceeds the two-site relaxation.

The actual pair has (p,q)=(0,1). Chart 3 would require negative peer entrance rank. The chart-355 row would give ΔP1=−34 and ΔP2=+17, paid total 110,502 and no productive change, if geometry held. Its one-site upper is 0.08583213854035211 at the old crossing. Both instances fail that geometry. At the only feasible common binary subspace the paid histogram stays fixed.

The five inherited native, ownership, compiler, precision/tape and analytic recovery premises stay in scope. A different route would need a fresh signed construction, full accounting and complete independent replay.
