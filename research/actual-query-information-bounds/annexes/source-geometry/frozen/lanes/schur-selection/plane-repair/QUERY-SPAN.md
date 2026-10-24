# Scalar source and response spans of payload queries

The actual eight-row centre query has 112 independent non-scalar
source directions when its inputs are plain fields. The same statement
holds for the proposed matched-plane version. This is an exact
representation statement. It does not give a native-child lower bound
for the full supplier, which also uses payload address maps and
sources that already have different phase encodings.

The theorem below also removes the common-negative-eigenspace premise
from the earlier controller query-count bound. Distinct actual plane
operators need not have a common negative sector. A linear functional
on operators is sufficient.

## The gate grammar

Let H be a finite-dimensional complex payload space. A state has a
finite number of fields, each with values in H. A scalar role map has
the form `B tensor I_H`, with arbitrary complex B. Such maps can be
singular. They include scalar additions, COPY and private CLEAR.
The initial input embedding and final output projection must also
be scalar role maps.

A payload query changes one scalar combination of fields by one
operator on H. It has the form

    L=I+u Q v,

where u is a scalar column, v is a scalar row, and Q is an operator
on H. Applying a payload operator P to one field is the case
`u=e_k`, `v=e_k^T`, `Q=P-I`. The Q operators at different queries can
be arbitrary and need not commute. A block query with r scalar
response directions is counted r times.

Every non-scalar payload operation must be counted or included in
an explicitly changed input/output contract. In particular an address
permutation is a payload query in this grammar. It is not a free
scalar role map, even when the native compiler gives it Fourier
rank zero. This distinction is essential.

## Two exact factorizations

After c queries, the input-to-state operator matrix M has both forms

    M=A tensor I+U V,       U scalar with at most c columns,
    M=A tensor I+W Z,       Z scalar with at most c rows.       (1)

The operator-valued matrices V and W in the two forms need not be
related. Extra private or borrowed fields do not change the claim.

Initially take A to be the scalar input embedding and take the
other factors to have size zero. A scalar gate B replaces A by BA,
U by BU and W by BW. It leaves the query count unchanged.

For the first form, a query gives

    LM=M+u Q v M
      =A tensor I+[U,u] [V; Q v M].                         (2)

Thus it adds at most one scalar response column. For the second form,

    LM=A tensor I+(LW)Z+u Q (v A tensor I)
      =A tensor I+[LW,u Q] [Z; v A].                       (3)

It adds at most one scalar source row. These equations preserve the
operator order. They do not commute Q through an earlier operator.
They also do not assume an invertible intermediate gate. A scalar
final projection or input restriction preserves both forms.

Let ell be any complex linear functional on operators on H with
`ell(I)=0`, and apply ell entrywise. Equations (1) give

    ell(M)=U ell(V)=ell(W)Z.                               (4)

For any finite collection of such functionals, all the resulting
column spaces lie in the same c-dimensional scalar response span,
and all their row spaces lie in the same c-dimensional scalar source
span. Consequently both the horizontal column rank and the vertical
row rank of these matrices are at most c.

This is a payload-query count theorem. A separate contract is needed
to turn that count into a native rank or primitive-operation cost.

## The actual line-centre query

The pinned supplier matrix R has eight rows and 112 columns. It
satisfies `R R^T=56 I_8`. Every column is nonzero. Its 112 actual line
labels q_p are distinct and nonzero.

Use the exact phase convention

    C_q=a I+b X_q,
    a=(1+i)/2, b=(1-i)/2,
    C_q^-1=b I+a X_q.                                    (5)

For a physical input `X_p=C_(q_p) x_p`, the centre Rx is the operator
query

    G=R diag(C_(q_p)^-1)                                 (6)

on the physical X fields. The same argument applies to the positive
phase version `R diag(C_(q_p))`.

For each p, let ell_p be the spatial matrix entry
`<q_p|operator|0>`. It kills I and all the other line translations.
Applied to (6), it gives a matrix whose only nonzero column is p,
equal to `a R[:,p]`. For the positive phase it is `b R[:,p]`.
Choose one nonzero entry from each R column. The 112 selected rows
of the stacked functional matrices form a nonzero diagonal minor.
After the common Gaussian scalar is removed, every diagonal entry
is 1 or -1. Thus the scalar source rank is exactly 112.

It follows from (4) that a circuit in the stated grammar needs at
least 112 payload queries to form these eight outputs from plain
inputs. Eight output fields do not imply eight scalar source
directions.

The conclusion holds at every positive tensor depth lambda. Let v
be the constant character, which is fixed by each C_q and its inverse.
Choose Q_q to be either C_q or its inverse. Compress all but one
tensor factor to v. This sends I to I and `Q_q^tensor(lambda)` to
Q_q. Compose ell_p with this compression. The same diagonal minor
remains nonzero. Spectator coordinates can be compressed in the
same way.

