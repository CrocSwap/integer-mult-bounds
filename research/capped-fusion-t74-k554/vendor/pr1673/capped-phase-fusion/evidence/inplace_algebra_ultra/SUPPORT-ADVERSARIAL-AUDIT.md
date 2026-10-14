# Adversarial audit of the support-local global H call

## Verdict and scope

No blocking circularity or lost complete-field hypothesis was found in the
proposed application at

```
g = Theta(p^.093),  n = Theta(p),  ell_axis = Theta(p^.002).
```

This conclusion retains the approved arbitrary-width equal-chunk primitive,
the exact common-frame/whole-child supplier contract, and the original
fixed-tape scan/repair interfaces. It does not approve a call on a fixed
coarse-label microbox. The call must include every value of the coarse
coordinates used as complete fields.

There is one specification detail worth making explicit: after a short-record
spectator has been moved to the suffix, every newly constructed router
reservoir and every router operation must be confined to the remaining
prefix. The retained router already makes this exclusion. The compact new
paragraph in `SUPPORT-ROUTER.md` does not spell it out. The explicit
construction below supplies it without any stronger primitive or exponent
restriction.

Reviewed sources are `SUPPLIER-SUPPORT-AUDIT.md`,
`work/halo_layout_ultra/SUPPORT-ROUTER.md`,
`work/integer-mult-current/notes/compact-control-layout.tex`,
`compact-control-movement.tex`, and the retained reports
`compact-arbitrary-source-routing.md`, `review-arbitrary-routing.md`,
`whole-complex-concatenation.md`, and
`whole-complex-prefix-and-wrapper-qualification.md`. The common global H
schedule was checked against `TENSOR-COMPILER.md`, especially its sections
3, 4, and 6.

## 1. Reservoir selection does not depend on a later coloring

For a matching with at most k moved endpoints, reserve the uniform field
width H0=kG before placing any controls. Three disjoint reservoirs contain
3H0 bits each; their existence requires only that the working binary prefix
have at least 9H0 bits. Use the retained layout: reservoir j comprises its
two H0-bit front blocks and one H0-bit block measured backwards from the
end. This convention makes all original placement swaps disjoint even at
the equality boundary.

An edge avoiding reservoir 0 belongs to the first cohort. An unassigned
edge avoiding reservoir 1 belongs to the second. Every remaining edge has
one endpoint in each of reservoirs 0 and 1 and therefore avoids reservoir
2. This uses only the two endpoints of an edge and pairwise disjointness of
the reservoirs; it makes no assumption about the number or spacing of
targets later assigned a residue color.

Place the cohort's avoided reservoir into the two front control fields and
the back control field using the original equal-H0 primitive. An endpoint
originally in a destination field is transported out to an unused reservoir
position. Since no endpoint originally occupied the avoided reservoir,
every transported endpoint is now in the middle field y. Recompute every
endpoint position, then color targets by their current position modulo K.
Thus the physical placement cannot invalidate the coloring: coloring is
performed afterwards.

A color with r targets uses the first r radix-B digits of each control field,
where B=2^G and rG<=H0. The unused high digits are inactive. A good-address
computation cannot carry into them. Bad-address computations may do so, but
the full operations remain bijective and their current-control inverses
are included in the retained repair. Source and target sets are disjoint
for each directional matching shear. Splitting that shear into colors does
not alter this fact.

For disjoint guard intervals [j_i,j_i+K), no equality of gaps is needed.
The four updates in the proposed lemma change a good guard block by

```
2zt + z(1 - 2(t+e)) = z(1 - 2e),
```

where e is its original low bit. The final temporary update restores its
digit. Consequently a completed four-update gadget fixes every non-target
bit, including source bits lying inside another guard. The two completed
gadgets surrounding load/unload therefore read identical source bits.
The good/bad predicate is fixed by the ideal shear, so the old sparse
repair on bad holes still applies. The last incomplete K-bit guard tail
uses the retained exact elementary CNOT and does not need record-paid
descriptor arithmetic.

## 2. An explicit noncircular short-record suffix construction

Let L=ceil(log2 p)^2 and let pi be the coordinate permutation to route,
moving at most k positions. In the sparse regime, choose an L-bit
consecutive field S that is disjoint from the support of pi and from the
actual last L binary positions. Such a field exists whenever

```
n > 2(k+1)L.
```

Indeed, after excluding the actual suffix, the at most k moved positions
cut the remaining interval into at most k+1 gaps. If every gap had length
less than L, that prefix would have length at most (k+1)L-1. The displayed
inequality contradicts this bound.

Let A be the old disjoint equal-L swap exchanging S with the actual suffix.
Execute A, route the conjugated permutation A pi A^{-1}, then execute
A^{-1}. Because pi fixes S pointwise, its conjugate fixes the actual suffix
pointwise. It still moves at most k coordinates. All endpoints are now in
the n-L prefix. Choose the three dirty reservoirs in that prefix and run
all compact rotations, original control shuttles, elementary CNOTs, and
bad-hole repair there. Recompute endpoint names after A and after the
reservoir placement. In the application, n-L>=9kG holds with a wide
asymptotic margin.

