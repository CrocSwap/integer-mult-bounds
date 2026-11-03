# One prescribed map and two target capacities

## Contract and computable criterion

Let V and W have the same finite dimension over an arbitrary field F. Let
h:U→W be injective, with image E. Let A,B⊆V and C,D⊆W be arbitrary subspaces;
no nesting is assumed. Every inclusion here allows equality. We seek an
isomorphism g:V→W extending h with g(A)⊆C and g(B)⊆D.

Set I=A∩B, UA=U∩A, UB=U∩B, U0=U∩(A+B), and

    Z = (E∩C)+(E∩D),              X = h(U0)∩Z,
    a = dim A−dim UA,             b = dim B−dim UB,
    s = dim(A+B)−dim U0,
    c = dim C−dim(E∩C),           d = dim D−dim(E∩D),
    t = dim(C+D)−dim(E∩(C+D)),
    k = dim I+dim X−dim UA−dim UB,
    ell = dim(C∩D)−dim(E∩C∩D).

The required isomorphism exists **if and only if** all seven conditions hold:

    h(UA)⊆C,       h(UB)⊆D,       h(U0)⊆C+D,
    a≤c,           b≤d,            s≤t,
    k≤ell.

The last condition is coupled compatibility, rather than another independent
capacity test. This result settles the two-target question in Nick Petalas's
PR6489 README question1. The predecessor settles nested target flags and their
completion count; it is not being reproved or claimed as new. We do not give a
formula counting every completion for arbitrary nonnested targets.

## The coupled quotient map

Let π:W→W/E. Write Cbar=π(C), Dbar=π(D), T=Cbar∩Dbar and H=π(C∩D). Put

    R = (E∩(C+D))/Z.

There is an exact sequence of vector spaces

    0 → H → T --rho--> R → 0.

For v∈T choose c0∈C,d0∈D with π(c0)=π(d0)=v and define
rho(v)=[c0−d0]. This difference lies in E∩(C+D). Changing either representative
changes it by an element of Z, so rho is well-defined and linear. Every
member e∈E∩(C+D) can be written c0−d0, so rho is onto. If c0−d0=zC+zD with
zC∈E∩C,zD∈E∩D, then c0−zC=d0+zD lies in C∩D and has coset v. Thus ker rho=H.

In V/U put Abar=(A+U)/U, Bbar=(B+U)/U and J=Abar∩Bbar. Under the three
compatibilities in the criterion, define

    delta:J→R,   delta(a0+U=b0+U)=[h(a0−b0)],   a0∈A,b0∈B.

The difference belongs to U0. Replacing a0 by another representative in A
changes it by UA, and similarly for B and UB. Their prescribed images lie in
E∩C and E∩D, hence in Z; delta is therefore well-defined and linear.

Its image is precisely the image of h(U0) in R. Indeed every u∈U0 has a
representation a0−b0 with a0∈A,b0∈B, and these define a member of J. Therefore

    rank delta = dim U0−dim X,
    dim J = a+b−s = dim I+dim U0−dim UA−dim UB,
    dim ker delta = k,                 dim H = ell.

These formulas also show k is nonnegative under the stated compatibilities.
No characteristic restriction or finite-field genericity is used.

## Necessity

If g exists, its restriction to UA, UB and U0 gives the three compatibility
conditions. It induces an injective quotient map from V/U to W/E. This map
sends Abar into Cbar, Bbar into Dbar and their sum into Cbar+Dbar, giving the
three dimension capacities.

Restrict that quotient injection to J, calling it j0:J→T. For representatives
as above, g(a0)−g(b0)=h(a0−b0), so rho∘j0=delta. In particular j0 maps
ker delta injectively into H=ker rho. Consequently k≤ell. This proves every
condition is necessary.

## An injective common lift

Conversely assume all seven conditions. Split J=ker delta⊕J1. Inject
ker delta into H, which is possible because k≤ell. Since rho is onto,
lift delta(J1) through a linear section of rho. On J1 the map delta is
injective, so these lifted vectors are independent modulo H. Together these
two choices give an injective map j0:J→T with rho∘j0=delta. Write L=j0(J)
and j=dim J. In particular j≤dim T.

We next extend j0 to an injection fbar:Abar+Bbar→Cbar+Dbar respecting both
capacities. Let tau=dim T. Choose complements of T in Cbar and Dbar. Their
images in (Cbar+Dbar)/T are disjoint, of dimensions c−tau and d−tau.
After fixing L, the unused common space has dimension tau−j. The additional
source dimensions are a−j and b−j. Their minimum requirements on this common
space are

    rA=max(0,a−j−c+tau),    rB=max(0,b−j−d+tau).

