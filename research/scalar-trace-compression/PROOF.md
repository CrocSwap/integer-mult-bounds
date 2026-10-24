# Exact logical rewrites and their physical execution

Prepared for Cinna Davis with substantial OpenAI Codex assistance; Apache-2.0.

## Equal elementary matrices

An ADD a += alpha*b has matrix I+alpha E_ab. Two ADDs commute if the first
destination is not the second source and the first source is not the second
destination. Repeated ordered pairs combine by adding their coefficients;
a zero sum deletes both instructions.

The scan records writes to each source, reads of each target and other touching
events. It combines gates only across instructions commuting with the repeated
ADD. Phases and touching warps, scales and non-ADDs are barriers. Transports
preserve logical values and are rebuilt afterwards. Stale history after a
deletion may reject legal combinations but cannot admit an illegal one.
There are 70 combinations, including 28 cancellations: 42+2*28=98 removed
ADDs in each orientation.

## Noncommuting triangles

For three distinct roles, execute each line left to right:

```
a += alpha*b; b += beta*c; a -= alpha*b
    = b += beta*c; a -= alpha*beta*c.

a += alpha*b; c += beta*a; a -= alpha*b
    = c += beta*a; c += alpha*beta*b.
```

In the first identity the net changes are -alpha*beta*c on a and beta*c on b.
The second restores a and adds beta*a+alpha*beta*b to c, using original input
values. Both hold for arbitrary rational coefficients and independent inputs.
No zero helper, Gaussian commutation or order-two complex phase is assumed.

Intervening instructions must touch none of the three roles. Their order is
preserved; modified regions cannot be reused. Lookahead is bounded at 180
instructions, with no optimality claim. There are 18 accepted triangles per
orientation: four of the first kind and fourteen of the second forward, with
counts reversed backward. Each removes one ADD, giving 116 removed macros.

## Physical execution and complete accounting

A field at frame f stores C_f times its logical value. A transport changes
this reference while preserving that value; an ADD requires exactly common
physical operand frames, under the retained native contract.

A triangle's first contact space must lie in the middle space, which must lie
in the last. Both replacement ADDs use the middle frame. Every transport is
rebuilt from its actual preceding reference; a non-nested or empty paid edge
is rejected. All warps, center episodes, residual adapters and terminal frames
are retained. Logical equality alone is not the physical certificate.

Both retained native interpreters execute the actual candidate on all 632
arbitrary persistent columns. Owned C0 is arbitrary before its permitted clear
and clears at return. Exact rational rows retain free noncommuting warp words
and the correct dual signs. The interpreters agree on every endpoint, physical
frame, paid rank and scalar invoice. A wrong paid rank is rejected. Separate
dense rational multiplication checks the triangle and rejects a wrong sign;
source-byte changes fail authentication before imports.

The candidate Gaussian edge set is contained in the source edge set. Their
operators, absolute phases and all-width interpretation reuse existing source
recipes; no new lowering is claimed. Helper boundaries are unchanged. Formal
prefix maxima remain 457 forward and 169 backward, below the retained envelope.
The source primitive lowerer, including coefficient preparation, gives exactly
914 fewer real allowance units in each orientation.

## Why K is unchanged

For every real C the recursive moment depends on the target profile T and
paid profile P through sums of r^(1-C). Both profiles are exactly unchanged.
Substituting into an unchanged complete controller therefore gives the old
moment function at every C, not just at sampled exponents. Fixed scalar work
can affect constants; it does not establish a new exponent saving here.
This is a constructive local simplification, not a global lower bound on
changed scalar circuits, native words or integer multiplication.
