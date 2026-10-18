# Model and certificate argument

This written argument concerns the 33 supplied formal words, with arbitrary
complex scalar coefficients. The executable certificate is not a Lean proof.

## Operators and endpoint

Use basis vectors |x> indexed by x in F2^3. Let X_v translate x by v, and
Z_v multiply |x> by (-1)^(v dot x). The paid gate, for nonzero v, is

    C_v = ((1+i)/2) I + ((1-i)/2) X_v.

In particular C_v^2 = X_v. Each occurrence is charged one paid call. The free
unaries are S_j|x> = i^(x_j)|x>, X_j, Z_j, directed CNOT gates
x -> x + x_a e_b, and CZ gates (-1)^(x_a x_b). The 18 free gate indices are
listed explicitly in `model.py`. Their words are fixed inputs, not additional
optimization variables in the exclusion.

Let G be their projective Clifford group, represented by conjugation on the
six Pauli generators. A Pauli is encoded as i^p X^x Z^z. Scalars that give the
same conjugation action are identified. Let D be the diagonal Pauli subspace
and H its monomial stabilizer. The frame key of g records g^-1(D); equal frame
keys specify the same left coset H g. The Fourier rank rho(g) is the binary
rank of the X parts of the images of the three Z generators. It is constant
on each left H coset.

A word is a 3-by-3 matrix over C[G], built from fixed unary diagonal matrices
and three arbitrary scalar matrices in GL(3,C). Its required endpoint is:
for each input column s, all nonzero group coefficients across the output
rows lie in one coset H g_s with rho(g_s)=3. This is the precise condition
being excluded. No finite 8-by-8 matrix representation is assumed linearly
independent. The negative conclusion is in the formal group algebra.

For an intended tensor realization the inherited phase-quotient convention
requires multiplicity divisible by four. The finite dense controls verify
projective operators, not all tensor sizes, compilation or paid bit costs.

## Necessary Boolean conditions

Expand the word by paths. A path chooses one scalar entry per block and
contributes their product to one output/input/group coefficient. Equal group
labels are collected before endpoint constraints. The saved words have
coefficient one on each resulting path monomial; the arithmetic checker
explicitly checks this condition when reducing to binomial equations.

Each scalar entry has a Boolean variable meaning nonzero. Invertibility
requires a nonzero determinant permutation term, although such a term alone
does not imply invertibility. Choose exactly one admissible full-rank frame
per input column. Every coefficient outside that frame must vanish. Exactly
one active monomial in such a coefficient is impossible, so the formula
forbids it. Allowing two or more active terms is only a relaxation.

There is also a necessary whole-matrix matching test. Augmentation g -> 1
maps the invertible word to the product of its scalar blocks. If positions
with any full-rank term admit no perfect matching, its augmented endpoint
would be singular. The formula then includes an empty clause.

Boolean UNSAT is checked by a tree of binary splits, unit reasons and conflict
clauses. The replay uses literal lists, separately from the solver's bitset
propagation. A surviving Boolean model is not an arithmetic solution.

## Invertibility constraints

Write a three-block word, in matrix-composition order, as

    diag(w) C diag(v) B diag(u) A diag(t).

For each middle product g = v_i u_j, let M_g retain the entries B_ij with
that product. Before the outside unaries its coefficient matrix is

    R_g = C M_g A.

At position (r,s) the outside operations relabel g as w_r g t_s, a bijection
on labels. The chosen endpoint frames thus determine allowed positions of R_g.

Only classes occupying distinct rows and distinct columns of B receive the
following strengthening. Such an M_g is a partial permutation with scalars.

1. A required zero column of R_g implies M_g A(:,s)=0 since C is invertible.
   Distinct occupied rows imply B_ij A_js=0 at every occupied position.
2. A required zero row implies C(r,:) M_g=0 since A is invertible.
   Distinct occupied columns imply C_ri B_ij=0.
3. rank(R_g)=rank(M_g) equals the number of nonzero retained B entries.
   A matrix supported on a graph has rank no larger than that graph's maximum
   matching. The allowed positions of R_g must admit a matching at least as
   large as every active subset of retained B entries.

These implications yield necessary clauses. Nonpartial classes are left to
the weaker filter. Omitting these constraints cannot create a false exclusion.
The independent encoding builds middle classes from unary group products;
the producer's encoding builds them from path monomials. Their full formulas
are compared for every supplied word.

## Torus refutations and learned clauses

Fix one exact entry support and three selected frames. Every retained entry
is in C*. When every unwanted coefficient has at most two active monomials,
its nontrivial equation is x^a+x^b=0, equivalently x^(a-b)=-1.

The certificate performs unimodular integer row and column operations on the
exponent matrix. Row operations preserve the torus equations; columns give
an invertible monomial substitution x_j=product(z_i^V_ji). A positive diagonal
and zero rows suffice; Smith divisibility is not needed. An odd right-hand
parity on a zero row is inconsistent.

Otherwise a diagonal entry 1 fixes a sign. An entry 2 with even parity has
both signs as components. Other torsion or excessive component counts are
left unresolved by the arithmetic producer; the negative checker accepts no
certificate that silently omits them. All 78 saved negative certificates have
diagonal entries 1.

On every component, substitute into det(A) det(B) det(C). If this Laurent
polynomial is identically zero, no point on the component makes all blocks
invertible. The checker directly expands the product using Leibniz's formula,
rather than the producer's successive polynomial products. It checks every
integer operation, the substitution and complete component coverage.

Such a refutation permits a clause blocking exactly this entry support and
these frame choices. It does not permit blocking neighboring supports or
unspecified frames. The checker verifies the literal learned clause and then
replays the next support proof. A final Boolean contradiction covers all
remaining assignments; the removed ones already have exact refutations.
Therefore the entire fixed word is excluded over C, including scalar blocks
with zero entries. No arithmetic search timeout is used as evidence.

## Boundaries

This proves no impossibility for arbitrary three-block words, arbitrary
Clifford circuits, different frame groups or a finite representation that
admits additional linear cancellations. It does not decide the full register
problem in PR #288 or bound integer multiplication. The inputs are 33 explicit
skeletons, not representatives of all possibilities.
