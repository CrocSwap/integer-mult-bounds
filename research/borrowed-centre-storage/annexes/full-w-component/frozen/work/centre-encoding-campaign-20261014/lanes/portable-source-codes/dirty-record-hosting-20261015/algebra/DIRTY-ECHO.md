# Eight dirty records with an exact erase query

This note proves a conditional replacement for the sixteen owned records
in the first common-F recovery. Eight T records are removed. The other
eight records can use arbitrary borrowed fields. The repair then gives

    data = z + E h,       donors = h + G z,       G E = 0.

Here z is the original logical pair of 224 fields, and h consists of the
eight arbitrary donor values in the repair coordinates. The exact inverse
is

    h = donors - G(data),       z = data - E h.

No donor is cleared. No extra output bank is used. One owned scalar scratch
field is enough for the row operations. This result does not allocate the
donors in the 482-event schedule. It does not make the future read G legal
in the current native frame. Those are separate conditions.

The [check](check_dirty_echo.py) and [receipt](ALGEBRA.json) use the actual
QQ16 matrix and the frozen common-F repair tail. The exact cleanup rows
are in [FUTURE-READ-ROWS.json](FUTURE-READ-ROWS.json). The source pins and
all output pins are in [MANIFEST.json](MANIFEST.json).

## Source and notation

The consumed sources are the private
[common-F proof](../../../paired-package-review/upstream-followthrough-20261015/COMMON-F-RESTORATION.md)
and the two earlier storage notes:
[relative dirty transport](../../../source-domain/carried-owner-reuse/RELATIVE-REUSE.md)
and [idle swaps](../../../source-domain/carried-owner-reuse/CLEAN-IDLE-STORAGE.md).
The source bytes remain unchanged. The parent worker supplied the T-record
reduction and the candidate A-record residue. This note proves and checks
their composition and the erase query. OpenAI Codex was used for this work.

Use the literal selected sets

    A = [0,7,20,27,36,46,57,111],
    T = [21,37,47,76,81,87,92,110],
    V = A union T,       U = the other 96 ports.

Let R be the source 8 by 112 scalar matrix. Its restricted Gram matrices
are R_A R_A^t = R_T R_T^t = 4I and R_U R_U^t = 48I. For stage s, let
D_(s,p) be the actual involutive owner route. Define

    ell_(s,S) v = sum_(p in S) R_p D_(s,p) v_p,
    (P_(s,S) f)_p = D_(s,p) R_p^t f / 4.

Write R_s = ell_(s,all), and K_(s,U) = P_(s,U). The stage-0 route is
identity. Thus P_(s,T) is the inverse of ell_(s,T), and the same statement
holds for A. All products below retain their order. In particular, define

    N2 = P_(2,A) ell_(2,U union T),       J0 = P_(0,T) ell_(0,A).

Let (x1,y1) be the logical F0 output and (x2,y2) the logical B1 output.
The boundary is the same as in the consumed common-F proof. For raw entry
arrays (a,b), the recovered physical output is (F_U1 Q^-1 a, F_U1 b).
This note does not remove the initial Q factor.

## Remove the eight T records

The actual B1 query exchange gives

    R1 y2 = ell_(1,T) x1_T.

To check this identity, put a = ell_(1,T) x1_T. The query-exchange output
v has R1 v = a. The final U and T transvections add K_(1,U) a and
-12 P_(1,T) a. Their contributions to R1 y2 are 12a and -12a, respectively.

After all 112 positive Y lines, both data banks have common frame F_U1.
Before any Y field outside T is changed, set B = P_(1,T) ell_(1,U union A)
and apply

    Y_T += X_T
    X_T  = -X_T + Y_T + B Y_(U union A).

Each right-hand side uses the values indicated by this order. The new
X_T is y2_T + B y2_(U union A) = P_(1,T) R1 y2 = x1_T. The new Y_T is
x2_T + y2_T = x_T + y_T. The eight T fields therefore have the same values
as after the old record exchange. No T record is needed.

The current-chart read uses all 112 original Y fields in the equation
R1 y2. Its implementation only needs the 104 off-T Y sources in B, since
the old Y_T appears in the in-place operation. The current-chart cover
intertwiner from the source proof supplies these routes. The new scalar
order and cover sweeps must be included in the new invoice.

## Use eight dirty A records

At the repair cut, suppose the decoded donor on each A port is

    r_A = h + x1_A.

There is no assumption on h. First set Y_A += X_A. Then use these four
ADD operations, with each right-hand side read after the previous line:

    X_A += r_A
    r_A -= X_A
    X_A += r_A
    r_A += X_A.

The first three operations put h+x1_A in X_A and -x2_A in r_A. The final
ADD retains the residue instead of clearing the donor. Since the B1
future logger gives

    y2_A = y1_A + N2 y1_(U union T),
    x2_A = x1_A - N2 y1_(U union T),

the retained donor is

    r_A = h + N2 y1_(U union T).

Now run the old common-F tail. It uses the recovered X_T to remove the
current-chart correction from Y_U, recovers X1_U, applies the F0 X inverse,
and subtracts the selected recovered X fields from the selected Y sums.
Before the F0 inverse, its only X error is +h on A. The exact F0 inverse
therefore leaves the following error E h:

    delta X_A = -h,          delta Y_A = h,
    delta X_T = J0 h,        delta Y_T = -J0 h,
    delta X_U = 0,           delta Y_U = 0.

This formula includes both selected banks. It does not discard donor
dirt into an unreported data output.

## Recover the exact erase query

For an arbitrary pair (X,Y), define f = R0 X and the 104 virtual fields

    u_U = Y_U + X_U - K_(0,U) f,
    u_T = X_T + Y_T - P_(0,T) f.

