# A closed-disk obstruction to an in-place reversible phase interface

Put h=2^-p, s=2^p and

    D_p = {(a+ib)/s : a,b are integers, a^2+b^2 <= s^2}.

This is the complete finite closed unit disk on the SAME input/output grid.
The phase z is fixed independently of x. A candidate F_p is a total function
D_p -> D_p, with no linearity or implementation assumptions. We ask jointly for

    (I) F_p is injective;
    (N) |F_p(x)| <= |x| for every x in D_p;
    (E) |F_p(x)-zx| < C h for every x in D_p.

The new contribution is the precise application of elementary finite-set and
dyadic-shell arguments to this strengthened phase/return contract. Those
elementary arguments, and the rounded-shear technique below, are not claimed
as new mathematics. PR2527 supplies (N),(E) for C=4 but does NOT claim (I).

## 1. Standard finite nonincrease lemma

If F:S->S is injective on a finite set and f(F(x))<=f(x) for every x, then
f(F(x))=f(x) for every x. Indeed F permutes S, so the sum of f(F(x)) over S
equals the sum of f(x). Every summand of their difference is nonnegative;
therefore every difference is zero. Apply this with S=D_p and f(x)=|x|^2.
Thus (I),(N) force exact norm preservation on every input, even for a nonlinear F.

On the boundary of D_p the only points are 1,-1,i,-i. To see this, if
a^2+b^2=2^(2p), reduction modulo 4 for p>=1 forces both a,b even. Divide by
4 and repeat p times. The final integers have squares summing to 1. This is
an all-p proof, not an extrapolation of the finite shell enumeration.

Consequently, at the particular input x=1, (I),(N) force F_p(1) to be a
Gaussian unit. For any fixed unit phase z define

    delta(z)^2 = min_{u in {1,-1,i,-i}} |u-z|^2.

If C^2*4^-p <= delta(z)^2, (E) is impossible. In particular every fixed
non-Gaussian unit phase is excluded at all sufficiently large p for every
finite fixed C. If the intended phase varies with p, this last conclusion
requires an appropriate lower bound on delta(z_p); none is assumed here.

## 2. Exact rational phase and sharp precision threshold

Choose z=(3+4i)/5. It is an exact unit phase admitted by PR2527's interface;
we do not identify it with any selected supplier phase. Its squared distances
to 1,-1,i,-i respectively are 4/5,16/5,2/5,18/5. Hence delta(z)^2=2/5.
For C=4 and every p>=3,

    16/4^p <= 1/4 < 2/5.

No total map can satisfy (I),(N),(E). The threshold is sharp among p>=1:
at p=1,2 the identity is injective and norm preserving, and
|x-zx|^2=(4/5)|x|^2<=4/5<16/4^p for every x in D_p. For Gaussian phases,
the exact coordinate rotation is a positive example at every precision.

## 3. What exactly restored helpers imply

Fix a precision, phase, and a complete entrance state H of all other roles,
control, history and auxiliary storage, independently of x ranging over D_p.
Suppose an exact reversible computation has final action

    (x,H) -> (F_{p,H}(x),H)

for EVERY x in D_p, with its data output on the same grid satisfying (N),(E).
Injectivity of the full computation implies injectivity of F_{p,H}: equal data
outputs would give equal complete final states. The preceding obstruction
applies on each such fixed H fiber. The number and initial dirt of helpers do
not matter when they are all restored and the other hypotheses hold.

This concerns a destructive in-place data update with a fixed helper fiber.
It is NOT an impossibility theorem for strict-zero cleanup in general. For
example (x,y)->(x,y+F_p(x)) is reversible by recomputing and subtracting F_p(x)
while retaining x, even when F_p itself has collisions. Also an entrance helper
containing a copy of x does not provide the stipulated independent fixed fiber.
The verifier executes dirty-accumulator return with the original kernel.

Allowing retained history, extra output, a finer output grid, a restricted
input domain, or outward norm slack changes a hypothesis. Merely declaring a
larger or unbounded data domain does not evade the argument if its restriction
to D_p remains injective and pointwise nonincreasing on the same grid: that
restriction still maps D_p into itself.

## 4. Binding to the actual pinned PR2527 kernel

VENDOR.json pins the unmodified kernel and its retained PR2313 interval code
at PR2527 head 3e1e819e4d0837123a4fc05674fc1df6bde859a9. We construct the
actual point enclosure of (3/5,4/5) at Q=p+8 and verify intended-phase
containment. Its inward phase numerators are

    w=(floor(3s/5),floor(4s/5)).

Both lie strictly between 0 and s for p>=1. Thus the actual last product
rounding sends the input numerators (1,0) to (0,0), just as it sends (0,0).
This proves an actual source collision at every p>=1; the executable checks
p=1,...,128. It is consistent with the source's norm/error promises.

At p=3 the unchanged source, with denominator 8, executes

    (8,0) --phase--> (4,6) --conjugate phase--> (6,0).

Thus 1 goes to 1/2+3i/4 and then 3/4, with exact roundtrip defect 1/4.
Both calls satisfy the source contract. Approximation of the conjugate phase
is not asserted by PR2527 to be an exact inverse; the witness rejects that
additional inference. PR2549's separate precision/private-erasure debt motivates
making return premises explicit, but this result neither identifies a new
defect there nor claims its collector cleanup needs an inverse of this kernel.

## 5. Constructive changes of hypothesis

**Refined output grid.** Keep w=(u,v) above, but return the exact product
(ua-vb,va+ub) with denominator s^2, instead of rounding back to denominator s.
The determinant u^2+v^2 is positive. Its inverse on its image recovers

    a=(uA+vB)/(u^2+v^2), b=(uB-vA)/(u^2+v^2).

It is injective and norm nonincreasing because |w/s|<=1. For this rational
phase each component of z-w/s has magnitude <h, so the error on |x|<=1 is
<sqrt(2)h<4h. The output belongs to the 2p-grid; image membership/divisibility
is required by the inverse. No free precision conversion or native cost is
claimed. The changed codomain explains why the finite self-map lemma does
not apply.

**Same-grid reversible lifting with outward slack.** Let R(t)=floor(t+1/2).
For integer coordinates, execute in the displayed sequential order

    a <- a-R(b/2)
    b <- b+R(4a/5)
    a <- a-R(b/2).

Reverse the three updates with opposite signs to obtain the exact inverse on
all Z^2. Without rounding this is rotation by (3+4i)/5. Writing the three
additive rounding residuals as e1,e2,e3, each of absolute value <=1/2, gives

    error_a = (3/5)e1-(1/2)e2+e3,
    error_b = (4/5)e1+e2.

Their absolute bounds are 21/20 and 9/10, hence squared error <=153/80<4 in
grid units: the physical error is <2h, uniformly over ALL integer inputs.
But at p=3 the input (0,8) maps to (-7,5), with squared numerator norm 74>64.
The map is a bijection of the whole grid, not a nonincreasing self-map of D_p.
Clipping that outward result to zero breaks the inverse. This standard
rounded-lifting construction is an escape control, not a new rotation algorithm
or an implementation of the repository's paid native interface.

## Scope

The impossibility is proved for every p>=3 by the argument above. Finite
executions corroborate the source and escapes; they are not the universal
proof. There is no selected phase binding, implementation timing, hosting
construction, physical storage bound, full supplier, or new kappa. The
downstream implication ruled out is precisely: the norm/error phase contract
alone may be strengthened to an exactly reversible destructive same-grid
update with every other state restored on a complete fixed-helper disk fiber.
