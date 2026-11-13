# Necessary prefix gate

Let `q` denote the central phase variable with `q⁴ = 1`. Let `B1,…,B17` be formal commuting body variables in the pinned caller's Laurent representation. In this representation the two roots in each pair have identical final diagonal `q³ B7 B8` or `q³ B9 B10`. An invertible input basis over the body-independent central-even ring commutes with that scalar diagonal. This permits the input change in the necessary test without assuming that an adapter has a physical implementation at any cost.

Write `E = Q(i)[q²]/((q²)² − 1)`. At cut `t` the literal prefix's two columns have coefficients `A[m,p](q²) ∈ E^(36×2)` at body monomial `B^m` and parity `p ∈ {0,1}`. The first column `v ∈ E²` of an invertible two-input basis is nonzero in both field factors of `E`, since evaluation at `q² = +1` and `q² = −1` gives `E ≅ Q(i) × Q(i)`.

If the first productive part has only body `Bj` and parity `ε`, every coefficient outside `(Bj, ε)` must annihilate `v`. At each sector evaluation, stack the corresponding forbidden rows over all 36 output coordinates. If this stack has rank two in either sector, the associated component of `v` must be zero, a contradiction. The gate also survives any invertible body-independent central-even output change at the cut, because it acts invertibly on each body and parity coefficient separately.

The forward engine propagates the two basis columns from the literal input through every signed event. It checks the exact final diagonals and records a nonzero two-row Gaussian-rational determinant in the positive sector for each of the 38,272 keys. The independent reverse engine starts from the required final diagonals, inverts the same literal events in a full-exponent Laurent encoding and checks the initial endpoint. It recomputes each forbidden rank from the Hermitian Gram determinant `A D − |C|²`, evaluates both sectors, and checks every reported forward row and determinant. In each sweep a cut is the number of completed signed events and includes 0 and 4,783.

This result excludes a specific prefix under the declared two-input basis and fixed itinerary. It does not exclude a changed prefix or paid itinerary, broader input mixing, altered body or phase contracts, or other rank classes. It provides no realized savings or complete supplier construction.

## Directed price

For one hypothetical split on each of the 96 Type A ports, the productive delta is `−96 rank17 +96 rank8 +96 rank9` and the paid delta is empty. Apply the inherited #7298 tariff at the pinned #7481 crossing interval to bound `96 × (8^κ + 9^κ − 17^κ)` between 4.07820585157566 and 4.07820585157568 raw, strictly. Even four compatible such directions would provide less than 16.31282340630272 raw before ancillary costs. An added rank-one position on each of the 96 ports costs 96 raw. The exact lower and upper bounds and price inputs are in `receipts/PRICE.json`.
