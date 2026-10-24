# Compact certificates with actual inverse calls

This is a scoped written proof for the register grammar below. The implementation
and finite tests corroborate it; there is no proof-assistant or independent human
verification claim. The contribution answers the inverse-frontend question in
[zxv's PR5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235), pinned at
`48976daa4dce59b4867ef046da72a370e389925d`. That package supplies the
independent-operator register bridge, invariant certificates and unipotent
witness method. Here inverse occurrences denote the **actual inverse of the
same generator**, and therefore need a different, cyclic realization and a
sound passage from formal series to arbitrary invertible substitutions.

Recognizable rational series, the Magnus substitution and weighted-automata
equivalence are classical. See Stefan Kiefer,
[Notes on Equivalence and Minimization of Weighted Automata](https://arxiv.org/abs/2009.01217),
and Retakh, Reutenauer and Vaintrob,
[Noncommutative rational functions and Farber's invariants of boundary links](https://arxiv.org/abs/math/0004112),
Remark 2.3 and Proposition 2.4, which recall the Magnus embedding and the
Schutzenberger/Fliess characterization. We claim a project-specific interface,
explicit state bound and executable certificate bridge, not a new general
automata/PIT algorithm or a new Magnus theorem. The argument below is
self-contained and does not require the injectivity theorem for the group
algebra embedding.

## 1. Grammar and statement

Fix a field K, a finite alphabet of independently chosen invertible operators
G_a on a common finite-dimensional K-vector space, and r >= 1 named registers.
All r initial vectors are independent; no dirty helper is assumed zero.
A program is a finite sequence of:

1. scalar linear assignment to a register, with all sources read before the
   assignment, including when the destination is also a source;
2. `dst <- G_a^s dst`, where s is +1 or -1;
3. `dst <- dst + c G_a^s src`, with the old source and destination, also when
   `src == dst`.

All scalar coefficients lie in K. Compare two such programs on the same
ordered roles and alphabet, returning **every** final register. Let q be the
total number of unary occurrences in both programs, including queries, inverse
occurrences, and queries with coefficient zero. Put D = r + q.

**Theorem.** There are effectively constructed scalar matrices
U in K^(r x D), V in K^(D x r), and T_a in K^(D x D) such that:

- the complete endpoint difference, expanded at G_a = I + Y_a, has coefficient
  matrix U T_a1 ... T_ak V at every word a1...ak, including k=0;
- the programs have equal complete endpoints for every payload dimension and
  every invertible substitution if and only if all these coefficients vanish;
- equality has a finite certificate consisting of at most D path rows, their
  initial-span coordinates and transition-closure coordinates;
- failure has a nonzero coefficient word of length k < D and an explicit
  simultaneous unipotent substitution in dimension k+1 <= D witnessing it.

The search below finds a shortest nonzero coefficient word. The independent
certificate checker certifies its nonzeroness, **not shortestness**. It does
not claim a least-dimensional witness among arbitrary invertible matrices.

The executable supports K=Q and prime fields F_p with p <= 2^31-1. Rational
input denominators must be nonzero in F_p. The written theorem holds over any
field. There are no commutation, involution, Clifford, adjoint or other
relations; a failure need not persist after imposing such extra relations.
Only inverses of named generators are in the grammar, not inverses of arbitrary
operator sums or matrices of operators.

## 2. One atom per unary occurrence

Create r leaf atoms x_i. Maintain each register as a scalar row in the atom
list. Each linear instruction updates that row. Each unary occurrence with
pre-instruction source row e creates a fresh atom z_j = G_a^s (e z).
An apply instruction replaces the destination by z_j; a query adds c z_j to
the old destination. Even a self-source query takes e before the update.

Compile the two programs with separate mutable register tables but the same r
leaf atoms. Append all unary atoms from both sides to one list. Their source
rows use earlier atoms only. Thus there are exactly D atoms. U is the
left-minus-right matrix of all final role expressions; it retains each input
role and each output role independently. An atom is an algebraic compiler
record, not a clean physical register or a free allocation.

Work in noncommutative formal series K<<Y_a>> and put G_a=1+Y_a. Its inverse
is the formal geometric series, well-defined over every characteristic. For a
forward occurrence and an inverse occurrence, respectively, the defining
equations are

    z_j = e z + Y_a e z,
    z_j = e z - Y_a z_j.

The second equation follows by multiplying z_j=(1+Y_a)^(-1)e z by 1+Y_a.
It is the inverse-aware step: a negative diagonal feedback term, not a new
independent operator label and not a truncated polynomial expansion.

Let E have row e at every unary atom and zero leaf rows. Let V0 embed the r
input roles at the leaf rows. For each a, let A_a have row e at a forward
a-occurrence, row -unit_j at an inverse a-occurrence, and zero elsewhere.
Then, with scalar matrices commuting entrywise with the series letters,

    z = E z + V0 x + sum_a Y_a A_a z.

E is strictly lower triangular. Consequently H=(I-E)^(-1) is the finite
scalar matrix I+E+...+E^(D-1). Set V=H V0 and T_a=H A_a. The equations become

    z = V x + sum_a Y_a T_a z.

This system has a unique formal solution: each coefficient of positive length
is determined by shorter coefficients. Iterating gives exactly

    [a1 ... ak](U z) = U T_a1 ... T_ak V.

Word order is matrix-product order: `[B,A]` means BA and applies A first.
The inverse feedback means T_a need not be nilpotent. Infinite nonzero tails
are allowed even though D is finite.

The producer uses the equivalent triangular recurrences

    V_j = e V,
    (T_b)_j = e T_b + 1_(b=a) e                 (forward),
    (T_b)_j = e T_b - 1_(b=a) unit_j            (inverse),

where e only reads earlier rows. The checker instead reconstructs E,A_a and
the triangular inverse H. These are separately transcribed compilers.

## 3. Finite closure certificates

A positive certificate provides b <= D path rows B_l=U_o T_w and scalar
coordinate matrices L and C_a satisfying

    U = L B,          B T_a = C_a B for every a,          B V = 0.

These finite equations imply U T_w V=0 for every word by induction.
Independence, minimality and reachability of B are unnecessary for soundness;
the supplied paths merely specify B compactly and bind it to the program.

Conversely, if every coefficient is zero, the reachable space
R=span{U_o T_w} has dimension at most D, is transition-stable and annihilates V.
Choose a basis from reachable path rows. Its initial and closure coordinates
give the displayed certificate. A basis of paths shorter than D exists:
R_k, the span of paths of length at most k, cannot stop increasing and later
increase again, since R_(k+1)=R_k+sum_a R_k T_a. If R_0=0, everything is zero;
otherwise at most D-1 strict increases are possible.

Breadth-first search tests output projections of accepted independent path
rows and appends their independent successors. Rejected dependent rows add no
possible earlier distinguishing length: their expression uses accepted rows
of no greater length, whose successors span their successors. Hence a first
nonzero projection occurs at a shortest coefficient word, of length < D.
Exact elimination is in the producer only. The checker rebuilds the path rows
and verifies the displayed equations, or verifies one claimed nonzero
coefficient on failure. No acceptance check relies on Python `assert`.

With alphabet size s, dense production takes polynomially many field
operations (O(s D^3) for reachable-space search and coordinates, plus parsing
and compilation). Coordinate storage is O(s D^2+rD), with at most O(D^2)
path letters. The simple checker may rebuild each path from scratch, costing
O(D^4+sD^3) field operations. These are arithmetic bounds, not bounds on
rational coefficient bit lengths or a practical scaling guarantee.

## 4. Why zero series implies every invertible substitution

Formal series cannot be evaluated directly at arbitrary matrices by summing an
infinite series. The following argument supplies the missing step.

Fix any dimension n and any tuple of invertible matrices M_a over K. Introduce
one central indeterminate t and substitute

    G_a(t) = I + t(M_a-I).

Each G_a(t) has determinant with constant term 1, so is invertible over K(t)
and its inverse has a well-defined expansion in K[[t]]. The program endpoint
is therefore a matrix of rational functions regular at t=0. Its formal
expansion is precisely the specialization Y_a -> t(M_a-I) of the series from
Section 2: in each degree there are only finitely many words, so substitution
is legitimate.

If the noncommutative endpoint series is zero, this matrix has identically
zero power series at t=0. A rational function regular at zero with zero formal
expansion is zero in K(t): multiply by its denominator, whose constant term is
nonzero. Finally every inverse occurrence is regular at t=1, since
det G_a(1)=det M_a != 0. Evaluating the zero rational endpoint at t=1 proves
equality for this arbitrary invertible tuple M_a. This is valid over finite
fields as well; it uses a formal indeterminate, not sampling field elements.

Thus a finite closure certificate proves the complete universal invertible
endpoint claim, without assuming convergence, generic numerical invertibility
or an infinite-field polynomial identity heuristic.

## 5. Nonzero series gives an explicit invertible witness

Suppose c=(U T_a1 ... T_ak V)_(o,i) is nonzero. On the basis e_0,...,e_k let

    N_a = sum_(j=0 to k-1, a_(j+1)=a) E_(j,j+1),
    G_a = I + N_a.

All N_a share the same strictly upper-triangular flag. All products of more
than k such matrices vanish, and each inverse G_a^(-1) is the finite sum
I-N_a+N_a^2-...+(-N_a)^k. Therefore the formal-series substitution now really
is a finite calculation, also for programs containing inverse calls.

In matrix entry (0,k), shorter words give zero, longer words give zero, and a
word of length k gives one exactly when its labels are a1,...,ak in order.
The literal endpoint difference in block (o,i), entry (0,k), equals c.
Use input e_k in role i and zero vectors in other roles to exhibit a concrete
failure. The universal check had kept all roles independent; this choice of
one witness input imposes no clean-state assumption on the theorem.
For k=0 take dimension one and all G_a=I.

This proves the converse in Section 1 and the constructive dimension bound.
The literal matrix oracle computes inverses by Gaussian elimination and
executes the original instructions; it does not reuse T_a or the producer.

## 6. Boundaries and discriminating examples

The dirty-sandwich example has roles x,h,y, all arbitrary. It temporarily
changes h to h+A x, adds B h to y, restores h, and subtracts B h. Its complete
endpoint is (x,h,y+B A x). The reference program temporarily applies A to x,
queries B x into y, and applies A^(-1) to x. Both full endpoints agree.
Deleting any one of the eight left-side instructions yields a detectable
failure in each tested field. This example certifies the stated algebraic
boundary; it is not a proposed faster physical implementation or a new echo
construction.

A false commutator identity B^(-1)A^(-1)BA=I has a nonzero degree-two
coefficient. Scalar/one-dimensional substitutions cannot reveal that error;
the certificate's unipotent witness does. Self-source queries, omitted helper
returns and wrong inverse signs have distinct rejecting fixtures.

The family G^(-1)(I-G)^d expands to (-Y)^d/(1+Y), so its first coefficient
occurs at degree d and its tail continues indefinitely. The replay checks
coefficients beyond the program's number of unary occurrences. In F_p,
G^p-I=Y^p supplies a characteristic-sensitive delayed witness.

The stress example computes (A+B)^64 x, which has 2^64 distinct noncommutative
words, on both sides, and inserts a C^(-1),C cancellation on one side.
The complete two-role comparison uses D=260 states and no expanded words.
The helper is explicitly overwritten on both sides in this stress program;
the separate dirty-sandwich example tests actual helper restoration.

For a termwise tensor substitution choose the new generators G_a^(tensor f)
and their actual inverses. The theorem then applies at the enlarged payload
dimension. Scalar coefficients stay scalar; no tensor power of a sum or of
the whole register-role matrix is taken. This is only an algebraic interface
lemma. Native realizations, phases, rounding, rectangular typing, precision,
stock, hosting, fixed-tape cost, complete paid invoices and supplier admission
are not proved here. No selected frontier or kappa changes.

Prepared by Krzysztof Wójt with substantial OpenAI Codex assistance. Apache-2.0.
