# Capped-interior layout extension: positive signoff

The earlier sparse-union layout proof extends to dyadic interior cap
`B=p^b<d=p^epsilon`. No step requires boundary density 1/d specifically.
Replace that density by `O(W/B polylog p)` throughout.

Within one original phase cell, each full B-block is followed by a W-wide
separator; reserve the original endpoint bands and apply dyadic tail
carving to the remainder. There are O(d/B) full blocks and O(log B) tails.
Thus the boundary count is `O(W(d/B+log B))`. Inside an L=p^8 microbox,
summing cells and its two possible clipped end cells gives

```
|E_i| = O(L W/B polylog p + W polylog p).
```

The extra term is negligible. Original bandwidth W makes different interior
blocks uncoupled once a W-wide separator lies between them. Eliminating a
block joins only its neighboring O(W)-wide boundary bands. In boundary
order the Schur half-bandwidth is O(W), independent of B or the number of
blocks. The original cyclic wrap remains an explicit boundary/border term.

Every original B_i/C_i shear and every S_i/S_i^-1 boundary operation still
acts as identity on E_i^c. Therefore U is invariant and
`U_i=E_i x [L]^(g-1)` is still a complete rectangle. The extraction,
one-field transpose, exact axis operation and ordered merge from AUDIT.md
apply unchanged. They give

```
per group: O(V g^2 W/B polylog p),
all groups: O(V d g W/B polylog p).
```

No extra scan per capped block is required. All capped circuits of an axis
form a direct sum, whose shorter members use identity rounds in a common
polylogarithmic schedule. Likewise, boundary factor pages and the capped
piece catalogue have polynomial total size per microbox: L, g, B and all
local matrix dimensions are polynomial in p. Their generation or sequential
copy once per complete microbox is absorbed by its superpolynomial inner
volume and spectator RHS stock. Increasing the number of blocks from L/d
to L/B does not change that argument. Random access to a global catalogue
is still not assumed.

Membership is calculated from the original phase-cell endpoints and the
local block quotient/remainder, followed by the dyadic-tail rule. Its cost
is O(g h^2 polylog p), h=Theta(p/d). For the pinned capped row the exponent is
about 0.09661446<1, so it is absorbed by a p-bit record. Inside a microbox,
coordinate headers use O(g log p) bits. Even the conservative full-coordinate
sparse sort with O(gh)-bit keys remains below the target; the complete-
rectangle implementation needs no such sort.

There is no requirement `g<h` or `beta<1-epsilon`. The support-sensitive
router uses O(g polylog p) moved/control bits spread through the entire
active group of width gh. Its reservoir headroom is
`gh/(g polylog p)=h/polylog p -> infinity`. Individual guarded neighborhoods
fit the original long axis; the collection of all g controls does not have
to fit in a single axis. This is the same support proof already audited.

Microedge correction is unchanged. The underlying rounded operator and its
physical bandwidth do not change when a factorization receives more cuts.
Only the principal restriction and Schur decomposition are repartitioned.
The retained Neumann/principal-window comparison still applies to that
same operator. With L=p^8 and halo A=p^3, the additional output fraction is
O(g p^-5), now about p^-4.9064. Its sparse gather, true-period correction and
old sequential local solvers are still negligible. Capping does not turn
this into a dense non-dyadic tensor halo.

The pinned independent arithmetic checks give approximately

```
epsilon = .9984838711085558
b       = .9064167934681446
beta    = .0935821965318554

per-group union movement power = -.2192524004044339
total union movement power     =  .6856492741722665
total group scan power         =  .9049016745767004
membership descriptor power    =  .0966144543147439.
```

`check_capped_layout.py` independently checks finite capped partitions,
dyadic block sizes, separator distances, worst-pattern elimination fill,
and these exact rational layout inequalities against the pinned candidate
JSON. No layout blocker was found.

This signoff is specifically for carving, sparse support, actual stream
movement, descriptors, and inherited microedge placement. It does not
independently prove the newly anchored broad/narrow Gaussian formulas or
their final precision bound. Those remain the algebraic/analytic cap audit.
