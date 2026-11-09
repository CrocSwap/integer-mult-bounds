# Admit full-period fine-family expansion pages, and delimit their direct port

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Source-bound enabling/adversarial result; no new kappa. Canonical main:
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## 1. What is new, and what is inherited

The actual canonical expansion is #3878's `Tile`, `TilePreparation`,
`BlockGeometry` and `ProductionBlock`. Its explicit page API is distinct
from `ProductionTile`, which imports the old paired compression
`ProductionPlan`. The latter's admission is incompatible with the fine
family, as the public caller audit at 96211247643059ae48af4c7d9dc960034798935d
proves. We change or bypass none of its guards and claim no old Tensor run.

#3878 already proves local expansion at every ratio 1<t/s<2, explicitly
including alpha^2*(t/s-1)<1. #5056 proves its actual inward norm invariant;
#5295 derives the actual five-residual accuracy telescope; #6085 proves the
encoded scalar exponential enclosures. Those results are reused, not new
norm, tail, rounding or transcendental theorems here. #5325 joins a different
old Tensor normalization and does not install a fine-family production policy.

The new source interface is a complete explicit full-period page admission,
with the original periodic halo and its multiplicities, and a declared
normalization/output conversion to the public fine-family middle at
8db3cc1e98ba295cec4d752478431515e159c34f. The existing forward normalization
pays the Tile's built-in one bit per axis. The changing source/target volume
cannot use the old input as the public codec's return clock. We give a paid
T-record adapter and a real native-word/codec witness for that exact seam.

This is an admitted **slow reference**, conditional on the credited exact
word/convolution and source arithmetic contracts. The explicit sequential
route below cannot meet the desired positive-kappa caller. Its literal
writes establish that limitation; generic per-axis costs are not claimed
as a new general lower-bound theorem. No broad Core is implemented.

## 2. Source-first full-period page certificate

Fix integer q>=101, integer alpha>=2 with u=alpha^2<q, and positive
integers s<t<2s. Require s,t,alpha<2^q, the literal `fits` metadata clauses.
Here q is the working component grid, while p0 below is the original
fine-family parameter. They are not silently identified. Define

    b=alpha*ceil(sqrt(q)), P=32768q, sigma=4096q,
    source_start=-b-1, source_count=input_capacity=s+2b+3,
    target_start=0, target_length=t, blocks=ceil(t/b).       (1)

These are inputs to the unchanged `TilePreparation.run_explicit`. Every
nonfinal block has m=b; the final block has 1<=m<=b. This instantiates the
public explicit API with a proved replacement source contract, rather than
changing `ProductionTile` or asserting its paired inverse guards.

The literal `compile_tile` inequalities all hold. Since q>=101,
ceil(sqrt(q))<sqrt(q)+1 and alpha<sqrt(q),

    b<q+sqrt(q)<=11q/10,
    3b+3<4q, 4b+2<5q.                                    (2)

The strict first square-root estimate remains valid when q is a square.
Each Block has n<=2b+m+3<=3b+3 and nc=n+m-1<=4b+2. For q>=101,
ceil(log2(32(3b+4)))+12<=q+21, whereas
P-2sigma-q=24575q. Thus every actual Block/Tile work-precision guard holds.
All header fields requiring positivity are positive, the version is 2,
source_count equals capacity, and the target origin is zero. Every later
block origin is below t and fits its q+2-bit origin clause.

For a block starting at v with length m, the exact source endpoints are

    a(v)=floor(sv/t)-b-1,
    c(v,m)=ceil(s(v+m-1)/t)+b+2.                           (3)

This follows from the actual j0, gamma and h_high formulas, with
`gamma=floor(sv/t)-sv/t`; in particular the upper endpoint uses a ceiling.
For the full period, ceil(s(t-1)/t)=s because 0<s/t<1. Hence the union
starts at -b-1 and ends at s+b+2, proving containment in (1).
Endpoints are nondecreasing and consecutive windows overlap: with
x=s(v+m-1)/t and 0<s/t<1, floor(x+s/t)<=ceil(x), leaving at least the
stated b margins. These are exactly the monotone stream conditions used
by `Tile.run`, including the clipped final block.

