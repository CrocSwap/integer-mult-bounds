# Construct the first successful projective pencil slice

## Contract and result

Let K=F_q be a supplied exact finite field, n>=1, and A,B in M_n(K).
The input pencil is regular: D(x,y)=det(xA+yB) is not identically zero.
Return the least positive integer e for which a projective slice is invertible
over F_(q^e), together with an explicit field representation, projective point,
literal slice and two-sided inverse. Infinity [1:0] is a valid output at e=1.
For a finite point the output is [alpha:1].

The algorithm below is deterministic, uses polynomially many operations in K,
and does not enumerate the irreducibles of all degrees through e. This fills
the raw-witness question in Nick Petalas's PR6451. Its sharp worst-case degree
threshold and companion attaining pencils are predecessor results. We do not
claim a new general polynomial-factoring algorithm or literature priority.

The arithmetic model supplies K, exact operations and equality, q, and an
explicit basis/encoding allowing enumeration of its elements without duplicates.
An operation in K includes inversion of a nonzero field element.
We charge the stated enumeration requests as well as field operations. Constructing
that base representation, primality/irreducibility admission, rational/bit/tape
costs and physical reversible cleanup are not consequences of this theorem.
The executable is a bounded prime-field reference, not an implementation of
every supplied prime-power representation.

## Raw determinant and the base-field branch

First compute det(A). If nonzero, return e=1, infinity, A and A^(-1).
Otherwise compute the nonzero polynomial

    f(t)=det(t A+B).

It has degree m<=n-1 because its leading degree-n coefficient is det(A)=0.
Regularity is equivalent to f!=0: D is its homogeneous degree-n lift. A zero
polynomial is therefore rejected, rather than treated as a failed finite search.
Polynomial fraction-free elimination with row pivots supplies f from raw A,B.

For completeness, its update is

    M_ij <- (p M_ij - M_ik M_kj)/previous_pivot,   i,j>k,

with initial previous_pivot=1 and row permutations tracked in the determinant
sign. Choose a nonzero pivot in the current column among remaining rows. The
Sylvester minor identity makes these divisions exact in K[t]; entries after a
stage are the corresponding signed minors. A missing pivot implies zero
determinant. In the regular case Gaussian elimination over K(t) always finds
a row pivot. A final sign correction gives f. This is the classical Bareiss
method, not a new determinant algorithm.

Now test f at min(q,n+1) distinct base elements in the supplied enumeration.
If f(a)!=0, return e=1, alpha=a, aA+B and its inverse. If q>n, n+1 trials
must find a nonroot by the degree bound. If every base element fails, then

    q <= m <= n-1.

In particular, the potentially large-q case terminates here. It never constructs
a dense polynomial of degree q. The conservative n+1 cap can be shortened but
no such optimization is needed for this claim. Constant nonzero f is valid.

## Find the least successful extension

For d=2,3,... in increasing order, let

    H_d(t)=t^(q^d)-t,       G_d=gcd(f,H_d), monic.

Finite-field Frobenius gives that H_d is squarefree, and its roots are exactly
F_(q^d) in an algebraic closure. Equivalently, its irreducible factors are the
monic irreducibles whose degrees divide d, each once. Consequently

    every finite slice over F_(q^d) is singular
       iff H_d divides f
       iff deg(G_d)=q^d.

Infinity is already singular and does not change with extension. The first d
with deg(G_d)<q^d is therefore exactly the required e. This is a sequential
search; existence is not presumed monotone in the integer degree.

The gcd can be computed from t^(q^d) modulo f, by exact modular powering;
there is no need to enumerate field elements or irreducible polynomials.
Termination follows once q^d>m. If the first success is e>1, failure at e-1
also yields H_(e-1)|f. Thus, at this actual stopping degree,

    q^(e-1) <= m <= n-1,
    q <= n-1,
    D := q^e <= q(n-1) <= (n-1)^2.

Every dense polynomial needed through this stopping point has polynomial
size in n. This bound uses the actual previous failure; PR6451's sharper
union-through-degree threshold is credited context and is not required here.

## Extract one missing factor

Form the nonconstant monic polynomial

    Q=H_e/G_e.

It is squarefree and coprime to f. Every irreducible factor h of Q has degree
r dividing e. If r<e, a root of h would already give f(alpha)!=0 in F_(q^r),
contradicting the minimality of e. Hence every factor of Q has degree exactly e.
It remains to obtain just one such factor, rather than list all irreducibles.

For any current squarefree divisor P of Q, consider the K-linear fixed space

    T_P = {b in K[t]/P : b^q=b}.

If P has r irreducible factors, the Chinese remainder theorem identifies its
quotient algebra with a product of r extension fields. The q-Frobenius-fixed
elements in each field are exactly K. Thus T_P is isomorphic to K^r and has
dimension r. Its matrix/kernel are obtained by ordinary finite-field linear
algebra on the powers 1,t,...,t^(deg P-1).