The three capacity inequalities imply rA+rB≤tau−j. If both are positive,
this is exactly a+b−j≤c+d−tau, namely s≤t. If only one is positive, its bound
follows from a≤c or b≤d. Assign disjoint basis slices of T/L of sizes rA,rB,
and use the separate complements for the rest. Lifting these choices gives
fbar. This is an ordinary basis construction over every field, including
small finite fields; it does not require a generic choice to exist.

## Lift and glue with the prescribed map

Choose paired representatives a_j∈A,b_j∈B for a basis of J, so a_j−b_j∈U.
Choose representatives c_j∈C,d_j∈D of fbar(j). The equality
rho(fbar(j))=delta(j) says

    c_j−d_j−h(a_j−b_j) ∈ Z.

Write that discrepancy as zC+zD with zC∈E∩C,zD∈E∩D. Replace c_j by c_j−zC
and d_j by d_j+zD. Their quotient images stay unchanged and now
c_j−d_j=h(a_j−b_j) exactly.

Choose complements to UA in A and UB in B whose images split into the common
J basis and separate quotient complements. On U use h, on each paired
representative use the adjusted c_j,d_j, and on the separate complements use
arbitrary lifts in C or D of the corresponding fbar vectors. The displayed
relations ensure the definitions agree on U+A+B; all cross-relations modulo
U occur in J, while the relations already in U are prescribed by h. Thus this
defines a linear map f:U+A+B→W with f|U=h, f(A)⊆C, f(B)⊆D.

Its quotient map is fbar. If f(v)=0, quotient injectivity forces v∈U, and
injectivity of h then forces v=0. Finally extend the domain and image bases
to bases of V and W. The resulting isomorphism is the requested g. This
proves sufficiency and describes a constructive basis procedure. The finite
software below checks the criterion; it is not a production general-field
implementation of this construction.

## An oblique three-dimensional obstruction

Over any field take V=W=F³, U=E=<e1,e2>, h=identity, and

    A=<e1+e3>,     B=<e3>,
    C=<e1,e3>,     D=<e1,e2+e3>.

The individual, sum and ordinary source-intersection dimensions pass, as do
all three prescribed-image compatibilities and the naive common quotient
capacity dim J≤dim T. Here a=b=s=c=d=t=1, dim J=dim T=1. But
Z=<e1>, h(U0)=<e1>, delta=0 and H=0. Hence k=1>ell=0.

Directly, any joint completion would send e3 to D, while e1+e3 must go to C
and e1 is fixed. Thus g(e3) lies in C∩D=<e1>⊆E, contradicting injectivity
because e3 is outside U. Each individual request is feasible: choose the
image of e3 outside E in the corresponding plane. The failure is genuinely
the coupled prescribed-map condition, not the earlier flag obstruction.

The opposite calibration is also useful. In F² take U=<e1−e2>, h=identity,
A=C=<e1>, B=D=<e2>. The identity is a completion. Here dim J=1 and H=0,
but delta has rank1, so ker delta=0 and the correct test passes. Requiring
all of J to fit in H would incorrectly reject this case.

## Reuse checks and finite evidence scope

For U=0 the criterion reduces to the individual, sum and intersection
dimension conditions for two subspace capacities. For C⊆D, rho=0 and
H=T=πC; the kernel condition follows from a≤c, and the remaining tests are
exactly the two-stage nested cumulative-source tests of PR6489. If D=W,
the criterion reduces to the one-capacity prescribed-map contract of PR5020.
These are algebraic sanity checks, not new predecessor results.

Every injective h of rank r can be put into the standard identity on the
first r coordinates by independent domain and codomain basis changes. The
finite checks fix that canonical h and vary ALL FOUR subspaces. This covers
all instances in each stated finite domain up to those basis changes; it is
not a census counting every differently labelled prescribed h.

The primary uses row reduction and precomputed subspace sums/intersections.
The separate checker uses literal vector sets and complete invertible-matrix
enumeration, with no primary or predecessor executable imports. Their finite
agreements corroborate the algebra; the all-field conclusion rests on the
proof above. Exact finite census sizes and controls are retained in the receipts.

## Attribution and limits

Nick Petalas/6489 supplied the nested theorem and explicit two-nonnested-target
question. Brian/JoyboyBrian/5020 supplied the one-capacity question; Cao Yifan/
intqwq/4610 supplied the native-map caller context. Retain Nick Petalas/4919,
codyw912/4735, Cinna Davis, Dugongue, zxv, Jacob Alan Sussman and the source
native/compiler lineage. Quotients, linear lifting and basis extension are
classical; no general literature-priority claim is made.

This is unrestricted GL feasibility. It supplies neither a symplectic/native
operator nor an absolute phase, causal access, dirty restoration, basis
preparation, delivery, productive debit or complete paid invoice. Precision,
stock, tapes, compiler, outer admission and all five framework assumptions
remain open. There is no new kappa or selected-frontier change, human acceptance
or formal proof-kernel certification.
