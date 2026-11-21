# Follow-up: arbitrary excess and conditional caller pricing

This note continues the [thin-window screen](../README.md), retaining the
pinned #7852 head `41beda1d6435760dc99e38bd7e65f36798aad212`. It gives
conditional price bounds for a specific (k=76, Q=1) type-B role template,
and separate graph consequences of the broader rank argument. It does **not**
prove a price ceiling for all callers or a new multiplication bound.

Reproduce the integer-enclosed numerical checks and graph arithmetic with:

```sh
cd .
python3 -B check_price.py
```

[RESULT.json](RESULT.json) records exact rational endpoints, power
coefficients, integer-root certificates, source blob identities, and controls.
The elementary price and counting arguments below are paper proofs; the
arbitrary-rank theorem invoked for the graph screen is separately developed
by the `broader_decoders` research lane, and is not a theorem proved by this
script.

## Source accounting and baseline

Write (p(x)=x^{99/100}), (k=76), (n=151), and (Q=n-(2k-2)=1).
Assume two distinct roles use every stage and each is matched to singleton
events at all 76 stages. Assume all other 149 roles have positive degree and
the stagewise `CallerEv.Match` hypotheses hold. The target exponent is odd,
and the caller has the #7852 type-B contact and plain-event prices. These
assumptions concern the template, not an assertion that a legal caller of
this shape exists.

The input-matching assumption here is the ordinary **per-stage** matching:
it does not require one event to be assigned to the same role at every stage
or require a partition of each role's mask. `CallerEv.roleVal_sum` identifies
the stage-form sum with the event invoice. For a role of degree (D), each
matched event has size (1\le a\le D), and

\[
 \frac{p(8a)}a = 8^{.99} a^{-.01}\ge \frac{p(8D)}D.
\]

Therefore its role value is at most (v(D)=p(8D+1)-p(8D)). Concavity of
(p) makes (v) decreasing, so every non-hub role is at most
(u=v(1)=p(9)-p(8)). Subtracting (Q=1), the scaled model has upper bound

\[
 B_{\rm broad}=\frac{104}{76}\bigl(2p(609)-152p(8)+149u-1\bigr).
\]

Its exact interval is in `RESULT.json`; it is about 129.68192769035.

For a nonempty odd-idle set of size (d\le76), define
(\delta(d)=1+p(8d)-p(8d+1)\), and let \(\delta(0)=0\). It increases with
(d); each QUERY has zero correction. If the plain thin count is
(T=1+e\), summing the pinned `SchemaCostB.mdl_thin_price` identity gives,
without using its tightness hypothesis,

\[
 \frac{104}{76}\,\text{repo}
 = \widehat c_Q + \frac{104}{76}\Bigl(-e+\sum_{j=1}^{1+e}\delta(d_j)\Bigr).
\]

This is a direct op-by-op algebraic extension of `repo_eq`; the latter is
stated in the source only for tight (e=0). Because \(\delta(76)<1\), the
right side is largest at (e=1) for all integer (e\ge1). Consequently

\[
 \frac{104}{76}\,\text{repo}
 \le B_{\rm broad}+\frac{104}{76}[-1+2\delta(76)]
 < 128.509128349620 < 128.891.
\]

This screen needs no (e=0) tightness, exact leaf count, role-wise piece
partition, or 26-bit mask assumption. It **does** require the two specified
all-stage singleton-matched roles, positive degree for the others, the
stagewise matching, and the stated caller-price rules.

## Tighter split-piece screens at e = 0

Now additionally assume exactly 76 leaves and 73 other non-hub nonleaves,
and a stronger assignment in which actual nonempty events can be assigned
bijectively to role pieces that partition each role mask. This stronger
condition is **not** implied merely by `CallerEv.Match`: a general stagewise
match can assign an event differently at different stages. It is required
for the split penalties below.

The upper bound before split penalties is

\[
 B=\frac{104}{76}\{2[p(609)-76p(8)]
       +73[p(17)-p(16)]+76[p(9)-p(8)]-1\},
\]

enclosed by `[129.041555678999, 129.041555679618]`. If a degree-(D\)
role is split into at least two nonempty pieces, subadditivity and concavity
give a loss of at least

\[
 \Delta(D)=p(8)+p(8D-8)-p(8D),
\]

which increases with (D\ge2). There is one plain thin, so the real repo
value adds at most one odd-idle correction. The following bounds use the
actual correction, rounded outward:

