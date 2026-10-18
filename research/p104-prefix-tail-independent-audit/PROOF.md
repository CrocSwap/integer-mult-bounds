# Independent mathematical audit of the PR2358 rank certificates

Run: `trial-20261015-0634`. Scope: the rational pooled-snapshot model stated
in PR2358 at `e8950db523c9682518049a42cfc28642224292ff`, with its README, certificate and source inspected. This is an AI-assisted independent written
mathematical audit, not human review or a formal-kernel proof. No source
trace replay is claimed in this note; that independent finite obligation
belongs to the parent trial. No code outside this note was changed.

**Finding:** the stated reduction and the two determinant arguments are
correct under the stated trace premises. The explicit cut-2754 residual
has rank exactly two. I found no algebraic counterexample to the stated
rational theorem. Availability and complete pool coverage remain finite
source-bound obligations, rather than consequences of these identities.

## Model and necessary projection hypotheses

Work over Q. Let V=X direct-sum Z, with X=Q^104 the source coordinates
and Z=Q^176 the independent initial target/helper nuisance coordinates.
For target t, let z_t denote its own target dirt coordinate. The trace
premises needed for the projection are:

1. Every eligible donor has zero z_t coefficient.
2. All 175 coordinate units in Z other than z_t lie in S_t(0), hence
   in the monotone pooled space S_t(c).
3. Every source projection of an eligible donor lies in row(R), where
   R is the stated 8-by-104 rational matrix satisfying RR^T=104 I_8.
4. Correction rows C_t lie in X, with C=I_104-R^T R/8.

These hypotheses use all independent dirty columns, not clean-input
specialization. For any s in S_t(c), its nuisance component belongs to
span{z_j:j != t}, which is contained in S_t(c). Subtracting that component
proves pi_X(s) in S_t(c) intersect X. The reverse containment follows by
projection, so pi_X(S_t)=S_t intersect X.

If C_t=s_t+h_t with h_t in a shared space H, projection gives
C_t=pi_X(s_t)+pi_X(h_t). Therefore pi_X(H) serves the same rows, lies in X,
and has dimension at most dim H. Conversely source-only H is allowed in
the original optimization. Thus optimization over all 280 coordinates is
exactly optimization over source-only shared spaces. This explicitly covers
arbitrary nuisance components in the original H.

The implementation's initial-state construction gives independent nuisance
unit rows. Its initial-frame checks put all 176 nuisance registers together
in the zero frame and all source registers in rank-one frames; hence for
each Y_t the other 175 nuisance units are eligible at cut zero. Its donor
checks test absence of the target's own dirt. These are the right checks;
the parent's independent replay must establish them on the actual pins.

## Minimum-rank reduction, including signs and factors

Put L_t={a in Q^8 : aR in S_t intersect X}. Since RR^T=104 I_8,
the coefficient a of any projected row v=aR is unique and equals
v R^T/104. This agrees with the WITNESS contact convention.

For any choices a_t in L_t, form A with rows a_t. The rows of
K=C+12 AR serve C because K_t-C_t belongs to S_t. Conversely, for any
serving source-only H choose C_t=s_t+h_t; write s_t=b_t R, and choose
a_t=-b_t/12. Then K_t=h_t. Taking row spans in both directions proves

    h(c) = min_{a_t in L_t(c)} rank(C+12 AR).

The factor -1/12 is legitimate because L_t is a rational linear space.
There is no clean-state, positivity, integrality or bounded-coefficient
restriction in this model. If one added such restrictions, this step would
require a different argument.

Set D=R^T/8-12 A. Then K=I_104-DR and

    RD=13 I_8-12 RA,
    I_8-RD=-12(I_8-RA).

For any rectangular D,R, the maps R and D restrict to inverse linear maps
between ker(I_104-DR) and ker(I_8-RD): if DRx=x then RD(Rx)=Rx and
D(Rx)=x; the reverse direction is identical. Hence

    rank K = 104-nullity(I_8-RD)
           = 96+rank(I_8-RD)
           = 96+rank(I_8-RA).

Writing r_t for column t of R, RA=sum_t r_t a_t. Independent choices of
the rows a_t imply that the set of attainable RA is exactly
E(c)=sum_t r_t L_t(c), also described as the span of all pool generators.
Thus the stated minimum-rank formula follows for every rational A, not
merely the two supplied witnesses. The optimization minimum exists: the
attainable set is nonempty and ranks take finitely many integer values.

## Universal compression lower bounds

