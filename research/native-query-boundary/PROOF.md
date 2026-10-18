# Native queries at the ordinary BIT boundary

This note gives a scoped obstruction, an abstract two-block encoding theorem,
and a finite construction that escapes the obstruction. It does not give a
new supplier or a new kappa. All ranks below are ranks of actual binary VALUE
operators. They are not ranks of rational ADDRESS
matrices. The proofs apply to arbitrary input bits.

## 1. Complete domains and endpoints

Let p be an odd prime, b >= 1, and m = p^b. Put A = Z/m and let Sigma be a
spectator set of size S >= 1. One complete row has ADDRESS domain

    Omega = A^6 x Sigma,       U = S m^6.

The six fields are `(H0,H1,H2,D0,D1,D2)`. Every field has b radix-p digits.
The native push map from Karl Appel's PR521 is

    h(z) = z + (r^T z / 4) s,
    s = (1,0,1,-1,0,-1)^T,
    r = (1,0,-1,-1,0,1)^T.

It acts as the identity on Sigma. Since r^T s = 0, its kth power replaces
1/4 by k/4. The map is defined on every odd prime-power ring. Write h also
for its binary permutation operator on a complete row.

For any signed dyadic unit a = +/-2^j, PR840 implements

    F_a = I + E_xy tensor (h^a + h^-a)

on three complete rows. Here E_xy sends row y to row x and is zero on the
other rows. Thus E_xy^2 = 0. Every other dirty row is unchanged. PR840 lowers
this operation to three ordinary children, eighteen ordered affine events,
and two full-row XOR scans. Its middle native query has power 2a.

Let Z interchange the two complete three-field banks. It sends `(H,D)` to
`(D,H)` and preserves Sigma. An ordinary completed boundary on q genuine
rows, with restored dirty helpers, is

    T_q = diag(Z,...,Z,I,...,I),      q >= 1.

A weighted or reversed ordinary bank interchange has the same rank as Z.
Its ADDRESS form is `(H,D) -> (A J D, J A^-1 H)`, where J reverses the three
atom positions and A is an invertible diagonal unit matrix. Each D determines
exactly one fixed H. Thus it has S m^3 fixed addresses. The weights can vary
with Sigma and with the role. This does not change that count.

**Frame normalization is a premise.** In a caller, a dirty helper can have
physical endpoint `B_out h_in` instead of literal `h_in`. Remove the declared
entry and exit frames before applying a theorem about restored helpers.
Those removals are mathematical comparisons; they are not free tape passes.
The rank theorem below applies when the resulting normalized program is a
conjugate `E^-1 F_a E`. It does not follow merely because the physical word
has that form. If normalization gives different adapters, use Section 5.
A helper whose required physical endpoint is itself an ordinary interchange
can instead be counted among the q ordinary rows.

## 2. Exact native orbit count

Put lambda = r^T z / 4. This is a surjective map A^6 -> A. Each fiber has
m^5 points. The value lambda stays constant under h, and h adds lambda s.
The first coordinate of s is 1. Therefore an address with value lambda has
orbit length

    L(lambda) = m / gcd(m,lambda).

For lambda = 0 this length is 1. The other possible lengths are p^j,
1 <= j <= b. There are phi(p^j) values of lambda of order p^j. Hence the
number of h-orbits, with every spectator included, is

    K = S m^5 sum_lambda 1/L(lambda)
      = S m^5 [1 + b(1 - 1/p)].                         (1)

Equivalently, K = S m^4 sum_lambda gcd(m,lambda). The term for every j is
necessary. Treating all nonfixed orbits as length m is false when b > 1.
For m=9, the complete six-field domain has 59,049 fixed orbits, 39,366 orbits
of length 3, and 39,366 orbits of length 9.

A separate coordinate description checks the count. Set

    u = H0, lambda = (H0-H2-D0+D2)/4,
    v1 = H1, v2 = D1, v3 = H0+D0, v4 = H0-H2.