Supply at halo position j the original source value x_(j mod s), for every
integer j in [-b-1,s+b+2). Repeated residues are repeated *occurrences*,
not a set of distinct source indices. The theorem does not require b<s.
When b>=s, some residues appear many times; replacing this stream by one
copy per residue changes the Gaussian sum. A target lift by c*t uses the
source lift by c*s and leaves the residue stream and exact output unchanged.
The optional capacity beyond source_count must be literal zero padding;
(1) needs no such padding. Borrowed original source values are preserved.

## 3. Bind the actual coefficient producer, not an arbitrary page

`prepare_page` forms the actual rational A/K/B exponent families in original
coordinates, measures the maximum ceiling of their absolute values, and
passes that positive bound to the unchanged encoded `Exponentials` owner.
The source quadratic identity is

    U_h+V_z+K_(h-z)=(j0+h-(s/t)(v+z))^2/u.                (4)

#3878's bounds, applicable under (1)-(2), give |U|<20q, |V|<3q and K<12q.
The factor scales are exactly sigma for A and B and zero for K. Thus the
actual arguments satisfy the all-rational sign/scale domain proved by #6085,
without importing that audit's separate narrow-Axis geometry. The lower
endpoints are nonnegative, no larger than the true factors, and have error
<3*2^-P/2, which is stronger than #5295's required 4*2^-P allowance.

The actual exact-unit and reflected-kernel branches preserve the same
factors. Crucially, a true factor <=1 alone would not prove the preparer's
*upper-endpoint* unit check. The actual production allocation supplies the
missing admission implication. Here K_d is the exponent in (4), and k_d=exp(-pi K_d) is its kernel
factor. Using pi<4 and e<4 in the quadratic bounds,

    2^(-4256q)<A_h,B_z<2^(-3936q),
    2^(-96q)<k_d<=1.                                    (5a)

The coefficient audit's lower error <3*2^-P/2 and interval width <=2*2^-P
therefore imply strictly positive stored A/B factors and upper endpoints
<1, for every admitted q. These inequalities also give positive stored kernel factors.
For the kernel upper endpoint, inspect the actual decay branch: positive_interval
starts total_lower at its R-grid unit, only adds nonnegative terms, and each
outward squaring preserves total_lower>=unit. Hence ceil(unit^2/total_lower)
<=unit. The subsequent outward shift to P still gives upper<=2^P, even for
arbitrarily tiny positive K arguments. The kernel at argument zero is exactly one.
Thus the actual unit check passes without an unjustified separation from
one. Reflected coefficients copy already-admitted identical K values.

The normalization is exactly floor(2^P/(2alpha))/2^P. It is positive because
2alpha<2^(q+1)<=2^P, at most 1/4, and has error <2^-P. This binds the scalar
enclosure theorem to every actual expansion producer acceptance check,
including positivity and the near-unit endpoint. It does not reclaim the
predecessor general enclosure theorem. The complete ordered page headers
agree with (1)-(3); arbitrary parsing or positivity does not certify a page.

The original exact line target is

    (A_i x)_v=(S_i x/2)_v
      =(1/(2alpha_i)) sum_(j in Z)
        exp(-pi*(j-s_i*v/t_i)^2/alpha_i^2) x_(j mod s_i). (5)

All omitted integer occurrences are outside the short stencil and at
source distance >b. The credited production tail bound therefore applies
also when several occurrences have the same residue. It is a sum of
positive omitted masses, not a distinct-residue count. Matching the actual
crop, work-grid restoration 2^(2sigma), and final q-grid extraction gives
#5295's actual-input complex-modulus defect

    ||Tile_i(x)-A_i x||_abs < (sqrt(2)+2^-11)2^-q.        (6)

The source coefficient/primitive and original-periodicity contracts remain
explicit. Equations (1)-(4) discharge the particular page/frame admission
missing when the old paired ProductionTile is unavailable; they do not
reprove the predecessor arithmetic theorem or all-size word service.