Use the vectors p,q,w,a,b,k stated in the README. For a generator
M=r_t alpha, each functional factors exactly as

    left^T M right = (left^T r_t)(alpha right).

Consequently checking its vanishing on every generator proves vanishing
on all of E(c), including arbitrary rational linear combinations.

For N=I-M, the three persistent equalities give the compression

    [p^T; q^T] N [a b] = [[0,-1],[-1,s]],

whose determinant is -1 for every rational s. Multiplication by the two
compression matrices cannot increase rank. Therefore rank N >= 2.

At cut 2753 the three additional k equalities imply

    [p^T; q^T; w^T] N [a b k]
       = [[0,-1,0],[-1,s,0],[u,v,2]],

whose determinant is -2 for all rational s,u,v. Thus rank N >= 3.
There is no requirement that either compression matrix be square or
invertible; the exhibited nonsingular compressed minor suffices.

Because pools are monotone, the second bound holds at every earlier cut,
and the persistent bound holds through 2823. With the cut-2646 rank-99
witness available thereafter and the cut-2754 rank-98 witness available
thereafter, these imply 99 on [2646,2753] and 98 on [2754,2823], conditional
on those witnesses' exact membership and rank. The advertised [2718,2753]
is a weaker subinterval. In particular no earlier cut can have h<=98.

## Explicit new residual and sharpness of the third constraint

Let x=-e2+e3+e7 and alpha=e1+2e7. The displayed matrix

    N=x alpha^T-e1 e2^T

is a sum of two rank-one matrices, so rank N<=2. Direct multiplication
with the stated vectors gives

    [p^T; q^T; w^T] N [a b k]
       = [[0,-1,0],[-1,0,-2],[1,0,2]].

Its upper-left 2-by-2 determinant is -1, so rank N=2; its full determinant
is zero. In particular q^T N k=-2 and q^T M k=2, while p^T N k=0 and
w^T N k=2. The cut-2753 third-column condition cannot extend to this N.

The README expression, the code's outer-product expression (using -e1 as
the second left vector), and this calculation have identical signs and
index conventions. The 46 contact terms must still independently sum to
this expression on the pinned original trace; this note does not infer
that membership from the expression alone.

## Independent arithmetic checks and useful defect controls

A standalone Python calculation using only fractions.Fraction and explicit
8-vectors, with no imports from the source package, recomputed the displayed
3-by-3 compression exactly and its determinants (-1 for the leading minor,
0 for the whole new compression). The general determinant formulas above
are written algebraic proofs; checking several rational free entries was
only an arithmetic sanity check, not their quantified justification.

The following are exact premise-sensitive controls:

* Delete the fixed zero in the 2-by-2 compression: N=(e1+e2-e7)(-e0)^T
  has compression [[-1,-1],[-1,-1]] and rank one. The two fixed off-diagonal
  entries alone do not certify rank two.
* Delete the q^T N k=0 premise in the 3-by-3 argument: the actual new N above
  satisfies every other displayed fixed entry but has rank two.
* Delete the fixed nonzero third diagonal entry: N=x e1^T-e1 e2^T has
  compression [[0,-1,0],[-1,0,0],[1,0,0]] and rank two.
* Delete nuisance-unit availability or allow own-target dirt in donors:
  already with X=Qx, Z=Qz, S=span(x+z), one has pi_X(S)=Qx but
  S intersect X=0. For C=x, projected local availability would incorrectly
  predict h=0, whereas the original space needs h>=1. This proves why
  projection cannot be assumed solely from source-row containment.

## Exact scope and unresolved implications

The algebra above is an all-rational written proof under explicitly listed
premises. It is not a formal-kernel proof. The finite source obligations are:
the exact root ordering and tight-frame identity, every eligible snapshot's
source-row membership and own-target-dirt absence, all pool generators for
the two lower endpoints, and all fixed witness contacts and their residual
sum. Source inspection shows checks for these obligations, but inspection
does not replace the parent's independent source-bound replay.

There is no precision or coefficient-height admission claim here. Rational
pooling allows free basis changes and access across different times. It does
not establish chronological execution, source-read charges, preservation of
later snapshots after insertions, creation/restoration of complement rows,
ownership or hosting, transport costs, an all-size supplier, or a new kappa.

Although arbitrary rational minimum-rank problems need not have the same
minimum over larger fields, these particular intervals would also have the
same values over any characteristic-zero field extension, if the model is
defined by scalar extension of these same rational pools: the compression
lower bounds still apply and the attaining rational witnesses remain valid.
This observation is conditional on the same finite trace premises; no
positive-characteristic or changed-construction claim is made.

