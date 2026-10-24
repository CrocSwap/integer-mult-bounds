# Exact mixed middle-factor optimum

Work over F2. Let S,T,H be diagonal r by r matrices. Every diagonal triple
(s_i,t_i,h_i) is either zero or one of the seven nonzero binary triples.
Let E be the coordinate subspace on the d nonzero triples, and let k count
the pure-central triples (0,0,1). Consider finite n and matrices

    X,U : F2^n -> F2^r,       Y,V : F2^r -> F2^n

with all X columns and all Y rows nonzero, E contained in im X and in the
row space of Y, and

    XY=0, UY=S, XV=T, UV=H.                         (1)

The exact minimum is

    n_min = 2d+k+[d=k=1].                          (2)

For d=0 the empty factorization attains zero. The written theorem permits
all finite r and d. The executable constructor is deliberately bounded to
64 active roles and two additional dirty identity roles.

This is an exact necessary coefficient relaxation. A column gives a nonzero
rank-one middle coupling x_j y_j^T, but U and V need not come from preceding
and following paid chronological paths. No formal group-algebra word follows.

## Lower bound, credited premise restated

This is the mixed quotient argument from Nick Petalas #2175, using the
mixed active-span constraints from Gareth Davidson #2027 and ToikY #1662's
central quotient method. It is restated to specify the solved optimization,
not claimed as a new lower bound.

Let pi delete output coordinates where S has a one. Restrict the input to
ker T. Since XV=T, V(ker T) lies in ker X. Since UY=S, pi U annihilates
im Y. Since XY=0, im Y is contained in ker X. Therefore pi H restricted
to ker T factors through ker X/im Y. Its rank is exactly k, as the only
surviving diagonal ones have s=t=0 and h=1. Thus

    k <= n-rank X-rank Y <= n-2d.

At d=k=1, n=3 would force both ranks to equal one. Over F2 all nonzero
X columns are the same vector x and all nonzero Y rows the same row y.
Then XY=3xy=xy is nonzero, a contradiction. Thus n>=4 in that case.
This binary exceptional case is inherited from ToikY #1662.

## New step: mixed blocks attain the lower bound

Direct sums preserve all four equations, nonzero columns and rows, and the
active-span constraints. The task is therefore to allocate small blocks
without paying a four-column singleton for an isolated pure-central role.

For a single noncentral triple (s,t,h), use X=Y^T=(1,1). Choose two-entry
binary rows U and V^T with sums s and t and dot product h. Such rows exist
whenever (s,t) differs from (0,0): if s=1 choose U=(1,0) and V=(h,t+h);
if s=0,t=1 choose V=(1,0) and U=(h,h). This costs two columns.

The following new five-column blocks pair one pure-central coordinate with
any one of the six noncentral coordinates. Encode a two-vector (a,b) by
a+2b. In every row of this table set

    X columns = (1,1,1,2,3), Y rows = (1,1,2,2,2).

The targets are S=diag(0,s), T=diag(0,t), H=diag(1,h).

| (s,t,h) | U columns | V rows |
| --- | --- | --- |
| (0,1,0) | (0,0,1,0,1) | (0,1,0,3,1) |
| (0,1,1) | (0,0,1,2,3) | (0,1,0,3,1) |
| (1,0,0) | (0,0,1,0,3) | (0,1,1,0,0) |
| (1,0,1) | (0,0,1,0,3) | (0,1,3,2,2) |
| (1,1,0) | (0,0,1,0,3) | (0,1,1,2,0) |
| (1,1,1) | (0,0,1,0,3) | (0,1,3,0,2) |

Each equality in (1) follows by adding the five outer products over F2.
Both X and Y have rank two and no zero column or row. This is a finite
algebraic table, not a search failure or a chronological witness. #2175's
single z/uz fixture already establishes one member's attainability. We use
its X and Y and supply a uniform table for all six partner labels. Neither
that existing special case nor its lower bound is new credit here.

For completeness the pure blocks below are ToikY #1662's construction.
For two pure-central coordinates take X=Y^T with columns
(1,1,2,2,3,3). For three take columns (1,2,3,4,5,6,7,1,1).
In both cases XX^T=0, X has full row rank q, and n=3q. The q-dimensional
quotient ker X/im X^T has a basis. Take representatives as the columns of V,
and take U to be their dual functionals, vanishing on im X^T and extended
to the ambient space. Then (1) holds with S=T=0 and H=I_q.
The executable independently constructs representatives and duals by bounded
binary elimination. It does not import or run a predecessor program.

Now allocate the roles. If k=0, use noncentral singletons. If k>=2, write
k as a sum of twos and threes, use the inherited pure blocks, and use
noncentral singletons for the rest. This costs 3k+2(d-k)=2d+k.
If k=1 and d>=2, use one new five-column mixed block and d-2 noncentral
singletons, for 5+2(d-2)=2d+1 columns. If d=k=1, the inherited four-column
fixture is X=Y^T=(1,1,1,1), U=(1,0,0,1), V=(1,0,1,0)^T.
Zero-padding and simultaneous coordinate permutation place every block on
its original coordinates and preserve arbitrary identity-role coordinates.
This proves (2) for every finite diagonal target family.

## Consequence and limits

No strengthened mixed-root lower bound can follow from precisely (1), these
two span constraints, and the nonzero coupling restrictions alone. They are
already attained at 2d+k except for the inherited one-role exception. Any
stronger formal-word bound must retain further chronological or coefficient
information, or another constraint omitted from this relaxation. This does
not exclude stronger methods and does not decide any remaining UT4 word cost.

The pure-central endpoint, quotient/spans and single mixed fixture are
predecessor work. The contribution is the six-partner mixed construction
and its uniform allocation theorem, closing the general mixed relaxation.
No literature-priority claim is made for rank-nullity, direct sums or dual bases.

## Verification and code bounds

The checker multiplies the four binary matrices directly, checks all nonzero
couplings, both exact active spans, the formula and every zero-padded coordinate.
It exhausts all seven-label sequences through four active roles, then covers
larger mixed multiplicities and the 64-role boundary. A separate scalar census
enumerates every U,V through four columns to recover all seven scalar minima.
Semantic controls alter a mixed coefficient, delete a column and exchange the
target coordinates. Invalid labels, Boolean integers and out-of-range requests
reject. Normal and optimized execution use explicit exceptions, not assertions.

All loops have finite bounds. The largest construction has at most 192 columns
and 66 role coordinates. Pure-block searches enumerate at most 512 vectors;
the exhaustive family domain is fixed at d<=4. Functions remain below 60 lines.
Python and its standard library allocate dynamically; this is a documented
managed-runtime deviation from fixed allocation. Bounded input dimensions bound
the live mathematical arrays. No recursion, generated code or network is used.
Strict Python warnings are enabled in registered commands. No separate static
analyzer or proof kernel is claimed.

This contribution is produced by Nick Petalas. Credit ToikY, Gareth Davidson,
Nick Petalas, Aaron Wang, Josie Elliston, steph4n-gh, Arham Tahir, Hanson Sun,
and the retained formal register-model lineage in the pinned sources.
Apache-2.0. Independent human and formal proof-kernel review are unclaimed.
