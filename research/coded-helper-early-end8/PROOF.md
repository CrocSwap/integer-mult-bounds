# Retimed helper endpoint and complete favorable cost bound

This is a fixed-program common-frame result, not a theorem about every
reversible multiplication algorithm. Let P denote the invertible scalar map
at the end of B, after input compensation, in one pinned PR855 word. Let h=448
be its fresh coded helper. All payload values, including helper dirt, are
independent. Scalar gates on non-target registers never read a target register;
the initial precondition and generated compensation update targets only.

## Exact cleanup row and minimum endpoint

Multiplying the h-th output row by inverse elementary matrices in chronological
order gives the h-th row of P^-1. Target-only prefix operations have no effect
on that row. It has exactly three nonzero entries:

```
e_h^T P^-1 = e_h^T - e_s^T - e_t^T.
```

For positive embeddings `(s,t)=(431,447)`; for negative embeddings they are
`(50,82)`. An independently implemented row replay verifies the inverse-row
identity against the complete scalar word. Consequently the two operations
`h -= s; h -= t` restore the original helper value at end B. Every other
remaining cleanup gate is independent of h. Removing the old two h-targeted
full-frame gates and doing these reads first therefore preserves all endpoints.
The inherited auditor separately checks every arbitrary input column in both
orientations after the transformation.

Let F_h,F_s,F_t be their end-B frames. In all four words, their join U has rank
eight (canonical raw basis `[256,128,64,32,16,8,6,1]`). Each operand frame is
contained in U, so the two reads have a legal common frame. The helper can stop
there; the other registers may subsequently climb to their original final
frames. Two new early-cleanup entries run before final climbs; retained entries
are renumbered after removing the old gates. Failing to update those entries is
a rejected frame/admission mutation, not a valid early-end construction.

This also establishes a rank-eight lower bound for *any remaining monotone
common-frame cleanup at this same end-B boundary*. If the helper finishes at W,
it must contain F_h. Its final scalar row has nonzero coefficients on the
independent end-B variables s and t. Neither variable can reach that helper
through a chain of common-frame gates unless W contains its initial frame.
Frames cannot shrink. Thus W contains F_h+F_s+F_t=U and dim W>=8. Auxiliary
mixing after B cannot evade that argument. Changing the earlier word, frames,
representation, noncoordinate primitives or restoration contract is outside
the statement. No global frame or reversible-program optimum is claimed.

## Respect the cold-helper wrapper interface

A cold helper must not be read by the caller's zero-frame precondition or
automatically derived compensation before its entry wrapper. Simply declaring
the shorter endpoint fails that guard. Compute its dirty-response column q in
the input target chart. Put the additions `target -= q_target * h` at the start
of A, inside the wrapped child. Because the target chart and main target block
are inverse, these additions cancel the main word's helper-dirt response.
The external zero-frame compensation no longer reads h. Other dirt columns are
unchanged. The exact all-column native replay independently certifies this
calculation; omission of the premix is a negative control.

No helper is cleared by erasing arbitrary information. The new word restores
its dirty helper exactly. Its logical child width is eight, because the helper
starts at bottom and ends at U. This is native scalar/frame evidence. New phase
lowering and residual-wrapper compilation are separate obligations, not inferred
from this finite replay. They are unnecessary to a favorable *cost rejection*.

## Price the source climbs too

Relative to each corresponding PR855 word, the paid local change is

```
4 H1 - H2 - H3,
```

and one width-nine helper becomes width eight. The helper's final climb is
split differently, and both source streams must reach U for the early reads;
their later climbs are still paid. At rank-mass exponent one, the local mass
falls by one, while the global idle mass increases by one. There is no new
rank deficit. Extra pointwise premix/preparation/access work is not assumed
negative or credited as a saving. The cost lower bound grants it for free.

## Complete packing relaxation

Keep PR626's fixed geometry: 72 calls, m=73, live=7168, rank deficit=2560 and
the data capacities 8/16/32/48. Recount capacities separately from the plan's
windows and all native data recipes. At any call choose the original provider,
the original positive/negative PR855 replacement, or its new early-eight
positive/negative replacement. Deltas agree for ck and jp8, so four counts
suffice. Every nonempty count vector whose sum is at most 72 is included:
`binomial(76,4)-1 = 1,282,974` mixtures.

Drop all windows, call labels and physical-family restrictions. Helpers still
occupy their full audited widths in capacity slots. Allow every integer width
multiset fitting a slot, including empty slots. Charge any residual rank with
one child; splitting it costs at least as much for 0<s<1 by concavity. This
relaxation is strictly favorable to candidates; it does not construct owners.

Reuse PR855's explicitly pinned rational lambda and 37 potentials as witnesses,
not as solver authority. With `s=1-b0`, `phi(r)=r^s-r`, width and capacity scores
as in that certificate, an independent Cartesian-product census enumerates all
1163 patterns. For every pattern and every residue j it freshly checks

```
phi(residual) >= lambda*score(pattern)
d[(j+score(pattern)) mod 37] - d[j]
    <= phi(residual)-lambda*score(pattern).
```

Telescoping over a packing lower-bounds idle cost by
`idle_mass + lambda*S + d[S mod 37]`. Add the complete audited local profile.
Each variant's local, idle and score changes are linear; rank mass remains
520704. A positive profile coefficient uses the lower power endpoint, while a
negative coefficient uses the upper endpoint, so removed costs retain a
conservative lower bound. The checker proves nonnegative inventories for every mixture first.

The new DP stores the minimum linear change for each number of modified calls
and residue. Extending a state by each of four variants enumerates every count
vector; order is irrelevant to its invoice. Merging equal states keeps the
lowest bound. Checking every reachable state for k=1..72 therefore covers all
1,282,974 mixtures, rather than sampling them. There are 2548 reachable states.
All their lower bounds exceed `7168*73^(1-b0)`. The least certified excess is
strictly above **0.018922942318** at one negative early-eight replacement.

## Independent real-power enclosures

The proof does not trust the predecessor's logarithm/exponential engine.
For r>1 set z=1-1/r and a=b0. The binomial series has

```
(1-z)^a = 1 - sum(k>=1) c_k,
c_1=a*z,
c_(k+1)=c_k*z*(k-a)/(k+1),
```

with all c_k positive and every ratio below z. After N terms the omitted tail
is at most `c_(N+1)/(1-z)`. Propagate outward integer intervals at scale 10^44
through 7000 terms, sum their lower/upper endpoints, subtract the appropriate
geometric tail and round outward at scale 10^30. Multiplying by r encloses
`r^(1-b0)`. No float, logarithm, exponential or predecessor power implementation
is used. Exact square-root identities at a=1/2 give separate positive controls.

## Comparison with the pinned selected target

The inherited balanced assembly has `a<b` and `kappa<a/(1+a)`, hence
`b>kappa/(1-kappa)`. The pinned PR799 target is
`1661634653669567/10^18`; its necessary complex saving is strictly above b0,
the excluded historical PR626 endpoint. All child ranks are below m=73, so
each normalized term `(r/m)^(1-b)` increases with b. Failure at b0 therefore
excludes every larger complex saving in this fixed model, including the saving
needed to match that target. This does not audit or refute PR799's different
construction, or rule out another geometry, coded core, compiler or invoice.

The source/input pins, exact complete model, native receipts, constructions,
potential checks and minimum-state witness are reproducible. All-size/compiler,
physical hosting, analytic transfer, precision and tape assumptions remain.
The full multiplication theorem is not formalized or proved here.
