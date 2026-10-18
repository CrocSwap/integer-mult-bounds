# Complete owner-path improvement

## 1. Fixed inputs and what changes

Fix the PR2322 supplier at commit
`002304ef01c4416a127916169ae6d94c1bee052b`. Its two local native words, 666-call
order, 74-replica data recipe, actual owner windows, helper widths and local
paid profiles are unchanged. Every call has 434 complete helpers. A pending
bin is an owner replica, source child and physical port, with capacity at most
48. A role is identified by its invocation and compact helper index. The
witness moves whole roles between these bins; it never splits a helper across
families, changes its width, or changes its local program.

The canonical source owner list provides stable role indices. `construct`
replays the exact paths in MOVES.json, checking their connected order, distinct
bins and named endpoints. A step moves one role of width w into
an available slot, checks the actual invocation window and distinct physical
family, and frees a width-w slot in its previous bin. Prefix offsets are then
recomputed. The separate inherited owner checker reconstructs windows from
literal source events and checks every field of the final assignment.

For a width-preserving path, every interior bin loses and receives one role
of the same width. Thus its total occupancy, idle rank and recursive price
are unchanged. All path operations are changes to the compile-time assignment,
not extra scalar operations in the executed word. The complete controller,
routing, prefix and row charges still receive fresh admission.

## 2. Forty-three complete composite exchanges

Each composite has four distinct endpoint bins with initial idle ranks
`(7,7,0,5)`. The first two are rank-16 bins containing one width-9 role. The
third is a rank-32 bin containing widths `(7,7,9,9)`. The fourth is a rank-32
bin containing `(9,9,9)`.

Two width-7 alternating paths move the two width-7 slots from the third bin
into the first two bins. A width-9 path then fills nine coordinates of the
third bin from the fourth. The final endpoint idle ranks are `(0,0,5,14)`.
Interior bins are unchanged. Therefore the **complete** profile change per
composite is `-2 H7 + H14`. The intermediate width-7 steps alone are not
credited as gains. Their entire composition, including the newly idle width,
is checked before accounting for the saving.

There are 43 actual composites in the certificate. Since
`14^p = 2^p 7^p < 2 7^p` for every `0<p<1`, each strictly decreases the complete
power sum without changing rank mass, supplier count or physical stock.
The favorable identity is already present in PR2309; the contribution is the
new full assignment on the stronger pinned supplier.

## 3. Fifty-three further complete transfers

A subsequent width-w path starts at a bin with idle rank R and ends at a bin
with idle rank S. Its exact exit ranks are `(R-w,S+w)`. The checker requires
`R>=w>0` and `S>R-w`, as well as all actual path constraints.

Write x=R-w. Then S>x and the old ranks are `(x+w,S)`, while the new ranks
are `(x,S+w)`. For `f(t)=t^p`, `0<p<1`, the increment `f(t+w)-f(t)` is strictly
decreasing in t on `[0,infinity)`, including t=0 by continuity. Consequently

```
f(x+w) - f(x) > f(S+w) - f(S),
```

or `f(R)+f(S) > f(R-w)+f(S+w)`. Every such fully charged transfer is strictly
beneficial for the entire relevant exponent interval, not just at one sampled
κ. The first 17 transfers realize `H1+H4 → H5`; the remaining 36 transfer
width-9 roles. MOVES.json records each old and new endpoint budget. Intermediate
bins keep exactly the same paid rank. No unpriced helper deletion is used.

The combined profile difference from PR2322 is

```
{1:-17, 3:+1, 4:-17, 5:+46, 7:-86,
 12:-1, 21:-1, 23:+1, 32:+13, 48:+1}.
```

It has zero rank mass. The complete final histogram is

```
{1:1576962, 2:340992, 3:292196, 4:79920, 5:28004,
 7:1, 8:5328, 23:1, 32:13, 48:24546}.
```

All 289,044 roles and all 1,332 owner windows are checked after composing the
paths, not merely one exchange at a time.

## 4. Native moment and outer admission

For dimension m=73, live count W=66304 and the complete histogram H, define

`F(b) = sum_r H_r (r/73)^(1-b) / 66304`.

Every occurring r satisfies `0<r<73`, so F is strictly increasing. Its rank
mass is 4,816,512, giving deficit `73*66304-4816512=23680`. The unchanged
source-directed integer log/exp engine proves

```
F(0.001697147064845350) < 1 < F(0.001697147064845351).
```

This is a rational interval certificate, not a floating-point root estimate.
The source positive control reproduces PR2322's complete profile. Corrupting
roles, widths, addresses, deadlines, offsets, path edges or endpoint bills is
rejected. The published root bracket is distinct from the final outer point.

`full_replay.py` regenerates all changed input bindings, invokes a source-bound derivative of the
PR2322 driver and PR2312 runtime with four exact PR2349 pricing files, and requires the complete
physical invoice to equal this H. Both original source inventories and all
reused baseline/native evidence must pass the inherited checks. Discovery
freezes a newly computed SPEC; strict mode then recomputes it, checks physical
phases and controller/owner bindings, and runs the retained fine-prime outer.
The wrapper requires

`κ(PR2322) < κ(published) < κ(admitted outer)`

and the inherited bit endpoint. The completed execution status and exact receipt
are recorded in VALIDATION.md and evidence/FULL-ADMISSION.json. The bounded
verifier authenticates the strict assembly and outer ledger, binds the complete
owner digest, and checks the admitted outer point against the exact native moment.

## 5. Limits

The final invoice additionally charges 78 dedicated zero buffers, their CLEAR
operations, every warp-routing reserve and the expanded adapter work, following
PR2349. Physical stock is 66,826. These are nonrecursive charges; the native
words, complete recursive histogram, moment denominator and bit endpoint stay
fixed. The changed strict invoice and outer admission are rerun under these
charges. The wrapper requires the actual stock and buffer count explicitly.

The unchanged ideal fractional rank-48 idle packing cap from PR2322 applies
because total idle mass, the local words, call count and allowed maximum rank
are unchanged. Its upper endpoint is below `0.001720061111244974`. The checker
reconstructs its entire weighted histogram before checking the directed upper
endpoint. This gives a scoped ceiling, not attainability or global optimality.

The search greedily finds explicit paths and is not claimed exhaustive over
all feasible reassignments. Finite construction and outer admission remain
conditional on the inherited premises listed in README.md. No universal
multiplication theorem, practical threshold or independent human review is
claimed.
