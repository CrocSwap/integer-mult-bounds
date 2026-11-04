# Exact restrictions on short full-query callers

These are scoped algebraic results. They do not give a new kappa. They
apply to arbitrary scalar frames, including frames that do not commute.
The scalar field is commutative. Sections 1 and 2 require characteristic
other than two. The six- and eight-field computations in Section 4 use
characteristic zero.

## 1. Contract and complete query normal form

There are n independent main fields and n+1 chronological rank-one query
calls. There is no additional main work field. A full call has the form

    D_i(z) (I + (S-1) R_i),    D_i(z) = I + (z-1) P_i,

where S is a central involution, z is a formal forward stage,
P_i is a rank-two projector, R_i is rank one and square-zero, and
P_i R_i = R_i P_i = R_i. A thin call has P_i=0 and the same query form.
Constant invertible ordinary maps can occur at every gap. Move these maps
to the final boundary by conjugation. Remove their total product there.
This gives the displayed form and normalizes the plus-character endpoint
at z=1 to I. No stage or query rank changes under this operation.

The required query condition is

    W_minus(z) = -W_plus(z).

This condition is weaker than a complete independent Gaussian endpoint.
It permits any remaining invertible stage matrix W_plus. Thus failure of
this condition also excludes every specified pure central-query target.

At z=1 put T_i=I-2R_i. The condition gives T_n ... T_0=-I. Necessarily n
is even, by determinants. Factor R_i=u_i v_i and let U contain the columns
u_i, V contain the rows v_i. Set G=VU and let L be its strict lower part.
Direct chronological expansion gives

    T_n ... T_0 = I - 2 U (I+2L)^(-1) V.

Thus U(I+2L)^(-1)V=I_n. Both U and V have rank n. The matrix
(I+2L)^(-1)VU is a rank-n projector on an (n+1)-dimensional space.
Consequently

    Z = I+2L-G

has rank one. Its diagonal is one, since v_i u_i=0. Write
Z_ij=a_i/a_j, where every a_i is nonzero. Rescale u_i by a_i and v_i by
a_i^(-1). This does not change R_i. It makes

    v_i u_j = 1 if i>j, -1 if i<j, and 0 if i=j.

The leading even n-by-n skew matrix in this formula is invertible. For
example, subtract consecutive row equations in a vector in its kernel;
successive coordinates alternate, and an end equation makes them zero.
We can therefore use u_0,...,u_(n-1) as a basis. The complete normal form is

    u_i = e_i                    (0 <= i < n),
    u_n = (-1,1,-1,1,...),
    (v_i)_j = sign(i-j)           (0 <= j < n).

This is a classification, not a restriction to one sampled query frame.
Every shortest query tuple under the stated contract is conjugate to it.
The coefficient field can be larger than the rationals.

## 2. Endpoint cancellation and the complete projector chart

The projectors at sites 0 and n do not enter the query test. Each commutes
with its own T_i. Multiply the endpoint equality by D_n^(-1) on the left
and D_0^(-1) on the right. Over the rational function field in z it becomes

    T_n D_(n-1) T_(n-1) ... D_1 T_1 T_0
      = - D_(n-1) ... D_1.

Put w=z-1. The coefficient of w is linear in the interior projectors;
the coefficient of w^2 is quadratic. Higher coefficients remain necessary
for a construction, but need not be checked after a contradiction.

For an interior full site i, choose a vector h with v_i h=1. Complete
[u_i,h] by vectors in ker(v_i). In this basis R_i=E_01. Every compatible
rank-two projector, and no other one, has the form

    P_i = B_i [[1,c_i,b_i],
               [0,1,  0 ],
               [0,a_i,0 ]] B_i^(-1),
    c_i + b_i a_i = 0.

Here a_i is a column of length n-2 and b_i is a row of that length.
To prove completeness, PR=RP=R fixes the first column and second row.
The remaining bottom-right block of an idempotent is an idempotent.
The total rank is two plus its rank, so that block is zero. The only
remaining idempotence equation is c_i+b_i a_i=0. Conversely the displayed
equation makes P_i idempotent, compatible with R_i, and rank two.

