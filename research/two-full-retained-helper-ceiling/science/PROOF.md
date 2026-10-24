# Retaining simultaneous helper jobs does not rescue two FULLs in the separated algebra

This outputs-only gate answers the four-owner correction to the original
three-owner question. It proves a scoped obstruction, not a new construction
or kappa. It keeps every original helper job distinct and counts its transform
once in its own paid invocation. Full central/fresh address mixing remains
outside the theorem and is the next constructive question.

## Literal simultaneous source contract

Freeze the native source at `20bb93cd990d2ff683e4d0fc56b87a42cd5d3296`.
Its authenticated main interface has form

    F_s = diag(d_sx,d_sy) [[1,0],[Q_s^-1,1]],
    B_s = diag(d_sx,d_sy) [[1,-Q_s],[0,1]].

The d factors include the real transverse operations and their raw phase
translations. They are not silently set to identity or commuted through
central wrappers. Two source invocations also act on two DISTINCT original
helper inputs. For a forward first call and backward second call, write

    T1=diag(d_1x,d_1y,H1,I) E21(Q1^-1),
    T2=diag(d_2x,d_2y,I,bar(H2)) E12(-Q2).

Here H1 is the first call's helper job and bar(H2) is the second call's raw
dual job. The helper on which the other invocation has already acted is an
identity spectator at that invocation. Eij(a)=I+e_i a e_j^T. Products act
on column vectors from right to left. No H1/H2 equality is assumed.

For arbitrary interstage W let D1,D2 be these four-owner diagonal factors,
and N=W D1. The exact noncommutative expansion is

    Mij = (D2)ii [ Nij + delta(j,1) Ni2 Q1^-1
                   -delta(i,1) Q2 N2j
                   -delta(i,1)delta(j,1) Q2 N22 Q1^-1 ].

This is a source contract, not an emitted consumer. It preserves the order
of every raw d, Q and H factor. A candidate would need legal pre/post
boundaries L,R producing the two desired main jobs and BOTH original
helper jobs; replacing the helpers by one twice-transformed owner changes
the inventory and the question.

The frozen `phase_check.py` explicitly uses
`P.conjugate(ce,op)` for backward helpers. `prune_native.conjugate` negates
the primitive C signs, diagonal phases and global phase while retaining
circuit order. Thus bar(H) is entrywise complex conjugation, equivalently
H^(-T) for these unitary operators, and is generally NOT H.adjoint().
It does not reverse the entry/output charts. The earlier low-rank adjoint
matching is not used here. Full H9 is a special case: its C_ej factors
commute, so bar(F9)=F9.adjoint.

## Exact fullH9 source normalizers, with absolute phase

Actual helper224 has empty entry frame0 and full exit frame1. The frozen
canonical-frame engine therefore gives the literal native job

    H9=F9=product(j=0,...,8) C_ej,
    C_v=((1+i)I+(1-i)X_v)/2.

For each of the112 actual ports, let q and a_1,...,a_8 be its source
`DATA-PHASES.json` directions. They form an orthonormal nine-dimensional
binary basis. Put Q=C_q, D_A=product C_ai, and u=xor_i a_i. The portable
checker derives and verifies the literal identities

    F9 Q^-1 = X_t D_A,
    H9 = X_t D_A Q,
    bar(H9) = X_(t xor u) D_A Q^-1.                 (1)

In a Fourier character k, C_v has exact eigenvalue i^parity(v.k).
The checker derives t from the nine single-bit characters and verifies
both identities for ALL512 characters at each of112 ports:114688 exact
modulo-four phase equalities, including k=0. This proves absolute phase,
not just a binary symplectic action. No numerical matrix tolerance, zero
phase omission or tensor power of a sum is used. Pure word identities
lift columnwise to every positive width.

For example port0 has q=11,
`a=[13,14,7,16,32,64,128,256]`, t=15 and u=500. Thus

    H9 = X15 D_A Q11,
    bar(H9) = X507 D_A Q11^-1.

