# A sharp floor for one odd-entry rank-nine completion

This is a written theorem in the finite PR717/PR968 E8 label model. The
standard-library checker supplies every finite premise used below. The
argument over arbitrary complex coefficients is written here; it is not
formalized in Lean and is not inferred from the example factorizations.

## Statement and notation

Let F be the eight mutually orthogonal E8 root lines used by the coordinate
decoder, and L = P120 minus F, with |L| = 112. Choose the norm-two real root
representatives r_i used by the checker. Let R have rows r_i, i in L, and
G = RR^T. Superscript T means ordinary transpose, including over C.

The binary labels u_i span a nondegenerate nine-dimensional space Lambda
with symmetric pairing

    S(u_i,u_j) = (G_ij + 1) mod 2.

For a factor column d, let V(d) be the binary span of the labels in its
nonzero support. A term d t^T costs the binary rank rho(d,t) of the pairing
between V(d) and V(t). These are separate term costs; shared physical copy
trees or a changed billing convention are outside this statement.

Choose alpha,beta in L with G_alpha,beta odd and lambda in C nonzero. Set

    K = 2G + lambda e_alpha e_beta^T.

**Theorem.** K has complex rank nine. For every factorization K = DT^T
with D,T of size 112 by 9, the nine term costs have sum at least 64.
More strongly, for every real 0 < q <= 1,

    sum_k rho(D_k,T_k)^q >= 8 * 8^q.

Both bounds are attained by the eight coordinate terms and the extra
singleton term, whose costs are (8,8,8,8,8,8,8,8,0). Thus changing just
one odd entry cannot improve the separate copy bill even when every
factor term is allowed to change coherently. This completion respects all
even-entry constraints of the masked decoder problem.

## Finite premises and why they are exact

The checker independently constructs the 240 doubled-coordinate E8 roots,
their 120 lines, F, G and the binary pairing. It imports no predecessor
implementation or pricing engine. Its complete deterministic receipt is
CERTIFICATE.json.

1. The pairing has binary rank nine and 120 distinct rows. Its row space
   therefore enumerates all 511 nonzero functionals on Lambda.
2. For each alpha in L and each such functional h, form the integer matrix
   whose rows are the doubled roots r_i with i in L minus {alpha} and
   h(u_i) = 1. Exactly nine functionals have complex kernel dimension one:
   h = S(u_gamma,.) for gamma in F union {alpha}. Their kernels are the
   complex lines C r_gamma. Every other matrix has complex rank eight.
   There are 1,008 rank-seven cases and 56,224 rank-eight cases.
3. For each of those 1,008 cases, the support
   {i in L minus {alpha}: G_i,gamma != 0} spans the binary hyperplane
   H_gamma = ker S(u_gamma,.), of dimension eight.
4. The even neighbors {i in L: S(u_alpha,u_i) = 1} span the real root
   space; so do L and each L minus {alpha}. Each live root has exactly
   four nonzero coordinates in the F basis.
5. For all 14,400 ordered root-hyperplane pairs,

       rank S|H_gamma x H_delta = 8 - [G_gamma,delta is odd].

   This also follows from nondegeneracy: H_delta's orthogonal complement
   is span_F2(u_delta), and u_delta belongs to H_gamma exactly for an odd pair.

For premises 2 and 4, rank eight modulo three is an exact nonzero-minor
certificate for rank eight over Q and C. In the rank-seven cases the
checker additionally tests the displayed nonzero integer null vector
against every row. The lower and upper bounds agree, proving the whole
complex kernel, rather than relying on finite-field rank alone. Premise 3
uses actual binary support elimination. No Weyl-flat classification or
sampled complex-normal search is needed.

## Support lemma

Write d = Ra + s e_alpha, where a in C^8 is nonzero. If V(d) is a proper
subspace of Lambda, some nonzero binary functional h annihilates it.
For every i other than alpha with h(u_i)=1, we must have r_i dot a = 0.
Premise 2 implies a is proportional to some r_gamma, gamma in F union
{alpha}. Premise 3 then puts the whole eight-dimensional H_gamma in
V(d). Therefore every such d has binary support dimension at least eight,
and a reduced support has V(d)=H_gamma with that normal.

For an unshifted column d=Ra, reduction is possible only for gamma in F.
Indeed gamma=alpha is live, d_alpha is nonzero, and S(u_alpha,u_alpha)=1;
adding that self-label to H_alpha gives dimension nine. The same argument
applies to any live gamma by choosing its own deletion in premise 2.

