# Formal semantics and source boundary

This package formalizes the nonlinear binary-commutator induction written in
PR628 and independently audited in PR663. The resource optimum from PR784/887
is a different statement. Here the question is what a completed recursive
call does to arbitrary initial source, target, and borrowed data.

## Values, leaves, and disjoint storage

`Value width` is `Fin width → Int`: an integer array of arbitrary finite width.
A common fixed-point grid is represented by an external common scale; complex
arrays can be represented by their integer real and imaginary coordinates.
Addition and subtraction are componentwise. The proof uses their exact group
identities, not any analytic estimate or floating-point arithmetic.

`f : Nat → Value width → Value width` assigns an arbitrary deterministic map
to each leaf label. It can be nonlinear, non-zero-preserving, discontinuous,
and can mix coordinates. Fixed coefficient, phase, orientation, and precision
parameters may be captured in this function. They must remain fixed across
paired calls. A positive completed leaf adds `f label source` to its target;
a negative leaf subtracts the same value.

The completed-leaf interface assumes that each leaf restores its source and
does not consult its target while computing the increment. This proof does
not establish that property for PR628's numerical `lift` implementation.
The source is accordingly an immutable argument of the formal evaluator.
`full_execution` includes that source in the returned state, but its source
part is an interface assumption encoded by the model, not a new proof about
the leaf's temporary source writes.

`Tree depth` contains a leaf label or two children at the next smaller depth.
Leaves may leave capacity unused. `Dirt width depth` contains a separate array
at each reserved level. The parent connector is the head, and both children
reuse the disjoint tail. Source, target, and scratch are distinct typed
components; equal *contents* are allowed. Aliased mutable locations and
stateful callbacks are outside this model.

## Literal recursive execution

The positive `run` evaluator performs four completed child calls:

```text
(z1, t1) = left +(x, z0, t0)
(y1, t2) = right +(z1, y0, t1)
(z2, t3) = left -(x, z1, t2)
(y2, t4) = right -(z2, y1, t3)
return (y2, z2::t4)
```

Its negative branch uses the complete reversed word with inverted signs:
`right +; left +; right -; left -`. The intermediate scratch states are
passed explicitly. They are not silently reset before the next child.

For arbitrary nonlinear leaves, the increment is defined recursively by

```text
delta_leaf(x,t) = f_label(x)
delta_node(x,z,t) = delta_right(z + delta_left(x,t), t)
                   - delta_right(z, t).
```

`run_eq` proves by structural induction that the positive result is
`(y+delta,scratch)` and the negative result `(y-delta,scratch)`. It quantifies
over all finite trees, widths, arrays, and maps, with no linearity premise.
The cancellation is valid because the induction hypothesis restores the
deeper pool at each intermediate call. Consequences include exact restoration
of all scratch, target independence, and cancellation in both execution orders.

Under the separate premise that every leaf map is additive, `delta_eq_product`
proves that the increment is the ordered composite of all leaves. At a node
the right composite is applied after the left composite. The proof uses
additivity and cancellation; it never interchanges factors. This covers
noncommuting additive maps on multi-coordinate arrays. Initial dirt disappears
from the ideal formula, whereas it need not disappear for nonlinear maps.

`nonlinear_dirt_counterexample` kernel-checks the latter distinction. With
`f0(x)=x`, `f1(x)=x²`, and `x=1`, the two increments are 1 and 3 at initial
connector values 0 and 1. Both calls still restore the connector exactly.

## What the executable binding proves

`positiveWord` lowers the same recursive four-call grammar to explicit
factor/source/target/sign records. `inverseWord` reverses the whole list and
flips signs. The universal `negative_node_order` theorem checks that this
negative lowering has the same child order as the negative evaluator.

The pinned Python `compose` function is extracted unchanged from its AST;
its top-level imports, arithmetic leaf, and preparation code are not executed.
A completed-leaf stub records actual source and target list identities and
performs the specified integer-array shear. The six vendored files are checked
against SHA256 and Git-blob identities before extraction.

For factor counts 1..64 and 83, both actual dispatcher traces agree with the
independent lowering. Lean additionally checks the complete source-derived
instruction lists for counts 1..16 and 83 by definitional equality: 34 trace
theorems, with no axiom dependencies. These include all 7,744 instructions of
each 83-factor sign. The generated literals come from the actual dispatcher,
not from the reference emitter.

Execution checks compare the mutable source dispatcher with a functional
transcription of `run` and the independent `delta` recurrence. A separate
instruction-list interpreter checks all 197 ordered binary trees through
seven leaves, including strongly unbalanced trees. Floor maps, bounded square
maps, and noncommuting integer shears exercise widths 1..3 with nonzero signed
initial dirt and targets. Both signs and full inverse cancellation are checked.

This is a universal proof of the typed recursive evaluator and bounded
evidence connecting it to the address-level lowering and Python dispatcher.
An all-size denotational correctness proof for the address compiler and a
formal semantics of Python remain separate obligations. Literal trace equality
alone is not a proof of the numerical leaf's correctness. In particular, the
known phase-alias admission gap in the unmodified PR628 source is not repaired
here; callers must satisfy the fixed, nonaliased external-data contract.

Rounding accuracy, coefficient preparation, physical bit/tape execution,
multiway echoes, connector reuse, cost optimization, and the multiplication
reduction are outside this result. The selected conditional κ is unchanged.