| Additional condition | Upper bound for `(104/76) repo` |
| --- | ---: |
| At least two non-hub nonleaf roles are split; any odd mask | 128.843115412000 |
| One split role has degree at least 3; odd mask has size at most 2 | 128.889366143632 |
| One split role has degree at least 4; odd mask has size at most 26 | 128.886676556982 |
| One split role has degree at least 5; any odd mask | 128.873902960988 |

Every row is below 128.891. The 26-size row has an explicit size assumption;
the generic caller model does not automatically inherit CERTKIT's 26-bit
packing correspondence. The other rows allow any stage set up to 76 where
stated.

There is also a coupled version requiring **no 26-bit cap**. Suppose an
`IDLE_ODD` event is itself a piece of a split non-hub role of degree at least
three. If its mask has (d\ge2), its role has degree at least (d+1), and

\[
 \Delta(d+1)-\delta(d)
 = p(8)-1-[p(8d+8)-p(8d+1)]
\]

is increasing in (d). Its worst case is (d=2), giving the second table
row. A singleton odd piece gives the stronger upper bound
`128.880593924303`. A QUERY has zero correction. The script checks the
finite monotonicity statements with integer power enclosures; the analytic
reason is concavity of (p).

The controls matter: with only one split degree-two role, the resulting
upper expression is about 128.893430118 for a QUERY and 128.935790836 for a
singleton odd idle. These expressions do **not** establish a value below
the bar. Similarly, one split degree-three role with an independently
placed size-three odd idle gives an upper expression about 128.894564381;
one split degree-four role with a size-76 odd idle gives about 128.900358679.
These show why the size and attachment hypotheses are used. They are
upper-bound expressions, not constructed legal callers.

## Rank generalization and disjoint-cluster screen

The other lane's arbitrary-rank result states that, under its signed-Gram
and invertible-host-block assumptions, if (m) selected ordered host stages
have precisely the same two roles in each pairwise overlap, their selected
matrix has rank at least (m). The common-kernel version permits a common
overlap set of size (h\ge2) when (h-2) independent vectors supported on
that set are killed by every selected host `B^T` block.

For two global hubs, draw an edge between stages if a non-hub role contains
both. If `rank K <= r`, that result gives independence number at most (r).
Thus Turán's theorem gives the minimum number of non-hub edges as

\[
 G(k,r)=t{q+1\choose2}+(r-t){q\choose2},\qquad k=rq+t,\ 0\le t<r.
\]

`CallerSGram.sgForward` gives `rank K <= 2+e` when `Q=1` and
`T=1+e`. With 73 degree-two roles and no other non-hub role meeting two
stages, the graph has at most 73 edges. At (k=76),
`G(76,26)=74 > 73`, while `G(76,27)=71`; hence this family is impossible for
every (e\le24), conditional on the rank theorem and host assumptions.
The latter value means only that this edge count stops excluding it; it does
not construct a frame at (e=25).

The common-kernel theorem also gives a more general conditional screen.
Allow the 73 non-hub nonleaves to comprise (m) degree-two roles and any
number of roles of degree at least three with **pairwise disjoint** masks.
Assume each long role has one actual event spanning its entire mask. Its
event's kernel vector is supported on that role and the two hubs and is
nonzero by event biorthogonality. Within its mask, pair-role edges must
therefore leave no independent set of (r+1) stages. Since the masks are
disjoint, each degree-two role can supply an internal edge to at most one
mask. Summing the local Turán bounds yields the necessary global inequality

\[
 G(76,r)\le (r+1)m+\frac{r-1}{2}\,76.
\]

For example, writing `r=2+e` and using only `m <= 73`, the two sides are
`1406 > 257` at (e=0), `925 > 368` at (e=1), and `684 > 479` at
(e=2). This excludes the whole stated disjoint-cluster family in those
cases, conditional on the rank theorem. At (e=3), the coarse test gives
`540 <= 590` and does not exclude it.

Derivation of the inequality: a long mask of size (D) needs at least
(G(D,r)\ge (D^2/r-D)/2) internal pair-role edges. Hence
({D\choose2}\le rG(D,r)+(r-1)D/2). Sum over disjoint masks, use
`sum D <= 76` and `sum G(D,r) <= m`, then add at most (m) edges from the
degree-two roles. The graph lower bound applies to distinct edges, whereas
the upper bound may count multiplicities, which only weakens the exclusion.

The original signed-Gram, event and invoice definitions are due to their
credited #7852 authors. The arbitrary-rank strengthening was supplied by the
`broader_decoders` Codex lane; this artifact adds the conditional (k=76\)
price bounds and the finite graph consequences.
