# Proof and explicit recovery program

## Frozen group and evaluation

TARGET.json contains 256 distinct records with coefficient +1/16 or -1/16.
A record (p,s) is the actual monomial matrix g e_j = i^{s(j)} e_{p(j)}.
Multiplication is composition, including every fourth-root phase. The verifier
never quotients by a central scalar or by a symplectic tableau. Let G be the
finite subgroup of these monomial matrices generated as needed below, and write
A=(1/16) sum_g a_g [g] in the complex group algebra, with a_g = +/-1.
For every f >= 0, evaluation rho_f([g])=g tensor ... tensor g is a unital
star-algebra homomorphism. Define A_f=rho_f(A). The coefficient a_g is outside
the tensor power: a tensor power of a sum is not used.

## Exact, bounded certificate

Let B=sum_{g,h} a_g a_h [g^{-1}h]. The verifier constructs B by integer
convolution. It has 704 nonzero coefficients, each divisible by 64. Thus
H=B/64=4 A* A has integer coefficients and coefficient l1 norm 1024.
Define C=H/64=A* A/16.

The low-first coefficients of the polynomial p are the literal POLY list in
verify.py. It has degree 18, is monic, and p=x q with q(0)=-40131624960.
The exact certificate is H * (64^17 q(H/64))=0 in the INTEGER group algebra.
The verifier evaluates this identity over unbounded Python integers on all
21,504 group elements, without modular reduction. It also checks the complete
coefficient table of H and every factor used to accelerate multiplication.
Consequently p(C)=0 in the group algebra and after evaluation at every width.

For reproducibility, the acceleration is itself an exact factorization. Put
c=i I, and let X0 and Z0,Z1,Z2 be the usual three-bit Pauli monomials. The
five factors (I+c^2), (I+c X0), (I+Z0), (I+Z1), (I+Z2) expand to the 32-element
subgroup average 32 D. Direct coefficient comparison proves D A=A and splits
the support of A into eight signed left cosets. If b0 is their signed sum of
representatives, A=2 D b0. Conjugating the five subgroup generators by one
representative r0, and setting b=r0^{-1}b0, gives exactly

\[
H=\frac12 b^*\prod_{j=0}^4 (I+r_0^{-1}d_jr_0)b.
\]

All factors belong to the 21,504-element Gram subgroup. The verifier reconstructs
this subgroup, checks the factorization against the independently convolved B,
and applies the rightmost factor first. Every division by 2 is checked integral.
No representation quotient replaces group-algebra equality.

A conservative bound starts at beta=1 and, for k=16,...,0, replaces beta by
`1024*beta + abs(q[k])*64**(17-k)`. The final multiplication has bound
`1024*beta`. The maximum bound has 187 bits, below 2^255. This also justifies a
separate exact signed 256-bit implementation; the public verifier uses Python
integers and does not rely on fixed-width overflow assumptions. Earlier modular
minimal-polynomial searches were discovery aids, not the certificate.

## Support projector and rank

C_f=A_f* A_f/16 is Hermitian positive semidefinite. Its nonzero eigenvalues
are roots of q because p(C_f)=0. Since q(0) is nonzero,

\[
P_{R,f}=I-q(C_f)/q(0)
\]

acts as 0 on ker A_f and as 1 on its orthogonal complement. It is the right
support projector onto im A_f*. Its trace equals rank A_f.
Expanding this polynomial in the actual group basis and grouping by the exact
complex trace of each 8 by 8 monomial gives the following nonzero contributions:

| trace of g | coefficient in trace(P_R) |
|---|---|
| -8 | 3/256 |
| -4 | 1/64 |
| -2 | -1/8 |
| 2 | -1/8 |
| 4 | 1/64 |
| 8 | 3/256 |

The verifier computes this table by integer arithmetic followed by rational
reduction. Every nonreal trace contribution cancels. Since
trace(g^{tensor f})=trace(g)^f, the displayed rank formula follows for ALL
integers f >= 1. Terms with trace zero can then be omitted. The restriction
f >= 1 is essential: a zero trace base contributes 0^0 at formal width zero,
and the displayed six-term expression is not the width-zero rank.

## Constructive pseudoinverse and output recovery

Write s(x)=(q(x)-q(0))/x and R(x)=-s(x)/q(0), an explicit polynomial of degree 16.
Then x R(x)=1-q(x)/q(0). Define

\[
A_f^\dagger=\frac1{16} R(C_f) A_f^*.
\]

