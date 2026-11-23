# Supplied dyadic arithmetic at the actual tensor caller

This package proves a local arithmetic bridge for the pinned direct-circulant
`Grid.multiply` operations. It preserves the earlier integer-rounded-gate
kernel and its finite diagnostic guards. Its new routine uses seven arithmetic
registers and four shift/add products; it rounds each complete component once,
with the caller's actual ties-toward-positive-infinity rule.

## Result

If the four supplied input numerators fit signed B bits, B>=2, and their common
fractional precision satisfies 1<=P<=B, every arithmetic temporary fits
W=2B+1. The routine keeps all four inputs and both outputs live simultaneously
within 4B+7W data bits plus O(log W) control bits. Its local arithmetic cost is
O(B^2). These are maximum word width and local register costs, not a total
tensor-memory or tape-time theorem.

Under the already reviewed spectral-downset numerical theorem, the actual
external table entries, suffix caches and represented data fit
B=P+max(A,E)+3. Thus this new local routine can compute every literal
`product_diagonal` multiplication without changing its values or event order.
The source makes at most (d+1)T such calls per diagonal scan, so the replacement
charges O(J(d+1)T B^2) local arithmetic work over its J-stage bound. No faster
service price is assumed.

For p=30 and one binary side width equal to one, P=3438, B=4924 and W=9849.
The local frame has at most 88639 data bits plus controls. The predecessor's
diagnostic API only accepts B<=2048 and C<=256; an actual constructor-domain
`operand(1)` already needs 3433 signed bits. This limit does not refute its
universal written theorem. The new implementation is separate and proved
for arbitrary valid B and P; no predecessor guard is changed.

## Rounding boundaries

`Grid.word` rounds coefficient ties to even. `Grid.multiply` and the retained
`exact.apply` round output ties toward positive infinity. The checker retains
an exact halfway example separating those rules. It also obtains an actual
Full.shear gate for which the source's sixteen-H lowering at a small diagnostic
grid differs from replacing the original gate by one rounded output. The
bridge acts on the actual scalar multiplication sites, preserving the
lowering, table conversions, coefficient errors and chronology.

## Replay

This directory is self-contained and uses only the Python standard library.

```sh
python -B check.py --output /tmp/grid-binding-normal.json
python -B -O check.py --output /tmp/grid-binding-optimized.json
cmp /tmp/grid-binding-normal.json /tmp/grid-binding-optimized.json
```

Run from this directory, or use an absolute path to `check.py`. The source
manifest authenticates canonical predecessor blobs, the exact external caller
and the frozen reviewed numerical dependency. The rational oracle is separate
from both source arithmetic and the new register program. The normal and
optimized results must be byte-identical.

## Boundary and credit

Coefficient synthesis, global array movement and ownership, native-H private
storage, and reversible cleanup remain retained. Resetting five scratch
registers is destructive overwrite; no reversible restoration is claimed.
The quadratic arithmetic charge is explicit and does not reprice the outer
multiplier recurrence. All five selected assumptions and kappa are unchanged.

Nick Petalas supplied the existing general rational-row arithmetic theorem;
Armin Pourshafeie supplied rounded matching-layer semantics; Jose Manuel
supplied the retained rational unitary compiler; Ali Romman supplied the
direct-circulant caller. The frozen numerical theorem retains the credits to
Vlado Vojdanovski, Chafik Boukhalfa, Brian/JoyboyBrian and the other authors
recorded in its source package. Prepared for Jerry Chen / @CubeJerry with
substantial OpenAI assistance. Separate review is required before publication.