## 4. Original coordinates and the reached half-disk

Start with source coordinates in order (D-1,...,0), axis zero fastest.
For axis i, treat that original axis as the contiguous line, use the pages
(1), and write all t_i target records for each spectator line. An exact
cyclic axis rotation then moves that completed axis to the slowest position.
After D steps the order is (D-1,...,0) again, with all target lengths t_i.
No coarse tile index is substituted for a Fourier axis and no coordinate
called a hole by the narrow map is omitted from the T-record target.

A concrete unchanged rotation is `FieldMove.run` with
C=1, A=V_(i+1)/t_i, field=t_i, R=2(q+2), right=False. Its declared map is
[C][A][field][R bits] -> [C][field][A][R bits]. Each t_i is dyadic for the
fine family; its padding is consequently exact with Q=t_i. This is a
specified, expensive reference route, not a free permutation or a new
fast Broad controller. Periodic halo creation is a sequential source-line
scan with an encoded residue counter and paid rewinds at each wrap.

The actual digit ingress in `Sandwich.ingress` scales each unsigned b_digit
bit digit by 2^-(b_digit+2). Its plan.p is our q; the source function
parameter named q instead counts digits. Provided our q>=b_digit+2, this is exact on the
q grid and its complex modulus is <1/4 (imaginary part zero). CRT address
permutation and zero padding preserve that bound. We reuse only this
literal ingress fact; we do not invoke the rejected old Sandwich catalogue.

#5056's positive-majorant argument proves the actual Tile norm bound at
each reached input, including every signed internal truncation. A sufficient
credited bound is 3/4 per axis. Thus an actual quarter-disk input reaches
modulus at most (1/4)(3/4)^D before the final normalization below, and never
leaves the unit disk during its sequence of completed axis calls. This
hard norm conclusion uses the matching lower coefficient pages in Section 3;
it is not inferred from an ideal-map bound while ignoring internal rounding.
The final inward normalization/serialization cannot increase modulus.
Consequently the public middle's actual <=1/2 guard is met with slack.

## 5. Spend the existing forward normalization and pay the return clock

Let k_i be the already-declared forward normalizers of the current
fine-family source, K_f=sum k_i, and require K_f>=D. The canonical sufficient
choice k_i=100 ceil(log2 p0) satisfies this. Let K_c be the already-declared
compression sum used by the public group ledger, so its existing Gaussian
restoration is Gamma=K_f+K_c. This Gamma covers only these declared
Gaussian dyadic normalizers; the two source-size S factors and any separate
outer Fourier/integer-recovery scales remain outside this proposition.
Native inverse normalizers are spent *inside*
K_c by that ledger's first policy. They are not added here.

The exact normalized expansion required by the current source is

    E=2^-K_f tensor_i S_i.

The unchanged Tile sequence instead approximates tensor_i A_i=2^-D tensor_i S_i.
Therefore apply exactly one final inward q-grid scale with

    J=K_f-D>=0.                                         (7)

Its exact unrounded target is E. Neither D nor J is a new addition to
Gamma, and the internal 2sigma restorations are already within each Tile.
Adding D to Gamma after (7), or using a final scale K_f instead of J, changes
the represented source transform by 2^D or 2^-D respectively.

The public Core/halo codec's `prepare_return` uses its unchanged input as
its record clock and checks the native EOF. A compact S-record original
source cannot clock a T-record expanded return when S<T. In particular,
reusing it would reject extra output; it would not silently complete the
same-volume bridge. `return_codec.py` supplies an owned T-record all-zero
clock, prepares the codec on that clock, then converts the actual T-record
native return with Format(q+2,q,q+2,q,J). The dummy native entrance and
zero clock are real paid fields. A protected output copy is made before
abort erases the helper data; the actual native return stays borrowed.
The adapter copies a borrowed encoded positive T Count at construction;
its small fixture supplies that Count literally. It does not implement the
outer source of T. Format(q,J) template construction is input-independent
and costs O(q+J); those prepared grid/normalizer scalars are declared caller
inputs. The online clock loop uses the copied Count and costs O(Tq).
The incoming native field is disjoint from the borrowed count, its copy,
the codec native buffer and every owned native scratch tape. Native and
external tape classes are distinct; all B-format clocks/work/output are
private distinct owners. These are explicit source/ownership premises,
not a claim that an encoded complete prefix controller was constructed. This is only the dimension-changing return adapter;
it does not claim execution of the complete Tile sequence in the fixture.

