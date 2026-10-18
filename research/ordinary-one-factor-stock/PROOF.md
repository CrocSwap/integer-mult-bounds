# Conditional ordinary-backend admission of one-factor stock

This proof binds a changed stock selector to the **existing** PR2899 consumer.
It inherits PR2753/2809's completed primitive, source refinement, uniform
physical-cost and reserve premises, and PR3246's one-factor NODE-guard lemma.
It does not discharge those entire caller proofs. The finite checks are
corroboration at small parameters, not a proof of a multiplication theorem.

## 1. Contract and exact dependency

Fix a source-admissible prime q>2^80. Let m=64, W=28416, Q=9475,
N=|GL64(F_q)|, H=q^(4096(w-1)), b=WNH, and K=Qb. Retain the pinned
selected source and a fixed w throughout one recursive invocation. Define
D(x)=0 for x<64 and D(x)=1+D(42 floor(x/64)) otherwise. Put

    S_0=1, S_d=Q*b^d (d>=1).

Nick Petalas's PR3246 proves the guard implication: a multiple of S_d supplies
every local quotient and Q guard down any admitted branch of depth at most d,
provided completed children restore the fresh rows and exposed spectators
pointwise. It does not prove that child restoration premise. We retain it.

The present consumer is Jose Manuel's PR2899 `Ordinary.fitted`, around
PR2809's `Machine`, with David Arias's PR2753 source and Nick Petalas's PR2808
wrapper. It is **not** a consumer promising both complete depth-d formats.
Ross Richardson's PR2420 still requires K^d for that stronger contract. For
a multiple t*S_d, its additional condition is Q^(d-1) dividing t. The new
adapter must not be substituted into that stronger contract without checking
this condition or supplying a priced adapter.

The exported PR3246 argument is byte-pinned in PREDECESSOR.json. The executable
inputs of this package are the main-base versions of PR2899 and its immutable
PR2808/2809 archives, pinned in SOURCES.json. No pending executable is imported.

## 2. Encoded selection, without silently changing a predecessor

For original positive width e, keep PR2899's choices

    w=ceil(e^(17/10000)), d=D(e).

The new function `select_guard_stock` first calls the unchanged encoded
selector with row_factor=W. This computes b^d and its least covering radix
power. At d>0 multiply stock by Q **once**; at d=0 leave stock=1. Grow rows
by q until it covers the new stock. Because the original rows were the least
q-power covering b^d, this returns precisely

    k=min{j>=0:q^j>=S_d}, R=q^k.

All operations on e, d, k, w, stock, R, n and ell use Count tapes. Q, W,
source dimension/rank and q are compiled constants. The adapter reuses the
existing execute_plan callback; it modifies no frozen source or default.

It then recomputes **both** the strict fit test 2k<e and
(n,ell)=divmod(e-k,w), requiring n>=64 before selecting the fitted branch.
The first live-only selection's old body and remainder are closed and replaced.
They cannot be reused after multiplying stock. At e=24 in the reduced fixture,
that mistake changes the strict fit decision; at e=32 it changes the body.

The depth is taken from e before borrowing, as in PR2899. This package does
not silently replace it with D(n), use an iterative fixed-point choice, or
claim an optimal borrowing selector.

For fixed e and w, S_d divides K^d and S_d<=K^d; their exact ratio is
Q^(d-1) at positive depth. Hence k_new<=k_old and n_new>=n_old whenever
the old plan fits. Every old fitted e remains fitted. The existing sufficient
fallback cutoff remains sufficient; no new cutoff is claimed. Equality of
rounded k is possible, so the stock factor is not a runtime-speed factor.

## 3. Follow the actual consumer, including both returns

For a fitted plan PR2899 uses the ordered input

    [P][Hhi:R][Hbody:(q^w)^n][Hrem:J][G]
       [Dhi:R][Dbody:(q^w)^n][Drem:J][T],  J=q^ell.

At each call, unchanged PR2786 padding supplies

    R'=ceil(R/S_d)*S_d,  R <= R' < 2R.

The actual C0 ports in `Ordinary.fitted` remain:

    old_count=P, depth=0, old_directory=empty, fresh_rows=R',
    before=1, gap=J*G*R, suffix=J*T, body_size=n, weight=1.

In particular, Dhi in the gap is the **genuine R**, not padded R'. No
spectator is relabelled as fresh stock. The empty directory still represents
P old prefixes. The unit ROOT is unchanged; an arbitrary weighted involution
is not interchangeable with this callee.

Since n<=e and D is monotone, D(n)<=d. If D(n)>0, S_D(n) divides S_d;
otherwise there is no internal NODE. Thus R' meets the recursive guard
contract. The `Machine.node` path calls `fresh_rows.quotient` to divide by
WNH, checks U mod Q=0 using `stock_multiple`, and passes the entire U to
children. `SelectedBinding.check_stock` adds no second depth-format test.
The S recurrence retains exactly these guards. The unrelated ToyBinding's
exact fixture-cardinality check is not a production condition.

