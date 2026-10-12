# Full theorem target and proof obligations

The active objective is to finish the full Lean proof. This package is progress
on that objective; neither the package build nor any finite certificate completes it.

## Frozen target

Main at `db0e57bc7f36b5ac0fc844ad7ce1396165ee6647` selects the reviewed
PR531 complex supplier with the PR493 bit supplier. The target saving is
`1517760977820331 / 1000000000000000000`.
The source statement in `upstream/build/sections/00-introduction.tex`,
`thm:main`, specifies the machine and output convention; the selected composition
replaces its historical exponent, not its computational model.

Required final statement: one deterministic Turing machine with a fixed finite
alphabet and a fixed finite number of one-dimensional tapes, for every `n ≥ 1`
and all length-`n` Boolean strings `x` and `y`, halts on `x#y` with exactly the
length-`2*n` padded binary representation of `val(x) * val(y)`. There must be
constants independent of the input and its length bounding worst-case elapsed
machine steps by `C*n*(max(ceil(log₂ n),1))^(1-kappa)` for all sufficiently large
`n`. The implementation must also handle all smaller input lengths correctly.

A conditional theorem which assumes its missing compiler, routing, numerical
correctness or runtime estimates does not satisfy this objective. Those results
must be proved and connected to the same actual machine. A weaker historical
exponent, abstract operation counter, average-case runtime or different machine
model is not a substitute for the target above.

## Current dependency audit

| Obligation | Evidence now | Still required |
| --- | --- | --- |
| Width assignment and block arithmetic | `WidthMatching.lean`: executable first-fit matching succeeds from sorted dominance; arbitrary stateful admissible policies preserve feasibility. `OwnerTransport.lean`: capacity, address injectivity and occupied-prefix coverage. | Connect the actual Python selector and its owner/capacity representation to this verified interface; establish its old-to-new assignment relation. No selector runtime bound is proved. |
| Selected finite ownership | `PR531TableCertificate.lean` certifies all 36,288 literal rows, complete helper census, actual offsets/capacity and inverse group/family indexes. `PR531ScheduledOwners.lean` proves distinct owners for all 728 registers of every selected invocation. | Python still projects source JSON and associates primary-wire formulas/helper routes. Connect the formal owner map to actual physical charts and event execution. |
| Complete selected word and physical streams | Incorporated PR509/PR516 prove general event/label realization under stated hypotheses; main retains finite Python audits. | Instantiate their hypotheses for all selected bit and complex instructions, arbitrary dirty helpers, exact recipes, complete rows/columns, and actual physical owner charts. Generic realization alone is insufficient. |
| Whole execution schedule | `PR531Controller.lean` certifies the projected 242-event trace, all 144 borrowing windows, idle deadlines, untouched interiors, exact admitted call sets and same-lane window separation. Every literal helper is inside its traced window. | Prove the trace model describes physical execution, then instantiate commutation/gathering, full-replica scheduling, endpoint states and actual costs for the complete word. |
| Uniform compilation and tape movement | Original source sections 02–06 describe complete-range layouts, routing, signed arithmetic, recursion and transforms. | Implement and verify all sizes on the fixed finite-tape model. Derive the recurrence normalization by logical volume and its setup/parking/return costs from actual execution. |
| Input, radix, convolution and output | Input preparation/counting PRs provide scoped machine components; source sections 06 and 08 specify assembly. | Reuse checked input modules, prove radix/carry conversion, convolution identities, final padded output and finite-input fallback; compose the same tape machine's endpoints and time bounds. |
| Precision, resampling and prime supply | Source sections 07–08 and the selected invoice give conditional numerical/analytic estimates. | Formalize the required resampling maps, prime existence/construction, finite-precision errors, recovery and all parameter cutoffs. Do not import them as unproved project axioms. |
| Analytic transfer and final exponent | Main retains exact rational/moment certificates and 47 outer inequalities for the selected composition. | Prove the analytical certificate interpretation, recurrence/asymptotic transfer and all hypotheses from the verified machine, then derive the stated exponent. |

## Next proof integration

The literal source certificate and controller-window checker now provide the
finite ownership and window interfaces. The next semantic boundary is actual
physical execution: tie the 728-register owner map and complete local word to
PR516's hosting/charts, exact recipes, row/column endpoint hypotheses and
supported operations, then apply its asynchronous gathering argument to the
certified controller. Source JSON parsing/projection remains an explicit
external reproducibility boundary. Neither that boundary nor physical
correctness is discharged by the finite checks alone.

The selected kappa and full machine requirements remain frozen throughout this
work. Newer PRs can inform methods, but switching the theorem target requires an
explicitly recorded mathematical reason rather than treating a smaller passing
module as completion.
