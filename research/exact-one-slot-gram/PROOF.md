# Exact one-slot doubled centre Gram polynomial

Krzysztof Wojt, with substantial OpenAI Codex assistance. Apache-2.0.

This is a finite exact algebraic theorem about the pinned historical query,
with a computational certificate. It is not a proof-kernel development or a
native/physical implementation theorem. Ali Romman (#4958/#4720), Nick Petalas
(#5120), the doubled representation of #1719, and their retained source lineage
receive predecessor credit. Their lower-bound certificates are not inputs to
this verification.

JoyboyBrian's concurrent, released
[feasibility handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144258)
independently reports the same six Bell-label representatives, without an
upper polynomial. It was read after this derivation and is credited accordingly.

## Operator and certificate statement

Use the eight-by-112 integer matrix R and distinct labels q in F2^9 from
`INTERFACE.json`, SHA256
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
Write r_q for its columns. All labels have odd binary weight; every column has
four entries in {+1,-1}; and RR^T=56 I. The verifier checks these properties and
the exact source bytes.

With X_q the binary translation and Z_q the binary character on F2^9, let

    H_q = (X_q + Z_q)/sqrt(2),
    Gamma_q = H_q tensor H_q,
    A_lambda = (1/4) sum_q r_q r_q^T tensor Gamma_q^tensor(lambda).

The coefficient r_q r_q^T appears once. We determine A_1, which has dimension
8*512^2 = 2,097,152. Put B=4 A_1, expressed in the Bell basis below.

`CERTIFICATE.json` gives 21 monic integer polynomials in ascending coefficient
order: p_0 and p_(c,t,s), for c in {1,3,7,30,128}, t in {0,1}, s in {+1,-1}.
Define P to be their monic least common multiple over Q. The exact statement is:

**The minimal polynomial of B is P, of degree D=881.** Consequently the monic
minimal polynomial of A_1 is `4^(-D) P(4x)`. The degree, coefficient hash
and component degrees are recorded in the certificate and README. The verifier
recomputes them; neither a declared degree nor the candidate producer is trusted.

## Bell blocks, with the inherited identity made explicit

The real Pauli matrices E_(a,b)=X^b Z^a form a basis of the 512-by-512 matrix
space. Vectorization identifies conjugation by H_q with H_q tensor H_q,
because H_q is real symmetric. Since q has odd weight, X_q Z_q=-Z_q X_q.
Expanding the four terms of H_q E_(a,b) H_q gives

    E_(a,b) -> (-1)^(q.a) E_(a,b),          q.(a+b)=0;
    E_(a,b) -> E_(a+q,b+q),                q.(a+b)=1.

Indeed the two diagonal terms have coefficient
`[(-1)^(q.a)+(-1)^(q.b)]/2`, while the cross terms have coefficient
`[1+(-1)^(q.(a+b)+1)]/2`. This is #4958's Bell identity, not a new claim of
native correctness.

Thus c=a+b is invariant. On its remaining address a, write

    P_q(c)e_a = e_(a+q)                    if q.c=1,
    P_q(c)e_a = (-1)^(q.a)e_a              if q.c=0.

The full B is the direct sum of the 512 integer symmetric matrices

    B_c = sum_q r_q r_q^T tensor P_q(c),

each of dimension 4096. This is an exact change of basis, not a sample of input
columns. No floating arithmetic is needed for the represented matrices.

## Reduction from 512 labels to six representatives

For each of the 13 explicit signed coordinate permutations S in `model.py`,
the verifier maps every root column to a source root line:

    S r_q = epsilon_q r_(Lq),   epsilon_q in {+1,-1}.

It reconstructs L from a binary port basis, checks all 112 mappings and verifies
`L^T L=I` on all nine basis vectors. For the payload permutation U_L e_a=e_(La),

    U_L P_q(c) U_L^-1 = P_(Lq)(Lc).

Therefore S tensor U_L conjugates B_c to B_(Lc). Root-line signs disappear in
r_q r_q^T. The argument uses verified generators only: no enumeration or
completeness claim about the full root automorphism group is needed.

Let e=511, the all-one binary vector. All q satisfy q.e=1. The tensor Walsh
transform F exchanges X_q and Z_q, so it conjugates B_c to B_(c+e). An
unnormalized integer Walsh matrix works equally well, with inverse 1/512 times
itself. This identity is also valid modulo every odd prime.

Breadth-first closure under the 13 L maps and c -> c+e gives the following
disjoint cover. Every edge is an exact similarity just proved.

| Representative | Number of Bell labels |
|---:|---:|
| 0 | 2 |
| 1 | 224 |
| 3 | 224 |
| 7 | 16 |
| 30 | 14 |
| 128 | 32 |

The verifier recomputes this partition and checks all 512 labels. Its role is
an upper-bound completeness certificate, not a search for additional lower
minors.

## Four integer sectors for each nonzero representative

For c different from 0 and e, the two payload involutions X_c and Z_(c+e)
commute: `c.(c+e)=0`. They also commute with every P_q(c). In the translation
case q.c=1, we have q.(c+e)=0; in the diagonal case q.c=0.

Their joint eigenspaces have dimensions 128. A basis for eigenvalues
X_c=s and Z_(c+e)=(-1)^t is

    f_a = e_a + s e_(a+c),
    a < a+c,  (c+e).a=t.

There are exactly 128 representatives for each t. Together the four sectors
span the entire 512-dimensional payload. Tensoring the eight query coordinates
gives four 1024-dimensional integer symmetric matrices B_(c,t,s).

If q.c=0, P_q acts diagonally by (-1)^(q.a). Otherwise set b=a+q and choose
the smaller of b and b+c: the coefficient is 1 if b is that representative,
and s otherwise. `check_sector_interface` independently applies the original
P_q(c) to both terms of f_a and checks every compressed column. Across the
20 sectors this covers 286,720 port columns, including both signs.

For c=0, all P_q are diagonal. The 4096-dimensional B_0 is a direct sum of
512 eight-by-eight matrices

    C_a = sum_q (-1)^(q.a) r_q r_q^T.

The p_0 annihilation check evaluates the polynomial on all entries of all 512
matrices; it does not use a representative sample.

## Complete integer upper certificates

The root/label generator words that fix c induce signed coordinate permutations
commuting with B_c. They preserve both sector eigenvalues because they fix c
and e. Their restrictions are signed permutations on the quotient coordinates
(i,a). The verifier obtains such words by orbit transversals and the products
`T_(g d)^-1 g T_d`; each fixes c. Suppressing the signs when computing support
orbits is safe: every resulting edge still has a signed commuting lift.

For any polynomial p, if p(B)v=0 and U commutes with B, then p(B)Uv=0. Therefore
it is enough to check p on one coordinate vector in each such orbit. These
are exhaustive orbit covers of a basis, not probabilistic Krylov seeds.

| c | Orbits for t=0 | Orbits for t=1 |
|---:|---:|---:|
| 1 | 26 | 22 |
| 3 | 26 | 26 |
| 7 | 16 | 8 |
| 30 | 11 | 11 |
| 128 | 8 | 8 |

The s sign changes the lifted action but not these support orbits. The verifier
recomputes each partition of 1024 coordinates and evaluates the corresponding
polynomial on all its representatives by Horner's rule. All these operations
use Python arbitrary-precision integers (`numpy` object arrays). Every residual
must be identically zero. Together with the full c=0 check, this proves that
each displayed polynomial annihilates its entire designated block and that P
annihilates the full B.

The optional producer used FLINT to suggest the integer polynomials. The upper
verification does not call that producer or any matrix-minimal-polynomial
routine. Its output is accepted only through the preceding complete integer
identities.

## Matching degree lower certificates

For each of the 21 blocks, let d be the degree of its candidate polynomial p.
The verifier fixes two vectors v,w by domain-separated SHAKE256 strings,
computes 2d-1 moments `m_j=w^T B^j v` modulo the prime l=2^31-1, and forms
the d-by-d matrix `K_(i,j)=m_(i+j)`. Its determinant must be nonzero.
Gaussian elimination and modular Bareiss condensation compute the same
determinant independently. Trial division verifies the primality of l.

If a polynomial of degree below d annihilated the block in characteristic zero,
its first d powers would be linearly dependent. But the integer Hankel matrix
has nonzero determinant modulo l, hence a nonzero integer determinant. Thus its
first d Krylov vectors are independent in characteristic zero. Combined with
the exact degree-d upper polynomial, this proves that p is that block's exact
minimal polynomial. This remains true over every characteristic-zero field
extension, by the same nonzero rational minor.

The minimal polynomial of a direct sum is the monic least common multiple of
the component minimal polynomials. The similarity and complete sector covers
above therefore prove the claimed exact P for B. The verifier computes the LCM
over Z, and additionally compares its reduction with the LCM of the modular
component polynomials. The individual characteristic-zero certificates are
the reason the LCM is minimal, rather than only an upper bound.

The modular computations are exact signed-64-bit computations with explicit
reduction points. Vector entries are reduced to [0,l); four-entry root sums
and the 112-port accumulation have absolute value at most 448l<2^40.
Each moment product is <l^2<2^62 and is reduced before at most 4096 terms
are summed. Gaussian products are <l^2. In condensation, each difference
of two nonnegative products has absolute value <l^2, is reduced, and is then
multiplied by a residue <l. These bounds exclude machine-integer overflow.
Polynomial LCMs and integer Horner evaluation use arbitrary precision.

## Inverses and higher tensor widths

For A_1 the exact degree is D. If alpha I+beta A_1 is invertible and beta is
nonzero in a characteristic-zero field, its inverse has a scalar-polynomial
representative of degree exactly D-1. The lower bound follows from
`((alpha+beta x)q(x)-1)(A_1)=0`. For attainment, let M be the monic minimal
polynomial of A_1 and r=-alpha/beta. Invertibility gives M(r)!=0, and

    q(x) = [1-M(x)/M(r)] / (alpha+beta x)

is a polynomial of degree D-1 giving the inverse. This is an algebraic degree
statement, not a circuit or native-call invoice.

The Bell vector with a=b=0 is fixed by every Gamma_q. As in #4958/#5120,
tensoring the whole one-slot space with this vector in every additional slot
embeds A_1 as a restriction of A_lambda for every positive lambda. Hence their
minimal-polynomial degrees are at least D, and affine-inverse polynomial
degrees are at least D-1 when defined. **No upper annihilator for lambda>1 is
proved here.** The root coefficient remains applied once in this embedding.

Physical source access, general ADD circuits, rational/matrix-valued decoders,
dirty restoration, owned storage, routing, rounded precision, fixed tape,
compiler closure, complete supplier admission and outer multiplication claims
are not supplied by this theorem. No cost previously marked unknown is set to
zero, and no new kappa or selected-frontier change is claimed.