There is no additional global phase. In these coordinates X_t is a product
of a central Pauli translation and transverse Pauli translations. Hence
`rawD0=X_t D_A` lies in the separated free subgroup below. It need not
commute with the central phase wrapper `S|x>=i^parity(q.x)|x>`; port0 is
an actual noncommuting control because parity(q.t)=1. Conjugating the
literal words by an admitted central monomial keeps rawD0 in that subgroup
and H9 outside it, even when the resulting central queries do not commute.
This uses subgroup membership, not a false commutation identity.

These calculations reuse the actual recipe and normalizer observation of
the independent source/accounting agent, with exact source bytes retained.
They do not rerun the whole native632-field execution or the outer compiler.

## Algebraic statement, including all retained pure helper jobs

Let G be a fixed finite-phase Clifford group for one column, and H a
subgroup. At width f work in a finite-dimensional central-character twisted
group algebra A_f with subgroup algebra B_f on H/Z, over a characteristic-
zero splitting field K. Write d=dim_K B_f. Let pi:A_f->B_f retain only
subgroup basis classes. It is a B_f-bimodule map. Membership and this
projection are unchanged by scalar phases. No domain assumption is made.

For the source application, H grants all transverse Clifford operations
and central monomial operations, retaining their tensor-factor separation.
It includes the raw d_s, their translations and admitted central monomial
wrappers. A full rank17 main target is outside H. Equation(1) shows the
literal fullH9 helpers are outside H: their central factor is Q or Q^-1,
which is not monomial, while D_A is purely transverse. This is an exact
factor statement; it does not homogenize a rank4 helper to rank9.

Consider two main owners, m1 non-H helper jobs emitted in the first call,
m2 other non-H helper jobs emitted in the second call, and s further owners
whose desired maps lie in H (including restored identity scratch). Thus

    n=2+m1+m2+s.

Each call has ONE elementary main shear with a pure query outside H.
Its diagonal factors on the main owners are units in B_f. On its own
helper owners it performs the specified pure group jobs; other helpers are
identity spectators. Any H-valued helper factors are units in B_f and
included among the s ordinary owners. Helper owner sets are disjoint.
Allow arbitrary L,W,R in GL_n(B_f), and arbitrary noncommuting queries and
helper group words outside H. Suppose the endpoint is the two independent
non-H main jobs together with every original helper job and its required
H-valued spectators. Then no such endpoint exists.

### Compression proof

Write M=T2 W T1, with diagonal factors before the source shears as above.
Let U contain all output rows except the second shear's destination main
row and the m2 non-H helpers transformed in the second call. Let C contain
all input columns except the m1 non-H first-call helper owners. Thus

    |U|=n-m2-1,       |C|=n-m1.

For rows in U the second shear contributes no non-H term and its diagonal
factor is a unit in B_f. For columns in C, T1's diagonal is a unit in B_f;
its only other possible term contains the SINGLE first query outside H.
Multiplication by B_f on either side keeps that term outside H. Therefore

    (pi(M))_(U,C) = (D2)_U W_(U,C) (D1)_C.          (2)

No product of two non-H words is evaluated or assumed to lie in H. In
particular Q2, Q1 and the helpers need not commute or normalize B_f.

View W as an invertible K-linear map on the regular right module B_f^n.
Restricting its input to C gives an injective map on a |C|d-dimensional
space. Projecting its output to U can destroy at most (n-|U|)d dimensions.
Consequently

    rank_K W_(U,C) >= (|U|+|C|-n)d = (s+1)d.

The B_f-unit diagonal factors in(2) preserve this rank. A compression
cannot have greater rank than the whole matrix, so

    rank_K pi(M) >= (s+1)d.                         (3)

The desired diagonal endpoint instead projects to zero on its two main
jobs and all m1+m2 non-H helper jobs. Its s H-valued target words are group
units, so its projected rank is exactly s*d. Because pi is a bimodule map,
invertible outer L,R preserve projected rank. This contradicts(3).
Zero divisors in B_f do not affect this finite vector-space argument.

