# Exact per-target relation price screen

## 1. Fixed source model

The verifier reconstructs the exact #7481 word from the bundled compressed
JSON and executes every native instruction over rational linear forms in all
1,501 original public inputs, while checking ownership, current frame,
coframed scalar contacts, fresh COPY destinations, and final owner charts. It
also verifies the exact 17-call caller and binds the bundled current price
invoice to the canonical decompressed native payload. The invoice was
independently verified as a complete signed T/P invoice in joint package
commit `509baf4514966e4202cfdde379d7adf3085b1cc7`; the byte-identical price
input is pinned here.

For each frame, its declared chart vectors are checked independent. Every
native MOVE source/destination pair and every helper initial/final pair is
checked nested, so the paid or target rank is the absolute difference of
frame dimensions. Histories are indexed by the span of their frame. This
same-span pooling is an explicit information overgrant for this optimistic
price screen; equal spans do not establish identical physical map or phase.

Let \(M\) be the source-derived main coordinate set
`live ∪ (live+112) ∪ hosted.X2 ∪ hosted.Y2`, and let \(H\) be the remaining
public helper coordinates. For one destination key, let \(P\) be the span of
all strictly earlier source observations delivered to that normalized
history. The target row of an event is excluded from its own earlier history.

## 2. Main projection filter

Let \(c\) be the target row of a MOVE and \(\pi_M\) the projection to main
coordinates. If \(\pi_M(c)\notin\pi_M(P)\), no helper-only relation can
supply that missing main part while the native history stays fixed. Such a
target is excluded. If \(\pi_M(c)\in\pi_M(P)\), choose \(p\in P\) with
\(\pi_M(p)=\pi_M(c)\), and set \(g=c-p\in H\). Put \(K=P\cap H\).

The helper-only part of the enlarged space is

\[
E=(P+\operatorname{span}\{c\})\cap H=K+\operatorname{span}\{g\}.
\]

To see this, a vector in the left side has form \(p'+\alpha c\), with
\(p'\in P\) and zero main projection. If \(\alpha=0\), it is in \(K\).
Otherwise scale to \(\alpha=1\); then \(p'=-p+k\) for some \(k\in K\),
so the vector equals \(g+k\). The reverse inclusion follows immediately.

If \(g\in K\), the target was already in full prior history. Every one of
the 1,066 selected public main hits has \(g\notin K\), so \(E/K\) has
exactly dimension one. The paired exact-rational pass maintains main-image
rows, full-row lifts, and the helper-only kernel online and computes the
support of \(E\) for every such candidate.

## 3. Minimum one-row debit price

For a helper \(h\), let \(r_h\) be its original helper-target rank, the
absolute dimension difference between its initial and final frames. For a
candidate target, the least possible rank of a helper target sacrificed by
one nonzero scalar relation in \(E\setminus K\) is

\[
d=\min\{r_h:h\in\operatorname{supp}(E)\}.
\]

The support of \(E\) is the union of supports of a basis of \(K\) and the
new direction \(g\). Any relation in \(E\setminus K\) has at least one
coordinate in that support, so its sacrificed target rank is at least \(d\).
If a rank-\(d\) coordinate occurs in \(g\), then \(g\) itself gives a
new relation outside \(K\) containing it. If it occurs only in a kernel vector
\(k\in K\), use \(g+\lambda k\). This remains outside \(K\) for
\(\lambda\ne0\), and at most one scalar cancels the chosen coordinate; over
\(\mathbb Q\), one of \(\lambda=1,2\) avoids cancellation. Thus the least
one-target rank debit is exactly \(d\) in this optimistic scalar-relation
model.

This minimum price grants all other processing, preparation, placement and
retirement for free. It does not claim the relation can be prepared while
preserving the fixed history, and it is not a cost for jointly using several
targets.

## 4. Exact profile classification

For a target of paid MOVE rank \(r\), the optimistic gross rank-price profile
is

\[
\Delta=f(r)-f(d),\qquad f(q)=q^{1-\kappa}.
\]

All counted ranks are positive. For every \(0\le\kappa<1\), \(f\) is
strictly increasing on positive ranks, so the sign of \(\Delta\) is exactly
the sign of \(r-d\). At \(\kappa=1\), \(f(q)=1\) for every positive rank
and all profiles are zero. The exact exhaustive counts are:

| Profile | Count | Exact rank condition |
| --- | ---: | --- |
| Positive | 376 | \(r>d\) |
| Zero | 437 | \(r=d\) |
| Negative | 253 | \(r<d\) |

At \(\kappa=0.0038\), the integer-power interval engine certifies every
profile and the exact best gross allowance

\[
f(8)-f(1)\in
[6.937034079270974725608699,6.937034079270974725608700].
\]
The best event is public event 40710, owner 885, frame 3 to 189, target row
\(h_{885}+h_{943}\), with a minimum-debit helper relation proportional to
\(-h_{1459}-h_{705}+h_{885}\), whose support includes original helper target
1459 of rank one.

The complete exact 17-call invoice has signed moment

\[
M\in[-59.241933884374900242189582,
     -59.241933884374900242139925]
\]

at \(\kappa=0.0038\). Dividing its deficit by 17 gives the required
per-call net native saving interval

\[
-M/17\in[3.48481964025734707306705441176470588235294118,
         3.48481964025734707306997541176470588235294118].
\]

This comparison only says the **single-target rank-price allowance** for
40710 is above the per-call threshold before physical costs. It does not
demonstrate a usable route or a full supplier.

## 5. Independent source checks and limits

A separate first-pass source replay classifies all 6,279 MOVE events by main
projection, identifies the 468 helper-only events, and selects 16 public
positive-rank main-history hits deterministically by earliest event within
rank (at most two per rank, descending rank). A different exact full-row
replay directly checks each selected event's source target, destination
history, main hit, full-history miss, \(E\)-dimension, support minimum,
relation identity, and rank-price class. The 16-check receipt includes an
executed equal-rank cancellation control and rejects a repeated-key dict
profile mutant. The all-1,066 exact paired result is validated by its
canonical records hash; the 16 direct examples are not substituted for that
exhaustive paired census.

The retained operation grammar has no free public INIT/CLEAR or zero-retag
operation. This package does not account for relation preparation, ADD/COPY/
SCALE work, phase, precision, storage, lifetime, or public retirement. It does
not sum per-target prices, prove any simultaneous funding, or change native
histories. A separate A54 preparation analysis depends on an additional
initial-access premise and is not part of this proof. No changed source,
physical cache, supplier admission, selected-frontier update, or \(\kappa\)
gain is claimed.
