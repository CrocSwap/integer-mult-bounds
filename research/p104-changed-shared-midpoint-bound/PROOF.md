# Exact changed-role midpoint exclusions

## Two-role topology

Keep the original nonzero ADD, its signed coefficient and clock,
both outside paths, and the four paid MOVE clocks. Each operand
must have its immediately preceding and following literal contact
be a public ascending MOVE into and out of the old ADD chart.
Both operands of ADD and COPY are contacts. This guard prevents
a rechart of an unmodified intervening operator.

The regenerated ten anchors come from the exact #7365 stock and
independent #7319 public-helper census. The forward contact
index and independent reverse chart walk agree on all their
adjacent events. For the other operand, six anchors have a
blocking ADD before only, one after only, and three on both
sides. Thus zero pairs reach actual reprice or exact GF(2)
offset tests. In the initial relaxation, eight of ten could
have a strictly positive rank profile if the peer geometry
were available. The directed one-edit upper was about
0.250511783519717 raw, the compatible relaxed whole upper about
1.372746550052082 raw, and the complete margin upper at κ =
0.0040075385047236 about −138.259532576579. Those stock ceilings
allow unknown peer ranks and grant ancillary work free. The
ten literal contacts give a verified compatible saving of zero
for this pair scope.

## Closed component on chart 746

The two blocking ADDs involving role 452 give a single joint
component with these exact old routes.

| Public role | Entrance chart | Midpoint | Exit chart | MOVE clocks |
|---:|---:|---:|---:|---|
| 1250 | 744 | 746 | 207 | 40833, 44593 |
| 452 | 263 | 746 | 916 | 40832, 41180 |
| 532 | 744 | 746 | 207 | 41178, 44611 |

The two original contacts are `40834 ADD 452,1250,+2` and
`41179 ADD 532,452,−2`. Both walks verify they are the only contacts
of these roles inside their respective MOVE intervals. This exact
component also appears in the independently replayed
[#7338](https://github.com/CrocSwap/integer-mult-bounds/pull/7338)
`GEOMETRY-69.json` receipt under keys `532:41178:44611` and
`1250:40833:44593`; the [published receipt manifest](https://github.com/CrocSwap/integer-mult-bounds/blob/349996445176e934ffb3c76813adcd230ca8f783/research/p104-compensated-fusion-readout-bound/receipts/SHA256.json)
pins it at SHA-256 `a2dd10737f5bfbd3818e6766df3890e445fd46f661af9521f5d724b7c56c1d45`.
That contribution tests a compensated paid contraction. This
scope retains all six calls and redistributes their paid ranks
with a common replacement chart.

The old paid leg ranks are 3+2, 3+1 and 3+2. Changing the
common midpoint rank from 6 to 6+δ changes each pair from
(p,q) to (p+δ,q−δ). Across all 17 copies, the only strictly
positive directed actual offset is δ = −2. Its signed paid
histogram delta is {1:+34, 2:−34, 3:−34, 4:+34}. Paid count
110,519, productive count 22,461 and signed rank surplus
1,424 stay fixed. This offset grants a net of at most about
0.106305391209185 raw at the incumbent crossing upper, and
one extra raw rank-one call overruns the price. The initial
whole component upper 0.197627453181767 grants all possible
peer ranks free and chooses at most one edit. It cannot be
added to the pair stock. The complete fixed-target upper is
about −139.549893451902.

Write L = A₇₄₄ + A₂₆₃ for the span of the two entrance frames,
and H = C₂₀₇ ∩ C₉₁₆ for the intersection of the exit frames. Both old entrance frames lie in chart 746, and
chart 746 lies in both exits. Any common candidate frame E
must therefore satisfy L ⊆ E ⊆ H, with all six
leg ranks positive. Exact enumeration and independent Gaussian
elimination give `dim(L)=5` and `dim(H)=6`. The only profitable
actual rank is four, so it cannot contain L. Both engines match
the entire binary vector sets. There is no signed physical
candidate to materialize.

## Same six legs with two coframes

Retain both literal ADD clocks and each old outer chart. If role
452 enters a middle chart between the two ADDs, the first ADD
would use chart 263. Role 1250 would need an ascending paid
MOVE from 744 into 263. Both charts have rank three, and vector
134 belongs to 744 and not to 263. If 452 exits its middle chart
between the two ADDs, the second ADD would use chart 916. Role
532 would need to ascend from 916 into 207, but vector 1 belongs
to 916 and not to 207. Vector numbers are the original binary
frame encodings. If both MOVEs fall between the ADDs, both
obstructions apply. With neither paid MOVE between the ADDs,
452 occupies one chart throughout and the distinct-coframe
case does not arise. This argument keeps the six original paid
legs, both ADD clocks and outside charts fixed.

These are scoped necessary-condition exclusions under the retained
native all-column, owned-erasure, compiler, precision/tape and
analytic recovery premises. No arbitrary-input supplier change,
full caller replay or new κ is asserted.
