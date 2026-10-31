# Sharp recovery with unequal tensor-test budgets

Let A and B be unitaries on the same nonzero finite-dimensional complex
Hilbert space. All norms are operator norms. Assume

\[
\|A^{\otimes2}-B^{\otimes2}\|\le e_2,\qquad
\|A^{\otimes3}-B^{\otimes3}\|\le e_3,\qquad 0\le e_2,e_3\le2.
\]

Put a=arcsin(e₂/2) and b=arcsin(e₃/2), both in [0,π/2]. The exact best
dimension-independent upper bound is

\[
\boxed{\quad\|A-B\|\le
\begin{cases}
2\sin\!\left(\frac12\min\{a,2b/3\}\right),&3a+2b<\pi,\\
2\sin(\pi/3+b/3),&3a+2b\ge\pi.
\end{cases}\quad}
\]

Every value is attained in every positive dimension, by scalar multiples
of the identity. Equality in the budget threshold belongs to the high
branch. This resolves Open next question 1 in the exact pinned
`research/tensor-phase-stability/README.md`, originating in #5916.
The predecessor supplies the equal-budget theorem; the result here is its
full asymmetric frontier and an exact rational branch/enclosure algorithm.

## 1. Spectral reduction, with its precise strength

Set U=B* A. Left multiplication by a unitary, and tensor multiplicativity,
give

    ||A-B|| = ||U-I||,
    ||A^(tensor j)-B^(tensor j)|| = ||U^(tensor j)-I||.

If z is an eigenvalue of U, an eigenvector repeated j times is an
eigenvector of U^(tensor j) with eigenvalue z^j. Thus every z obeys
|z²−1|≤e₂ and |z³−1|≤e₃. The spectral theorem gives
||U−I||=max |z−1|. A bound for the scalar feasible set therefore bounds
all unitary pairs.

These scalar constraints are necessary, but are not asserted sufficient
for an arbitrary list of eigenvalues: mixed tensor eigenvalues can add
constraints. This causes no loss in the optimum over all unitaries,
because U=zI has no mixed eigenvalue distinction and realizes every
scalar feasible value. In particular, sharpness does not rely on
pretending an arbitrary spectrum passes the tensor tests.

## 2. Exhaust every scalar arc

Complex conjugation preserves the three distances, so write z=exp(iθ)
with 0≤θ≤π. The two tests give exactly

    θ ∈ [0,a] ∪ [π−a,π],
    θ ∈ [0,2b/3] ∪ [2π/3−2b/3,2π/3+2b/3].

The endpoint b=π/2 is included: the second cube interval then ends at π.
The endpoint a=π/2 is included: the two square intervals meet at π/2.
No further cube interval meets [0,π].

There are only four pairwise intersections:

| Square component | Cube component | Existence / right endpoint |
|---|---|---|
| [0,a] | [0,2b/3] | Always; min(a,2b/3) |
| [π−a,π] | [2π/3−2b/3,2π/3+2b/3] | Exactly when 3a+2b≥π; right endpoint 2π/3+2b/3 |
| [0,a] | second cube component | Requires 3a+2b≥2π, so the previous intersection already exists |
| [π−a,π] | first cube component | Would require 3a+2b≥3π, impossible since 3a+2b≤5π/2 |

When present, the high right endpoint is at least 2π/3 and is larger
than every point of [0,a]. Consequently the largest feasible θ is
min(a,2b/3) below the threshold and 2π/3+2b/3 on or above it.
Since 2sin(θ/2) increases on [0,π], this proves the bound. Choosing the
displayed θ and A=exp(iθ)B proves attainment in every positive dimension.

## 3. The discontinuity curve and degenerate budgets

For fixed b, the high component first appears at

    a₀=(π−2b)/3,
    e₂*=2sin((π−2b)/3).

At any interior point of this curve the left-hand low limit has phase
min((π−2b)/3,2b/3), while the attained boundary value has phase
2π/3+2b/3. Their difference is strictly positive. The low limiter switches
at b=π/4; this does not change the high-branch threshold. The corner
(a,b)=(0,π/2) likewise has low-region limit zero and attained error two,
although a negative-a approach at fixed b is outside the domain.

Useful exact boundary cases are:

| Squared budgets (s,t)=(e₂²,e₃²) | Optimal squared error | Witness phase |
|---|---|---|
| (0,0) | 0 | 1 |
| (0,4) | 4 | −1 |
| (3,0) | 3 | exp(2πi/3) |
| (1,2) | 2+√3 | exp(5πi/6) |

At (1,2), the limiting low value along t=2 and s↑1 is 2−√3. This
explicit asymmetric jump demonstrates why a strict high-branch test is
incorrect. Setting a=b recovers #5916's threshold a=π/5 and both of
its branches, including equality. Interchanging the two error budgets
does not preserve the answer: their test widths differ.

