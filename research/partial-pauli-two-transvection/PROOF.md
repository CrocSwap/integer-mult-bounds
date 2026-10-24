# Exact low-length completion of a partial Pauli contract

This contribution was produced by Nick Petalas. Apache-2.0.

The claim is a scoped algebraic proof. Its new repository application is an
exact low-length completion decision for the partial contracts in
[JoyboyBrian's PR5051](https://github.com/CrocSwap/integer-mult-bounds/pull/5051),
head `0960807a68ff46acbe6510c8867912ef2324ee71`. That predecessor supplies the
compatibility problem and a general construction, rather than this optimum.
Binary symplectic transvections and residual bilinear forms are classical.
No literature-priority claim is made. No predecessor verifier is imported or run.

## Model and statement

Let V be a finite-dimensional nondegenerate symplectic space over F2, with
alternating pairing omega. Let U be any subspace and let h:U -> V be an
injective linear isometry. Its displacement is d(u)=h(u)+u, its displacement
space is D=d(U), and r=dim D. A transvection with nonzero axis a is

    T_a(v) = v + omega(v,a) a.

Let ell(h) be the least number of such transvections in a symplectic map
whose restriction to U equals h. Transvections may act on the full given V;
no new dimensions are adjoined. This is an unsigned label-word length.

The following bilinear form on D is well defined:

    b(d(u),d(v)) = omega(u,d(v)).                         (1)

Here "alternating" means b(x,x)=0 for every x, not merely that the ambient
symplectic pairing is alternating. The exact cutoff is:

| Displacement data | Conclusion |
|---|---|
| r=0 | ell(h)=0 |
| r=1 and b is nonzero | ell(h)=1 |
| r=1 and b=0 | ell(h)=2 |
| r=2 and b is nonsingular and nonalternating | ell(h)=2 |
| r=2 and b is nonsingular and alternating | ell(h)=3 |
| r=2 and b is singular | ell(h)>=3 |
| r>2 | ell(h)>=r |

In particular, the first four rows are necessary and sufficient for ell(h)<=2.
This statement classifies every partial isometry at that cutoff. The last two
rows deliberately give only lower bounds, not an infeasibility conclusion or
a classification of every longer word. The executable API uses `minimum=None`
for those rows.

For a compatible signed Hermitian-Pauli contract, use the same tariff when
arbitrary Pauli conjugations are free and each literal quarter-turn is charged
one unit. Signs do not change this tariff. This is a declared formal alphabet;
turn count is not Gaussian paid rank, recursive-child rank or physical cost.

## The induced form and the rank lower bound

If z is in ker d, then h(z)=z. Isometry gives

    omega(z,d(v)) = omega(h(z),h(v)) + omega(z,v) = 0.

Changing the preimage u of d(u) in (1) therefore changes nothing. Bilinearity
and well-definedness in the other argument are immediate. Expanding the
isometry equation for u,v gives

    b(x,y) + b(y,x) = omega(x,y),  for x,y in D.          (2)

Each T_a-I has rank one on V. The identity AB-I=A(B-I)+(A-I) implies
rank(S-I)<=t for a product S of t transvections. Since (S-I)|U=d for an
extension, ell(h)>=r. In particular only r<=2 can pass the two-turn cutoff.

## Rank-one displacement

Write D=<d0> and d(u)=alpha(u)d0, with alpha a nonzero functional on U.
Equation (1) says

    omega(u,d0) = alpha(u)b(d0,d0).

If b(d0,d0)=1, T_d0 agrees with h, and the rank bound proves ell(h)=1.
Conversely, any single turn extending a nonidentity h must have axis d0,
so this condition is necessary for length one.

If b=0, then U is orthogonal to d0. Choose a in V satisfying

    omega(u,a)=alpha(u) for every u in U,
    omega(d0,a)=0.                                     (3)

This is a consistent linear functional on U+<d0>. Indeed, if d0 belongs
to U, injectivity of h forces alpha(d0)=0: otherwise h(d0)=0. If d0 is
outside U there is no additional relation. Nondegeneracy of omega supplies a
representing a, by solving a linear system. Since alpha is nonzero and
omega(U,d0)=0, a is neither zero nor d0. Thus a and a+d0 are distinct
nonzero orthogonal axes. Their commuting turns give, for u in U,

    T_(a+d0) T_a(u) = u + alpha(u)d0 = h(u).

The one-turn exclusion proves ell(h)=2. No clean ancilla or enlarged V was used.

## Exactly two turns at rank two

First consider two distinct nonzero axes a,c. They are linearly independent
over F2. Put gamma=omega(a,c). The displacement of S=T_c T_a is

    (S-I)v = omega(v,a)a + (omega(v,c)+gamma omega(v,a))c. (4)

Nondegeneracy makes the two functionals omega(-,a), omega(-,c) independent.
Consequently im(S-I)=<a,c> and rank(S-I)=2. In the ordered basis (a,c),
the residual form defined as in (1), now on all of V, has matrix

    [1 gamma]
    [0   1  ].                                         (5)

This follows directly by substituting (4) into b((S-I)v,a)=omega(v,a)
and b((S-I)v,c)=omega(v,c). If S extends a partial map of displacement
rank two, its full displacement space equals D, so its residual form is
the form already fixed by the partial contract. Hence b must be nonsingular
and nonalternating. Equal axes instead cancel and cannot have rank two.

Conversely suppose r=2 and b is nonsingular and nonalternating. Choose
a in D with b(a,a)=1. The kernel of the nonzero functional x -> b(x,a)
is a line different from <a>; choose its nonzero element c. In this basis
b(c,a)=0, and nonsingularity forces b(c,c)=1. Equation (2) gives
b(a,c)=omega(a,c)=gamma. Thus b has exactly the form (5).

For d(u)=lambda a+mu c, equation (1) now gives

    omega(u,a)=lambda,
    omega(u,c)=gamma lambda+mu.

Formula (4) therefore equals d(u). The two turns extend h, and rank two
excludes every shorter word. This also proves the singular-form obstruction.
All choices require only linear algebra in the two-dimensional D.

## The alternating three-turn boundary

For a nonsingular alternating form on a binary two-space, every basis (a,c)
has b(a,c)=b(c,a)=1 and zero diagonal. Equation (2) says omega(a,c)=0.
Equation (1) gives

    d(u)=omega(u,c)a+omega(u,a)c.

The three distinct nonzero axes a,c,a+c are pairwise orthogonal. Multiplying
their commuting turns gives on all of V

    T_(a+c) T_c T_a(v) = v + omega(v,c)a + omega(v,a)c.

This extends h. The preceding two-turn criterion excludes shorter words,
so ell(h)=3. For an explicit full contract in any dimension at least four,
take a,c independent isotropic basis vectors, fix them and every other
standard basis vector except their duals, and send

    f_a -> f_a+c,   f_c -> f_c+a.

The new criterion proves its exact three-turn cost directly. This example is
a boundary witness for the cutoff, not an additional supplier construction.

## Signed Hermitian Paulis

Write a label as (x,z), and H_v=i^(popcount(x & z)) X^x Z^z. It is Hermitian
and squares to I. The literal unitary

    C_a = (I-i H_a)/(1-i)

has Gaussian-dyadic entries and conjugates labels by T_a. Direct multiplication
gives C_a H_v C_a^-1=H_v when the labels commute, and -i H_a H_v otherwise.
Thus each attaining label word above has an actual Clifford lift.

For independent source generators, let U0 be that lift. Its output signs may
differ from the desired signs. The differences specify a functional on h(U).
Extend this functional to V and represent it by omega(k,-). Conjugating last
by H_k supplies exactly those sign differences. For dependent equations,
compatibility of the actual central product phases is a premise, as stated in
PR5051, so the same correction handles the whole contract. Any word with
Pauli conjugations inserted has the same unsigned transvection label word;
therefore free sign corrections cannot beat the lower bounds.

Conjugation equations leave a global scalar phase unspecified. Equality with
an independently supplied absolute-phase target still needs its own anchor.
Tensorizing an actual chosen word is valid, but no tensorized paid-rank or
precision invoice follows from this turn-count theorem.

## Evidence and scope

The proof is uniform in dim V. The finite census independently enumerates
literal binary symplectic matrices and a complete transvection Cayley graph
through dimension four. For every source subspace it groups full maps by their
restricted target images, takes the minimum literal word length, and compares
the new classifier and every returned witness. Complete sign choices are checked
only for independent Hermitian generators in the rows where a sharp word is
returned. The finite counts and file-bound receipt come from `verify.py`.

This is not an audit of PR5051 or the native compiler. The predecessor's proof
and executable are not dependencies. The all-size claim rests on this written
argument, with classical transvection structure credited. A general transvection
reference is Brown and Humphries, [Orbits under symplectic transvections](https://groupoids.org.uk/pdffiles/brown-humphries1.pdf),
whose introduction also distinguishes generation from individual word length.
No external theorem from that paper is needed in the cutoff proof above.

No native cost optimum, actual profitable caller, compiler or supplier admission,
physical movement, dirty-owner schedule, precision, storage, stock, complete
multiplication theorem or new kappa is established. Independent human and formal
proof-kernel review are unclaimed.
