# Four widths decide every affine-quadratic native identity

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

This is a complete algebraic result for the class below. It does not prove a
physical native implementation, a cost saving, or a multiplication exponent.
The group-theoretic and Fourier tools used in the proof are classical.

## 1. Exact class and result

Fix n>=1. Let V have basis e_x, x in F_2^n. The group G_n consists of the maps

    U(A,t,c,a,b) e_x = i^q(x) e_(Ax+t),
    q(x) = c + sum_j a_j x_j + 2 sum_(j<k) b_jk x_j x_k  (mod 4),

where A is invertible over F_2, t is binary, c and each a_j are in Z/4,
and each b_jk is in Z/2. The phase is evaluated at the input. This is exactly
the affine/quadratic Gaussian monomial grammar used by the pinned [PR #2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250)
recipe functions. It excludes Hadamard gates and other nonmonomial operators.

The recipe is unique. Its affine part is determined by its action on 0 and
the n unit vectors. Its phase coefficients are determined by q(0), q(e_j),
and q(e_j+e_k). Composition and inversion preserve this form: a Boolean
affine form is a quadratic polynomial modulo four, and twice a product of
two Boolean affine forms is quadratic modulo four. The two implementations
use these two different ways to compute the coefficients.

Write rho_f(U)=U^(tensor f). The tensor power acts on payloads; it does not
tensorize a scalar combination of operators. All external coefficients in
this proof remain fixed scalars. Let

    P = sum_(U in G_n) alpha_U [U] in C[G_n].

Only finitely many coefficients need be stored. Put F=2n+4.

**Theorem.** The following statements are equivalent:

1. Every coefficient alpha_U is zero.
2. rho_f(P)=0 for every positive integer f.
3. rho_f(P)=0 at the four widths F,F+1,F+2,F+3.

If P is nonzero, the proof constructs f in this four-width window and two
basis tuples x,y in (F_2^n)^f such that the (y,x) entry of rho_f(P) is nonzero.
The two tuples need O(n^2) bits. This is a compressed basis address, not a
polynomial bound on the dimension 2^(nf) of the tensor space.

For Gaussian rational coefficients and s stored nonzero group terms, the
witness construction uses O(s n^2) exact Gaussian scalar operations for its
Fourier choices, plus polynomial binary linear algebra and bit operations.
This count starts from the expanded residual. Expansion of a register circuit
can require exponentially many terms. There is no polynomial-time claim for
the complete circuit checker.

The theorem applies entry by entry to a complete matrix over C[G_n]. Thus it
applies to scalar register programs using ADD, SCALE, SWAP, unary APPLY and
`v_dst += alpha U v_src`, including a self query. The compiler starts every
role as a separate arbitrary input and checks every returned role. A reference
program must state any discarded or zero output. A borrowed role is restored
only when the reference contains its identity endpoint.

The four-width equivalence requires the same recipes, scalar coefficients
and program at all four widths. It does not apply to an arbitrary program
which changes with f. The per-residue statement in Section 5 is more general.

## 2. A short tuple realizes every phase character

The diagonal phase subgroup D has coefficient group

    (Z/4)^(n+1) x (Z/2)^(n(n-1)/2).

Write a character of D as (r,u,v), with r,u_j in Z/4 and v_jk in Z/2. Its
value on a phase polynomial q is

    chi(q) = i^(r c + sum_j u_j a_j + 2 sum_(j<k) v_jk b_jk).

We construct an ordered tuple X of points which has affine span F_2^n and
has exactly these phase statistics:

    |X| = r (mod 4),
    sum_(x in X) x_j = u_j (mod 4),
    sum_(x in X) x_j x_k = v_jk (mod 2), j<k.

Start X with 0,e_1,...,e_n. This fixes the affine span. Form the symmetric
binary matrix M with diagonal u_j mod 2 and off-diagonal entries v_jk.
The starting tuple has Gram matrix I, so factor M+I as YY^T with at most
n+1 columns. Append those binary columns as points of X.

For completeness, such a factor always exists. Symmetric elimination splits
a binary form into nonsingular one-dimensional blocks, hyperbolic pairs,
and its radical. If there are a one-dimensional blocks and b hyperbolic
pairs, embed the first blocks on a separate orthonormal coordinate set.
Embed the alternating 2b-dimensional part in the even-weight subspace of
F_2^(2b+1). That subspace is nonsingular: its orthogonal complement is the
all-ones vector, which has odd weight and is outside the subspace. A
symplectic basis gives the required hyperbolic pairs. Undo the original
congruence. The number of columns is a+2b+1 if b>0, or a otherwise, hence
at most rank(M+I)+1<=n+1. This is a sufficient form of the classical binary
symmetric factorization result; no optimal factor width is claimed here.

The current Gram matrix is now M. Let w_j be the current coordinate count
modulo four. Then u_j-w_j is even. Define the single binary vector

    z_j = (u_j-w_j)/2 (mod 2).

Append two copies of z if z is nonzero. They correct every coordinate count
modulo four at once. They change no pair count modulo two. This two-copy
correction is necessary; Gram parity alone does not determine a Gaussian
phase character.

The tuple now has length at most

    (n+1) + (n+1) + 2 = 2n+4 = F.

For any prescribed f>=F with f=r mod 4, append zero points until its length
is f. Zero points change neither coordinate nor pair counts. Their count
sets the constant-phase character. In particular there is such an f among
F,F+1,F+2,F+3. The tuple still contains 0 and every unit vector.

This construction is uniform in n and in the character. No group enumeration
or tensor matrix is needed.

## 3. Separate an arbitrary nonzero residual

Choose a nonzero affine bucket (A,t) of P. Its coefficients are a nonzero
function alpha(q) on D. Finite Fourier inversion gives a character chi with

    S = sum_q alpha(q) chi(q) != 0.

Construct X for chi by Section 2, and put Y=(Ax+t : x in X), in the same
order. A term with a different affine map cannot send X to Y, because X
contains an affine basis. A term in the chosen bucket contributes exactly
alpha(q) i^(sum_(x in X) q(x))=alpha(q) chi(q). Therefore

    <e_Y, rho_f(P) e_X> = S != 0.

This proves the theorem. It also proves the bound on the witness encoding.
The proof does not assume that independent free operators represent the
native symbols; it uses their actual affine and phase relations.

The executable finds chi without enumerating D or its dual. Regard alpha as
a sparse table on the coefficient coordinates of D. For the first coordinate,
try each of its two or four characters, collect terms on the remaining
coordinates, and retain a nonzero table. At least one choice is nonzero:
otherwise the invertible Fourier matrix for that coordinate would imply that
the original table was zero. Repeat. The final table is the single nonzero
number S. Each stage has at most s terms and at most four trials. There are
1+n+n(n-1)/2 stages. This proves the stated exact scalar-operation bound.

## 4. Four widths are necessary; the widths must grow with n

For each residue r modulo four consider the central phase projector

    C_r = sum_(c=0..3) i^(-r c) [i^c I].

At width f it is 4I if f=r mod 4, and zero otherwise. Any proposed test set
that misses one residue admits a false all-width identity. Thus no set of
three widths can replace the four tests for this full group. The theorem is
optimal in the number of widths, not in the value of the cutoff F.

A second family shows that a fixed small-width test is insufficient even
when scalar phases are treated correctly. Let S_j have phase x_j and let
Z_j=S_j^2. Let CZ_jk have phase 2x_jx_k. Form the matrix polynomial

    P_n = product_j ((I-i S_j)(I-Z_j)/4)
          product_(j<k) ((I+CZ_jk)/2),

with all products interpreted termwise at width f. These diagonal operators
commute. On a basis tuple X, the first factors select coordinate counts
equal to one modulo four, and the second factors select even pair counts.
If the entry is nonzero, the n-by-f binary matrix with columns X satisfies
XX^T=I_n. Hence f>=n. Thus rho_f(P_n)=0 at every positive f<n.
At f=n, the tuple (e_1,...,e_n) has eigenvalue one. Zero padding gives a
witness at any larger width too.

The program has O(n^2) instructions, but its expanded phase support can be
exponential. The nine-axis example is invisible at all widths 1 through 8.
The independent checker executes its basis witness without expanding that
support. This example is an algebraic diagnostic; it is not a paid native
supplier or a proof that its self queries have an admitted physical cost.

## 5. Exact stabilization within a phase residue

Fix r in Z/4. Combine global phases in each affine/nonconstant-phase class:

    beta_(A,t,a,b) = sum_(c=0..3) alpha_(A,t,c,a,b) i^(r c).

For every f>=F with f=r mod 4, rho_f(P)=0 if and only if every beta is zero.
The forward implication follows by applying the Fourier argument to (a,b)
only and using Section 2 with the prescribed constant character r. The
reverse implication follows directly by collecting the same tensor maps.

Thus the kernel of tensor evaluation, after the scalar relation [iI]=i^r,
has stabilized by F. This is a quantitative replacement, for this monomial
subgroup, of the older general finite-alphabet separation bound
[f>=|G/Z|-1](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/two-full-retained-helper-ceiling/science/PROOF.md). It does not assert this linear cutoff for the full Clifford group.
For n=9 the stabilized threshold is 22; the four all-width tests are 22..25.
For n=17 they are 38..41. These are sufficient bounds, not minimum thresholds.

This statement permits any scalar coefficients at one specified f. To infer
an identity for all f from four tests, the single fixed P premise in Section 1
must still hold.

## 6. A computational boundary even for reversible dirty programs

Consider five-role programs which use only the commuting sign generators
Z_j e_x=(-1)^x_j e_x, rational ADD and QUERY between distinct roles, unary
APPLY(Z_j), and SWAP. Every instruction is invertible. All five roles start
with arbitrary independent inputs. With n unbounded and rational coefficients
in ordinary binary notation, equality of complete endpoints for this class
is coNP-complete. No clean scratch or zero-return role is needed.

For membership, every tensor basis tuple supplies only the n signs
z_j=(-1)^(sum x_j). All sign tuples already occur at width one. For a chosen
sign tuple, the complete five-by-five scalar endpoint can be evaluated in
polynomial time and exact bit complexity. The product of all instruction
denominators is a common denominator for the final entries. For L instructions,
the numerator bit lengths are bounded by the total coefficient bit length
plus O(L log 5). A sign tuple and a differing matrix entry therefore
certify inequality. This argument concerns the unbounded mathematical class;
the implementation has the separate finite input limits in README.md.

For hardness, we use Barrington's classical width-five permutation program
construction. The following explicit version is in `reversible_cnf.py`.
Represent a permutation by its five images, and let composition p q mean
apply q first. Set

    A = (1,2,3,4,0),
    B = (1,3,0,4,2),
    C = B^-1 A^-1 B A = (4,3,1,0,2).

Each of A, B and C is a five-cycle. A Boolean literal gives a single branch
instruction which is the identity when the literal is false and a chosen
five-cycle when it is true. Negation inverts the word and then appends the
target cycle. For an AND, choose a permutation F with F C F^-1 equal to
the target cycle. Compile the two children to F A F^-1 and F B F^-1.
The chronological word P,Q,P^-1,Q^-1 is identity if either child is false,
and the target cycle if both are true. OR follows by De Morgan's law.
These rules prove the Boolean program property by induction. The conjugator
exists because both C and the target are five-cycles: map C^k(0) to the
target's k-th iterate of 0.

A clause with at most three literals needs at most 25 branch instructions.
Combine m clauses with a balanced AND tree. Each leaf is copied at most
2^ceil(log2(m)) times, so the word has at most 50*max(1,m)^2 instructions.
An empty conjunction is true and an empty clause is false. The resulting
word is A if the three-literal CNF formula is true, and identity otherwise.

It remains to implement each branch with the permitted dirty operations.
A permutation of five roles needs at most four swaps. For a branch which
selects permutation a at bit zero and b at bit one, first perform a. Then
perform the swaps for b a^-1, each controlled by the native sign Z_j. A
controlled swap on arbitrary dirty inputs x,y is the five-step word

    x -= y
    y += x/2
    y -= Z_j x/2
    x  = Z_j x
    x += y

On sign +1 this is identity. On sign -1 it swaps x and y. Direct substitution
proves both claims for all x,y. Each step is a distinct-role shear or an
invertible unary map. Thus each branch needs at most 4+4*5=24 instructions,
and the complete reduction needs at most 1200*max(1,m)^2 instructions. Its
only nonintegral coefficients are 1/2 and -1/2.

Every truth assignment occurs as one tensor basis address at width one.
On that address the full five-role endpoint is the identity if the formula
is false and the nonidentity permutation A if it is true. The program equals
the empty reference on all dirty inputs at all positive widths exactly when
the CNF formula is unsatisfiable. This is a polynomial reduction from
three-literal CNF unsatisfiability and proves coNP-hardness.

The construction is an algebraic statement. It does not assign physical
cost to a native query or admit a paid supplier. Barrington retains credit
for the permutation program theorem; the package makes its use in this exact
native dirty grammar explicit. The checker reports a resource limit as no
decision, not as identity. No general polynomial runtime bound is claimed.

## 7. Source binding and verification boundary

The retained source files and hashes are in [SOURCES.json](SOURCES.json)
and [SOURCE-PINS.json](SOURCE-PINS.json). [PR #2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250) evaluates
the same input phase, affine matrix rows and offset. Its quadratic rows use
only the strict upper entries; the adapter preserves that convention. Its
tensor phase includes f times the constant phase. The source check covers
all 512 one-column addresses of the retained nine-axis event8814 recipe,
its inverse and a native Pauli-conjugation identity, plus tensor phase probes.

For the actual recipe G=(A,t,q), take Z_v e_x=(-1)^(v.x)e_x. Then

    G Z_v G^-1 = (-1)^(v.A^-1.t) Z_(A^-T.v).

The package chooses v so that the constant sign is negative. Its complete
two-role circuit adds the conjugated source to a dirty target, restores the
source, and subtracts the stated native right side. The checker proves this
endpoint is identity at all positive widths. Removing the constant phase
from the right side passes all even widths but fails at the generated odd
width witness. This is an application of actual native relations, not a
new discovery of Pauli conjugation.

The recipe fixture was supplied by the predecessor packet investigation.
This package authenticates those bytes and the scalar recipe convention;
it does not reproduce the full dispatcher-to-chart chain, production packet
order, recursive child, fixed-tape implementation, precision, hosting or
complete paid invoice. The full multiplication theorem and selected kappa
are unchanged.

The certificate checker imports neither the producer nor its group algebra.
For a positive claim it rebuilds the complete endpoint with direct Boolean
polynomial substitution, whereas the producer interpolates coefficients at
0, unit vectors and pairs. For a negative claim it runs the original program
on the declared tensor basis input, with literal affine maps, phases and
inverse actions. Both share exact Gaussian rational arithmetic, Python and
the declared instruction semantics. This is separate implementation evidence,
not an independent human review or a proof-assistant kernel.

## 8. Prior work and open next questions

Binary symmetric factorization is classical; see Abraham Lempel,
[Matrix Factorization over GF(2) and Trace-Orthogonal Bases of GF(2^n), 1975](https://doi.org/10.1137/0204014).
The proof above includes the sufficient factorization argument it uses.
Finite Fourier inversion is classical. General tensor generation by a
faithful finite-group representation is the Burnside-Brauer theorem; see
Benjamin Steinberg's [account and extension, 2014](https://arxiv.org/abs/1409.7632).
The coNP statement uses the classical NP-completeness of Boolean SAT; see
Stephen Cook's [The Complexity of Theorem-Proving Procedures, 1971](https://www.cs.toronto.edu/~sacook/homepage/1971.pdf).
Its reversible reduction uses David A. Mix Barrington's
[Bounded-Width Polynomial-Size Branching Programs Recognize Exactly Those Languages in NC1, 1989](https://people.cs.umass.edu/~barring/publications/bwbp.pdf),
[journal record](https://doi.org/10.1016/0022-0000(89)90037-8).
Section 6 gives the permutation construction and its exact dirty-register
implementation explicitly.

The [binary-stream faithfulness proof](https://github.com/CrocSwap/integer-mult-bounds/blob/7c472563474e60185e6ca101a17622133d047e56/research/binary-stream-faithfulness/PROOF.md)
prepared for @ywz65 in
[PR #2599](https://github.com/CrocSwap/integer-mult-bounds/pull/2599)
already uses the affine basis 0,e_1,...,e_n to recover
complete dirty-register coefficients for the binary permutation action over
F_2, with a sharp width boundary for that action. That result keeps its
credit. The Gaussian phase subgroup here has additional Fourier characters
and four central residues. An affine basis alone does not separate them.

Jose Manuel (@jmbarrancoml) also constructs selected phase-character sectors
at a common tensor length in
[Discussion #2106](https://github.com/CrocSwap/integer-mult-bounds/discussions/2106).
That construction uses pair vectors and repeated unit vectors for a specified
three-axis invariant sector. This package does not claim phase-character
realization as a new idea. Sections 2 and 3 give a linear width bound for every
character, preserve an affine basis, and separate every native residual.

The repository's [PR #4928](https://github.com/CrocSwap/integer-mult-bounds/pull/4928) and [PR #4978](https://github.com/CrocSwap/integer-mult-bounds/pull/4978) already use finite-alphabet tensor
separation, including the projective |G/Z|-1 bound. Chris R (@Clear1nsight) and
the retained source authors keep that credit. [PR #5235](https://github.com/CrocSwap/integer-mult-bounds/pull/5235) by zxv and [PR #5262](https://github.com/CrocSwap/integer-mult-bounds/pull/5262) by
Krzysztof Wójt (@krzysztofwojt) supply the related complete dirty-register certificate
interfaces for independent operators and true named inverses. Those methods
do not impose the native finite-order and phase relations used here.
Jose Manuel (@jmbarrancoml) supplied [PR #2250](https://github.com/CrocSwap/integer-mult-bounds/pull/2250)'s recipe implementation, with
Douglas Colkitt's compact construction and the retained notices. JoyboyBrian
and Cinna Davis supply the event fixture/caller lineage recorded in the source
manifest. No general Fourier, Gram, tensor generation, Pauli conjugation or
PIT theorem is claimed as new.

The contribution is the explicit four-width native criterion, constructive
short basis witness, residue stabilization bound, executable complete-endpoint
interface, matching test-count and growing-width obstructions, and an explicit
reversible complexity reduction for this exact source grammar. No global
literature priority is claimed.

Open next questions:

1. Determine the least stabilized width for G_n. The projector lower bound
   and F=2n+4 leave a gap. Start with exact small-n phase-character realizations
   with an affine-span constraint; a minimum for one character is not the
   complete representation threshold.
2. Extend a quantitative witness theorem to nonmonomial native Cliffords.
   The affine-bucket isolation argument does not apply to Hadamard operators.
   Start with a specified finite Clifford group and its projective character
   sectors. Keep that hypothesis separate from this proof.
3. Add a source-bound adapter for another complete monomial register word.
   Preserve every dirty input, global phase, source order and scalar placement.
   Physical realization and its full invoice must still be supplied separately.