The replay takes h=e_p/(v_i)_p at the first nonzero coordinate p. The other
columns of B_i are e_j-(v_i)_j h, in increasing j, except j=i,p.
This fixes all chart and coefficient conventions.

## 3. Five full calls on four fields: a short identity for one

For sites 1,2,3 write the variables in the order

    (a10,a11,b10,b11,c1, a20,a21,b20,b21,c2,
     a30,a31,b30,b31,c3).

All first-coefficient equations have the following complete solution,
where a=a30, u=b21, b=b30 and c=c3:

    (a+2, b, b+1, 2-c, -a-2,
     a+u-c+2, -b-c, a+b+2, u, -a+c-2,
     a, b+1, b, -c, c).

Its dimension is four. The replay checks that the coefficient matrix has
rank eleven using only divisions by powers of two, and that this displayed
four-parameter solution satisfies every row. These facts prove completeness
over every characteristic other than two.

The first and third projector equations, followed by entries (0,0), (0,2)
and (2,0) of the second endpoint coefficient, give the five equations below.
Indices here start at zero. Each expression must be zero.

    g0  = b(a-c+4),
    g2  = b(a-c),
    g3  = 2a^2-2ab+4a-4ub+6bc-4b+2c^2+2,
    g5  = 4a^2+2ab+12a-4ub+2bc+8b+10,
    g11 = -4ab-2ub+6bc-2b+2c^2.

Define the following combinations of these zero equations:

    B  = (g0-g2)/4 = b,
    C2 = g11/2 - B(-2a-u+3c-1) = c^2,
    F  = g3/2 - C2 - B(-a-2u+3c-2) = (a+1)^2,
    A  = g5/2 - 2F - B(a-2u+c+4) = 2a+3.

But 4F-(2a+1)A=1. This contradicts their vanishing. The proof uses only
powers of two as denominators. It excludes five full calls on four fields
over every field of characteristic other than two. It does not require a
choice of target stage powers. In particular it excludes the proposed
(2,2,3,3) target.

The verifier builds the five equations from the original matrices. It
does not merely check an independently typed copy of the equations.
A changed coefficient breaks the identity. Another control uses actual
projectors with a=-1 and u=b=c=0: all first-coefficient equations pass,
but the second coefficient fails. Thus the first-order test alone is not
a valid acceptance test.

## 4. Six and eight fields, and exact thin-query counts

The same complete charts give computational algebraic proofs over every
characteristic-zero field. The replay does the following exact operations:

1. Rebuild the canonical R_i and every affine P_i from Sections 1 and 2.
2. Multiply the original chronological words through degree two in w.
3. Solve the linear coefficient equations by rational row reduction.
4. Combine all projector quadratics with every second-coefficient entry.
5. Row-reduce their polynomial coefficient vectors, with degree-two
   monomials before affine monomials. Each new affine row is a rational
   linear combination of necessary equations.
6. Solve those affine consequences and substitute them in every equation.
   Repeat until a nonzero constant is obtained or no new affine row exists.

Every substitution describes the complete solution set of a linear system.
No random point, small numerical residual, or bounded coefficient domain is
used. A nonzero constant proves that the original equations have no solution,
including over the complex numbers. This is an exact finite algebraic proof
for the stated field counts. It is not a theorem for all n.

The complete tested domains are:

| Main fields n | Queries n+1 | Interior thin-site subsets tested | Necessary minimum thin calls | Only surviving subset at that minimum |
| --- | --- | --- | --- | --- |
| 4 | 5 | all subsets of size 0 or 1: 4 cases | 1 | {2} |
| 6 | 7 | all subsets of size at most 2: 16 cases | 2 | {2,4} |
| 8 | 9 | all subsets of size at most 3: 64 cases | 3 | {2,4,6} |

Sites are indexed 0 through n. Thin calls at an endpoint cannot rescue a
failed interior test, because endpoint projectors cancel. Hence the lower
bounds count thin calls anywhere in the complete word. At the minimum,
both endpoints must be full, and the stated interior subset is unique.

The total is 84 exhaustive symbolic domains, not 84 sampled tuples. The
all-full cases start with 15,45,91 affine variables and leave 4,16,36 free
variables after the first coefficient, respectively. The complete rational
outcomes and elimination counts are in RESULT.json.

