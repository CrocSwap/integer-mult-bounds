# An all-depth component format for the actual QQ16 producer

## Statement and scope

Fix the literal F_0 then B_1_2 words, recipes, scalar coefficients and full
cover action authenticated by SOURCES.json. Let lambda be any positive
integer. Every owner has N=2^(73 lambda) complex payload coordinates, grouped
into lambda layers of 73 binary axes. The owner group is the inherited
73-axis cover group; increasing lambda does not replace it with a new group.

Let h be a positive binary quantum and P a nonnegative integer. Suppose all
real and imaginary components in the 704 persistent input fields, uniformly
over every owner and payload coordinate, belong to h Z and have magnitude
strictly below 2^P h. The eight owned private fields start zero. Dirty helpers
may vary independently within this bound.

**Theorem.** Under the inherited tensor-native and full-cover semantics, the
complete literal producer reference executes exactly using quantum

```
q = h 2^(-71-19(lambda-1))
```

and signed component width

```
W = P + 215 + 38(lambda-1).
```

All native interiors, constant-product partials and the carried F0 state fit.
There is no arithmetic rounding, overflow or underflow relative to this exact
reference. These are sufficient bounds. No minimum-format claim is made.

The conclusion concerns numerical execution of the stated reference. Its
logical/frame semantics and endpoint identities remain inherited. It does
not assert literal common-coordinate restoration of arbitrary helper vectors.
PR3293's helper frame-return calculation and PR3294's prefix reachability
question are separate and unused. No admitted caller entry format, paid
physical implementation, consumer, supplier or multiplication exponent follows.

## Tensor lifting is part of the premise

The canonical native review explicitly states that the identities hold at
every tensor length. Each address layer uses the same owner route and
translation, with phase equality summed over layers. A scalar coefficient
acts once on the port index, not once per tensor factor. The nine-axis native
kernel acts with spectators within each 73-axis layer.

A recipe of Gaussian rank r is implemented at depth lambda by r lambda
coordinate Gaussian lines, with its right and left tensor monomials. One
may group the lines by active axis because operations in different tensor
factors commute. Within each factor the original order is retained. Tensor
monomials are signed permutations of real/imaginary components and preserve
their uniform magnitude and grid. This is a lift of the original native
recipe, not lambda repetitions of the whole producer word, and scalar
coefficients are not raised to lambda-th powers.

For each of the 512 distinct cover maps used by B1, the checker verifies the
73-by-73 owner matrix g is invertible, delta has 73-bit range, and the action is

```
out(d,z_1,...,z_lambda)
    = in(d*g,z_1 XOR d*delta,...,z_lambda XOR d*delta).
```

This is a bijection for every lambda: recover d through g inverse and then
undo all lambda translations. It preserves a uniform bound over all owners.
It is not a payload-only permutation of a 512-coordinate array. The source
native/bridge proof and cover closure remain premises rather than being
recertified by checking invertibility alone.

## Symbolic induction

Put t=lambda-1>=0. At a cut, represent each field by a quadruple (M,g,a,b):

```
|each component| <= 2^P h M 2^(a t),
each component belongs to h 2^(-g-b t) Z.
```

M is a nonnegative rational, g an integer, and a,b nonnegative integers.
A proved-zero field has the unique quadruple (0,0,0,0). Entry persistent
fields have (1,0,0,0). Dependence, correlations and cancellation do not
invalidate these upper bounds.

For adding two nonzero fields, use

```
M = M1+M2, g = max(g1,g2), a = max(a1,a2), b = max(b1,b2).
```

This dominates both exponent functions because t>=0. For a nonzero dyadic
coefficient c=n/2^k in lowest terms, multiply M by |c|, add
k-v2(n) to g, and leave a,b unchanged. Integer-product partials use |n| M
before division and the original grid. Their partial sums cannot exceed
the sum of the absolute shifted copies. CLEAR is used only for owned
private fields and produces the canonical zero. Monomials and covers
preserve all four bounds.