All admitted fresh-row factors remain complete spectator multiplicities.
Under the unchanged completed primitives, split/merge restores the ordinal
of **each** of the R' rows. Neither aggregation of row sums nor preservation
of total volume is enough. Padding starts added rows at zero; rowwise F_I
maps keep those rows zero. Restriction therefore returns exactly R genuine
rows immediately after the first F_I, before the intervening ADD, and again
after the second F_I. The second call reuses S_d; sequential calls do not
multiply reserve requirements.

The unchanged chronological body identity is

    D-=H; F_I; D+=H; F_I; D=-D; D+=H,
    F_I(H,D)=(C_n D,C_n H).

It returns (D,H). The original high-field and remainder exchanges complete
the ordinary endpoint. Source ownership, two distinct root outputs, consumed
leases, session markers, template lifetime and successful-return erasure are
unchanged. This argument is conditional on those caller/primitive contracts,
not a claim of interruption recovery or a new universal compiler refinement.

## 4. Keep the complete recurrence and the bill

Changing a row multiplier neither removes a child nor makes any helper free.
For f=floor(n/64), the inherited normalized C0 bound is

    T(n,w) <= C_q*w                                      (n<64),
    T(n,w) <= sum_r H_r/W*T(r*f,w)
               + epsilon*F/W*max_{1<=j<=f}T(j,w)
               + C_q*(n+w)                              (n>=64),

with epsilon=10^-16, F=118606528512 and

    r:   1       2      3      4      5      6      7     42
    H_r: 381024 400416 22752 26880 29376 17376 26784 288.

The same source-refinement and uniform preparation/physical-cost hypotheses
must hold for every complete admitted packet. Because every class contains
its complete low/high Cartesian range times U, lowering U does not change
these normalized child weights. Parent/child volume ratios and root coupling
(n<=e, unchanged w) also remain the same. The source proof's packet-volume
argument uses R=WNHU and U>=1, not a hidden extra Q factor per ancestor.
No numerical stage reserve or universal cost premise is discharged here.

The predecessor moment argument gives T_C0/V=O_q(n+n^(1-c)w), c=17/10000.
Retain all 3n ADDs, n signs, k+ell digit passes, both C0 calls on volume <2V,
both padding/restriction bills, output copies, disposal, ownership operations,
initialization/erasure, frames, routing and recursive children. Consequently

    T_ordinary/V = O_q(n+n^(1-c)w+k+w) + setup/V,
    space = O_q(V)+F_q,

conditional on the inherited C0 statements. S_d<=K^d preserves
k=O_q(w log e), so the same a=c(1-c)=169711/10^8 rate follows. **No improved
exponent or practical runtime follows from the smaller divisor.**

The extra setup is not free. The adapter first completes the live-only
selector, then multiplies stock once, grows rows at most ceil(log_q Q) times,
rechecks fit and performs at most one encoded division. It retains a fixed
number of Count tapes. Its largest integers are O_q(e) bits; the inherited
fixed-polynomial setup bound can absorb these additional scans and division.
The largest live overlap is bounded by the same 64 setup-role allowance:
after the initial selector's temporaries return, seven plan Counts coexist
with one `twice` Count, or with `remaining`, `dimension` and the fixed
workspace of encoded.divide/subtract. This is below the predecessor selector's
own conservative 64-role bound; no extra physical tape is allocated in scope.
Neither this bound nor observed peak roles are a full machine-step constant.

## 5. Exact evidence and limits

The integer specification independently computes widths, depths, reserves,
minimal radix powers and body splits. Literal tape replay covers reduced
profiles, changing-width cases, Q=1, and strict-fit boundaries. Actual
fresh_rows quotient and compatibility checks reject missing-Q and incomplete
packet inputs. Exhaustive bounded divisor/padding cases corroborate the
universal proof rather than replacing it.

The two-level physical fixture sets Q=2, b=6 and R=72 instead of 144. It runs
the retained full GL2(F2) child grammar with a coordinate-projector root and
checks every one of 18432 payload bits, borrowed input preservation, 12 child
calls/returns, and complete work erasure. This is one patterned payload,
not all Boolean inputs or a selected GL64 execution.

A separate manual fitted ordinary fixture uses Q=2, S=12, R=16, R'=24. It
tracks all 4096 independent Boolean columns through both literal physical C0
calls, each padded return and the complete ordinary return. Its body has two
atoms and no recursive child. It is not generated by the full selected
selector and is not described as an end-to-end selected-parameter run.
The nested and outer fixtures exercise different seams; neither is promoted
into a larger unexecuted composition.
