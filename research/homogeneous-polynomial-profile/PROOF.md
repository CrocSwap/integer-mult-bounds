# Linear extraction along a homogeneous constant trajectory

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and claim

Let K be an infinite field and R a subring of K. Fix finitely many vector
registers in K^d, d >= 1. Data and dirty registers vary independently. Clean
registers start at zero. Every gate has distinct source a and target b, one
fixed R-linear matrix T, one fixed scalar polynomial p in R[t], and a label.
Allow either placement, with powers evaluated coordinatewise:

    b += p(Ta),                 b += T p(a).

The polynomial may have any constant term. Every gate preserves its source,
and its inverse subtracts the same increment. The full finite word, ports,
polynomials and labels are independent of input values. A gate's label may
record its operator, orientation, ports and any other fixed charge category.
The comparison linear class allows every scalar multiple kT, k in R, at the
same label charge. This is an optimistic operator-call model. Pointwise
polynomial work is not a claimed free physical operation.

Write e=(1,...,1). Assume, for each allowed T,

    T e = lambda_T e,           lambda_T in R.                 (1)

Equivalently, T has constant row sum. Matrices need not be invertible,
commuting, triangular, or simultaneously diagonalizable.

**Theorem.** If such a polynomial word implements the exact linear endpoint L
on all allowed inputs, then there is a linear word with the same endpoint,
all required dirty and clean returns, and no larger count in any label.
Each retained gate has the original operator, source, target, label and order.
Consequently the two models have identical Pareto-minimal call profiles and
identical minima for every nonnegative label tariff, whenever a minimum exists.

## Follow constants before differentiating

Set every independent input coordinate to zero. Initially every register is
zero, including clean scratch. After each prefix, every register has the form
c_v e for a scalar c_v in R. To prove this, suppose the source has value c_a e.
Condition (1) gives the following scalar updates to the target:

| Gate | Update to c_b | Derivative on perturbations |
|---|---|---|
| b += p(Ta) | c_b += p(lambda_T c_a) | delta_b += p'(lambda_T c_a) T delta_a |
| b += T p(a) | c_b += lambda_T p(c_a) | delta_b += p'(c_a) T delta_a |

All other register constants remain unchanged. These equations prove the
induction and show that every scalar coefficient in the derivative belongs
to R. The derivative of coordinatewise p at z e is p'(z) times the identity.
The displayed chronological derivatives are therefore allowed linear gates.
If the coefficient is zero, omit that gate.

Apply the chain rule at this single zero input, using each gate's actual
intermediate constant state. The product of these derivative shears is the
Jacobian of the complete polynomial word, restricted to the allowed input
space. This also covers clean scratch: its initial tangent is zero, while its
required final return is included among the endpoint coordinates.

The infinite-field hypothesis turns equality of polynomial functions on all
independent inputs into polynomial equality. The endpoint is L, so its
Jacobian is L. The extracted word consequently implements L with every
required return. At most one gate survives per original gate, always under
the original label. Conversely every linear word is already a polynomial
word satisfying this contract. These two inclusions prove the profile and
tariff conclusions. They do not assert that the set of all profiles is equal;
only their coordinatewise minimal profiles are equal.

## Uniform families

Suppose one finite word uses operator families T_f at every permitted width,
with T_f e_f=lambda_T e_f where lambda_T is independent of f. Its polynomials,
labels and ports are also fixed across f. The scalar constant recurrence above
is then independent of f. So are all extracted coefficients and the pattern
of omitted gates. A uniform polynomial endpoint L_f supplies one uniform
linear word for the complete family.

Without width-independent row sums, the pointwise theorem still holds at
each width. It does not promise width-independent extracted coefficients.
For example, an after-operator translated-square pair with T_f=f I has
extracted coefficient 2cf in front of T_f. This is a limitation of the
uniform conclusion, not a proof that no other uniform word exists.

## A nonzero trajectory that the predecessor does not cover

For an operator T satisfying (1), c in R, and arbitrary a,b, execute:

    a += c e
    b += (Ta)^2
    a -= c e
    b -= (Ta)^2
    b -= (c lambda_T)^2 e

Each translation is itself a permitted constant-polynomial gate with T=I
and any distinct source. The source a returns exactly, and the endpoint is

    b += 2 c lambda_T T a.

The two square calls have zero formal derivative at the local zero state.
Nevertheless the first square call occurs at source c e. Its actual derivative
is 2 c lambda_T T; the second derivative is zero. The extracted word retains
one square-call label and deletes the other call and the three translations.
For the before-operator placement, replace the last translation by
b -= c^2 lambda_T e. The endpoint is b += 2c T a.

These are genuinely nonzero trajectories with exact linear endpoints and
arbitrary dirty source and destination. PR6017's common-zero-state theorem
does not apply. The present theorem proves that such trajectories still
cannot improve a linear call-profile minimum under (1).

## Boundaries and what is new

If T does not satisfy (1), the zero-input orbit can cease to be homogeneous.
For instance T=diag(1,2) and a=e give the after-square derivative
2 diag(1,2) T=diag(2,8), which is not a scalar multiple of T. Thus retaining
T's label by the table's scalar replacement would be unjustified. This
example marks a failed implication; it does not claim a cheaper endpoint.

The theorem concerns exact polynomial endpoints on all independent inputs
over an infinite field. Restricted grids, finite-field function identities,
branching, data-dependent operators, coordinate-dependent polynomials,
arbitrary vector constants and rounded execution are outside its scope.
A word with a nonlinear endpoint is not certified by its Jacobian alone.
Native frame costs, scalar work, movement, precision, storage, stock,
compiler closure and the complete signed invoice remain separate.

Nick Petalas's PR6017 supplies the zero-preserving predecessor and explicitly
asks about nonzero constant trajectories. The new step is the invariant
constant-vector orbit, its two placement-specific derivatives, and the
width-independent row-sum criterion. The chain rule and polynomial identity
principle are classical. Jose Manuel / jmbarrancoml's PR1757 nonlinear cut
obstruction and Chris R / Clear1nsight's PR3992 Jacobian obstruction retain
their distinct models and credit. No predecessor result is audited here.
