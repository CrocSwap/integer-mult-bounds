# Independent review: uniform canonical three-stage budget

The proposed bound is correct in the stated canonical shortest-query model.
For every even n>=4 and arbitrary coupled width q>=1, three pairwise
commuting compatible stage projectors that commute with their own chronological
prefixes have total rank at least 7q. The scalar sharp construction extends to
every such n and attains 7q. This is a rank/endpoint theorem, not a native
Gaussian realization, complete paid invoice, precision theorem or new kappa.

This is internal AI-assisted author-side review, not external scientific
acceptance. The q=1 all-even-n local commuting-triple predecessor is Ali
Romman's #6398, not new here. The canonical coupled query normal form is also
inherited. The proposed extension concerns arbitrary coupled projectors of
mixed ranks, with the prefix condition retained. See SOURCES.json.

## Exact hypotheses and notation

Work over a field of characteristic different from 2. All scalar vectors and
matrices below are tensored with I_q. This tensor description applies to the
fixed canonical query data; the unknown projectors can mix all nq coordinates.
No tensor decomposition of those projectors is assumed.

Let u_i=e_i for 0<=i<n, and u_n[k]=(-1)^(k+1). Let
v_i[k]=sign(i-k), so v_n is the all-ones row. Set R_i=u_i v_i and
B_i=(I-2R_i)...(I-2R_0). The complete product B_n=-I. At each selected site i
there is an idempotent P_i satisfying P_i R_i=R_i P_i=R_i and
[P_i,B_i]=0; the three selected P_i commute pairwise. Compatibility is
equivalent to P_i u_i=u_i and v_i P_i=v_i because the query factors have
full column/row rank.

Every compatible projector has rank at least 2q: its image contains im(u_i),
its row space contains row(v_i), and v_i u_i=0. More generally, if an
idempotent P contains a column space A and a row space C, with CA=0, then
rank(P)>=dim(A)+dim(C). Indeed C=C P restricts to independent functionals
on im(P), and A is contained in their joint kernel there.

For 0<=i<n define the column a_i[k]=(-1)^k for k<=i and zero otherwise;
let h_i be the prefix-ones row on 0..i, h_prev the row on 0..i-1, and
h_tail the row on i+1..n-1. Write J_i for diagonal -1 on 0..i and +1 on
the remaining coordinates. Direct chronological multiplication gives

    B_i=J_i+2 a_i h_all.                         (1)

This formula is used only at interior indices i<n. The last prefix is the
separate identity B_n=-I. Substituting i=n into (1) is incorrect.

## Even interior full sites cost at least 4q

For even i with 2<=i<=n-2, formula (1) gives

    B_i u_i=-u_i+2a_i,
    v_i B_i=-h_prev-h_tail,
    v_i=h_prev-h_tail.

Compatibility and prefix commutation therefore force P_i to contain the two
column spaces u_i,a_i and both row spaces h_prev,h_tail. The two columns and
two rows are independently rank 2q, and their pairing is zero. The only
nontrivial scalar alternating sum is sum_{k<i}(-1)^k=0. Thus
rank(P_i)>=4q. Together with the two other minimum ranks 2q, any triple
containing an even interior site costs at least 8q.

## Forced projector at every odd site

For odd i, formula (1) instead yields

    B_i u_i=-u_i+2a_i,
    (v_i B_i+v_i)/2=h_i.

Consequently P_i fixes both columns u_i,a_i and supports both rows h_i,v_i.
They pair by

    [h_i;v_i] [u_i,a_i] = I_(2q).

The rank-2q projector

    E_i=u_i h_i+a_i v_i                          (2)

is therefore contained in P_i on both sides: P_i E_i=E_i P_i=E_i.
Writing F_i=P_i-E_i gives an idempotent with

    rank(F_i)=rank(P_i)-2q=:f_i >=0,
    E_i F_i=F_i E_i=0.

These conclusions use arbitrary coupled P_i; only the forced part E_i has
the displayed scalar tensor form.

## Two odd sites force at least q additional rank

For odd i<j, put t_j=e_j^T+h_tail_j. Multiplication of (2) gives

    E_i E_j=-a_i t_j,
    E_j E_i=(u_j+a_j) h_i.                       (3)

The two columns a_i and u_j+a_j are independent: rows i,i+1 give a 2x2
minor of determinant -1. The two rows t_j,h_i are independent: columns j,0
give a 2x2 minor of determinant 1. Thus rank([E_i,E_j])=2q over every
allowed field. In particular the independence claim must not be justified
at coordinate j, where both columns are zero.

Using [P_i,P_j]=0, the efficient exact expansion is

    [E_i,E_j]=-[F_i,E_j]-[P_i,F_j].              (4)

Each commutator with a rank-f factor has rank at most 2f. Equations (3)-(4)
give f_i+f_j>=q. The third projector costs at least 2q, so any triple
containing two odd sites costs at least 7q.

## One odd site and two endpoints: one far endpoint suffices

The only remaining triple consists of endpoints 0,n and one odd i. Write
P_i=E_i+F_i, rank(F_i)=f. Directly from (2),

    E_i u_0=u_i+a_i,       v_0 E_i=v_i-h_i,
    E_i u_n=-a_i,          v_n E_i=h_i.          (5)