For the natural four-owner case, m1=m2=1,s=0. The two U rows are the source
main row of the second shear and the FIRST helper row. If pi(M)=0, both
rows of W must be supported on the first helper's single column. They
cannot jointly surject onto two independent B_f output modules. This is
the shortest form of the obstruction. It does not depend on a common Q,
the first shear orientation, or the quadratic double-query product.

## All-width faithfulness and exact free-control boundary

Let Z be the scalar subgroup of the chosen finite-phase group G; H contains
Z. At width f specialize every scalar z=ζI as ζ^f. The quotient A_f has
one basis class per projective group element G/Z. The proof of injective
tensor evaluation is short. Choose representatives v_t. For each t and
each other u choose a linear functional vanishing on v_u and nonzero at
v_t. Their product isolates v_t in degree |G/Z|-1. Multiplying by a power
of a functional nonzero at v_t extends this to every larger degree f.
Applying it to the tensor vectors proves independence for every
f>=|G/Z|-1. Thus the operator endpoint would give a forbidden A_f identity
at all sufficiently large widths. Width-dependent scalar coefficients and
free choices within this same finite alphabet are allowed. Accidental
small-width linear relations between Clifford matrices are not used.

The theorem grants a large but SPECIFIC free grammar: central monomials
and transverse Cliffords, with their separation preserved. Arbitrary
central/fresh address mixing is outside B_f. The theorem also retains
invertible global owner controls and restored spectator contracts. It
does not inherit the separate4856 maximal-grade proof's arbitrary
rectangular COPY/DROP conclusion. Discarding or erasing main-dependent
garbage can lower projected rank and is a different endpoint. Zero clean
work fields cleared at exit can be included by the equivalent kernel
form: (3) gives nullity at most (m1+m2+1)d, while the 2+m1+m2 required
non-H original input columns would all have zero projected output.
This requires a reversible global B_f extension and full cleanup, not an
unproved permission to erase arbitrary dirty state.

## Invoice, nearest predecessor and next actual lever

Retaining all816 autonomous helper rewards leaves the hypothetical invoice
`224H17+2H-2P`, with supplied optimistic margin39.063938114801903 at
C=.0030217758. That positive budget motivates testing a changed resource;
it is not an endpoint certificate. This gate closes the separated-resource
realization even with retained transformed helper operations. No kappa gain
or complete native obstruction is claimed.

PR4712, head b75a27bf07f1584b20babfddf887493981cd5949, already gives the
dirty-helper word `h+=x; h=Fh; y+=h; h=F^-1h; h-=x; h=Fh; y-=h`.
It returns `(x,y+Fx,Fh)`, with three F/F^-1 calls and four scalar ADDs.
Its paid-minus-helper bill is2*r^t against one replaced owned centre's
r^t. It is not a new saving and is credited here rather than rediscovered.

The nearest method is PR4920 at7eb4ef5251f7ba96c7e5d78c42fc98e66b7be4ba:
its separated theorem allowed identity scratch, while its full-monomial
grade theorem allowed exactly two owners. The present compression argument
adds simultaneously transformed productive helper operations to the first
scope; it does not combine the two old scopes into a universal result.
The parent independently checked the rank argument and supplied the
commuting-Q row-kill precursor. Native operators and source interfaces are
credited to Cinna Davis/1337isnot1337 and the upstream contributors. Source
normalizer reuse and backward-ABI correction are credited to the independent
accounting/source agent and shared-producer agent. New derivation and
portable corroboration: OpenAI Codex gpt-6.1-sol/high. Apache-2.0.

The smallest constructive change is a literal central/fresh monomial route
on the actual native role boundaries. It must preserve both distinct helper
jobs and pay for any entrance-chart conversion. X begins in a rank1 chart;
Y and the full helper begin empty. Common full exit charts do not make
swapping X and helper inputs free. An already transformed arbitrary value
Hh, supplied before all controls and returned unchanged, is just an arbitrary
dirty coordinate after renaming w=Hh; useful resource access must involve
the producer H itself or a correlated saved original input. No routing
family search or native word was emitted for this gate.