It remains to bound one tensor Gaussian line and all its interiors. On one
coordinate pair the inherited pair-first lowering forms s=x+y, d=x-y,
then ((s+i*d)/2,(d+i*s)/2). With input component bound L, pair sums have
bound 2L, cross numerators 4L and outputs 2L. One output halving refines
the grid by at most one.

At the j-th coordinate line, 1<=j<=lambda, earlier lines multiply the
component envelope by at most 2^(j-1) and refine the grid by j-1. Thus the
following three symbolic observations dominate *every* interior line:

```
pair sums:      (2M, g,   a+1, b+1)
cross numerators:(4M, g,   a+1, b+1)
final output:   (2M, g+1, a+1, b+1).
```

For example the pair grid exponent is at most g+b t+j-1<=g+(b+1)t,
and its magnitude is at most M 2^(a t+j)<=2M 2^((a+1)t).
The cross bound has one extra factor two. The final output uses j=lambda
and grid exponent g+b t+lambda=(g+1)+(b+1)t. Earlier outputs are bounded
by the final-output observation. A zero input stays exactly zero.

Apply this grouped rule r times for a rank-r recipe. Induct through the
53,118 literal events, including private and cover sweeps in their original
order. The entire 712-field state after F0 is B1's input state. Nothing is
reset at the stage boundary. Owned private clears and inherited sweep order
give the same uniform reasoning even though a private sweep completes one
owner's row before moving to the next owner.

## Source-bound finite arithmetic

At t=0, the symbolic rule is exactly PR3270's one-layer rational recurrence.
The verifier reproduces its complete primitive trace, both completed-cut
hashes, both final-state hashes and every operation count. Its 270,288
symbolic observations give

```
max g = 71, max a = max b = 19,
max M = 35714190970741142696015664337123072062513575/4 < 2^143.
```

Therefore every visited grid exponent is at most 71+19t and every component
magnitude is below 2^P h 2^(143+19t). In units of q, the latter is strictly
below 2^(P+214+38t)=2^(W-1). Each value is an integer multiple of q.
Consequently every signed W-bit component, partial product and native
numerator fits, and every exact division has its required divisibility.
This proves the theorem for every positive integer lambda by the preceding
induction. The finite calculations establish constants of that induction;
small-depth tests are not its universal quantifier.

The separate numeric interpreter does not import the symbolic Bound,
Envelope or dispatcher. It explicitly repeats every Gaussian coordinate
line at depths 1,2,3,8. Its observed grid guards are 71,90,109,204 and its
exact range bounds obey the stated affine formula. It shares authenticated
input loading and event expansion. Behavioral controls also compare the
grouped tensor rule with each interior of 120 small repeated-line instances,
reject source/schema/usage/receipt mutations, and detect resetting F0 state.

## Symbolic numeric costs and remaining bill

The one-layer source has 11,076 Gaussian lines. Each costs at most 4N real
additions, 2N exact halvings and 4N component copies, hence 10N numeric
word operations. Only these coordinate-line counts multiply by lambda.
Scalar operations still act once on a port. Each tensor monomial can be
applied as one signed global permutation using the existing reusable
out-of-place buffer. Computing its addresses and signs is outside this
numeric count and must not be inferred to be free.

The retained one-layer numeric count is 483082N+12. Subtracting its
110760N Gaussian contribution gives the all-depth bound

```
(372322 + 110760 lambda) N + 12 W-bit numeric word operations per owner.
```

The 528 cover moves additionally require 2112N conceptual real-component
transfers per owner. Logical numeric storage remains at most 1426N+12
W-bit words: 712 complex fields, one complex global-cover buffer and 12
scalar temporaries. The count includes constant-product copies, additions,
shifts, sign changes and private clears. Diagnostic call/phase labels are
excluded. A W-bit operation is a reference operation, not a claimed unit
cost on a fixed-word machine.

Addresses, sign/control computations, code, tables, physical movement,
recursive tariffs, a caller's entry-format conversion and F17 consumption
remain unpriced. The reference's zero arithmetic defect meets any positive
completed-output tolerance only on this stated input lattice and under its
exact semantics. It does not discharge those separate supplier obligations.
The full N-dimensional payload is never allocated or executed by these
checks. Family decision: close this numerical-domain gap and stop.
