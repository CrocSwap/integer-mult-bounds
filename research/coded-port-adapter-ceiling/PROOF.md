# A one-parallel-bank ceiling for the actual coded-port recovery adapter

This is a scoped exact-operator result, conditional on Dugongue's native
producer #4929 at `361f5d4100640177d6a983dd2f336021c75bfd5e`.
It is not a complete caller obstruction or a κ improvement. The package
independently checks the source charts, supported transport grades and code
inverse used below. It does not rerun the producer's all 632-input replay.

## 1. Actual source and physical offer

The native source compressed SHA256 is
`7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05`.
Its decompressed payload SHA256 is
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
These are two hash conventions for the SAME source object, retained in
canonical main `624de9dc` and the frozen #4610 source; they are not different
native words.

There are 112 X fields, 112 Y fields and 408 independent arbitrary helper
fields. X enters 112 distinct rank-1 charts U_i and exits a common full chart
T=F9 (its diagonal 112-fold action is denoted T below). Y enters the ground chart and exits 112 distinct rank-8 charts V_i.
Put U=diag(U_i), V=diag(V_i). All are the actual canonical source frame
Cliffords, including their phases; a bare C_q must not replace U_i without
its literal source normalizers. The source physical main operator is

    N_A = diag(T,V) S_y(A) diag(U*,I),
    S_y(A) = [[I,0],[A,I]].                         (1)

The source producer supplies (1) with autonomous original helper operators
on their own arbitrary inputs. It removes exactly8H8, retaining

    P_coded =2201H1+412H2+510H3+127H4+40H5,
    H       =28H4+7H7+47H8+326H9.

Its 6596 extra ground-chart dyadic ADDs have a supplied ordinary scalar
allowance 32652. The checker verifies these event counts and ground-chart
conditions from the emitted words; finite precision/stock admission is not
inferred. Eight owned centre Gaussian jobs disappear, but owned centre
scratch and its legal CLEAR lifecycle are not arbitrary productive inputs.
The original 632 input owners and all 408 helper jobs remain distinct.

The scalar code is A=I-14P with P an orthogonal rank-8 projection. The exact
checked polynomial is

    A^2+12A=13I,       A^-1=(A+12I)/13.              (2)

A is symmetric, has zero diagonal, and has 5824 nonzero off-diagonal entries
±1/2. Its eigenvalues are 1 and -13, with multiplicities 104 and 8. Thus its
Euclidean condition number is 13. The main shear and inverse each have norm
at most 14, giving condition number at most 196 for the complete physical
producer with its independent unitary helper block. These endpoint bounds
do not replace bounds on a newly implemented adapter's intermediate states
or propagation of rounding discrepancies inserted inside its word.

## 2. Exact forward and raw-dual recovery

Let N_I be the original uncoded main operator, replacing A by I in(1).
Set

    K=U A^-1 U*,       L=diag(A,I).

The common full X exit T commutes with scalar port mixing A. Hence

    N_I = L N_A diag(K,I).                          (3)

All helper outputs are untouched by these main-only wrappers. This is an
exact algebraic recovery statement on all original inputs, not an
implementation of K in the heterogeneous entrance charts.

The chronological naive implementation of K is: apply U_i* to every X_i,
perform the scalar A^-1 mixing in the common ground chart, then apply U_i
to every resulting X_i. It costs two banks of 112 H1, plus all scalar, routing,
storage, precision and normalization work. The full-exit A operation has
recursive grade 0, not zero ordinary cost. A simple out-of-place scalar
protocol needs owned output storage and a declared restoration/cleanup
protocol; an in-place rational elimination needs its actual fixed scalar
word. Neither is silently supplied by the matrix identity.

The raw inverse transpose preserves product order:
(ABC)^(-T)=A^(-T)B^(-T)C^(-T). The retained backward source uses entrywise
conjugated frame maps, rather than reversing chart labels. Therefore(3)
gives backward recovery with

    entrance X: K_B=bar(U) A^T bar(U)*,
    exit X:     A^(-T) in the common conjugate-full chart.            (4)

Y and helpers remain unchanged. In general bar(U) is not U*. Source helper
raw-dual operations are also entrywise conjugates; no low-rank adjoint
replacement is assumed. The special full F9 product happens to be symmetric.
Formula(4) places the odd denominator in the full-exit scalar map, while
formula(3) places it in the entrance recoding.

The dyadic scaled alternative

    13K=12I+U A U*                                  (5)

is kept separate. It avoids 1/13 inside that entrance matrix, but produces
a scaled offer until the scalar 13 is carried or normalized at a specified
boundary. It is not automatically the old uncoded supplier. Fixed odd
rational normalization, rounded division/constant multiplication, storage,
all intermediate coefficients and error propagation require a finite
Word-RAM protocol in the selected ABI. No universal impossibility is
inferred merely from the denominator 13.

## 3. Fourier grade and a finite phase quotient

Fix a finite-phase one-column Clifford group G on the declared ambient
address space, containing all source frames and all allowed gates. Let Z
be its scalar subgroup. Let H contain Z and all admitted monomial
Cliffords. Free owner controls may have arbitrary coefficients over the
subgroup algebra B_f. This grants more owner mixing than a fixed finite
ADD schedule. Non-Clifford monomials and noncolumnwise width-specific
address operations are outside this grammar.

At width f impose z=ζ^f for every scalar z=ζI. The resulting twisted
algebra A_f has one basis class per projective group element G/Z over a
characteristic-zero splitting field. No domain assumption is needed.
The Fourier grade of a pure Clifford is the binary rank of its Z-to-X
symplectic block. Scalar phases do not change grade. Multiplying on either
side by a monomial Clifford preserves grade. Consequently the basis
projection pi_2 retaining exactly grade 2 words is a B_f-bimodule map:

    pi_2(b a c)=b pi_2(a)c,       b,c in B_f.         (6)