It rounds each component once, with component-l1 error <2^(1-q), except
that J=0 is exact. Signed zero is canonicalized. Its native word count,
external word width, grid, and normalization bits are checked explicitly.
Short, long and old-S-clock returns are rejected, and owned helper cleanup
and borrowed native body/origin are checked in the bounded witness.

## 6. Explicit prefix error into the public middle

Use ||.||_* for maximum coordinate component-l1. Because every exact A_i
has nonnegative real coefficients and row sum at most 3/4, it contracts
this norm by 3/4. Convert the *local final* complex error (6) once:

    delta_* < (2+sqrt(2)/2048)2^-q < 3*2^-q.

At the actual computed input of each axis, the credited telescope therefore
gives e_D<3*2^-q sum_(j=0)^(D-1)(3/4)^j<12*2^-q. This is an application
of #5295, not a new general telescope and not a Lipschitz claim for rounded
Tiles. Exact rotations and periodic copies introduce no arithmetic error.
After (7) and the actual return projection,

    epsilon_exp = ||Ehat(x)-E(x)||_*
      < (12*2^-J+2)2^-q <=14*2^-q.                     (8)

Inward radius is retained even when a coarse grid erases values; accuracy
still requires (8) with the later restoration paid. In the public middle's
actual caller equation, this prefix contributes at most

    2^Gamma ||C_N||_* sqrt(2) epsilon_exp,              (9)

where C_N is the exact normalized ideal compression from the public
Reference join. Under that caller's proved ||C_N||_*<=1 premise, the simple
sufficient allocation

    q>=Gamma+tau_exp+5                                 (10)

makes (9) strictly less than 2^-tau_exp, since 14sqrt(2)<32. Retain the
actual norm if that premise is absent. The middle gets its separate chi/f
allocation; compression and all extra interfaces retain separate allowances.
For example the completed total is bounded by 2^-tau_core +2^-tau_exp
+2^-tau_mid + e_extra when all three admitted budgets are satisfied.
This is not complete Fourier, opposite-sign or integer-recovery admission.

The original fine family has D=Theta(p0^(1-epsilon)), epsilon=10^-30,
alpha^2=O(log p0), log2 T=Theta(p0), and Gamma=O(D log p0)=o(p0).
Choose q to satisfy (1), metadata fits, ingress q>=b_digit+2, (10), and
the middle/caller's other sufficient conditions. For targets O(p0), one
q=O(p0) suffices eventually. No unquantified finite onset is inferred from
that asymptotic statement. These exact inequalities are finite admission
tests, including the original-period size conditions used below.

## 7. Full invoice and the obstruction for this direct port

Let V_i=product_(j<i)t_j product_(j>=i)s_j, so V_0=S and V_D=T.
Axis i has V_i/s_i complete original spectator lines. Its halo has
s_i+2b_i+3 records; one encoded periodic counter copies every occurrence,
with initial positioning and every wrap paid. The literal Tile validation,
all A/K/B/normalization products, prefix convolution, crop, copying,
return consumption and cleanup have the inherited complete bound

    O((V_i/s_i)(s_i+t_i+b_i) q log^2(q+2)).             (11)

This includes the short-block coefficient reads for every line. Production
pages are prepared once per original axis and reused, not regenerated per
spectator. The actual source size is O((t_i+b_i)q); input-independent
preparation costs sum_i polynomial(t_i,q), with every coefficient owner,
ratio operation, reflection scan, header, page copy and retained history
charged. #6085's explicit shifts cost their lengths; sigma=4096q is O(q),
not merely O(log q). With fresh history the fine family pays
D*2^O(ell)*poly(p0)=2^o(p0); retained historical backing remains additional.

