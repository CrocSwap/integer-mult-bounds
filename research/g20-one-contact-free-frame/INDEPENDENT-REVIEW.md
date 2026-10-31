# Independent review: one contact with a freely chosen correction frame

Reviewer: @CubeJerry with substantial OpenAI Codex assistance (worker D).
Frozen source base: `2485805a6d47f36ea83ddde6327d453ac82d44dc`.
The reviewed scalar source is the final 685-role word of
CrocSwap/integer-mult-bounds#5708. **No new κ.**

## Local-update theorem

Moving the sole inserted A2 correction to another chart does not change its
normalized linear row operation, once both operands are routed to that chart.
Thus every row's zero/nonzero status is unchanged. For each correction operand,
only its incoming frame demand and its next outgoing demand can change: after
that next demand its actual frame is again the original fixed frame. An owned
ERASE or INIT may instead reset the frame, in which case no outgoing paid
transition survives. A final public return is a genuine next demand and must
be charged. These statements hold independently of the particular route used
for each frame demand under the inherited invertible frame interpretation.

I inspected the primary adjacent-demand update. Its trace includes the actual
start frame, every non-skipped ADD demand, owned resets, and every public final
return. Each demand records whether its entire normalized row is nonzero at
that time. The incoming cost uses the correction operand's pre-correction row;
the outgoing cost uses the next demand's row, after the ADD and all intervening
operations. Therefore a zero destination, a cancellation to zero, an owned
reset, and a final return are distinguished correctly. The two operands are
distinct, so their demand traces do not overlap. Replacing the correction
chart changes precisely these incident terms, with no uncharged return or
implicit source access.

## Independent exhaustive computation

`independent_symbolic.py` imports no primary construction, trace or invoice
code. It uses the separately computed 645×645 integer distance fixture whose
decoded hash is
`4e0b9aad61d7d3c9bc249c76dce0729a65216ae7bb2613c060ab2e6cd31f4a3f`.
The fixture's derivation by independent rational RREF inclusion and bucket
shortest paths, and its equality to the fresh primary metric, are checked
separately. The checker pins the original source word bytes.

First it independently scans all pairs of equal original ADDs, rejects operand
resets and reversed contacts, and retains exactly the 184 intervals with one
noncommuting contact. It reconstructs each correction and its exact index in
the rewritten scalar word. All 685 initial roles are independent formal input
sets; ADD is symmetric difference and only legal owned operations erase rows.
The complete expected endpoint is checked for every rewritten word.

For each word, the checker performs a **full chronological symbolic-chart
replay**. At the correction it assigns its target chart the formal variable X.
It carries X through the actual state of each operand until a later demand or
owned reset overwrites it. Every paid transition is collected either as a
constant rank term or a symbolic request involving X. It then substitutes
each of the 645 catalogue frames into those expressions and constructs the
whole invoice from its constant and symbolic terms. It does not obtain new
bills by subtracting and replacing incident terms in a pre-existing bill.

All **118,680 assignment keys and exact signed invoices** agree with the
primary receipt. There are 245 distinct shapes. Each of the 184 programs has
four symbolic paid demands in this particular source; this is measured, not
assumed by the symbolic interpreter. Additionally, four deterministic frames
per interval are replayed numerically from the start, for **736 complete
chronological replays**. Their endpoints and invoices agree with symbolic
substitution. Normal and optimized isolated Python executions produce identical
receipts.

## Signs and precise scope

The shared native graph floor gives, for every finite route with edge ranks
r_i and every `0<t<1`,

    sum_i r_i^t >= (sum_i r_i)^t >= d(source,target)^t.

A separate direct multiset check inside the symbolic verifier confirms every
partition occurrence, target, multiplicity and strictness flag. The 244
partition-certified shapes are strictly positive by disjoint rank
coverage, monotonicity and strict subadditivity. The remaining shape occurs
exactly three times and is

    H_3 + H_4 - H_2 - H_5,  where H_r=r^t.

For `0<t<1`, `f(x)=x^t` has strictly decreasing derivative. Consequently
`f(3)-f(2) > f(5)-f(4)`, so this exceptional shape is also strictly positive.
Its assignment keys `(left,right,correction_index,frame)` are
`(6089,6567,6354,338)`, `(6074,6582,6401,440)` and
`(6093,6563,6342,410)`. There is no numerical sign assumption or near-zero
rounding issue. All 118,680 assignments have strict lower paid-query loss.

This result permits a changed chart for one correction, unlike the separate
fixed-chart neutral-first two-step theorem. It does not cover multiple
contacts with independently selected correction charts, relocation in time,
new frame spaces, altered ownership or targets, shared/cancelled routes across
separate demands, other scalar identities, or arbitrary-depth rewriting.
The lower-bound relaxation does not optimize ordinary scalar work or prove a
new native/caller supplier. The five selected-frontier assumptions remain
inherited.

## Controls and reproduction

Seven controls detect a missing assignment, an altered invoice, a duplicated
assignment, a zero source that must omit both symbolic demands, a zero
destination whose source still pays its final return, dirty owned
initialization, and reuse of a positive partition occurrence. The checks are explicit exceptions and remain active under
Python optimization.

```sh
python -I independent_symbolic.py --word WORD.json.gz --metric inputs/DISTANCES.json.gz --certificate RESULT.json.gz
```

Use the exact source paths and registered reproduction command in the package.
Credit the lead's adjacent-demand construction, worker B's native geometry and
independent metric, and Ali Romman, unpaidmoon, Nick Petalas and their retained
predecessor lineage. Prepared for @CubeJerry with substantial OpenAI Codex
assistance.
