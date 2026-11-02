# True periods inside a near-one dyadic container

The primary halo theorem extends to arbitrary true periods s_i when an
already supplied dyadic rectangle t_i>=s_i has bounded total inflation
`product t_i / product s_i=O(1)`. Simultaneous zero embedding and its inverse
cost one ordered scan each by `RECTANGULAR-EMBEDDING.md`. This prerequisite
is satisfied only where the inherited near-one capacity bound applies; it
must not be replaced by independently rounding every axis to its next power.

Take N dividing every t_i. Write `s_i=q_i N+r_i`, `0<=r_i<N`. There are
q_i full valid cores and, if r_i>0, one ragged core in axis i. The initial
support-limited gather uses the dyadic storage coordinates, not mixed-radix
division. It may produce invalid all-zero storage tiles; discard those.

Apply ordinary flat cyclic convolution only to tiles whose every active
side has valid length N. Their interior outputs remain exact. Regular tile
face corrections use the earlier first-boundary-axis rectangles, but every
halo coordinate is now reduced modulo **s_i**, never t_i.

If any side of a tile is ragged, discard its entire flat-convolution output.
For its actual side lengths r_i(tile), compute every valid output in
`product [0,r_i(tile))` using the input rectangle
`product [-L,r_i(tile)+L)`. All sides are at most N+2L. The same g successive
polynomial-length convolution/crop passes therefore produce exact outputs.
Full ragged tiles and regular face outputs form a disjoint correction set.

Let Q_i=q_i+1_(r_i>0). The total full-halo volume of *all* valid tiles is

```
H_all = product_i [s_i + 2L Q_i].
```

Their all-full-tile contribution is `product_i q_i(N+2L)`. The sum of the
ragged-tile halo volumes is their difference. Expanding by a first ragged
axis, or simply telescoping the product, gives

```
H_ragged <= H_all * sum_i (N+2L)/s_i
         = O(S gN/s_min),
```

since `H_all/S <= exp(2L sum_i Q_i/s_i)=O(1)` when gL/N=o(1).
Regular face input volume is O(S gL/N). Thus total sparse copy volume is

```
M=O(V [gL/N + gN/s_min]).
```

The new term is smaller than V divided by every fixed polynomial in p when
`s_min=2^Theta(p/d)` and `N,g=poly(p)`. It pays all the same key sorting,
metadata and local computation factors. No new per-axis full scan appears.

## One source-driven enumerator

For each valid source coordinate x_i, list the valid destination tiles t
for which an unwrapped representative

```
y_i = x_i - tN + k s_i
```

lies in `[-L,r_i(t)+L)`. Only the home and neighboring core intervals can
qualify; there are at most three choices because L<N/4 and s_i is much
larger than N. Compute them from quotient/remainder and the first/last-core
cases, in O(log s_i) metadata work. No scan through all tile numbers occurs.

Enumerate the Cartesian products of these short lists. The number of
candidate pairs over the whole input is exactly H_all, hence O(V) in
payload units. For an all-full destination tile, emit only those of its
first-axis face rectangles containing y. For a ragged destination tile,
emit its one full local rectangle. Full regular interior candidates are
tested and discarded without copying their payload. All coordinate tests
and keys have O(gh) bits and fit the same metadata budget as before.

Sort and compute only the emitted sparse records. Their tags distinguish
regular faces from full ragged tiles; their output sets are disjoint. The
final sparse sort uses the physical dyadic tile and within-tile output
address. After merging, inverse-gather and crop invalid storage entries by
the original true-period predicate. Every cyclic lookup has used s_i.

## Exact finite controls

`check_ragged.py` compares the source-driven construction against an
independent rectangle enumeration for periods (19,22) and (17,18,20), N=8
and L=1. It verifies unique gathered keys, true-period wrap, every corrected
signed tensor-convolution output, and that only complete-tile interiors
are left to flat cyclic convolution. Small finite enumeration loops over
tile numbers as an independent reference; the asymptotic enumerator uses
only the home/neighbor cases described above.