This does not add 112 queries to the selected supplier. Its productive
source advances already provide a non-scalar input encoding before
the eight centres are formed. Such an encoding is outside the plain
input premise of (1). A reusable code can therefore matter by carrying
these directions from earlier work. The theorem requires a proposed
shortcut to state where that information enters its interface.

## The matched-plane version

For one actual ordered matched pair q,r, put w=q+r and let
`P_w y=y+(w dot y)w`. The exact plane involution is
`T=C_q C_r^-1 P_w`. In the Fourier basis it fixes each character y
with `w dot y=0`. On the other characters it has the matrix entry

    T_(y+w,y)=i (-1)^(q dot y).                           (7)

For its plane index k, define

    ell_k(M)=(-i/256) sum_(w_k dot y=1)
                        (-1)^(q_k dot y) M_(y+w_k,y).     (8)

It kills I. If another plane has a different w, its contribution
is zero. For the same w, character orthogonality on the affine
hyperplane gives zero unless its q is q_k or q_k+w. Distinct actual
matched planes use neither of those labels. Thus

    ell_k(T_j)=1 if k=j, and 0 otherwise.                (9)

There are 41 distinct swap directions among the 56 actual planes.
The checker does not assume they are all distinct. It checks every
character sum within each repeated-direction group.

Assign the same ordered plane T to its two matched ports, as in the
new plane core. For `G_plane=R diag(T_p)`, each ell_k isolates the
two R columns of its matched ports. Their two-column Gram determinant
is 12, so they are independent. The checker selects two centre rows
per plane. The resulting 112-column minor is block diagonal in
matching order and has exact determinant 8. Therefore G_plane also
has scalar source rank 112 and obeys the same query-count limit.

Compression to constant characters gives the same conclusion at all
positive tensor depths. The statement concerns this proposed plane
interface with the actual R; it does not claim that it is the selected
native source interface.

## A mixed-plane endpoint consequence

For an endpoint that applies T_p independently to n productive fields,
use one common functional

    ell(M)=trace(M)/dim(H)-<v|M|v>,                       (10)

where v is the normalized constant character. Every T_p fixes v and
has normalized trace `2^-lambda`. Therefore

    ell(I)=0, ell(T_p)=2^-lambda-1 != 0.                 (11)

Applying (10) to `diag(T_p)` gives a nonzero scalar multiple of I_n.
Equation (4) requires at least n queries. Fixed invertible scalar
input and output maps do not change this rank. No common negative
eigenvector is used, so this statement permits distinct plane labels
and arbitrary scalar mixing of their field roles.

The same limit holds with feedback and with reuse of a previously
computed query. If each counted query is required to be a complete
native rank-two plane transfer, its native mass is at least 2n.
That last inference does not apply to arbitrary smaller native
operations or to rank-zero address maps.

## Limits relevant to the supplier

The full native compiler is larger than the gate grammar above.
It permits different payload maps on different fields. Factoring
different productive advances E_(s,p) out of a port-mixing R/K bridge
can make that bridge operator-valued. Such a bridge no longer acts
as B tensor I and cannot be treated as free in (1).

There is a direct check against an incorrect native-cost inference.
At tensor depth one, (5) forms a line phase from the identity and one
rank-zero translation X_q, using scalar arithmetic. Therefore 112
payload accesses need not mean 112 native Fourier calls. At larger
depth a direct translation expansion has exponentially many terms;
the present theorem does not price or admit that expansion.

The result excludes neither changed source encodings nor rank-zero
address algorithms, partial native phase algorithms, productive dirty
carriers, or a changed recursive interface. It identifies the scalar
source and response support which those mechanisms must supply.
It makes no new supplier or kappa claim.

## Checks and credit

Run from the workspace root:

    python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/schur-selection/plane-repair/check_query_span.py

Expected first line:

    PASS_EXACT_QUERY_SOURCE_SPANS

The checker pins the actual R, actual phase labels and the frozen
plane construction. It checks the line diagonal minor, all repeated
plane-direction character sums, all 56 pair Grams and the exact
plane minor determinant. The all-depth result and the circuit
invariant follow from the displayed proofs. No broad search is used
as evidence for a lower bound.

The interface-proof lane checked both factorization arguments and
the line tensor-compression argument independently before this note
was frozen. The exact emitted certificate still needs its own frozen
review. The source R comes from the circuit-interface reconstruction;
the plane matching comes from
[PR #1825](https://github.com/CrocSwap/integer-mult-bounds/pull/1825).
Substantial OpenAI Codex assistance was used under the user's direction.
No new publication is authorized.