Consequently, for d=Ra+s e_alpha and t=Rb+v e_beta with both a,b nonzero,
rho(d,t)>=7. Cost seven requires both supports to be reduced, their
normal lines gamma in F union {alpha}, delta in F union {beta}, and
G_gamma,delta odd. If either support has dimension nine, the cost is at
least eight by the dimension bound dim V(d)+dim V(t)-9.

There is one further fact for pure singleton sides. If s!=0 and b!=0,
then rho(s e_alpha, Rb+v e_beta)=1. Premise 4 ensures Rb is nonzero on
some even neighbor of alpha. Beta is odd-paired with alpha, so the shift
at beta cannot cancel that entry. Thus the singleton pairing has a
nonzero entry. Transposing gives the corresponding right-side assertion.

## Factor spaces and coefficient identities

Premise 4 implies e_alpha is outside col R: if Ra=c e_alpha, deleting
alpha forces a=0 and then c=0. Likewise e_beta is outside col R.
Hence A=[R,e_alpha] and B=[R,e_beta] have full column rank nine, and

    K = A diag(2I_8,lambda) B^T

has rank nine. Every nine-term factorization has col D = col A and
col T = col B. Its columns can thus be written uniquely as

    d_k = Ra_k + s_k e_alpha,
    t_k = Rb_k + v_k e_beta.

Comparing coefficients in the independent row/column bases gives

    sum a_k b_k^T = 2I_8,       sum a_k v_k = 0,
    sum s_k b_k = 0,            sum s_k v_k = lambda.             (1)

Call a term mixed when a_k,b_k are both nonzero, and let m be their
number. The first identity in (1) implies m>=8, so m is eight or nine.

## Nine mixed terms

Every cost is at least seven. If the sum were below 64, all nine integer
costs would be seven. Consider their left normal directions. A left
normal in F can pair oddly with a right reduced normal only if that
right normal is beta, because every pair of F normals is even. Thus
all left normals lie among alpha and the four frame lines odd-paired
with beta. Their span has dimension at most five. This contradicts
the rank-eight first identity in (1).

At least one cost is therefore eight or more. For 0<q<=1,

    sum rho_k^q >= 8^q + 8*7^q >= 8*8^q,

since (7/8)^q >= 7/8. This proves both bounds in this case.

## Eight mixed terms

Number the mixed terms 1,...,8 and the extra term 0. The eight a_k and
the eight b_k are each bases by (1). Interchanging sides if necessary,
assume a_0=0. Full rank of D means s_0!=0. The second identity in (1)
forces v_k=0 for all eight mixed terms.

If b_0=0, the third identity forces s_k=0 for all mixed terms too.
Both sides of each mixed term are now unshifted root-linear columns.
They each cost at least eight: a reduced side must have a normal in F,
and two frame normals cannot pair oddly. The extra term costs zero.

If b_0!=0, the pure singleton side costs one by the support lemma.
All eight right mixed columns are unshifted, so a cost-seven term must
have right normal in F and left normal alpha. At most one mixed term
can have that left normal, because its a_k form a basis. The cost profile
therefore dominates either eight eights plus one, or seven eights plus
seven plus one. Both have sum at least 64, and

    7*8^q + 7^q + 1 >= 8*8^q

by subadditivity (7+1)^q <= 7^q+1 for 0<q<=1. Transposition preserves
cost, so this covers an extra pure right side as well. QED.

## Attainment, scope and remaining obligations

For the frame roots f_j, let X_ij = G_i,f_j. Orthogonality and norm two
give XX^T=2G. Premise 3 gives cost eight for every coordinate term;
the odd singleton term costs zero. This proves attainment for every
allowed alpha,beta and every nonzero complex lambda.

The checker also supplies a nontrivial attaining profile
(7,8,8,8,8,8,8,8,1). It cancels one live self-entry in a new root-normal
column and pays for the necessary compensating singleton-side term.
Discarding that compensation is an invalid masked decoder. Its sum is
64 but its separate power bill is strictly larger when 0<q<1.

Only one changed odd entry, exactly nine factor terms, this finite P112
geometry and separate label-pairing costs are covered. Arbitrary free
rectangles, multiple changed odd entries, ten or more terms, different
punctures and shared-copy pricing are outside the theorem. This is an
optimistic rejection screen: no physical gathering, frames, helpers,
restoration, hosting, precision/tape or whole supplier is built or priced.
The selected supplier and its inherited all-size/compiler, common-label,
mutable-source, analytic and bit H1-H5 obligations are unchanged.
