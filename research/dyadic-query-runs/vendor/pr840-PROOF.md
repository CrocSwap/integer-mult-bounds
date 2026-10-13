# Three queries for a centered dyadic native BIT shear

This is a local recursive-interface construction and a scoped query lower
bound. Ordinary ADDRESS interchange and ordered affine tape streams remain
premises. There is no new supplier, kappa, or formal multiplication proof.

## Object and predecessor contracts

Karl Appel / applecrusher's PR521 gives the native unipotent query below and
its one-child lowering at `k=1`. PR677 by commdata2338 completes the shear
`S_h(x,y,z)=(x+(h+I)y,y,z)` using two queries on the DATA target. Its source
remains untouched, and no full private row is required. VALUE addition is
over F2; ADDRESS arithmetic is rational arithmetic specialized to an odd
residue ring. The contribution here combines **two completed shears**,
extends the literal lowering to signed dyadic powers, and changes the
intermediate query to `h^(2a)`. It is not PR521's unfinished dirty chart.

Use six physically ordered equal-width ADDRESS fields
`(H0,H1,H2,D0,D1,D2)`, each ranging over `Z/(ell^b)`, `b>=1`, `ell` odd.
Arbitrary intervening/exterior spectator fields and suffix VALUE records
are retained. Define column vectors

    s=(1,0,1,-1,0,-1)^T, r=(1,0,-1,-1,0,1)^T,
    M(k)=I6+(k/4)s r^T.

Since `r^T s=0`, `M(k)M(l)=M(k+l)` and `M(k)^-1=M(-k)`.
Let `h` be the array permutation induced by the ADDRESS **push** map `M(1)`.
Thus a VALUE moves from address `z` to `M(1)z`, and the value at a new address
is read from its inverse image. The full-array operator for `M(k)` is `h^k`.

For each fixed integer `j>=0`, let `a=+/-2^j`. The desired completed endpoint is

    F_a(x,y,z)=(x+(h^a+h^-a)y,y,z).                     (1)

Every additional arbitrary dirty row is unchanged. Source `y` is never
modified. The target requires exclusive access until the completed boundary;
the caller may not read its temporarily permuted representation mid-program.
This is the same target permission needed by PR677's DATA-target program.

## One-child lowering of every signed dyadic power

Put `c=k/4`, for `k=+/-2^j`. Apply, chronologically,

    z2 <- z2-z0
    z3 <- z3+z0
    z5 <- c*z5+(1+c)*z0-c*z2-c*z3
    CHILD_C(0,5)
    z2 <- z2+z0
    z3 <- z3-z0
    z5 <- -(1/c)*z5+(1/c-1)*z0+z2+z3.                (2)

Every control precedes its target. The child swaps exactly two `b`-digit
fields on the complete queried BIT row, preserving every spectator. All six
affine events are charged, including their preparation, temporary tapes,
source access, counter work and head returns. The child uses its own restored
workspace; it is not an uncharged VALUE swap.

To check (2), write incoming coordinates as `A,B,C,D,E,F` and
`d=A-C-D+F`. Just before the child, the later field is `A+c*d`, and the
middle fields are `C-A,D+A`. After the child and the next two events,
the first field is `A+c*d`, and the middle fields are `C+c*d,D-c*d`.
The final line gives `F-c*d`. Coordinates 1 and 4 stay fixed. This is
exactly `z+(k/4)s(r^T z)=M(k)z`. The literal reverse of (2), inverting
each affine event and using the same involutive child, implements `M(-k)`.

The only diagonal units are `1,c,-1/c`. All numerator and denominator
factors of these units are powers of two, up to sign. Every control
denominator is also a power of two. Therefore (2) and its inverse
specialize to **every odd modulus**, including every odd prime-power
width. A control numerator may vanish modulo ell without invalidating a
diagonal. An arbitrary non-dyadic k would introduce prime exclusions into
this particular lowering; no such all-odd-radix claim is made.

At k=1 this is exactly PR521's attributed word. The extension changes its
coefficients, not its tape/child contracts. For a fixed j, the finite
coefficient table is compiled into the machine description. Its size and
streaming constants depend on j. A growing j is separately priced below.

## Completed pair fusion

Two successive applications of PR677's completed DATA-target program,
for `h^a` and `h^-a`, produce (1): the two identity contributions cancel
over F2. This literal baseline has four queries and four XOR scans.

Instead apply, chronologically,

    x <- h^-a x
    x += y
    x <- h^(2a) x
    x += y
    x <- h^-a x.                                    (3)

Following x gives `h^-a x+y`, then `h^a x+h^(2a)y`, then
`h^a x+h^(2a)y+y`, finally `x+h^a y+h^-a y`. The three target
permutations multiply to the identity. The unchanged source and spectators
can be arbitrarily dirty. No private row is initialized, borrowed, copied
or cleared. Because (1) is a VALUE shear, `F_a^2=I` despite `h^a` being
noninvolutive. Reversing and inverting the literal events restores all data.

Lowering all queries by (2) gives **three separately paid ordinary children,
eighteen affine events and two XOR scans**, versus four children,
twenty-four affine events and four XOR scans for the completed pair.
This is a count comparison for this baseline; physical speed is not measured.

## Three queries are necessary in the stated model

