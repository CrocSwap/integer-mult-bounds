# Sharp radial cost for exact-sum Gaussian square-to-swap rounding

The optimum forward outward radial slack is
`beta = sqrt(19) - sqrt(13)` within the class of total maps
`F: Z[i]^2 -> Z[i]^2` preserving exact complex sum, approximating the
positive ideal pair transform within Euclidean error one, and satisfying
`F^2(u,v) = (v,u)`. The same optimum holds for absolute radial distortion
and the maximum of forward and inverse outward slack. The construction
also commutes with global Gaussian units. The lower bound needs no phase,
periodicity or separately assumed equivariance condition.

The all-input proof reduces every candidate on the sum-one fiber to a
quarter-turn-equivariant perfect unit matching on the half-integer plane.
A 36-vertex square cannot close under such a matching because internal
edge orbits consume eight vertices. Its forced crossing has radial cost
at least beta. Pairing adjacent square rings gives a matching attaining
that cost. The exact four-cycle `(3,-2) -> (3i,1-3i) -> (-2,3) ->
(1-3i,3i) -> (3,-2)` alternates squared norms 13 and 19.

Read `PROOF.md` for the universal argument and complete pairing rule.
`SOURCES.json`, `OVERLAP.json` and `NOTICE.md` record exact predecessors,
bounded overlap coverage, attribution and reference-code exposure. This
narrows the exact-sum/order class; it is not an unrestricted forward-only
rounding lower bound.

Run the standard-library checker from this directory:

```sh
python3 -I -W error -B verify.py
python3 -I -O -W error -B verify.py
sha256sum -c CHECKSUMS
```

Expected marker: `PASS_ANNULAR_GAUSSIAN_ORDER_OPTIMUM`. The receipt checks
seven ring pairs, all 24 geometric edges crossing the 36-vertex box, 625
Gaussian pair inputs, the exact attaining cycle, and controls for missing
quarter-equivariance, overlapping edge orbits, conjugated inverse and the
known tensor obstruction. Radical comparisons use integer interval bounds.
The written proof covers all rings and inputs. The checker deliberately
generates bounded ring dictionaries; it is corroboration, not an
unbounded physical implementation or an accelerated native tariff.

The inverse is `swap o F`. Exact sum and the square identity universally
exclude inverse-by-conjugation. This map's unit covariance and integral-image
exactness put it under the known #6778 theorem, so the same stateless map
cannot commute across rows and columns. No selected caller, native graph,
physical scratch cleanup, tensor error supplier, assumption discharge or
new kappa is claimed. All five selected assumptions remain in force.

The original radial-cost-one construction remains a separate frozen
superseded checkpoint at `../exact-sum-square-to-swap/`; it is not counted
as another publication. No remote mutation was performed here.
