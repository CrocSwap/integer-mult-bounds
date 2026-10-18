# Whole-helper neutral paths remove seven rank-7 residuals

## Construction and exact domain

This is a successor to Rohan Arun's selected PR1094 owner assignment. The local
provider (480 whole helpers per call), 144 complete calls, port set, orientations,
all source events, endpoint adapters, global bridges and terminal corrections
are fixed. Only the physical owner and coordinate offset of whole helper roles
change. `CONSTRUCTION.json` gives 24 moves in eleven rounds. Prefix compaction
changes 47 serialized role rows. It is part of the construction, not a free
post-processing convention: the native emitter rebuilds every affected chart.

A bin is `(owner replica, idle child, port)`. Its capacity and strict borrowing
interval are the original idle transition. The invocation has to lie after the
last source-event touch and before its idle deadline. The native lift and two
owner audits recompute those intervals from the original source events,
including all 144 bridges; the search uses the corresponding pinned plan.

For a gap of free rank y, a helper of width w in a bin of free rank x can move
into the gap if its whole invocation lies in the destination interval, its
physical family is unused by every other helper in that invocation, and w<=y.
The new free ranks are `(x+w,y-w)`. A neutral leg satisfies `x+w=y` and exchanges
the two free ranks. The final leg satisfies `x+w>y`, strictly concentrating them.
No helper is split; all local entry/exit interfaces are retained.

The first round moves width-seven helper roles 1664, 14144, and 34306:

```
(12,0,90) -> (1,0,0)
(15,0,72) -> (12,0,90)
(11,8,103) -> (15,0,72)
```

The first two moves transfer a free-rank-seven gap through full bins. The last
replaces free ranks `1+7` by `8+0`. Later rounds collect the remaining rank-seven
gaps. The final idle profile changes exactly by `{1:+1,7:-7,16:+3}`. Rank mass is
conserved: `1-7*7+3*16=0`.

## All-input operator argument

Use the inherited exact local supplier contract: a complete invocation applies
its stated data shear, independently of all incoming helper values, and acts on
each dirty helper by its declared residual Clifford operator. Private work is
erased at the endpoint. This holds on all columns, hence on arbitrary correlated
dirt, not only independent or clean helper inputs. The source-bound native local
proof/phase receipts are unchanged; the new global run binds their exact hashes
and semantic identities rather than assuming a favorable histogram proves them.

Inside one borrowed bin, the owner has no data touch between the interval's
opening event and its idle deadline. Consecutive whole invocations can therefore
observe arbitrary transformed dirty values; each invocation's data output is
independent of that dirt, while the owner's residual transformations compose.
For its fixed orthonormal pending axes q_0,...,q_(c-1), the contribution of an
assigned width-w role is the exact product of C_q over its assigned slice, using
the admitted source/target wrappers. The residual idle child acts on the unused
suffix. Distinct slices partition the same original c axes. Thus at the deadline

```
(product over assigned helper slices) * (remaining suffix child)
  = product_(j=0)^(c-1) C_(q_j).
```

These exact Gaussian-dyadic factors commute. Chart changes are actual inherited
orthogonal adapters, including their Z4 phase translations and spectator
normalization; they are freshly emitted and checked. The proof never identifies
operators merely from binary frames. There is no movement of an idle factor
past a bridge, unlike the rejected earlier phase-flow attempt.

By induction over deadlines and data touches, every physical owner's value is
exactly the original value whenever the controller reads it. Each complete
invocation has the original data shear on arbitrary incoming helper values.
The original eight-stream operator, dirty-state endpoint, source restoration,
terminal Y correction, signed exchange and cover corrections consequently remain
identical on all inputs. This uses the inherited complete-cover/common-label and
mutable-source realization assumptions; it is not a new proof of those interfaces.

## Exact cost improvement

For every real `0<a<1`, `f(r)=r^(1-a)` is strictly concave on nonnegative r.
A neutral leg leaves `f(x)+f(y)` unchanged. If `x+w>y` and `0<=y-w`, then the new
pair has the same sum and strictly larger maximum; hence
`f(x+w)+f(y-w)<f(x)+f(y)`. Each of the eleven rounds has one such strict leg.
This is a uniform analytic proof of the moment improvement, not a floating-point
search score. The final complete profile is

```
{1:349605, 2:60192, 3:62585, 4:20448,
 5:11808, 8:1152, 16:3, 48:4866}.
```

The new boundary does not add calls, helpers, data families or conversions.
Recompacted offsets change only the existing chart selection. Native recounting
charges all adapters, phases, normalization, bridges, wrappers and the retained
full idle-child overcharge. Live stock 14336, physical stock 14826, rank mass
1041408 and deficit 5120 remain fixed. The independent owner checker additionally
uses a conservative historical reserve of 14850, which has the same 2642-bit
stock bound; it does not assert that larger reserve is the emitted stock.

The prefix bound is 397 bits, charged within the unchanged 512-bit allowance.
The physical row coefficient is 16469<20161. The maximum child stays 48 and
`73^2=5329>4608=2*48^2`. The native complex surcharge remains absent under the
selected exact-cover contract; the complete bit surcharge is retained. The
conservative complex surcharge variant is checked separately and also improves.

## Scope

This establishes a finite conditional construction under the inherited all-size
compiler, common-label/mutable-source realization, whole-call hosting,
precision/tape, exact recovery, analytic transfer and bit H1-H5 assumptions.
It is not a full multiplication theorem, formal Lean proof, global packing
optimum, or claim of a new hosting principle. A failed two-role-swap nomination
is retained separately and makes no universal obstruction claim.
