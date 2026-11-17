# Independent monotone prices for the repeated two-letter target

This contribution was produced by Nick Petalas. Apache-2.0.

## Model and result

Retain the model of ToikY's [#6821](https://github.com/CrocSwap/integer-mult-bounds/pull/6821).
Let K be any field and G=S3, with simple involutions s,t. Let d>=1 and
r>=d be finite. The complete required endpoint in M_r(K[G]) is

    T_d = diag([st], ..., [st], [e], ..., [e]),
                   d copies

with arbitrary initial data on every role. Every spectator and every
off-diagonal coefficient must be restored. A paid factor is

    F_u(A) = I + ([u]-[e]) A,  u in {s,t},  0 < rank_K(A) <= b_u.

The finite positive integer caps b_s,b_t may differ. A can be singular or
nonidempotent. Interleaved scalar GL_r(K) maps are free. No free address
maps, resets, discarded outputs or clean allocations are allowed.

For each u let tau_u:{0,...,b_u}->R be nonnegative and nondecreasing, with
tau_u(0)=0. A u-call costs tau_u(rank A). The two tables need not agree or
be proportional, concave or convex. Set K_u=min(b_u,d) and define

    H_u(0) = 0,
    H_u(m) = min_{1 <= k <= min(K_u,m)} [tau_u(k)+H_u(m-k)],
                                      1 <= m <= d.

**Theorem.** The exact minimum bill for T_d is H_s(d)+H_t(d). Independent
minimizing partitions for the two letters give an attaining word on the d
productive roles, with no extra workspace. The two recurrences each have
d+1 states and at most d K_u transitions.

The universal claim is this written proof, using the cited separate-letter
rank inequalities. The finite checker corroborates the new optimization
and full attaining endpoints; it is not a census of all circuits.

## Inherited lower bounds

We cite #6821's PROOF.md, equations (3) and (4), for

    sum_(s-calls) rank A >= d,
    sum_(t-calls) rank A >= d.                         (1)

Its selective regular cuts {e,t} and {e,s} apply over every field, to
arbitrary couplings, free scalar mixing and any finite number of restored
dirty roles. These are inherited inputs, not new cut inequalities or
results audited here. Adam Gall #1941 and Ross Richardson #1966/#1989
retain the separate-letter cut-method credit. ToikY applies those cuts to
this repeated-st endpoint. Benny Zhao / zhaobenny #6817 and David Arias
#2738 supply the retained formal model and Coxeter/packing context.

## Monotone truncation and the exact price

For either letter, list the positive paid ranks a_1,...,a_q of an arbitrary
finite valid word. Equation (1) gives sum a_i>=d. There are integers
0<=e_i<=a_i with sum e_i=d: visit the entries in order and keep the smaller
of a_i and the remaining demand. The remaining demand reaches zero by
the last entry. Each e_i<=min(b_u,d)=K_u. Monotonicity, including at zero,
therefore gives

    sum_i tau_u(a_i) >= sum_i tau_u(e_i) >= H_u(d).     (2)

For the last inequality, drop zero entries. The recurrence is the minimum
over all positive integer partitions of exact mass d and parts at most
K_u. This follows by induction on the remaining mass: a first part k
leaves the smaller instance m-k, and every partition has such a first
part. There are finitely many candidates, so the minimum is attained.

Truncation is a lower-bound argument about integer rank lists. It does
not change the matrices of the original program or assert that truncating
those matrices preserves their endpoint. It also handles ranks greater
than d in a word with many dirty roles. Rank caps greater than r cause no
problem: attaining parts are at most d<=r, and an unavailable rank is
never requested.

Apply (2) independently to s and t and add their actual costs. This proves
the lower bound H_s(d)+H_t(d), including flat and zero prices. No bound on
the number of spectators, beyond finiteness, is used.

## Independent partitions attain the full endpoint

Take a minimizing partition of d for s. Divide the first d coordinate
roles into consecutive blocks of those sizes, and apply one s-factor with
the coordinate projector of each block. Their product is

    D_s = diag([s], ..., [s], [e], ..., [e]).

Independently partition those same d roles using a minimizing partition
for t. The blocks need not coincide with the s-blocks. Their t-factors
multiply to D_t. In written product order the complete program is D_s D_t.
It equals T_d coefficientwise in the full group algebra. Each spectator
is untouched. Every call is a legal positive-rank projector with its own
declared cap. This attaining construction requires no preparation, scalar
maps or restoration. The price is exactly H_s(d)+H_t(d).

Products act rightmost first, so a chronological implementation executes
the t-blocks before the s-blocks. The proof and checker use written product
order throughout. Free scalar maps are allowed in the lower bound; the
upper word needs none. Gauged finite fixtures include them explicitly at
both ends and restore the original full endpoint.

## First strict extension

At d=7 and b_s=b_t=4, use tau_s(k)=3+k^2 for positive k, tau_s(0)=0,
and tau_t(k)=k/(k+1). Both tables are nondecreasing. The s-table has slopes
4,3,5,7, so the common-concave theorem does not apply to it.

The minimizing s-parts are 2,2,2,1, of price 25. A short lower certificate
is tau_s(k)>=(7/2)k on 1<=k<=4, with an additional 1/2 whenever k is odd.
Every partition of odd mass seven has at least one odd part, proving
price at least 25. The t-parts 4,3 have price 31/20 by the credited concave
packing lemma, or by enumerating the partitions of seven. Thus the exact
bill is 531/20. Applying parts 4,3 to both letters would cost 651/20.
The independent partitions save six under this declared abstract tariff.

This comparison evaluates a legal coordinate word, rather than applying
the predecessor's concave theorem outside its hypotheses. It changes no
native or recursive invoice. The first verified extension ends this work.

## Scope and credit

The new result removes concavity and common pricing from #6821's exact
repeated-st tariff, permits separate caps, and realizes independent optimal
partitions. The rank demands, group-algebra model, partition dynamic
programming and monotone clipping are credited or elementary inputs, not
claimed as new general methods. Nick Petalas's older #4846 applies a
related monotone-partition method to the different UT3 central endpoint;
its shared degree-list issue does not occur in the consecutive two-letter
construction here. Retain the #6821/#6817/#2738 register-model lineage,
including ywz65, eumemic, Ali Romman and Gareth Davidson.

No claim is made for decreasing prices, changed targets, other paid labels,
free address maps or incomplete dirty restoration. Native realization,
the price of scalar mixing, ownership, movement, frames, stock, precision,
all-size compilation, recursive child-rank identification and the complete
supplier/consumer invoice remain unknown. All five selected framework
assumptions remain. No kappa or selected-frontier change, multiplication
theorem, independent human review or formal proof-kernel acceptance is
claimed.
