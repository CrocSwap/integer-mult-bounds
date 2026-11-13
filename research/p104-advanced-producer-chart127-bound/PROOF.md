# Exact separation with the advanced producer

The pinned word moves public role 1351 from chart 516 to chart 518 at MOVE38867 and from chart 518 to chart 127 at MOVE48154. The only middle contact is ADD38868, which subtracts the historical role 1020 row h. The proposed edit removes the two earlier events and replaces MOVE48154 by a single rank-five chart 516 to 127 MOVE. Before ADD48155 it inserts the old ADD52128 to role 1369 from owned role 1568, then the already-paid MOVE52129 of 1369 from chart 240 to chart 127. The originals at 52128 and 52129 are removed. The independent verifier checks the move intervals and that both placements of the advanced ADD read the same owned value.

In the normalized chart model, MOVE preserves the normalized coordinate. If w is the owner 1568 value from ADD37773 and p is the old role 1098 before ADD36360, the current role 1020 is h−p+w. The advanced role 1369 contributes its old value plus 12w. The proposed edited role 1351 is old1351+h. The exact continuation reconstructs these covectors and grants all 669 active edited chart-127 rows as repair sources, including edited role 1351 and advanced role 1369.

After the initial rational solver capped, sparse primitive integer elimination found an exact separator. The 90-coordinate rational probe in `receipts/LEAD.json` makes all 669 edited rows zero, old1351 equal to 1 and h equal to −1. The original ADD48155 into role 408 therefore yields 1, while the edited ADD yields zero. The independent normalized forward program verifies both trajectories, all granted bank responses and the owner version through the advanced and original placements. Any deterministic repair confined to this bank receives the same input as on the all-zero assignment and cannot supply the required old response.

The exclusion fixes one route and one cut with unchanged other paths. It leaves earlier repair, a different arrival, or a changed downstream contract open. No physical lowering, absolute phase, complete signed adjoint, all-size, precision or tape acceptance gate was reached.

## Directed price

Native paid delta is −1 rank-one, −1 rank-four and +1 rank-five. Productive counts are unchanged. With 17 exact signed calls, the price change before repairs is 17 × (1 + 4^(1−κ) − 5^(1−κ)). The exact directed rational bounds at the #7481 crossing are in `receipts/LEAD.json`. The upper bound is below 0.15453192223429988 raw. One additional rank-one child per native call costs 17 raw.
