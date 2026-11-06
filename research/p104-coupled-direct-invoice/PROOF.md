# A complete direct-invoice obstruction for the four-site coupled root

Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.

## Exact scope and full bill first

This note fixes coupled width q=2, n=4, eight arbitrary independent input
fields per two physical ports, and the shortest five rank-two square-zero
queries. The four full sites are 0,1,3,4. Ordinary constant changes of basis
may mix all eight fields. Each selected idempotent P_i must satisfy
P_i R_i=R_i P_i=R_i, commute with its actual complete chronological query
prefix B_i, and commute with the other three selected projectors. All
inputs remain arbitrary; no initialized or discarded main input is used.

The supplier is the unchanged P104 source priced in #6726 at commit
435bbe91fb28cb1d7a569ca70c6c4e9eb302d486. A native invocation has the
following productive helper and paid-request inventories. Native main
outputs are accounted for by the caller, not counted again here.

| Rank | Helpers | Paid requests |
|---:|---:|---:|
| 1 | 14 | 2231 |
| 2 | 8 | 454 |
| 3 | 4 | 490 |
| 4 | 108 | 109 |
| 5 | 16 | 152 |
| 6 | 3 | 8 |
| 7 | 9 | 9 |
| 8 | 40 | 1 |
| 9 | 361 | 0 |

There are 104 physical native ports. Grouping them into 52 pairs gives
the coefficient-space q=2 normalization; it does not create new native
ports. At full site i use an ordinary binary supplier with a_i>=1 leaves;
put F=sum a_i. There are exactly F native invocations, F-4 internal binary
nodes, and F-3 thin queries (one at the root and one at each binary node).
Each internal node of leaf size u contributes 208 independent rank-(8u+1)
targets and pays 208 rank-8u idles plus 104 rank-one thin requests.
Each root stage of rank r_i pays 52(r_i-4) whole rank-8a_i idle requests.
These root idles are paid separately at their respective stages. Cross-stage
fusion, new retirements, fresh handoff inputs, and changed native schedules
are outside this model.

Let H(r)=r^(1-k), let ell be the native signed moment divided by 104, and
define the complete binary-subtree contribution

    D(1)=0,
    D(u)=max_{1<=v<u}(D(v)+D(u-v))+2[H(8u+1)-H(8u)]-1.

Commuting idempotents have a joint eigenspace decomposition over any field
of characteristic different from two. Let c_m be the dimension of joint
sector m in {0,...,15}; then sum c_m=8 and
r_i=sum_m c_m m_i. Its root target has rank 1+8 sum_i m_i a_i.
The entire recursive signed gap, per physical port, is exactly

    G = F ell + sum_i D(a_i)
        + (1/2) sum_m c_m H(1+8 sum_i m_i a_i)
        - (1/2) sum_i (r_i-4)H(8a_i) -1.                 (1)

The last term is the root thin query. This formula includes all native
helper credit, paid native calls, binary productive auxiliaries, binary
idles, root idles and thin queries. Its rank-mass surplus is 48F-104 in
physical units. Ordinary operations are optimistically free, which
strengthens the exclusion. We claim no physical implementation of an
unrealized inventory.

**Result:** every root in this declared model has G<0 at k=0.00330720.
The exclusion holds throughout [0.00330720,0.004]. Thus this entire direct
four-site model cannot supply a profitable complete recursive invoice
in that interval. This is not an exclusion of paid fragmentation or
retirement, other selected sites, longer words, larger n, or native changes.

## Proven geometric reductions

We use the exact shortest-query normal form and odd-projector/leakage
lemmas from #6717 at commit 3c9072b8738323dda9f9c7dfb421d578ed3fc17a.
Its original proof is retained byte-for-byte in inputs/pr6717-PROOF.md.
Ali Romman's earlier scalar/coupled normal-form, closure and rank lemmas,
Cinna Davis's query lineage, and thu-nmrc's all-even extension retain
their credit. The following application does not assume the later
four-stage equality obstruction being developed alongside this note.