Multiplication gives A_f^dagger A_f=C_f R(C_f)=P_R,f. The matrix A_f A_f*
has the same positive eigenvalues as A_f* A_f, and its zero eigenspace is
ker A_f*. Therefore the same polynomial gives the LEFT output projector
P_L,f=I-q(A_f A_f*/16)/q(0), and A_f A_f^dagger=P_L,f.
These statements can also be checked on each singular vector pair. They imply
all four Moore-Penrose identities, and for every arbitrary input y,

\[
A_f^\dagger(A_f y)=P_{R,f}y.
\]

In particular an inherited partial channel z=A_f K_f x constructively determines
P_R,f K_f x. It does not determine the complementary projection of K_f x.
The zero odd-width channel has pseudoinverse zero, as the same formula shows.

There is a uniform numerical bound independent of f: ||A_f||_2 <= 16 from its
coefficient sum, and ||C_f||_2 <= 16 from ||H||_1/64. Thus

\[
||A_f^\dagger||_2 \le
\frac{\sum_{k=0}^{16}|q_{k+1}|16^k}{|q_0|},
\]

where q_k is the low-first coefficient of q. This deliberately coarse but
explicit finite constant proves that no inverse norm growing with width is
hidden in the recovery program.

## Native cost, ownership and limits

R(C)A* is a fixed finite rational linear combination of actual monomials.
It supplies an explicit recovery PROGRAM, rather than an assumed decoder oracle.
For a fixed buffer/limb constant c, require 2^w >= c N: equivalently w >= log2 N + O(1), with address headroom for the retained input and three owned buffers. Include rounded payload and fixed guard words in the scalar-cost contract. For N=8^f, each lifted three-bit monomial is evaluated by a base-8 address
odometer; updating the changed digit contributions takes O(N) total operations,
including phases. Evaluating each fixed sum into an OWNED zero output buffer
retains the entire arbitrary input and every other live bank. One may use three owned buffers: retain A* applied to the original input in one buffer and alternate the other two for Horner evaluation, charging initialization, linear passes and clearing. Buffer ownership and clearing are not obtained from a dirty unknown
bank by overwriting it.

The total number of monomial passes is a fixed constant independent of f.
There are fixed rational coefficients, including odd denominators from q(0).
If an admitted word model charges d(w) operations for the prescribed rounded
fixed-rational scalar arithmetic at w-bit precision, total cost is O(N d(w)),
plus initialization and clearing; O(N) follows only under a justified constant
scalar-cost contract. The polynomial has fixed degree and coefficient height.
For inputs with coordinate magnitude at most B and a desired coordinate error delta, a conservative total precision is O(log(2+B) + log N + log(1/delta)) bits, with fixed additive constants determined by the displayed coefficients and norm bound. The log N term safely covers
conversion between coordinate and Euclidean errors; no precision oracle is
assumed. Actual source input precision, error budget and native supplier tariff
still require a consumer-specific invoice.

The rank theorem and polynomial recovery are unconditional algebraic statements
about the frozen A. No new complete supplier, paid saving or kappa follows from
them alone. Independent missing coordinates, retained complements and physical
chronology must still be supplied and charged.

## Controls and precedent

The verifier checks a changed source byte against its SHA256 pin; confirms a
constant-polynomial mutation has nonzero residual H; and checks that the actual
central -I is distinct from I and squares to I. The exact checks remain active
under Python optimization. They protect source integrity, polynomial identity
and central phase semantics respectively.

JoyboyBrian's PR #4797 provides the frozen coefficient, partial-channel identity,
norm analysis and rank question. Nick Petalas's PR #4825 supplies the exact
width-four rank 100 certificate and asks for a general even-width formula.
Its lineage credits Yiyang (#4710 phase repair and staggered continuation),
lee-phys (#4688 two-image prefix), and Jacob Sussman (#4628 free alphabet).
This contribution by Dugongue derives the all-width group-algebra certificate,
rank formula and explicit uniform pseudoinverse. It does not claim invention of
spectral projectors, group algebras or Moore-Penrose inversion. No proof-kernel
or independent human audit is asserted.

## Explicit basic-arithmetic fallback

The cost parameter d(w) does not assume a hidden division oracle. If only bounded-word addition, subtraction, shifts, bit operations and comparisons are available, multiply by each fixed integer numerator with its fixed finite shift/add expansion. Divide by a fixed positive denominator by ordinary restoring long division: scan the w input bits, keep a remainder below that denominator, and emit one quotient bit after one comparison/subtraction. The denominator and numerator heights are fixed constants; for sufficiently large w the remainder uses a fixed number of words. Round using the final remainder and retain the sign separately. This gives an explicit conservative d(w)=O(w) implementation, hence O(N w) recovery, with fixed-size setup for small w. It is not an O(N) or improved multiplication-complexity claim. Faster admitted scalar arithmetic may replace this fallback only with its own invoice.
