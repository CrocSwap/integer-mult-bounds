# What the symbolic audit establishes

This is an independent audit of a finite collection of **compiled address
words**, with a universal statement about their incoming unit weights.
It is not a proof of every fallback plan, physical child implementation,
the all-size supplier, or the multiplication theorem. No new κ.

## Object and quantifiers

Pin Jose Manuel's PR2207 at
`149d55d90d3c0877ed3d78e1deca8eb2f72e0d00`. The unchanged compiler,
coefficient evaluator and two imported modules are retained under `vendor/`.
The selected-object binding follows the actual PR1094 assembly's PR589
receipt citation to idle child 6, unhosted copy 213, of rank 42 in dimension
64. This is the same conditional GL implementation object used by
commdata2338 in PR2160/2188 and by PR2207. The bridge to emitted
orthogonal-cover invocations is still an assumption.

For each of the four explicitly defined matrices M below, fix f=3 atom
columns. Work over R=Z/9, Z/25, Z/49, or Z/25 respectively. For **every**
assignment of the 192 symbols x_(i,j), 0<=i<64, 0<=j<3, to units of R,
the checked compiled word equals the independently constructed direct
address operator. At logical column j that operator is

    B_j M B_j^-1,  B_j = diag(x_(0,j),...,x_(63,j),1,...,1).

The physical coordinate of field i at logical column j is `3i+j` in the
head bank and `3i+2-j` in the tail bank. Comparison covers the full 384 by
384 matrix, including off-column zeros, for each fixture. Arbitrary initial
address vectors are covered by equality of linear operators. The formal
weights need not be realizable by any actual ancestor descriptor: they
are a stronger algebraic input class, not an admission claim.

## Independently constructed base matrices

Let `D=diag(I_42,0_22)`. Define h by the identity except for two disjoint
2 by 2 blocks:

    axes (0,43): [[q,q-1],[1,1]],
    axes (1,42): [[1,0],[1,1]].

Both blocks have determinant one; their inverses are written explicitly
as `[[d,-b],[-c,a]]`. A column permutation S maps the selected axes
22..63 to 0..41, so `g=hS` satisfies
`g diag(0_22,I_42) g^-1 = h D h^-1`. For q=3,5,7, take P=hDh^-1.

The fourth fixture uses q=5 and

    C_ik = (67 + 17i + 29k + ik) mod 5,
    U = I + 5C, U^-1 = I - 5C mod 25,
    P = (Uh) D (h^-1 U^-1).

This is one fixed dense high lift, not a random search or an exhaustive
high-fiber census. It retains the low chart because U=I modulo 5. In
particular P_00 is zero modulo q, so these are nongeneric fixtures for the
good branch. The audit checks the explicit inverse, P²=P and M²=I using
its own matrix multiplication. With C64 the coordinate reversal,

    M = [[I-P, P C64], [C64 P, I-C64 P C64]].

The endpoint oracle constructs these four blocks directly. It does not
use the predecessor's projector, inverse, residual, elimination or
reconstruction functions. The predecessor's elimination **is** run to
produce the plan under test; a faulty plan cannot determine the oracle.

## Why this is more than sampled weights

The arithmetic ring used by the audit is

    L = R[x_0^±1,...,x_191^±1].

Each polynomial is stored as its sparse map from integer exponent tuples
to coefficients modulo q², with zero coefficients removed. Addition and
multiplication combine equal monomials exactly. No floating-point values,
random evaluations, cancellation assumptions about nonunits, or field
division are used. The only inversion implemented is that of a single
monomial whose scalar coefficient is a unit. Shear coefficients may be
zero or nonunits, and are never divided by in the operator interpreter.

The pinned `compile_program` and `coefficient` functions execute unchanged.
Their **bank-read boundary** returns the corresponding formal variable for
a head field and one for a tail field; their arithmetic object performs
Laurent operations. This instrumentation does not run ancestor preparation
or prove that bank reads are physically implemented. Separate numeric
tests check all 384 bank positions and compare the instrumented coefficient
function with its unmodified numeric execution for all 36 pairs of units
modulo 9 on a small plan.

A separately written sparse interpreter applies each emitted lower shear,
weighted swap and sign to the identity operator. It uses the source's
logical-column selector at the actual physical target. The direct oracle
constructs physical indices separately. Each resulting polynomial entry
is compared with the direct operator, including absent/zero entries.

For any tuple of units in R, substitution extends to a ring homomorphism
L -> R, since negative powers are defined. Applying this homomorphism to
the checked polynomial matrix equality proves equality for that tuple.
This is the justification for **all unit weights on these fixed matrices**.
It does not turn four chart instances into an all-chart theorem. Nor is
this a proof-assistant certificate: the small arithmetic implementation,
Python execution and written argument remain part of the review boundary.

## Coverage and failure evidence

Every selected fixture retains 16,256 shear slots and 16,554 swap
instructions. Zero coefficients are retained. There are 589,824 compared
matrix entries over the four fixtures and 65,024 source shear slots.
The three block fixtures each have 432 nonzero physical endpoint entries;
the dense fixture has 20,244. Its nonzero shear count is 6,413, compared
with 18 in each block fixture. These counts describe this audit, not
improvements to the supplier's paid bill.

A separate 4 by 4 diagonal matrix `diag(-1,1,1,1)` over Z/9, with two
atom columns, exercises the fixed-sign path. It is not a selected
rank-42 instance.

Six endpoint mutations must produce an actual failed unit assignment:
final instead of live row permutations; wrong inverse chronology; wrong
inverse-shear sign; dropping a diagonal pair's weight quotient while
retaining its scalar; wrong physical target orientation; and omitting
the fixed sign. RESULT.json records each failed basis entry and a
concrete assignment, usually all weights one except a single weight two.
These are deliberate corruptions, **not bugs found in PR2207**.

For example, replacing the live permutation by the final one gives 24
instead of 23 at physical output 129, basis input 0, modulo 25 when
x_129=2 and all other weights are one. Losing the pair quotient gives 15
instead of 5 at output 0, basis input 383, when x_3=2. Dropping that
quotient is invisible when all weights equal one; this motivates the
symbolic method.

Three further controls reject a missing zero shear slot, a nonunit inverse,
and changed source bytes. A control passes only when it fails for its
specified reason; unrelated fixture exceptions are not accepted as
successful negative controls. The arithmetic tests independently evaluate
polynomials at all 436 unit pairs modulo 9 and 25, including zero-divisor
and cancellation cases.

## Unresolved obligations

No all-chart census, all-prime or all-atom-width claim is made. Ancestor
Root/Good/FallbackPair preparation, physical ADD payload movement,
weighted child execution, COPY lifetimes, caller/descriptor-stack
integration, hosting, precision/tape and the full cost recurrence are
outside this audit. The pre-existing 98,682 fallback-child allowance and
131,072 charged envelope are not recomputed or reduced. No selected cold
replay, external human review, formal-kernel proof or hosted CI result is
claimed. PR2209's concurrent implementation work remains separate.