If deg(P)=e, P is already irreducible by the equal-degree property above.
Otherwise r>=2, so choose a nonconstant vector b in T_P. Its components in
K^r cannot all equal the same scalar c: that would make b constant modulo P.
For some c in K, gcd(P,b-c) therefore has positive degree strictly below deg(P).
Scan the q supplied scalars, retain one such proper monic divisor, and repeat.
All retained factors still have degree e, so degree strictly decreases and the
process ends at an irreducible h of degree e. Only one branch is retained.
This is classical Berlekamp splitting applied to the already isolated
equal-degree missing-root polynomial. Its q-way scan is paid, and q<n here.

## Construct and check the literal answer

Set L=K[t]/h and alpha=t mod h. Since h is irreducible, this is a field of
degree e over K. Since h is coprime to f, f(alpha)!=0. Therefore

    S=alpha A+B

is invertible. Gaussian elimination in L constructs S^(-1); direct multiplication
can check both S S^(-1)=I and S^(-1) S=I. For e=1 the returned field is K and
the finite-point scalar is the literal base element found earlier; infinity
uses A. This proves both existence of the returned witness and minimality.
No normalization, stabilizer, determinant-character or original-field SL
transport is inferred from extension invertibility.

## Conservative arithmetic and storage bill

All bounds below are arithmetic upper bounds, not timings or physical tariffs.
Use naive polynomial multiplication/division and ordinary Gaussian elimination.

- Polynomial Bareiss has O(n^3) updates. Its minor entries have degree at most
  n and intermediate numerators degree at most 2n, so O(n^5) operations in K
  suffice, with O(n^3) coefficient storage. Pivot searches and exact remainders
  are included. Infinity testing and the at-most-n+1 base trials fit this bound.
- Write L0 for the number of tested degrees. It is at most
  1+floor(log_q(max(1,m))). Modular powering and gcd computations cost at most
  O(L0*(n+D)^2*log(D)) operations, a deliberately loose bound that includes
  reducing f when its degree exceeds the dense Frobenius degree D.
- At a Berlekamp stage of degree s<=D, forming the Frobenius matrix by modular
  powers costs O(s^3*log(q*s)), and its kernel costs O(s^3). Scanning q scalar
  gcds costs O(q*s^2). There are fewer than D stages. Thus a safe total is
  O(D^4*log(q*D)+q*D^3), with O(D^2) simultaneous coefficient storage.
- The final extension inverse and its two matrix-product checks cost
  O(n^3*e^2) base-field operations using naive extension arithmetic, and
  O(n^2*e) output coefficients. Extended Euclid supplies extension inverses.
- Enumeration requests are at most n+1 in the large-q base branch and at most
  q per proper-factor stage in the extension branch. Their representation
  overhead must be charged by any concrete field backend.

The bounded reference uses Fermat powering instead of extended Euclid for
extension inverses. Its at-most-n pivot inversions add O(n*e^3*log q)
base-field operations. This remains within the coarse extension-branch bound
below. Python's implementation of a supplied base-field inversion is backend
work, rather than a claim of one machine/bit instruction. Trace counters do
not purport to measure every coefficient operation in the asymptotic proof.

If e>1, q<n, D<n^2, e=O(log n) and L0=O(log n), so these are polynomial in n;
for example O(n^8*log n) is a coarse combined field-operation bound for n>=2.
If e=1, the determinant/base/inverse branch is polynomial without a dense q
allocation. We claim neither an optimal bound nor a runtime improvement over
an existing implementation. A supplied field operation is not a unit physical
or bit operation, and this bill does not fund field descent or a native caller.

## Evidence, attribution and remaining boundaries

Finite reference checks are corroboration, not the proof of the quantified
algorithm or operation bounds. PENCILS.json contains explicit raw inputs and
source/elementary expectations; it is not a table of computed algorithm outputs.
The separate oracle uses literal extension fields and actual matrix operations,
not the Frobenius-gcd/Berlekamp construction. It independently checks all
declared census degrees/statuses and the named returned witnesses; a claim
that it checks every primary census inverse is deliberately not made.

Credit Nick Petalas/PR6451 for the sharp threshold, attaining pencils and raw-
witness question; Ali Romman/PR5689/5692/5712 for regular raw-pencil interfaces,
decomposition with classical factorization and transport; apoursh/5672,
Petalas/5250, David Ganz and the retained tensor-atlas lineage. Frobenius,
Sylvester's identity, Bareiss elimination, Berlekamp splitting and the Chinese
remainder theorem are classical. No predecessor program or census is executed.

The arithmetic construction does not supply a physical native operation,
original-field descent/SL transport, coefficient invoice, arbitrary dirty
restoration, routing, precision, stock, tapes, compiler or outer admission.
All five selected framework assumptions remain. No new kappa, selected-frontier
change, independent human acceptance or formal proof-kernel result is claimed.