Allow d>=2 arbitrary dirty F2-valued rows, invertible address-independent
linear XOR maps between row roles, and queries `h^e` on one row for any
integer e. All other ADDRESS maps, clean/disposable storage, erasure,
nonlinear VALUE gates and intermediate observations lie outside this model.
The lower bound counts queries, even when a non-dyadic power would need a
different physical lowering. It is not a lower bound on all tape programs.

Restrict the complete ADDRESS domain to the orbit of `e_H0` under h.
Its addresses are `e_H0+k*s/4`, indexed by `Z/m`, `m=ell^b`. They are
distinct because a component of s and 1/4 are units. Hence h is multiplication
by t on the regular module of `R=F2[t,t^-1]/(t^m-1)`. Basis monomials
`1,t,...,t^(m-1)` are independent; zero divisors in R do not affect the
following determinant and coefficient arguments. The same proof works
over the Laurent ring for a uniform symbolic identity.
The determinants are those of d-by-d row matrices over R, not of the
expanded F2 matrix of all individual BIT positions.

Move all constant row maps to the left, conjugating queries. At t=1,
the target `I+(t^a+t^-a)N`, `N=e_x e_y^T`, is I, so the remaining
constant map is I. A normalized query has the form

    D_P(t^e)=I+(t^e+1)P, P=u v^T, v^T u=1,
    det D_P(t^e)=t^e.                                (4)

The determinant of the target is one. Zero queries cannot produce its
nonzero off-diagonal entry: a is a unit modulo odd m and `t^a!=t^-a`.
One query either is the identity (e=0 modulo m) or has the wrong determinant.
For two queries, the determinant forces opposite exponents modulo m,
and their product is

    I+P+Q+t^e(P+PQ)+t^-e(Q+PQ).                      (5)

If e=0 modulo m, both are identity. Otherwise, as m is odd, `1,t^e,t^-e`
are distinct basis monomials. The target's constant coefficient is I.
Comparing constant coefficients in (5) therefore forces P=Q. Then
`P^2=P` cancels both other coefficients and (5) is I, a contradiction.
Thus no two-query program implements (1), even with arbitrary dirty
spectator rows and arbitrary integer-power queries. Program (3) attains
three. This is a written algebraic proof, not an inference from finite tests.

PR677's different first-difference target has constant coefficient `I+N`
and attains two queries. Its theorem is preserved. Allowing `h^(2a)` here
changes the physical query alphabet: substituting two `h^a` calls would
restore the four-child bill. At an even orbit a centered target can vanish;
the odd full-order hypothesis is necessary for this formulation.

## Complete typed costs and workspace

Let each genuine DATA row have full logical BIT volume U, including every
spectator range; V=3U and N=3b. Let C(U,b) pay one ordinary ADDRESS
interchange with restored child workspace. Let L_k(U,b) be the sum of the
six actual ordered-affine charges in (2), **including** finite coefficient
preparation, source access, counter work, temporary tapes and their returns.
Let X(U) pay one aligned XOR scan. Let R_f,R_b pay row split/merge, evaluator
routing, descriptors, parking and all additional head returns. Then

    B_a(V,3b) <= 4 C(U,b)+2 L_a(U,b)+2 L_-a(U,b)+4 X(U)+R_b,
    F_a(V,3b) <= 3 C(U,b)+2 L_-a(U,b)+L_2a(U,b)+2 X(U)+R_f. (6)

The new middle lowering has a different coefficient table. Equation (6)
does not assume equal costs for it. Relative to these literal invoices,
the saving is `C+2 L_a-L_2a+2 X+R_b-R_f`; this is not asserted positive
for every finite implementation. Under the retained tape contracts and
**fixed j**, L_k, X and R are O_j(V), giving normalized recursive-child
coefficients 4/3 and 1 respectively. The three children are sequential,
each on actual volume V/3 and width N/3. Persistent genuine-role storage is
V in both programs, with no additional full private role. A safe peak bound is

    W_f(V,3b) <= V+B_f(V,b,j)+W_C(U,b),

where B_f pays streaming, counter/coefficient and evaluator parking workspace.
No exact physical tape count or scratch-cell saving is claimed.

For growing j, table entries have O(j+1) numerator/denominator bits and
modular preparations and all primitive costs must retain their j dependence.
In particular the original direct multiplication stream can have a number
of pieces depending on a fixed large integer. No polynomial-in-j runtime
or uniform O(V) constant is inferred from (2). The `j=54` fixture is exact
coefficient evidence, not a practical performance demonstration.

The left sides of (6) are a centered DATA shear; C is ordinary ADDRESS
interchange. Replacing C by F_a and solving a self-recursion would require
a separate compiler and would be circular here. Arbitrary-width padding,
common-label construction, scalar/frame/owner schedules, both supplier
invoices, precision/tape/hosting and analytic transfer remain obligations.
No supplier or assembly constraint is changed, so no new kappa follows.

## Evidence boundary

The checker compares (2) to an independently derived rational matrix and
modular formula, checks the VALUE endpoint over exact Laurent matrices,
and uses a separate sparse-set full-domain replay. Negative controls remove
children, change powers/directions, omit scans, destroy a dirty spectator,
and demonstrate the first-difference/even-orbit scope boundaries.
The recorded finite domains, fixed seed-selected coefficient and source pins
are in CERTIFICATE.json and SOURCES.json. No search outside those domains,
proof-assistant verification, complete supplier replay or runtime benchmark
is claimed. The universal argument above remains open to mathematical review.