The suffix is a complete binary field with arbitrary contents. Reinterpreting
its 2^L values as part of a record gives record length R0*2^L, without
creating, padding, or deleting data. This length exceeds every fixed
polynomial in p. No operation whose cost relies on that record length acts
on its component coordinates. Both instances of A use the already approved
primitive and cost O(V L^(1-a))=O(V polylog p); they do not invoke the new
router. This removes the prospective circularity.

For the general router outside this sparse branch, the retained
first-L/second-L/actual-last-L candidate convention and matching cohorts
also work. Arbitrary candidates should not be substituted blindly: a
candidate can partially overlap the actual suffix, whereas the old swap
requires equal disjoint fields. After each candidate placement, the same
n-L prefix exclusion is mandatory. If the entire binary span is only
polylogarithmic, the old elementary construction suffices. If
n=O((k+1)polylog p), the old full-span construction gives the desired
support bound up to polylogarithms; its own short-record preparation must
still use the old suffix construction.

For a full H supplier call, reserve the suffix outside its selected field
and keep it fixed throughout the completed call. If necessary, perform
the same old L-bit placement before exposure, update the logical names of
the neighborhoods, and restore it after inverse exposure. The source
neighborhoods need not remain physically consecutive before exposure:
the exposure permutation explicitly routes their named bits. The target
complete chunks are placed before the reserved suffix.

## 3. Whole-row padding and the next diagonal scan

The leading row prefix and the front/back controls are assembled from
complete K-bit neighborhoods in the globally complete binary tensor.
Their bits are not assumed zero or semantically independent of coefficient
values. Completeness means every coordinate value is represented in the
stream. Multiplication by previous coarse-dependent diagonal coefficients
does not remove any address or change this property.

Deferring the selected bits lying in reserved chunks is valid: the accepted
active invocation is the desired tensor on the other selected bits and
identity on every reserved coordinate, for arbitrary incoming coefficients.
The preliminary individual transforms in the old layout were used to
finish those selected bits, not to create complete row or control ranges.
After deferral, those transforms are performed in later phases instead.

The row count is rounded once to a multiple of the actual product

```
Q_rows = W_complex^D_complex * W_bit^D_bit.
```

The padded row label is allowed to be a nonbinary preceding fiber count.
Every within-row field remains a full binary field. The supplier's
interchanges and controls act within those complete fields; the global
exposure router is not applied to the padded row label. Nested bit adapters
consume and restore the bit stock before later complex splits, exactly as
in the retained product-stock argument.

At the completed invocation boundary, the operator is identity on the row
label. A padded zero row therefore returns to zero even though temporary
role computations may have combined or moved its contents. Delete those
rows before inverse exposure or the next deferred phase. This bounds each
phase's volume by twice its original volume, not by a factor exponential in
the number of phases.

All H calls in the compiler have the same selected-bit schedule for every
coarse label; label dependence resides in the intervening diagonal tables.
Run one H call on the complete global tensor, complete every deferred
phase, remove padding, and restore the original exposed-coordinate order.
Only then run the next diagonal scan. The microbox layout used for that
scan is the restored layout in which the local coordinates are already
contiguous (or the separately paid low-bit gather layout). No padded row,
partial H result, or temporarily relocated coarse label is presented to
the diagonal-table lookup. Thus scanning different coarse-label tables
does not require separate H invocations or borrowing fixed labels inside
a microbox.

## 4. The actual parameter inequalities

The largest exposure moves k=O(gK)=O(p^.093 log p) binary coordinates.
With G=Theta(log p), its three dirty reservoirs require

```
9kG = O(p^.093 log^2 p) = o(p).
```

The suffix occupies only L=Theta(log^2 p) positions. In particular,

```
n/(kG) = Omega(p^.907/log^2 p) -> infinity,
n/((k+1)L) = Omega(p^.907/log^3 p) -> infinity.
```

There is ample room both for the old spectator placement and for all
subsequent prefix-only reservoirs. These inequalities concern the full
binary address, not any one original axis.

The only per-axis inequality is

```
K + O(log p) < ell_axis = Theta(p^.002),
```

which holds eventually. The original K/log p -> infinity wording must be
replaced, as already noted in `SUPPLIER-SUPPORT-AUDIT.md`, by the finite
guard inequality K>=G+4ceil(log2 p)+10. K=128G satisfies it.

The supplier's front/back controls are made by concatenating reserved
complete neighborhoods. Their chunk count is

```
ceil(2hG/K) + ceil(hG/K) <= 3h/128 + 2.
```

The leading row stock adds O(log h) complete chunks. Above a fixed
polylogarithmic cutoff this is at most h/16, and smaller h is handled
individually. No single original axis stores hG control bits. Indeed
gG/ell_axis=Theta(p^.091 log p) diverges; the construction works precisely
because it does not demand this false per-axis fit.

Consequently the reviewed mechanisms support the proposed
O(V g^(1-q) polylog p) global-call cost under the retained supplier
assumptions. The suffix exclusion and completed-call boundary should be
kept explicit in any final assembly. They are necessary bookkeeping,
not a new exponent restriction or an unproved sorting primitive.
