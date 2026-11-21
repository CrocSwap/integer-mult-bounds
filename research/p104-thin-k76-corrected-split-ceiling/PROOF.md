# A common-piece and fragmentation cut for the k=76 split window

**Result and limits.** Under the precise two-hub, event-partition, signed-frame
and type-B invoice hypotheses below, if at least one of the 73 non-hub
nonleaves is split into more than one event piece, then

\[
 (104/76)\,\mathrm{repo} \le
 \frac{24487090883802209}{190000000000000}
 < 128.879425704223 < 128.891.
\]

The rational number is an outward upper enclosure, not an attained price.
The proof uses the actual `IDLE_ODD` correction and no 26-stage packing cap.
It does not resolve the zero-split case, establish the stronger event
assignment from ordinary per-stage matching, construct a legal word, or
prove a kappa improvement. The new linear-algebra and combinatorial argument
is a paper proof; the finite computation has **not** been checked in Lean.

This builds on [#7852 at `41beda1d6435760dc99e38bd7e65f36798aad212`](https://github.com/CrocSwap/integer-mult-bounds/commit/41beda1d6435760dc99e38bd7e65f36798aad212),
the [common-kernel rank work at #7861, `5cbe00f354aae5923205ec68370ddaa5296c2ea7`](https://github.com/CrocSwap/integer-mult-bounds/commit/5cbe00f354aae5923205ec68370ddaa5296c2ea7),
and the [actual odd-idle correction at #7858, `729a0de5c2c1d225085c3b1a7d8b37eb96713138`](https://github.com/CrocSwap/integer-mult-bounds/commit/729a0de5c2c1d225085c3b1a7d8b37eb96713138).
It extends the earlier [conditional price and disjoint-cluster screens](https://github.com/CrocSwap/integer-mult-bounds/blob/5cbe00f354aae5923205ec68370ddaa5296c2ea7/research/p104-host-strip-rank/PRICE-PRUNING.md).
The original frame and invoice definitions are due to the credited upstream
authors. The new contribution here is the overlapping-mask triple and
fragmentation cut coupled to the one-event correction.

## Reproduce

```sh
python3 -I -B verify.py
```

The script checks Git blob identities of its local #7852 source copies,
integer root certificates for every power it uses, the finite monotonicity
checks, all fragmentation cases, an independent triple-capacity dynamic
program, and controls. It records exact rational upper bounds, all finite
rows and root floors in [expected/RESULT.json](expected/RESULT.json). For each base `b`, its
floor `L` is certified by

`L^100 <= b^99 * 10^1400 < (L+1)^100`.

The script does not re-prove the rank lemma, the passage from word to frame,
or the event-partition hypothesis. The separately shipped #7861 proof and
#7858 account are source snapshots, not full predecessor-package replays.

## Model and price hypotheses

Let `p(x)=x^(99/100)`, `v(d)=p(8d+1)-p(8d)`, and
`delta(d)=1-v(d)` for `d>=1`, with `delta(0)=0`.

* There are `k=76` ordered two-column host stages and `n=151` positive-degree
  roles. `Q=T=1`, so `e=T-Q=0`. The signed frame is over a field of
  characteristic other than two, has `P=-I`, and each host's `2 x 2`
  diagonal block of the signed Gram matrix `K` is invertible. Thus #7852's
  `sgForward` gives `rank K<=2`.
* Two distinct hubs cover all 76 hosts, with 76 distinct singleton event
  pieces for each hub. Of the remaining roles, exactly 76 are degree-one
  leaves and 73 have degree at least two. All target exponents are odd.
* There is a **single global assignment of all nonempty charged events to
  role pieces**, bijective on events, in which the pieces assigned to each
  role partition its stage mask. The `CallerEv`/`CallerRC2` event kernel,
  support, and shared-stage biorthogonality hypotheses hold. This is stronger
  than #7852's ordinary stage-by-stage `CallerEv.Match`: the latter can
  reassign the same event to different roles at different stages and does
  not by itself provide a role-wise partition.
* Type-B native contacts and plain-event prices are those in #7852. The one
  plain thin contributes either zero correction or `delta(a)` for its actual
  nonempty odd-idle event of size `a`. Pieces outside the hubs need not have
  any packed-mask size cap. A non-hub role is **split** if at least two
  assigned pieces are nonempty.

For unsplit non-hub roles, the full-mask event contributes value `v(d)`.
Every non-hub nonleaf has baseline at most `v(2)`, and a split of degree
`d>=2` costs at least

\[
\Delta(d)=p(8)+p(8d-8)-p(8d)
\]

relative to a single full-mask event. Concavity makes this lower bound valid
for any number of pieces; the script certifies its monotonicity for
`d=2,...,76`. Define `s(d)=v(2)-v(d)>=0` and

\[
B=\frac{104}{76}\{2[p(609)-76p(8)]+73v(2)+76v(1)-1\}.
\]

Before split losses and odd correction, `B` is approximately
`129.0415556793`. The `-1` is the `Q=1` model charge. In a tight word,
#7852's `repo_eq` adds the nonnegative actual odd-idle correction to the
modeled invoice.

The original one-split screen is not enough on its own: the degree-two split
upper expressions for a QUERY and for a singleton odd idle are respectively
about `128.89343011759` and `128.93579083535`. These are abstract price
upper expressions, not constructed callers.

## Rank cut: each uncovered triple needs a differentiating role

First suppose exactly one non-hub nonleaf is split, with degree `d`.
Take three host stages and suppose no non-hub role contains exactly two of
those three. Further suppose the triple is **not** wholly inside the split
role's mask. The roles meeting any two of the hosts are then exactly the
same set `H`: the two hubs plus all non-hub roles containing all three.
Every non-hub member of `H` has one event spanning its entire mask.

The associated event kernel vector is supported on `H` and annihilated by
all three host `B^T` blocks: support follows because every role on which it
is nonzero must contain that full event mask. These `|H|-2` vectors are
independent by the shared-stage event biorthogonality. Invertibility of
`K`'s host diagonals and `rank K<=2` give invertible cross-host blocks and
rank two for each relevant `B^T` map on `H`. Its kernel is therefore exactly
the common `|H|-2`-dimensional space. The common-kernel rank-three sign
obstruction from #7861 rules out the triple.

Consequently, every triple must either have a role containing exactly two
of its stages or be wholly contained in the split mask. The latter exception
never occurs for a degree-two split; in general there are at most
`binom(d,3)` such triples. A role of degree `D` differentiates exactly

\[
f(D)=\binom D2(76-D)
\]

triples. Therefore, counting with multiplicity,

\[
\sum_{r\;\mathrm{nonhub,nonleaf}} f(D_r)+\binom d3
 \ge \binom{76}{3}=70300. \tag{1}
\]

Leaves and hubs contribute zero to `f`. This is a necessary condition,
not a sufficient frame or word construction. It also applies to overlapping
full-piece masks; disjointness is not assumed. When `d=2` it is the requested
exact rank cut for the smallest split that survived the earlier price-only
screen.

## Signature-cell fragmentation

The cut yields more than the total triple count. Let `L` of the 73 non-hub
nonleaves have degree at least three; the remaining `73-L` are pair roles.
Partition the 76 stages by their incidence bit vectors on the `L` long-role
masks. In each cell, every triple is either an exception contained in the
split mask or requires an edge from one of the degree-two roles. There are at
most `binom(d,3)` exceptional triples in total.

For a cell of size `a`, a pair graph with no independent triple needs at
least `g(a)=binom(a,2)-floor(a^2/4)` edges. To handle the exceptions, add
one arbitrary edge to each exceptional triple; this costs at most one edge
per exception. Because `g` has nondecreasing finite differences, distributing
`N` vertices as evenly as possible among `c` cells minimizes the total.
Writing `N=c t+r`, `0<=r<c`, set

\[
h(N,c)=(c-r)g(t)+r g(t+1).
\]

Thus `h(76,2^L) <= 73-L+binom(d,3)`. For `d=2,3,4`, the left sides at
`L=0,1,2,3` are `1406,684,324,144`, all larger than the right side. Hence
**at least four long roles are necessary** in every one-split `d=2,3,4`
case.

A stronger version removes any `q` long-role masks. At least
`76-sum_{i=1}^q D_i` stages remain outside their union; partition those
stages by the other `L-q` long masks. Let `D_1<=...<=D_L` be the sorted
degrees, and let `N_q` be the largest `N<=76` with

\[
h(N,\min(76,2^{L-q})) \le 73-L+\binom d3.
\]

Then `sum_{i=1}^q D_i >= 76-N_q`, hence
`D_q >= ceil((76-N_q)/q)`. This remains valid with overlap among all masks.
The script enumerates `L=4,...,73`, obtains each sorted degree lower-bound
vector, and charges the corresponding monotone `s(D)` losses. For the
worst degree-two split row, `L=9` and the vector is

`[3,3,3,3,3,4,6,7,7]`.

The one role receiving the correction may be excluded from the price
loss. Removing the largest lower bound is a favorable relaxation, giving an
unscaled loss of at least `0.04760037148865`. The corresponding corrected
upper bound is `128.879425704223`. The role degrees in this row are only
individual lower bounds; they are **not** a realization or a tight optimizer.

## Coupling the correction and the price

For `d=2,3,4`, the fragment cut gives `L>=4`. If the actual odd event belongs
to an unsplit non-hub role, designate that role; if it belongs to the split
role, its size is at most `d-1<=3`, so designate any other unsplit long role;
if it is on a hub or leaf, designate any unsplit non-hub role. For a QUERY or
empty odd set use the same upper relaxation. In each case, a designated
unsplit role of degree `D` exists whose `delta(D)` is at least the actual
correction. The identity

\[
\delta(D)-s(D)=1-v(2)
\]

then accounts for both its full-mask value and the odd correction without
assuming the odd set is a singleton. For split degree `d`, this yields the
unscaled price bound `B*76/104 - Delta(d) - s(d) + 1-v(2)` minus the losses
of the remaining unsplit roles. For `d=3,4`, the fragmentation calculation
can generously omit both the split and designated roles from its long-role
loss sum; for `d=2`, only the designated role is long.

For an independent check, (1), `max f(D)=f(51)=31875`, and the baseline
`f(2)=74` imply that the 71 roles other than the split and designated roles
must provide surplus at least `33097`, `32951`, or `32735` for split degree
`2`, `3`, or `4`, respectively. They contain at least `3`, `2`, or `2` long
roles. An unbounded integer dynamic program minimizes an outward lower
approximation to `sum s(D)` over these conditions; allowing more than 71
roles only relaxes the problem. Its upper ceilings are `128.882153555578`,
`128.826956644219`, and `128.789299257074`. For degree two, the signature
fragmentation ceiling is sharper than this dynamic program.

The degree-two dynamic-program witness has long degrees `[3,7,49,51]`, of
which 51 is the freely corrected role, with 69 pair roles. This is not a
frame: remove the degree-3 and degree-7 masks. At least 66 hosts remain, and
the two remaining long masks create at most four signature cells. They
require at least `h(66,4)=240` internal pair edges, but only 69 pair roles
exist. Thus even this numerical relaxation's optimizer is eliminated by a
further exact fragmentation cut, independent of its placement.

The final certified case table uses the better of the two screens:

| Non-hub split condition | Corrected upper enclosure |
| --- | ---: |
| Exactly one split, degree 2 | 128.879425704223 |
| Exactly one split, degree 3 | 128.826956644219 |
| Exactly one split, degree 4 | 128.789299257074 |
| Exactly one split, degree at least 5 | 128.862125746997 |
| At least two split roles | 128.843115411690 |

The last two rows use the unconditional size-76 correction cap within this
76-stage model and monotonicity of the relevant split and degree losses; they
need no fragmentation. The maximum is the degree-two row. No step here
excludes or bounds the remaining **zero-split** two-hub family below the
bar, and none turns these conditional hypotheses into general caller laws.