## 4. An exact branch test on rational squared budgets

Let s=e₂², t=e₃², and H=(1−s)²(4−s). For s≥3, a≥π/3 and the high
branch always applies. For 0≤s<3, 0≤3a<π, so monotonicity of cosine on
[0,π] gives

    3a+2b≥π
    iff cos(3a)≤cos(π−2b)
    iff (1−s)√(4−s)≤t−2.

Squaring only after fixing signs yields the following exact predicate:

| s region | High branch exactly when |
|---|---|
| s≥3 | Always |
| 0≤s≤1 | t≥2 and H≤(t−2)² |
| 1<s<3 | t≥2 or H≥(t−2)² |

This includes every equality and requires rational arithmetic alone when
s and t are rational. Blind squaring would reverse or discard sign
information and is not the stated test.

The entire boundary has an algebraic parametrization

    1≤q≤2,   s=4−q²,   t=2+q(q²−3),   X=2+q.

Indeed q=√(4−s), and the branch equality gives the displayed t. Substituting
X=2+q verifies both residual equalities. Thus rational q supplies exact
rational budget and optimum triples even along the nonsymmetric jump.

Write X for the optimal squared error. The trigonometric identities give

    square defect² = X(4−X),
    cube defect²   = X(3−X)².

On the high branch, X is the unique root of X(X−3)²=t in [3,4]. On the
low branch, X is the minimum of the unique root of X(4−X)=s in [0,2]
and the unique root of X(3−X)²=t in [0,1]. Each polynomial is strictly
increasing on the named interval, apart from endpoint zero derivatives,
which do not affect uniqueness. Exact rational bisection gives nested
enclosures, with no rounded transcendental decision. The implementation
returns an interval of width at most 2^(−bits); exact rational roots
encountered by bisection return point intervals.

## 5. Independent finite corroboration

`verify.py` compares the formula with a generic periodic-arc intersection
at 10,201 rational angular pairs and 101 exact threshold points. It also
tests literal rational unit-circle phases and forms dense tensor defect
Gram matrices for 16 two-by-two unitary pairs, including 12 noncommuting
pairs. The complete
four-by-four and eight-by-eight matrices are checked over Gaussian
rationals; no floating-point eigensolver is used.

`independent.py` uses no angle or branch criterion in its oracle. It
constructs the two residual polynomials in X, makes their product
square-free, and isolates all roots in [0,4] with exact Sturm sequences.
Polynomial gcds decide zero signs at shared roots, including the jump
curve. Interior root brackets have endpoints that are nonroots of the
original square-free polynomial, including any endpoint roots stripped
before subdivision. This prevents a gcd root count from confusing the
represented root with a separately recorded endpoint root. It also checks
33 rational jump points, their 64 feasible one-sided perturbations, and
23 near-endpoint/common-root cases with gaps down to `2^(-160)`. The largest
feasible boundary root is the optimum: the feasible
set is nonempty, compact, and if a maximum is interior to [0,4], at
least one continuous inequality is an equality. The oracle checks 289
rational squared-budget pairs against the new enclosure algorithm.
Its imports of the algorithm are only for this final comparison.

Finite tests corroborate the proof and protect its implementation;
they do not prove the universal theorem by enumeration. All test domains
are deterministic and exhaust their stated bounds. No random search or
unreported early stopping is used.

## 6. Scope and credit

The hypotheses require the same fixed pair of exact unitaries at both
widths and absolute operator-norm comparisons. Projective equality is
insufficient: A=−B has one-column distance two despite projective
agreement at every width. Unitarity is essential: the scalar operators
A=1/2 and B=−1/2 have tensor-square difference zero, tensor-cube difference
1/4 and one-column difference one. The unitary formula at (e₂,e₃)=(0,1/4)
would instead give zero. This is a genuine tensor counterexample outside
the hypotheses, not a substitution of ordinary powers for tensor powers.
Approximate tests do not assert the same error
at all later widths, nor apply to independently rounded tensor factors.

This is an interface theorem, not a selected-caller application, supplier
admission, discharge of `native_all_columns`, or complete multiplication
theorem. All five selected framework assumptions remain. No new κ.

Nick Petalas's #5916 supplies the equal-budget theorem and the explicit
asymmetric open question. Credit unpaidmoon #5837 for its motivating
finite-width phase question, DLamdata #5894 for separate selected
absolute-phase coverage, and the retained native/caller lineage. Spectral
theory, elementary trigonometry and Sturm root counting are classical;
no general literature-priority claim is made. Prepared for @CubeJerry
with substantial OpenAI Codex assistance. Apache-2.0. No independent
human or formal proof-kernel acceptance is asserted.
