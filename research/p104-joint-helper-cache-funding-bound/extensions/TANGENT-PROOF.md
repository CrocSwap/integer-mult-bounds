# One common tangent preserves finite exact cache and zero dependencies

## Proved local statement

Let F=R and S be an embedded C1 submanifold without boundary of F^H, or
let F=C and S be a complex submanifold of C^H. Work at an interior point.
Let I be the original retained helper coordinates, J its complement, and
M=F^a times S, with all main inputs independent of the helper promise.
Fix finitely many F-linear observation maps A_e and F-linear targets t_e
on F^a plus F^H. Assume t_e is an exact deterministic function of A_e on
M locally: equivalently it is constant on each observation fiber. No
continuity or differentiability of the provider function is assumed.
Let finitely many linear zero rows z_j vanish identically on M.

At q=(m,p), assume pi_I:S->F^I is a submersion, and each A_e restricted
to M has locally constant rank near q. Put T=T_p S and W=F^a plus T.
Then ONE W simultaneously has:

1. surjective projection of T onto the retained original I coordinates;
2. z_j restricted to W equal to zero for every original zero job;
3. F-linear maps B_e with t_e|W=B_e A_e|W for every original cache.

T is a homogeneous linear space of variations; p need not be zero or
belong to T. The resulting provider coefficients need not be rational.
The statement is about fixed original maps, not input-dependent histories.

## Fiber-curve proof, without differentiating the provider

For a constant-rank map f, every v in ker(df_q) is the velocity of a
C1 curve through q contained in f^{-1}(f(q)). One local proof chooses a
nonzero maximal Jacobian minor and uses the inverse function theorem to
make its r output coordinates the first r domain coordinates u. Write
the remaining domain coordinates v. Constant rank forces every other
output derivative in the v directions to vanish; on a small connected
coordinate box those outputs depend only on u. Fibers therefore contain
all curves with u fixed, realizing their entire differential kernel.
The holomorphic argument is the same over C.

Apply this to A_e|M. Exact deterministic recovery makes t_e constant on
each such fiber curve, so dt_e annihilates ker(dA_e). Because A_e and t_e
are ambient linear maps, their derivatives are themselves restricted to
W. Thus ker(A_e|W) is contained in ker(t_e|W). Define B_e(A_e w)=t_e w;
this is well-defined and F-linear on A_e(W), and extends linearly to the
ambient observation space. The provider itself was never differentiated.
Differentiating z_j=0 on M gives z_j|W=0. The retained submersion gives
surjectivity onto I. The same p is used for every dependency.

## Existence of one common regular point for finite smooth data

The fixed-point constant-rank assumption cannot be dropped at an arbitrary
critical point. Nevertheless, if the retained projection is a submersion
somewhere and the exact dependencies hold on that neighborhood, a suitable
nearby common point always exists for finitely many maps.

The locus where the rank of a continuous matrix/bundle map is locally
constant is open dense. In any nonempty open patch, choose a point where
the finite-valued rank is maximal. A nonzero maximal minor gives a smaller
open patch with that constant rank. Apply this to each restricted A_e
Jacobian. A finite intersection of these open dense sets meets the open
retained-submersion locus. For ambient linear A_e, its rank on F^a plus
T_pS depends only on p, not m. Thus one helper p works for arbitrary main
variations. This argument does not use Sard's theorem or a differentiable
cache decoder. It does not cover an infinite family of required maps.

## Retained-coordinate funding

Let U=T-perp be the F-linear annihilator in helper covectors. Restriction
U->F^J is injective: a covector supported only on I and zero on T must
vanish, since T projects onto all of F^I. Hence the J columns have full
row rank in U. A column basis can be chosen entirely from J, giving
beta_f(U)<=sum_{j in J} f(R_j). This is an upper bound on the tangent's
minimum target debit by the actually fully debited helper set.

Every original zero/cache benefit survives on W, and the tangent may add
more. Thus the scalar-linear optimistic funding payoff of U is at least
the original payoff with the charged J targets, before preparation costs.
Any upper bound proved for all such linear U therefore bounds this smooth
nonlinear promise class as well. Preparation, circuit/grid admission and
ordinary costs are not constructed by this argument.

C40's proof permits real/complex coefficients: rational source ranks and
minor zeros persist under characteristic-zero extension, and a rational
generic appended row attains all maximal finite prefix ranks. A special
real/complex row cannot have a smaller minimum basis price than that
generic lower debit. The exact dependency review is snapshotted in inputs/.
No numeric kappa improvement follows from this reduction.

## Irreducible complex-algebraic corollary

Let S be an irreducible reduced complex algebraic variety in C^H, with
coordinate projection to C^I dominant. Assume exact set-theoretic cache
functional dependencies on C^a times S (or a common nonempty Zariski open),
with the same fixed finite linear maps. There is a nonempty Zariski open
of common valid p in S's smooth locus.

Indeed retained coordinates are algebraically independent in C(S).
In characteristic0 extend them to a separating transcendence basis;
their differentials are independent at the generic point. A nonzero
minor gives a dense open retained-submersion locus. Each observation
Jacobian has maximal rank on a dense open of the smooth locus. Intersect
these finitely many opens and choose a complex point there. Apply the
holomorphic fiber-curve proof. Irreducibility ensures the intersection is
nonempty. No differentiability or regularity of the decoder is needed.

Primary background: Ravi Vakil, The Rising Sea (2024 draft),21.6.1 and
21.6.4, gives generic smoothness; Stacks tag0322 records characteristic-zero
separability. The fiber argument and simultaneous-point/funding deductions
above are supplied here. Positive characteristic is explicitly excluded.

## Scalar arrays versus general array-valued promises

The proved scalar application has S contained in F^H. It also applies to
a coordinatewise product promise S^D with normalized observations A_e
acting componentwise, A_e tensor Id_D. Use the diagonal basepoint(p,...,p).
Its tangent is (T_pS)^D and has the same scalar equations on every entry.
A one-column variation shows the scalar kernel inclusion, so the same B_e
works componentwise. No f(D*r), dimension scaling or new all-column rule
is introduced; all retained native pricing conventions remain unchanged.

For arbitrary S contained in (F^D)^H, the tangent is block-linear.
BLOCK-LIFT.md now proves the required funding extension; its two independent
reviews are included alongside this note. Real-smooth complex promises use
realification to2D real entries, justified by this source's common rational-real
normalized coefficients. The conjugation example still refutes a complex-scalar
lift, while the real block theorem covers it. No infinite-dimensional claim is made.

Arbitrary discrete/exact-grid promises, nonregular digit-encoding sets,
main-dependent helper promises, approximate recovery and changing native
maps are not covered. See COUNTEREXAMPLES.md. No physical source or kappa
is claimed. The independent block reviews are BLOCK-REVIEW-A.md and BLOCK-REVIEW-B.md;
the smooth-array corollary is in SMOOTH-ARRAY-COROLLARY.md.