This is invertible over A. Its inverse is

    H0=u, H1=v1, H2=u-v4, D0=v3-u, D1=v2,
    D2=4 lambda-v4+v3-u.

In these coordinates h is `(u,lambda,v) -> (u+lambda,lambda,v)`.
This is an algebraic change of coordinates for the proof. No tape cost or
free implementation of that change is asserted.

## 3. No single-block conjugacy to whole ordinary rows

On one h-orbit of odd length L, the kernel of `h^a+h^-a` is the kernel of
`h^(2a)+I`. Since gcd(2a,L)=1, that kernel consists exactly of the constant
vectors on the orbit. It has dimension one over F2. Thus

    rank(F_a-I) = rank(h^a+h^-a) = U-K =: r.             (2)

A binary permutation involution has one rank-one difference block for each
pair of exchanged addresses. Its fixed addresses give zero blocks. Therefore

    rank(Z-I) = S(m^6-m^3)/2 =: t,
    rank(T_q-I) = q t.                                 (3)

For m=3, equations (1)--(3) give r=324S and t=351S, so `0<r<t`.
For every other odd prime power,

    t < r < 2t.                                        (4)

To prove the upper inequality, K > S m^3. To prove the lower inequality,
write d=1+b(1-1/p). It is enough that d<m/2. This holds at p>=5,b=1 and at
p=3,b=2. On increasing b by one, d increases by less than 1 and m is
multiplied by p>=3. Thus it continues to hold by induction. This covers all
remaining odd prime powers.

No positive integer q has r=q t. Appending identity helpers does not change
either rank. Conjugation by any invertible binary linear map preserves the
rank of an operator minus I. Consequently:

> One PR840 fused block cannot be converted into any positive number of
> whole ordinary three-field interchange rows by an arbitrary invertible
> binary linear encoding and its inverse, with any number of restored dirty
> helper rows. The statement includes weighted and reversed ordinary rows.

The encoding can mix all VALUE positions, all roles and all spectator
coordinates. It need not be an ADDRESS permutation. This is a full-domain
rank obstruction, not a bounded word search. It does not exclude different
entry and exit adapters, several fused blocks, or another required helper
endpoint before frame normalization.

For a product of k separately conjugated complete fused blocks, rank
subadditivity gives the necessary condition

    k >= ceil(q t/r).                                  (5)

Indeed, `AB-I=(A-I)B+(B-I)`, so ranks add as an upper bound. For q=3 and
S=1, the bound gives k>=4 at m=3, k>=3 at m=5,7,9, and k>=2 at m=11,27.
These small-width restrictions do not by themselves rule out an asymptotic
construction that stops recursion above those widths.

## 4. The native orbit quotient is still missing

This section concerns the unweighted bank swap Z. It commutes with h:
bank interchange sends both s and r to their negatives. It therefore induces
an involution Zbar on the set of native orbits.

Exactly S m^3 native orbits are fixed by Zbar. To prove this, use the sum
H+D and difference v=H-D. The sum is fixed by both maps. On v, the native
map is `v -> v+(1/2)u(t0^T v)`, with `u=(1,0,1)` and `t0=(1,0,-1)`.
If -v is in the orbit of v, then for some k,

    -v = v+(k/2)u(t0^T v).

Apply t0^T. Since t0^T u=0 and 2 is a unit, t0^T v=0. The displayed equation
then gives v=0. Conversely, v=0 is a fixed point. The sum has m^3 possible
values. This proves the claim, including rings with zero divisors.

Let pi sum the VALUE bits on each native orbit. For every integer e,
`pi h^e=pi`. Every completed centered shear has identity action after pi.
The PR677 first-difference shears and the complete PR990 batch also have
identity action there. Constant XOR maps can mix roles at one orbit; they
cannot move a value to another orbit.

Thus no circuit of same-h power queries and address-independent role XORs
can realize T_q, regardless of length or dirty-helper count. The stronger
class of all linear operations confined to individual native orbits also
fails. A fixed encoding that only permutes these orbit subspaces does not
remove the obstruction when it is decoded by its inverse.