## Addendum: independent review of the parent's audit implementation

Reviewed
`trial-20261015-0634/research/p104-prefix-tail-independent-audit/verify.py`
after the parent reported a passing pinned full replay (4,059 cuts, 280
columns, 110,814 target/snapshot pairs, pools 324/427, upper ranks 99/98).
This addendum reviews mathematical coverage of that implementation; the
reported full rank/certificate execution belongs to the parent. I separately
executed its trace replay to check the contact coefficient types below.
**No mathematical blocker found for its fixed pinned inputs and certificate.**

* `rank()` is a correct exact forward row-echelon algorithm. Each stored
  row has zero entries strictly before its stored pivot. The existing rows
  are used in increasing pivot order, so eliminating a pivot never
  reintroduces an earlier pivot. The new row is zero at every existing
  pivot, hence its first nonzero coordinate, if any, is a new pivot. This
  remains true when pivots are inserted out of order. Normalization and
  backward elimination are unnecessary for counting rank. All actual
  caller matrices have fixed rectangular widths (8 or 104), so the lack of
  a generic ragged-input guard does not affect this pinned computation.
* `frame()` first constructs a binary echelon basis with distinct highest
  bits. Its ascending pivot cleanup removes each lower pivot from every
  higher pivot row. Lower rows have already been cleaned at that point,
  so this gives the unique reduced basis of the binary subspace, returned
  in descending pivot order. `inside()` then correctly reduces against
  that descending basis. Exact frame equality is therefore equality of
  binary subspaces, not equality of an arbitrary presentation.
* Every event checks scalar donors against the destination and the event's
  declared binary frame. Source-code membership is a separate condition
  checked in `projection()`; the implementation does not confuse scalar
  common-frame eligibility with membership of a source row in row(R).
* `inspect()` rebuilds current frame groups at every cut and visits every
  eligible donor before considering `(target,row_id)` reuse. A row ID
  represents the complete immutable rational row, including all nuisance
  columns. Own-target-dirt absence and source projection depend only on
  that row, so reusing an already inspected pair cannot skip a changed
  mathematical value. A changed frame can affect present eligibility,
  but cannot create a new pooled row when the same target/full-row pair
  was already eligible at an earlier cut. This use of reuse is exact.
* All initial nuisance rows are independent units in the common empty
  frame, so nuisance lifting is justified. Every requested contact's
  exact-cut eligibility is checked separately. It was also visited by
  that cut's generic inspection, which either checks its own-target dirt
  directly or reuses the same previously checked full row. Thus the
  contact-specific path need not duplicate the dirt assertion.
* Root reconstruction and the exact tight-frame identity fix the source
  coefficient map. The upper witness forms A from the replayed contacts,
  checks both small and full ranks, and checks the exact displayed new
  residual. The lower routine tests the required generator functionals
  and constant compression entries. The SHA256 certificate pin fixes
  the intended cuts, target indices, vector lengths and witness entries;
  this code is a fixed-evidence auditor, not a general certificate-schema
  validator. Source-file hash verification supplies its other fixed inputs.

Independent small arithmetic controls were executed against the parent's
`frame`, `inside`, and `rank` routines, with reference results constructed
without those routines: 2,746 ordered independent binary frame fixtures in
four bits, all 66 subspaces of dimension at most three and all their
containment pairs, dependent fixtures rejected, and all 729 two-by-three
matrices over {-1,0,1} ranked by an independent exact-minor criterion in
both row orders. All passed. These controls supplement the written
all-dimension echelon arguments; they do not exhaust nine-bit frames or
104-dimensional matrix ranks.

One harmless arithmetic detail: a row having no source entries yields
floating zero coefficients through Python's `0/104`; any row with a
source entry yields Fractions in every coordinate. These floating values
are exactly zero, fail `any(alpha)`, and cannot enter a nonzero projected
pool. I independently executed the parent trace replay and checked that
all 49 distinct fixed upper contacts have nonzero source projections and
every coordinate is a Fraction; hence the fixed upper calculation cannot
encounter these floating zero tuples. Their arithmetic cannot introduce
rounding error into this result. For a changed certificate, a zero-projected
contact following a nonzero contribution to the same target could coerce a
nonzero Fraction sum to float, so generic acceptance would require attention.
Using `Q(0)` as the sum initializer enforces a uniform exact representation,
but is not a correctness gate for these fixed pinned contacts.

Parent repair after review: the projection sum now starts with Fraction(0), so source-empty rows also retain exact Fraction coordinates. The final registered replay and controls were rerun after this repair.
