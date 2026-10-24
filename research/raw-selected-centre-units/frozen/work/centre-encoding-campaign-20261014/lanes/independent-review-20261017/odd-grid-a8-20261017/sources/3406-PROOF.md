# Sharp conditional Newton entrance for the literal P104 word

Put R = Z[i], pi = 1+i, and let B_r be the image of
E_r = [[1,0],[1,pi]] tensor r over R. Equivalently, an array on the
r-bit cube belongs to B_r exactly when its multilinear Newton coefficient
at x^S is divisible by pi^|S|. We use r=9 and 512 complex entries.
This is the domain introduced in the P104 setting by Clear1nsight's
[PR3382](https://github.com/CrocSwap/integer-mult-bounds/pull/3382), exact
`2834523b1cd4ea83ba7a043e2e2f5f3332cf9909`, following the credited Clifford,
Barnes-Wall, period and lifting work. We rederive the properties needed here.

## The statement and its inherited premise

Fix ywz65's PR2586 word, exact
`7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`, with the unchanged WORD and
NATIVE bytes pinned in SOURCES.json. A transport from frame A to frame B
has its retained ideal meaning Delta_B Delta_A^-1. Its archived implementation
is the actual left monomial, distinct-coordinate C stages, and right monomial.
The equality of every archived recipe to that ideal change of chart is an
**inherited native-source premise**, not a new exhaustive matrix-identity
certificate here. This distinction is needed for the symbolic row proof.
We authenticate all recipes, prove their lattice closure, and separately replay
the complete literal word on one dense entrance. That finite replay does not
independently prove the inherited recipe identities for all vectors.

For each of the 358 independent initial public roles s, choose an integer
k_s >= 0 and allow every input in pi^k_s B_9. Private C is owned zero when
allocated. The following property holds if and only if

- k_s >= 4 for every one of the 104 Y roles;
- k_s >= 2 for every one of the 78 N roles;
- k_s >= 0 for the remaining 104 X, 32 D, 32 G and eight Q roles.

The property is that every public/private array at every event boundary and
at every native wrapper/stage prefix belongs to B_9. All scalar divisions and
signed-floor native stages then agree with their ideal maps on the same grid.
All eight private erasures are literal zero, and the original logical dirty
restoration and X-output shear hold in their declared final frames.
Multiplying every input and output by 2^-f gives the same statement for any
fixed nonnegative integer fractional width f.

This is sharp among these independent principal-ideal product entrances.
It is not maximality among correlated input sets, a claim of necessary
conditions for completed-output equality, or a claim that arbitrary physical
inputs can be converted into this entrance without cost. It does not assert
that public physical arrays have identical entry/exit bytes when their frames
change. Dirty restoration means equality after their declared chart changes.

## The lattice and the actual wrapper alphabet

Write an array as sum_S pi^|S| c_S x^S. A one-coordinate Gaussian butterfly
C(a,b) = ((a+b+i(a-b))/2, (a+b-i(a-b))/2) obeys

    E_1^-1 C E_1 = [[1,1],[0,i]].

Both this matrix and its inverse are integral. Thus each coordinate C and
its inverse is an automorphism of B_r and of every pi^k B_r.
At any coordinate pair of an admitted array, the input difference is divisible
by pi. Its real and imaginary parts therefore have equal parity. In the
signed-floor pair, the difference between the ideal half and a floor half is
zero for both components or is the same half-unit for both. Rotating the
difference by i and taking the second floor cancels these errors. The resulting
pair is exactly C. The same argument works for the inverse and for negative
integers. The verifier compares the literal signed-floor formula from
Tekalign/PR3025 against each exact pair used in the complete fixture.

The other generators are also integral automorphisms in Newton coordinates.
A bit flip sends x_j to 1-x_j, reducing or retaining degree. A coordinate swap
preserves degree. For CNOT, substitute x_j+x_k-2*x_j*x_k for x_j. If a monomial
contains j but not k, the new terms retain its degree or add one variable with
a coefficient divisible by 2, hence by pi. If it contains both, the substitution
reduces to a lower-degree monomial minus the old one. Each resulting coefficient
has the required pi divisibility. These address generators are involutions and
generate all invertible binary affine substitutions.

A linear Gaussian phase is multiplication by 1+(i^l-1)*x_j. Its nonconstant
coefficient is divisible by pi. A quadratic sign is multiplication by
1-2*x_j*x_k; its nonconstant coefficient is divisible by pi^2. The added degree
is at most one or two respectively. Their inverses have the same property.
Constant Gaussian units preserve every module. Therefore every invertible
binary affine address map with phase

    i^(p + sum_j l_j*x_j + 2*sum_(j<k) q_jk*x_j*x_k)

is an automorphism of every pi^k B_r. The verifier checks that all 2,490 actual
wrapper records have this alphabet and bijective addresses. Every archived
native prefix, and the canonical Delta charts and their inverses, consequently
has the stated lattice property. This does not substitute a different return
recipe or infer identical circuits from matching frames/ranks.

## Exact scalar certificate

For a role t at event cut j, let c_(j,t,s) be its rational scalar coefficient
on initial logical role s. Begin with the identity matrix, apply each literal
ADD or sign, and leave coefficients unchanged on transport. A private allocation
starts a zero row and an erasure requires its row to be identically zero.
All ADDs have a common declared frame. By induction and the inherited native
identity, the physical row is

    sum_s c_(j,t,s) Delta_(j,t) Delta_(0,s)^-1 f_s.

Both Delta factors are automorphisms of B_9 and commute with scalar pi powers.
If v_pi is the Gaussian pi valuation, the exact product-domain requirement is

    k_s >= max(0, max_(j,t) -v_pi(c_(j,t,s))).

Zero coefficients impose no condition. Sufficiency follows term by term,
then by module closure. Native prefixes preserve the same module. The exact
forward rational trace in verify.py computes this maximum through all 5,398
events. RECEIPT.json records every initial exponent, all eight zero-erasure
cuts and a coefficient attaining every positive maximum. The results are four
for all Y, two for all N, and zero for all other initial roles. The final scalar
rows restore every non-X role and give each X its original input plus Y terms.

Necessity uses input independence. Fix a source with an attaining coefficient
q and set all other initial roles to zero. The operator between its initial
and witness frames is a B_9 automorphism. An encoded unit column is primitive
in this free R-module, and an automorphism preserves primitivity. Thus
q*pi^k times that primitive vector belongs to B_9 only if
v_pi(q)+k >= 0. Lower k by even one pi and the property fails. A smaller k
allows that same violating vector, since the input modules are nested.
The 182 witness coefficients are checked again by separate backward adjoint
traces. The verifier also runs all 182 literal single-source controls with
constant input pi^(k_s-1), all other public inputs zero. Each fails membership
or exact division no later than its recorded witness event. These finite
negative fixtures do not use the change-of-chart oracle.

Simple minimum-path propagation loses a correlation. It asks for four pi
powers on N2 and N4. At events 448-449 the logical pair becomes

    n2' = n2-n4,     n4' = (n2+n4)/2.

Later half-reads of n2' are legal because n2' remains in 2B_9 under the stated
entrance. At events 4696-4697 the correlated update recovers the original dirty
contributions before their later half-read. Exact coefficient collection retains
these cancellations. The full forward certificate checks this through the
intervening Y updates and transports. The stronger path-only condition is
sufficient but is not the sharp product entrance.

## Scope and the active neighboring investigation

The current actual-caller claim is
[Discussion2750 comment19008790](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19008790).
It studies the first collector's actual 58-bank dependency cone, its named
later consumers and a complete bill. This result instead changes the **global
initial input contract** and classifies independent pi-power modules for the
entire word. It does not admit the current caller or prepare these inputs.
Our [advance scope](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-19008906)
records that boundary. No first-cone/consumer result is claimed here.

The theorem supplies a source-local restricted-state contract, under the
retained ideal native identities, at the fixed nine-bit address width. The
finite fixture confirms actual array values for one dense signed entrance,
all event/native-stage memberships, all 358 chart-aware outputs and eight
private erasures. It does not prove native covariance for every recipe/vector,
a physical allocation/route, fast recursive tariffs, a favorable complete cost,
a new all-size supplier, a new precision minimum, or a new kappa. Tensor-depth
extensions and the selected cold replay are unrun. A cheap arbitrary-input
caller still needs its own encoding/intertwining/dirty restoration and full bill.