A concrete failure witness is a bit at address e_H1. Both e_H1 and e_D1 are
separate fixed h-orbits. Z sends the first address to the second. A program
confined to native orbits cannot do so.

There is also an exact charge for new linear adapters. Suppose a circuit
adds arbitrary linear maps A_1,...,A_j to the same-h/XOR class. Delete those
maps, leaving a map P0. On the orbit quotient P0 acts as `B tensor I_K` for
one constant role matrix B. For the desired endpoint T_q, select one input
orbit and the opposite output orbit from each nonfixed Zbar pair. On the
q genuine rows this submatrix of `pi(T_q-P0)` is the identity. Hence

    rank(pi(T_q-P0)) >= q(K-S m^3)/2.

A telescoping product difference gives

    sum_i rank(A_i-I) >= q(K-S m^3)/2.                  (6)

The pi map cannot increase rank. The adapters may be interleaved, and they
need not preserve native orbits. Equation (6) identifies actual transport
that a conversion must supply. It is not a lower bound on tape time or on
recursive children. A high-rank map can still have a cheap streaming rule.

## 5. Different entry and exit maps

Let A_in and A_out be arbitrary invertible binary linear adapters. Do not
assume that they are inverses. If

    T = A_out F_a A_in,

then `T-A_out A_in = A_out(F_a-I)A_in` has rank r. In particular,

    rank(A_out A_in-I) >= rank(T-I)-r.                  (7)

For T=T_3 the right side is positive for every odd prime power. This shows
why the single-block result cannot be carried over to different boundary
frames without accounting for their product. It does not claim that this
rank forces an expensive adapter.

As a simple paid possibility, an arbitrary adapter can already contain the
required interchange. That is not an improvement. A less circular escape
uses two completed fused blocks and inverse adapter pairs. Section 6 gives
that construction and its literal all-input replay.

## 6. A complete two-block escape and its price

Use one genuine DATA row and two arbitrary dirty helper rows, each of full
volume U. The desired boundary is T_1. The helper rows must be restored in
the normalized physical coordinates used here. Let N=T_1-I, with rank t.
Let J be a binary basis in which N sends t basis vectors w_i to t independent
vectors v_i and is zero on all remaining basis vectors. Such a basis exists
because N^2=0. The verifier constructs the basis and checks every column.

At m=3, r=324 and t=351. On the t-dimensional map from w to v, put

    A = diag(0_27, I_27, C_297),       B=I_351+A.

Choose C_297 as a direct sum of one 3 by 3 companion block for `x^3+x+1`
and 147 two-dimensional companion blocks for `x^2+x+1`. Both C_297 and
I+C_297 are invertible. Thus A and B both have rank 324. Let N1,N2 have these
w-to-v blocks and be zero elsewhere. Then

    N1^2=N2^2=N1 N2=N2 N1=0,
    N1+N2=N,       (I+N2)(I+N1)=T_1.                  (8)

Both I+N_i are conjugate to F_a: in characteristic two, a square-zero
operator is determined up to similarity by its rank and ambient dimension.
The verifier does not just assume this classification. It builds a complete
basis of image/preimage pairs for each map, constructs the encoder E_i, and
checks `F_a E_i = E_i(I+N_i)` on every binary column.

Each block runs `E_i`, the literal PR840 lowering, then `E_i^-1`. Gaussian
row elimination emits each encoder as a list of individual bit-XOR transfers.
The full order-three execution checks all 2,187 independent input columns.
It also runs the literal inverse. No row is initialized, copied or cleared.
The two helper outputs equal their arbitrary inputs on every column.
A second execution lifts every encoder and child to two complete spectator
fibers and checks all 4,374 columns in both directions.

The same algebra gives a finite construction for every odd prime power.
For m>=5, r>t. Choose C_t and I+C_t invertible on the t target pairs. Put
that pair of complementary maps on those pairs. Add r-t equal nilpotent pairs
in helper coordinates to both factors. Their extra actions cancel in (8).
Both factors then have rank r. There is space: 2r<2U<3U. Every integer t>=2
can be split into blocks of sizes 2 and 3. This proves existence; only the
m=3 literal program and its two-fiber lift are executed in this package.