The specified whole-axis FieldMove rotation costs
O(V_(i+1) q (1+ell_i)) including each split, padding/crop, full spectator
scan, parent copy, child consumption and restoration. This is its actual
full-field application; the old short-field O(log q) rotation bill cannot
be substituted when the moved field is the complete original t_i.
The final clock/codec costs O(T(q+J)+q+J), and owns a constant number of
full T-record fields, plus encoded templates and their retained extents.
All axis/period metadata, owned halo buffers and full original source data
remain in the bill. Storage includes the complete O(Tq) field banks,
O(sum_i(t_i+b_i)q) pages, short work fields and every numerical child's
active/inactive and historical high-water backing.

If each b_i<=s_i and T/S<2, (11) sums to O(DTq log^2(q+2)). The reference
route and final conversion give the conservative online upper bound

    O(Tq(log2 T + D log^2(q+2)) + T J),                 (12)

plus the stated setup and metadata. The period condition b_i<=s_i holds
eventually because ell_i=Theta(p0^epsilon) dominates log p0, but it remains
an explicit finite test; the general bill (11) applies when it fails.

There are two literal lower bills. First, `Tile.run` copies every returned
complex word, so its outputs alone require

    2(q+2) sum_(i=1)^D V_i > (q+2)D T                  (13)

under T/S<2. Since digit ingress requires q>=b_digit+2=Theta(p0), this
already costs Omega(n p0^(1-epsilon)), excluding this unchanged sequential
port from O(n p0^(1-kappa)) for any fixed kappa>epsilon. This is a statement
about these mandatory writes, not a general lower bound for Gaussian maps.

For the particular full-axis FieldMove route specified above there is an
even stronger bound: its loop performs ell_i complete-volume stages on
axis i. In its actual right=False branch, stage j has 2^j prefixes,
A=V_(i+1)/t_i spectators and suffix=(t_i/2^(j+1))*2(q+2).
The two copies per spectator write exactly 2(q+2)V_(i+1) bits.
The Counter loop runs ell_i times; even A=1, all-zero data or an identity
permutation does not skip it. With Q=t_i, padding adds no coordinates.
Thus the stage writes give
Omega(S q sum ell_i)=Omega(n p0)=Omega(n log n). When the fine-family tests
hold, (12) matches O(n log n) up to the stated inherited constants because
D log^2 p0=o(p0). We do not price these rotations as the old microbox moves.
Changing the routing could remove this latter obstruction while leaving
(13). Avoiding (13) requires changing the one-full-field-return-per-axis
schedule, for example a separately admitted grouped implementation.

## 8. What a fast grouped Broad can reuse, and what it must still prove

The reusable object is the certified original-coordinate operator E and its
actual normalization/precision boundary: a quarter-disk source reaches the
middle's half-disk, with error (8) and unchanged Gamma. A future group
implementation can compare its output against the same S_i coefficients,
including every periodic occurrence, or against their certified intervals.
In the augmented canonical broad representation, scattering source j to
its original q_j and filling holes with zero gives M J_source=S_gauss;
this is the source convention already specified in GAUSSIAN.md, not a new
identity or permission to relabel coordinates freely.

Such a group implementation must prove its own prepared coefficient/source
binding, original-q scatter and hole semantics, reached-input error/radius,
full movement/ownership/setup bill, and actual same-map normalization. It
cannot reuse this slow reference's favorable numerical contract as evidence
for its missing runtime or as a free whole-field routing oracle. The public
middle and compression still retain their scalar/Fourier/native premises;
the five foundational assumptions and accepted bound remain unchanged.

The checks combine source fingerprints with independently derived integer
halo/header/cost and rational normalization cases. The native fixture runs
only the new return adapter with the real public codec and real native
Tape words, under the inherited loader; it does not execute production
Tiles, a complete prefix, or production GL64/O73. Written universal proof,
finite support and source-model-assisted review have distinct roles.