Write A=P0,B=P1,C=P3,D=P4. In canonical n=4 coordinates, the closure
forced by B1 contains U0,U1 and supports V0,V1: a1=e0-e1 and
h1=v1-v0. At site3, a3=-u4 and h3=v4, so C contains/supports the
two selected queries R3,R4. Hence B supports R0 and C supports R4.
Replace the endpoint projectors by A'=AB and D'=DC. They remain
idempotent and mutually commuting, support their original queries on
both sides, and satisfy endpoint prefix commutation (B0=I-2R0 and
B4=-I). Thus we may arrange A<=B and D<=C.

This shrinking is favorable for (1), not just geometrically legal.
Deleting one body bit from a joint sector loses target increment
H(x+y)-H(x) but saves paid idle H(y), where x>=1 and y>0.
Strict subadditivity gives H(x+y)-H(x)<H(y). Native calls, binary
suppliers and root queries are unchanged. Therefore the original gap
is at most that of its shrunk root.

The union projector of any three selected stages is the identity.
It contains three query-image spaces of total dimension 3q and supports
three row spaces of dimension 3q. The corresponding skew-sign Gram
matrix has rank 2q. The inherited image/row lemma therefore gives union
rank at least3q+3q-2q=4q=8. Independence of these image and row spaces
is immediate from the canonical shortest tuple (and can be checked by
deleting any two of its five block sites). Consequently no joint sector
has weight zero or one.

Together with A<=B and D<=C, the only masks are

    3=AB, 6=BC, 7=ABC, 12=CD, 14=BCD, 15=ABCD.           (2)

Furthermore V0 U4=-I_q factors through AD, so rank(AD)>=q=2;
in (2) this says c15>=2. Each stage has rank at least2q=4.
The two odd-site commutator lemma gives r_B+r_C>=5q=10.
The far-endpoint leakage bound rank(Q)>=4q-2(rank(P)-2q)
gives the two additional inequalities

    r_A+2r_C>=16,       2r_B+r_D>=16.                    (3)

Every condition used in the finite inventory below is one of these
proved necessary conditions. They are not assumed sufficient.

## Exhaustive inventory and allocation reduction

There are 267 multisets of eight masks from(2) satisfying r_i>=4,
c15>=2 and(3), including the odd-pair inequality. A deletion removes
one bit from one mask while staying inside this finite necessary-condition
set. The same strict subadditivity calculation used for endpoint shrinking
shows that every such deletion strictly increases G. Repeated deletion
terminates, since total rank decreases. The 267 inventories therefore
reduce to their nine deletion-minimal inventories. Reversing stages
A,B,C,D to D,C,B,A preserves this necessary-condition set and the full formula; there
are six reflection classes. These are finite statements about integer
multisets, exhaustively checked by the standard-library verifier.

This relaxed set intentionally retains the rank 20 profile
(AB,AB,BC,BC,CD,CD,ABCD,ABCD). A separate geometric obstruction to
that profile is not needed here. This cost result is independent of the
concurrent stronger four-stage rank/equality results.

For every F=4,...,127, enumerate all four positive child sizes summing
to F and all six minimal reflection classes. The dynamic program D
optimizes over every ordered binary split, so the test covers all binary
tree shapes, rather than only balanced trees. There are 10,334,625 ordered
allocations and 62,007,750 class/allocation comparisons.

At k=0.00330720, the largest outward upper bound in this relaxed finite
set is

    -13529435522300 / 208000000000000
    = -0.06504536308798077... per physical port.          (4)

It occurs at sizes(8,1,1,8), ranks(4,6,6,4), and the retained rank 20
mask profile above. The maximum is negative even though this profile
need not be realizable. The complete winning relaxed invoice has 18
native calls, 14 internal binary nodes, 15 thin queries and 30 whole idles
per physical port; it is not a new proposed construction.

## Unbounded allocation tail

Let i(u)=H(8u+1)-H(8u) and A=2i(2)-1. Concavity implies i decreases,
so every internal binary-node contribution is at most A. There are F-4
internal nodes. Subadditivity, applied to each root output, gives

    H(1+8 sum m_i a_i) <= 1+sum m_i H(8a_i).

Summing the eight outputs and subtracting all root-idle terms cancels
each stage's r_i-dependent multiplicity. Hence, for every inventory,

    G <= F ell +(F-4)A +2 sum_i H(8a_i)+3
      <= B(F):=F ell +(F-4)A+8H(2F)+3.                  (5)