For that literal program the exact counts are:

| Item | Count |
|---|---:|
| Ordinary full-row children | 6 |
| Ordered affine events | 36 |
| Full-row XOR scans | 4 |
| Individual bit-XOR transfers in all encoders and decoders | 21,606 |
| Full dirty helper rows | 2 |

Let V denote the genuine DATA volume here, so V=U, not 3U. Let C(V,b) pay
one ordinary child and its restored work. Let L_k(V,b) pay the six ordered
affine events for native power k. It includes their source access, table
preparation, temporary tapes, counters and head returns. Let X(V) pay one
full-row XOR scan. Let Q(3V) pay a transfer of one selected bit to another
by complete scans of the three-row storage. The source bit is held in one
private zero cell; a later scan updates the target. Another source scan clears
that cell. All scans and head returns are paid by Q. The source is retained.
This gives a
finite, exact tape implementation without a constant-time random-access
premise. Let P(m,S) pay generation and storage of the encoder instructions,
and R(3V,b) pay routing, descriptors, parking and all remaining head returns.
The complete bill for this order-three escape is

    B_two(V,3b) <= 6 C(V,b) + 4 L_-1(V,b) + 2 L_2(V,b)
                   + 4 X(V) + 21606 Q(3V) + P(3,1) + R(3V,b). (9)

The two-fiber lift has 43,212 bit transfers, while every one of its six
children acts on the complete doubled row. Larger domains require their
own encoder bill G(m,S) in place of 21,606. Gaussian elimination is a finite
algorithm, but its growing instruction table is not a fixed all-size
linear-time stream contract. No such contract is claimed.

Persistent row storage is 3V. A safe peak bound also includes the encoder
table, its generation work, one bit for a transfer, primitive temporary tapes,
parking/descriptors and the restored child workspace. Calls are sequential.
No copy, clear or free recovery step is omitted.

Even with free encoders, this route cannot yield a positive BIT saving. It
would give recursive coefficient 6 with width reduction 3:

    B(V,3b)/V <= 6 C(V,b)/V + lower-order work.

For the trial bound C(V,n) proportional to V n^(1-c), its child moment is
`6/3^(1-c)=2*3^c`, which is greater than one for every c>=0. The two helper
rows are not productive DATA volume. Counting them as three productive rows
would falsely replace coefficient 6 by 2. The width remains b; retaining a
full spectator volume does not divide that width a second time.

For a different construction with three genuine output rows, k complete
fused blocks would instead cost `3k C(V/3,b)` plus every adapter and scan.
Its favorable normalized coefficient would be k. Section 7 proves the
abstract k=2 construction for m>=11 and identifies its encoder cost. Cheap
uniform encoders and recursive hosting are still open. The present result
does not prove that native fusion cannot help a supplier.

## 7. Two fused blocks suffice abstractly for three genuine rows

The three-genuine-row case has a stronger positive result. Let m>=11 be an
odd prime power. Put t3=3t. Equations (1)--(3) give

    r<t3,       e=2r-t3>=2.

For the second inequality it is enough that d=1+b(1-1/p)<m/4. This holds
at p>=11,b=1; at p=5 or 7,b=2; and at p=3,b=3. It persists when b increases,
as in Section 3. These base cases cover all odd prime powers m>=11. In fact
`e=S m^6/2 - 2K + 3S m^3/2 > 3S m^3/2` under this sufficient inequality.

In a Jordan basis for T_3-I, use

    A=diag(0_(t3-r), I_(t3-r), C_e),       B=I_t3+A.

Both A and B have rank r. Here C_e and I+C_e are invertible direct sums of
the same two- and three-dimensional blocks used in Section 6. The associated
square-zero maps N1,N2 have zero product in both orders and sum to T_3-I.
Thus two conjugates of F_a implement T_3 exactly. The Jordan bases need
2t3 coordinates, and 2t3=3S(m^6-m^3)<3U. No extra helper row is needed.
The remaining coordinates are fixed. Section 3 excludes one block, so:

> For every odd prime power m>=11, exactly two complete PR840 fused blocks
> suffice for three genuine ordinary-interchange rows when arbitrary binary
> linear encoders and their inverses are free.

This is a constructive algebraic theorem. It is not a search result or a
claim that its encoders are free on tape. The general encoder procedure in
`two_block_encoders` accepts the number of genuine rows. Its proof uses the
same image/preimage construction already executed for one genuine row.
The certificate checks the complementary two- and three-dimensional blocks
and all dimension/rank counts for nine specified prime powers with m>=11.
It does not allocate or replay the full m=11 matrix. The universal statement
follows from the displayed direct sums and the written rank inequalities.

Let V=3U now denote three genuine DATA rows. The complete typed invoice is

    B_three(V,3b) <= 6 C(V/3,b)
                     + 4 L_-1(V/3,b) + 2 L_2(V/3,b) + 4 X(V/3)
                     + G(m,S) Q(V) + P(m,S) + R(V,b).                (10)

All six children retain all spectator fields. A binary n by n encoder can
be reduced to the identity with at most n(n-1) row additions and n swaps;
each swap uses three XOR transfers. With n=V, the two encoders and their two
inverses therefore have the safe bound `G<=4V^2+8V`. Their instruction table
and its generation are included in P. Dense binary matrices and instructions
require additional storage; they are not stored in arbitrary dirty DATA.
A safe peak bill is V plus generation/table storage, transfer/counter work,
primitive scratch, routing/parking/descriptors, and the child workspace.

The child-only coefficient is 2, and its moment is `2/3^(1-c)`. For example,
the child-only moment at c=1/3 is less than one because 8<9 after cubing.
This is a favorable budget for a cheap encoder, not a certified exponent.
The current encoder implementation cannot discard its other terms.

There is a useful lower bound for its stated tape implementation. Every
individual bit-XOR adapter has rank one after subtracting I. Equation (6)
therefore requires

    G >= 3(K-S m^3)/2.                                (11)

The specified Q implementation makes a full V-cell scan for each transfer.
Its cost is at least a fixed positive multiple of

    V * 3(K-S m^3)/2.

At S=1 and fixed p, K has order `b m^5` while V=3m^6. Thus this work has
order at least `b m^11`. It cannot be absorbed in `O(V (3b)^(1-c))` for any
fixed c. This excludes the explicit unbatched scan-per-bit-transfer emission
from the required supplier time bound. It does not exclude a structured
encoder that groups many transfers in one scan or uses a different layout.
The dense gate bound is an upper bound, not a general circuit lower bound.

The remaining constructive objective is precise: give encoders for these
rank-r factors with the retained tape/row contract and a paid overhead small
enough for (10), then supply arbitrary widths, routing, hosting and recursive
admission. The abstract two-block theorem is useful evidence for that route.
It does not establish those missing interfaces. The one-genuine-row failure
in Section 6 must not be applied to this three-genuine-row construction.

## 8. Evidence and connection to kappa

The written proofs establish the quantified statements. The finite checker
checks their formulas and the new construction. It uses a six-coordinate
permutation census, a separate two-coordinate orbit census, exact binary
elimination, full symbolic VALUE execution, literal inverse execution, and
corruption controls. It does not import predecessor code or a search solver.
The checker uses no random choices. Its domains and stopping rule are fixed
in CERTIFICATE.json. It is not a proof-assistant formalization.

At the pinned base the selected PR942 assembly has complex b equal to
0.001664727258740678855772 and BIT c equal to 0.001733427039589844234749.
The complex side binds. Even a valid improvement to this BIT route would
not alone increase that selected kappa. This package changes neither
supplier, neither invoice, nor the selected record. It retains the all-size,
common-label, mutable-source, hosting, precision/tape and analytic obligations
of any later supplier adoption.
