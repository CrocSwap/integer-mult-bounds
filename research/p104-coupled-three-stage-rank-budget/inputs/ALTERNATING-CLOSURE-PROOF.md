# All-length obstruction for the fixed alternating interior

No new kappa is claimed. This theorem concerns the explicit alternating
interior in boundary_curvature.py. It does not classify all longer callers.

For every even n>=4 and every positive coupled width q, no pair of compatible
rank-2q positive boundary projectors turns this fixed interior into a
constant conjugate of independent monomials in the common formal stage z.
The query identity can hold; the independent stage endpoint cannot.

## Curvature condition

Write W(z)=I+(z-1)H+(z-1)^2 W_2+... . A constant monomial endpoint has
H=C diag(d_j) C^(-1) and 2W_2=H^2-H. For a product of projector stages,
this condition is equivalent to

    sum_(i<j) [P_i,P_j] = 0.

The first and last projectors range over the complete compatible block
charts. All interior projectors are the explicit scalar matrices tensored
with I_q. Every scalar chart parameter may be an arbitrary q-by-q matrix.

## Small lengths: a cyclic trace certificate

For n=4,6,8,10, trace_curvature.py builds the curvature equations and the
boundary projector equations over the free associative algebra. Complete
matrix affine substitutions reduce the system. The retained certificates
combine these equations, with left multipliers of degree at most one, to
obtain the scalar constant 1 modulo cyclic rotations of words.

At every finite matrix width, cyclic rotations have the same trace. If the
matrix equations held, the certificate would give trace(I_q)=0. In
characteristic zero this says q=0, a contradiction. This is stronger than a
commutative Groebner contradiction; matrices are allowed to fail to commute.
The trace method is standard linear algebra. Its application and explicit
certificates here are new parts of this investigation.

The exact search rechecks its witness by direct rational addition. A failed
bounded search is not an impossibility result. The positive-boundary
certificates are in discovery-results/trace-n4-d1.json through
trace-n10-d1.json. Their source equations are reconstructed from the literal
projectors, not read from a numerical solver.

## All larger lengths: a rank argument

Put n=2m. For the k-th adjacent coordinate pair, use basis vectors
p_k=e_(2k-2)-e_(2k-1) and q_k=e_(2k-1). Write t_k=sum_(h<=k) p_h.
In this basis the k-th nonzero interior projector is block upper triangular.
Its two diagonal blocks are

    A_k=t_k e_k^T,       D_k=e_k t_k^T,

where the t_k in each diagonal block is the length-m prefix vector.
For the interior curvature C=sum_(k<l)[P_k,P_l], the diagonal blocks are

    C_A(i,j)=j-i for i<j, and zero otherwise;
    C_D(j,i)=-(j-i) for i<j, and zero otherwise.

Each has rank m-1. Select the first m-1 rows and last m-1 columns in C_A,
and the last m-1 rows and first m-1 columns in C_D. Their minors are
triangular, with diagonal 1 and -1. The corresponding block upper
triangular minor of C has nonzero determinant. Thus rank C >= (n-2)q.

Let H be the sum of the interior projectors. Adding the two boundary
projectors changes curvature by

    [P_0,H+P_n] + [H,P_n].

Each commutator with a rank-2q projector has rank at most 4q. Therefore
zero total curvature would require rank C <= 8q. For n>=12 this contradicts
rank C >= (n-2)q. This part does not require boundary compatibility.
It also applies if either boundary stage is inverse, since its sign only
changes the two commutators.

Together the finite trace certificates and the rank proof cover every even
n>=4 for positive boundaries. The inverse-boundary small cases are separate:
the n=4 and n=6 inverse cancellation examples are exact monomial endpoints,
although their bills are not favorable.

## Extra stages and remaining scope

Inserting extra stage projectors of total rank R changes curvature by a sum
of commutators with total rank at most 2R. Thus the fixed interior with two
rank-2q boundaries needs R >= (n-10)q/2 when n>10. This is a stage-rank lower
bound, not a paid invoice. Forward stages can change the productive powers;
those targets and all paid maps must be counted together.

An inverse-boundary word with this interior has another simple restriction.
Its z^(-2) coefficient is P_n B(0) P_0. The first interior projector fixes
U_0, so B(0)U_0=0. Since image(P_0) contains this q-dimensional query image,
rank(B(0)P_0)<=q. Therefore at most q independent targets can have power -2.
The initially tested ten-field profile with two such targets per port fails
this cut. A revised signed profile is retained as a separate search.

## Complete gate at the selected exponent

The same-sign inverse certificates for n=8 and n=10 are also retained.
For n=4 and n=6, inverse cancellation can give monomial endpoints; these
examples are controls and are not excluded by those larger-case proofs.

The fixed interior has n=2m and m full calls. Let b be the number of full
boundary calls, with b=0,1,2. The other boundaries are thin. Thus F=m+b
and the total thin count is m+1-b. Each full boundary can be forward or
inverse. The following cases close this fixed family at the selected
exponent 781451/250000000 and the selected PR6030 local source profile:

- n>=12: curvature rank excludes every b and every boundary orientation.
- n=8 or n=10 with b<=1: curvature rank is at least (n-2)q, but the
  boundary correction has rank at most 4bq. No monomial endpoint exists.
- n=8 or n=10 with b=2 and equal signs: the retained trace certificates
  exclude every coupled width.
- n=8 or n=10 with opposite signs: the only inverse boundary gives a
  simple pole. Its coefficient has rank at most q, since B(0)U_0=0 for
  an initial inverse, or V_n B(0)=0 for a final inverse. Hence the total
  negative target degree is at most q. The determinant gives signed
  degree nq, so total absolute degree is at most (n+2)q. Even crediting
  full linear rank mass, the price margin is below -1563 for n=8 and
  below -1528 for n=10 at q=104.
- n=2,4,6: for every b and orientation, the total absolute stage degree
  is at most 2Fq. This follows by applying the exterior-degree bound at
  zero and infinity to the positive and inverse projector factors.
  Concavity makes the favorable integer degree profile as balanced as
  possible. All nine resulting price upper bounds are negative. The
  least negative one is below -8.437 for n=6,b=2.

The productive Gaussian rank of a stage power e is credited by the favorable
upper bound 8|e|+1. Unknown extra costs are omitted. Independent helper
outputs retain their full source credit. These choices favor the caller.
They do not assume a free physical implementation of its output charts.

price_check.py authenticates the retained selected source certificate and
recounts its paid and helper profiles. It encloses r^(1-kappa) with rational
logarithm and alternating exponential series. All reported signs are exact
rational signs. The separate price bound does not rerun the native source,
selected caller, compiler or outer theorem.

This closes the fixed alternating-interior family on the selected 104-port
source and on whole copies of that source. Zero, one or two full boundaries,
either orientation and arbitrary compatible boundary projectors are allowed.
The algebraic exclusions hold at every positive coupled width; the price
bounds use the stated source invoice and its homogeneous whole-copy scaling. It does not exclude a changed
interior, extra queries, owned work, extra stage maps, noncentral native
coefficients or finite-period endpoints that do not lift to formal z.
No kappa improvement is claimed.

## Open next questions

The fixed ten-field inverse-boundary profile is now excluded by its trace
certificate. Can a changed interior or an extra query give a better
endpoint at a favorable full price? Can the nonformal order-six contract
escape the polynomial curvature condition? Those are different questions.

Credit Cinna Davis and the retained query/native/caller lineage, and the
PR6168 normal-form proof. New application, trace certificates and rank
argument: Ali Romman with substantial OpenAI Codex assistance. No subagents.
Apache-2.0. Independent scientific review is pending.
