# Removing auxiliary roots from the characteristic-two predictor

Status: **finite refinement accepted by independent Route B review** at
[review-power-two-degree-predictor.md](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/routes/B/review-power-two-degree-predictor.md). This is
an optional representation improvement. The already accepted whole-input
theorem uses its previously audited constructor and constants unchanged.

## 1. A power-of-two-compatible count window

For m>=4096 let B=3ceil(sqrt m), take T=2^t as the least power of two
at least 2B+1, and put

    D=T-1,
    u=m-floor(D/2),   v=u+D.

Then D>=2B, D=O(sqrt m), and D<=m. The integer window contains every
count within distance B of its mean m. Hence the same order-three count
tail bound gives fewer than 1/32 exceptional shifts at every frequency.
The small initial range can use the total known constructor.

Let B_i be the degree-controlled bit formulas for (c-u) modulo T from
[characteristic-two-count-formula.md](characteristic-two-count-formula.md), and put a=omega-1. Since the entire
range 0<=h<T is retained, distributivity gives the exact formal identity

    sum_(h=0)^(T-1) a^h product_(i:h_i=1) B_i
        = product_(i=0)^(t-1) (1+a^(2^i) B_i).           (P2-1)

Multiplying by the source phase omega^(u-sum beta) gives the original
truncated predictor on all allowed spectral tuples. Its degree budget is
sum_i 2^i=D and its formula size is polynomial in m.

## 2. Every addition has a power-of-two degree budget

Assign the formula for bit i and its incoming carry the explicit length
budget 2^i, even if its actual syntactic degree is smaller. Affine or zero
leaves can be identity-padded to that length. The factored carry

    xy+(x+y)c

then uses two products of length 2^{i+1}, an addition at that same length,
and an inner addition at length 2^i. Output-bit additions and the fixed
offset obey the same rule. Each factor 1+a^(2^i)B_i in (P2-1) has an
addition budget 2^i. Finally multiply those factors by concatenation;
these products require no addition at their non-dyadic total lengths.

Thus every sum gate in this prescribed formula has power-of-two length.
In the characteristic-two cyclic tensor sum, one can set the twist xi=1:
the operators X and Y commute and Frobenius gives

    (X+Y)^(2^i)=X^(2^i)+Y^(2^i).

No auxiliary root is needed. The full-rate D-factor predictor is defined
over F4 itself. Its row dimension is a product of power-of-two sum budgets,
hence is a power of two, and remains at most D^S=2^{m^C}. It accepts an
arbitrary independent input on every coordinate. All coefficients in its
affine factors are among the four base-field elements.

This does not contradict the need for roots at an arbitrary odd sum
degree: the prescribed degree architecture avoids those sum degrees.
The final product length D is odd, but that product uses concatenation,
not a degree-D tensor sum.

## 3. Check nodes in a polynomial-degree finite field

Let R=32*3^m*w be the pre-descent independent row count. Take
e=ceil(log_4 R) and explicitly construct a monic irreducible f of degree
e over F4. Then

    E=F4[X]/f,   |E|=4^e>=R,   [E:F4]=e=O(log R)=m^O(1). (P2-2)

Use the first R distinct coordinate vectors as check nodes. Every nonzero
node difference is a unit in this field, so the same source Hermite check
and interpolation identities apply. No relation between the check nodes
and the order-three query root is required.

An entirely bounded constructor suffices. Enumerate all 4^e monic
degree-e candidates and test each by division by every monic polynomial
of degrees at most floor(e/2). Reducibility is exactly the existence of
one such factor. There are O(4^(e/2)) trial factors, and schoolbook
division uses poly(e) four-element operations. The whole search therefore
uses at most 4^(3e/2)poly(e)=R^O(1) time and space, including construction
of the candidate and divisor lists. It need not enumerate a larger field
or invoke an unbounded factorization search.

For completeness, existence of a degree-e irreducible follows from the
roots of X^(4^e)-X in an algebraic closure. They form a field of 4^e
elements. Elements of smaller degree lie in subfields of sizes 4^d with
proper divisors d of e; their total size is at most
sum_(i=1)^floor(e/2) 4^i<4^e. Thus at least one element has degree e.
For e=1 use a linear polynomial. This proves termination of the stated
finite enumeration.

Represent every element by its e coefficients in F4. Scalar multiplication
and inversion have ordinary polynomial-e algorithms, for example schoolbook
polynomial multiplication/reduction and exponentiation to 4^e-2. All
repair tables and 3^m spectral cases still have R^O(1) construction work.
The completed target descends to 2e binary coordinates, a polynomial-m
factor, rather than requiring a cyclotomic degree comparable to R.

## 4. Consequence and limit

This refinement keeps the same 2^{m^C} finite-data envelope and therefore
does not improve the already accepted whole-input rate. It gives a more
structured finite target: a base-F4 predictor and only polynomial-m scalar
coordinate degree during repair. Changing the width of the count window
changes the absolute stage coefficient; applying this variant to an
existing explicit invoice requires enlarging that coefficient, not silently
reusing its old numerical constant.

The exponential row width, dense row/check operations, numeric address
costs and current physical compiler thresholds still remain. A smaller
scalar extension alone does not make those operations polynomial in m
per input row. Those are concrete remaining interfaces for a future
structured implementation, not costs proved away by this note.

Credits: source count prediction and check repair; elementary Frobenius,
finite-field and binomial identities; cyclic tensor factorization as cited
by B/C; @CubeJerry; AI-assisted representation refinement.