Both column/row closure pairs

    A_0=[u_0,E_i u_0],    C_0=[v_0;v_0 E_i],
    A_n=[u_n,E_i u_n],    C_n=[v_n;v_n E_i]

have zero pairing. For A_0,C_0 their dimensions are both 2q precisely
when i>=3; they are only q at i=1. For A_n,C_n their dimensions are both
2q precisely when i<=n-3; they are only q at i=n-1. These assertions follow
from unit scalar minors or the distinct nonempty prefix/tail supports.
Since n>=4, every odd site has at least one endpoint with the full 2q/2q
zero-paired closure. In particular i=1 uses the right endpoint, while
i=n-1 uses the left endpoint. No separate boundary-adjacency argument is
needed.

Here is the rank-defect argument without any tensor restriction on the
endpoint projector Q. Suppose Q is compatible with endpoint (U,V), and
[Q,P_i]=0. Since QU=U and VQ=V,

    (I-Q)E_i U=-(I-Q)F_i U,
    V E_i(I-Q)=-V F_i(I-Q).                     (6)

Thus at most f dimensions of A=[U,E_i U] can fail to lie in im(Q), and at
most f dimensions of C=[V;V E_i] can fail to lie in row(Q). Their retained
subspaces still pair to zero. The elementary image/row-space lemma gives

    rank(Q)>=4q-2f.                             (7)

It also has the baseline rank at least 2q. Therefore its extra rank above
2q is at least max(0,2q-2f). The extras of the three projectors sum to at
least

    f+max(0,2q-2f)>=q.

This proves 7q in the last case, for arbitrary extras, including q>=3 cases
where fewer than two projectors have minimum rank. It avoids the invalid
shortcut of assuming a total below 7q forces two minimum-rank projectors.
The three cases above exhaust every triple of distinct sites.

## Uniform sharp completion and every original output

The root research agent supplied the following completion; this audit
reconstructs it without importing that agent's code. Define an n-by-n basis H
by the first four entries of its first three columns:

    c0=(1,1,0,0), c1=(1,2,1,0), c2=(1,2,2,0).

Their remaining entries vanish. Every column j>=3 has first four entries
t=(0,1,1,1). For 3<=j<=n-2 its extra part is e_(j+1). The extra part of
the last column is -sum_{j=3}^{n-2}(-1)^(j+1)e_(j+1).

To see that H is invertible uniformly, add
sum_{j=3}^{n-2}(-1)^(j+1)c_j to the last column. Its extra part cancels, and
its first four entries remain t because the alternating sum over the even
number n-4 of terms is zero. Subtract this new last column from each column
j=3..n-2. The result has the invertible 4x4 block [c0,c1,c2,t] of determinant
1, together with n-4 identity columns. Thus det(H)=+/-1.

Conjugate every canonical R_i by H. The selected columns and rows at sites
0,1,n are exactly

    u0=(1,1,0,0),    v0=(1,-1,0,0),
    u1=(1,2,1,0),    v1=(1,0,-1,0),
    un=(-1,0,0,1),   vn=(1,0,0,1),

with all extra coordinates zero. The canonical u_n combination cancels all
extra rows by the definition of the last column; the selected rows are checked
by multiplying the displayed rows by H. The construction is not required to
be the identical n=4 basis representative used in an earlier audit.

Let the selected projectors be diagonal masks 3,7,9 on the first four
coordinates, zero on the remaining n-4 directions. Their ranks are 2,3,2.
They commute pairwise and are compatible. At site1 the rank-three projector
contains both R0 and R1, so it commutes with their chronological prefix;
at site0 compatibility suffices, and the last prefix is -I.

For independent central formal stage variables A,B,C and S^2=1, insert a
stage I-P+zP before each selected query I+(S-1)R. The prefix conditions and
pairwise commutation give the full endpoint

    S diag(ABC,AB,B,C,1,...,1),                 (8)

on all n independent original coordinates. Tensoring this explicit sharp
construction with I_q attains rank sum 7q for every q. The n-4 extra fields
have output S times their own input, not disposable or identity jobs.

The verifier compares every matrix coefficient of (8), separately at S=+1
and S=-1; 2 is invertible, so those two characters determine the full formal
S endpoint. This formal identity does not supply a priced native realization
of arbitrary rank-q query calls, or a multiplication admission theorem.

## Reproduction and limits

Run `python3 -I -B independent.py` or `python3 -O -I -B independent.py` in this
directory. Default execution is read-only and compares its exact result with
INDEPENDENT.json. `--write` is only for deliberately regenerating the receipt.

Finite exact checks cover even n=4..20, every interior prefix, all even-site
closures, every odd pair and unit independence minor, and both far-endpoint
closure rank domains. Complete sharp multivariate endpoints are checked at
q=1 for all those n and q=2 for n=4,6,8. They corroborate the written
symbolic proof; the proof of arbitrary n,q is not inferred from this grid.
Executed controls reject treating the last prefix as an interior prefix,
removing a paid thin query, and dropping extra original S outputs. A genuine
n=2 counterexample has three commuting compatible rank-two stages of total
6<7, so the n>=4 restriction is necessary.

No claim is made about more than n+1 queries, different query ranks, stages
not commuting with their prefixes, noncommuting stage projectors, initialized
or discarded input directions, noncentral ordinary coefficient maps, or any
complete caller tariff. No new kappa or scientific acceptance is claimed.