For each surviving alternating subset the replay reconstructs constant
rational projectors and checks every coefficient of the full query word.
These are positive controls for the query condition. They do not prove
independent Gaussian targets. With the natural endpoint choices P_0=P_1
and P_n=P_(n-1), put A=W_plus(2). The replay checks that
N=(A-2I)(A-4I) is nonzero but N^n=0. Hence A is not diagonalizable:
a polynomial in a diagonalizable matrix cannot be both nonzero and
nilpotent. The stage word cannot be a constant conjugate of diagonal
monomials. Different endpoint projectors are not excluded by this control.

Discovery used SymPy with conjugated tail projectors and a different
parameter elimination order. The registered replay uses a separate
standard-library implementation, direct chronological multiplication,
sparse rational polynomials, and no discovery output. Both confirm the
all-full exclusions. They are two implementations by the same author and
AI session, not independent human review.

## 5. A signed extreme-degree bound for any coupled width

This separate result does not require the query normal form. Work in any
finite-dimensional space over a field of characteristic other than two.
For an idempotent K write D_K(z)=I-K+zK.

**Peeling lemma.** If

    D_(K_m)(z) ... D_(K_1)(z) = I-E+z^m E

for an idempotent E, then every K_i=E. To prove this, multiply on the left
by D_(K_m)^(-1)=I-K_m+z^(-1)K_m. The remaining product has no negative
power and has degree at most m-1. Its coefficient of z^(-1) gives
K_m(I-E)=0. Its coefficient of z^m gives (I-K_m)E=0. These equations give
K_m=K_m E=E. Remove that factor and continue. The m=1 case is immediate.

Now take m=a+b full calls on 4q fields. Each stage projector has rank 2q
and each square-zero query has rank q. There are a forward and b inverse
stages, no extra work or stage calls, and the proposed endpoint is

    S (z^a E + z^(-b)(I-E)),       rank(E)=2q.

Normalize constant ordinary maps as in Section 1. At S=1 multiply the
whole word by z^b. An inverse stage becomes D_(I-P)(z). The peeling lemma
then forces P=E at every forward site and P=I-E at every inverse site.
Every query is confined to the same sector as its P. At S=-1 each sector
must therefore produce -I from its own square-zero unipotent factors.

Zero or one such factor cannot give -I. Two cannot give -I either: if
T_2 T_1=-I with T_j=I-2R_j and R_j^2=0, then
T_2=-T_1^(-1)=-I-2R_1. Its eigenvalues are -1, while those of T_2 are 1.
Thus both a and b must be at least three.

Five calls cannot realize this extreme signed endpoint, at any coupled
width q. Six calls do attain the algebraic bound: use a three-transvection
triangle on each two-dimensional sector, with three forward stages on one
sector and three inverse stages on the other. The replay checks the complete
Laurent endpoint with powers (3,3,-3,-3). Direct sums give every q.
This is a sharp caller-count statement for this endpoint, not a cost result.

## 6. Scope left open

The results do not cover more than n+1 queries, initialized extra work,
separate native stage maps or idles, a stage with a finite-order relation,
ordinary coefficients that do not commute with S or z, coupled query rank
greater than one in Sections 1--4, or changed independent helper targets.
COUPLED.md supplies a separate complete extension of the thin-call bounds
to every coupled width in characteristic zero, without commuting matrix
coefficients. It also extends the finite-period argument.
They do not replace native phase checks, source-bound routing, ownership,
precision, complete pricing, compiler or outer admission.

The finite-order example U_7 from the linked predecessor has ranks
8,16,24,24,16,8,0 in its seven powers. The balanced nine-call/eight-field
test is outside the predecessor's cyclic reduction lemma. PERIOD.md gives
an additional Gram argument that does reject it, and checks that the actual
native stage has all seven characters. Period six remains open. The saved
bounded cyclic numerical tests are not impossibility certificates.

Prepared by Ali Romman with substantial OpenAI Codex assistance. The model
uses Cinna Davis's query/controller lineage and the retained P104/native
sources. New normal-form application, projector exclusions, signed bound,
and replay: this package. No worldwide priority claim. Apache-2.0.