Grade is not asserted additive under general Clifford multiplication.
All actual phases remain in the quotient multiplication.

For completeness, this algebra faithfully evaluates into the literal
columnwise tensor action at every sufficiently large f. Choose matrix
representatives v_t for G/Z. For each t and other u, a linear functional
can vanish on v_u and not v_t because they are nonproportional. The product
of these functionals isolates v_t in homogeneous degree |G/Z|-1. Multiplying
by a power of a functional nonzero at v_t extends the isolating polynomial
to every larger degree f. Applied to v_t^⊗f, it proves linear independence
of the projective representatives' tensor powers, with the scalar character
ζ^f retained. Thus an all-positive-width exact operator identity implies
the algebra identity at all sufficiently large widths, even when owner
coefficients depend on f. No width-1 independence of Clifford matrices,
phase deletion or tensor power of an operator sum is used. The scalar code
A remains owner mixing at each width; it is not replaced by A^⊗f.

## 4. The one-bank theorem

The checker classifies all 5824 supported pairs of the actual code. For
each nonzero A_ij, i differs from j and U_i U_j* has Fourier grade 2.
Together with A_ii=0, equations(2)-(3) give

    K=(12/13)I+(1/13)U A U*,
    pi_2(K)=(1/13)U A U*.                           (7)

The latter matrix is invertible over A_f: U and A are invertible, with
phases retained. As a K-linear operator on the regular module A_f^112,
it has rank 112 dim(A_f). The backward adapter K_B is also invertible with
every supported entry of grade 2. Scaling 13K preserves the same projected
rank. The scalar rank-8 of P does not provide eight native observation
oracles in heterogeneous input charts; coefficient projection pi_2 can
increase the ordinary operator rank of a low-rank update.

Consider only a standalone exact adapter made from free B_f-valued linear
pre/post controls and ONE parallel bank D of pure Gaussian Clifford
operations, with identities on other channels. Rectangular boundaries,
zero scratch, free saved-input bypass, copies or output selection may be
granted. Let r be the number of grade 2 channels in D. Other grades have
zero pi_2 projection. A free bypass has zero grade 2 projection. By(6),

    pi_2(L D R + B_0)=L pi_2(D) R,       B_0 over B_f.

Each retained diagonal grade 2 entry is a group unit. On the regular module
pi_2(D) therefore has rank r dim(A_f); rectangular pre/post maps cannot
increase it. Equation(7) requires

    r >=112.                                        (8)

An H1-only parallel bank cannot realize K. A bank with other grades still
needs 112 grade 2 channels. This is a theorem about the specified exact,
fixed finite columnwise alphabet. It does not address approximate/border
endpoints, chronological multiple banks, absorbing a conversion into
existing native operations, source-prefix access, nonlinear controls or a
changed direct coded consumer.

## 5. Complete optimistic tariff screen, not a constructed endpoint

Grant, without an endpoint certificate, 224 independent H17 main targets
and all 816 original helper targets from two coded source calls. Their raw
margin at C=.0030217758 is

    166.262158203082210620506138658847..848,

and at C=.0034 it is 159.070799023745749761534310198754..755. Subtracting
112 H2, as forced for even one standalone bank by(8), gives respectively

    -57.269156882594712940928576503039..038,
    -64.401921647290247704383966403396..395.

The naive224 H1 route also loses. Exact rational intervals, profiles and
sign controls are regenerated in RESULT.json from the vendored interval
engine. For each stated bill, negative signed coefficients have ranks at
most5 and positive coefficients ranks at least7. Its normalized moment
M(t)/5^t is strictly increasing in t=1-C. Negativity at the funded lower-C
endpoint excludes the full interval through .0034. This does not price a
realized caller or establish its uniform compiler reserve.

The stronger three-original-bank offer 336 H17+2H-224 H9 has 928 owners and a
positive raw relaxation, but its third H17 job is unproved. The known
#4698 pattern has a third H16 job and already loses even with free embedding.
A_ii=0 and the nonuniform physical headers prevent substituting either
old one-port template into the new code without a new all-input operator
identity. These distinct models are recorded explicitly in RESULT.json.

For the frozen 18-FULL/15-query caller, a literal interface-preserving
replacement would change its paid profile by -144H8+K_added, retaining
its old query/IDLE costs and productive targets. That formula is conditional
on a chronological endpoint with every new adapter and resource counted.
The code does not automatically commute through port-dependent entrance
maps or standardized Q/native letters. No such amortization is proved.

## 6. Admission and credit boundary

The local Gaussian children and independent helper targets retain their
source phase/ownership contracts. The coded cross-transfer is changed.
The old 18-FULL word, its rank-145 productive endpoint, finite template
constants, 54 strict outer predicates and 4 functional guards do not bind
merely by replacing P in a dictionary. A complete Gaussian endpoint,
actual scalar/routing/storage word, prefix AND suffix/error bounds,
odd-denominator protocol, uniform compiler gap and ordinary BIT/outer
admission must be newly supplied. No κ is claimed here.

Credit Dugongue for the exact native coded producer, Cinna Davis/1337isnot1337
for #4694/#4698, Cao Yifan/intqwq for the retained round-three source and
#4610, and the retained native, Clifford, helper, compiler and outer
contributors. The parent agent derived the one-bank projection/rank
argument and exact price screen; the source/interface agent independently
bound the physical adapter, all supported grades and raw-dual formula.
The proof and portable checks were prepared for Chris R/Clear1nsight with
substantial OpenAI Codex assistance. Apache-2.0. Independent agent review
is separate from independent human or formal proof-kernel acceptance.