For the original pair z=(x,y), these fields are exactly y1_(U union T).
For the perturbed pair z+E h, they have the same values. In fact,

    R0 delta X = -ell_(0,A) h + ell_(0,T) J0 h = 0,
    delta X_V + delta Y_V = 0,
    delta X_U = delta Y_U = 0.

Define G(X,Y) = N2 u. These identities prove G E = 0 without moving a
stage-2 route through an earlier query. Thus, at the dirty repair output,

    G(data) = N2 y1_(U union T) = G z.

Subtract this read from the eight donors. They now equal h. Use the
restored donors to correct the data in this order:

    X_A += h;       Y_A -= h;
    X_T -= J0 h;    Y_T += J0 h.

Every original data field and every donor is restored. The donors remain
unchanged during the final correction. The complete joint linear map has
blocks [[I,E],[G,I]], with Schur complement I-GE=I. It is invertible on
all independent data and donor inputs.

No array of 104 virtual fields is required. A row of G is a known finite
linear combination of reads from the existing data fields. Form one row
in the owned scratch C, subtract it from its donor, clear C, and then form
the next row. The eight donor writes do not affect any source of G. The
same row method computes J0 h. This proves the storage statement; the
physical legality and cost of those routed reads remain separate.

For this joint state, the read G is necessary for linear donor restoration.
If A r + L data = h for every z and h, its z coefficient gives L=-A G.
Its h coefficient then gives A+L E=A(I-GE)=I. Hence A=I and L=-G.
This is a statement about this representation. It is not a lower bound
on every possible reversible storage construction.

If N2 is already legal at the B1 cut, even the A records can be removed:
recover y1_(U union T) from T and U first, then use
x1_A = x2_A + N2 y1_(U union T). The dirty construction instead permits
this same future read to be postponed.

## Physical donor transport and a postponed erase

The equation r=h+x1_A is conditional on an exact transport identity. Let
an old donor have arbitrary physical baseline a at capture. Let T_d be
its original complete interval operator, and let M be a chosen cover
reindexing. A sufficient condition is

    T_d M F_L = M F_U1.

Capture adds M F_L x1_A to a. At the repair cut the donor is then

    T_d a + M F_U1 x1_A = M F_U1 (h+x1_A),
    h = F_U1^-1 M^-1 T_d a.

This does not require a to have the query's entry frame. Decode a donor
read with M^-1 and encode a donor write with M. The scalar exchange above
then acts on the stated physical arrays. After the erase, the donor is
T_d a, its required value in the original schedule. It need not equal its
earlier baseline a if the original interval advances that baseline.

Every helper use in the interval must have the complete two-sided source
contract on arbitrary inputs. No other data or scalar use can be ignored.
A mismatched native advance is not free: it must be compensated, or the
stated restoration fails. The parent worker is checking these intervals
against the actual schedule. This note does not perform that check.

There is also an exact delayed form. Suppose the data and donor contents
then advance separately by invertible operators D and K. Their values are

    D(z+E h),       K(h+G z).

Read K G D^-1 from the current data and subtract it from the donors. The
donors become K h because G E=0. Then subtract D E K^-1 of those donors
from the current data. The data become D z. An actual delayed implementation
must supply these two reads in the actual frames. It must prove the stated
separate advances D and K. This formula is not a schedule or a permission
to commute a helper job through an unproved data operation.

## Exact access obligation and a scoped route obstruction

The erase read needs R0 X from the current data, the displayed 104-field
alias, and the actual future operator P_(2,A) ell_(2,U union T). The final
correction also needs J0 h. At a delayed cut these obligations become
K G D^-1 and D E K^-1. A later full native frame alone is not a proof of
the required content alias.

The checker finds a specific nonzero term in G: donor A port 0 has the
coefficient 1/2 on

    D_(2,0) D_(2,1) Y_1.

Port 1 belongs to U. The actual 73-axis owner matrix of this word sends
the unit vector at axis 17 to the bit mask 1310731. Every stage-1 route
fixes each E2 axis, 17 through 24, pointwise. Thus no product of stage-0
and stage-1 routes gives this owner word. On independent full-cover source
arrays, a linear combination of reads at those earlier owner routes
cannot replace this term. This obstructs only that route class. It does
not exclude a legal native adapter, a later alias, or another representation.

## Executed checks and limits

Run from the workspace root with standard-library Python:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/portable-source-codes/dirty-record-hosting-20261015/algebra/check_dirty_echo.py
```

Expected status: `PASS_EIGHT_DIRTY_DONOR_ECHO_ALGEBRA`.

The check uses all 224 independent original data columns, eight independent
donor columns, and one arbitrary owned scratch column. It checks the new
T operation, all A exchanges, the 1,853 emitted events formed from the A
exchange and frozen scalar tail, every data error row, the exact donor
residue, G E=0, the erase, and all final data and donor rows. It verifies
all 224 actual stage-1 and stage-2 owner involutions on 73 axes. The free
ordered route algebra only reduces an adjacent identical involution pair.
It does not use accidental route relations to make an identity pass.

G has eight rows, 22,048 routed terms, 216 distinct original source columns,
and route words of length at most two. These are formal row counts, not
native operation costs. Controls reject use of the dirty record as a clean
record, omission of G, the old record erase after the new exchange, and
clearing the borrowed donors.

The check does not replay the physical record lift or the 112 positive
Y lines; it starts the repair from their stated common logical frame.
It does not assign old donors or new child helpers. It does not check the
482-event delayed data path, the physical phase of the future read, or a
finite-precision implementation. The earlier sixteen-owned-record guard
bound and invoice do not transfer to this new word. No new complete native
profile, stream cost, controller, supplier, or kappa result is claimed.
