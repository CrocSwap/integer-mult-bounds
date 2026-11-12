# Fixed-clock two-bank source synthesis

The four frozen windows retain the #7334 native and #7113 signed
caller contracts. For a mover path A→B→C, the proposed edit puts
the direct rank-two MOVE A→C at the old first clock. The peer
keeps its paid path in B. Both original ADDs stay at their signed
clocks in their original order. The destination chart is C when
the mover is written and B when the peer is written. Other paths,
scalar events and ownership lifetimes are fixed.

Let d be the arbitrary dirty destination's normalized pre-event
row, s the original source row, α the signed ADD coefficient,
and uᵢ unchanged public rows in the new destination chart.
The two old operands are excluded from independent donors. The
destination may appear once as a diagonal SCALE. An exact
replacement would satisfy d + αs = λd + Σ βᵢuᵢ. Since α is nonzero,
the old source must lie in the rational span of d and the uᵢ.
The test grants this entire span, including every rational
diagonal factor. A linear separator for that relaxation is
also a separator under any narrower signed dyadic coefficient
and dirty restoration constraints.

The old second ADD uses the actual original post-first rows.
If the first replacement were exact on arbitrary inputs, those
rows would still be valid at the second clock. Thus each
necessary bank test may use its original pre-event prefix.
One failed bank suffices to rule out its whole fixed-clock edit.

## Exact bank certificates

The forward engine reconstructs signed normalized prefix rows
and uses coordinate tests followed by exact elimination. The
reverse engine recovers the same public donor and destination
rows by exact adjoints through all 76,466 events. It validates
the signed coordinate witnesses and the exact rational residual.

| Mover | ADD clock | Destination chart | Separator | Signed value on αs |
|---:|---:|---:|---|---:|
| 1305 | 41322 | 207 | x1488 − 2x1493 | −2 |
| 1305 | 41323 | 983 | x651 | 1/2 |
| 1303 | 43855 | 207 | x651 | 1 |
| 1303 | 43856 | 984 | x653 | −1/2 |
| 654 | 44565 | 983 | x40 | 1/4 |
| 654 | 44566 | 207 | x2 | −1/4 |
| 652 | 44586 | 984 | x5 | −1/2 |
| 652 | 44587 | 207 | x1 | −1/4 |

Here xj is evaluation at original normalized input coordinate j.
Every listed functional vanishes on all granted bank rows.
At clock 41322 the bank is just the destination diagonal
role 1305. The reverse rational covector has value +2 on
the original source role 1488 and −2 after applying α = −1.
Both engines give bank rank one and the augmented rank is two.
The seven other certificates use one absent coordinate each.
No owned row was present in the exact bank stock.
All four windows fail and no coefficient or physical gate is needed.

## Complete price

Across all 17 caller copies, an edit changes paid rank-one count
by −34 and rank-two count by +17. Paid count would change from
110,519 to 110,502 for one edit or to 110,451 for the optimistic
four-edit stock. Productive count remains 22,461 and signed rank
surplus 1,424. The one-edit directed upper is about
0.08583213854035211 raw and the disjoint relaxed four-edit upper
about 0.34332855416140845 raw at the incumbent crossing upper.
The complete fixed-target margin upper is about
−139.38966768429373 at κ = 0.0040075385047236.
One additional raw paid rank-one position defeats the entire
four-edit bound. This fixed-clock scope and the retimed-pair scope in
[#7371](https://github.com/CrocSwap/integer-mult-bounds/pull/7371)
consume the same paid stock.

The conditional ordinary envelope grants two donor ADDs and one
nonzero destination SCALE per replacement in the retained F25
dyadic format. It charges 18 conservative ordinary copies and
1,000 added route units per edit without credit for deleted
ordinary work. The corresponding upper is 782,762,408 for one
edit and 782,903,240 for four. With the hosted endpoint boundary
fixed, one edit can add at most 2,176 scalar services and removes
34 map slots under the quoted tape accounting. These are
price limits. A physical survivor would still need exact
all-width frames, ownership, restoration, precision, tape and
accumulated grid/envelope checks and full independent caller
replay. No κ gain follows from these exclusions.