The second step is Jensen's inequality on the four positive a_i with
sum F. The function B is concave in real F>0. Exact rational outward
bounds give

    B(128) <= -59484190917/500000000000 < 0,
    B'(128)<= -45852109977/1000000000000 < 0.

For F>=128, concavity places B(F) below its negative-slope tangent at 128.
This proves the infinite tail. The finite range is a proved reduction,
not a search cutoff assumed to cover all allocations.

## Extension through k=0.004

The verifier bounds the derivative of the native signed moment ell
uniformly on [0.00330720,0.004] and proves it is negative. Each
H_k(r) decreases with k. Also i_k(u) decreases with k: its derivative
is -f_k(8u+1)+f_k(8u), where f_k(r)=r^(1-k)log r is increasing for
r>=1 and k<1. Thus D_k(u), the maximum of finitely many decreasing
tree contributions, is decreasing, and A_k decreases.

For the finite allocation range, all root target ranks are at most 1025.
The function f_k(r)/r=r^(-k)log r is increasing on [1,1025], since
k log1025<1 throughout the interval. Consequently f_k is superadditive
for sums in that range. Differentiating the root contribution in(1)
and applying superadditivity to each output shows

    d/dk(root target minus idle contribution)
      <= -2 sum_i f_k(8a_i) < 0.

So every finite invoice decreases with k. In the infinite tail, each
term of B_k(F) in(5) decreases for F>=128, because ell_k,A_k,H_k do.
The negative finite and tail bounds at the left endpoint therefore
persist throughout the claimed interval.

## Exact arithmetic, source binding and limits

Run `python -I -B verify_direct_bill.py`; `--write` explicitly authors
the receipt. The verifier authenticates all retained source bytes against
SHA256 and Git blob hashes in ORIGINS.json, and parses the native helper
and paid histograms directly from the authenticated #6726 pricing source.
The inherited caller source is retained to identify every binary auxiliary,
idle and thin-query charge. Its original notices are copied unchanged.

The numerical engine is independently implemented using rational series.
Range reduction writes log n=e log2+log(n/2^e), and
log x=2 sum_{j>=0} z^(2j+1)/(2j+1), z=(x-1)/(x+1), with 0<=z<=1/3.
After 36 terms its positive tail is at most
2z^73/[73(1-z^2)]. For exp x,0<=x<1, the degree 16 Taylor polynomial
is a lower bound and the remaining tail is at most its degree 17 term
divided by 1-x/18. Inverting positive exp bounds encloses H(n).
All powers are then rounded outwards to multiples of10^-12. Subsequent
inventory and allocation arithmetic uses integers only. The positive
target and negative paid sides always use their respective outward ends.

The finite implementation separately compares its winning compressed
expression to the direct general formula. Deleting the root thin-query
charge reverses the sign of that winning upper bound; this is a missing
cost negative control, not a feasible positive witness. Normal and
optimized Python runs must produce the same mathematical receipt.

This is an author proof with exact computational support, not independent
human review or a proof-kernel verification. It supplies no new kappa,
no native supplier, and no unconditional multiplication theorem. The
five assumptions retained by #6726 remain outside its scope. Because
the negative result gives ordinary work for free, no unproved ordinary
compiler or physical routing claim is required for this exclusion.

## Open next questions

1. Can a changed root with actual paid cross-stage idle fusion or a new
   legal retirement beat this direct-invoice obstruction? First provide
   a literal arbitrary-input word and recompute all productive and paid
   terms; the current proof deliberately does not price such mechanisms.
2. What coupled profiles occur for larger n or a different full-site set?
   A first useful step is a chronological-prefix compatible projector
   certificate and a complete native invoice. Passing an incidence-only
   relaxation does not establish either obligation.
3. Independently audit endpoint shrinking, the six-mask reduction and
   the outward integer evaluator. The retained source pins and small
   geometric identities make those boundaries reviewable.

The original rank 19 mention in #6726 is discovery context only: the
published prose does not define a full rank 19 candidate contract. This
note explicitly defines and closes its own direct four-site model,
rather than assigning unstated hypotheses to that predecessor.
